# Motion

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
window.__seek = (t) => { master.seek(t, false); };   // false = suppress callbacks-on-seek side effects
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

Film grain is one tiled PNG generated once, positioned by a fixed offset table stepped as a
series of `master.set()` calls — eight offsets at 12 steps per second:

```js
const GRAIN = [[0, 0], [-91, 47], [63, -112], [-140, -33], [111, 88], [-27, 131], [148, 19], [-72, -95]];
for (let i = 0; i * (1 / 12) < TL.duration; i++) {
  const [gx, gy] = GRAIN[i % GRAIN.length];
  master.set($("grain"), { x: gx, y: gy }, i * (1 / 12));
}
```

The layer is inset well beyond the stage (`inset: -256px`) so the offsets never expose an
edge, at low opacity with `mix-blend-mode: multiply`.

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

## Entrances, easings and staggers

A consistent motion vocabulary is what makes ten frames read as one film. One shipped
composition's whole vocabulary, as a table — the numbers are that film's, but the *ratios*
are the transferable part:

| Move | Tween | Duration | Ease |
|---|---|---|---|
| Frame crossfade in | `fromTo` opacity 0 -> 1 | 0.42 | `power2.out` |
| Frame crossfade out | `to` opacity 0, starting at `start + hold - 0.42 * 0.5` | 0.42 | `power2.in` |
| Panel / card entrance | `fromTo` `{y: 26-34, opacity: 0}` -> `{y: 0, opacity: 1}` | 0.60-0.75 | `power3.out` |
| Line or row reveal | `fromTo` `{opacity: 0, x: -14}` or `{opacity: 0, y: 10-14}` | 0.28-0.42 | `power2.out` |
| Button press | scale 1 -> 0.96 then back to 1 | 0.10 down, 0.16-0.18 up | `power2.in` / `power2.out` |
| Pointer travel | `to` `{x, y}` | 0.52-0.55 | `power2.inOut` |
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

## Nothing ends unresolved

Law 6, and the one most often mis-applied.

**The rule:** by the time a shot cuts, what the shot is *saying* must have arrived. A reveal
that lands in the last second of a hold arrives as the cut does, and the viewer sees it
leaving rather than arriving.

The mechanical form, checked by `probe.mjs`: **a frame's last change-point must be no later
than `start + hold - 1.0s`.** The probe steps at 1/30s through each frame, hashes a signature
of every descendant (`x, y, w, h, opacity, color, filter, className, textContent.length`),
records the last time the signature changed, and prints the margin against the deadline.

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

The complementary probe is the **dead-window** check: any window longer than **1.2s** in
which the full-DOM signature does not change at all. Both checks are needed. The resolution
check catches shots that end too late; the dead-window check catches shots that ended too
early and then sat there. Neither alone will tell you the film is paced.

**Prove the check before you change the film.** Two probe results on real films were wrong
rather than the frames: the grain-period false positive above, and a film that "ended on a
black frame" — the sample time was past the last frame's PTS, so ffmpeg returned a
placeholder. Per-frame luma over the final second was a flat 217. Bright ground, correct.
