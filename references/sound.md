# Sound

Law 7: **sound is arithmetic.** Every claim in this file is a number you can reproduce, and
every claim about the mix is a measurement on the **delivered file** — never on the source.

Two rules define the approach. **Nothing licensed, nothing downloaded, nothing purchased** —
every sound is synthesised from `math` + `struct` + `wave`; across four films the SFX library
was four generated wavs in one and two in another. And **every cue time comes from
`timeline.json`**, the same word alignment the picture's reveals are cued to; no cue is ever a
typed second.

Synthesis buys three things a library cannot. It is **deterministic**, so a re-run is
byte-identical and a re-master is not a new mix. There is **nothing to licence**, which
removes the failure mode where a film is pulled because a bed was licensed for personal use.
And it is **exact** — a cue that needs to be 85 ms long at 1750 Hz is exactly that, rather
than trimmed out of a field recording that opens with 400 ms of room tone.

## Design first, generate second

The sound design is a paragraph in the brief before it is a line of Python. A real one:

> The design is two sounds, because the film's argument is that you stop operating things. A
> click marks the only press in the film. The pointer returns once at frame 04, reaches for
> the form's Next button and is refused — and that moment is **silent on purpose**: you have
> already learned what a click sounds like, so its absence is audible. One sub-bass marks the
> only other resolution.

Two sounds. That is the entire mix of a 59 s film, and the silence is one of its three events.
Rules that keep a cue table from becoming noise: **one cue per event, not per element**;
**match the cue to the physics** — a chime on a click is the tell of a template; **nothing
repeats more than twice**; **one sub-bass per film**, at the one resolution, because if
everything gets a sub nothing lands; and **silence is a cue**, but only if the sound it
replaces was established earlier.

## The generators

Every generator is a pure function of the sample index. Two from a shipped film, complete:

```py
def build_click() -> Path:
    """A short mechanical press: a filtered noise burst with a woody resonance."""
    n = int(RATE * 0.085)
    rng = lcg(20260815)
    out, lp = [], 0.0
    for i in range(n):
        t = i / RATE
        env = math.exp(-t * 105)
        lp += (next(rng) - lp) * 0.42                              # one-pole low-pass: takes the fizz off
        body = math.sin(2 * math.pi * 1750 * t) * math.exp(-t * 170) * 0.5
        out.append((lp * 0.55 + body) * env)
    return write_wav("click.wav", out)

def build_sub() -> Path:
    """One low note. The only sub-bass in the film, at the only resolution."""
    n = int(RATE * 1.35)
    out = []
    for i in range(n):
        t = i / RATE
        f = 68.0 - 16.0 * (1 - math.exp(-t * 5.5))                 # a short pitch drop reads as settling, not as a hit
        env = min(1.0, t / 0.035) * math.exp(-t * 2.35)
        out.append(math.sin(2 * math.pi * f * t) * env)
    return write_wav("sub.wav", out)
```

Four more from a different film, as shapes to steal: a **key press** (35 ms — deterministic
pseudo-noise from the sample index, one-pole low-pass at 0.35, `exp(-i / (RATE * 0.006))`
envelope; wooden, not hissy); a **panel arriving** (300 ms — a sine sweeping
`150 * exp(-t * 7) + 58` Hz under `exp(-t * 9)`; felt, not heard); a **sub-bass** (2.4 s —
44 Hz at 0.85 plus its octave at 0.15, a 0.5 s swell then `exp(-(t - 0.5) * 1.25)`); and a
**UI tick** (90 ms — 2100 Hz at 0.5 plus 3300 Hz at 0.25 under `exp(-t * 46)`).

`write_wav` normalises each asset to its own peak and writes 16-bit mono at 48 kHz. Level the
**asset**, not the cue: a cue's gain cannot rescue a quiet source, because summing a quiet
signal into a loud one changes the total by hundredths of a decibel.

