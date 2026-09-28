# Hybrid style: chapters × channel-thread

A contents page gives the film its structure, and inside each chapter a chat thread carries the content. A
cold open states the pain first. Each chapter starts as a teammate's question in the product's channel, the bot
answers with the feature's name and status flag, and the camera whips out of the chat into that chapter's
artifact cards. A pullback to the contents page ticks the row, and the next dive starts one bar later.

It combines the two parent styles: the spine, dives, pullbacks and map of [chapters](../chapters/RECIPE.md),
and the ask → reply → artifact grammar of [channel-thread](../channel-thread/RECIPE.md). The runnable scaffold
is [starter/](starter/README.md).

## When to use it

- A short film (about 2 to 2:30) for a room that already knows the work and the chat, covering 3 or 4 shipped
  pieces that are each big enough to need their own thread and 2 to 4 cards.
- The room should see the list and tick it off, *and* each piece is best introduced the way people meet it:
  someone asks in the channel.
- There is a real pain to open on (lost knowledge, a question nobody answers) that the chapters then resolve.

Use something else when:

- **The audience is new to the subject.** Use [vo-explainer](../vo-explainer/RECIPE.md). Without a voice, a
  room that does not know the work cannot follow three layers at once (cold open, contents page, thread and
  cards); the reference film's own subject called it unclear (see "Reference film" below).
- **It is a release round-up with many small features.** Use [channel-thread](../channel-thread/RECIPE.md),
  the default: one continuous snake with a volley for the minor features, no contents page.
- **The features have no natural question behind them**, or the room wants a checklist catch-up. Use
  [chapters](../chapters/RECIPE.md): the chapter pain is a caption, not a message.
- **Under about 90 s.** The cold open and the hub take 28 s on their own; there is no room left for threads.

## Structure

```
cold open (10 bars): title on beats · counters · tile wall · one transcript line · "nobody answers" chat · the turn line
   ─▶ contents page (bar 10): title on eighths, rows stagger in with flags, row 1 lights up
   ══ DROP ══ dive along row 1's line ─▶ #channel thread: older message fades · teammate types the ask · bot is typing · bot replies + flag
   ─whip─▶ artifact cards on a 2 × 2 grid (hand-offs, pushes) ─▶ wide shot + benefit pill ─pullback─▶ ✓ row 1, row 2 lights
   ─▶ … chapter 2 (breakdown under it) ══ RE-DROP ══ chapter 3 … chapter 4
   ─▶ all ticks glow ─▶ map pullback with labels and flags ─▶ dot ─▶ end card on the track's final hit
```

1. **Cold open, 10 bars.** Title words land on beats 1–5, then 4 counters count up one per beat. A wall of
   tiles (meetings, threads) fills the frame. One tile opens into a transcript and a line highlights: this
   is the question the film answers later. The wall dims under the pain line. A chat window shows the ask that
   nobody answers. The turn line lands and the wall lights up in the accent colour.
2. **Contents page, 1.5 bars.** It is complete within about 2 s. The first dive is the music's drop.
3. **Chapter, 8–11.5 bars.** The thread takes bars 0–2 (ask at 0.2, typing from 0.85, reply at 1.25). Cards
   start at bar 2 and land every 1.5–2 bars. The wide shot and benefit pill take the last 1.75 bars.
4. **Pullback, 1 beat**, then the ✓ lands with a chime, the next row highlights, and the next dive starts.
5. **Tie the open to a chapter.** The reference's transcript line reappears in chapter 1 and becomes the rule
   the product extracted. It links pain to product without a caption.
6. **Finale.** The map shows the tile wall, four chapters and the lines, with mono labels and flags above the
   cards. The dot travels to the end card, and the wordmark wipe lands on the final hit.

Every chapter's end state stays composed in the world, so the map shows the whole film at once.

## Look

- Dark ground with a soft radial glow and faint drifting contour lines. Light cards (26 px radius, deep
  shadow) for artifacts, dark cards with an accent border for tool calls and code.
