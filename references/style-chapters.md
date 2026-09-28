# Chapters style: the contents-page film

The **documented alternative** to the canonical channel-thread style (`references/style-channel-thread.md`) for
release films, catch-ups and feature round-ups. Use it when the director wants a table-of-contents catch-up: 1–2
minutes, several features, no voiceover, and a room that should see the list and tick it off. It was built for the Daimon September release (Opus B, "The contents
page", 1:04, 2026-09-27). Carlos called it "very very good" and asked for it as a core style. The runnable
scaffold is `assets/chapters/`.

It is the One-thread / One-deck motion grammar (continuous camera, a line that draws through, cards that morph,
reveals on the beat) given a **contents page as its spine**. The room always knows where it is and how much is
left, and it never sits on a static page.

## Structure

```
contents page (hub) ──dive along line 1──▶ chapter 1 ──pullback──▶ hub ✓1 ──dive──▶ chapter 2 … 
      … ▶ "Everything else" panel (New → Fixed) ──pullback──▶ hub ✓5, all ticks glow ──▶ map pullback ──▶ end card
```

1. **Contents page, landing inside bar 0.** Title words land on eighth notes. The rows stagger in on eighths,
   status flags (IN TRIAL / EXPERIMENTAL) pop with their rows, and the camera settles from 1.42× to 1.18×. The
   page is complete at about 2 s. It must not type in line by line: the first cut spent 8 s doing that and was
   rejected as "exactly the static feel Carlos hated".
2. **The drop is the first dive.** On bar 1 the row highlights, an aqua line launches from the row's end, and
   the camera pushes into the row (to 1.75×). It then rides the line tip with motion blur (dipping to 0.85×) and
   lands on the chapter on a downbeat.
3. **Chapter:** 3–4 bars. The header lands with the dive, then the camera punches between elements on the beat
   while cards morph into each other.
4. **Pullback:** one beat of zoom out and travel back to the hub (a 0.62 scale dip). The row's ✓ lands on the
   next beat with a chime, the next row highlights on the same beat, and the next dive starts one beat later. A
   whole transition is one bar.
5. **"Everything else" panel** is the last chapter: a New card, rows landing on beats, then a 180° flip into a
   Fixed card. This is where the lighter features and fixes go, so the main chapters stay about the four big things.
6. **Finale:** pullback to the hub, and all ticks glow on the beat. A zoom-out to the whole map shows every
   chapter, the lines, and mono labels with their flags. A dot travels to the end card (mascot, wordmark, URL,
   music credit) on the track's final bar.

Every chapter's end state stays composed in the world, so the map pullback shows the whole release at once.

## Motion grammar: the numbers

| | value | why |
|---|---|---|
| Tempo | 95–120 BPM; 103 BPM in the reference (bar = 2.33 s) | 10–20% slower than the 34 s shorts at 120 BPM (Carlos's pace rule) |
| Scene-change rate | **0.6–1.0 camera moves per second** (reference: 48 moves in 64 s) | Root measured One thread at 24 in 34 s. The rejected preview had 2 in 22 s |
| Punch-in / pan | 0.34 s quintic ease, starting on a beat or eighth | a whip, not a glide |
| Dive | 1–2 beats, following the line tip | the hub → chapter link is the signature move |
| Pullback | 1 beat, with a 0.62 scale dip | reads as "back to the contents page" |
| Holds | 2.5–3.5 s, always drifting (+10 px/s, +0.8%/s scale) | "slower means longer holds inside motion, never static slides" |
| Reveals | card lands 0.12 bar (about 0.28 s) with an ease-out and a 30 px rise; chips pop with ease-back | on beats and eighths, never between |
| Morphs | geometry flows from the previous card over 0.25 bar; old content fades out in the first half, new in the second | the survivor dot → post card, template → slide 1, link → browser, composer → call → transcript |
| Motion blur | directional Gaussian from screen-space camera velocity, capped at 48 px, applied to a screen-sized wrapper (not the huge world) | a blur on the world div costs seconds per frame |
| Frame rate | 30 fps | 24 judders on the dives |

## Framing

- The focal element fills **55–65% of the frame width**. The scaffold's `autoShot()` computes the scale from
  the card's rect, clamped to 0.9–1.5×, and every beat can override it with `shot`. The hub sits at 1.18×.
- Centre the camera on the focal element. Root rejected the preview with everything small at the top left and
  a mostly empty navy frame.
- **The focal element is never cut by the frame edge at rest.** The chapter header fades out once the camera
  moves in (at 0.3 bar), and the pain line fades before the tight punches. A header left half-visible at the top
  edge reads as broken: the reviewer flagged it in six chapters.
- A strip of a wide row (five slides, a list) gets a shot at about 1.04× so both ends stay in frame.

## Three text moments per chapter

| moment | where | length |
|---|---|---|
| **Pain**: the old way, in plain words ("A new deck meant copying an old one and cleaning it up.") | under the header, landing with the dive | about 4 s, then it leaves before the tight punches |
| **Product at work**: cards doing the thing, with real artifacts and real counted figures | the beats | 2–3 bars |
| **Benefit**: one plain sentence in the accent colour ("It only speaks up when something matters.") | bottom centre, on the final wide shot | the last 0.75 bar |

This is Carlos's script rule (pain → turn → product → plain benefit) with the turn carried by the dive. Status
flags go wherever the feature's name appears: in the hub, the chapter header, the map labels, and any card that
could be mistaken for live ("IN TRIAL · POSTING PAUSED").

## Music and audio

- A **groove with a beat**, 95–120 BPM, cleared (CC BY or royalty-free). Check the licence, credit it on the end
  card and in the caption, and claim the track in the batch's `MUSIC-CLAIMS.md` before you use it. Ambient pads
  are out; so was a calm piano piece ("Dreamer") once the correction landed. Reference track: "Dispersion
  Relation" (Kevin MacLeod, 103 BPM, kit and bouncy bass).
- The **film bar grid is the track bar grid**: measure the tempo and the first downbeat (phase), and put every
  cue at `PH + bar × BAR`.
- **Build and drop:** bar 0 is filtered (high-pass plus low-pass), there is a suck-out just before bar 1, and
  the full band hits on the first dive. Put a low-passed three-beat breakdown before one late chapter (Voice in
  the reference), with a re-drop on its landing.
- **Ending:** splice the track so its last bar lands on the end card. The offset must be a whole number of
  phrases (4 or 8 bars) or the harmony jumps; `mix.py` refuses otherwise and tells you how many bars to add.
- **SFX:** a soft whoosh under every camera move (at −24 dB), a dive whoosh, a thud on the landing, a
  pullback whoosh, and a mallet chime on every ✓. Add pops on reveals, ticks on list rows, and a mallet on the
  end card. The reference had 160 cues.
- **Targets on the delivered file:** −14 LUFS ±0.15 integrated and ≤ −1 dBTP true peak (reference: −14.1 /
  −1.7, LRA 4.4). Check that SFX cues are measurably present: per cue window, the delivered audio should match
  the mix better than the music-only stem (reference: 157 of 160 present; the misses were −24 dB swishes).

## QA checklist

- [ ] `node scripts/timing.mjs`: moves/s between 0.55 and 1.0. Count the first 20 s separately; the preview
      is judged on it.
- [ ] Every sentence the room must read is on screen and still for at least 2.5 s. Numbers that count up must
      not show a wrong figure with a label. Hold the label until the count lands, or snap later stages.
- [ ] `node scripts/stills.mjs 1`: open every labelled sheet yourself, then give the sheets to an independent
      reviewer with the director's words quoted verbatim. Ask per frame: what is cut off, too small for a
      meeting-room screen, empty at rest, off-centre, misspelled, or missing its status flag?
- [ ] Check the transitions at 0.25 s steps: a returning row must never pass through a neighbour, and
      neighbours fade in only after the dive or pullback has landed.
- [ ] `node scripts/qa.mjs`: forward and backward seeks are byte-identical, and no text overflows its box.
- [ ] **Send a 20 s motion preview to the orchestrator before the full render** (intro, drop, chapter 1,
      pullback and the next landing). No full film reaches the director until the motion is cleared.
- [ ] After mastering: loudness and true peak on the delivered file, SFX presence, and frames pulled *from the MP4*
      (tail included; a sheet that pastes an unscaled frame reads as a broken last frame).

## Anti-patterns

**The rejected one: Codex "Before we start" (2026-09-27).** Carlos: *"the codex gen is so fucking ass... what
happened to the flowy beats etc"*. It had:
- **A static document with fades.** Each feature was a card that faded in, sat, and faded out, like an
  animated slide deck. There was no camera travel, no morph, and nothing hitting a beat.
- **Ambient 60 BPM music**, so there was no groove to cut on and no drop.
- **"Slower" read as "static".** The brief said slower; the fix is longer holds *inside* continuous motion.

Also rejected along the way:
- **A contents page that types itself in over 8 s**, then glides at 1–1.5 s. At 2 scene changes in 22 s, it
  was "the static feel" again.
- **12–20 s stops per feature.** Carlos: *"they should still be fast paced, maybe only 10-20% slower than the
  very first set"*. The film is longer because there is more content, not because each moment is slower.
- **Everything small in the top-left of a navy frame.** Push in and centre.
- **Punch-ins that crop the focal card**, or headers left half-sliced at the top edge.
- **A chapter that is only a list.** The only list is the Everything-else panel, and even it flips and lands
  rows on beats.
