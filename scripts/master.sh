#!/usr/bin/env bash
# Mix the audio onto the silent render and master it to broadcast loudness.
#
#   scripts/master.sh renders/silent-v3.mp4 renders/myfilm-v3.mp4 [assets/mix.wav]
#
# Two passes, then a residual loop. loudnorm can only run linear=true when the
# mix's crest factor is <= target_TP - target_I (13 dB at -14/-1). Above that it
# silently falls back to dynamic normalisation and lands short — 0.6 dB in the
# case that produced this loop. So we measure the OUTPUT and correct, up to four
# times, and fail loudly rather than ship silently off spec.
set -euo pipefail

SILENT="${1:?usage: master.sh <silent.mp4> <out.mp4> [mix.wav]}"
OUT="${2:?usage: master.sh <silent.mp4> <out.mp4> [mix.wav]}"
MIX="${3:-assets/mix.wav}"
I_TARGET=-14; TP_TARGET=-1; LRA_TARGET=11; TOLERANCE=0.2

json_field() { echo "$1" | grep "\"$2\"" | head -1 | sed -E 's/.*: *"?([-0-9.a-z]+)"?,?/\1/'; }

# ---- pass 1: measure the source -------------------------------------------
MEASURE=$(ffmpeg -hide_banner -i "$MIX" \
  -af "loudnorm=I=$I_TARGET:TP=$TP_TARGET:LRA=$LRA_TARGET:print_format=json" \
  -f null - 2>&1 | sed -n '/^{/,/^}/p')
I=$(json_field "$MEASURE" input_i)
TP=$(json_field "$MEASURE" input_tp)
LRA=$(json_field "$MEASURE" input_lra)
THRESH=$(json_field "$MEASURE" input_thresh)
OFFSET=$(json_field "$MEASURE" target_offset)
echo "source: I=$I TP=$TP LRA=$LRA"

# ---- pass 2: normalise, limit, mux ----------------------------------------
mkdir -p "$(dirname "$OUT")"
ADJUST=0
for attempt in 1 2 3 4; do
  ffmpeg -y -hide_banner -loglevel error -i "$SILENT" -i "$MIX" -filter_complex \
    "[1:a]loudnorm=I=$I_TARGET:TP=$TP_TARGET:LRA=$LRA_TARGET:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$THRESH:offset=$OFFSET:linear=true,volume=${ADJUST}dB,alimiter=limit=0.891:level=disabled,aresample=48000[a]" \
    -map 0:v -map "[a]" \
    -c:v libx264 -pix_fmt yuv420p -crf 19 -tune film -movflags +faststart \
    -c:a aac -b:a 256k -ar 48000 -ac 2 -shortest "$OUT"

  # ---- verify on the DELIVERED file. Measuring the source proves nothing. --
  READOUT=$(ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | tail -14)
  GOT_I=$(echo "$READOUT" | grep -oP 'I:\s*\K-?[0-9.]+' | tail -1)
  GOT_TP=$(echo "$READOUT" | grep -oP 'Peak:\s*\K-?[0-9.]+' | tail -1)
  RESIDUAL=$(python3 -c "print(round($I_TARGET - $GOT_I, 3))")
  echo "attempt $attempt: I=$GOT_I LUFS  TP=$GOT_TP dBTP  (residual ${RESIDUAL} LU)"

  if python3 -c "import sys; sys.exit(0 if abs($RESIDUAL) <= $TOLERANCE else 1)"; then
    echo "master ok: $OUT"
    ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate \
      -of default=noprint_wrappers=1 "$OUT"
    exit 0
  fi
  ADJUST=$(python3 -c "print(round($ADJUST + $RESIDUAL, 3))")
done

echo "FAILED to reach $I_TARGET +/- $TOLERANCE LUFS after 4 passes (last: $GOT_I)." >&2
echo "Do not ship this. Check the mix's crest factor." >&2
exit 1
