# Motion

Applies to every style in [styles/](../styles/). Where this file names "the skeleton", it means the legacy rig at `styles/vo-synced-legacy/starter/film.skeleton.html`; the newer starters (channel-thread, chapters and the rest) follow the same seek contract.

The renderer never advances wall-clock time. For every output frame it calls
`window.__seek(n / FPS)`, paints once, and screenshots. Everything below follows from that.

## Seek determinism

**Seek to T twice, get the same bytes — forward and backward.** Backward matters because the
QA probes sweep, and because a shard boundary is a backward seek in disguise.

| Banned | Why |
|---|---|
| `Math.random()` | Different every seek. Every render is a different film. |
| `Date.now()`, `new Date()`, `performance.now()` | The composition must not know what time it is. |
| CSS `transition` and `@keyframes` | **They never fire.** See below. |
| `repeat`, `yoyo`, `repeatRefresh` on a tween | Position in the repeat cycle is not a pure function of the playhead in every GSAP version; treat it as non-deterministic and unroll it. |
| A bare `.call()` with no backward counterpart | A `.call()` does not replay on a backward seek. See "call pairs". |
| Anything reading live layout at tween-build time | Measure after `document.fonts.ready`, never during a seek. |

Two lines at the top of the composition make the whole thing seek-driven:

```js
gsap.ticker.remove(gsap.updateRoot);   // seek-driven only; no wall clock
const master = gsap.timeline({ paused: true });
```

and three at the bottom are the entire renderer API:

```js
master.pause(0);
window.__seek = (t) => { master.seek(t, false); };   // false = do NOT suppress events; .call() fires on the crossing
window.__duration = TL.duration;
window.__ready = true;
```

### CSS transitions never fire — the easiest trap in the pipeline

`transition: opacity .3s` is *correct CSS*, and opening the file in a browser plays the fade.
Under the renderer it does not exist: the page jumps to time T and paints one frame, so there
is nothing to interpolate over. The element is at one end value or the other in every frame,
and a fade you can see in the browser silently never happens in the film.

**Every animated property must be a GSAP tween on the master timeline.** No exceptions.

### Noise: derive it from a seed or from the playhead

Deterministic noise costs nothing and removes a whole class of bug. Two forms.

**A seeded LCG**, for anything drawn once — a trace plot, a scatter, a jittered layout:

```py
def lcg(seed: int):
    state = seed
    while True:
        state = (state * 1103515245 + 12345) % 2147483648
        yield state / 2147483648 * 2 - 1
```

**A pure function of the playhead**, for anything that changes during a shot. Strictly better
than a seeded stream, because it is correct on a backward seek for free. One film's closing
beat shuffles six rows before resolving; the lit set is computed from the draw index alone,
so a re-render and a backward seek both agree with no state to restore.

Two real bugs from that beat. **A plain LCG on `(row, draw)` had period 3, so every
three-option row blinked on a loop** — mix both indices through a 32-bit hash before the
modulus: `(((d + 1) * 2654435761) ^ ((r + 1) * 40503)) >>> 0`. And when a row needed two
distinct picks, *filtering* a duplicate away made the row silently drop a chip, which reads
as a dropped frame — offset within the remaining range instead of rejecting.

### Grain from an offset table

The texture is one tiled PNG generated once, or an inline `feTurbulence` data URI — which is
what the skeleton ships, so there is no asset to build. It is positioned by a fixed offset
table stepped as a series of `master.set()` calls, eight offsets at 12 steps per second:

```js
const GRAIN = [[0, 0], [-91, 47], [63, -112], [-140, -33], [111, 88], [-27, 131], [148, 19], [-72, -95]];
for (let i = 0; i * (1 / 12) < TL.duration; i++) {
  const [gx, gy] = GRAIN[i % GRAIN.length];
  master.set($("grain"), { x: gx, y: gy }, i * (1 / 12));
}
```

The layer is inset beyond the stage — every shipped film uses `inset: -20%` — so the offsets
never expose an edge, at low opacity with `mix-blend-mode: multiply`.

**Mask the grain off near-black areas while you are writing it.** Grain over near-black
defeats the encoder: 65 s came out an 85 MB master where the same cut without grain encodes at
21 MB. This is a compositional decision made here, not a delivery check — though check the
master's size against the CRF budget before you ship it too.

**And mark the node `data-camera`.** Grain is camera, not content: unmarked, its 12-per-second
step makes every frame read as never settling and makes a dead window unreachable. See
`references/qa.md`, "The two gates need different signatures".

