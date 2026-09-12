#!/usr/bin/env bash
# gif_encode.sh in.mp4 out.gif [width=480] [fps=10] [colors=64]
# Palette-optimised GIF for feed posts (LinkedIn caps around 8 MB). Prints the result size.
# Ten seconds of flat 2D at 480/10/64 lands near 7 MB; raise width or colours only if there is room.
set -euo pipefail
in=${1:?input mp4}; out=${2:?output gif}; w=${3:-480}; fps=${4:-10}; colors=${5:-64}
ffmpeg -v error -y -i "$in" \
  -vf "fps=$fps,scale=$w:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=$colors[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" \
  "$out"
printf '%s  %dpx %dfps %d colours  %.2f MB\n' "$out" "$w" "$fps" "$colors" "$(stat -c %s "$out" | awk '{print $1/1e6}')"
