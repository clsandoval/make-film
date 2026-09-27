# Batch and variant films

Use when the director wants several films or several looks at once: a batch of
style pegs, one script rendered in N worlds so they can be compared, or a set of
20-30 s films in different styles. Two September 2026 batches set this down: about
20 short product films in 20 styles (pegs, then motion tests, then full films),
and 10 variants of one 20 s cold open for an internal research film, three of them
a model bake-off.

Everything in [Style peg](../SKILL.md) still applies: Codex stills, code-orchestrated
motion, Playwright capture, ffmpeg. No video model.

## Layout: one orchestrator, one worker per variant

```
hub/
  TASK.md            the director's asks, appended as dated sections, newest wins
  COMMON-BRIEF.md    every rule that applies to all variants
  DECISIONS.md       one line per decision, with time and who said it
  done.log           the worker → orchestrator channel
  shared/vo/         the one VO take, its word timings, the spend log
  shared/brand/      the brand sheet and a screenshot of the source site
  v1-<world>/TASK-VARIANT.md
  v2-<world>/TASK-VARIANT.md ...
```

- The orchestrator talks to the director, writes the briefs, does QA and delivery.
  It does not build films.
- One tmux window per variant, each started in its own folder:
  `tmux new-window -d -t 'main:' -n v1-notebook -c hub/v1-notebook 'bash -ic claude'`.
  Close the window when its line lands in done.log. Around 10 at once is the ceiling;
  queue the rest.
- Generate the per-variant briefs from one script (`mktasks.py`) so they only
  differ where they should. Each TASK-VARIANT.md is short: "FIRST read
  COMMON-BRIEF.md, all of its rules apply", the world in two lines, a starting beat
  map against the VO cues, the signature move, and the exact output file names.
- Only COMMON-BRIEF.md holds rules. A change of direction goes into COMMON-BRIEF.md as
  a new section marked as overriding the old one, then a one-line note to each
  worker to re-read it. Don't paste new rules into worker panes.
- After sending text to a pane, capture-pane and check it was submitted. A fix note
  once sat unsubmitted for 90 minutes.

## done.log protocol

Workers never message the director and never send to Telegram. They append one line:

```
STILLS    <variant> <glob>     key-beat frames ready for a reaction
STILLS-V2 <variant> <glob>     re-skinned or revised key beats
<variant> <mp4 path>           finished render, QA'd by the worker
BLOCKED   <variant> <reason>   stopped; what was spent, what exists
```

Plus a DONE.md (or PEG-DONE.md / FINALPASS-DONE.md) in the folder: paths, durations,
beat map, images used, QA results, weak spots stated honestly. The orchestrator
waits on done.log and those files (`tail -f`, or an until-loop on line count), or
on a pid. Never `pgrep -f`: it matches its own command line. Watchers run under
`setsid nohup`, because recreating tmux kills window-bound jobs.

## Order of work

1. **Script or treatment first, style-agnostic.** For a long film, a one-page
   treatment with a beat sheet: section, minutes at 185 wpm, the story, and one
   *picture move* per section, the physical thing the picture does that tells the
   story without narration. Any world you pick later has to be able to do every
   move. Lock the words before any look.
2. **Key-beat stills, sent for a reaction before any full render.** Each worker
   saves 4-6 frames from its real scaffold at the VO beats and logs `STILLS`. The
   orchestrator looks at them and sends them to the director labelled by variant.
   A palette change at this stage cost a re-skin of stills, not seven renders.
3. **Full renders** only on the director's go.
4. **Orchestrator QA, frame by frame.** Workers over-grade their own renders. Pull
   a cue sheet at each VO sentence plus a 2 fps sheet and the last frame, and look
   at them. Bounce with specific notes (tofu glyphs, clipped labels, end card too
   small, a tile that reads as a slash on a phone, empty page holds). Log bounces.
5. **Deliver each file as it passes**, labelled by variant, and check the send
   receipt. Don't wait for the batch.
6. Close with a contact sheet and a short table: variant | what moves | would it
   carry the long version?

## Fair comparison

