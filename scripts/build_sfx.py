#!/usr/bin/env python3
"""Synthesise the sound effects and mix them onto the narration bed.

Nothing is downloaded, sampled or licensed — every sample is computed here, so
there is no third-party audio in the film and a re-run is byte-identical.
Math.random has no place in a render; the noise source is a seeded LCG.

Cues come from film.json. A cue time is either a number (for a silent frame,
which has no word to sit on) or ["frame-id", "word"], resolved against the same
alignment the picture is cued to.

    "sfx": [
      {"sound": "click", "at": 1.22, "gain": 0.30},
      {"sound": "sub",   "at": ["09-potential", "yours"], "gain": 0.42}
    ]
"""
import math
import struct
import subprocess
import wave
from pathlib import Path

from film import CONFIG, ROOT, frame, resolve_time, timeline

RATE = 48000
OUT = ROOT / "assets/sfx"


def lcg(seed: int):
    """Deterministic noise. A render is not a lottery."""
    state = seed
    while True:
        state = (state * 1103515245 + 12345) % 2147483648
        yield state / 2147483648 * 2 - 1


def write_wav(name: str, samples: list[float]) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    peak = max(abs(s) for s in samples) or 1.0
    scaled = [int(max(-1.0, min(1.0, s / peak * 0.977)) * 32767) for s in samples]
    dest = OUT / name
    with wave.open(str(dest), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(struct.pack(f"<{len(scaled)}h", *scaled))
    return dest


def build_click(seed: int = 20260815) -> list[float]:
    """A short mechanical press: filtered noise with a woody resonance."""
    n = int(RATE * 0.085)
    rng = lcg(seed)
    out: list[float] = []
    lp = 0.0
    for i in range(n):
        t = i / RATE
        env = math.exp(-t * 105)
        lp += (next(rng) - lp) * 0.42  # one-pole low-pass: takes the fizz off
        body = math.sin(2 * math.pi * 1750 * t) * math.exp(-t * 170) * 0.5
        out.append((lp * 0.55 + body) * env)
    return out


def build_sub(seed: int = 0) -> list[float]:
    """One low note. Use it once, at the film's one resolution."""
    n = int(RATE * 1.35)
    out: list[float] = []
    for i in range(n):
        t = i / RATE
        # a short pitch drop reads as "settling" rather than as a hit
        f = 68.0 - 16.0 * (1 - math.exp(-t * 5.5))
        env = min(1.0, t / 0.035) * math.exp(-t * 2.35)
        out.append(math.sin(2 * math.pi * f * t) * env)
    return out


def build_tick(seed: int = 0) -> list[float]:
    """A dry UI tick — two short partials, no body."""
    n = int(RATE * 0.045)
    out: list[float] = []
    for i in range(n):
        t = i / RATE
        env = math.exp(-t * 260)
        out.append((math.sin(2 * math.pi * 2100 * t) + math.sin(2 * math.pi * 3300 * t) * 0.4) * env)
    return out


SYNTHS = {"click": build_click, "sub": build_sub, "tick": build_tick}


def cue_list(tl: dict[str, object]) -> list[tuple[Path, float, float]]:
    out: list[tuple[Path, float, float]] = []
    for spec in CONFIG.get("sfx", []):
        sound = spec["sound"]
        if sound not in SYNTHS:
            raise SystemExit(f"unknown sound {sound!r}: have {sorted(SYNTHS)}")
        path = write_wav(f"{sound}.wav", SYNTHS[sound](int(spec.get("seed", 20260815))))
        out.append((path, resolve_time(tl, spec["at"]), float(spec.get("gain", 0.3))))
    return out


def mix(tl: dict[str, object], cues: list[tuple[Path, float, float]]) -> None:
    voice = ROOT / "assets/voice/vo-track.wav"
    inputs: list[str] = []
    parts: list[str] = []
    labels: list[str] = []
    idx = 0
    if voice.exists():
        inputs += ["-i", str(voice)]
        parts.append("[0:a]volume=1.0[v]")
        labels.append("[v]")
        idx = 1
    for path, when, gain in cues:
        inputs += ["-i", str(path)]
        ms = int(when * 1000)
        parts.append(f"[{idx}:a]adelay={ms}|{ms},volume={gain}[c{idx}]")
        labels.append(f"[c{idx}]")
        idx += 1
    if not labels:
        raise SystemExit("nothing to mix: no voiceover and no sfx cues")
    # apad before -t: -t truncates but never pads, and a short bed lets -shortest
    # clip the film's tail off the master.
    graph = ";".join(parts) + f";{''.join(labels)}amix=inputs={len(labels)}:normalize=0,apad[out]"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
         "-map", "[out]", "-t", str(tl["duration"]), "-ar", "48000", "-ac", "2",
         str(ROOT / "assets/mix.wav")],
        check=True,
    )
    for path, when, gain in cues:
        print(f"{path.stem:8} @ {when:6.2f}s  gain {gain}")
    print(f"->  assets/mix.wav ({tl['duration']}s)")


def demo(tl: dict[str, object], cues: list[tuple[Path, float, float]]) -> None:
    """Self-check: every cue still lands inside the film after any retime."""
    for path, when, _ in cues:
        assert 0 <= when < float(tl["duration"]), f"{path.stem} @ {when}s is outside the film"
    for spec in CONFIG.get("sfx", []):
        if isinstance(spec["at"], list):
            f = frame(tl, str(spec["at"][0]))
            when = resolve_time(tl, spec["at"])
            assert float(f["start"]) <= when < float(f["start"]) + float(f["hold"]), \
                f"{spec['sound']} is cued to {f['id']} but lands outside it"
    print(f"self-check ok: {len(cues)} cues, all inside the film and their own frame")


if __name__ == "__main__":
    tl = timeline()
    cues = cue_list(tl)
    demo(tl, cues)
    mix(tl, cues)
