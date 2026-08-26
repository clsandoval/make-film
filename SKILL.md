---
name: make-film
description: "Use when making, directing or rescuing a product film built from code — a launch or demo video, onboarding film, feature announcement, teaser, explainer or sizzle — and when an existing one looks basic, reads as a slideshow, has reveals that miss the voiceover, dead screen time, a clipped or too-quiet mix, TTS that clicks or chops word endings, or a render that will not reproduce. Covers SaaS, apps, hardware, dev tools and services. Keywords: motion design, storyboard, voiceover sync, word-locked, kinetic typography, GSAP, Playwright, deterministic render, ElevenLabs, LUFS, ffmpeg, film grain, 9:16, captions."
---

# make-film

One command, one directory, one film. HTML/CSS/GSAP drawn frame by frame, seeked
deterministically by Playwright, mixed and mastered by ffmpeg. No GPU, no diffusion
model, no stock footage, no After Effects. The same commit produces the same file.

**A film is a directory.** `film.json` + `film.html` + the scripts. There is no state
file: the artifacts are the state. Invoked with no argument, resume at the first
missing one.

## The one rule that matters most

**Hard-gate at the human beats.** Four films were built with this pipeline in a day.
The two that were gated at every decision came out good. The one run autonomously to
a first cut came out unusable. Speed is not the constraint — a wrong direction
rendered fast is still wrong, and a render started while direction is still moving is
thrown away. Four of the first film's seven renders died that way.

**A note arriving mid-render kills the render.** Not after this one finishes.

## The seven gates

Everything between them runs unattended. Stop, show, and wait at each.

| # | Gate | Show | Passes when |
|---|---|---|---|
| **G0** | Intake | 2–3 `AskUserQuestion`s: deliverable shape, length, **destination** | Destination is decided. It determines whether there is a voiceover at all — a feed placement that autoplays muted must carry its claim as type in the first two seconds, and narration there is decoration. |
| **G1** | Direction | Three genuinely different directions, two killed with reasons, each with a named signature move → `BRIEF.md` | One is chosen, and the ONE claim survives *"would every competitor's film make this same claim?"* → `references/direction.md` |
| **G2** | Stills first | Draft frames as stills, **before any voiceover exists**. "Tell me what's wrong with these frames." | Composition and register are right. Do this and you will render three times instead of seven. |
| **G3** | Copy lock | A per-beat table: **on screen \| voice**, side by side — and the VO read straight through on its own, as one block. Then per-line alternatives for anything flagged. | The user says lock, on both. **Nothing generates voice before this.** → `references/copy.md` |
| **G4** | Pre-render | Contact sheet, stills at 10/35/65/90% of every hold, after VO and the measured timeline — **plus an independent agent that LOOKS at them** | Approved, or noted. A still is 40 seconds; a render is a commitment. |
| **G5** | Note round | The delivered MP4, plus a review encode if it is going over chat | **Two consecutive clean rounds.** Renders are versioned, never overwritten — v5 is how you prove v6 fixed it. |
| **G6** | Deliverables | Aspect cuts, captions, poster, licences, `HANDOFF.md` | Shipped. |

G2 before G3 before voice is the ordering the good films paid for. The first film
shipped a v4 before anyone tabulated screen copy against narration, and four of ten
beats turned out to be word-for-word duplicates — invisible until tabulated, because
each beat is defensible on its own.

## Setup

```bash
mkdir my-film && cd my-film
cp -r <skill>/scripts <skill>/assets/film.skeleton.html .
mv film.skeleton.html film.html
cp <skill>/assets/film.example.json film.json      # then edit it
npm init -y && npm i gsap@^3.15 playwright@^1.62 && npx playwright install chromium
```

`scripts/` must live **inside** the film directory — Node resolves `playwright`
relative to the script, not the film.

**Keys.** `ELEVENLABS_API_KEY` is the only metered service in the whole pipeline, and
only for a voiced film. Set it in the environment, `./.env`, or `~/.config/film/.env`.
The voice is a casting decision: put a voice id from your ElevenLabs library in
`film.json`, there is no default. No image generation, no video generation and no
licensed music — every sound is synthesised and every frame is drawn. Needs `node ≥20`, `ffmpeg`, `ffprobe`, `python3`.

## The pipeline

