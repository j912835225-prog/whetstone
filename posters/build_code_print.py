# -*- coding: utf-8 -*-
"""Poster: code-print.

RECIPE
  subject:  two plates of the same form, one printed slightly off the other
  intent:   announce
  text:     CODE PRINT (locked)
  inks:     ink #15151A + cinnabar #C1352C; paper warm white #F1EAD8
  division: cinnabar = the under-plate, offset; ink = the over-plate and the type
  layout:   overprint - the two plates carry the same shape and cross once
  focus:    one extreme crop - the form runs off the right edge at full height
  air:      the lower left, where the small type sits alone
  paper:    ~45%
  texture:  paper grain + misregistration (this poster is a demonstration of it)

WHY
  The whole tool is about what a plate can do that a prompt cannot: exact type, exact
  size, the same file every time, and misregistration used on purpose. So the poster is
  literally two plates, three pixels apart, with paper cut out from inside the form.
"""
from poster_kit import (CINNABAR, H, INK, LATIN, MONO, W, WARM, cut_shape, cut_stroke,  # noqa: F401
                        d_of, disc, ellipse, footer, group, hatch_field, hatched, rule,
                        smooth, text, write)

FORM = [(700, 250), (1120, 230), (1420, 380), (1560, 640), (1400, 860),
        (1000, 900), (760, 780), (660, 520)]


def build():
    shape = cut_shape(smooth(FORM, 18), seed=4, wobble=2.8)
    under = f'<path d="{shape}" fill="{CINNABAR}"/>'
    over = f'<path d="{shape}" fill="{INK}"/>'
    # paper cut out from inside the form - the line between "printed" and "filled in"
    hole = (f'<path d="{cut_shape(smooth([(960, 470), (1120, 430), (1210, 540), (1120, 660), (960, 630)], 14), seed=8)}" '
            f'fill="{WARM}"/>')
    cuts = hatched(shape, "formclip", angle=64, spacing=21.0, seed=5, w=4.0,
                   keep=(0.04, 0.42), paper=WARM)

    inner = (group(under, dx=-13, dy=9)
             + group(over + hole + cuts)
             + text(88, 190, "CODE PRINT", 132, INK, LATIN, track=-2.2, weight="700")
             + rule(88, 228, 1512, 224, 3.6, 2.4, seed=5)
             + text(88, 272, "printed matter drawn in code", 30, INK, LATIN, track=1.4)
             + text(88, 430, "vector out", 25, INK, MONO, track=1.6)
             + text(88, 486, "PDF-ready", 25, INK, MONO, track=1.6)
             + text(88, 542, "type never wrong", 25, INK, MONO, track=1.6)
             + text(88, 598, "same input, same file", 25, INK, MONO, track=1.6)
             + text(88, 682, "two plates. 3px apart.", 21, CINNABAR, MONO, track=1.2)
             + text(88, 714, "on purpose.", 21, CINNABAR, MONO, track=1.2)
             + footer("code-print", "one sheet · two plates · one focus · one area of air"))
    write("code-print", WARM, inner,
          extra_defs=f'<clipPath id="formclip"><path d="{shape}"/></clipPath>')


if __name__ == "__main__":
    build()
