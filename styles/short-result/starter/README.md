# Short-result starter

A runnable template for the **short-result** style ([../RECIPE.md](../RECIPE.md)): a film of about 20 s that
explains one result. The claim lands as type in the first 2 s. A teammate asks in a chat channel, the bot answers
with a status flag, and on the drop the camera whips out onto a short chain of cards: what changed, the
before/after bars, one big stat, and the caveat. A short outro ends on the wordmark. Everything on screen comes
from `channel.json`.

It is the channel-thread scaffold (`../../channel-thread/starter/`) with the additions the approved reference
needed: an `outro` block for a short ending with no map pullback, `intro.cps` for faster typing, counters that
count from `data-from` with `data-dec` decimals and a `data-pre`/`data-suf` prefix or suffix, and the card
vocabulary `.pl` (method rows, `.swap` for the replaced step, `.tg` tags), `.bars` (`.faint`, `.win`), `.rec`,
`.big` and `.fn`.

**Every name and figure in `channel.json` is a placeholder** (Beacon, Example Co, sam, 48% / 60% / 81%,
2.1 → 1.3, 52 / 60, $0.001, +0.1 s). The cards carry a `PLACEHOLDER` flag so this can't be mistaken for a
result. Replace them with one counted, sourced result and remove the flags before anything is delivered.

## Commands

```bash
cp -r <skill>/styles/short-result/starter my-film && cd my-film
npm i && npx playwright install chromium
# edit channel.json: brand, channel, people, intro (title = the claim, 3-4 words), the four cards
node scripts/timing.mjs            # -> timing.json; prints duration, camera moves/s and changes/s
node scripts/stills.mjs 1          # -> stills/*.png + stills/sheet-N.png. Iterate here, not on renders
node scripts/qa.mjs                # determinism, rates, text overflowing its box (exit 1 on failure)
python3 scripts/mix.py             # -> assets/mix.wav (music on the beat grid + synthesized SFX)
node scripts/render.mjs frames/full 8          # the whole film; at 20 s this is also the motion preview
bash scripts/master.sh frames/full renders/film-v1.mp4   # -14 LUFS, <= -1 dBTP, refuses to overwrite
```

Needs Node 18+, Python 3 (stdlib only) and ffmpeg. No network calls and no paid APIs.

## Music

`music.file` points at `music/track.mp3`, which is not shipped. With no file there, `mix.py` synthesizes a
placeholder groove at `music.bpm` (`music/_synth-groove.wav`), so a fresh copy renders end to end. For delivery,
drop in a cleared track (CC BY or royalty-free, 95 to 120 BPM, with a groove), measure its tempo and first beat,
set `bpm`, `phase` and `offset`, and put the credit in `music.credit` so it shows on the end card.

## Fonts and mascot

No fonts ship. The page falls back from Inter to Helvetica Neue or Arial. To use brand fonts, put the files in
`fonts/` and add `@font-face` rules at the top of the `<style>` block in `film.html` (a missing font file shows
up as a page error and stops the scripts). Set `brand.mascot` to an image path to use it as the bot's avatar and
on the end card; without it the avatar is the bot's initial.

## channel.json keys this style uses

| key | what |
|---|---|
| `brand` | `name`, `url` (end-card line), `org`, `font`, `mono`, `palette`, optional `mascot` |
| `music` | `file`, `bpm`, `phase`, `offset`, `final_bar` (`null` for a short film), `phrase_bars`, `credit` |
| `channel`, `people` | the chat window; exactly one person has `"bot": true` |
| `intro` | `title` (the claim; words land on beats), `bars` (3: the drop is at bar 3), `cps` (typing speed), `messages[]` |
| `chapters[0].cards[]` | `w`, `h`, `beats`, `html`, optional `push[]` `{at, focus: [x, y, w, h]}` |
| `outro` | `pull` 0, `dot` 1, `hit` 2, `tail` 3 (beats) and `labels: false`: a short ending with no map labels |
| `volley`, `fixes`, `pullback` | left empty for this style |

Inside card `html`: `data-at` (beats after the card lands) reveals, `data-until` hides, `data-grow` grows a bar,
`data-count` counts up (with `data-from`, `data-dec`, `data-pre`, `data-suf`). Timing is derived from the beat
grid, never hand-typed: change a card's `beats` and every cue, move and SFX follows.
