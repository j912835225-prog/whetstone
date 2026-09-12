#!/usr/bin/env python3
"""selftest - prove this toolchain still works. No external footage: it builds its own.

    selftest.py                # everything green, or do not trust the SKILL.md claims
    selftest.py --with-whisper # also exercise transcribe.py (downloads a model)

Why it exists: a written report cannot verify itself, a runnable assertion can.
Every check below has a known answer computed from a synthetic fixture, so a
failure means the tool, the environment, or the invocation is broken - not that
the assertion needs relaxing.

Covers: shots -> EDL -> NLE export, pack, timeline_view, render.
Skips transcribe unless --with-whisper (model weights are a large download).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FPS = 30
PY_ = sys.executable


def sh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True)


def tail_json(out: str) -> dict:
    """Scripts print progress lines before their JSON summary; take the summary."""
    return json.loads(out[out.index("{"):])


def make_fixture(d: Path) -> Path:
    """A 6s clip: red/green/blue for 2s each, with tone, so shot boundaries are
    known to be at frames 60 and 120.

    It must carry audio: "video and audio tracks both present" is a load-bearing
    claim for the NLE export, and a silent fixture can never test it.
    """
    parts = []
    for i, color in enumerate(("red", "green", "blue")):
        p = d / f"{i}.mp4"
        sh("ffmpeg", "-v", "error", "-y",
           "-f", "lavfi", "-i", f"color=c={color}:s=320x240:r={FPS}:d=2",
           "-f", "lavfi", "-i", f"sine=frequency={220 * (i + 1)}:duration=2",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(p))
        parts.append(p)
    lst = d / "l.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    out = d / "fixture.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
       "-c", "copy", str(out))
    return out


def fake_words(src: Path, edit_dir: Path) -> Path:
    """A hand-written word table with a known 1.0s gap in the middle, so pack and
    timeline_view can be checked without running an ASR model."""
    words = [
        {"word": "one", "start": 0.20, "end": 0.60, "speaker": "S0"},
        {"word": "two", "start": 0.65, "end": 1.00, "speaker": "S0"},
        {"word": "three", "start": 1.05, "end": 1.50, "speaker": "S0"},
        # 1.0s gap here -> exactly one gap marker and one line break
        {"word": "four", "start": 2.50, "end": 2.90, "speaker": "S0"},
        {"word": "five", "start": 2.95, "end": 3.40, "speaker": "S0"},
    ]
    out = edit_dir / "transcripts" / f"{src.stem}.words.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"source": str(src), "stem": src.stem, "duration": 6.0,
                               "language": "en", "words": words}, ensure_ascii=False))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="self-test for the rough-cut toolchain")
    ap.add_argument("--with-whisper", action="store_true",
                    help="also run transcribe.py (downloads model weights)")
    a = ap.parse_args()

    if sh("ffprobe", "-version").returncode != 0:
        print("FAIL · ffmpeg/ffprobe not on PATH, nothing here can run")
        return 1
    fails: list[str] = []

    def check(name: str, ok: bool, got: str = "") -> None:
        print(f"{'ok  ' if ok else 'FAIL'} · {name}{'' if ok else '  got=' + got}")
        if not ok:
            fails.append(name)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        edit = d / "edit"
        src = make_fixture(d)
        check("fixture built (6s, three colours, with audio)",
              src.exists() and src.stat().st_size > 0)

        # (1) shot boundaries: known answer 60 / 120 frames
        r = sh(PY_, str(HERE / "shots.py"), str(src),
               "-o", str(d / "s.json"), "--edl", str(d / "edl.json"))
        if r.returncode != 0:
            check("shots.py runs", False, r.stderr.strip()[-300:])
            return report(fails)
        shots = json.loads((d / "s.json").read_text())["shots"]
        check("shots.py finds 3 shots", len(shots) == 3, str(len(shots)))
        edges = [s["start_frame"] for s in shots]
        check("boundaries at frames 0/60/120 (+-2)",
              len(edges) == 3 and all(abs(x - y) <= 2 for x, y in zip(edges, [0, 60, 120])),
              str(edges))

        # (2) NLE export: timecode must be HH:MM:SS:FF, never decimal seconds
        r = sh(PY_, str(HERE / "to_nle.py"), str(d / "edl.json"), "-o", str(d / "t"))
        if r.returncode != 0:
            check("to_nle.py runs", False, r.stderr.strip()[-300:])
            return report(fails)
        xml, ed = d / "t.xml", d / "t.edl"
        check("writes .xml and .edl", xml.exists() and ed.exists())
        body = ed.read_text()
        tcs = re.findall(r"\d\d:\d\d:\d\d[:;.]\d+", body)
        bad = [t for t in tcs if not re.fullmatch(r"\d\d:\d\d:\d\d[:;]\d\d", t)]
        check("EDL timecode is HH:MM:SS:FF (or drop-frame ;FF), no decimal seconds",
              bool(tcs) and not bad, f"{len(tcs)} total, {len(bad)} malformed")
        x = xml.read_text()
        check("xml is xmeml v4", '<xmeml version="4">' in x)
        check("xml carries 3 clipitems per track", x.count("<clipitem") == 6,
              str(x.count("<clipitem")))
        check("media path written into the xml", str(src) in x)

        # The next three check values, not shapes. An earlier version of this
        # file only counted elements: a mutated build with every segment start
        # set to 0 passed all eight checks. Counting is not asserting.
        io = re.findall(r"<in>(-?\d+)</in>\s*<out>(-?\d+)</out>", x)
        got = [(int(p), int(q)) for p, q in io][:3]
        want = [(0, 60), (60, 120), (120, 180)]
        check("per-segment in/out frame values are right",
              len(got) == 3 and all(abs(g[0] - w[0]) <= 1 and abs(g[1] - w[1]) <= 1
                                    for g, w in zip(got, want)), str(got))
        starts = [int(v) for v in re.findall(r"<start>(-?\d+)</start>", x)][:3]
        check("segments are butt-joined on the timeline",
              starts[:3] == [0, 60, 120] if len(starts) >= 3 else False, str(starts[:3]))
        kinds = re.findall(r"<(video|audio)>", x)
        check("video and audio tracks both present",
              "video" in kinds and "audio" in kinds, str(kinds))
        check("EDL event count is 3", len(re.findall(r"(?m)^0\d\d\s", body)) == 3,
              str(len(re.findall(r"(?m)^0\d\d\s", body))))

        # (3) pack: one known 1.0s gap -> one gap marker, two lines
        words_json = fake_words(src, edit)
        r = sh(PY_, str(HERE / "pack.py"), "--edit-dir", str(edit))
        if r.returncode != 0:
            check("pack.py runs", False, r.stderr.strip()[-300:])
        else:
            packed = (edit / "takes_packed.md").read_text()
            body_gaps = len(re.findall(r"⟨gap \d", packed))
            check("pack.py marks exactly the one 1.0s gap", body_gaps == 1, str(body_gaps))
            check("pack.py breaks the words into 2 lines",
                  len(re.findall(r"(?m)^  \[", packed)) == 2,
                  str(len(re.findall(r"(?m)^  \[", packed))))
            check("pack.py keeps word text", "three" in packed and "four" in packed)

        # (4) timeline_view: renders a png and finds the same gap
        png = d / "view.png"
        r = sh(PY_, str(HERE / "timeline_view.py"), str(src), "0", "4",
               "-o", str(png), "--words", str(words_json))
        if r.returncode != 0:
            check("timeline_view.py runs", False, r.stderr.strip()[-300:])
        else:
            info = tail_json(r.stdout)
            check("timeline_view.py writes a png", png.exists() and png.stat().st_size > 2000,
                  str(png.stat().st_size if png.exists() else 0))
            check("timeline_view.py reads all 5 words in the window",
                  info["words"] == 5, str(info["words"]))
            check("timeline_view.py finds the 1.0s gap",
                  any(abs(g[0] - 1.5) < 0.05 and abs(g[1] - 2.5) < 0.05
                      for g in info["gaps"]), str(info["gaps"]))

        # (5) render: two segments, known total, drift under the tolerance
        edl = {"version": 1, "sources": {"A": str(src)}, "height": 240, "fps": "30/1",
               "grade": "none",
               "ranges": [{"source": "A", "start": 0.5, "end": 2.0, "beat": "one"},
                          {"source": "A", "start": 4.0, "end": 5.5, "beat": "two"}]}
        (d / "r.json").write_text(json.dumps(edl))
        r = sh(PY_, str(HERE / "render.py"), str(d / "r.json"), "-o", str(d / "cut.mp4"))
        if r.returncode != 0:
            check("render.py runs", False, r.stderr.strip()[-400:])
        else:
            info = tail_json(r.stdout)
            check("render.py output exists", (d / "cut.mp4").exists())
            check("render.py duration matches the EDL within 0.5s",
                  abs(info["drift_s"]) <= 0.5, str(info["drift_s"]))
            check("render.py keeps the audio track", info["audio"] is True)

        # (6) optional: the ASR leg
        if a.with_whisper:
            r = sh(PY_, str(HERE / "transcribe.py"), str(src),
                   "--edit-dir", str(d / "edit2"), "--model", "tiny", "--language", "en")
            check("transcribe.py runs and writes a word table",
                  r.returncode == 0 and list((d / "edit2" / "transcripts").glob("*.words.json")),
                  r.stderr.strip()[-300:])
        else:
            print("skip · transcribe.py (pass --with-whisper to include it)")

    return report(fails)


def report(fails: list[str]) -> int:
    print()
    if fails:
        print(f"FAIL · {len(fails)} check(s) failed: " + "; ".join(fails))
        print("Do not relax the assertions to match the result. Find the cause first: "
              "the tool, the invocation, or the environment.")
        return 1
    print("all green · shots, NLE export, pack, timeline_view and render are usable"
          + (" (transcribe included)" if "--with-whisper" in sys.argv else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
