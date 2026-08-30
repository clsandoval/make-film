#!/usr/bin/env bash
# The set that actually ships, derived from the newest master.
#
#   scripts/deliverables.sh [master.mp4]
#
# Three traps live in the 9:16 cut and all three are load-bearing:
#
#  1. libass sizes a bare .srt against a default 384x288 PlayRes, so FontSize and
#     MarginV are NOT pixels — every number is scaled by PlayResY/288. We convert
#     to .ass and patch PlayResX/Y, or MarginV lands off-frame.
#  2. ASS alpha is INVERTED: &H00 is opaque, &HFF is transparent.
#  3. A ground with a vignette is not a flat colour, so single-colour letterbox
#     bars leave a visible seam. The bars are built from the picture's own edge
#     rows, stretched.
set -euo pipefail
cd "$(dirname "$0")/.."

read -r NAME GROUND CROP_X CROP_W STAGE_H POSTER_AT CAP_FONT CAP_SIZE CAP_COLOUR FONTSDIR <<< "$(python3 - <<'PY'
import json
c = json.load(open("film.json"))
stage = {"w": 1920, "h": 1080, **c.get("stage", {})}
margin = int(c.get("safe_margin", 0))
cap = {"font": "sans-serif", "size": 44, "colour": "&H00FFFFFF", "fontsdir": "assets/fonts", **c.get("caption", {})}
print(c["name"], c.get("ground", "0x000000"), margin, stage["w"] - 2 * margin, stage["h"],
      c.get("poster_at", 0), cap["font"].replace(" ", "~"), cap["size"], cap["colour"], cap["fontsdir"])
PY
)"
CAP_FONT="${CAP_FONT//\~/ }"

MASTER="${1:-$(ls -t renders/${NAME}-v*.mp4 2>/dev/null | head -1)}"
[ -n "$MASTER" ] && [ -f "$MASTER" ] || { echo "no master found: pass one, or render renders/${NAME}-v*.mp4" >&2; exit 1; }
OUT=deliverables; mkdir -p "$OUT"
echo "master: $MASTER"

# A master already taller than it is wide was composed vertical. Cropping a
# square out of it cuts content off both ends, and stacking it into 9:16 is
# meaningless. A different aspect is a different COMPOSITION — render it with
# FILM_PAGE/FILM_W/FILM_H — never a crop of this one.
MW=$(ffprobe -v error -select_streams v:0 -show_entries stream=width  -of csv=p=0 "$MASTER" | head -1)
MH=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$MASTER" | head -1)
PORTRAIT=0; [ "$MH" -gt "$MW" ] && PORTRAIT=1

# ---- 1:1 -------------------------------------------------------------------
if [ "$PORTRAIT" = 1 ]; then
  echo "1:1 skipped: master is ${MW}x${MH}, composed vertical"
else
ffmpeg -y -loglevel error -i "$MASTER" \
  -vf "scale=1080:-2,pad=1080:1080:0:(oh-ih)/2:$GROUND" \
  -c:v libx264 -pix_fmt yuv420p -crf 19 -tune film -movflags +faststart \
  -c:a copy "$OUT/$NAME-1x1.mp4"
fi

# ---- 9:16 ------------------------------------------------------------------
# Centre-crop to the safe margin so the picture fills more of a vertical frame,
# then letterbox with the picture's own stretched edge rows.
PIC_H=$(python3 -c "print(int(round(1080*$STAGE_H/$CROP_W/2))*2)")
BAR_H=$(python3 -c "print((1920-$PIC_H)//2)")
SRT="$OUT/$NAME.srt"; ASS="$OUT/$NAME.ass"
SUBS=""
if [ -f "$SRT" ]; then
  ffmpeg -y -loglevel error -i "$SRT" "$ASS"
  python3 - "$ASS" "$CAP_FONT" "$CAP_SIZE" "$CAP_COLOUR" <<'PY'
