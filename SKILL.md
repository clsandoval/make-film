---
name: make-film
description: "Use when making, directing, fixing or re-rendering a short film or video: a product, release or feature film, a team catch-up, a narrated explainer, a personal trip video, a 20 s single-result clip, a 10 s LinkedIn GIF, a set of style tests to choose a look, or several variants at once. Also when an existing film reads as a slideshow, has dead screen time, reveals that miss the voiceover, a bad mix or a render that won't reproduce. Routes the request to one style (channel thread by default), each with a recipe and a starter: most are code-rendered (HTML/GSAP, Playwright, ffmpeg) and run for free; the video-model styles are paid and need the director's go-ahead."
---

# make-film

This file is a router. Pick one style from the table, read that style's `RECIPE.md`, copy its
`starter/`, and run the universal gates below. Everything style-specific lives in the recipe.
`<skill>` in any command means the directory holding this file.

## 1. Pick the style

Match the director's intent, top row first. **If nothing clearly matches, use channel-thread.**

| The director wants | Style | Starter |
|---|---|---|
| A product, release, launch or feature film; "what's new"; a feature round-up | [channel-thread](styles/channel-thread/RECIPE.md) (canonical) | `styles/channel-thread/starter/` |
| A catch-up the room follows as a list and ticks off; a table of contents; an agenda | [chapters](styles/chapters/RECIPE.md) | `styles/chapters/starter/` |
| About 2 min on 3–4 shipped pieces of one project or customer, for a room that knows the work: a contents page, each piece opened by a chat ask | [hybrid](styles/hybrid/RECIPE.md) | `styles/hybrid/starter/` |
| An explainer for people who know nothing, with narration, drawn in code (diagrams, cards) | [vo-explainer](styles/vo-explainer/RECIPE.md) | `styles/vo-explainer/starter/` |
| An illustrated or animated explainer (science, story, character) made with a video model | [voice-first-seedance](styles/voice-first-seedance/RECIPE.md) (paid: confirm spend first) | `styles/voice-first-seedance/starter/` |
| A trip, holiday or travel recap video | [trip-thread-map](styles/trip-thread-map/RECIPE.md) | `styles/trip-thread-map/starter/` |
| One result, one number or one before/after in about 20 s for a feed | [short-result](styles/short-result/RECIPE.md) | `styles/short-result/starter/` |
| A 10 s joke or GIF for LinkedIn | [gif-10s](styles/gif-10s/RECIPE.md) (paid: confirm spend first) | `styles/gif-10s/starter/` |
| "Show me some looks": compare new visual styles before committing | [style-peg](styles/style-peg/RECIPE.md) (image-model stills: confirm spend) | `styles/style-peg/starter/` |
| A narrated animatic from stills, to compare directions cheaply or when no video model is authorized | [stills-first](styles/stills-first/RECIPE.md) (image-model stills: confirm spend) | `styles/stills-first/starter/` |
| Rescue or extend a film built on `film.json` with word-locked voiceover reveals | [vo-synced-legacy](styles/vo-synced-legacy/RECIPE.md) | `styles/vo-synced-legacy/starter/` |

Tie-breaks:
- Release or feature film with narration requested: still channel-thread or chapters, unless the
  director says the audience knows nothing about the product; then vo-explainer.
- "Animated" alone does not mean a video model. An animated or illustrated explainer goes to
  voice-first-seedance only if the director wants generated footage and authorizes the spend;
  otherwise it is vo-explainer, drawn in code.
- A GIF or joke with no video-model budget: the gif-10s recipe's code-rendered fallback.
- Several variants of any style at once: run the chosen style through
  [batch-variants](references/batch-variants.md) (orchestrator plus one worker per variant).
  "Show me 3 looks" is style-peg run as a batch.
- If you can open the reference film named in the style's recipe, watch the MP4, not its brief.
  If you can't, the recipe's description of it is the reference.

Say which style you picked and why in one line to the director, then continue. Ask only if two rows
fit equally well and the choice changes the film.

## 2. Profiles

Profiles in `profiles/` hold one director's taste: palette, voice, quotes, delivery habits. **Load a
profile only when the director names one or the brief says to use it.** Otherwise do not read them.

