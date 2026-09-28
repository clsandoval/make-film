# Sound

Applies to every style in [styles/](../styles/); each style's RECIPE.md says which parts it uses.

Law 7: **sound is arithmetic.** Every claim in this file is a number you can reproduce, and
every claim about the mix is a measurement on the **delivered file** — never on the source.

Two rules define the approach. **Nothing licensed, nothing downloaded, nothing purchased** —
every sound is synthesised from `math` + `struct` + `wave`; across four films the SFX library
was four generated wavs in one and two in another. And **every cue time comes from
`timeline.json`**, the same word alignment the picture's reveals are cued to; no cue in a
voiced film is ever a typed second.

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

Every `SYNTHS` entry has the same signature — **it takes only a seed and returns samples**.
`cue_list` owns the filename, writing `<sound>-<seed>.wav`, because two cues of the same sound
with different seeds once wrote one filename and every cue got the last seed's audio. A
generator that calls `write_wav` itself, or returns a `Path`, crashes the caller.

```py
def build_click(seed: int = 20260815) -> list[float]:
    """A short mechanical press: a filtered noise burst with a woody resonance."""
    n = int(RATE * 0.085)
    rng = lcg(seed)
    out, lp = [], 0.0
    for i in range(n):
        t = i / RATE
        env = math.exp(-t * 105)
        lp += (next(rng) - lp) * 0.42                              # one-pole low-pass: takes the fizz off
        body = math.sin(2 * math.pi * 1750 * t) * math.exp(-t * 170) * 0.5
        out.append((lp * 0.55 + body) * env)
    return out

def build_sub(seed: int = 0) -> list[float]:
    """One low note. The only sub-bass in the film, at the only resolution."""
    n = int(RATE * 1.35)
    out = []
    for i in range(n):
        t = i / RATE
        f = 68.0 - 16.0 * (1 - math.exp(-t * 5.5))                 # a short pitch drop reads as settling, not as a hit
        env = min(1.0, t / 0.035) * math.exp(-t * 2.35)
        out.append(math.sin(2 * math.pi * f * t) * env)
    return out
```

A cue's `seed` keys both the filename and the generator argument, so it only changes the
*audio* of a generator that draws from `lcg(seed)` — `click` alone, today. On `sub` and `tick`
it changes nothing but the filename; they take the parameter so the dispatch stays uniform.

Four more from a different film, as shapes to steal: a **key press** (35 ms — deterministic
pseudo-noise from the sample index, one-pole low-pass at 0.35, `exp(-i / (RATE * 0.006))`
envelope; wooden, not hissy); a **panel arriving** (300 ms — a sine sweeping
`150 * exp(-t * 7) + 58` Hz under `exp(-t * 9)`; felt, not heard); a **sub-bass** (2.4 s —
44 Hz at 0.85 plus its octave at 0.15, a 0.5 s swell then `exp(-(t - 0.5) * 1.25)`); and a
**UI tick** (90 ms — 2100 Hz at 0.5 plus 3300 Hz at 0.25 under `exp(-t * 46)`).

`write_wav` normalises each asset to its own peak and writes 16-bit mono at 48 kHz. Level the
**asset**, not the cue: a cue's gain cannot rescue a quiet source, because summing a quiet
signal into a loud one changes the total by hundredths of a decibel.

And never peak-normalise a whole mix that has one big arrival in it. One film's arrival was
**11x the bed**, so normalising to that transient left the beds ~22 dB down and the source at
**-27.6 LUFS**. Bring the transient down; do not push makeup gain through a limiter that will
then eat it.

`lcg(seed)` is the same seeded generator the picture uses for noise — see
`references/motion.md`.

## One source of timing

`build_sfx.py` reads `timeline.json` and resolves every cue through `film.resolve_time`,
which matches whole words after `norm()` strips surrounding punctuation and keeps internal
apostrophes — the same match the picture uses:

```py
def norm(w):
    return re.sub(r"^[^a-z0-9]+|[^a-z0-9']+$", "", str(w).lower())
```

A needle matching more than one word in the frame is a hard failure — `SystemExit`, not an
assert — unless you pass an occurrence index: `["09-potential", "yours", 2]`. So a copy edit
that duplicates or removes a cue word stops the build instead of sliding the sound.

The assertion is the point: when the copy changes and the cue word disappears, the build
fails instead of quietly sliding the sound.

**The anti-pattern, from a real handoff.** One film hand-mirrored the picture's frame table
into its sound script, and its own handoff had to warn:

> `build_sfx.py` mirrors `film.html`'s frame table by hand. **If you retime the film, retime
> both** — they are not wired together, and the failure is silent.

That is the bug, not the workaround. Both `build_sfx.py` and `build_captions.py` read
`timeline.json`; neither holds a copy of anything.

**A numeric cue time is only legitimate in a film with no voiceover.** Three tick SFX
hardcoded at `14.2 / 15.6 / 17.0` migrated into the wrong beat the moment one line was
re-recorded, and nothing failed — the numbers were still valid, they were just in a different
scene. Every cue in a voiced film is `["frame-id", "word"]`, `["frame-id", "word", occurrence]`, or
`{"frame": .., "word": .., "offset": 0.15, "occurrence": 1}` when it must land just off a
word. All of them resolve through `resolve_time` in `scripts/film.py` — and `resolveTime` in
`scripts/film.mjs`, which is why a `probes.hits` entry takes the same forms — against the
alignment the picture is cued to. `build_sfx.py`'s self-check asserts every word-form cue
lands inside its own frame, so a negative `offset` large enough to push a cue before its
frame's start fails the build.

A silent cold open has no alignment, so its cues are authored numbers — and then asserted
against the frame table, so a retime that moves the frame breaks the build rather than the
film:
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
-af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$THRESH:offset=$OFFSET:linear=true,alimiter=limit=0.85:level=disabled,aresample=48000"
```

`alimiter`'s limit is a **sample-peak** ceiling; the gate reads **true peak**, which can sit
higher. Sample peak is the largest number in the file; true peak is the largest value of the
*continuous waveform a converter reconstructs between* those samples, so a signal whose samples
all sit at -1.0 dBFS can reconstruct above it — and a lossy encode, which does not preserve
sample values, moves the reconstruction again. That is why the ceiling has to be measured on
the delivered AAC and not assumed from the limiter setting.

`limit=0.891` is -1.0 dBFS — the target exactly, with nothing in hand. Measured across the
delivered masters, every film limited there read exactly **-1.0 dBTP**, clamped to spec by
the limiter rather than passing it with room, and both films that moved to `limit=0.85`
(-1.4 dBFS) read **-1.4 dBTP**, 0.4 dB in hand. A mix that never reaches the ceiling lands well under it
either way — one earlier film at 0.891 delivered **-3.4 dBTP** — which is why the -1.0 readings
read as the limiter clamping the mix rather than as headroom that happened to be there. Zero
margin is the finding: any platform re-encode pushes a -1.0 master over.

`linear=true` computes **one** gain for the whole file from the pass-1 numbers and does not
back off for a transient, so a limiter after it is not belt-and-braces — it is the thing that
catches a peak going over. **`level=disabled` is mandatory**: `alimiter` scales its output by
`level_out / limit`, so `limit=0.85` alone applies about +1.4 dB of makeup gain, and the
limiter added to protect the target overshoots it.

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
    -af "volume=${ADJ}dB,alimiter=limit=0.85:level=disabled" -ar 48000 -ac 1 "$TMP/next.wav"
  mv "$TMP/next.wav" "$TMP/cur.wav"
done
```

Shape only — `master.sh` runs this loop on the muxed mp4 with an accumulating `volume=` inside
the pass-2 chain, and gates true peak inside it.

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

Pass: **-14 LUFS +/- 0.2** — the tolerance `master.sh` actually gates on, after four
convergence passes — **and true peak <= -1 dBTP.** Real shipped results: -13.7 / -1.0 / LRA
7.9; -14.2 / -1.0 / LRA 9.8; -14.0 to -14.2 with true peak <= -3.4; and the two `limit=0.85`
masters at -14.1 / -1.4.

True peak was printed here for four films and **gated in none of them**. `master.sh` now exits
non-zero on a delivered true peak above target.

**And prove every cue is present in the delivered file.** "It sounds fine to me" is not
evidence at 11pm on the machine that rendered it. A real readout:

> Three landings at **-6.9 dB** max against **-91 dB** digital silence between them; the
> collapse sub is **+20.7 dB** in the sub-120 Hz band while the above-200 Hz speech band
> **rose** to -18.3 dB — measured, so no masking.

The band-split is what turns "I think the sub is masking the voice" into a number: measure
the two bands separately over the cue window and compare against the same window with the cue
removed.

**Verify a cue with an envelope, not a window peak.** A window peak proves a cue is loud
*somewhere*; it cannot see a cue that starts late. One film shipped a typing cue whose window
peak was a healthy -1.4 dB while **56% of the animation played in silence**, because the sound
landed 0.435 s in:

```
t=10.72  -4.6 dB   <- narration only; the animation has already started
t=11.12  -1.6 dB   <- the first keystroke finally lands
```

So print peak per 100 ms slice across the cue window:

```bash
ffmpeg -hide_banner -i "$OUT" -af \
  "atrim=10.5:12.5,asetnsamples=n=4800,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.Peak_level" \
  -f null -
```

`asetnsamples=n=4800` is what makes a slice exactly 100 ms at 48 kHz; without it `astats`
resets every 1024 samples, which is 23 ms. Read **peak** for percussive cues, never
mean: mean tells you a bed is present, peak tells you a transient was heard. A cue is audible
when its transients land within ~12 dB of the narration in the same window.

One measurement trap: **`-v error` on a measurement pass suppresses the readout.**
`volumedetect` and `ebur128` print to stderr at info level. Drop `-v error` when you want the
numbers.

## A silence check proves absence of loudness, not absence of artifact

`silencedetect` at a coarse threshold (e.g. -35dB) will happily call a gap "silent" while a
breath, mouth-click or room-tone swell sits in it well above the noise floor but below the
threshold. One film's opening line lost its first word to encoder priming (the take started
0.192s in, sitting exactly on the sample the player eats), and the gap between it and the next
line measured 953ms of "silence" at -35dB — a listener still heard a breath there, because a
real take artifact clears -50dB without ever approaching -35dB. **Run the check tighter than
you think you need** (-50dB, `d=0.02`) and where it disagrees with your ear, trust the ear:
listen to the raw take, don't just read the detector's verdict.

**Do not drop a cleanup pass because a later step damaged something upstream of it.** One
session skipped its own boundary-fade script (the thing applying an 8ms fade to every clip
edge) because an earlier re-roll pass had wrecked some takes, and shipped a film where every
clip butts a non-zero sample straight into digital silence — audible clicks at every cut. The
fade script was not the thing that broke the takes; skipping it was an unrelated regression
introduced to route around a different bug. Fix the step that's actually broken. If a script
must be skipped, that is a flagged gap to close before delivery, not a silent omission — say
out loud what got skipped and why, so it doesn't ship as "verified."

## Silent cuts

A film destined for a muted autoplay feed carries no meaning in its audio, and one shipped
that way deliberately: a room-tone bed under the wait, accelerating ticks that stop when the
thing they count stops, and the bed cut 0.55 s before the turn, so silence lands first and the
arrival lands into it.

**What that film did next broke its master.** Nothing followed the answer, so 28 of 37.4 s were
pure digital silence, integrated loudness measured **-15.0 LUFS**, and no makeup gain recovered
it without the limiter eating the arrival. The film's own diagnosis: *"the cause is a creative
bug, not a mastering one."*

Silence itself is free — R128's absolute gate drops blocks below -70 LUFS, so digital silence
never enters the integration at all. Measured, not assumed: a 10 s tone and the same tone with
30 s of silence appended both read **-41.1 LUFS** — the same number, to 0.0 LU.

```bash
ffmpeg -f lavfi -i "sine=f=1000:d=10,volume=-20dB" -af ebur128 -f null -
ffmpeg -f lavfi -i "sine=f=1000:d=10,volume=-20dB,apad=pad_dur=30" -af ebur128 -f null -
```

The damage is the other side of the same gate. It measures only the loud
blocks, so a film whose sustained content is a handful of cues in its first third is measured on
those cues alone, and reaching -14 takes gain the limiter then eats. Sparse loud material, not
silence, is what puts the target out of reach — which is why the fix is a bed, not a gain.

That film's fix was a brighter pad fading up on the arrival over 1.6 s and sustaining to the
end — the first thing scoring its second half at all.

**A film that opens on true digital silence reads as broken audio**: the viewer turns it up,
just in time for the first line to arrive loud. **No bed generator ships and there is no
`film.json` bed key** — do not go looking for one. A bed is a `SYNTHS` entry like any other,
cued from the `sfx` array like any other, but two things differ. The generator takes only a seed, so it must read
its own length from `timeline()["duration"]` (or its stop time) and bake the 1.2 s fade-in and
0.25 s fade-out into the samples — long enough not to click, short enough to register as an
absence. And `write_wav` peak-normalises it like a click, so unlike every other cue a bed's
level **is** its cue gain. Expect it to cost crest factor — a bed under long holds is the
~20 dB case in Pass 3.

Even then the track is generated, mastered and measured like any other — a silent-feed film
still gets played with sound on by someone, and a track that has never been measured is a
track that is wrong.
