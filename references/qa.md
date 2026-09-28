# QA

Applies to every style in [styles/](../styles/). Where this file names "the skeleton", it means the legacy rig at `styles/vo-synced-legacy/starter/film.skeleton.html`; the newer starters (channel-thread, chapters and the rest) follow the same seek contract.

## The friction, and what removes it

Every item here cost real time on a real film. They are ordered by how much.

### The probe only sees what it walks

`signature()` walks `probes.scope` from `film.json`, defaulting to `.scene`. A film
whose moving layer lives directly on `#stage` — one continuous UI, camera driven —
has nothing inside `.scene`, so the walk returns an empty string at every timestamp.
Only one of the three checks goes green on that: resolution passes every frame,
precisely because nothing ever changes. Dead-window and blank fail the whole film for
the same reason. On a film whose whole moving layer was one camera-driven UI, the pre-fix probe reported the
whole film frozen AND blank AND every frame cleanly settled — garbage in both directions out
of one bug.

That film has no `.scene` wrappers at all. A second one shipped eleven empty
`<section class="scene" data-frame=…></section>` markers and walked the same empty
set — "**probe.mjs was a silent no-op before this session** and had been for every
version of this film"; the first honest run found 13 failures. Having the wrappers is
not evidence the walk found anything. Read the scope line.

A third film is the other shape of the same symptom: it walked a real set that did not
contain the thing that moves — its persistent layers sit outside `.scene` — and spent
an hour on a drift fix that moved the numbers by exactly zero. **The tell is a real
composition change that moves no probe number at all.**

The probe now refuses to run on nothing. It prints the scope it walked, and exits 1
either when `probes.scope` matches no element or when the walk at the film's **midpoint**
(`duration / 2`, the one timestamp it samples) turns up fewer than two nodes:

```
scope "#stage": 1 root(s), N nodes walked
```

Because it samples one timestamp, a film that is legitimately near-empty at its midpoint —
a hard cut, a held black, a single-element beat — fails this on a correct scope. Check what is
on screen at `duration/2` before you change `scope`.

The guard only catches the empty case. A scope that walks 400 nodes and still misses
the moving layer passes it — so a real composition change that moves no probe number at all
stays the only symptom you get. Read that line every run. Three of four films set
`"probes": { "scope": "#stage" }`.

### A composition that throws looks exactly like a slow render

`stills.mjs` and `render.mjs` wait for `window.__ready`. If the composition throws
before setting it, the wait times out and you get `TimeoutError` with an empty log —
no mention of the actual error, which is sitting in a `pageerror` you already
captured. **`openFilm` re-throws the captured page errors on timeout**, so the
message you get names the real fault. Without that it did not, and a one-character
mistake cost a ten-minute detour. Twice. Any new script opens the film through
`openFilm` from `scripts/film.mjs` — never its own `newPage` + `waitForFunction`,
which is how the message gets lost again.

### `str.replace` that matches nothing fails silently

Patching a composition with `s.replace(old, new)` and a stale `old` is a no-op that
reports success. One left a reference to a data field that had been deleted; the
film rendered `undefined` on screen in three places and the only symptom was the
timeout above. **Assert before you replace.** Every edit:

```python
assert old in s, f"NOT FOUND: {old[:70]}"
```

Matching twice is as bad as matching zero times, and the assert above passes on both.
The two bottle labels on one film are separate SVGs with byte-identical inner markup, so
an anchor written against one matched both and hid a label through a whole beat.
Count, don't test for presence: `assert s.count(old) == 1`.

And when a patch applies several edits, know that the first failed assertion aborts
the rest — so a half-applied patch is a state you must expect and check for.

### `cue()` returns FILM time, not frame-relative time

`timeline.json` word starts are absolute. Writing `frameStart + cue(...)` pushes every
reveal a whole frame late — 19 to 45 seconds in one case, so most of the film's
reveals simply never fired. If a composition looks like nothing is animating, check
this first.

### Stills wipe their own directory

`stills.mjs` clears `stills/` on every run, so rendering one timestamp deletes the
sheet you were assembling. Render every timestamp you need in a single invocation.

### Dead-window numbers from a pre-VO stills pass are void; the composition notes are not

G3 mandates stills before any voiceover exists, so every hold is pad-only and the
cues bunch at each beat start. **Dead-window numbers from that pass are not real;
composition and emptiness notes from it are.** One blind reviewer's "18s of provably
frozen frames" was correctly deferred as a timing artifact — and then reappeared in
the finished film, because nobody re-ran the check once the timeline was real. Defer
the number, then put it on the list for the first pass after `build_timeline.py`.

