# Chapters scaffold

The runnable template for the **chapters** style ([RECIPE](../RECIPE.md)): a contents page that is the hub
of one canvas, a camera dive along a drawn line into each chapter, beat-locked punch-ins, a pullback with a ✓,
a New/Fixed panel, a map pullback and the end card. Everything on screen comes from `chapters.json`.

```bash
cp -r ~/.claude/skills/make-film/styles/chapters/starter my-film && cd my-film
npm i && npx playwright install chromium
# edit chapters.json: brand, palette, hub, chapters[], panel; put a cleared track at music.file
node scripts/timing.mjs            # -> timing.json, prints duration and camera moves/s (target 0.55-1.0)
node scripts/stills.mjs 1          # -> stills/*.png + labelled stills/sheet-N.png. Iterate HERE, not on renders
node scripts/qa.mjs                # determinism, move rate, text overflowing its box
python3 scripts/mix.py             # -> assets/mix.wav (music arranged on the bar grid + synthesized SFX)
START=0 END=20 node scripts/render.mjs frames/preview   # 20 s motion preview first
node scripts/render.mjs frames/full 8
bash scripts/master.sh frames/full renders/film-v1.mp4  # -14 LUFS, <= -1 dBTP, refuses to overwrite
```

No music file yet? `mix.py` synthesizes a placeholder groove at `music.bpm` so the whole pipeline runs from a
fresh copy. Replace it with a cleared track before anything is delivered.

## chapters.json

| key | what |
|---|---|
| `brand` | `name`, `url`, `org` for the end card; `palette` (CSS colours); `font`, `mono`; optional `mascot` image path |
| `music` | `file`, `bpm`, `phase` (seconds to the first downbeat), `final_bar` (track bar index of its last bar, to splice the ending onto the end card, or `null`), `phrase_bars`, `breakdown_before` (chapter index), `credit` |
| `hub` | contents-page `title` (words land on eighth notes) and `subtitle` |
| `chapters[]` | `title`, `sub`, optional `flag` `{text, kind: "trial"\|"exp"}`, `pain`, `benefit`, `bars`, `beats[]` |
| `beats[]` | `at` (bars after landing), `card` `{x,y,w,h}` in the 1920×1080 chapter frame, `html`; optional `morph: true` (geometry flows from the previous beat), `count` `{to, label, dur}`, `dark`, `chip`, `shot` `[x,y,scale]` to override auto-framing, `until` |
| `panel` | the Everything-else chapter: `title`, `sub`, `bars`, `benefit`, `groups[]` of `{label, rows: [[key, value]]}` |

Timing is derived, never hand-typed: chapter *i* lands at bar `L[i]`, exits at `L[i] + bars`, and the next lands
one bar later. The first dive is the music's drop at bar 1. Change `bars` and every cue, camera move and SFX moves with it.
