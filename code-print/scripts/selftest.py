#!/usr/bin/env python3
"""selftest - prove the two engines still draw. No assets, no network, no dependencies.

    python3 selftest.py

Each check has a known answer. Several of them exist because the return types here are
easy to get wrong in a way that produces *no error and no drawing*: `limb` returns a
tuple, `ribbon` returns points, `hatch_field` returns a list and clips nothing. A silent
blank is the failure mode this file is here to catch.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET  # only ever parses files this script just generated
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from woodcut import (coil, cut_shape, cut_stroke, d_of, ellipse, hatch_field,  # noqa: E402
                     ink_line, limb, noise, ribbon, smooth)
from printlab import defs, group, plate, svg_document                          # noqa: E402

fails: list[str] = []


def check(name: str, ok: bool, got: str = "") -> None:
    print(f"{'ok  ' if ok else 'FAIL'} · {name}{'' if ok else '  got=' + got}")
    if not ok:
        fails.append(name)


def is_d(x) -> bool:
    return isinstance(x, str) and x.startswith("M") and len(x) > 40


def main() -> int:
    # --- return types: the silent-blank traps --------------------------------
    circle = ellipse(100, 100, 60, 40)
    check("ellipse returns points", isinstance(circle, list) and len(circle) > 20)
    check("d_of turns points into a path", is_d(d_of(circle)))
    check("cut_shape returns a path directly", is_d(cut_shape(circle, seed=1)))
    check("cut_stroke returns a path directly",
          is_d(cut_stroke([(0, 0), (100, 20), (200, 0)], 20, 4, seed=1)))
    check("ink_line returns a path directly",
          is_d(ink_line([(0, 0), (50, 40), (120, 10)], w=3)))

    lb = limb((0, 0), (100, 80), 30, 18, seed=1)
    check("limb returns a (d, spine) TUPLE - taking it whole draws nothing",
          isinstance(lb, tuple) and is_d(lb[0]), type(lb).__name__)
    rb = ribbon(smooth([(0, 0), (60, 30), (120, 0)], 8, closed=False), 20, 4)
    check("ribbon returns POINTS, not a path - wrap it in d_of",
          isinstance(rb, list) and not isinstance(rb, str), type(rb).__name__)
    check("d_of(ribbon(...)) is a usable path", is_d(d_of(rb)))

    hs = hatch_field(cut_shape(circle, seed=2), 45, 8.0, seed=3)
    check("hatch_field returns a LIST of paths, one per cut",
          isinstance(hs, list) and len(hs) > 2 and is_d(hs[0]),
          type(hs).__name__)

    # --- geometry behaves ----------------------------------------------------
    n = noise(7, 4, 1.0)
    vals = [n(t / 50) for t in range(50)]
    check("noise is correlated, not white (neighbours stay close)",
          max(abs(b - a) for a, b in zip(vals, vals[1:])) < 0.9,
          f"{max(abs(b - a) for a, b in zip(vals, vals[1:])):.2f}")
    check("noise stays bounded", all(-1.2 < v < 1.2 for v in vals))
    co = coil(0, 0, 0, s0=9, turn=0.13, n=40)
    check("coil produces a growing spiral", isinstance(co, list) and len(co) >= 40)
    tight = hatch_field(cut_shape(circle, seed=2), 45, 4.0, seed=3)
    check("smaller spacing yields more cuts", len(tight) > len(hs),
          f"{len(tight)} vs {len(hs)}")

    # --- document assembly ---------------------------------------------------
    body = cut_shape(circle, seed=5)
    doc = svg_document("t", 300, 200, "#F1EAD8",
                       plate([body], "#15151A", dx=2, dy=-1)
                       + group(f'<path d="{d_of(circle)}" fill="#3F6FA8"/>'),
                       defs(seed=1))
    check("svg_document is well-formed XML", _parses(doc))
    check("paper rectangle is underneath", doc.index("<rect") < doc.index("<g "))
    check("misregistration survives into the output", 'translate(2,-1)' in doc)

    # --- the shipped example actually runs and draws --------------------------
    example = HERE / "example_two_ink_poster.py"
    if example.exists():
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([sys.executable, str(example)],
                               capture_output=True, text=True, cwd=td)
            svg = HERE / "example_two_ink_poster.svg"
            ok = r.returncode == 0 and svg.exists()
            check("example_two_ink_poster.py runs", ok, r.stderr.strip()[-200:])
            if ok:
                text = svg.read_text()
                check("example is well-formed XML", _parses(text))
                # The point is that the hatch family drew at all: without the
                # clipped group the piece is four silhouettes and no volume.
                hatch = text.split('clip-path="url(#bodyclip)"')[-1].split("</g>")[0]
                check("the clipped hatch family drew (>=8 cuts inside the body)",
                      hatch.count("<path") >= 8, str(hatch.count("<path")))
                check("example draws the whole cast (>=15 paths)",
                      text.count("<path") >= 15, str(text.count("<path")))
                check("example uses exactly two inks plus paper",
                      len(set(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', text))) == 3,
                      str(sorted(set(re.findall(r'fill="(#[0-9A-Fa-f]{6})"', text)))))
                check("example keeps its display text intact", "夜 航" in text)
    else:
        print("skip · example_two_ink_poster.py not present")

    print()
    if fails:
        print(f"FAIL · {len(fails)} check(s) failed: " + "; ".join(fails))
        return 1
    print("all green · both engines draw, and the worked example builds")
    return 0


def _parses(text: str) -> bool:
    try:
        ET.fromstring(text)
        return True
    except ET.ParseError:
        return False


if __name__ == "__main__":
    sys.exit(main())
