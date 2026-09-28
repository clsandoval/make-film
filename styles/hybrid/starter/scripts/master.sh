#!/bin/bash
# usage: scripts/master.sh <frames_dir> <out.mp4>   frames f00000.png… at 30 fps + assets/mix.wav (from scripts/mix.py)
# -> H.264 CRF 17 + AAC 320k, integrated loudness -14 LUFS (±0.15), true peak <= -1 dBTP. Refuses to overwrite.
set -euo pipefail
FR=$1; OUT=$2; cd "$(dirname "$0")/.."
[ -e "$OUT" ] && { echo "refusing to overwrite $OUT (version it)"; exit 1; }
DUR=$(python3 -c "import json;print(json.load(open('timing.json'))['TOTAL'])")
mkdir -p "$(dirname "$OUT")"; PIC=${OUT%.mp4}-pic.mp4; M4A=${OUT%.mp4}.m4a
echo "frames $(ls "$FR" | wc -l) for $DUR s"
ffmpeg -v error -y -framerate 30 -i "$FR/f%05d.png" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart "$PIC"
meas(){ ffmpeg -hide_banner -i "$1" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}'; }
MI=$(meas assets/mix.wav); G=0
for it in 1 2 3 4; do
  GAIN=$(python3 -c "print(-14.0-($MI)+$G)")
  ffmpeg -v error -y -i assets/mix.wav -af "volume=${GAIN}dB,alimiter=limit=0.72:attack=2:release=60:level=false,aformat=sample_fmts=fltp:channel_layouts=stereo,apad=whole_dur=$DUR" -t "$DUR" -c:a aac -b:a 320k "$M4A"
  OI=$(meas "$M4A"); echo "pass $it gain $GAIN dB -> $OI LUFS"
  python3 -c "import sys;sys.exit(0 if abs(-14.0-($OI))<=0.15 else 1)" && break
  G=$(python3 -c "print($G+(-14.0-($OI)))")
done
ffmpeg -v error -y -i "$PIC" -i "$M4A" -map 0:v -map 1:a -c copy -movflags +faststart "$OUT"
rm -f "$PIC" "$M4A"
ffprobe -v error -show_entries stream=codec_name,width,height,nb_frames,duration -of compact "$OUT"
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
ls -la "$OUT"
