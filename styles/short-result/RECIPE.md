# Short result: one number in about 20 seconds

A film of about 20 s that explains **one result**: one number, one before/after, or one benchmark. It is built
for a feed (LinkedIn, X) or a busy colleague, where the film autoplays muted and has about two seconds to earn
attention. So the claim arrives as type in the first 2 s, the proof is two or three cards, and the caveat is on
screen before the end card.

It is the channel-thread motion grammar compressed to 9 bars: title words on the beats, a chat question and the
bot's one-line answer, a drop that whips out of the chat, then a short chain of cards with the numbers held long
enough to read. The runnable starter is [starter/](starter/README.md).

## When to use it

| you have | use |
|---|---|
| One result, one number or one before/after, 30 s or less, for a feed or a quick share | **short-result** |
| A joke or a single gag, silent, as a looping GIF under the feed's size cap | [gif-10s](../gif-10s/RECIPE.md) |
| A release or feature round-up with several features, 1 to 2 minutes | [channel-thread](../channel-thread/RECIPE.md) |

If the story needs a second result, it is not a short-result film. Either cut to the stronger result or move to
channel-thread and give each result its own chapter.

## Structure (9 bars at about 105 BPM, about 20 to 22 s)

| bars | what is on screen |
|---|---|
| 1 | **The claim as type.** Three or four words, one per beat ("Beacon finds it first"). This is the thumbnail and the first two seconds of a muted autoplay, so it must state the result, not the topic |
| 2 to 3 | The chat window rises and the camera pushes in. A teammate types the question in their own words; the bot answers in one line with its status flag (NOT LIVE YET, IN TRIAL) |
| drop | Ring from the bot's avatar, 0.35 s whip out of the chat, the line launches |
| 4 to 5 | **What changed**: two rows, today and new. The changed steps swap in on the beat with a small tag each (WIDER NET, REPLACES THE SORT) |
| 5 to 6 | **Before/after bars**: the headline number grows and holds. An optional faint middle bar can show where the gain comes from. One secondary figure lands underneath. A mono footnote says what was measured |
| 7 | **One big stat** (a counter, "52 / 60") and two pills (cost, latency) landing on beats |
| 8 | **The caveat card**: what has to happen before it ships, as pills |
| 9 | Short outro: the dot one beat after the last card, the wordmark two beats later, a 3-beat tail with the music credit. No map pullback, no chapter labels |

## Look

- 1920x1080 at 30 fps from the starter, dark ground, light cards, one accent colour for the winning bar and the
  swapped step. Brand tokens come from the client's site or a named profile, never from another film.
- The focal card fills 55 to 65% of the frame. Numbers are big: the winning figure is 52 px in world units on a
  card shown at about 1.3x, the big stat 150 px.
- Status flags sit on every card where the result could be mistaken for live.
- The reference was delivered 16:9 to the director over Telegram. For a feed post, square or 4:5 plays larger than
  16:9 or 9:16 (see [gif-10s](../gif-10s/RECIPE.md)); the starter is 16:9 only, so a feed cut means re-framing
  the cards for that aspect and checking the stills again.

## Pace

- About one change per second: the reference ran 1.17 changes/s and 0.40 camera moves/s. Its handoff notes
  1.17 as "over 1.1, deliberately fast for a 20 s film". The starter's scripts report against 0.9 to 1.2.
- Every key number is on screen for at least 2 s, and no hold goes past about 3.5 s. The reference held the
  headline figure about 3.2 s and every other figure and pill about 2.0 to 2.3 s.
- The camera always drifts during holds. Nothing sits still.
- All cues are on the music's beat grid, derived from `channel.json`, never hand-timed. See
  [motion.md](../../references/motion.md).

## Sound

- No voiceover. A cleared groove (95 to 120 BPM) with a build into the drop at about 7 s, plus soft synthesized
  SFX on every reveal, landing and whip. The film must still work with the sound off, because the feed plays it
  muted: every claim is type.
- The reference track had no drop of its own, so the build was made with a low-pass that opens on the drop, and
  the ending lands on a bar-line hit.
- Delivered file at -14 LUFS integrated, true peak at or below -1 dBTP (reference: -14.1 LUFS, -1.5 dBTP).
- The starter synthesizes a placeholder groove when no track is present. Never deliver on it. Credit the real
  track on the end card and claim it in the batch's music log. See [sound.md](../../references/sound.md).

## Copy and truth