### Absolute SSIM measures the encoder, not the shards

Film grain on a dark ground costs ~0.02 SSIM at crf 16 whether or not a shard seam
is near. A fixed 0.995 threshold fails every seam — and also frame 0, which is not a
seam, which is the tell. **`probe.mjs` baselines on three mid-shard frames, takes the median,
and asks only whether the seams beat `baseline − 0.015`.** It prints the baseline it used. A
corrupt shard scores far below it, not 0.01 under.

The seam frame numbers are derived from the shard count, so **the probe must be given the
count the render used** — `node scripts/probe.mjs renders/silent-v1.mp4 <shards>`, or pin
`"shards"` in `film.json` and both scripts read it. Left to differ, the SSIM pass compares
frames that are not seams and the one check that exists to prove shard contiguity proves
nothing.

### The same grain floor governs motion detection

A film with playhead-stepped grain has a real per-frame pixel-motion floor, so a gate
that samples two frames 0.25s apart is comparing two grain offsets, not two pictures.
One such gate failed until the grade was turned off, and it had been right about
nothing.

The DOM probe has the hole from the other side. With `scope: "#stage"` the walk
reaches `#grain`, a sibling of `.scene` in the skeleton, and the skeleton steps the
grain transform 12 times a second. 0.083s is far under the 1.55s dead-window limit,
so no window can ever read as dead. The other half is loud: the resolution gate
samples every 1/30s, so an unmarked `#grain` leaves every frame "still changing" at
its cut and every frame fails. Mark `#grain` `data-camera`: the probe then counts it
as present without its transform. One shipped film is the live case — scope `#stage`,
grain stepped at 1/12, not one `data-camera` in the file. The skeleton now ships the
attribute; a hand-rolled rig will not.

**A `.scene` wrapper reached from a `#stage`-scoped walk is the same hole.** The signature
excludes a scene's own opacity because a crossfade is the cut, not content arriving — but with
`scope: "#stage"` the wrappers are walked as ordinary elements and their opacity came straight
back in, so every non-final frame read as still changing at its own cut. `signature()` now
treats any `[data-frame]` element as a scene wherever it meets it. If you write your own probe,
that is the line to copy.

### The two gates need different signatures

A camera drift, a list scroll and a typing indicator all "change the DOM", but none
of them is content arriving. `signature()` separates them by attribute:

- **`data-camera`** — a push or a scroll is the edit, not content. The probe reduces
  that element to a presence marker: it records only the tag, so its transform,
  geometry, opacity and text are all invisible to both checks. Its descendants still
  count in full — put it on a node that carries motion and nothing else, never on one
  that also carries content, or every reveal written into that node vanishes from both
  gates. Without it, every shot reads as never settling.
- **`data-ambient`** — a typing indicator or a read-position marker is interface
  state. `closest("[data-ambient]")` drops the element and its whole subtree from the
  **resolution** signature only. The **dead-window** check still sees it — the screen
  genuinely is alive — and the resolution check must not, or a shot can never cut
  while it pulses.

Geometry is `offsetLeft/offsetTop/offsetWidth/offsetHeight` plus the element's own
`getComputedStyle().transform` — never `getBoundingClientRect()`, which folds in
every ancestor transform and turns one camera move into "everything changed".

A shot that legitimately never settles — a close card on a continuous drift — goes in
`probes.resolution_exempt` by frame id, and the probe prints `exempt <id>: still
moving at …` instead of failing. Declaring one frame on the record is a decision;
loosening `SETTLE_BY` for all of them is not.

The dead-window threshold has the same shape and the same rule. `DEAD_LIMIT=2.0 node
scripts/probe.mjs` is the only knob on the probe's own thresholds — `SETTLE_BY`, `BLANK_RUN`
and the 0.06 blank floor are file constants. `FILM_ROOT`, `FILM_PAGE`, `FILM_W` and `FILM_H`
still apply, since the probe opens the film through `film.mjs`. Use it to reproduce a failure,
never to pass one. Its shipped value of 1.55s belongs to a film whose camera drifts continuously, where
a pause that long reads as composure; three other films ran at 1.2s. If you change it, change
it in the file with the reason beside it, so the next run inherits the decision.

### A blank FAIL has nothing to do with your palette

