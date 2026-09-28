# Channel-thread style: the #channel film

This is **the canonical default for product, release and feature films**: 1–2 minutes, several features, no
voiceover, for a room that knows the product's chat. It was built for the Daimon September release (Opus C,
"The #daimon channel", 1:19, 2026-09-27). The director: *"i really like opus c"*, and asked for it to be the
canonical form. The runnable scaffold is [`starter/`](starter/README.md). The documented alternative for a
table-of-contents catch-up is [chapters](../chapters/RECIPE.md); the two mixed is [hybrid](../hybrid/RECIPE.md).

**The medium is the message.** Staff meet the product in a chat channel, so the film opens in one. Every
feature arrives the way people actually meet it: a teammate asks, the bot answers, and the answer **expands
out of the chat into its artifact**. It is the One-thread motion grammar (continuous camera, a line that draws
through, cards that fill themselves and hand off, reveals on the beat) with the channel as its spine.

## Structure

```
title words on the beats ─▶ #channel window: release post · teammate types the pain · bot answers (IN TRIAL)
   ══ DROP ══ ring from the bot's avatar, whip out of the chat ─▶ one snake canvas, accent line drawing under it:
   chapter 1 artifact cards (hand-offs) ─whip─▶ [ask thread card] ─▶ chapter 2 cards ─▶ … ─▶ [ask] ─▶ breakdown chapter
   ══ DROP 2 ══ ─▶ volley: 4 quick thread cards (minor features) ─▶ fixes card(s) ─▶ map pullback ─▶ dot ─▶ end card
```

1. **Intro, inside the first 4 bars.** The title words land on beats 1–4. The title shrinks as the channel
   window rises, and the camera pushes into the messages (1.3×). The bot posts the release, a teammate *types*
   the first pain as a question, "Bot is typing…", and the bot answers with the feature name and its status
   flag.
2. **The drop is the exit from the chat.** On the downbeat a ring pulses from the bot's avatar. The camera whips
   (0.35 s, motion-blurred) onto the canvas, and the line launches from that avatar.
3. **A chapter is 1 thread card + 1–3 artifact cards.**
   - The first chapter's question was asked in the intro, so it has no thread card.
   - The thread card is the question, in the teammate's own words, and the bot's one-line answer.
   - The artifact cards are the product at work, with real artifacts and counted figures. They fill themselves
     on the beat and hand pieces to each other (source chips fly into the funnel's first bar; the "1" bar hands
     off to the would-post card; slides fly out of the template).
4. **Breakdown under one late chapter.** The music thins out (hats out, or a low-pass) under the quietest
   feature (Voice in the reference). The re-drop lands on the whip into the volley.
5. **Volley.** The minor features are one quick thread card each, with a feature tag in the card's header
   (WATCHES, NOTION, AGENT KEYS, SOURCE STATUS). Each has an ask and a reply, 2.4–3 s per card, with glides
   between.
6. **Fixes, as a reactions card.** "Also fixed in this release", with ✓ pills landing on beats. A second card
   ("Faster and steadier") holds the rest.
7. **Map pullback.** The whole snake shows at about 0.19×, with the headline and subtitle above it and mono
   chapter labels with their flags. The labels sit *above* the cards, never on them. Then a dot travels from
   the line's end to the end card (mascot, wordmark, URL, org, music credit), and the wordmark wipe lands on the
   track's final hit.

## Motion grammar: the numbers

| | value | reference (Opus C v2) |
|---|---|---|
| Tempo | groove at 95–120 BPM, with a build and at least one drop | "Chill Wave", 100 BPM, bar 2.4 s |
| Scene changes | **0.8–1.1 changes/s**: camera moves plus beat-locked reveals, posts and hand-offs | root measured about 0.95/s, with 18 in the 20 s preview window. The rejected m1 preview had 0.3/s |
| Camera moves | ≥ 0.4 camera moves/s on their own | 31 camera moves in 78.6 s |
| Whip | 0.35 s quintic ease-in-out, directional motion blur from screen-space velocity (cap 46 px) | between chapters, into thread cards, on row changes, on both drops |
| Glide / hand-off | 0.4–0.5 s cubic ease-in-out | card to card inside a chapter, and volley card to volley card |
| Push / reframe | 0.4 s cubic ease-in-out, 1–2 per artifact card, on a beat | onto the "1 would post" bar, the render-check pill, the share panel |
| Holds | **2.4–3.5 s, always drifting**: +18 px/s (capped at 3 s) and +1.2% scale per s (capped at 3.5%) | the funnel was up 3.5 s and the would-post card 3.1 s. m1 held 5–6 s and was rejected |
| Card land | 0.3 s ease-out, 36 px rise, 0.96 → 1 scale, on the move's landing | |
| Message post | 0.25 s, 22 px rise; ask on the beat after landing, reply 1 beat later | a typing indicator runs for 1.2 beats before bot posts in the intro |
| Counters | count up over 0.55 s. The text counter-scales against its growing bar, or it squashes | a reviewer caught "1,055" squashed mid-grow |
| Frame rate | 30 fps | |