**The grain will break your stillness checks.** A real QA run reported all seven shots "still
moving" at the cut. It sampled 0.25s apart; grain steps every 1/12s over an eight-entry
cycle, so that separation *guarantees* a different offset every sample. Any stillness or
dead-window probe must exclude the grain node or sample on the grain period.

### Call pairs

`master.call(fn, [], t)` fires when the playhead crosses `t` going forward. It does **not**
fire going backward, so a one-way `.call()` leaves the DOM wrong on any backward seek —
including the one a QA sweep or a mis-ordered shard performs. Write the inverse immediately
before it:

```js
master.call(() => { light(FINAL); el.classList.add("resolved"); }, [], resolveAt);
// seeking backwards past the resolve must restore a draw, not leave FINAL up
master.call(() => { light(drawAt(LAST)); el.classList.remove("resolved"); }, [], resolveAt - 0.001);
```

This is also why parallel render shards must be **contiguous** ranges, each seeking
monotonically forward through its own span. Interleaved shards corrupt exactly the frames
that depend on a `.call()`.

### `fromTo`, `to`, and writing from the playhead

"`fromTo`, never `to`" is half a rule.

- **One state change on a property:** `fromTo`. Add `immediateRender: false` when the
  from-state must not be visible before its cue — otherwise the ripple or the badge is up on
  frame 0.
- **Two or more state changes on one property:** neither `to` nor `fromTo` is safe. "Converting
  these to `fromTo` is **not** a fix — a `fromTo` that has not started still applies its
  from-state, so stacking those re-creates the bug." Compute the value from the playhead in one
  `onUpdate` and write it once.

A determinism pass on one film found ten stacked `fromTo` tweens on a single headline.
Converting them to playhead-derived writers fixed the backward seeks.

### Thread after sorting, not before

A chain of scroll segments threaded at declaration time and then sorted by time gives every
segment the *file-order* predecessor instead of the temporal one. One film shipped that way:
"Beat 08 played back with the thread parked off-screen at scale 0.455 from ~47.8s: the
ranking, the whole payoff, never appeared." The probe was green throughout. Sort first,
thread second.

## Fonts before layout

```js
await page.waitForFunction(() => window.__ready === true);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(400);   // let woff2 + any bitmap assets decode before frame 0
```

`document.fonts.ready` must be awaited **before the timeline measures anything**, not just
before the first screenshot. Any tween whose start or end value comes from a
`getBoundingClientRect()` taken under fallback metrics bakes the fallback's line height into
the film — invisible in the browser, where the real font loaded long ago, and permanent in
the render. Serve the fonts from the film directory; a network fetch makes `fonts.ready` a
race.

## Reserve space that text will occupy later

`display: block` on an empty element is a zero-height box. Reserving a second line for a
string that types in later does nothing until the first character lands — at which point
everything below it jumps.

**Reserve with `min-height`**, set to the rendered height of the finished string, measured
after `fonts.ready`. A real composition sets it on every element that types or counts in:
42px on a body line, 84px on a two-line block, 200px on a five-line message, 63px on a panel
header, 27px on an inline span.

**Reserve a text body's height, never a panel's.** A panel sized to its final height while its
rows are still empty is a large hollow slab — about a second of dead area, on three separate
frames across two films. The rows inside reserve; the panel grows to fit them.

## Entrances, easings and staggers

A consistent motion vocabulary is what makes ten frames read as one film. One shipped
composition's whole vocabulary, as a table — the numbers are that film's, but the *ratios*
are the transferable part:

| Move | Tween | Duration | Ease |
|---|---|---|---|
| Frame crossfade in | `fromTo` opacity 0 -> 1 | 0.42 | `power2.out` |
| Frame crossfade out | `to` opacity 0, starting at `start + hold - 0.42 * 0.5` | 0.42 | `power2.in` |
| Panel / card entrance | **Two tweens**: `fromTo` `{y: 26-34}` -> `{y: 0}` over the full duration, `fromTo` opacity 0 -> 1 over 0.22. Ramping both together is the grey-slab bug — see below | 0.60-0.75 | `power3.out` |
| Line or row reveal | `fromTo` `{opacity: 0, x: -14}` or `{opacity: 0, y: 10-14}` | 0.28-0.42 | `power2.out` |
| Button press | scale 1 -> 0.96 then back to 1 | 0.10 down, 0.16-0.18 up | `power2.in` / `power2.out` |
| Pointer travel | `to` `{x}` and `to` `{y}` as separate tweens, different eases | 0.52-0.55 | `power2.inOut` / `power2.out` |
| Colour sweep across a set | `to` `{color}` with `stagger` | 0.55 | `power2.out` |
| End-card arrival | `fromTo` `{y: 40, opacity: 0}` | 0.80 | `back.out(1.5)` |

