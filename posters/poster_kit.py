# -*- coding: utf-8 -*-
"""poster_kit - the shared scaffolding for the nine skill posters.

Landscape 1600x900 (16:9), so one image drops into a social card, a README header or a
slide without being re-cropped. Every poster here is drawn by `code-print`'s own engines:
two inks, paper showing through from inside, one focus, one area of air.

Each poster file carries its own recipe in its docstring - subject, inks, division of
labour, layout family, focus, air - exactly as the skill demands of any other job.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINES = os.path.join(os.path.dirname(HERE), "code-print", "scripts")
sys.path.insert(0, ENGINES)

from woodcut import (coil, cut_shape, cut_stroke, d_of, ellipse, hatch_field,  # noqa: E402,F401
                     ink_line, limb, ribbon, smooth)
from printlab import defs, group, svg_document                                 # noqa: E402

W, H = 1600, 900

# Papers
WARM = "#F1EAD8"
COOL = "#EAEAE6"
WHITE = "#FAFAF7"

# Inks
INK = "#15151A"
INDIGO = "#1B3FA0"
CINNABAR = "#C1352C"
PINE = "#0A7A50"
OCHRE = "#B45A33"
VIOLET = "#5E3C6B"
BLUE = "#3F6FA8"
SLATE = "#2A3B4C"

# Type stacks. System fonts only: for a print piece the export is the piece, and a
# webfont that fails to load silently changes the work.
CJK_SONG = "Songti SC, STSong, Noto Serif CJK SC, serif"
CJK_HEI = "PingFang SC, Heiti SC, Noto Sans CJK SC, sans-serif"
LATIN = "Helvetica Neue, Arial, sans-serif"
MONO = "Menlo, DejaVu Sans Mono, monospace"


def text(x, y, s, size, fill=INK, family=LATIN, track=0, anchor="start", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'letter-spacing="{track}" font-family="{family}" '
            f'text-anchor="{anchor}"{w}>{s}</text>')


def rule(x0, y0, x1, y1, w0=4.0, w1=2.6, seed=7, fill=INK):
    """A drawn rule, not a rectangle: it has a hand, and it costs nothing."""
    return f'<path d="{cut_stroke([(x0, y0), (x1, y1)], w0, w1, seed=seed, wobble=1.1)}" fill="{fill}"/>'


def blob(points, seed=3, wobble=2.6, fill=INK, smooth_n=16):
    return f'<path d="{cut_shape(smooth(points, smooth_n), seed=seed, wobble=wobble)}" fill="{fill}"/>'


def disc(cx, cy, rx, ry=None, fill=INK, seed=5, wobble=2.0):
    ry = rx if ry is None else ry
    return f'<path d="{cut_shape(ellipse(cx, cy, rx, ry), seed=seed, wobble=wobble)}" fill="{fill}"/>'


def hatched(shape_d, clip_id, angle=58, spacing=18.0, seed=5, w=3.4, keep=(0.08, 0.55),
            fill=None, paper=WARM):
    """A clipped family of parallel cuts. `hatch_field` does not clip itself."""
    fill = paper if fill is None else fill
    cuts = "".join(f'<path d="{d}" fill="{fill}"/>'
                   for d in hatch_field(shape_d, angle, spacing, seed=seed, w=w, keep=keep))
    return f'<g clip-path="url(#{clip_id})">{cuts}</g>'


def footer(name, tagline, fill=INK, paper_side="left"):
    """Every poster carries the same two lines, small, on the paper margin."""
    x = 64 if paper_side == "left" else W - 64
    anchor = "start" if paper_side == "left" else "end"
    return (text(x, H - 58, name.upper(), 15, fill, MONO, track=5.0, anchor=anchor)
            + text(x, H - 34, tagline, 15, fill, LATIN, track=2.6, anchor=anchor))


def write(path_stem, paper, inner, extra_defs="", seed=6, grain=0.12):
    out = os.path.join(HERE, f"{path_stem}.svg")
    svg = svg_document(path_stem, W, H, paper, inner, defs(seed=seed, grain=grain) + extra_defs)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"{os.path.basename(out)}  {len(svg) / 1024:.0f} KB")
    return out