`lcg(seed)` is the same seeded generator the picture uses for noise — see
`references/motion.md`.

## One source of timing

`build_sfx.py` reads `timeline.json` and resolves each cue by **word**, with the same
whole-word match the picture uses — and asserts that exactly one word matched:

```py
hits = [w for w in frame(frame_id)["words"] if str(w["word"]).strip(".,!?").lower() == needle.lower()]
assert len(hits) == 1, f"{frame_id}: {needle!r} matched {len(hits)} words"
return float(hits[0]["start"])
```

The assertion is the point: when the copy changes and the cue word disappears, the build
fails instead of quietly sliding the sound.

**The anti-pattern, from a real handoff.** One film hand-mirrored the picture's frame table
into its sound script, and its own handoff had to warn:

> `build_sfx.py` mirrors `film.html`'s frame table by hand. **If you retime the film, retime
> both** — they are not wired together, and the failure is silent.

That is the bug, not the workaround. Both `build_sfx.py` and `build_captions.py` read
`timeline.json`; neither holds a copy of anything.

**Authored times are legitimate where there is no word.** A silent cold open has no
alignment, so its cues are authored numbers — and then asserted against the frame table, so a
retime that moves the frame breaks the build rather than the film:
`assert all(0 < c < f1_end for c in clicks_at)`, `assert f9.start < sub_at < f9.start + f9.hold`,
`assert sub_at < TL["duration"]`.

## The mix graph

One `ffmpeg` invocation. The narration track is input 0; each cue is delayed into place with
`adelay` and gained with `volume`; everything sums through a single `amix`.

```py
inputs = ["-i", str(voice)]
parts = ["[0:a]volume=1.0[v]"]
for idx, (path, when, gain) in enumerate(cues, start=1):
    inputs += ["-i", str(path)]
    parts.append(f"[{idx}:a]adelay={int(when*1000)}|{int(when*1000)},volume={gain}[c{idx}]")
chain = "".join(f"[c{i}]" for i in range(1, len(cues) + 1))
graph = ";".join(parts) + f";[v]{chain}amix=inputs={len(cues)+1}:normalize=0,apad[out]"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
                "-map", "[out]", "-t", str(TL["duration"]),
                "-ar", "48000", "-ac", "2", str(dest)], check=True)
```

Four things in that graph are not optional:

| | |
|---|---|
| `adelay=<ms>\|<ms>` | Both channels. One value delays only the left. |
| `amix=...:normalize=0` | Default `normalize=1` divides every input by the input count, so adding one quiet tick quietly attenuates the narration. With many cues, add `dropout_transition=0` too. |
| **`apad` before `-t`** | `-t` truncates but never pads. A track whose last event ends before the film does stays short, and `-shortest` then clips the tail off the master. One real master came out **53.13s against a 54.2s render** — a second of end card, gone. |
| `-t TL["duration"]` | The mix is exactly as long as the film, by construction, not by luck. |

The same `apad`-then-`-t` pair builds `vo-track.wav` in `build_timeline.py`, for the same
reason.

## Mastering arithmetic

Target: **-14 LUFS integrated, true peak <= -1 dBTP.** That is what web and social platforms
normalise toward; delivering louder just means the platform turns you down and squashes your
dynamics for nothing.

`scripts/master.sh` runs two passes, then a residual loop.

**Pass 1 — measure.** `loudnorm` cannot correct what it has not measured.

```bash
ffmpeg -hide_banner -i "$MIX" -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 |
  sed -n '/^{/,/^}/p'
```

Read `input_i`, `input_tp`, `input_lra`, `input_thresh`, `target_offset` — **and
`normalization_type`**, the field that decides whether you need the loop.

**Pass 2 — normalise and limit.**

```bash
-af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$THRESH:offset=$OFFSET:linear=true,alimiter=limit=0.891:level=disabled,aresample=48000"
```

