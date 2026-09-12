#!/usr/bin/env python3
"""to_nle - EDL -> an editable NLE project (multi-track), not a flattened mp4.

    to_nle.py edl.json -o my_cut        # writes my_cut.xml (import this) + my_cut.edl

Eats the same edl.json as render.py: render.py gives you a deliverable, this
gives you a timeline you can keep cutting. The .xml is FCP7 XML (xmeml v4),
which DaVinci Resolve, Premiere Pro and Final Cut can all import.

Traps, all of them observed:
  - Let OTIO write the timecode; never hand-assemble it. CMX3600 wants
    HH:MM:SS:FF, and a decimal-seconds timecode like 00:00:04.566 is simply
    rejected on import.
  - media_reference must carry available_range, or the fcp_xml adapter raises
    `'NoneType' object has no attribute 'start_time'`.
  - Media paths must actually exist. An NLE rejects the whole timeline when a
    clip is offline, and the error usually says nothing more than "failed to
    import" - which looks identical to a malformed file.
  - Use the .xml extension: the output is xmeml v4 (FCP7 XML), not FCPXML 1.x.

Installs opentimelineio into a local venv on first run.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _env import ensure
ensure("opentimelineio", "opentimelineio-plugins")

import opentimelineio as otio                                   # noqa: E402
from opentimelineio.opentime import RationalTime as RT, TimeRange as TR  # noqa: E402


def probe_frames(src: Path, fps: float) -> int:
    """Total frames of the source. Fall back to duration x fps; without an
    available_range the adapter crashes."""
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=nb_frames", "-of",
                          "default=nw=1:nk=1", str(src)],
                         capture_output=True, text=True).stdout.strip()
    if out.isdigit() and int(out) > 0:
        return int(out)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(src)],
                         capture_output=True, text=True).stdout.strip()
    try:
        n = int(float(dur) * fps)
    except ValueError:
        n = 0
    if n <= 0:
        # An earlier version fell back to 1 frame here: unreadable media then
        # produced a clean exit code and a project the NLE silently refused.
        sys.exit(f"cannot read frame count or duration (is this file readable?): {src}")
    return n


def has_audio(src: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0",
                          "-show_entries", "stream=codec_type", "-of",
                          "default=nw=1:nk=1", str(src)],
                         capture_output=True, text=True).stdout.strip()
    return out == "audio"


def build(edl: dict, name: str) -> otio.schema.Timeline:
    fps_raw = str(edl.get("fps", "30"))
    fps = (float(fps_raw.split("/")[0]) / float(fps_raw.split("/")[1])
           if "/" in fps_raw else float(fps_raw))
    sources = {k: Path(v) for k, v in edl["sources"].items()}
    for k, p in sources.items():
        if not p.exists():
            sys.exit(f"missing media {k}: {p}\n"
                     f"(the NLE will reject the whole timeline and only say 'failed to import')")
    avail = {k: probe_frames(p, fps) for k, p in sources.items()}

    tl = otio.schema.Timeline(name=name)
    tl.global_start_time = RT(0, fps)
    track = otio.schema.Track(name="V1", kind=otio.schema.TrackKind.Video)
    for i, r in enumerate(edl["ranges"], 1):
        src = sources[r["source"]]
        ref = otio.schema.ExternalReference(target_url=str(src))
        ref.available_range = TR(RT(0, fps), RT(avail[r["source"]], fps))
        s = round(float(r["start"]) * fps)
        e = round(float(r["end"]) * fps)
        clip = otio.schema.Clip(name=r.get("beat") or f"seg{i:02d}", media_reference=ref,
                                source_range=TR(RT(s, fps), RT(max(e - s, 1), fps)))
        if r.get("reason"):
            clip.metadata["reason"] = r["reason"]
        track.append(clip)
    tl.tracks.append(track)

    # Audio track. Without it a dialogue cut opens in the NLE as a silent film.
    if all(has_audio(p) for p in sources.values()):
        atrack = otio.schema.Track(name="A1", kind=otio.schema.TrackKind.Audio)
        for clip in track:
            atrack.append(clip.deepcopy())
        tl.tracks.append(atrack)
    else:
        print("note: some source has no audio stream, writing video track only",
              file=sys.stderr)
    return tl


def main() -> None:
    ap = argparse.ArgumentParser(description="EDL -> editable NLE project")
    ap.add_argument("edl", type=Path)
    ap.add_argument("-o", "--out", required=True, help="output name, without extension")
    a = ap.parse_args()
    edl = json.loads(a.edl.read_text())
    out = Path(a.out)
    tl = build(edl, out.name)

    xml, ed = out.with_suffix(".xml"), out.with_suffix(".edl")
    otio.adapters.write_to_file(tl, str(xml), adapter_name="fcp_xml")
    otio.adapters.write_to_file(tl, str(ed), adapter_name="cmx_3600")
    n = len(tl.tracks[0])
    total = tl.duration().to_frames()
    kinds = [t.kind for t in tl.tracks]
    print(f"{n} segments / {total} frames / {len(tl.tracks)} tracks ({'+'.join(kinds)})")
    print(f"NLE project -> {xml}\nEDL         -> {ed}")
    print("DaVinci Resolve: File > Import > Timeline, pick the .xml")


if __name__ == "__main__":
    main()
