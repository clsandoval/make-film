# Deliverables

Gate G6. A film is not one file, and shipping only the master is the most common way a good
film underperforms — it plays muted in a feed, letterboxed into a slot it was not composed
for, with a thumbnail nobody chose.

Decide the set at intake (G0), because some of it changes how the frames are composed:
a 9:16 cut only works if every shot keeps its payload in a central band and its top and
bottom edge rows clear of content.

## The set

| File | Notes |
|---|---|
| **Master**, the aspect the film was composed in | -14 LUFS, <= -1 dBTP, `-crf 19 -tune film -movflags +faststart` |
| **1:1 cut** | Common feed placement |
| **9:16 cut**, captions burned in | Muted feeds. See the four traps below |
| **`.srt`** | Sidecar for the master, so a landing-page hero stays clean |
| **Poster frame** | Chosen, not frame 0 |
| **Review encode** | A small copy for sending through a chat transport during the note rounds |
| **`HANDOFF.md`** | Direction, rebuild commands, licences, open items |

`scripts/deliverables.sh` derives every one of them **from the newest master**, so a cut can
never go stale against the film it came from.

## Aspect cuts: resize `#stage`, not the viewport

The composition lives inside a fixed-size `#stage` element and the renderer screenshots that
element, not the page. So setting the Playwright viewport to 1080x1080 for a square cut
silently produces a **4:5 file labelled 1:1** — the stage kept its own dimensions and the
screenshot was of the stage. This shipped once, as "the 1:1 cut is done", and it was a
mislabelled copy of the master. **Resize `#stage`; the viewport is not the frame.**

And know which of the two things you are doing:

| | What it is | Cost |
|---|---|---|
| **Letterbox** | The same picture, padded into a taller frame | An ffmpeg filter |
| **Re-layout** | The frames rebuilt at the new size, type re-broken, columns stacked | A separate film |

A letterbox is honest when every frame is a centred composition on a plain ground. It is not
a re-layout and should never be described as one. A film whose shots are two-column, or
whose type is sized for a wide frame, needs the second option — and that is a new
storyboard, not a flag.

The letterbox is worth improving even so. One shipped 9:16 crops the empty side margins
before scaling, because the panels all live between two known x-values: a **1500 px centre
crop loses nothing and lifts the picture from 32% to 40% of a 9:16 frame** — the difference
between readable and not, on a phone.

## Trap 1 — flat-colour bars leave seams

If the film's ground carries a vignette, padding to a single hex leaves two visible bands
where the pad meets the picture. On one film the ground runs from one value at the top edge
to a different one at the bottom, so `pad=...:0xRRGGBB` produced a seam at each join.

**Build the letterbox out of the picture's own edge rows.** Crop a thin strip from the top
and one from the bottom, stretch each vertically to the height of its bar, and composite:

```
[b]crop=1500:16:210:0,scale=1080:571:flags=bilinear[top];
[c]crop=1500:16:210:1064,scale=1080:571:flags=bilinear[bot];
```

This continues the gradient seamlessly. It works only because every frame in that film keeps
its first and last ~20 rows clear of content — there is nothing in those strips to smear.
Reserve that margin at storyboard time or this technique is unavailable to you.

A raw edge strip carries film grain, and stretching it 30x turns the grain into vertical
streaks; blur the bands horizontally, or generate them from a de-grained pass.

## Trap 2 — libass sizes a bare `.srt` against 384x288

**Every style number in a `force_style` on a bare SRT is scaled by `PlayResY / 288`.** They
are not pixels.

An SRT carries no ASS header, so libass assumes a default `PlayRes` of 384x288 and scales
everything by `height / 288`. At 1350 px tall that factor is **4.6875**. `original_size` does
**not** override it.

The first attempt on a real film used `FontSize=30` / `MarginV=96` and rendered roughly
**140 px type floating in the middle of the frame**. The working values were pre-divided:
`FontSize=7` becomes ~33 px, `MarginV=44` becomes ~206 px — clear of the footer rule.

Two ways out, and prefer the second:

1. **Pre-divide the numbers** in `force_style` and write down why, or the next person will
   "fix" them.
2. **Convert to `.ass` and patch an explicit `PlayRes`** matching the output size, so every
   number is a real pixel again:

```bash
ffmpeg -y -i "$SRT" "$ASS"     # then rewrite PlayResX/PlayResY to the output dimensions
```

Whichever you choose, **look at a burned frame.** This was found by extracting a frame, not
by trusting the filter's exit code.

## Trap 3 — ASS alpha is inverted

`&H00` is **opaque**. `&HFF` is **transparent**.

A caption box authored with a `BackColour` alpha of `CC` — intended as "mostly opaque" —
rendered as a washed-out grey instead of a solid box. `1A` is about 90% opaque.

