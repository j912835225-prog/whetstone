#!/usr/bin/env python3
"""pack - squeeze every word table into one takes_packed.md, the primary read surface.

All the content of a folder of footage becomes a few dozen KB of text, each line
carrying [start-end] and a speaker. Sampling 30,000 frames for a model is tens of
millions of tokens of noise; this file is small and carries word-boundary precision.

Usage:
    pack.py --edit-dir <footage>/edit
    pack.py --edit-dir edit --break-gap 0.5

Line breaking: a gap of >= break-gap between words, or a speaker change, starts a
new line. The gap itself is printed at the end of the line, because a gap is a cut
candidate - you pick cut points by reading this file, without going back to video.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def pack_one(data: dict, break_gap: float) -> tuple[str, dict]:
    words = data.get("words", [])
    stem = data.get("stem", "?")
    dur = data.get("duration", 0.0)
    if not words:
        return f"## {stem}  ({dur:.1f}s, no speech)\n", {"phrases": 0, "gaps": 0}

    phrases: list[list[dict]] = [[words[0]]]
    gaps: list[float] = []
    for prev, cur in zip(words, words[1:]):
        gap = float(cur["start"]) - float(prev["end"])
        if gap >= break_gap or cur.get("speaker") != prev.get("speaker"):
            if gap > 0:
                gaps.append(gap)
            phrases.append([cur])
        else:
            phrases[-1].append(cur)

    lines = [f"## {stem}  ({dur:.1f}s, {len(phrases)} lines, language {data.get('language','?')})"]
    for i, ph in enumerate(phrases):
        s, e = float(ph[0]["start"]), float(ph[-1]["end"])
        spk = ph[0].get("speaker", "S0")
        text = "".join(w["word"] if _cjk(w["word"]) else " " + w["word"] for w in ph).strip()
        tail = ""
        if i + 1 < len(phrases):
            nxt = float(phrases[i + 1][0]["start"])
            if nxt - e >= break_gap:
                tail = f"   ⟨gap {nxt - e:.2f}s⟩"
        lines.append(f"  [{s:07.2f}-{e:07.2f}] {spk} {text}{tail}")
    return "\n".join(lines) + "\n", {"phrases": len(phrases), "gaps": len(gaps)}


def _cjk(token: str) -> bool:
    """CJK text is not space separated; joining with spaces would corrupt it."""
    return any("一" <= c <= "鿿" or "　" <= c <= "〿" for c in token)


def main() -> None:
    ap = argparse.ArgumentParser(description="word tables -> takes_packed.md")
    ap.add_argument("--edit-dir", type=Path, required=True)
    ap.add_argument("--break-gap", type=float, default=0.5)
    a = ap.parse_args()

    tdir = a.edit_dir / "transcripts"
    files = sorted(tdir.glob("*.words.json"))
    if not files:
        raise SystemExit(f"no *.words.json in {tdir}; run transcribe.py first")

    blocks, stats = [], {}
    for f in files:
        block, st = pack_one(json.loads(f.read_text()), a.break_gap)
        blocks.append(block)
        stats[f.stem.replace(".words", "")] = st

    out = a.edit_dir / "takes_packed.md"
    header = (f"# takes_packed  ({len(files)} sources, break gap {a.break_gap}s)\n\n"
              "Each line is `[start-end] speaker text`; a trailing ⟨gap⟩ is a cut candidate.\n"
              "Cuts may only land on word boundaries, and need 30-200ms of padding to\n"
              "absorb ASR drift.\n\n")
    out.write_text(header + "\n".join(blocks))
    print(json.dumps({"packed": str(out), "size_kb": round(out.stat().st_size / 1024, 1),
                      "takes": stats}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
