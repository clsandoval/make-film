# VO-synced (legacy): the code-rendered, word-locked voiceover pipeline

**When to use.** Only when the director asks for a narrated film whose reveals must land on
spoken words, with a synthesized mix and a broadcast master, and none of the newer styles fits.
This was the skill's first pipeline. It still works, but it is not a default: a narrated explainer
starts at [vo-explainer](../vo-explainer/RECIPE.md), a product or release film at
[channel-thread](../channel-thread/RECIPE.md).

**The starter** is `starter/film.skeleton.html` + `starter/film.example.json` with the shared
Python/Node pipeline in the repo's `scripts/` (gen_vo, fix_vo, build_timeline, build_sfx, stills,
probe, render, master, deliverables).

The universal gates in [SKILL.md](../../SKILL.md) still apply. The G0–G6 table below is the
finer-grained version this pipeline was built around.

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

## Default gates for a new code-rendered film

Everything between them runs unattended. Stop, show, and wait at each.

| # | Gate | Show | Passes when |
|---|---|---|---|
| **G0** | Intake | Four `AskUserQuestion`s — deliverable shape, length, **destination**, **whose palette wins** — plus the subject named back in one sentence for a yes/no | Destination is decided, the subject is confirmed in the director's own words, and one palette authority is named. |
| **G1** | Direction | Three genuinely different directions, two killed with reasons, each with a named signature move → `BRIEF.md` — written after reading the subject's published brand guideline and **watching the sibling films, the MP4s not their briefs** | One is chosen, the ONE claim survives *"would every competitor's film make this same claim?"*, and the guideline's hard constraints are listed in `BRIEF.md`. → `../../references/direction.md` |
| **G2** | Copy lock | A per-beat table: **# \| frame \| on screen \| voice**, every figure a named slot — and the VO read straight through on its own, as one block. Then per-line alternatives for anything flagged. Show it inline. Print only **on screen \| voice** for the lock — `#` and `frame` are
join keys for the persisted file, not columns the director reads. | The user says lock, on both, and every slot has a source. **Nothing generates voice before this.** → `../../references/copy.md` |
| **G2.5** | Truth pass | `truth/generate.py` → `truth/fit.py` → `fit.js`, then every named slot filled from it | Every slot on screen traces to a posterior or a counted fact, and anything that cannot be sourced is on the refused list. Run it before the storyboard: it is the step most likely to change the scenario. → `../../references/truth.md` |
| **G3** | Storyboard, then stills | The locked beats drawn — layout per beat, then rendered as real stills **before any voiceover exists** — which means a pad-only timeline: `build_timeline.py` raises `KeyError: <frame-id>` on any frame carrying a `vo` string with no `audio_meta.json` behind it, so comment the `vo` values out (or point `FILM_ROOT` at a pad-only copy of `film.json`) for this pass. Dead-window numbers measured pad-only are void — re-run the probe once the real timeline exists. "Tell me what's wrong with these frames." | Composition, register and density are right, **and no note from the previous round has recurred.** Do this and you will render three times instead of seven. |
| **G4** | Pre-render | Contact sheet, stills at 10/35/65/90% of every hold, after VO and the measured timeline — **plus an independent agent that LOOKS at them** | Approved, or noted — and a note that has now appeared in two independent review rounds sends the film back to G3, it does not become a G6 flag. A still is 40 seconds; a render is a commitment. |
| **G5** | Note round | The delivered MP4, plus a review encode if it is going over chat | **Two consecutive clean rounds**, and a round in which an old note reappears is not clean. Renders are versioned, never overwritten — v5 is how you prove v6 fixed it. |
| **G6** | Deliverables | Aspect cuts, captions, poster, licences, `HANDOFF.md` | Shipped. |

A feed placement that autoplays muted must carry its claim as type in the first two
seconds, and narration there is decoration. One film was built about a company's
*programme* when the subject was the *product* named after it. Unasked, palette authority
got shouted twice in opposite directions — once for the product's own site CSS, once for
the parent company's brand kit.

**A premise that moves after G1 is a re-gate, not a patch.** One film's product premise
changed after 11 VO lines were recorded and five storyboard QA passes had run; two lines
were dead and the correction landed mid-loop. Re-run G1, then audit every downstream
artifact the change invalidates — recorded VO first, then the approved-figures list.

Two versions of one film were built in a register its guide forbids, down to a hand-recoloured
light wordmark, and the correction was four simultaneous reversals — ground, layout,
numbering, logo treatment. A series designed off three `BRIEF.md` files without opening one
MP4 cost an hour: a brief records what a film meant to argue; the grammar you inherit or
break exists only in frames.

