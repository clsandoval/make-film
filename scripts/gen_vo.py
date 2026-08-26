#!/usr/bin/env python3
"""Render the voiceover, keeping the word alignment from the same generation.

/with-timestamps returns the audio AND the character alignment in one response,
so the file we ship and the times we cue to can never disagree. Ask for them
separately and they will.

Reads film.json. Writes assets/voice/*.wav and audio_meta.json.
Run order: gen_vo.py -> fix_vo.py -> build_timeline.py
"""
import base64
import json
import subprocess
import urllib.request

from film import FRAMES, ROOT, VOICE, api_key, voice_id

OUT = ROOT / "assets/voice"


def words_from_alignment(align: dict[str, object], text: str) -> list[dict[str, object]]:
    """Collapse per-character times into words by splitting on whitespace."""
    chars = align["characters"]
    starts = align["character_start_times_seconds"]
    ends = align["character_end_times_seconds"]
    assert isinstance(chars, list) and isinstance(starts, list) and isinstance(ends, list)

    words: list[dict[str, object]] = []
    buf, w_start = "", None
    for ch, s, e in zip(chars, starts, ends):
        if str(ch).strip() == "":
            if buf:
                words.append({"word": buf, "start": w_start, "end": e})
                buf, w_start = "", None
            continue
        if not buf:
            w_start = s
        buf += str(ch)
    if buf:
        words.append({"word": buf, "start": w_start, "end": ends[-1]})
    return words


def synth(key: str, name: str, text: str) -> dict[str, object]:
    body = json.dumps(
        {
            "text": text,
            "model_id": VOICE["model"],
            "voice_settings": {
                "stability": VOICE["stability"],
                "similarity_boost": VOICE["similarity_boost"],
                "style": VOICE["style"],
            },
        }
    ).encode()
    # Never send output_format=mp3_44100_192 — it 403s below Creator tier.
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id()}/with-timestamps",
        data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json"},
    )
    payload = json.load(urllib.request.urlopen(req))

    mp3, wav = OUT / f"{name}.mp3", OUT / f"{name}.wav"
    mp3.write_bytes(base64.b64decode(payload["audio_base64"]))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ar", "48000", "-ac", "1", str(wav)],
        check=True,
    )
    mp3.unlink()

    # measured, never taken from the API
    dur = float(
        subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    )
    words = words_from_alignment(payload["alignment"], text)
    print(f"{name:16} {dur:5.2f}s  {len(words):2d} words  {text[:44]}")
    return {"file": wav.name, "text": text, "duration": dur, "words": words}


def lines() -> dict[str, str]:
    """Frames with a `vo` string. A frame without one is silent by design."""
    return {f["id"]: f["vo"] for f in FRAMES if f.get("vo")}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    key = api_key()
    meta: dict[str, object] = {"voice_id": voice_id(), "model": VOICE["model"], "frames": {}}
    for name, text in lines().items():
        meta["frames"][name] = synth(key, name, text)
    total = sum(float(f["duration"]) for f in meta["frames"].values())
    meta["spoken_total"] = round(total, 2)
    (ROOT / "audio_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nspoken total: {total:.2f}s  ->  audio_meta.json")


if __name__ == "__main__":
    main()
