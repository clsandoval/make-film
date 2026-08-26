#!/usr/bin/env python3
"""Re-roll VO lines whose audio starts or ends mid-waveform, then fade every line.

eleven_v3 occasionally hands back a take that is truncated at a boundary — the
waveform is still at half amplitude on the first or last sample, which reads as a
click or a chopped word. Generation is stochastic, so the fix is to measure the
boundary and ask again until it comes back clean. The short fade at the end is
belt-and-braces: it kills any residual discontinuity without touching the read.
"""
import json
import struct
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from film import ROOT, api_key  # noqa: E402
from gen_vo import OUT, lines, synth  # noqa: E402

BOUNDARY_LIMIT = 0.03  # max amplitude allowed in the first/last 5ms
MAX_ATTEMPTS = 5
FADE_MS = 8


def boundaries(path: Path) -> tuple[float, float]:
    with wave.open(str(path)) as w:
        n, rate = w.getnframes(), w.getframerate()
        samples = struct.unpack(f"<{n}h", w.readframes(n))
    win = int(rate * 0.005)
    head = max(abs(x) for x in samples[:win]) / 32768
    tail = max(abs(x) for x in samples[-win:]) / 32768
    return head, tail


def trim_trailing_artifact(path: Path) -> float:
    """Cut a burst the model tacked on after the last word.

    DANGER: a word-final consonant looks almost exactly like an appended
    artifact — the closure before the /k/ in "check" or the /s/ in "chains" is a
    dip followed by a louder burst. An earlier, looser version of this function
    cut 50-130ms off five lines and chopped real speech. Three guards keep it
    honest:

      1. Only run at all when the take actually ends hot. A line that already
         decays to silence has nothing to repair, so we never touch it.
      2. Require a real gap — 40ms+ of near-silence, far longer than the closure
         before a consonant release.
      3. Cap what can be removed, so a misfire is small rather than a lost word.
    """
    head, tail = boundaries(path)
    if tail <= BOUNDARY_LIMIT:
        return 0.0  # guard 1: it already ends cleanly

    with wave.open(str(path)) as w:
        params = w.getparams()
        n, rate = w.getnframes(), w.getframerate()
        samples = list(struct.unpack(f"<{n}h", w.readframes(n)))

    bucket = int(rate * 0.010)
    tail_buckets = 20  # look at the last 200ms
    env = []
    for i in range(tail_buckets):
        a = n - (tail_buckets - i) * bucket
        env.append(max(abs(x) for x in samples[a:a + bucket]) / 32768)

    # guard 2: find a run of >=4 near-silent buckets (40ms), then a burst after it
    SILENT, MIN_GAP, MAX_REMOVE_MS = 0.02, 4, 120
    best_cut = None
    run_start = None
    for i, amp in enumerate(env):
        if amp < SILENT:
            run_start = i if run_start is None else run_start
            continue
        if run_start is not None and i - run_start >= MIN_GAP:
            best_cut = run_start  # a genuine gap ended here; everything after is suspect
        run_start = None
    if best_cut is None:
        return 0.0

    cut_at = n - (tail_buckets - best_cut) * bucket
    removed = (n - cut_at) / rate
    if removed * 1000 > MAX_REMOVE_MS:  # guard 3
        return 0.0

    with wave.open(str(path), "w") as w:
        w.setparams((params[0], params[1], params[2], cut_at, params[4], params[5]))
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples[:cut_at]))
    return removed


def apply_fade(path: Path) -> None:
    """An 8ms cosine-ish ramp at each end. Inaudible; removes the discontinuity."""
    with wave.open(str(path)) as w:
        params = w.getparams()
        n, rate = w.getnframes(), w.getframerate()
        samples = list(struct.unpack(f"<{n}h", w.readframes(n)))
    ramp = int(rate * FADE_MS / 1000)
    for i in range(ramp):
        g = i / ramp
        samples[i] = int(samples[i] * g)
        samples[n - 1 - i] = int(samples[n - 1 - i] * g)
    with wave.open(str(path), "w") as w:
        w.setparams(params)
        w.writeframes(b"".join(struct.pack("<h", s) for s in samples))


def main() -> None:
    meta = json.loads((ROOT / "audio_meta.json").read_text())
    key = api_key()
    rerolled: list[str] = []

    for name, text in lines().items():
        path = OUT / f"{name}.wav"
        head, tail = boundaries(path)
        if max(head, tail) <= BOUNDARY_LIMIT:
            print(f"{name:14} clean       head={head:.4f} tail={tail:.4f}")
            continue

        best = (max(head, tail), path.read_bytes(), meta["frames"][name])
        print(f"{name:14} re-rolling  head={head:.4f} tail={tail:.4f}")
        for attempt in range(1, MAX_ATTEMPTS + 1):
            entry = synth(key, name, text)
            h, t = boundaries(path)
            score = max(h, t)
            print(f"  attempt {attempt}: head={h:.4f} tail={t:.4f} dur={entry['duration']:.2f}")
            if score < best[0]:
                best = (score, path.read_bytes(), entry)
            if score <= BOUNDARY_LIMIT:
                break
        path.write_bytes(best[1])
        meta["frames"][name] = best[2]
        rerolled.append(name)
        print(f"  -> kept take scoring {best[0]:.4f}")

    for name in lines():
        path = OUT / f"{name}.wav"
        removed = trim_trailing_artifact(path)
        if removed:
            print(f"{name:14} trimmed {removed * 1000:.0f}ms of trailing artifact")
        apply_fade(path)
        # re-measure: a trim shortens the file, and build_timeline.py derives
        # every downstream cue from this number.
        meta["frames"][name]["duration"] = float(
            subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "csv=p=0", str(path)],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
        )

    meta["spoken_total"] = round(sum(f["duration"] for f in meta["frames"].values()), 2)
    (ROOT / "audio_meta.json").write_text(json.dumps(meta, indent=2))

    print(f"\nre-rolled: {', '.join(rerolled) or 'none'}")
    print(f"faded {FADE_MS}ms both ends on all {len(lines())} lines")
    print("\nfinal boundaries:")
    for name in lines():
        h, t = boundaries(OUT / f"{name}.wav")
        print(f"  {name:14} head={h:.4f} tail={t:.4f}")


if __name__ == "__main__":
    main()
