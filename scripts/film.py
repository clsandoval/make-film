#!/usr/bin/env python3
"""The one per-film contract: film.json.

Every script here is generic. Everything that differs between films — the name,
the stage size, the voice, the frame list, the pads, the SFX cues — lives in
film.json next to film.html. Nothing is hand-edited inside a script.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("FILM_ROOT", Path.cwd()))
if not (ROOT / "film.json").exists():  # allow running from scripts/
    ROOT = Path(__file__).resolve().parent.parent

CONFIG = json.loads((ROOT / "film.json").read_text())

VOICE = {
    "model": "eleven_v3",
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.0,
    **CONFIG.get("voice", {}),
}


def voice_id() -> str:
    """Checked where it is used, not at import — a silent film needs no voice."""
    if "id" not in VOICE:
        sys.exit(
            'film.json needs a voice: {"voice": {"id": "<elevenlabs voice id>"}}\n'
            "  Pick one at https://elevenlabs.io/app/voice-library and copy its ID.\n"
            "  Cast it deliberately — the voice is a casting decision, not a default."
        )
    return str(VOICE["id"])
FPS = int(CONFIG.get("fps", 30))
STAGE = {"w": 1920, "h": 1080, **CONFIG.get("stage", {})}
NAME = CONFIG["name"]
FRAMES = CONFIG["frames"]


def api_key() -> str:
    """ELEVENLABS_API_KEY, from the environment or a dotenv beside the film."""
    if key := os.environ.get("ELEVENLABS_API_KEY"):
        return key
    for env in (ROOT / ".env", Path.home() / ".config/film/.env"):
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("\"'")
    sys.exit(
        "ELEVENLABS_API_KEY not set.\n"
        "  export ELEVENLABS_API_KEY=sk-...\n"
        "  or put it in ./.env or ~/.config/film/.env"
    )


def timeline() -> dict[str, object]:
    return json.loads((ROOT / "timeline.json").read_text())


def frame(tl: dict[str, object], frame_id: str) -> dict[str, object]:
    try:
        return next(f for f in tl["frames"] if f["id"] == frame_id)
    except StopIteration:
        raise SystemExit(f"no frame {frame_id!r} in timeline.json") from None


def norm(word: str) -> str:
    """Strip surrounding punctuation, keep internal apostrophes ("don't")."""
    return re.sub(r"^[^a-z0-9]+|[^a-z0-9']+$", "", word.lower())


def cue(tl: dict[str, object], frame_id: str, needle: str, occurrence: int = 1) -> float:
    """Film-time start of a word. Whole-word, and it refuses to guess.

    The launch film matched substrings and silently took the first hit; a needle
    that appears twice then cues the wrong syllable and nothing tells you.
    """
    words = frame(tl, frame_id)["words"]
    want = norm(needle)
    hits = [w for w in words if norm(str(w["word"])) == want]
    if not hits:
        raise SystemExit(f"{frame_id}: no word {needle!r} in {[w['word'] for w in words]}")
    if len(hits) > 1 and occurrence == 1:
        raise SystemExit(f"{frame_id}: {needle!r} matches {len(hits)} words — pass an occurrence")
    if occurrence > len(hits):
        raise SystemExit(f"{frame_id}: {needle!r} has no occurrence {occurrence}")
    return float(hits[occurrence - 1]["start"])


def resolve_time(tl: dict[str, object], spec: object) -> float:
    """A cue time is a number, ["frame-id", "word"] / [.., .., occurrence], or
    {"frame": .., "word": .., "offset": 0.15} when it must land just off a word.

    Prefer a word form. A number does not survive a VO regeneration: three ticks
    written as 14.2/15.6/17.0 migrated into the wrong beat when one line was
    re-recorded, and nothing failed."""
    if isinstance(spec, (int, float)):
        return float(spec)
    if isinstance(spec, list) and len(spec) in (2, 3):
        return cue(tl, str(spec[0]), str(spec[1]), int(spec[2]) if len(spec) == 3 else 1)
    if isinstance(spec, dict):
        return cue(tl, str(spec["frame"]), str(spec["word"]),
                   int(spec.get("occurrence", 1))) + float(spec.get("offset", 0.0))
    raise SystemExit(f"bad cue time {spec!r}: want a number, [frame, word], or {{frame, word, offset}}")