- One accent colour for the lines, ticks, GROUNDED/PASS pills and the benefit pill. A second, warm colour is
  reserved for status flags. A third, muted colour for avatars and secondary bars.
- Wide bold display face for titles and headers, a plain sans for body and chat, a mono for kickers, ids and
  tool calls.
- Chat windows are the product's own chrome: server name, sidebar with the active channel, 44 px message text
  (about 60 px on screen at the push).
- 1920×1080, 30 fps.

## Pace (reference numbers)

| | value |
|---|---|
| Tempo | 103 BPM, bar 2.33 s, beat 0.58 s; cuts on 2- or 4-beat lines |
| Length | 60 bars, 2:19.2 (4,177 frames): cold open 0:00–0:23, contents 0:23, chapters 0:26–2:01, map and end 2:01–2:19 |
| Chapter length | 8–11.5 bars (19–27 s); 2–4 cards plus the thread |
| Camera moves | 77 in 139 s = 0.55/s; in the 20 s preview window, 11 moves and 40 beat reveals |
| Changes/s | about 1.8 including beat reveals (175 reveals) |
| Holds | 2.5–3 s on text the room must read, always drifting (+6 px/s, +0.7%/s scale, capped at 3 s) |
| Whip / push | 0.36 s quintic ease; far moves 0.55 s log-scale zoom |
| Dive | 2 beats along the line, pushing to 1.6× then dipping to 0.7× |
| Pullback | 1 beat, log-scale zoom back to the hub at 1.18× |
| Reveals | card land 0.28 s with a 30 px rise; pops with ease-back; counters 0.45–0.55 bar |
| Motion blur | directional, from screen-space camera velocity, capped at 46 px, on the screen-sized wrapper |

The film is longer than a short because it covers more, not because any moment is slower. See
[motion.md](../../references/motion.md) for the shared grammar.

## Sound

- A cleared groove at 95–120 BPM with a clear drop. Reference: "Dispersion Relation" (Kevin MacLeod,
  CC BY 4.0), 103 BPM at native speed. Credit it on the end card and in the caption, and keep the licence
  evidence next to the track.
- **Film bar grid = track bar grid.** Measure tempo and phase; every cue sits on `phase + bar × BAR`.
- **Arrangement** (`starter/scripts/mix.py`): the cold open is heavily filtered and opens a little on the turn
  line; a 0.18 s suck-out before the first dive; the full band on the drop; a 2.4 kHz low-pass breakdown under
  one middle chapter with a 600 Hz dip in its last 3 beats and a re-drop on the next dive; a splice so the
  track's last bar lands on the end card. The splice offset must be a whole number of phrases, and the script
  refuses otherwise and says how many bars to add.
- **SFX**, synthesized and placed from the page's exported cue sheet: key ticks under typing, a pop per
  message, a thud per card, pops on chips, ticks on the tile wall, a shimmer and whoosh on each dive, a
  whoosh on each pullback, a mallet chime on each ✓ and on the end card. The reference had 411 cues.
- **No voiceover.** If the room needs a voice to follow, the style is wrong for it (see "When to use it").
- Delivered file: −14 LUFS ±0.15 integrated, ≤ −1 dBTP (reference: −14.1 LUFS, −2.1 dBFS peak). See
  [sound.md](../../references/sound.md).

## Gates, in order

1. **Brief.** Audience, room, the 3–4 pieces, the pain, what is live vs merged vs in trial, and the length.
   Confirm the audience already knows the subject; if not, stop and propose vo-explainer.
2. **Script lock.** A proposal with the chapter table (bars and times), every thread line, every card, every
   figure with its source, the music and the palette. No render or paid spend before the director approves it.
   Rules for the copy: [copy.md](../../references/copy.md); for figures: [truth.md](../../references/truth.md).
3. **Stills.** `node scripts/stills.mjs 1.5`; read every sheet yourself before anyone else sees motion.
4. **20 s motion preview to the orchestrator, never to the director.** Cover the end of the cold open, the
   contents page, the drop, chapter 1's thread and first two cards (the reference used film 18–38 s).