```bash
python3 scripts/gen_vo.py           # → assets/voice/*.wav + audio_meta.json
python3 scripts/fix_vo.py           # → boundary re-roll, artifact trim, 8ms fade
python3 scripts/build_timeline.py   # → timeline.json + timeline.js + vo-track.wav
python3 scripts/build_sfx.py        # → assets/mix.wav
node    scripts/stills.mjs          # → stills/  ← iterate HERE
node    scripts/probe.mjs           # → dead windows, resolution, blanks, hit tests
node    scripts/render-parallel.mjs renders/silent-v1.mp4
bash    scripts/master.sh renders/silent-v1.mp4 renders/<name>-v1.mp4
node    scripts/probe.mjs renders/silent-v1.mp4   # + shard-vs-live SSIM
python3 scripts/build_captions.py
bash    scripts/deliverables.sh
```

Run `gen_vo.py` → `fix_vo.py` → `build_timeline.py` in that order. The timeline must
be built from the *repaired* audio, because a trim changes the duration every
downstream cue is derived from.

## film.json — the only per-film contract

Nothing is hand-edited inside a script. The single authored timing number in the whole
pipeline is each frame's `pad`: the breath after its last word.

```
hold = vo.duration + pad     voiced      hold = pad     silent (no "vo" key)
```

A cue time is a number, or `["frame-id", "word"]` resolved against the same alignment
the picture is cued to. See `assets/film.example.json`.

## The renderer contract

Three globals. That is the entire API surface between composition and renderer.

```js
window.__seek = (t) => master.seek(t, false);
window.__duration = TL.duration;
window.__ready = true;
```

`assets/film.skeleton.html` is a working rig — stage, unhooked ticker, `cue()`,
`typeInto()`, `growIn()`, `countTo()`, crossfade loop, playhead-stepped grain. Copy
it. It ships the rig, not the set: the palette, type and frames are yours to derive.

## The laws

1. **Truth.** Every numeral on screen is on an approved-figures list written before a
   frame is drawn. An empty list is legitimate. The rule governs figures and claims,
   not execution — the film is *drawn*, so nothing real has to be built to make it
   honest. → `references/truth.md`
2. **The voice carries the context; the screen carries the evidence.** The viewer
   arrives knowing nothing. The voice's first job is to say who this is and why
   they should care — and every line after it must still make sense to someone
   who has never seen the product. The screen shows *what is true*; the voice
   says *what is going on*. Where the voice merely repeats the screen it is
   wasted; where it assumes context the screen has not established, it is worse
   than wasted, because the viewer stops following. → `references/copy.md`
3. **Word-locked.** Every reveal sits on a measured word start, never a typed second.
   Audio and alignment come from one generation, so they cannot disagree.
4. **Determinism.** No `Math.random`, `Date.now`, `new Date`, CSS transitions,
   `repeat` or `yoyo`. A CSS transition never fires in a seek renderer — the clock
   never advances, so you get one end value or the other and a fade that silently
   never happens. Derive noise from a seeded LCG or the playhead.
5. **Fonts before layout.** `await document.fonts.ready` before building the timeline,
   or anything measuring live geometry bakes fallback metrics into every frame.
6. **Nothing ends unresolved.** Every reveal completes by `hold − 1s`. **This governs
   resolution, not stillness** — a shot may still be moving at its cut; what it is
   *saying* may not still be arriving. Over-applying this as "zero change-points" is
   what froze 24% of a finished film. → `references/motion.md`
7. **Sound is arithmetic.** Level the asset, not the cue. → `references/sound.md`
8. **Cheap before expensive.** Stills converge, then you render.
9. **Verify the delivered file.** The source passing proves nothing about the output.

Violating the letter is violating the law. "Mostly deterministic" is
non-deterministic; "roughly on the word" is off the word.

## Red flags

Each is a real defect that cost real hours.

