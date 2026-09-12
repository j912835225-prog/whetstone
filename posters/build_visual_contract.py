# -*- coding: utf-8 -*-
"""Poster: visual-contract.

RECIPE
  subject:  one reference image, split into the half you may take and the half you may not
  intent:   notify
  text:     VISUAL CONTRACT (locked)
  inks:     ink #15151A + violet #5E3C6B; paper neutral white #FAFAF7
  division: ink = the structure you may borrow, and the type; violet = the skin you may not
  layout:   overprint - two plates carrying the same rectangle, crossing once
  focus:    the extreme crop where structure and skin meet mid-page
  air:      the band under the title
  paper:    ~45%
  texture:  paper grain + misregistration

WHY
  The whole skill is one sentence: a reference lends you structure, never taste. So the
  poster is one frame drawn twice - wireframe on the left, decorated skin on the right,
  meeting on a hard edge with no blend.
"""
from poster_kit import (H, INK, LATIN, MONO, VIOLET, W, WHITE, cut_shape, cut_stroke,  # noqa: F401
                        footer, rule, text, write)

TOP, BOT = 330, 800
SPLIT = 800


def wire():
    """Structure: grouping, hierarchy, flow. Drawn in ink, and this half is yours."""
    out = [f'<path d="{cut_stroke([(120, TOP), (SPLIT, TOP)], 4, 3, seed=3, wobble=1.2)}" fill="{INK}"/>',
           f'<path d="{cut_stroke([(120, BOT), (SPLIT, BOT)], 4, 3, seed=4, wobble=1.2)}" fill="{INK}"/>',
           f'<path d="{cut_stroke([(120, TOP), (120, BOT)], 4, 3, seed=5, wobble=1.2)}" fill="{INK}"/>']
    boxes = [(160, 372, 420, 96), (160, 500, 260, 150), (452, 500, 288, 150),
             (160, 686, 580, 66)]
    for i, (x, y, w, h) in enumerate(boxes):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                   f'stroke="{INK}" stroke-width="3" stroke-dasharray="12 9"/>')
        out.append(text(x + 10, y + 26, f"{i + 1}", 17, INK, MONO, track=2))
    return "".join(out)


def skin():
    """Taste: palette, radius, shadow, gradient. Drawn in the second ink, and this half
    is not yours - the poster shows it flattened to one plate, which is what borrowing it
    actually does to your work."""
    out = [f'<rect x="{SPLIT}" y="{TOP}" width="{W - SPLIT - 120}" height="{BOT - TOP}" fill="{VIOLET}"/>']
    cards = [(SPLIT + 60, 372, 420, 96), (SPLIT + 60, 500, 260, 150),
             (SPLIT + 352, 500, 288, 150), (SPLIT + 60, 686, 580, 66)]
    for x, y, w, h in cards:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="{WHITE}" opacity="0.93"/>')
    return "".join(out)


def build():
    inner = (skin() + wire()
             + f'<path d="{cut_stroke([(SPLIT, TOP - 26), (SPLIT, BOT + 26)], 7, 5, seed=8, wobble=1.6)}" fill="{INK}"/>'
             + text(120, 176, "VISUAL CONTRACT", 112, INK, LATIN, track=-1.4, weight="700")
             + rule(120, 214, 1480, 210, 3.6, 2.4, seed=5)
             + text(120, 258, "a reference lends you structure, never taste", 27, INK, LATIN, track=1.2)
             + text(120, 296, "BORROW", 19, INK, MONO, track=4.0)
             + text(SPLIT + 60, 296, "DO NOT BORROW", 19, VIOLET, MONO, track=4.0)
             + footer("visual-contract", "state it before you design, or the screenshot decides"))
    write("visual-contract", WHITE, inner)


if __name__ == "__main__":
    build()