- **One VO take, reused by every variant.** Record it once, before workers start,
  and budget characters (the internal film had 600 characters for the take plus
  retakes). Tighten pauses on the take, then freeze it. Workers get `vo.wav`,
  `vo-words.json` and a cue table in the brief: place the VO at 0.40 s, each
  sentence's film-time window listed.
- Same opening line, same beat order, same end-card timing and the same maximum length for
  every variant. The only thing that varies is the world.
- If the words change, re-record once, move the old take to `v1-old/` marked
  retired, send HOLD to every worker, then UPDATE with the new cue table.

## Brand skin

- Pull the palette and type from the client site's CSS variables and homepage,
  not from an old deck. Write it to `shared/brand/BRAND.md` as a token table (name,
  hex, where the site uses it) plus type families and the site's texture, with a
  screenshot beside it.
- Rules for film: one ground, one text colour with 70% / 45% secondaries, **one
  accent per frame**, a single call-out colour used sparingly, secondary hues only
  for secondary data. Strip every default UI colour that isn't in the sheet:
  notebook blue, spreadsheet selection blue, terminal diff red/green.
- Re-skin every variant from the sheet at once. Keep each world's idea and moves;
  re-skin, don't redesign. Re-send stills labelled "brand v2" and say which earlier
  sends they supersede.

## Finding the direction with the director

When the director says the look is boring but can't say what they want, ask about
the reference they did like before pitching anything:

- What made it feel high quality? The answers that came back: precise real detail;
  restraint (calm palette, nothing cartoonish); things build themselves, so you
  watch the work happen and there are no slide cuts; the medium is the message,
  the world is the subject.
- Energy: calm and premium, or fast and punchy?
- Audience: internal experts, where fake detail loses trust, or outsiders?

Then offer concrete worlds that keep those qualities, each in two lines with its
signature move (a notebook where cells run; case files filed and redacted; a
system map that draws itself; a terminal with a diff; a transcript whose key
lines lift out into a rule; the original reference as the control; a mix that moves
between worlds per section). Build them all on the same opening.

## Script voice

The director rejected three rewrites of one batch as "claudish". Strip these:

- setup then twist ("X. But then Y."), and stacks of those lines in a row
- tacked-on emphasis and closing punchlines
- signposting ("here's the thing", "the answer comes back...")
- "not X but Y" contrasts and contrast openers
- tagline endings, triads, "honest"

State facts plainly, one concrete scene, spoken sentences of 3-8 words. Numbers go
on screen or in the VO only if they are on the source and undisputed; anything the
source contradicts is `[TBC with <owner>]` in the script and absent from the
screen. Props (dates, anonymised IDs, filenames, real-looking code) are fine; made-up
statistics that read as claims are not.

When the director has approved a script, it is locked verbatim. Don't send another
rewrite unless asked.

## Model bake-off

To compare models on the same work, clone a variant's brief into a sibling folder
(`v4b-terminal-<model>`) and start that window on the other model (e.g. MiMo via
ClaudeX). Add a no-peek rule to its TASK-VARIANT.md: don't open, list or copy any
other `v*` folder; build from COMMON-BRIEF.md, `shared/` and this brief only. Log
start times and QA bounces per arm in `BAKEOFF.md`, then send the two renders
side by side.

## Hard rules already paid for

- **No Seedance, fal or any video model for pegs, motion tests or variants.** A
  Seedance peg batch was rejected and cancelled mid-run; the fix was redoing all
  ten in the previous batch's method. For a new batch, copy the last batch's brief
  and scaffold verbatim.
- **A one-line script fix is a splice.** Generate only the changed phrase, splice
  it into the approved take, shift later cues. A full regeneration changes the
  delivery of every other line.
- **Look at the frames yourself before relaying.** A worker's "best" shot was
  called horrendous by the director: rigid limbs, crops, design pops, a generic
  AI background. Contact sheet plus consecutive frames around each hit, read the
  PNGs, say plainly what's wrong.
- A product name the TTS mangles gets a respelling and a phoneme check on the final
  mix, at every occurrence. Log which take passed.
- Renders go to new file names. Delete nothing with globs.