Copy before frames before voice is the ordering the good films paid for.

**The script sets the beat count and the beat boundaries**, so it is the only thing a
storyboard can be a storyboard *of*. Draw first and you lay out beats the script then
splits, merges or deletes. A fourth film wrote copy first; one note on the opening two
lines turned them into three beats and collapsed a held beat elsewhere. Nothing had been
drawn, so it cost a table edit. Storyboarded first, it is a redraw.

The defect the copy gate exists to catch is the screen repeating the voice, and stills
do not catch it — **tabulation does**. Author the copy AS the screen-vs-voice table and
it is caught at writing time, for free. The first film shipped a v4 before anyone
tabulated, and four of ten beats turned out to be word-for-word duplicates — invisible
until tabulated, because each beat is defensible on its own.

And **every figure in the script is a named slot**, never a number. The truth pass has
not run yet; it is the step most likely to change the scenario. A script written around
numbers the fit has not produced is a script you rewrite. Slots also mean the VO can be
locked and generated while the figures are still moving, because no numeral is spoken. The
slots get filled at G2.5, from `truth/` — a seeded generator, a PyMC fit, and `fit.js` as the
only data `film.html` reads. → `../../references/truth.md`

## Setup

```bash
mkdir my-film && cd my-film
cp -r <skill>/scripts <skill>/styles/vo-synced-legacy/starter/film.skeleton.html .
mv film.skeleton.html film.html
cp <skill>/styles/vo-synced-legacy/starter/film.example.json film.json      # then edit it
npm init -y && npm i gsap@^3.15 playwright@^1.62 && npx playwright install chromium
```

`scripts/` must live **inside** the film directory — Node resolves `playwright`
relative to the script, not the film.

**Keys.** `ELEVENLABS_API_KEY` is the only metered service in the pipeline, and only
for a voiced film. `scripts/film.py` reads it from the environment, then `./.env`, then
`~/.config/film/.env` — and if it is in none of the three, search your other repos'
`.env` files for `ELEVENLABS_API_KEY`. Exactly one hit: copy it to `~/.config/film/.env`.
Zero or several: ask the director which key, and never stall on it — one session stalled
for hours on a missing key and spent them timing stills against durations that were
already stale. The voice is a casting decision: put a voice id from your ElevenLabs
library in `film.json`, there is no default. No image generation, no video generation and no
licensed music — every sound is synthesised and every frame is drawn. Generated footage,
when a director asks for it, leaves this pipeline and is metered: keep a ledger in the
film directory, one line per generation — `shot · model · duration · credits · balance
after · kept/discarded` — and quote the ledger, never a recalled total.

Needs `node ≥20`, `ffmpeg`, `ffprobe`, `python3`.

## The pipeline

```bash
python3 truth/generate.py           # → truth/*.csv + facts.json   G2.5, only if the film has figures
python3 truth/fit.py                # → truth/fit.json             one seed, PyMC
#   then merge the two JSONs into fit.js — the exact one-liner is in references/truth.md
python3 scripts/gen_vo.py           # → assets/voice/*.wav + audio_meta.json
python3 scripts/fix_vo.py           # → boundary re-roll, artifact trim, 8ms fade
python3 scripts/build_timeline.py   # → timeline.json + timeline.js + vo-track.wav
python3 scripts/build_sfx.py        # → assets/mix.wav
node    scripts/stills.mjs          # → stills/  ← iterate HERE
node    scripts/probe.mjs           # → dead windows, resolution, blanks, hit tests
node    scripts/render-parallel.mjs renders/silent-v1.mp4 [shards]
bash    scripts/master.sh renders/silent-v1.mp4 renders/<name>-v1.mp4
node    scripts/probe.mjs renders/silent-v1.mp4 [shards]   # + shard-vs-live SSIM
node    scripts/dump_copy.mjs       # → the screen-vs-voice table, re-run from the picture
python3 scripts/build_captions.py
bash    scripts/deliverables.sh
```

`render.mjs` is the serial equivalent of `render-parallel.mjs`, for a short film or a
debug pass. The **shard count must be the same in both probe and render** — they default to
the same expression and `film.json`'s `shards` pins it — because the probe derives its seam
frame numbers from it and a mismatch checks frames that are not seams.