Staggers: **0.10 s** for chips arriving as one gesture, **0.16 s** for rows of a list,
**0.28-0.46 s** for a colour sweep that should read as a sentence being underlined. Below
0.08 reads as simultaneous; above 0.5 reads as separate events.

Typing is a tween on a counter object, not a per-character timer — `ease: "none"` because
typing is not eased, and `Math.round` on the tweened float so the same seek always yields the
same substring:

```js
function typeInto(el, text, tl, start, dur) {
  const state = { n: 0 };
  tl.to(state, { n: text.length, duration: dur, ease: "none",
    onUpdate: () => { el.textContent = text.slice(0, Math.round(state.n)); } }, start);
}
```

### `tabular-nums` on anything that counts

Proportional numerals have different widths, so a count-up reflows its own box on nearly every
frame and visibly jitters. The skeleton ships `.num` for exactly this; `countTo()` writes into
an element that needs it. Two films discovered the rule by hand instead. Grow a numeral with
`transform: scale`, never `font-size`.

### Nothing pops

Every visibility change is a tween of **0.20s or longer**. One film had everything from 30s on
built as `opacity: 1/0` toggles plus two blinking badges; the note back was "30 seconds onwards
is ugly shits clipping in and out etc". The probe cannot find this for you: every check it runs
fires on the absence of change, and a pop is a change. Nothing in it measures how long a
visibility change took.

### Reveals sit on words, not on seconds

Law 3. Every reveal's position argument is `cue(frameId, "word")` — the film-time start of a
measured word from the alignment — not a typed number. `cue()` throws if the word is absent
and throws if it is ambiguous unless an occurrence index is passed, so a copy edit that
removes a cue word fails loudly at load instead of silently sliding a reveal.

Two consequences worth designing around. **Name the rows in the order the voice names
them** — one frame's five rows were originally cued off a single word and four arrived inside
three-quarters of a second. And **do not cue a reveal to the final word of a sentence**: a
sentence needs time to be read, so one frame cues its three rows to mid-line words and
nothing arrives on the full stop.

## A dark panel fading in over a light ground is a grey slab

It does not composite to a dark panel at 71% opacity. It composites to a **third ground**: a
`#313338` panel at opacity 0.71 over `#f7f7f7` paper is a flat `#6a6c6f`, and measured
`#5c5e62` at its worst over 11.2% of the frame. If the film's law is "the only dark
object is the product surface", the entrance breaks that law for the length of the ramp.
**Every DOM check passes — 0.71 is a legal opacity. Only a rendered frame shows it.** It came
back four times in one film, twice after it had been "fixed".

| Case | What to do instead |
|---|---|
| Panel entering mid-beat | Split the tweens. Transform carries the entrance over 0.6-0.75s; opacity gets out of the way in 0.22s. A panel arriving at a scene *start* is covered by the crossfade; one arriving mid-beat is not. The skeleton's `growIn()` is written this way; a single-tween version is the bug. |
| Panel leaving | Do not ramp opacity at all — wipe with `clip-path`. A fading dark card is the same grey slab in reverse. |
| Two panels handing off | The outgoing reaches 0 before the incoming starts. One shipped film: out at 1.67, in at 1.68, zero overlap frames. |
| Crossfading between beats | The two panels share width and top edge, or the dissolve reads as a grey double-exposure box. Change the height, never the frame. |

## The skeleton's crossfade is a placeholder, not a grammar

`film.skeleton.html` opacity-crossfades every scene into the next because the rig has to do
*something* between frames. Three of four shipped films use no inter-frame transition at all:
one is a single continuous scroll dolly, one is per-beat camera moves, one is a continuous
morph. The fourth uses the crossfade and deliberately exempts its main node set from it: "They
are not rebuilt per scene and they do not crossfade with the scenes... That is what makes this
read as one system observed continuously rather than as ten slides."

**Anything that persists across a cut has to match-cut.** The same sentence jumped 122px across
an 01→02 cut; because it was the same text, it read as a jolt rather than as a new frame.

## A crossfade on the whole frame is a scene cut, not a content update