The blank check reads composited **opacity** only — the scope root's opacity times each
element's own, thresholded at 0.06 in `probe.mjs`'s blank check. Note it does *not* apply a
`.scene` wrapper's opacity to that scene's children the way `signature()` does, so under
`scope: "#stage"` a fully faded-out scene still counts as composited: the check is a floor
against a walk that finds nothing, not a proof the frame is visible. It never reads colour, so contrast
has nothing to do with it and a light ground cannot cause it. What trips it is
everything in scope sitting under 0.06 for four consecutive samples — or a scope that
walks nothing at all. It fired once on a light-ground film that rendered correctly and
cost a debug cycle. If blank fails, extract frame 0 and look at the pixels, then check
what the scope actually walked, before touching the composition. Do not re-derive the
check from ground contrast.

### A tween that has not started still applies its from-state

One film shipped with its payoff beat parked off-screen at scale 0.455 from ~47.8s and
the probe was green: the resolution gate reads *change*, and a shot that has been
wrong since frame 0 never changes. Stacking `fromTo` tweens is not the fix — each one
asserts its from-state before its own start time. The resolved rule is in
`references/motion.md`. Its QA payoff is measurable: replacing ten stacked `fromTo`
tweens on that film's headline with playhead-derived writers fixed backward seeks and
lifted every shard boundary from 0.9964 to 0.9983 — a film whose seams a fixed 0.995 would
have waved straight through, both before and after the fix. On the grain-over-dark film above,
the same fixed threshold fails every seam. One number cannot serve both, which is the whole
argument for baselining.

### "Nothing ends unresolved" and "no dead windows" leave a 0.55s band

Resolve by `hold − 1.0s`, never freeze for more than 1.55s: on a long narration line
those two rules nearly collide. The answer is not to loosen a threshold. It is to
give the film an ambient marker that tracks the narration: excluded from the
resolution signature, still visible to the dead-window one, so a shot can resolve
while the screen breathes. A camera drift does not do this job — `data-camera` drops
out of *both* signatures, so a push satisfies resolution and leaves the freeze exactly
where it was.

### A reveal belongs to the beat it lands in

Starting the next beat's message early makes the current shot never resolve, and the
gate reports it as the *current* beat failing. When resolution fails on a beat whose
content clearly settled, look at what the following beat starts early.

### The probes measure time, not area

A dead-window check finds a frame where nothing *changes*. It cannot find a frame
where nothing *is*. One film passed every temporal gate with 57–86% of every frame bare
ground and was killed in one sentence. The counter at QA time is to ask the G4 reviewer for
the number, not the impression: *"for each frame, estimate the percentage that is bare ground,
and name any frame over ~50%."* The counter that would have prevented it is a density budget
drawn at G3 — `references/direction.md`, "It fills the frame".

Judge weight from full-resolution stills, never a contact sheet. One pass briefed a
rebuild for "the card is too small", then measured and found it already filled 60–77%
of the frame.

### Solve the framing against the FINAL layout, not the empty one

A composition that types its text in starts with empty elements. If you measure
scroll targets or camera framing at build time, you measure a page that has not
grown yet — then the copy arrives, the page gets ~115px taller, and every shot is
short by that much. In a chat-shaped film that puts each attachment *under* the
input bar: the viewer sees the message and never sees the evidence.

Fill every body with its final copy, measure, then blank them again — and pin the
measured height so typing can never reflow the page:

```js
BODIES.forEach(([id, txt]) => { el(id).textContent = txt; });
BODIES.forEach(([id]) => { el(id).style.minHeight = el(id).offsetHeight + "px"; });
// ... solve every shot here ...
BODIES.forEach(([id]) => { el(id).textContent = ""; });
```

### A card shorter than its own contents silently eats the payoff

`overflow: hidden` on a panel with a declared height and absolutely-positioned rows
does not warn you. One card was 172px tall with rows laid out to 236px, so the
widest bar — the one the whole film was arguing toward — was clipped away and never
appeared in any render. Another put its headline number at `x=900` inside an 828px
card; the number was simply not in the film.

**Assert it, per beat, for the card that is on screen:**

```js
for (const k of card.querySelectorAll("*")) {
  const kb = k.getBoundingClientRect();
  if (kb.right  > cardBox.right  - 2) fail(`${k.id} overflows right`);
  if (kb.bottom > cardBox.bottom - 2) fail(`${k.id} overflows bottom`);
}
```

Check only the *active* card at each beat — the others are legitimately below the
fold, and flagging them buries the real hit.

