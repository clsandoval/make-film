# QA

## The friction, and what removes it

Every item here cost real time on a real film. They are ordered by how much.

### A composition that throws looks exactly like a slow render

`stills.mjs` and `render.mjs` wait for `window.__ready`. If the composition throws
before setting it, the wait times out and you get `TimeoutError` with an empty log —
no mention of the actual error, which is sitting in a `pageerror` you already
captured. **`openFilm` must re-throw the captured page errors on timeout.** Without
that, a one-character mistake costs a ten-minute detour. It has done, twice.

```js
try {
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 15000 });
} catch (e) {
  if (errors.length) throw new Error(`composition threw before __ready:\n  ${errors.join("\n  ")}`);
  throw e;
}
```

### `str.replace` that matches nothing fails silently

Patching a composition with `s.replace(old, new)` and a stale `old` is a no-op that
reports success. One left a reference to a data field that had been deleted; the
film rendered `undefined` on screen in three places and the only symptom was the
timeout above. **Assert before you replace.** Every edit:

```python
assert old in s, f"NOT FOUND: {old[:70]}"
```

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

### Absolute SSIM measures the encoder, not the shards

Film grain on a dark ground costs ~0.02 SSIM at crf 16 whether or not a shard seam
is near. A fixed 0.995 threshold fails every seam — and also frame 0, which is not a
seam, which is the tell. **Baseline on mid-shard frames, then ask only whether the
seams are worse than that.**

### The two gates need different signatures

A camera drift, a list scroll and a typing indicator all "change the DOM", but none
of them is content arriving:

- **Camera** (`data-camera`): a push or a scroll is the edit. Its own transform must
  be excluded from both checks, or every shot reads as never settling.
- **Ambient** (`data-ambient`): a typing indicator or a read-position marker is
  interface state. The **dead-window** check wants it — the screen genuinely is
  alive. The **resolution** check must not see it, or a shot can never cut while it
  pulses.

Measure the DOM with `offsetLeft/offsetTop/offsetWidth/offsetHeight` and the
element's own `getComputedStyle().transform` — never `getBoundingClientRect()`,
which folds in every ancestor transform and turns one camera move into "everything
changed".

### "Nothing ends unresolved" and "no dead windows" leave a 0.2s band

Resolve by `hold − 1.0s`, never freeze for more than ~1.5s: on a long narration line
those two rules nearly collide. The answer is not to loosen a threshold. It is to
give the film something that is *alive but not arriving* — a slow continuous camera
drift, or an ambient marker that tracks the narration. Both are excluded from the
resolution signature, so a shot can resolve while the screen still breathes.

### A reveal belongs to the beat it lands in

Starting the next beat's message early makes the current shot never resolve, and the
gate reports it as the *current* beat failing. When resolution fails on a beat whose
content clearly settled, look at what the following beat starts early.

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