Run `gen_vo.py` → `fix_vo.py` → `build_timeline.py` in that order. The timeline must
be built from the *repaired* audio, because a trim changes the duration every
downstream cue is derived from. `gen_vo.py` is **incremental**: it reads the existing
`audio_meta.json` and skips any line whose `vo` text is unchanged and whose wav still exists,
so a one-line copy fix costs one generation and every approved take survives. The skip key is
the `vo` text and the wav's existence — **nothing else**. Changing `voice.id`, `model` or any
`voice_settings` value re-rolls nothing, and `audio_meta.json` is still rewritten with the new
`voice_id` over the old voice's audio, so the provenance file states something false. Delete
`audio_meta.json` after any change to the `voice` block; deleting `assets/voice/<id>.wav`
re-rolls that one line.

`film.py` and `film.mjs` parse `film.json` for every Python and Node script. `FILM_ROOT`
repoints them at another film; `master.sh` and `deliverables.sh` both `cd` to the project root
and ignore your working directory, so neither honours it. `FILM_PAGE`/`FILM_W`/`FILM_H` render
another composition at another aspect.

## film.json — the only per-film contract

Nothing is hand-edited inside a script. The single authored timing number in the whole
pipeline is each frame's `pad`: the breath after its last word.

```
hold = vo.duration + pad     voiced      hold = pad     silent (no "vo" key)
```

A cue time takes four forms, all resolved against the same alignment the picture is cued to
(`resolve_time` in `film.py`, `resolveTime` in `film.mjs`):

```
1.22                                            a number
["03-close", "whole"]                           a word
["03-close", "whole", 2]                        the nth occurrence of that word
{"frame": "02-claim", "word": "thread", "offset": -0.12}   just off a word
```

**Prefer a word form.** A number does not survive a VO regeneration — three ticks written as
`14.2 / 15.6 / 17.0` migrated into the wrong beat when one line was re-recorded and nothing
failed — so it is only legitimate in a film with no voiceover.

`probes` configures `probe.mjs` and nothing else reads it:

```
"probes": {
  "scope": "#stage",                     what counts as content; default ".scene"
  "resolution_exempt": ["03-close"],     frames that legitimately never settle
  "hits": [{ "cursor": "cur", "target": "authorize",
             "at": ["02-claim", "thread"], "tip": [4, 2] }]
}
```

`scope` is the one to get right: a walk that matches nothing reports green on an empty set,
and three of four films needed `#stage`. `tip` is the cursor tip's offset from its node
origin, default `[4, 2]`. See `starter/film.example.json` and `../../references/qa.md`.

## The renderer contract

Three globals. That is the entire API surface between composition and renderer.

```js
window.__seek = (t) => master.seek(t, false);
window.__duration = TL.duration;
window.__ready = true;
```

`starter/film.skeleton.html` is a working rig — stage, unhooked ticker, `cue()`,
`typeInto()`, `growIn()` (two tweens, deliberately), `countTo()` (locale pinned), crossfade
loop, playhead-stepped grain marked `data-camera`. Copy it. It ships the rig, not the set: the
palette, type and frames are yours to derive. Its `#stage` and `film.example.json`'s `stage`
are both 1080x1920 and must stay in sync — the CSS is what a browser preview shows, the JSON
is what gets shot.

## The laws

1. **Truth.** Every numeral on screen is on an approved-figures list written before a
   frame is drawn. An empty list is legitimate. The rule governs figures and claims,
   not execution — the film is *drawn*, so nothing real has to be built to make it
   honest. → `../../references/truth.md`
2. **The voice carries the context; the screen carries the evidence.** The viewer
   arrives knowing nothing. The voice's first job is to say who this is and why
   they should care — and every line after it must still make sense to someone
   who has never seen the product. The screen shows *what is true*; the voice
   says *what is going on*. Where the voice merely repeats the screen it is
   wasted; where it assumes context the screen has not established, it is worse
   than wasted, because the viewer stops following. → `../../references/copy.md`
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
   what froze 24% of a finished film. → `../../references/motion.md`
7. **Sound is arithmetic.** Level the asset, not the cue. → `../../references/sound.md`
8. **Cheap before expensive.** Stills converge, then you render.
9. **Verify the delivered file.** The source passing proves nothing about the output.

Violating the letter is violating the law. "Mostly deterministic" is
non-deterministic; "roughly on the word" is off the word.

## Red flags

Each is a real defect that cost real hours.