| The thought | What it means |
|---|---|
| "The copy is basically settled, I'll write the VO now" | Tabulate screen against voice first. Four of ten beats were duplicates and nobody saw it until v4 |
| "The visuals tell the story, the voice can be oblique" | Then nobody knows what they are watching. Read the VO alone, start to finish, with the picture off: if it does not introduce the situation and carry it, it is not a script |
| "Every line is doing real work" | Check their *shapes*. Three consecutive `setup / turn` lines read as composed, and a director will call it "two-line rhyming" before you hear it yourself |
| "That's just the correct term for it" | You learned it during the truth pass. *Catchment*, *trading*, *utilisation* — if a stranger would stop to ask, it is jargon. Check the screen copy too, the headline is where it survives |
| "This line is a great line" | Aphorisms, reversals and "X could be nothing; Y could not" read as a writer performing. Say the plain sentence |
| "Opening on silence is stronger" | Only if the screen alone establishes the situation. If the voice is carrying context, it starts at zero |
| "Re-rolling fixed the click" | Two different TTS failures. Re-roll fixes boundary clicks; a trailing artifact needs a guarded trim, or it eats word-final consonants |
| "I'll run it autonomously to a first cut" | That is exactly how the unusable one was made |
| "I'll build the real thing so the film is honest" | The film is drawn. Truth governs figures and claims, not execution |
| "The DOM checks pass, the frame is fine" | Look at the picture. One pass found a cursor that had never rendered in any frame |
| "I looked at the contact sheet myself, it's fine" | You know what you intended, so you see it. Spawn an agent that has only the frames and the director's words. It finds the crop you stopped noticing three renders ago |
| "The probe is green, so the shot works" | Every probe measures whether something *changed*, never whether it is *readable, framed, or uncropped*. Those are eyes-only |
| "I'll patch the composition with a quick replace" | A `str.replace` that matches nothing is a silent no-op that reports success. Assert before you replace |
| "Sample each beat in the middle" | Sample **10**/35/65/90%. The 10% sample is the only one that sees content painted at frame entry that should have been cued |
| "It's a series, so I'll reuse the frames" | Shared grammar is not shared frames |
| "Parallel agents can each edit a frame" | One `film.html`. Serialise |
| "The 1:1 cut is done" | Resize `#stage`, not the viewport, or you get a mislabelled aspect |
| "`-t` will fix the length" | `-t` truncates but never pads. `apad` first, or `-shortest` clips the end card |
| "It's rendering, I'll check back" | Confirm it actually started. A declined permission prompt looks exactly like a long render |
| "It sounds fine to me" | Measure it, on the delivered file |
| "Small tweak, no need to re-verify" | Small tweaks are how a −14 LUFS master became a clipped one |

## Have someone else look at the frames

**You are the worst possible reviewer of your own frames.** You know what each one
is meant to show, so your eye supplies what the picture is missing. Every layout
defect in this skill's history — a cursor that never rendered, `undefined` printed
on screen, a card sliced by the composer bar, a headline clipped off the right edge
— survived because the author looked and saw the intent.

At G4, before any render, dispatch an agent whose only inputs are:

- the image files, which it must actually open, not read the code
- what the film is supposed to be
- **the director's requirements quoted verbatim, in their own words**

Then ask it, per frame: what is cut off, what is too small to read, what is empty,
what looks broken. Tell it to be blunt and rank worst-first. A reviewer holding the
director's exact words checks them literally — which is the point, because "the text
box is cut off" is a pass/fail question about pixels, not a matter of taste.

Do this **every time the framing changes**, not once at the start.

## Reference map

Load only what the current step needs.

| File | What's in it |
|---|---|
| `references/direction.md` | Three directions, killing two, the signature move, deriving a look instead of inheriting one, the accent budget |
| `references/truth.md` | Approved figures, the refused list, sourcing real assets, genericising private material |
| `references/copy.md` | The screen-vs-voice table — the cheapest gate and the highest-value one |
| `references/motion.md` | Seek determinism, easing, staggers, resolution, and the two failure modes (slideshow / screensaver) |
| `references/sound.md` | Deterministic synthesis, the mix graph, and the mastering arithmetic |
| `references/deliverables.md` | Aspect cuts, the libass traps, captions, poster, licences |

## Definition of done

- [ ] Three directions written, two killed with reasons, recorded in `BRIEF.md`
- [ ] The film has a signature move you can name in one sentence
- [ ] It does not look like the last film you made
- [ ] Every on-screen numeral is on the approved-figures list
- [ ] The screen/voice table exists and no beat duplicates itself
- [ ] Five reveals spot-checked: opacity < 0.15 before the measured word, > 0.85 after
- [ ] `probe.mjs` clean: no dead window, every shot resolved, never blank, hits land
- [ ] Determinism: seeks byte-identical forward **and** backward
- [ ] Delivered file measures −14 LUFS ±0.5, true peak ≤ −1 dBTP
- [ ] Every SFX cue measurably present in the delivered file
- [ ] Renders versioned, never overwritten
- [ ] Two consecutive clean note rounds
- [ ] Deliverable set, licence block, and `HANDOFF.md` written
- [ ] You have written down what you would fix next