The pace rule, from the director who approved this style: *"they should still be fast paced, maybe only 10-20% slower than the very first set"*.
Match the 34 s shorts' cut rhythm plus 10–20%. The film is longer because it covers more features, not because
any moment is slow.

## Framing

- **The focal card fills 55–65% of the frame by area.** The scaffold's `autoShot()` scales by
  `sqrt(0.6 · 1920 · 1080 / (w · h))`, clamped so the card fits (w·s ≤ 1780, h·s ≤ 960), at 0.9–1.5×.
  - Thread cards end up at about 1.7×, which gives about 60 px chat type on screen. That reads in a meeting room.
  - Big artifact cards end up at 1.1–1.4×.
- **A push never crops its own card**, unless you mark it `tight: true`. The reference's round-1 blockers were
  all crops on pushes: the Artifact share panel with its EXPERIMENTAL badge cut, the Voice title and tiles cut,
  the transcript shot cutting the voice header. The fix was small pans at 1.3×, not tight pushes at 1.45–1.6×.
- **Chat type is large.** Message text is 37 px in world units (about 60 px on screen), names 32 px,
  timestamps 21 px mono. Never fewer than 25 px in world units for anything the room must read.
- **Neighbouring cards partly in frame are the continuous-canvas look.** Don't fight them. But a card must not
  overlap its neighbour (in round 1 the template cover sat on the ask card), and the chat sidebar must not be
  cropped in the intro push.
- **Status flags go everywhere the feature is named**: the bot's reply, the artifact card's header, the
  pullback label, and any card that could be mistaken for live ("WOULD POST · IN TRIAL", "Not posted to
  Discord: paused in trial"). Use the director's wording: a reviewer failed "Not sent: posting paused" because
  the brief said *Discord posting paused*.

## Copy: pain as the team's own messages

The script rule (pain → turn → product → plain benefit, see [copy](../../references/copy.md)) maps onto the channel with no captions:

| moment | where | reference |
|---|---|---|
| **Pain** | a teammate's message, lower-case, the way people type | "anyone keeping an eye on competitors?", "can you start the Q3 deck from our template?", "can the client click through these results?" |
| **Turn** | the bot's one-line reply, with the feature name and its flag | "Market Pulse does now. IN TRIAL", "I turned them into a page. EXPERIMENTAL" |
| **Product** | the artifact cards, with real artifacts and counted figures only | a four-stage funnel from items gathered down to the one that would post, every stage a counted figure from a real sample run |
| **Benefit** | a pill or a short line on the last card, not a caption | "✓ Only slide 3 changed", "Checked against its source" |

- Fewer words than it looks. The most text-heavy card (the would-post message) got 3.1 s plus a push-in.
- Names are illustrative and generic (maya, tomas, ines in the reference). No client names, and no private data.

## Music and audio

- **Choose a groove with a beat** at 95–120 BPM, cleared (CC BY or royalty-free).
  - Check the licence, credit it on the end card and in the caption, and claim the track in the batch's
    `MUSIC-CLAIMS.md` before you use it.
  - Calm tracks are out: "Vibing Over Venus" was released as too calm after the motion correction.
  - Reference: "Chill Wave" (Kevin MacLeod, 100 BPM). It has a bass-only intro, a hats-out breakdown, a no-bass
    breakdown into a big drop, and a final hit.
- **Put the film's beat grid on the track's beat grid.** Measure the tempo and phase (librosa's beat tracker,
  then check the onsets). Every cue sits on `phase + n · beat`.
- **Edit the track on bar lines, with the same phase modulo the chord cycle** (4 bars) at every splice, or the
  harmony jumps. The reference edit:

  | film | track | use |
  |---|---|---|
  | 0–10.0 s | 143.6–153.6 s | build, low-pass opening up |
  | 10.0 s | 153.6 s | the track's own drop |
  | 10.0–41.2 s | 153.6–184.8 s | groove |
  | 41.2–48.4 s | 69.6–76.8 s | hats-out breakdown under Voice |
  | 48.4 s | 76.8 s | drop 2 |
  | 48.4–72.4 s | 76.8–100.8 s | groove |
  | 72.4 s | 225.6 s | bass-only bar |
  | 74.8 s | 228.0 s | final hit on the wordmark |

  Crossfade each splice over 30 ms. Check that onsets after each splice sit on the 0.6 s grid.
- **SFX:** synthesized and deterministic, placed from the page's exported cue sheet (`__timing`, never hand
  times).
  - Soft key ticks under typing.
  - Distinct pops for user and bot posts.
  - A whoosh under every whip, glide and push (whips at −10 dB, pushes at −22 dB), a ring shimmer on the drop,
    and a thud on each card landing.
  - Ticks on reveals, a chime on the funnel's last stage, and a mallet on the end card.
  - The reference had 146 cues.