- One claim, stated as narrowly as the evidence allows. The reference's brief said: "it measures the evidence
  handed to the agent, not final answers. No 'proven', no client names." The footnote on its bars card carried
  that limit on screen.
- Every figure traces to a named source file. If a figure needs a sentence of explanation to be read correctly,
  cut it rather than explain it (see the rejected framing below).
- The caveat is part of the film, not fine print: the reference's last card is "Before it goes live · 1 human
  spot check · 2 end-to-end answer test".
- See [copy.md](../../references/copy.md) and [truth.md](../../references/truth.md).

## Gates

1. **Brief.** The one result, its source file, what it does and does not measure, the audience, and the status
   flag wording.
2. **Script lock.** A short proposal: the beats table with timings, the chat lines, every figure with its source,
   and the track. The director approves it before anything is rendered.
3. **Motion preview.** For a 20 s film the preview is the whole film at draft quality: stills every 0.5 to 1 s,
   then one full render on the draft mix. Iterate on the stills first.
4. **Orchestrator frame review** of frames decoded from the MP4, including the tail, by someone who did not make
   them. The director's words go to the reviewer verbatim.
5. **Full render** with the final mix, mastered.
6. **Review** of the mastered file: loudness, peak, frames from the MP4.
7. **Deliver** only after the orchestrator clears it. Verify the API receipt and log it in `DELIVERY.log`.

Universal gate detail lives in [direction.md](../../references/direction.md) and
[deliverables.md](../../references/deliverables.md).

## QA checklist

- [ ] The first 2 s show the claim as readable type, and the claim states the result.
- [ ] `node scripts/timing.mjs`: about 1 change/s, at least 0.4 camera moves/s, 20 to 30 s total.
- [ ] `node scripts/qa.mjs` exits 0: forward and backward seeks are byte-identical, no text overflows its box.
- [ ] Every key number holds at least 2 s, measured from the stills or the timing cues, not guessed.
- [ ] Every figure matches its source file; the footnote says what was measured; no overclaiming words.
- [ ] Status flags are on every card where the result could read as live, in the brief's wording.
- [ ] No placeholder content or `PLACEHOLDER` flags remain, and no synth music.
- [ ] -14 LUFS (plus or minus 0.15) and at or below -1 dBTP measured on the delivered file.
- [ ] Frames pulled from the MP4, tail included, reviewed independently. See [qa.md](../../references/qa.md).

## Reference film (delivered; no director verdict recorded)

**`~/cs/films/jev-rerank-20s-20260928`, "Jev picks the six", 2026-09-28, 22.3 s.** An internal retrieval
result: widen the candidate pool and let a new reranker pick the six rules an agent gets.

- The ask (TASK.md): "a 22nd no voice over channel thread type video", read as a film of about 20 s whose
  purpose is to "explain the Jev reranking result ... at a glance".
- The plan (PROPOSAL.md): "9 bars ≈ 20.9 s; every cue on the 0.58 s grid" and "about 20 camera moves and
  reveals in 21 s (~1/s)".
- The render (HANDOFF.md): 22.3 s, 1920x1080, 30 fps, -14.1 LUFS, -1.5 dBTP, determinism OK, no text overflow,
  0.40 camera moves/s, 1.17 changes/s. The maker's note to the orchestrator explains the length: it runs
  22.3 s, not 20, "because of the end card's wordmark + credit tail".
- Cleared by the orchestrator on frames and delivered: DELIVERY.log records the send as "root-cleared".
- Source: `channel.json` and `film.html` on the channel-thread scaffold "with a short outro: no pullback labels,
  dot 1 beat after the last card, wordmark hit 2 beats later". The starter keeps exactly that.

## Rejected versions

No render of the reference was rejected: v1 went from the orchestrator's frame review straight to delivery.

One framing was rejected at the proposal stage. The first proposal showed the best rules in the six going from
"~2 to ~4". The orchestrator's correction, recorded in PROPOSAL.md under "Decisions": "No '~2 → ~4 of the 6'
framing or dot visual. 21% → 41% is the share of ALL the best (label-2) rules that make the 6 (recall), not how
many of the 6 are good. On screen it reads only '21% → 41% of the best rules make the 6'." The lesson: in a film
this short there is no time to explain a metric, so the on-screen wording must be literally true of the number
as measured, even if a looser phrasing reads more vividly.

For the failure modes of the parent grammar (static cards with fades, small cards in a big frame, long static
holds), see the anti-patterns in [channel-thread](../channel-thread/RECIPE.md).
