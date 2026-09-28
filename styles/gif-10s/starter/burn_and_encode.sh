#!/usr/bin/env bash
# burn_and_encode.sh IN.mp4 OUT_BASENAME [overlays.txt]   -> OUT.mp4 (words burned in) + OUT.gif (feed cap)
# burn_and_encode.sh --test OUT_BASENAME [overlays.txt]   -> same, on a local 10 s 720x720 ffmpeg test clip ($0)
#
# GIF settings come from the positional defaults of gif_encode.sh (480 px, 10 fps, 64 colours) unless
# GIF_ARGS="540 10 64" is set. The encoder is found at $GIF_ENCODE, else ./gif_encode.sh, else the skill's
# scripts/gif_encode.sh three directories up. Font: $FONT, default DejaVu Sans Bold.
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
in=${1:?input mp4, or --test}; out=${2:?output basename}; ov=${3:-$here/overlays.txt}
font=${FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf}
enc=${GIF_ENCODE:-}
[ -z "$enc" ] && [ -x "$here/gif_encode.sh" ] && enc=$here/gif_encode.sh
[ -z "$enc" ] && enc=$here/../../../scripts/gif_encode.sh
[ -f "$enc" ] || { echo "gif_encode.sh not found: copy the skill's scripts/gif_encode.sh next to this script or set GIF_ENCODE" >&2; exit 1; }
[ -f "$font" ] || { echo "font not found: $font (set FONT)" >&2; exit 1; }

if [ "$in" = --test ]; then
  in=$out-testsrc.mp4
  ffmpeg -v error -y -f lavfi -i "testsrc2=size=720x720:rate=24:duration=10" -c:v libx264 -pix_fmt yuv420p "$in"
fi

vf=$(grep -v '^[[:space:]]*#' "$ov" | grep -v '^[[:space:]]*$' | sed "s#{F}#$font#g" | paste -sd, -)
ffmpeg -v error -y -i "$in" -vf "${vf:-null}" -an -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart "$out.mp4"
bash "$enc" "$out.mp4" "$out.gif" ${GIF_ARGS:-}
size=$(stat -c %s "$out.gif")
[ "$size" -le 8000000 ] || echo "WARNING: $out.gif is over 8 MB; lower width or colours" >&2
# grid frame for placing text: 480 px wide, 60 px lines
ffmpeg -v error -y -ss 1.5 -i "$in" -frames:v 1 -vf "scale=480:-1,drawgrid=w=60:h=60:t=1:c=red@0.6" "$out-grid.jpg"
echo "$out.mp4  $out.gif  $out-grid.jpg"