Colours are `&HAABBGGRR`, so the byte order is reversed too. Get both wrong at once and the
caption is a different colour at a different transparency, which reads as a font problem.

## Trap 4 — `split` and `vstack` in some ffmpeg builds

Two build-specific failures found while composing a 9:16 letterbox. Both have the same
symptom (a segfault, no useful message) and both have a mechanical workaround:

- **Reusing `[0:v]` more than once relies on ffmpeg's implicit split**, which segfaulted.
  Split explicitly: `[0:v]split=3[a][b][c]`.
- **`vstack` with three inputs segfaulted** (malloc corruption, reproducible). Composite the
  letterbox with `pad` plus two `overlay`s instead:

```
[a]crop=1500:1080:210:0,scale=1080:778,pad=1080:1920:0:571:$GROUND[base];
[base][top]overlay=0:0[s1];
[s1][bot]overlay=0:1349[stacked];
[stacked]ass='$ASS':fontsdir='<film>/assets/fonts/ttf'[v]
```

Pass `fontsdir` pointing at the film's own font directory, or libass substitutes whatever the
system has and the captions ship in the wrong typeface.

Burn captions with `-c:a copy`. Re-encoding the audio re-normalises a track you already
mastered and measured.

## Captions come from the alignment

`scripts/build_captions.py` reads `timeline.json` — the same word alignment the reveals are
cued to — and splits each frame's narration into reader-sized chunks **on word boundaries**,
at a 42-character maximum. Nothing is typed by hand, which is why the captions cannot drift
from the picture the way a hand-authored or re-transcribed track does.

Its self-check is the part worth copying: cues are ordered, non-overlapping, and the last one
ends inside the film.

Style them in the film's own typeface, positioned above the platform's bottom chrome. On a
light ground, navy type on the picture with **no outline and no shadow** is legible and looks
designed; on a ground that changes value mid-film, an opaque box is the honest answer,
because white-on-transparent will vanish over the light half.

If you burn captions in, keep an un-captioned master. A site hero usually should not have
them, and someone will ask.

## Poster frame

Pick it. The browser otherwise shows frame 0, which is usually an empty ground.

Choose the one frame that states the whole claim — typically the resolve, not the end card —
and test it at **200 px wide**, which is the size most people will see it at. Avoid a
half-typed string, a mid-motion frame, or a frame with a cursor in it.

```bash
ffmpeg -y -ss 51.6 -i "$MASTER" -frames:v 1 "$OUT/poster.png"
```

## The review encode

A `-crf 19 -tune film` master of a 36s 1920x1080 film runs about **70 MB at ~15.7 Mb/s**,
which will not go through a chat transport — the usual bot upload cap is 50 MB. Ship a second,
smaller encode alongside it purely for the note rounds. Real numbers from two shipped films:

| | Master | Review encode |
|---|---|---|
| 41.27s film | 78 MB | 23 MB |
| 35.77s film | 68 MB, 15.7 Mb/s video, 159 kb/s audio | 22 MB, 5.0 Mb/s video, 101 kb/s audio |

Same resolution, same duration, lower bitrate. The director notes on the review encode; the
master is what ships. Never let the review encode become the deliverable.

## Verify every variant

A cut is a re-encode, and a re-encode can be wrong. Run the same probe on every file:

```bash
ffprobe -v error -show_entries format=duration -show_entries stream=width,height -of csv=p=0 "$f"
```

Check the **dimensions** (catches a mislabelled aspect), the **duration** (catches
`-shortest` clipping a tail), and, on anything that touched audio, the loudness.
`deliverables.sh` prints that table at the end of every run for exactly this reason.

## Licences and `HANDOFF.md`

Write the licence block even when the answer is "none". The sentence a real handoff carries:

> Nothing third-party is embedded. The fonts, the logo and the cover art are the real files
> the subject already ships, used unmodified. The whole audio track is synthesised by
> `scripts/build_sfx.py`; no music bed, no purchased SFX.

`HANDOFF.md` also carries:

- **The deliverable table** — which file is for which placement, and which one is the master.
  Where a film ships two cuts they may not be the same edit at different lengths; say so.
- **The measured numbers** on the delivered files.
- **The rebuild commands**, in order, with a note on what is derived from what.
- **Superseded files**, kept and named, with one line on why they were superseded — including
  any asset that was deleted with an instruction not to regenerate it.
- **Open items** — decisions the film took a position on that were not actually agreed, the
  one invented element, anything refused at the truth pass, and which frames change if a
  pending decision lands elsewhere.
- **What I would fix next** — the weakest beat, named, with the fix.

Renders are versioned, never overwritten. `v5` is how you prove `v6` fixed it.