The neutral default: take brand tokens (colours, fonts, logo) from the client's own site CSS and
published brand guide, pick the voice as a casting decision with the director, and deliver however
the director asked. Every starter ships placeholder brand values ("Beacon", "Example Co"); replace
them before anything is shown.

## 3. The universal gates

Every style runs these in order. Nothing downstream starts until the gate before it passes.

Who holds the gates: the **orchestrator** is whoever runs the film for the director. When one agent
works alone, it is the orchestrator, and the frame review in gate 4 goes to a fresh subagent that has
only the frames and the director's words. The recipe says how each gate applies to its style: a
20 s film previews whole, a silent GIF skips loudness, a style peg stops after gate 4.

1. **Brief.** `BRIEF.md`: subject in one sentence confirmed by the director, destination and aspect,
   length, palette authority, the style picked and its reference film. Style recipes add their own
   questions. → [direction](references/direction.md)
2. **Script lock.** The words (voiceover, chat messages, on-screen copy) as a table, every figure a
   named slot with a source, read straight through once. The director says lock. No voice is
   generated before this. → [copy](references/copy.md), [truth](references/truth.md)
3. **20 s motion preview.** Render about 20 s from the busiest part (the recipe names the window)
   at full quality and send it to the orchestrator, not the director. Motion, pace and framing are fixed here,
   while it is cheap. → [motion](references/motion.md)
4. **Orchestrator frame review.** Someone other than the author opens the frames (stills at
   10/35/65/90% of each hold, a labelled contact sheet) with the director's words quoted, and lists
   what is cut off, unreadable, empty or broken, worst first. → [qa](references/qa.md)
5. **Full render.** Only after 3 and 4 pass. Versioned file names, never overwritten. A note that
   arrives mid-render kills the render.
6. **Review.** The orchestrator watches the delivered file itself: frames around every cut, the mix
   measured (−14 LUFS, ≤ −1 dBTP unless the recipe says otherwise), duration and size checked.
   → [sound](references/sound.md)
7. **Deliver** the way the director asked. Send each file as it passes, confirm it arrived, log it in `DELIVERY.log`, write
   `HANDOFF.md` with credits and what you would fix next. → [deliverables](references/deliverables.md)

When the director has authorized iteration ("keep going"), continue inside that scope without
re-asking at each still. When the director orders an unattended run, the gates queue: run to a first
cut and write every skipped gate at the top of `HANDOFF.md` as a question, not a decision.

## 4. Rules for every style

- **Determinism** (code-rendered styles). No `Math.random`, `Date.now`, CSS transitions, `repeat` or `yoyo` in a composition.
  The renderer seeks; the page exposes `window.__seek`, `window.__duration`, `window.__ready`.
- **Fonts before layout.** `await document.fonts.ready` before building the timeline.
- **Stills before renders.** Iterate on stills; a still costs seconds, a render is a commitment.
- **Truth.** Every figure on screen comes from a counted fact or a named source. Placeholder figures
  never ship.
- **Verify the delivered file**, not the source: exit status, size, duration, loudness, last frame.
- **Spend.** Paid calls (voice, video or image models) need the director's go-ahead. Keep a ledger in
  the film folder, one line per call, and quote the ledger, never a recalled total. A spending stop
  ends the authorization.
- **Look before you relay.** Nothing reaches the director that the sender has not opened frame by frame.

## 5. Map

| Path | What |
|---|---|
| `styles/<name>/RECIPE.md` | When to use, look, pace, sound, gates, QA, approved and rejected reference films |
| `styles/<name>/starter/` | Copy it into a new folder and follow its README (`npm i` where it has a `package.json`) |
| `profiles/` | Per-director taste. Only when named |
| `FILMS.md` | History: every past film with date, style, verdict and lesson. It quotes one director; it is a record, not a rule, and routing never needs it |
| `references/` | Cross-cutting: direction, copy, truth, motion, sound, qa, deliverables, batch-variants, fal-seedance-25-api |
| `scripts/` | The shared legacy pipeline (VO, timeline, render, master, deliverables) plus `seedance_gen.py` and `gif_encode.sh` |
| `assets/` | Compatibility links to the old starter paths. Do not add new files here |

Needs `node ≥ 20`, `ffmpeg`, `ffprobe`, `python3`. Run `python3 scripts/check_links.py` after editing
any markdown in this repo.