| The thought | What it means |
|---|---|
| "The copy is basically settled, I'll write the VO now" | Tabulate screen against voice first. Four of ten beats were duplicates and nobody saw it until v4 |
| "I'll storyboard first, the copy can catch up" | The script decides how many beats there are. Draw first and you redraw when a line splits a beat in two |
| "I know roughly what the numbers will be, I'll write them into the script" | Slots, not numerals. The truth pass has rewritten the scenario in every film that ran one |
| "The visuals tell the story, the voice can be oblique" | Then nobody knows what they are watching. Read the VO alone, start to finish, with the picture off: if it does not introduce the situation and carry it, it is not a script |
| "Every line is doing real work" | Check their *shapes*. Three consecutive `setup / turn` lines read as composed, and a director will call it "two-line rhyming" before you hear it yourself |
| "That's just the correct term for it" | You learned it during the truth pass. *Catchment*, *trading*, *utilisation* — if a stranger would stop to ask, it is jargon. Check the screen copy too, the headline is where it survives |
| "This line is a great line" | Aphorisms, reversals and "X could be nothing; Y could not" read as a writer performing. Say the plain sentence |
| "Opening on silence is stronger" | Only if the screen alone establishes the situation. If the voice is carrying context, it starts at zero |
| "Re-rolling fixed the click" | Two different TTS failures. Re-roll fixes boundary clicks; a trailing artifact needs a guarded trim, or it eats word-final consonants |
| "I'll run it autonomously to a first cut" | That is exactly how the unusable one was made. If the director orders one anyway, the gates queue — see below |
| "I'll build the real thing so the film is honest" | The film is drawn. Truth governs figures and claims, not execution |
| "The DOM checks pass, the frame is fine" | Look at the picture. One pass found a cursor that had never rendered in any frame |
| "I looked at the contact sheet myself, it's fine" | You know what you intended, so you see it. Spawn an agent that has only the frames and the director's words. It finds the crop you stopped noticing three renders ago |
| "The probe is green, so the shot works" | Every probe measures whether something *changed*, never whether it is *readable, framed, or uncropped*. Those are eyes-only |
| "I'll patch the composition with a quick replace" | A `str.replace` that matches nothing is a silent no-op that reports success — and one that matches twice is as bad: a pattern for `s-label` also hit the `s-label` nested inside `o-label` and hid a label through a whole beat. Assert the match count, not just the match |
| "Sample each beat in the middle" | Sample **10**/35/65/90%. The 10% sample is the only one that sees content painted at frame entry that should have been cued |
| "It's a series, so I'll reuse the frames" | Shared grammar is not shared frames |
| "Parallel agents can each edit a frame" | One `film.html`. Serialise |
| "The 1:1 cut is done" | `openFilm` resizes `#stage` to `FILM_W`x`FILM_H` for you now. The mislabelled-aspect failure is only reachable from a hand-rolled renderer that screenshots the viewport instead |
| "`-t` will fix the length" | `-t` truncates but never pads. `apad` first, or `-shortest` clips the end card |
| "It's rendering, I'll check back" | Confirm it actually started. A declined permission prompt looks exactly like a long render |
| "It sounds fine to me" | Measure it, on the delivered file |
| "Small tweak, no need to re-verify" | Small tweaks are how a −14 LUFS master became a clipped one |
| "It'll sit on top, it's drawn later" | DOM order is stacking order until you say otherwise. A mascot rendered behind the panel it was meant to perch on, for three renders |
| "I'll re-render and see if the framing works" | A framing fix is a still. Three renders died inside one framing loop, and the director then reverted the lot — "actually fuck that lets just keep it centered". Net change zero |
| "I'll send it and let the director spot it" | Nothing reaches the director unlooked-at. Open every frame you are about to send, first |
| "It's only a voice line, the picture is unaffected" | A line swap invalidates every reveal cue in those beats *and* the screen copy written to answer the old line: "the your on the second frame shows up too early and it kind of ruins the video" |
| "The clock is a nice touch, leave it up" | Persistent furniture needs an exit. One rode the margin for ~20s after it had already flipped to ANSWERED: "the clock and time thing shouldn't stay forever" |
| "No news until the file exists" | "whats happening" / "you ran it for 20 mins and nothing". Report rate and ETA the first time you look, unprompted |
| "The upload command returned, so it was delivered" | Confirm it arrived — "did you send on tg" / "No". One 1.4KB send hung a wait loop for 110s because its own `pgrep -f` pattern matched itself, while the API had answered in 0.15s |
| "The contact sheet speaks for itself" | Unlabelled it reads as duplicates: "why are there four copies same thing". Legend every tile — beat, timestamp, percentage |
| "Grain everywhere, it's one line" | Grain over near-black defeats the encoder: 65s came out an 85MB master where the same cut without grain encodes at 21MB. Mask grain off near-black areas, and check the master's size against the CRF budget before you deliver it |
| "The render finished, the file is there" | Check exit status and size. An OOM kill (137) leaves a plausible partial — 45MB where 111MB was expected |
| "The film ends on black, I checked the tail" | Two different things produce it and the fix differs. A seek past the last video PTS writes no file at all and still exits 0 — you end up looking at the stale PNG from the previous run. Or the seek lands in range and ffmpeg returns the correct last frame, which a reviewer reads as black on a dark ground: one film's final second measured a flat luma of 217, bright ground, correct (`../../references/motion.md`). And `apad` makes the container longer than the video stream, so the file's duration is already past the last frame. Seek to the *video stream's* duration minus one frame, and assert the PNG's mtime is from this run |
| "I'll nudge the path now and fix the motion after" | One geometry, one edit. A dashed path and the bezier that follows it are two expressions of the same numbers; edited separately, a coin flew 550px above its own arc for three versions |
| "57% of the frame is empty, but it's composed" | Empty is a note, not a style. Composition is what you say after someone else fails to see the point |
| "I'll total the generation credits at the end" | Ledger each one as it happens. The recalled total the kill decision was made on said 957; the real spend was 1,073 credits across five generations |

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

