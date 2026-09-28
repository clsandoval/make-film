# Style peg: choosing a look from stills and code-orchestrated motion

**Use when** the director wants to compare new visual styles before any film is made, and the film itself will be
built from static images animated in code (cut-out, collage, puppet, print, diagram looks where held poses and
snapped moves read as intentional).
**Do not use** to make the film (a picked peg goes to a film brief), to test a video model's look (that is a
reference pass in [voice-first](../voice-first-seedance/RECIPE.md)), or when the look is already settled.
The runnable scaffold is [`starter/`](starter/README.md).

## What one peg is

1. **A 1-2 line pitch**: why static art plus orchestrated motion suits this style, what the "limitation"
   becomes as a feature ("choppy movement is part of a school play").
2. **2-3 image-model stills of the same story beat**, so pegs compare across styles. Same cast, same beat, only
   the style changes.
3. **A silent 5-8 s motion test**, 1920x1080 H.264, built from those stills with code-orchestrated motion
   (HTML/JS page, the `lib.js` seek contract, Playwright capture, ffmpeg). It shows the style's one signature
   move: a hand of providence descending, puppets shoved up on sticks, a panel-to-panel camera.

Hard rules for every peg:

- **No video model.** The motion test is code only. A peg is a test of the static-assets method, so a
  generated clip answers the wrong question and spends money on it.
- No voiceover, no music. Light SFX in the style is optional.
- At most 8 image-model stills per peg (the cut-out pieces for the motion test count). Log every attempt; the
  log is the spend count.
- Frame-check the key beats of the motion test before it goes anywhere (`starter/scripts/peek.mjs` at each beat, a
  contact sheet with `starter/scripts/sheet.py`).
- **Stop at the peg.** No full film until the director picks a style.
- Deliver each peg as soon as it is ready (pitch, then stills, then clip), one style at a time, through the
  channel the profile or brief names.

## A second batch copies the first

When the director asks for more pegs, copy the previous batch's brief and scaffold exactly and change only the
style line. Do not write a fresh brief and do not swap in a different method.

On 2026-09-25 a new batch of ten styles was briefed with a video model for the motion tests instead of the
scaffold. The director rejected it: "only same method as the last 10". The account also ran dry on the way.
Source: the director's note of 2026-09-25, recorded in FILMS.md.

## Stills that animate

Generate the art as pieces, not as finished frames, so code can move them:

- a **plate**: the background, cover-cropped to 1920x1080;
- **cut-out sheets**: every piece separate on a flat solid magenta `#FF00FF` background, generous magenta space
  between pieces, nothing touching another piece or the image edge. `starter/art/cut.py` keys the magenta out
  and slices each sheet into trimmed RGBA pieces in reading order, with a labelled index image for review.

A prompt is four blocks: CHARACTER (the cast, with reference images used for design only: "redraw everything in
the target STYLE, do not copy the references' rendering"), STORY BEAT (the same beat for every style), STYLE
(medium, materials, palette, texture, what is forbidden, for example no lettering), and the cut-out-sheet line
above for pieces.

Reject glossy, ornate, airbrushed, over-detailed stills. In the second batch the director dropped three styles
(ukiyo-e, stained glass, explorer map) as looking "very AI-generated" and asked for "flat, imperfect, handmade
texture that reads as made by a person". Check each still against that before it is sent.
Source: `~/cs/daimon-peg2-cardboard-20260924/TASK.md`.

## Motion that reads as intentional

- Every clip page keeps the contract in `lib.js`: `window.__seek(t)`, `window.__duration`, `window.__ready`.
  GSAP's ticker is removed; nothing advances a clock, so frame N depends only on N.
- `mk(build, dur, { step: 1/12 })` quantizes film time to animate on twos at 24 fps. Use it when the style
  wants snapped, stop-motion movement; leave it off for smooth styles (blueprint draw-on, Ken Burns).
- `ease: "steps(1)"` for single-frame pose changes: squash on landing, a hinged arm snapping between angles,
  a group hopping in two-frame jolts, a three-frame camera jolt on impact.
- Grain and vignette overlays sit above the camera layer so they do not move with it.
- Screenshot the `#stage` element, never the viewport.

## Approved references

- **Batch 1 (2026-09-24)**: eight pegs (pitch plus two stills each), one motion test (Gilliam cut-out, 7.2 s).
  `~/cs/daimon-style-pegs-20260924/HANDOFF.md`, scaffold in `motion/` (`gilliam.html`,
  `lib.js`, `scripts/`), clip `clips/gilliam-raw.mp4`, prompt blocks in `art/gen.py`.
- **Batch 2 (2026-09-24)**: thirteen single-style windows, each with the same TASK.md apart from the style line,
  e.g. `~/cs/daimon-peg2-cardboard-20260924/TASK.md`. Ten of them were greenlit into full films:
  each of `~/cs/daimon-peg2-{cardboard,ikea,jrpg,postit,receipt,safetycard,saulbass,shadowpuppet,transitmap,zine}-20260924/TASK-FILM.md`
  opens with the style being greenlit and the script locked. The cardboard film's result is in its
  `FINALPASS-DONE.md` (17 s, built from the peg's stills and motion test plus at most 12 new stills).