`.scene`-level crossfade is for moving between scenes. Applying that same full-frame blend
because *one element inside an unchanging scene* is updating is a different bug wearing the
same visual — the report card, the chart, the highlighted point all sit still while a tooltip
box swaps from one dataset to another, and the whole frame still gets a double-exposure
crossfade for it. Reviewed on the delivered file: everything outside the tooltip is pixel-identical
before and after the cut, so nothing there earned a scene-level transition — the ghosting is the
tell that the wrong layer got animated.

**The rule:** transition scope must match the scope of what actually changed. If only one
element updates, that element crossfades or cuts on its own — a `min(120–200ms)` opacity/blur
swap scoped to its own box — while every sibling stays byte-identical, frame to frame, across
the cut. Route the whole scene through the shared crossfade only when the scene itself is
changing (a new shot, a new subject, a hard content change) — never as the default handler for
"something on screen updated." Verify it the same way `signature()` does for `.scene`: pull a
contact sheet across the update window and confirm every element *outside* the one that's
supposed to move reads as the same pixels, not a blend.

## The cursor is a stage prop

Four films, two cursors on record, neither like the other, neither written down — and two of
the four needed one and had none.

| | one film's `#cur` | another's `#s4-cursor` |
|---|---|---|
| Size / stage | 21×31 in a 1280 world (~31×46 at 1920) | 22×30 on a **1080** stage |
| Fill / stroke | `#fff` / `#0a0a0a` at 2.2 | `#0C1F40` / `#F7F7F7` at 1.4 — inverted |
| Shadow | `drop-shadow(0 3px 7px rgba(0,0,0,.85))` | **none** |
| Press | scale 0.88 → 1 plus a state flip | none — translate only |

Neither reaches 2.3% of stage width — they measure 1.64% and 2.04% — and the second has no
shadow at all, which is the "reads as a smudge" failure. The first wrote the
rule into its own file as a comment: **"the cursor is a stage prop: oversized, heavy stroke,
deep shadow."**

- **Size it as a prop, not as a pointer:** ~44×54 at 1920, about 2.3% of stage width. If it
  lives inside a world the camera scales, divide by the camera floor.
- White fill, dark stroke, a real drop shadow. One cursor across a whole series.
- **Position it by the tip**, and write the tip's offset from the node origin down beside the
  node.
- Put it **inside** the node the camera moves, in rig-local coordinates. Outside the rig it
  drifts off its target on every camera move.
- Fade it out once its work is done.

A drawn hand is not an upgrade. One film substituted one and then indicted it: "at silhouette
scale it still reads closer to a mitten than a hand... a plain wedge is honest in a way a
not-quite hand is not."

### Anticipation is the difference between a cursor that slides and one that decides

8px of anticipation at 0.05s against the direction of travel, then x and y as **separate**
tweens on different eases so the path bows. Committed moves only, never on text. Start the
travel early enough that the *click* lands on its word, not the departure.

The click is four layers, and the last one is the one people forget:

1. A bloom **leading** the press by 0.1s.
2. Cursor scale 0.86 and back, `back.out(2.4)`.
3. An expanding ring.
4. The control itself moving. A cursor pressing a button that does not move is uncanny.

Size the feedback to the control: a 200px bloom over a 154px button is a halo, not a click.

### The hit test does not measure occlusion

`probe.mjs` asserts the cursor tip is *inside* the target it clicks. A pointer occluding 14.6%
of the "Authorize" wordmark it was pressing passed that test. Inside the target and clear of
its lettering are different questions, and the second one is eyes-only.

### A state change needs its cause on screen

Frame 01 cut from a marketing page straight to Discord's authorize card with nothing having
been clicked. Director: "it should show a cursor clicking the add to discord button and then
show the ... discord authorized screen cause it's confusing if you don't show the click".

Any frame that arrives in a different state from the one before it owes the viewer the action
that changed it, in shot, before the cut. Audit it at G3: for every state flip in the
storyboard, name the frame where its cause is visible.

## Nothing ends unresolved

Law 6, and the one most often mis-applied.

**The rule:** by the time a shot cuts, what the shot is *saying* must have arrived. A reveal
that lands in the last second of a hold arrives as the cut does, and the viewer sees it
leaving rather than arriving.

The mechanical form, checked by `probe.mjs`: **a frame's last change-point must be no later
than `start + hold - 1.0s`.** The probe steps at `1/fps` through each frame, builds a signature string
of every descendant, records the last time it changed, and prints the margin against the
deadline. The signature is layout-only geometry (`offsetLeft/Top/Width/Height`) plus the
element's own transform — never `getBoundingClientRect()`, which folds in every ancestor
transform and turns one camera move into "everything changed". The two gates use *different*
signatures, and `data-camera`, `data-ambient` and `probes.resolution_exempt` are how you tell
them apart: `references/qa.md`, "The two gates need different signatures".