One film carried "57–86% flat ground per frame — the single most common note across all
three review rounds" into its own `HANDOFF.md`, passed every mechanical check, and was
rejected in one sentence — the recurrence the gate table now sends back to G3.

## When the director orders an autonomous run

The order comes: "do not stop and i mean do not stop i'm going to sleep i want you to
ultra code finish it". The gates do not disappear then, they queue. Run to a first cut,
and write every skipped gate at the top of `HANDOFF.md` as a numbered list of questions
the director answers on waking — the questions, not a summary of what you decided in
their place. **Without explicit iterative authorization, do not build a second version on top of an unanswered direction.** That is the run
the opening refers to: it returned v8, the one unusable film in the set, and it failed
exactly here — the skipped gates were written up as decisions already taken, not as
questions still open.

## Reference map

Load only what the current step needs. Other styles are listed in [SKILL.md](../../SKILL.md).

| File | What's in it |
|---|---|
| `../../references/batch-variants.md` | Orchestrator + worker windows, the done.log protocol, stills before renders, one shared VO, brand sheet, direction Q&A, script tells to strip, model bake-off |
| `../../references/direction.md` | Three directions, killing two, the signature move, deriving a look instead of inheriting one, the accent budget |
| `../../references/truth.md` | The truth stage: `generate.py` → `fit.py` → `facts.json`/`fit.json` → `fit.js`. Then the approved-figures list, the refused list, sourcing real assets, genericising private material |
| `../../references/copy.md` | The screen-vs-voice table — the cheapest gate and the highest-value one |
| `../../references/motion.md` | Seek determinism, easing, staggers, resolution, and the two failure modes (slideshow / screensaver) |
| `../../references/sound.md` | Deterministic synthesis, the mix graph, and the mastering arithmetic |
| `../../references/deliverables.md` | Aspect cuts, the libass traps, captions, poster, licences |
| `../../references/qa.md` | The failures that look like other failures — a throwing composition that reads as a slow render, `cue()`'s time base, patch asserts, SSIM against the wrong reference. Open it the first time something is inexplicable |

## Definition of done

- [ ] Three directions written, two killed with reasons, recorded in `BRIEF.md`
- [ ] The film has a signature move you can name in one sentence
- [ ] It does not look like the last film you made
- [ ] Every on-screen numeral swept from the live DOM and diffed against the approved-figures list — reading them off the frames does not count
- [ ] Every quoted line checked against its source; watching the film finds neither of these
- [ ] The screen/voice table exists and no beat duplicates itself
- [ ] Five reveals spot-checked: opacity < 0.15 before the measured word, > 0.85 after
- [ ] `probe.mjs` clean: scope line read, no dead window, every shot resolved, never blank, and any configured hit tests land
- [ ] Determinism: seeks byte-identical forward **and** backward
- [ ] Delivered file measures −14 LUFS ±0.2 (the tolerance `master.sh` gates on), true peak ≤ −1 dBTP
- [ ] Every SFX cue measurably present in the delivered file
- [ ] Renders versioned, never overwritten
- [ ] Two consecutive clean note rounds, and no note recurs across two independent review rounds
- [ ] Deliverable set, licence block, and `HANDOFF.md` written
- [ ] You have written down what you would fix next