import re, sys
path, font, size, colour = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(path).read()
s = re.sub(r"PlayResX: *\d+", "PlayResX: 1080", s)
s = re.sub(r"PlayResY: *\d+", "PlayResY: 1920", s)
if "PlayResX" not in s:
    s = s.replace("[Script Info]", f"[Script Info]\nPlayResX: 1080\nPlayResY: 1920", 1)
# Name,Font,Size,Primary,Secondary,Outline,Back,Bold,...,Outline,Shadow,Align,ML,MR,MV,Enc
s = re.sub(r"^Style: Default,.*$",
           f"Style: Default,{font},{size},{colour},&H000000FF,&H00000000,&H00000000,"
           f"0,0,0,0,100,100,0,0,1,0,0,2,60,60,120,1", s, flags=re.M)
open(path, "w").write(s)
PY
  SUBS=",ass='$ASS':fontsdir='$FONTSDIR'"
fi
# split=3 explicitly (implicit split segfaults in some builds) and pad+overlay
# instead of vstack (malloc corruption in some builds).
ffmpeg -y -loglevel error -i "$MASTER" -filter_complex \
  "[0:v]split=3[a][b][c];\
   [b]crop=$CROP_W:16:$CROP_X:0,scale=1080:$BAR_H:flags=bilinear[top];\
   [c]crop=$CROP_W:16:$CROP_X:$((STAGE_H-16)),scale=1080:$BAR_H:flags=bilinear[bot];\
   [a]crop=$CROP_W:$STAGE_H:$CROP_X:0,scale=1080:$PIC_H,pad=1080:1920:0:$BAR_H:$GROUND[base];\
   [base][top]overlay=0:0[s1];[s1][bot]overlay=0:$((BAR_H+PIC_H))[stacked];\
   [stacked]null$SUBS[v]" \
  -map "[v]" -map 0:a -c:v libx264 -pix_fmt yuv420p -crf 19 -tune film \
  -movflags +faststart -c:a copy "$OUT/$NAME-9x16.mp4"

# ---- poster ----------------------------------------------------------------
ffmpeg -y -loglevel error -ss "$POSTER_AT" -i "$MASTER" -frames:v 1 "$OUT/$NAME-poster.png"

# ---- review encode: Telegram and most chat apps cap uploads at 50 MB --------
# -c:a copy, like every other cut. Re-encoding to aac 128k saved under a megabyte
# on a video-dominated file and pushed true peak from -1.0 to -0.8 dBTP on three
# shipped films — over the ceiling master.sh exits non-zero on, in the one file
# the director actually watches during the note rounds.
ffmpeg -y -loglevel error -i "$MASTER" -c:v libx264 -crf 28 -preset slow \
  -pix_fmt yuv420p -movflags +faststart -c:a copy "$OUT/$NAME-review.mp4"

# ---- verify every variant --------------------------------------------------
# Dimensions catch a mislabelled aspect, duration catches -shortest clipping a
# tail, and loudness catches a cut that re-encoded audio you already mastered.
printf '%-52s %-16s %-8s %s\n' FILE WxH/DURATION SIZE "I / TRUE PEAK"
for f in "$MASTER" "$OUT/$NAME"-*.mp4; do
  printf '%-52s ' "$f"
  printf '%-16s ' "$(ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0:s=x "$f" | tr '\n' ' ')"
  printf '%-8s ' "$(du -h "$f" | cut -f1)"
  if [ -z "$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$f")" ]; then
    echo "no audio track"
  else
    READOUT=$(ffmpeg -hide_banner -i "$f" -af ebur128=peak=true -f null - 2>&1 | tail -14)
    echo "$(echo "$READOUT" | grep -oE 'I:\s*-?[0-9.]+' | tail -1 | grep -oE '\-?[0-9.]+') LUFS  $(echo "$READOUT" | grep -oE 'Peak:\s*-?[0-9.]+' | tail -1 | grep -oE '\-?[0-9.]+') dBTP"
  fi
done