**The mis-application:** reading "nothing ends unresolved" as "nothing may be *moving*", and
then as "there must be zero change-points in the tail". Enforced that way it froze **24% of a
finished film** into dead stills — long tails where nothing at all happened, which reads as a
hung player, not as composure.

The distinction, stated as a table:

| Allowed at the cut | Not allowed at the cut |
|---|---|
| A slow drift, a breathing panel, a rotation still easing out | A line still typing |
| Grain stepping | A row still fading up |
| A chart's interval still settling by a pixel | A count still climbing toward its final value |
| A cursor leaving frame | The claim of the shot still arriving |

One shipped frame runs a `rotate: -1.3 -> 1.0` tween across its entire hold minus 1.6s — it
is *moving* at the cut, deliberately, and it passes, because the thing the frame says landed
seconds earlier.

The complementary probe is the **dead-window** check: any window longer than **1.55s** in
which the full-DOM signature does not change at all. Both checks are needed. The resolution
check catches shots that end too late; the dead-window check catches shots that ended too
early and then sat there. Neither alone will tell you the film is paced.

**Prove the check before you change the film.** Two probe results on real films were wrong
rather than the frames: the grain-period false positive above, and a film that "ended on a
black frame" — the sample time was past the last frame's PTS, so ffmpeg returned a
placeholder. Per-frame luma over the final second was a flat 217. Bright ground, correct.

## Zoom is a property of the layout, not of the camera

If the composition is exactly the size of the stage, there is nowhere to push from:
scale 1.0 already shows everything, and any value above it crops. The camera cannot
magnify what is already at full size — it can only cut pieces off.

**So size the world smaller than the frame.** A 1280×720 interface inside a
1920×1080 stage means the *floor* of the camera is 1.5×, the whole surface is in
shot at that floor, and real magnification is available above it. This is the single
change that turned "I can barely see the text" into legible frames.

But there is a second trap, and it is the one that costs a rebuild:

### What must never leave the frame decides your ceiling

A director asking for a UI film wants the UI to read as a UI. That means its
chrome — the sidebar, the header, the input box — is not decoration to be cropped
when convenient. If the brief says *"you should actually see the text box"* and
*"we can actually see the sidebar as well"*, then the widest the camera may ever go
is the scale at which **all of that chrome fits**, and no shot may exceed it.

Work it out before you choreograph anything:

1. List the elements that must always be visible.
2. Find the bounding box that contains all of them.
3. `maxScale = min(stageW / boxW, stageH / boxH)`.
4. If the type is too small at that scale, **the type is too small** — enlarge the
   type inside the layout. Do not solve it by zooming past the box.

Then do the keep-out arithmetic on all four edges *before* choosing a scale. Under a
scale `s` about an origin `O`, a point `P` maps to `O + (P - O) * s`, so:

```
edge_after = edge + (edge - origin) * (s - 1)
```

A card whose bottom sits at y=872 with the push origin at y=395 tops out at scale 1.05
against an 897px keep-out line — 1.06 puts it at 900.6 and over. Put the push origin exactly
on the control being clicked and that control becomes a fixed point of the transform — no
compensating arithmetic at all, and it is the most natural-looking push anyway.

Anchoring is not a fix either. Pinning the frame to the bottom-left to "keep the
composer and sidebar in shot" showed the *bottom* of the sidebar, which is empty —
the channel list lives at the top. A real sidebar has content at the top and nothing
at the bottom; a real composer sits at the bottom. **You cannot have both by
anchoring to a corner. You can only have both by fitting the box.**

### One camera, two nodes

Never put a whole-shot rotation and a mid-shot scale on the same element. Two tweens
writing one transform matrix over an overlapping window means second-to-update wins each
frame, and the move judders. The outer node owns the dolly — scale, x, y — the inner node
owns the turn. The skeleton's `.dolly` / `.turn` pair is this split.

The other half of the rule is the cursor's — see "The cursor is a stage prop".

### Symptoms in the frames

- A wide empty band down one side is a chrome element you are seeing the blank half
  of, not a margin.
- Content sliced by the *top* edge is a scroll anchored to the bottom without a
  fixed header to stop against.
- A card cut by the input bar means the layout has no minimum gap between the last
  attachment and the fixed chrome. Enforce one; a card either clears it fully or is
  not in shot.
