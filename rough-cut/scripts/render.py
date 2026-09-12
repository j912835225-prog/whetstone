#!/usr/bin/env python3
"""render - EDL -> finished cut.

Pipeline: extract each segment (pinned fps/height + 0.06s afade at both ends)
-> concat demuxer with -c copy -> loudnorm=I=-16:TP=-1.5:LRA=11 over the whole
file -> mux with -ar 48000.

Four traps, each one paid for:
  - A hard cut at a segment boundary pops. Fade 60ms in and out of every
    segment; do not use acrossfade.
  - Use the concat *demuxer* with `-c copy`, not the concat *filter*. The
    filter loops the first segment's audio track, and nothing about the picture
    shows you that it happened.
  - loudnorm raises the sample rate to 192k; mux without `-ar 48000` and the
    output lands at 96k AAC.
  - Mixed frame rates (30fps + 60fps sources) break `-c copy`, so every segment
    is re-encoded to one pinned frame rate.

EDL format: see SKILL.md. Usage:
    render.py edl.json -o out.mp4
    render.py edl.json -o preview.mp4 --preview     # 720p, fast
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

FADE = 0.06          # 60ms; 30ms also works, this is the conservative value
LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=11"

GRADES = {
    "none": "",
    "neutral_punch": "eq=contrast=1.06:saturation=1.02,curves=preset=medium_contrast",
    "warm_cinematic": "colorbalance=rs=.03:gs=0:bs=-.03:rm=.02:bm=-.02,eq=saturation=0.94:contrast=1.05",
}


def run(cmd: list[str], what: str) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"{what} failed:\n{' '.join(cmd)}\n{r.stderr[-1800:]}")


def probe(path: Path, entries: str, stream: str | None = None) -> str:
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream]
    cmd += ["-show_entries", entries, "-of", "csv=p=0", str(path)]
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().split("\n")[0]


def resolve_grade(name: str | None) -> str:
    if not name or name == "none":
        return ""
    return GRADES.get(name, name)          # unknown value = raw ffmpeg filter string


def extract_segment(src: Path, start: float, end: float, out: Path,
                    fps: str, height: int, grade: str, has_audio: bool) -> None:
    dur = end - start
    if dur <= 2 * FADE:
        sys.exit(f"segment too short ({dur:.2f}s) to carry two {FADE}s fades: "
                 f"{src.name} {start}-{end}")

    vf = [f"fps={fps}", f"scale=-2:{height}", "setsar=1"]
    if grade:
        vf.insert(1, grade)
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
           "-i", str(src), "-vf", ",".join(vf),
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"]
    if has_audio:
        af = (f"afade=t=in:st=0:d={FADE},"
              f"afade=t=out:st={max(dur - FADE, 0):.3f}:d={FADE}")
        cmd += ["-af", af, "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]
    else:
        cmd += ["-an"]
    cmd += ["-video_track_timescale", "90000", str(out)]
    run(cmd, f"extract {src.name} {start:.2f}-{end:.2f}")


def concat(parts: list[Path], out: Path, workdir: Path) -> None:
    lst = workdir / "_concat.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(out)], "lossless concat")
    lst.unlink(missing_ok=True)


def normalize(src: Path, out: Path, has_audio: bool) -> None:
    if not has_audio:
        shutil.copy(src, out)
        return
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-af", LOUDNORM, "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)], "loudness normalise")


def main() -> None:
    ap = argparse.ArgumentParser(description="EDL -> finished cut")
    ap.add_argument("edl", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--preview", action="store_true", help="720p, fast")
    a = ap.parse_args()

    edl = json.loads(a.edl.read_text())
    sources = {k: Path(v) for k, v in edl["sources"].items()}
    ranges = edl["ranges"]
    if not ranges:
        sys.exit("no ranges in the EDL")
    for k, p in sources.items():
        if not p.exists():
            sys.exit(f"missing source {k}: {p}")

    first = sources[ranges[0]["source"]]
    has_audio = bool(probe(first, "stream=codec_type", "a:0"))
    fps = edl.get("fps") or (probe(first, "stream=r_frame_rate", "v:0") or "30")
    height = 720 if a.preview else int(edl.get("height", 1080))
    grade = resolve_grade(edl.get("grade"))

    work = a.out.parent / "clips"
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    total = 0.0
    for i, r in enumerate(ranges):
        p = work / f"seg{i:03d}.mp4"
        extract_segment(sources[r["source"]], float(r["start"]), float(r["end"]),
                        p, fps, height, grade, has_audio)
        parts.append(p)
        total += float(r["end"]) - float(r["start"])
        print(f"  seg{i:02d} {r['source']} {r['start']:.2f}-{r['end']:.2f}"
              f"  {r.get('beat','')} {r.get('reason','')}".rstrip())

    base = a.out.parent / "_base.mp4"
    concat(parts, base, a.out.parent)
    normalize(base, a.out, has_audio)
    base.unlink(missing_ok=True)

    got = float(probe(a.out, "format=duration") or 0)
    print(json.dumps({
        "out": str(a.out), "segments": len(parts),
        "edl_duration_s": round(total, 2), "actual_duration_s": round(got, 2),
        "drift_s": round(got - total, 3),
        "fps": fps, "height": height, "audio": has_audio,
        "grade": edl.get("grade", "none"),
    }, ensure_ascii=False, indent=2))
    if abs(got - total) > 0.5:
        print("WARNING: output is >0.5s off the EDL; a segment was probably truncated",
              file=sys.stderr)


if __name__ == "__main__":
    main()
