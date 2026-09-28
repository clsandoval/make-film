# Hybrid scaffold (chapters × channel-thread)

The runnable template for the **hybrid** style (`../RECIPE.md`). A cold open states the pain, a contents page
gives the structure, and inside each chapter a chat thread carries the content: a teammate asks, the bot
answers, and the camera whips out of the chat into that chapter's artifact cards. A pullback ticks the row, a
map pullback shows the whole canvas, and the end card closes. Everything on screen comes from `hybrid.json`.

```bash
cp -r <make-film>/styles/hybrid/starter my-film && cd my-film
npm i && npx playwright install chromium
# edit hybrid.json: brand, channel, people, open, hub, chapters[], map; put a cleared track at music.file
node scripts/timing.mjs            # -> timing.json; prints duration, chapter times, moves/s and changes/s
node scripts/stills.mjs 1.5        # -> stills/*.png + labelled stills/sheet-N.png. Iterate HERE, not on renders
node scripts/qa.mjs                # determinism, move rate, text overflowing its box; exits 1 on failure
python3 scripts/mix.py             # -> assets/mix.wav (music arranged on the bar grid + synthesized SFX)
node scripts/shots.mjs 26.8 33.5   # single frames at exact times, e.g. a push landing
START=18 END=38 node scripts/render.mjs frames/preview 8   # the 20 s motion preview goes to the orchestrator first
node scripts/render.mjs frames/full 12
bash scripts/master.sh frames/full renders/film-v1.mp4     # -14 LUFS, <= -1 dBTP, refuses to overwrite
```

No music file yet? `mix.py` synthesizes a placeholder groove at `music.bpm`, so the whole pipeline runs from a
fresh copy. Replace it with a cleared track before anything is delivered. Fonts are not bundled: the stacks fall
back to system sans and mono. Put licensed font files in `fonts/` and list them in `brand.fonts`.

The example content (Beacon, Example Co, sam/lee/kai, every figure) is placeholder. Replace it, and use only
counted facts, before anything is delivered.

## hybrid.json

| key | what |
|---|---|
| `brand` | `name`, `org`, `url` for the end card; `palette` (CSS colours: `ground`, `deep`, `ink`, `accent`, `accent2`, `card`, `cardInk`, `flag`, `peri`); `font`, `head`, `mono`; `fonts[]` of `{family, src, weight, style}`; optional `logo` and `mascot` image paths (`null` is fine: the bot gets a letter avatar and the end card is type only) |
| `music` | `file`, `bpm`, `phase` (seconds to the first downbeat), `splice_to_track_bar` (track bar the last chapter's exit is spliced to so the track's ending lands on the end card, or `null`), `phrase_bars`, `credit` |
| `channel` | `server`, `name` (the thread channel), `topic`, `sidebar[]` |
| `people` | id → `{name, color}`; exactly one has `"bot": true` |
| `open` | the 10-bar cold open: `title` (words land on beats), `counters[]` of `{value, label, suffix}`, `tile` (label on the wall tiles), `first_year`, `transcript` `{kicker, who, quote}`, `line1` (the pain), `chat` `{channel, sidebar, who, text, sys, tm}` (the unanswered ask), `line2` (the turn) |
| `hub` | contents-page `title` and `subtitle` |
| `chapters[]` | 1–4 chapters: `title`, `sub`, `flag`, `bars`, `benefit`, optional `benefit_at` (bars, default `bars − 1.75`), optional `breakdown: true` (music low-passed under it, re-drop on the next dive), `thread`, `cards[]` |
| `thread` | `before` `{who, text, tm}` (an older message that fades), `ask` `{who, text, tm}` (typed in), `reply` `{text, flag, tm}` (the bot) |
| `cards[]` | `at` (bars after the chapter lands; the thread takes bars 0–2), optional `slot` `[col, row]` (default order `[1,0] [2,0] [2,1] [1,1]`), `dark`, `push` (bars after `at` for the push-in, default 0.6, `null` for none), and either `html` or `thread` `{channel, topic, sidebar, messages[]}` with messages `{who, text, at, tm, typing?}` |
| `map` | `title` over the map pullback |

All times are in bars; 0.25 is one beat. Inside card `html`, `data-at` is in bars after the card lands, and
reveals are chosen with `data-k`:
- no `data-k`: land (rise and fade in). `pop`: scale pop. `type`: types its text over `data-dur` bars.
- `count` with `data-to` (and optional `data-suf`, `data-dec`, `data-dur`): counts up.
- `grow` with `data-w` (percent): grows a bar. `swap`: two stacked children cross-fade. `hl`: highlight.
- Card classes: `.k` kicker, `.big` figure, `.lab`, `.row`, `.ok` tick, `.chip`, `.pill` (`.pe` for the flag colour), `.quote`, `.tiles`, `.hbar`, `.sk`/`.cardsk` skeleton lines, `.stack`, `.mono`.

Timing is derived, never hand-typed. The contents page lands on bar 10, chapter 1 lands on bar 11.5, each
chapter exits after its `bars`, and the next lands one bar later. The map, dot and end card follow the last
exit. Change `bars` or a card's `at` and every cue, camera move, line and SFX moves with it.
