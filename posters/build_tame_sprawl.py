# -*- coding: utf-8 -*-
"""Poster: tame-sprawl.

RECIPE
  subject:  forty scattered pieces, and the one line they all hang from
  intent:   observe
  text:     TAME SPRAWL (locked)
  inks:     ink #15151A + pine #0A7A50; paper cool grey #EAEAE6
  division: ink = the scattered pieces and the type; pine = the single line, nothing else
  layout:   object field - one element repeated at different sizes and angles
  focus:    the one green line running through a page of grey debris
  air:      the upper left, where the title sits alone
  paper:    ~55%
  texture:  paper grain only

WHY
  The failure mode the skill names is "47 files down to 12" - a count, not order. So the
  poster does not show fewer pieces after the tidy. It shows the same pieces, with one
  line through them: the generating principle, which is the only thing that changed.
"""
import math
import random

from poster_kit import (H, INK, LATIN, MONO, PINE, W, COOL, cut_shape, cut_stroke,  # noqa: F401
                        disc, footer, rule, smooth, text, write)


def debris():
    rng = random.Random(5)
    out = []
    for i in range(42):
        x = rng.uniform(110, 1520)
        y = rng.uniform(340, 790)
        w = rng.uniform(16, 74)
        h = rng.uniform(12, 30)
        a = rng.uniform(-28, 28)
        out.append(f'<g transform="rotate({a:.1f} {x:.0f} {y:.0f})">'
                   f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" '
                   f'fill="{INK}" opacity="{rng.uniform(0.55, 0.92):.2f}"/></g>')
    return "".join(out)


def build():
    # the principle: one line, drawn once, touching everything without moving anything
    spine = [(90, 700), (420, 604), (760, 556), (1130, 498), (1520, 424)]
    line = f'<path d="{cut_stroke(spine, 11, 7, seed=6, wobble=1.8)}" fill="{PINE}"/>'
    nodes = "".join(disc(x, y, 15, 15, fill=PINE, seed=10 + i, wobble=2.0)
                    for i, (x, y) in enumerate(spine[1:-1], 1))

    inner = (debris() + line + nodes
             + text(90, 176, "TAME SPRAWL", 118, INK, LATIN, track=-1.6, weight="700")
             + rule(90, 214, 1510, 210, 3.6, 2.4, seed=5)
             + text(90, 258, "traverse · fuse · cut · raise the principle, then get out of the way",
                    27, INK, LATIN, track=1.2)
             + text(1510, 300, "not: 47 files down to 12", 19, INK, MONO, track=1.6, anchor="end")
             + footer("tame-sprawl", "report contradictions resolved, never a file count"))
    write("tame-sprawl", COOL, inner)


if __name__ == "__main__":
    build()
