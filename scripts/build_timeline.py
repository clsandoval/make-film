#!/usr/bin/env python3
"""Derive every frame start from measured voiceover, and lay the narration track.

Nothing here is typed by hand. The only authored timing in the whole pipeline is
each frame's `pad` in film.json — the breath after its last word. Durations come
from ffprobe; cue times come from the ElevenLabs alignment.

    hold = vo.duration + pad          (voiced frame)
    hold = pad                        (silent frame — no `vo` in film.json)

Writes timeline.json, timeline.js and assets/voice/vo-track.wav.
"""
import json
import subprocess

from film import FPS, FRAMES, ROOT, cue  # noqa: F401  (cue re-exported for other scripts)


def build() -> dict[str, object]:
    meta_path = ROOT / "audio_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"frames": {}}
    frames: list[dict[str, object]] = []
    t = 0.0
    for spec in FRAMES:
        frame_id, pad = spec["id"], float(spec["pad"])
        if spec.get("vo"):
            vo = meta["frames"][frame_id]
            hold = float(vo["duration"]) + pad
            words = [
                {"word": w["word"], "start": round(t + float(w["start"]), 3)}
                for w in vo["words"]
            ]
        else:
            hold, words = pad, []
        frames.append(
            {
                "id": frame_id,
                "start": round(t, 3),
                "hold": round(hold, 3),
                "vo": frame_id if spec.get("vo") else None,
                "voStart": round(t, 3) if spec.get("vo") else None,
                "words": words,
            }
        )
        t += hold
    return {"fps": FPS, "duration": round(t, 3), "frames": frames}


def build_vo_track(tl: dict[str, object]) -> None:
    """Lay each frame's narration at its film-time offset in one wav."""
    voice = ROOT / "assets/voice"
    inputs: list[str] = []
    filters: list[str] = []
    idx = 0
    for f in tl["frames"]:
        if not f["vo"]:
            continue
        inputs += ["-i", str(voice / f"{f['vo']}.wav")]
        delay_ms = int(round(float(f["voStart"]) * 1000))
        filters.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")
        idx += 1
    if not idx:
        print("no voiceover — skipping vo-track.wav")
        return
    mix = "".join(f"[a{i}]" for i in range(idx))
    # apad first: -t truncates but never pads, so without it the track ends at
    # the last word and -shortest clips the film's tail off the master.
    graph = ";".join(filters) + f";{mix}amix=inputs={idx}:normalize=0,apad[out]"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", graph,
         "-map", "[out]", "-t", str(tl["duration"]), "-ar", "48000", "-ac", "2",
         str(voice / "vo-track.wav")],
        check=True,
    )
    print(f"vo-track.wav  {tl['duration']}s")


def demo(tl: dict[str, object]) -> None:
    """Self-check: frames tile the timeline, every word lands inside its frame."""
    for a, b in zip(tl["frames"], tl["frames"][1:]):
        expected = round(float(a["start"]) + float(a["hold"]), 3)
        assert abs(expected - float(b["start"])) < 1e-6, f"gap or overlap before {b['id']}"
    last = tl["frames"][-1]
    assert abs(float(last["start"]) + float(last["hold"]) - float(tl["duration"])) < 1e-6
    for f in tl["frames"]:
        if f["words"]:
            assert float(f["words"][-1]["start"]) < float(f["start"]) + float(f["hold"]), \
                f"{f['id']}: a word starts after the frame ends"
    print("self-check ok: frames tile the timeline, all words land inside their frame")


if __name__ == "__main__":
    tl = build()
    demo(tl)
    build_vo_track(tl)
    (ROOT / "timeline.js").write_text("window.TIMELINE = " + json.dumps(tl, indent=2) + ";\n")
    (ROOT / "timeline.json").write_text(json.dumps(tl, indent=2))
    for f in tl["frames"]:
        end = float(f["start"]) + float(f["hold"])
        print(f"{f['id']:16} {float(f['start']):6.2f} -> {end:6.2f}")
    print(f"\ntotal {tl['duration']}s @ {tl['fps']}fps")