- **Targets on the delivered file:** −14 LUFS ±0.15 integrated and ≤ −1 dBTP true peak (reference: −14.0 /
  −2.0, LRA 6.2).
  - The delivered audio correlates ≥ 0.99 with the premaster once you allow for the ~2 ms AAC offset (reference:
    0.995). Search the lag; a zero-lag correlation reads 0.42 and looks like a broken mux.
  - Every SFX cue is present (146 of 146).

## Gates (in this order)

1. **Direction approved** (it usually is: this is the default).
2. **Stills.** A contact sheet every 1.2–1.6 s. Look at it yourself first.
3. **The 20 s motion preview, sent to the orchestrator, never to the director.** It covers the intro's end,
   the drop, chapter 1 and the whip into chapter 2 (film 8–28 s). It is judged on framing, hold length and
   changes/s.
   - The reference's m1 was sent back ("cards fill about 25% … holds about 6 s … 0.3/s").
   - m2b was cleared ("framing much bigger, holds about 3 s, 18 moves in 20 s").
4. **Full render, then an independent reviewer on frames decoded from the MP4.** Give the reviewer the
   director's words verbatim. Iterate until a round finds no new blocker; a note that reappears is a regression.
5. **The orchestrator clears the full cut**, and only then does it go to the director. Confirm it arrived
   and log it in `DELIVERY.log`.

## QA checklist

- [ ] `node scripts/timing.mjs` shows ≥ 0.4 camera moves/s and 0.8–1.1 changes/s. Read the 8–28 s window
      separately; the preview is judged on it.
- [ ] Holds are 2.4–3.5 s, and none is static: the drift is always on. Nothing the room must read is on
      screen for less than 2.4 s.
- [ ] The focal card is 55–65% of the frame, and no card is cropped at rest or on a push. Check the frames at
      each push's landing, not only at the stills' 1.5 s spacing.
- [ ] No overlaps: template on ask card, chips on avatars, pullback labels on cards.
- [ ] Status flags are visible, in the brief's wording, on every card where the feature appears.
- [ ] Figures are counted facts only (release notes, a sampled run, the repo). Example or placeholder numbers
      say so on screen, or they don't ship.
- [ ] Counters don't squash: the text counter-scales against its growing bar.
- [ ] `node scripts/qa.mjs`: forward and backward seeks are byte-identical, and no text overflows its box.
- [ ] Loudness, true peak, lag-searched correlation and SFX presence, all measured on the delivered file.
- [ ] Frames pulled *from the MP4*, the tail included, reviewed by someone who didn't make them.

## Anti-patterns

- **The rejected one: Codex "Before we start" (2026-09-27).** The director: *"the codex gen is so fucking ass...
  what happened to the flowy beats etc"*.
  - It was a static document with fades: each feature was a card that faded in, sat, and faded out.
  - There was no camera travel, no hand-offs, and nothing on a beat.
  - The music was ambient at 60 BPM.
- **This style's own first build (Opus C slow v1), killed mid-render.** It was a slowly scrolling chat window
  in which each answer expanded into an overlay card and folded back, on a calm 94 BPM track, with 12–20 s per
  feature. The expand/fold idea was right. Doing it inside a static window, at meeting pace, was "the static
  feel" again. **Slower means longer holds *inside* continuous motion, never a static frame.**
- **Small cards in a big empty frame.** m1 had the focal card at about 25% of the frame, and root sent it back.
  Push in until the card is 55–65%.
- **Pushes that crop the card they push on.** A push is a reframe inside the card, not a crop.
- **Long type-ons as the only motion.** The funnel sat for 6 s while its rows typed in, and the would-post card
  5 s. Cap holds at about 3.5 s and push or drift during them.
- **Captions narrating the chat.** The pain is already a teammate's message. Don't add a caption over it
  restating it.
- **The fixes as a wall of text.** Pills landing on beats, 4 per card, two cards if needed.
