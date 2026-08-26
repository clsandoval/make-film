#!/usr/bin/env python3
"""Write the .srt from the same word timings the film's reveals are cued to.

The film carries no burned-in captions, so muted feeds need this file. Nothing
here is typed by hand: every cue time comes from the ElevenLabs alignment that
is already in timeline.json, which is why the captions cannot drift from the
picture the way a hand-authored subtitle track does.
"""
from film import CONFIG, NAME, ROOT, timeline

TL = timeline()
MAX_CHARS = int(CONFIG.get("caption", {}).get("max_chars", 42))  # readable at a glance


def stamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def cues() -> list[tuple[float, float, str]]:
    """Split each frame's narration into reader-sized chunks on word boundaries."""
    out: list[tuple[float, float, str]] = []
    for frame in TL["frames"]:
        words = frame["words"]
        if not words:
            continue
        frame_end = float(frame["start"]) + float(frame["hold"])
        chunk: list[dict[str, object]] = []
        for word in words:
            candidate = " ".join([*(str(w["word"]) for w in chunk), str(word["word"])])
            if chunk and len(candidate) > MAX_CHARS:
                out.append((float(chunk[0]["start"]), float(word["start"]),
                            " ".join(str(w["word"]) for w in chunk)))
                chunk = []
            chunk.append(word)
        if chunk:
            out.append((float(chunk[0]["start"]), frame_end,
                        " ".join(str(w["word"]) for w in chunk)))
    return out


def demo() -> None:
    """Self-check: cues are ordered, non-overlapping, and inside the film."""
    rows = cues()
    assert rows, "no cues built"
    for (a_start, a_end, _), (b_start, _, _) in zip(rows, rows[1:]):
        assert a_start < a_end, f"cue at {a_start} ends before it starts"
        assert a_end <= b_start + 1e-6, f"cue at {a_start} overlaps the next"
    assert rows[-1][1] <= float(TL["duration"]) + 1e-6, "last cue runs past the film"
    print(f"self-check ok: {len(rows)} cues, ordered, none past {TL['duration']}s")


if __name__ == "__main__":
    if not any(f["words"] for f in TL["frames"]):
        # A silent film has no speech to caption. Not an error.
        raise SystemExit("no narration in timeline.json — nothing to caption")
    demo()
    lines = []
    for i, (start, end, text) in enumerate(cues(), start=1):
        lines.append(f"{i}\n{stamp(start)} --> {stamp(end)}\n{text}\n")
    dest = ROOT / f"deliverables/{NAME}.srt"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text("\n".join(lines))
    print(f"-> {dest}")
