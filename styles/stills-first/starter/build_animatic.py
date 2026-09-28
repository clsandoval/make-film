#!/usr/bin/env python3
"""Build a stills animatic: each still held for its duration, optional voiceover under it.

    build_animatic.py shots.json OUT.mp4 [--stills DIR] [--vo vo.wav] [--label]

shots.json:
  {"size": [720, 1280], "fps": 24,
   "shots": [{"id": "b01", "still": "b01.png", "dur": 2.0, "line": "optional VO words"}, ...]}

Stills are letterboxed (never stretched) onto the size. With --vo the audio is padded with silence
or cut so the file ends with the last shot; the script reports the gap between plan and VO length.
--label burns the shot id and start time into the corner for review copies. Local ffmpeg only.
"""
import argparse, json, pathlib, subprocess, sys

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def probe_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan"); ap.add_argument("out")
    ap.add_argument("--stills", help="folder the still paths are relative to (default: the plan's folder)")
    ap.add_argument("--vo", help="voiceover wav to lay under the stills")
    ap.add_argument("--label", action="store_true", help="burn shot id and start time into the corner")
    a = ap.parse_args()

    plan_p = pathlib.Path(a.plan).resolve()
    plan = json.loads(plan_p.read_text())
    w, h = plan.get("size", [1920, 1080]); fps = plan.get("fps", 24)
    root = pathlib.Path(a.stills).resolve() if a.stills else plan_p.parent
    shots = plan["shots"]
    if not shots:
        sys.exit("no shots in plan")
    missing = [s["still"] for s in shots if not (root / s["still"]).exists()]
    if missing:
        sys.exit(f"missing stills in {root}: {missing}")

    # one looped input per still, each fitted to the frame, then the concat filter. (The concat demuxer
    # drops stills when their pixel sizes differ: ffmpeg rebuilds the filter graph and loses the held frame.)
    cmd, parts, labels, t = ["ffmpeg", "-v", "error", "-y"], [], [], 0.0
    fit = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
           f"setsar=1,fps={fps},format=yuv420p")
    for i, s in enumerate(shots):
        d = float(s["dur"])
        cmd += ["-loop", "1", "-framerate", str(fps), "-t", f"{d:.3f}", "-i", str(root / s["still"])]
        parts.append(f"[{i}:v]{fit}[v{i}]")
        labels.append((s.get("id", s["still"]), t, t + d))
        t += d
    total = t
    graph = ";".join(parts) + ";" + "".join(f"[v{i}]" for i in range(len(shots))) + f"concat=n={len(shots)}:v=1:a=0"
    if a.label:
        for sid, t0, t1 in labels:
            txt = f"{sid}  {t0:.2f}s".replace(":", r"\:")
            graph += (f",drawtext=fontfile={FONT}:text='{txt}':fontsize={max(18, h // 40)}:fontcolor=white:"
                      f"box=1:boxcolor=black@0.6:boxborderw=8:x=20:y=20:enable='between(t,{t0:.3f},{t1:.3f})'")
    graph += "[v]"
    if a.vo:
        cmd += ["-i", a.vo]
    cmd += ["-filter_complex", graph, "-map", "[v]"]
    if a.vo:
        cmd += ["-map", f"{len(shots)}:a", "-af", "apad", "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-t", f"{total:.3f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)

    got = probe_duration(a.out)
    msg = f"{a.out}: {len(shots)} shots, plan {total:.2f}s, file {got:.2f}s, {w}x{h} @ {fps}"
    if a.vo:
        vo = probe_duration(a.vo)
        msg += f", VO {vo:.2f}s"
        if vo > total + 0.05:
            print(f"WARNING: the VO runs {vo - total:.2f}s past the last shot and was cut; lengthen the last shots",
                  file=sys.stderr)
    print(msg)


if __name__ == "__main__":
    main()
