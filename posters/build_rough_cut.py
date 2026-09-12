# -*- coding: utf-8 -*-
"""Poster: rough-cut.

RECIPE
  subject:  one waveform, and the silence inside it
  intent:   announce
  text:     ROUGH CUT (locked)
  inks:     ink #15151A + blue #3F6FA8; paper warm white #F1EAD8
  division: ink = the waveform and the type; blue = the gap, and nothing else
  layout:   image-dominant, the wave crossing both side edges
  focus:    one abnormal scale relation - the silence is wider than any sound around it
  air:      the upper band above the wave; the title sits in it alone
  paper:    ~55%
  texture:  paper grain + misregistration on the type

WHY
  The whole skill is one claim: the cut is in the audio, not the picture, and it lives in
  the gaps. So the poster draws a waveform and gives the second ink exactly one job - to
  be the gap. Nothing else on the sheet is blue.
"""
import math
import random

from poster_kit import (BLUE, CJK_HEI, H, INK, LATIN, MONO, W, WARM, cut_shape,  # noqa: F401
                        cut_stroke, d_of, footer, rule, text, write)

MID = 560
GAP0, GAP1 = 760, 1010          # the silence: wide, and the only blue on the sheet


def envelope_bars():
    """Mirrored RMS bars. Amplitude from correlated noise, not random heights - random
    heights read as a barcode, not as a voice."""
    rng = random.Random(11)
    out = []
    x = 40
    while x < W - 40:
        if GAP0 < x < GAP1:            # inside the silence: near-zero, still drawn
            h = rng.uniform(1.5, 4.0)
        else:
            base = 0.42 + 0.38 * math.sin(x / 190.0) + 0.22 * math.sin(x / 47.0 + 1.3)
            h = max(4.0, base * 150 * rng.uniform(0.55, 1.25))
        out.append(f'<rect x="{x:.1f}" y="{MID - h:.1f}" width="6" height="{2 * h:.1f}" '
                   f'rx="1" fill="{INK}"/>')
        x += 11
    return "".join(out)


def build():
    # the gap, as a standing block of the second ink - the one place it appears
    gap = (f'<path d="{cut_shape([(GAP0, 300), (GAP1, 296), (GAP1 + 4, 828), (GAP0 - 4, 832)], seed=4, wobble=3.2)}" '
           f'fill="{BLUE}"/>')
    # the two edges of the silence, drawn: this is where a cut may land
    edges = (f'<path d="{cut_stroke([(GAP0, 300), (GAP0, 828)], 5.0, 3.0, seed=6, wobble=1.4)}" fill="{INK}"/>'
             f'<path d="{cut_stroke([(GAP1, 296), (GAP1, 824)], 5.0, 3.0, seed=9, wobble=1.4)}" fill="{INK}"/>')

    words = "".join(
        text(x, 808, w, 19, INK, MONO, track=1.2, anchor="middle")
        for x, w in [(300, "so"), (430, "then"), (560, "we"), (670, "cut"),
                     (885, "[ 1.04s ]"), (1180, "here"), (1330, "not"), (1470, "there")])

    inner = (gap
             + f'<g>{envelope_bars()}</g>'
             + edges
             + text(70, 190, "ROUGH CUT", 132, INK, LATIN, track=-2.0, weight="700")
             + rule(70, 226, 1530, 222, 3.4, 2.2, seed=7)
             + text(70, 268, "read the transcript, not the frames", 27, INK, LATIN, track=1.4)
             + words
             + footer("rough-cut", "unscripted footage → EDL → cut"))
    write("rough-cut", WARM, inner)


if __name__ == "__main__":
    build()