### A failed assertion aborts the whole patch, not just the line

Patching a composition with a batch of `replace` calls that each `assert` first is
correct — but the file write happens at the end, so **one stale match discards every
edit in the batch**, including the ones that matched. Twice in one session a type
increase appeared to apply and had not.

Report per edit instead of trusting the batch:

```python
applied, missed = [], []
def sub(old, new, tag):
    global s
    if old in s: s = s.replace(old, new); applied.append(tag)
    else: missed.append(tag)
# ... all edits ...
p.write_text(s)
print("APPLIED:", applied); print("MISSED:", missed)
```

Then read the MISSED list. It is the difference between "I fixed it" and "I believe
I fixed it".

### Derived artefacts go stale

`qa/` contact sheets are built from `stills/` and nothing rebuilds them. One round's
sheets were reviewed against a composition that had moved on. The QA agent's own
note: "Re-generate the `qa/` sheets before the next round or they will send the next
reviewer chasing ghosts." Rebuild every sheet after every stills run, or delete it.

### A wholesale revert takes the fix out with the regression

Reverting a bad pass "wholesale" because most of it was wrong throws away the parts that were
right along with it. One film had already fixed a dropped opening word with a 0.5s lead-in —
then a later trim pass got reverted in full, including that lead-in, because the revert target
was "the trim pass," not "the trim pass minus the one line I already know is correct." The
defect came back identical to the first report, and cost a second full round to re-diagnose
something already fixed once. **Revert at the same granularity you'd commit at.** Before
reverting a batch of changes, check whether anything already-verified is riding inside it, and
carve that part out first — or re-apply it immediately after the revert, in the same turn, not
as a follow-up you might forget.

### "The check passed" is not "I verified it"

A script exiting 0 is evidence about what the script measures, not about what the viewer will
experience. Declaring a film done because `probe.mjs` is green, or because a silence check
returned clean, reports the state of your instrument, not the state of the film — see the two
entries above, where a coarse threshold and a wholesale revert both produced a clean-looking
check on a broken delivery. Before calling a round finished: pull the actual frames or the
actual waveform for the specific thing that was reported broken, and look at *that*, not at
the pass/fail line of whatever automated check happens to cover the same general area. The gap
between "my script says this region is fine" and "I looked at this region" is exactly where a
regression survives two rounds of QA in a row.

### A note is a symptom report, not a specification

The person giving a note is almost always right that something is wrong and almost
never precise about what. Implement the words literally and you fix nothing; ignore
them and you fix nothing twice.

| The note | Literal reading (wrong) | The mechanism (right) |
|---|---|---|
| "Make it 3D" | Add a rotation | A camera rig, depth on the elements the story touches, and a coordinate refactor so the shot moves as one object |
| "I don't like the ripple" | Delete the ripple element | Find EVERYTHING that reads as a ripple — there were two, and removing one would not have satisfied the note |
| "It looks basic" | Add effects | A shot is carrying a beat with two rectangles. Rebuild what the shot IS, not how it is decorated |
| "Add a typing sound" | Raise the cue volume | Measure. The cue may already exist and be inaudible for an arithmetic reason |
| "Speed it up" | Compress everything uniformly | Usually: tighten the clauses, keep or lengthen the tail holds |
| "The cursor is bad" | Redraw the cursor | It is probably invisible, not ugly — size, stroke and shadow before shape |

Three habits behind the table. Ask what they saw, not what they want — "at which
second?" turns an aesthetic note into a frame number. Reproduce it before fixing it:
extract the frame, and if you cannot see what they saw, you do not understand the
note yet. Say what you changed in their words, not yours. When a note is genuinely
wrong — and sometimes it is — the answer is a measurement, not an argument.

### Look at the video before you relay it

A worker grades its own render generously. Before an orchestrator passes any film on as good or
done, it extracts a contact sheet and consecutive frames around every pose swap, hit and cut, opens
them, and says plainly what is wrong:

```bash
ffmpeg -i film.mp4 -vf "fps=2,scale=480:-1,tile=4x4" -frames:v 1 qa/sheet.png
ffmpeg -ss 12.0 -i film.mp4 -frames:v 6 qa/around-12s-%02d.png
```

One film was relayed as "best" on the worker's word and the director called it horrendous: a rigid
limb, no action, cropping, design pops and a generic generated background, all visible in the frames.
For character animation, check that limbs bend and follow arcs, that each shot has one action beat,
and that the design does not change between shots.