`alimiter=limit=0.891` is -1.0 dBFS. `linear=true` computes **one** gain for the whole file
from the pass-1 numbers and does not back off for a transient, so a limiter after it is not
belt-and-braces — it is the thing that catches a peak going over. **`level=disabled` is
mandatory**: `alimiter` scales its output by `level_out / limit`, so `limit=0.891` alone
applies about +1 dB of makeup gain, and the limiter added to protect the target overshoots it.

**Pass 3 — the residual loop.** `linear=true` is only *possible* when the mix's crest factor
is at most `target_TP - target_I`, which at -14/-1 is **13 dB**. Above that, `loudnorm`
silently falls back to `dynamic` and lands short. A voiced mix with a quiet bed under long
holds against speech peaks measured a **~20 dB crest factor** and came in **~0.6 dB under
target** with no error printed anywhere.

So the last stage measures the normalised audio and applies the exact difference, repeatedly:

```bash
for i in 1 2 3 4; do
  GOT=$(ffmpeg -hide_banner -i "$TMP/cur.wav" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | grep -oE '\-?[0-9.]+' | head -1)
  ADJ=$(awk -v t=$TARGET_I -v g="$GOT" 'BEGIN{printf "%.2f", t-g}')
  OK=$(awk -v a="$ADJ" 'BEGIN{print (a<0.2 && a>-0.2) ? 1 : 0}')
  echo "    iter $i: $GOT LUFS (residual ${ADJ} dB)"
  [ "$OK" = "1" ] && break
  ffmpeg -y -loglevel error -i "$TMP/cur.wav" \
    -af "volume=${ADJ}dB,alimiter=limit=0.891:level=disabled" -ar 48000 -ac 1 "$TMP/next.wav"
  mv "$TMP/next.wav" "$TMP/cur.wav"
done
```

**One residual pass is not enough**, because the limiter eats part of any correction: a
+2.10 dB pass was observed landing at -14.6. Hence up to four iterations, converging to
+/-0.2 LU — and **failing loudly rather than shipping silently off**.

Do not replace the loop with a hand-tuned gain. That was tried on another film: its first
master landed -14.5 (edge of spec) because `loudnorm` fell back to `dynamic` and the limiter
took a further 0.3 dB, and the fix was to re-master at a -13.6 target to land mid-spec. That
works once, for one mix, and is not a method.

## Verify on the delivered file

The filter graph's own report proves nothing. Measure what you will ship.

```bash
ffmpeg -hide_banner -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | tail -14
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate \
  -of default=noprint_wrappers=1 "$OUT"
```

Pass: **-14 LUFS +/- 0.5, true peak <= -1 dBTP.** Real shipped results: -13.7 / -1.0 / LRA
7.9; -14.2 / -1.0 / LRA 9.8; -14.0 to -14.2 with true peak <= -3.4.

**And prove every cue is present in the delivered file.** "It sounds fine to me" is not
evidence at 11pm on the machine that rendered it. A real readout:

> Three landings at **-6.9 dB** max against **-91 dB** digital silence between them; the
> collapse sub is **+20.7 dB** in the sub-120 Hz band while the above-200 Hz speech band
> **rose** to -18.3 dB — measured, so no masking.

The band-split is what turns "I think the sub is masking the voice" into a number: measure
the two bands separately over the cue window and compare against the same window with the cue
removed.

One measurement trap: **`-v error` on a measurement pass suppresses the readout.**
`volumedetect` and `ebur128` print to stderr at info level. Drop `-v error` when you want the
numbers.

## Silent cuts

A film destined for a muted autoplay feed carries no meaning in its audio, and one shipped
that way deliberately: a room-tone bed under the wait, accelerating ticks that stop when the
thing they count stops, and then **the bed stops 0.55 s before the cut, so silence lands
first and the arrival lands into it.** Nothing after the answer.

Even then the track is generated, mastered and measured like any other — a silent-feed film
still gets played with sound on by someone, and a track that has never been measured is a
track that is wrong.
