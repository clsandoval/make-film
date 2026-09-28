# VO explainer scaffold

The runnable template for the **vo-explainer** style ([../RECIPE.md](../RECIPE.md)): a narrated explainer where the
voice carries the story, there is no music, and every cut lands on an invisible beat grid. A cold open, a contents
page, a dive into each chapter, one idea on screen per spoken line, a pullback with a tick, an end card.
Everything on screen comes from `explainer.json`.

## Run it (free, no voice needed)

```bash
cp -r styles/vo-explainer/starter my-film && cd my-film
npm i && npx playwright install chromium
node scripts/timing.mjs       # -> timing.json + captions.srt; prints duration, wpm, moves/s
node scripts/stills.mjs 1     # -> stills/*.png + labelled stills/sheet-N.png. Iterate HERE, not on renders
node scripts/qa.mjs           # determinism, lines on the beat, chapters on the bar, no VO overlap, overflow, copy tells
```

With no `audio_meta.json`, line lengths are **estimated** at `grid.wpm_estimate` (150 wpm). Every frame says
`PLACEHOLDER VO TIMING` in the corner, and `master.sh` will only make a picture-plus-SFX preview. That is enough
to lock the script, the storyboard and the motion before anything is paid for.

## Record the voice (spends characters, only after the script is locked)

```bash
python3 scripts/vo.py chars                   # free: characters per chapter and total. Check the account budget
# set voice.id in explainer.json (there is no default), then:
ELEVENLABS_API_KEY=... python3 scripts/vo.py gen   # one take per chapter -> assets/voice/raw/
python3 scripts/vo.py split                   # free: per-line wavs + audio_meta.json (real durations, word times)
node scripts/timing.mjs && node scripts/qa.mjs
```

`gen` and `line` refuse to run without both `ELEVENLABS_API_KEY` in the environment and `voice.id` in the config.
They never read a key from a file. Raw takes are kept, so nothing is paid for twice.

**One-line fix after approval:** edit that line's `text`, add `"take": "line"` to it, then
`ELEVENLABS_API_KEY=... python3 scripts/vo.py line <line_id>` and `python3 scripts/vo.py split`. Only that line is
re-recorded; every other line is cut from the approved chapter take exactly as before, and the later cues move with it.

## Render

```bash
python3 scripts/mix.py                                                    # -> assets/mix.wav (VO + soft SFX, no music)
START=0 END=20 node scripts/render.mjs frames/preview                     # 20 s motion preview first
START=0 END=20 bash scripts/master.sh frames/preview renders/preview-v1.mp4
node scripts/render.mjs frames/full 8
bash scripts/master.sh frames/full renders/film-v1.mp4                    # -14 LUFS, <= -1 dBTP, refuses to overwrite
```

Needs node 18+, python 3, ffmpeg. Optional: `python3 scripts/stt.py assets/voice/raw/*.wav` (local faster-whisper,
free) lists every word of a take with low-confidence words flagged, so you can check names before you split.

## explainer.json

| key | what |
|---|---|
| `brand` | `name`, `org`, `url` (end card), `title`, `subtitle` (contents page), `font`, `mono`, `palette` |
| `grid` | `bpm` (the invisible grid, 100 gives a 0.6 s beat), `snap_beats` (0.5: lines start on half beats), `lead_in_beats`, `breath` (seconds of silence after each line), `min_beats` (shortest hold per line), `wpm_estimate` |
| `voice` | `id` (empty until chosen, no default), `model`, `stability`, `similarity_boost`, `style` |
| `tts_respell` | spoken spellings, e.g. `{"Daimon": "Day-mon"}`; changes what the voice hears, never the screen |
| `sound.sfx` | soft tick on each cut and a chime on each chapter tick; `false` for voice only |
| `chapters[]` | `id`, optional `title` + `sub` (a chapter with no title is the cold open, before the contents page), `lines[]` |
| `lines[]` | `id`, `text` (what is spoken), `show` (the one idea on screen), optional `breath` (extra seconds before a line that starts a new idea), optional `take: "line"` |

`show.type` is one of:

| type | fields | on screen |
|---|---|---|
| `say` | optional `text` | the line itself, words landing on eighth notes as they are spoken |
| `card` | `kicker`, `title`, `body`, `tag` | a light card lands |
| `count` | `to`, `prefix`, `suffix`, `decimals`, `label`, `tag` | a number counts up over 2 beats |
| `swap` | `from`, `to` | before, then an arrow and the after two beats later |
| `steps` | `items[]`, `active` | a track of stations; consecutive `steps` lines move the highlight along it |
| `chips` | `title`, `items[]` | chips land one per half beat |
| `bars` | `title`, `items[[label, value]]`, `tag` | bars grow one per beat |

Timing is derived, never hand-typed. Each line starts on the grid (a half beat by default) and holds for
`max(min_beats, voice length + breath, rounded up to the grid)`; each chapter ends on a bar line; the camera move into
each line ends on the grid point where the voice starts. Change a line and every later cue moves with it. Use `tag: "example"` on any
made-up figure or name.
