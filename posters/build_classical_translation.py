# -*- coding: utf-8 -*-
"""Poster: classical-chinese-translation.

RECIPE
  subject:  a hundred chapter spines, and the gap where 78 should be
  intent:   notify
  text:     CLASSICAL TRANSLATION (locked)
  inks:     ink #15151A + ochre #B45A33; paper warm white #F1EAD8
  division: ink = one hundred spines and the type; ochre = the missing chapter, and only that
  layout:   object field - one element repeated a hundred times, varying in height
  focus:    one abnormality: in a hundred even spines, the seventy-eighth is empty
  air:      the band under the title
  paper:    ~50%
  texture:  paper grain

WHY
  The skill is not about how to translate. It is about the fact that by chapter 78 the rule
  set on day one has quietly stopped applying. A gap raises no error - it just clears a
  space. So the poster draws a hundred, and leaves that one empty.
"""
import math
import random

from poster_kit import (CJK_SONG, H, INK, LATIN, MONO, OCHRE, W, WARM,  # noqa: F401
                        cut_stroke, footer, rule, text, write)

MISSING = 78


def spines():
    rng = random.Random(3)
    out = []
    x0, gap = 92, 14.4
    for i in range(1, 101):
        x = x0 + (i - 1) * gap
        h = 200 + 150 * abs(math.sin(i / 9.0)) + rng.uniform(-24, 24)
        y = 810 - h
        if i == MISSING:
            # the gap: drawn in the second ink, at full height, so the absence is loud
            out.append(f'<path d="{cut_stroke([(x + 4, 330), (x + 4, 812)], 9, 7, seed=11, wobble=1.8)}" fill="{OCHRE}"/>')
            out.append(text(x + 4, 314, "78", 21, OCHRE, MONO, track=1.0, anchor="middle"))
            continue
        out.append(f'<rect x="{x:.1f}" y="{y:.0f}" width="9" height="{h:.0f}" fill="{INK}" '
                   f'opacity="{rng.uniform(0.72, 0.95):.2f}"/>')
    return "".join(out)


def build():
    inner = (spines()
             + text(88, 176, "CLASSICAL TRANSLATION", 88, INK, LATIN, track=-1.0, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 258, "the failure is never that you cannot translate it - it is that by chapter 78",
                    27, INK, LATIN, track=1.0)
             + text(88, 292, "the rule you set on day one has quietly stopped applying",
                    27, INK, LATIN, track=1.0)
             + text(1512, 866, "a gap raises no error. it just clears a space, and memory fills it.",
                    22, OCHRE, LATIN, track=0.6, anchor="end")
             + footer("classical-chinese-translation", "source discipline · cross-check every title · four drift traps"))
    write("classical-chinese-translation", WARM, inner)


if __name__ == "__main__":
    build()
