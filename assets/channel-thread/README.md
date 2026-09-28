# Channel-thread scaffold

This is the runnable template for the **channel-thread** style (`references/style-channel-thread.md`), the canonical
product, release and feature film. The film opens in the product's own chat channel. A teammate asks, the bot
answers, and on the drop the camera whips out of the chat onto one continuous canvas. An aqua line draws
through a chain of cards: each answer's artifact, then a volley of short Q&As, then the fixes cards. A map
pullback shows it all, and the end card closes. Everything on screen comes from `channel.json`.

```bash
cp -r ~/.claude/skills/make-film/assets/channel-thread my-film && cd my-film
npm i && npx playwright install chromium
# edit channel.json: brand, channel, people, intro, chapters[], volley[], fixes[]; put a cleared track at music.file
node scripts/timing.mjs            # -> timing.json; prints duration, camera moves/s and changes/s
node scripts/stills.mjs 1.5        # -> stills/*.png + labelled stills/sheet-N.png. Iterate HERE, not on renders
node scripts/qa.mjs                # determinism, rates, text overflowing its box
python3 scripts/mix.py             # -> assets/mix.wav (music arranged on the beat grid + synthesized SFX)
START=8 END=28 node scripts/render.mjs frames/preview 10   # the 20 s motion preview goes to the orchestrator first
node scripts/render.mjs frames/full 10
bash scripts/master.sh frames/full renders/film-v1.mp4     # -14 LUFS, <= -1 dBTP, refuses to overwrite
```

No music file yet? `mix.py` synthesizes a placeholder groove at `music.bpm`, so the whole pipeline runs from a
fresh copy. The example content (Beacon, Example Co, sam/lee/kai, every figure) is placeholder. Replace it, and
use only counted facts, before anything is delivered.

## channel.json

| key | what |
|---|---|
| `brand` | `name`, `url`, `org` for the end card; `palette` (CSS colours, including `panel` for chat chrome and `app` for the APP badge); `font`, `mono`; optional `mascot` image path, used for the bot's avatar and on the end card |
| `music` | `file`, `bpm`, `phase` (seconds to the first beat), `offset` (track seconds at film 0, to line the track's own drop up with ours), `final_bar` (track bar whose hit should land on the wordmark, or `null`), `phrase_bars`, `credit` |
| `channel` | `server`, `name`, `topic`, `sidebar[]` channel names |
| `people` | id → `{name, color}`; exactly one has `"bot": true` |
| `intro` | `title` (words land on beats), `bars` (the drop comes at the end, 4 by default), `messages[]` of `{who, at (beat), text, typed?}`. The last message is the bot's answer that the drop whips out of |
| `chapters[]` | `title`, optional `flag` `{text, kind: "trial"\|"exp"}`, optional `ask` `{who, text}` + `reply` (a thread card; leave both out for the chapter the intro asks), optional `breakdown: true` (the music drops out under it), `cards[]` |
| `cards[]` | `w`, `h`, `html`, `beats` (hold length; 5–8), optional `dark`, `handoff` (its revealed pieces fly into the next card), `push[]` of `{at (beat), focus: [x, y, w, h]}` in card pixels, optionally `tight: true` to let a push crop the card |
| `volley[]` | minor features as `{tag, ask, reply}`, one quick thread card each |
| `fixes[]` | `{title, items[]}`; the items land on beats |
| `pullback` | `title`, `subtitle` over the map |

Inside card `html`, reveal with attributes. They're in beats after the card's arrival:
- `data-at` makes an element appear, and `data-until` makes it leave.
- `data-grow` grows a bar from its `data-at`.
- `data-count="1240"` counts up.
- `.eq` gives a speaking waveform.

The card vocabulary classes are in the `<style>` block of `film.html`, and `channel.json` uses every one of them.

Timing is derived, never hand-typed. Every card starts on a beat, and the drop is `intro.bars`. The pullback
starts on the bar line after the last card, the dot leaves two bars later, and the wordmark lands one bar after
that. Change a card's `beats` and every cue, camera move, line segment and SFX moves with it.
