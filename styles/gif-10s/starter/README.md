# Ten-second GIF starter

For the [ten-second GIF](../RECIPE.md). The generation itself is paid and goes through the skill's
`scripts/seedance_gen.py`; everything here is local ffmpeg and runs for $0.

| file | what |
|---|---|
| `JOKE.template.md` | the joke, three beats, burned-in text per beat, the prompt and `spec.json` |
| `overlays.txt` | one ffmpeg `drawtext` filter per line (`{F}` = font path): typing, correction, a descending word |
| `burn_and_encode.sh` | burns `overlays.txt` into a clip, encodes the GIF with `gif_encode.sh`, warns over 8 MB, writes a 60 px grid frame for placing text |

```bash
./burn_and_encode.sh --test /tmp/joke          # $0 dry run on a 10 s 720x720 ffmpeg testsrc2 clip
./burn_and_encode.sh ../clip/raw.mp4 out/joke  # the real take -> out/joke.mp4 + out/joke.gif + out/joke-grid.jpg
GIF_ARGS="540 10 64" ./burn_and_encode.sh raw.mp4 out/joke-540   # try a larger GIF if there is room
```

The encoder is `$GIF_ENCODE`, else `./gif_encode.sh`, else `../../../scripts/gif_encode.sh` (the skill's copy).
If this folder is copied out of the skill, copy `scripts/gif_encode.sh` next to the script.
