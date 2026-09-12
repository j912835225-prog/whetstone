#!/usr/bin/env python3
"""shots - video -> shot boundaries, at frame precision, without scanning by eye.

    shots.py a.mp4                      # print the shot table
    shots.py a.mp4 --edl edl.json       # also write an EDL render.py / to_nle.py can eat

Two outputs, deliberately not mixed:
  - Shot boundaries (form). Where the picture changes. Frame precise, objective,
    reproducible.
  - Long shots get a warning, not an interpretation. Any shot longer than
    `--long` seconds prints "a machine cannot tell you what happens inside this
    one, look at it yourself". An earlier version tried pixel-difference
    "event detection" here; tested against real footage it ranked the only real
    event (a person being knocked down) below three cars passing, because a car
    crossing frame moves far more pixels than two small figures fighting. The
    whole block was deleted; an honest warning is worth more.
  - Parameter self-check. Boundaries are detected at 0.75x / 1x / 1.3x of the
    threshold; if the counts disagree the script says so. Measured on one clip:
    thresholds 12/20/27 all gave 3 shots, 35 collapsed it to 1. A threshold you
    have not stress-tested is not a parameter, it is a guess.

Traps:
  - Do not hand-write timecode into an EDL. CMX3600 wants HH:MM:SS:FF; decimal
    seconds are silently rejected by NLEs. Always go through to_nle.py,
    which lets OTIO write the timecode.
  - 27 is the ContentDetector default: it shreds fast-cut material and misses
    slow dissolves. Tune --threshold per source.

Needs: ffprobe on PATH. Installs scenedetect + opencv into a local venv on first run.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _env import ensure
ensure("scenedetect", "opencv-python")

from scenedetect import open_video, SceneManager, ContentDetector  # noqa: E402


def probe_fps(src: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=r_frame_rate", "-of",
                          "default=nw=1:nk=1", str(src)],
                         capture_output=True, text=True).stdout.strip()
    if "/" in out:
        a, b = out.split("/")
        return float(a) / float(b)
    return float(out or 30)


def detect(src: Path, threshold: float, min_len: int) -> list[tuple[int, int]]:
    vid = open_video(str(src))
    sm = SceneManager()
    sm.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_len))
    sm.detect_scenes(vid)
    scenes = sm.get_scene_list()
    if not scenes:                       # single-shot video: scenedetect returns []
        total = int(vid.duration.get_frames()) if vid.duration else 0
        return [(0, total)]
    return [(s.get_frames(), e.get_frames()) for s, e in scenes]


def main() -> None:
    ap = argparse.ArgumentParser(description="shot boundary detection (frame precise)")
    ap.add_argument("src", type=Path)
    ap.add_argument("--threshold", type=float, default=27.0)
    ap.add_argument("--min-len", type=int, default=15, help="shortest shot, in frames")
    ap.add_argument("-o", "--out", type=Path, help="shot table JSON")
    ap.add_argument("--edl", type=Path, help="also write an EDL (render.py format)")
    ap.add_argument("--long", type=float, default=8.0, help="warn above this many seconds")
    a = ap.parse_args()
    if not a.src.exists():
        sys.exit(f"missing source: {a.src}")

    fps = probe_fps(a.src)
    scenes = detect(a.src, a.threshold, a.min_len)
    shots = [{"n": i, "start_frame": s, "end_frame": e,
              "start": round(s / fps, 3), "end": round(e / fps, 3),
              "frames": e - s, "seconds": round((e - s) / fps, 3)}
             for i, (s, e) in enumerate(scenes, 1)]

    print(f"{a.src.name}  fps={fps:.3f}  {len(shots)} shots")
    for sh in shots:
        print(f"  shot{sh['n']:02d}  {sh['start']:8.3f}s -> {sh['end']:8.3f}s  "
              f"({sh['frames']} frames / {sh['seconds']}s)")

    for sh in shots:
        if sh["seconds"] >= a.long:
            print(f"  ^ shot{sh['n']:02d} runs {sh['seconds']}s - a machine cannot tell you "
                  f"what happens inside it; watch it yourself")

    # Self-check: a boundary that only exists at one threshold is a fragile boundary.
    lo = detect(a.src, a.threshold * 0.75, a.min_len)
    hi = detect(a.src, a.threshold * 1.3, a.min_len)
    if not (len(lo) == len(scenes) == len(hi)):
        print(f"  ! unstable: thresholds {a.threshold*0.75:.0f}/{a.threshold:.0f}/"
              f"{a.threshold*1.3:.0f} give {len(lo)}/{len(scenes)}/{len(hi)} shots - this "
              f"clip changes its answer with the parameter, so do not treat these "
              f"boundaries as settled; look at it first")

    payload = {"source": str(a.src.resolve()), "fps": fps, "shots": shots}
    if a.out:
        a.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"shot table -> {a.out}")
    if a.edl:
        edl = {"version": 1, "sources": {"S01": str(a.src.resolve())},
               "fps": f"{fps:.6f}/1", "height": 1080, "grade": "none",
               "ranges": [{"source": "S01", "start": sh["start"], "end": sh["end"],
                           "beat": f"shot{sh['n']:02d}",
                           "reason": "automatic boundary, no human judgement yet - "
                                     "review every line before using it"}
                          for sh in shots]}
        a.edl.write_text(json.dumps(edl, ensure_ascii=False, indent=2))
        print(f"EDL -> {a.edl}  (automatic boundaries, not an edit decision)")


if __name__ == "__main__":
    main()
