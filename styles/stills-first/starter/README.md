# Stills-first starter

For [stills-first](../RECIPE.md) roughs. Local ffmpeg and Python only; nothing here generates images or calls
an API.

| file | what |
|---|---|
| `SHOTLIST.template.md` | beats against the locked VO: words, what must be seen, source type, status; rejected ideas; the three reviews |
| `shots.example.json` | frame size, fps and one entry per still (`id`, `still`, `dur`, optional `line`) |
| `build_animatic.py` | holds each still for its `dur`, letterboxes it to the frame, lays the VO under it, writes an H.264 MP4 |

```bash
cp shots.example.json shots.json          # edit: stills paths relative to this file, durations from the VO timings
python3 build_animatic.py shots.json rough-v1.mp4 --vo vo.wav             # delivery rough
python3 build_animatic.py shots.json rough-v1-review.mp4 --vo vo.wav --label   # shot id + start time burned in
python3 build_animatic.py shots.json silent.mp4 --stills ../stills        # stills in another folder, no audio
```

The file always ends with the last shot. A VO shorter than the plan is padded with silence; a VO longer than the
plan is cut and the script prints a warning, because the check is audio through the last word. Stills of
mixed sizes and orientations are fine: each is fitted inside the frame, never stretched.
