# -*- coding: utf-8 -*-
"""Poster: unknown-first.

RECIPE
  subject:  one known/unknown map - which is the artefact the skill actually produces
  intent:   observe
  text:     UNKNOWN FIRST (locked)
  inks:     ink #15151A + coral #D97757; paper pale #FAF9F5
  division: ink = the axes, the solid run and the type; coral = the dashed reach and the
            one mark that is worth going to
  layout:   specimen - one instrument floating on the sheet, large air around it
  focus:    the coral × out past the end of what was reached
  air:      the lower left quadrant
  paper:    ~60%
  texture:  paper grain only - an instrument is not an aged object

WHY
  The skill's own map spec is: three nodes maximum, no bullets, and the only complete
  sentence on the picture belongs to the mark you did not reach. This poster obeys its
  own spec, which is the cheapest honest test of whether the spec is any good.
"""
from poster_kit import (H, INK, LATIN, MONO, W, cut_stroke, disc, footer, rule,  # noqa: F401
                        smooth, text, write)

PAPER = "#FAF9F5"
CORAL = "#D97757"
GREY = "#C9C4B8"
OX, OY = 300, 800          # origin
EX, EY = 1500, 300         # frame extent


def build():
    axes = (f'<path d="{cut_stroke([(OX, OY), (EX, OY)], 3.0, 2.4, seed=3, wobble=0.7)}" fill="{INK}"/>'
            f'<path d="{cut_stroke([(OX, OY), (OX, EY)], 3.0, 2.4, seed=4, wobble=0.7)}" fill="{INK}"/>')
    grid = "".join(f'<line x1="{OX}" y1="{y}" x2="{EX}" y2="{y}" stroke="{GREY}" stroke-width="1"/>'
                   for y in range(380, OY, 70))

    # the reference line: through the origin, present for comparison, barely labelled
    ref = (f'<line x1="{OX}" y1="{OY}" x2="{EX}" y2="{OY - 330}" stroke="{GREY}" stroke-width="3"/>'
           + text(1400, 512, "generic", 17, GREY, MONO, track=1.4))

    # what was reached: solid, with three nodes and no more
    run = [(OX, OY - 120), (640, OY - 214), (980, OY - 326), (1210, OY - 392)]
    solid = f'<path d="{cut_stroke(run, 7.5, 5.5, seed=6, wobble=1.1)}" fill="{INK}"/>'
    nodes = "".join(disc(x, y, 11, 11, fill=INK, seed=9 + i, wobble=1.4)
                    for i, (x, y) in enumerate(run[1:], 1))
    # labels sit clear of the line, not on it
    labels = (text(640, OY - 252, "the material", 19, INK, MONO, track=1.2, anchor="middle")
              + text(980, OY - 364, "the layer under it", 19, INK, MONO, track=1.2, anchor="middle")
              + text(1180, OY - 430, "what it costs", 19, INK, MONO, track=1.2, anchor="end"))

    # the unknown: dashed, and the one place worth going, marked
    dashed = (f'<line x1="1210" y1="{OY - 392}" x2="1444" y2="{OY - 486}" stroke="{CORAL}" '
              f'stroke-width="4" stroke-dasharray="16 13"/>')
    cross = (f'<path d="{cut_stroke([(1424, OY - 512), (1474, OY - 464)], 6, 5, seed=12, wobble=1.0)}" fill="{CORAL}"/>'
             f'<path d="{cut_stroke([(1474, OY - 512), (1424, OY - 464)], 6, 5, seed=13, wobble=1.0)}" fill="{CORAL}"/>')
    # the only complete sentence on the picture belongs to the mark
    sentence = text(1500, OY - 536, "nobody has opened the second archive yet",
                    23, CORAL, LATIN, track=0.6, anchor="end")

    inner = (grid + ref + axes + solid + nodes + labels + dashed + cross + sentence
             + text(88, 172, "UNKNOWN FIRST", 108, INK, LATIN, track=-1.4, weight="700")
             + rule(88, 210, 1512, 206, 3.4, 2.2, seed=5)
             + text(88, 254, "fill the person's known with the unknown; the reverse is agreement",
                    27, INK, LATIN, track=1.0)
             # the quiet quadrant: under the run, right of the axis
             + text(700, 704, "the map is only a map.", 23, INK, LATIN, track=0.8)
             + text(700, 740, "the coordinate reached is what matters.", 23, INK, LATIN, track=0.8)
             + footer("unknown-first", "one obligation · one map · two archives"))
    write("unknown-first", PAPER, inner, grain=0.07)


if __name__ == "__main__":
    build()