5. **Orchestrator frame review** of frames pulled from the preview MP4. Fix every note before the full render.
   The reference preview's notes were an empty frame after the drop and an empty rule card.
6. **Full render and master**, then an independent reviewer on frames decoded from the MP4 (every 1.5 s plus
   the tail), given the director's words verbatim. Iterate until a round finds no new blocker.
7. **Orchestrator clears the full cut, then deliver** to the director. Verify the send receipt and log the
   message id in `DELIVERY.log`.

See [direction.md](../../references/direction.md) and [deliverables.md](../../references/deliverables.md).

## QA

- [ ] `node scripts/timing.mjs`: moves/s between 0.55 and 1.0; read the preview window separately.
- [ ] `node scripts/qa.mjs`: forward and backward seeks match (text antialiasing up to 4/255 is tolerated and
      reported), no text overflows its card, no contents row is too wide.
- [ ] Every sentence the room must read is on screen and still for at least 2.5 s. Counters never show a wrong
      figure under their label mid-count.
- [ ] Wide shots: no card cut at the frame edge. The reference's v1 failed review on wide-shot edge crops.
- [ ] Every figure matches its source exactly, including sample sizes. The reference's v1 also failed on "208"
      questions next to "n = 216" in the footnote; state both and say what each counts.
- [ ] Status flags in the brief's wording on the contents row, the chapter header, the bot's reply, the map
      label, and any card that could be mistaken for live.
- [ ] Illustrative names and examples are labelled *example* on screen; no client names anywhere.
- [ ] Headers and subtitles are not cropped at rest (the reference's hub subtitle was).
- [ ] Loudness, true peak and SFX presence measured on the delivered file. See [qa.md](../../references/qa.md).

## Reference film

**EAP knowledge-extraction short, v2**, 2026-09-28. Folder: `~/cs/films/rocco-short-20260928`
(`PROPOSAL.md`, `SHOTLIST-2MIN.md`, `HANDOFF.md`, `film.html`, `scripts/`). 2:19.2, no voiceover, "Dispersion
Relation" at 103 BPM, four chapters (the knowledge repo, the agent, retrieve + verify, does it work) after a
23 s cold open. Delivered to the director the same day (`DELIVERY.log`). The folder records no reaction from
the director to the delivered cut.

After delivery, the film's subject (the presenter it was cut for) said the cut had *"too much going on; super
unclear what's happening"* (recorded in `~/cs/films/eap-film-v2-20260928/BRIEF.md` and `TASK.md`). That led to
eap-film-v2, a voiceover explainer for an audience that knows nothing, in the same visual style at about 20%
slower pacing. The lesson is the "when to use it" rule above: this style assumes a room that already knows the
work.

Superseded along the way:

- **The first proposal**: 1:33 and 2:01 cuts at 120 BPM with no cold open. The director picked a slower
  track (103 BPM at native speed) and added a 20–30 s context opener, taking the main cut to 2:20.
- **The first 20 s preview** had an empty frame just after the drop and an empty rule card; both fixed before
  the full render.
- **Full cut v1** failed independent review on wide-shot edge crops and a mismatched sample size (208 vs
  n = 216); the hub subtitle crop and a channel label were also fixed in v2. v2 passed a second independent
  review with notes only (some push-ins fill about 85% of the frame, small mono type).
- **Known weak spots in v2** (`HANDOFF.md`): dives pass through about 0.3 s of near-empty frame, the map labels
  are small, and the chat history jumps rather than scrolls when a message arrives.

## Anti-patterns

- **Three layers for a new audience.** Cold open, contents page, thread and cards is a lot of grammar. For a
  room that does not know the work, it reads as noise.
- **A README list as a chapter.** Every chapter is pain (the ask), turn (the reply), product (cards), plain
  benefit (the pill).
- **Captions narrating the chat.** The ask is the pain; don't restate it over the thread.
- **Static holds.** Longer holds happen inside drifting, pushing camera motion, never on a still frame.
- **Everything small in a big empty frame.** Push until the focal card is 55–65% of the frame, and don't crop it.
