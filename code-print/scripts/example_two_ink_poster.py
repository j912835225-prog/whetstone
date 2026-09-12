# -*- coding: utf-8 -*-
"""Example: a two-ink poster, image-dominant family. Copy this skeleton, replace the subject.

Run:  python3 example_two_ink_poster.py   ->  example_two_ink_poster.svg
      (optional) rsvg-convert -z 2 example_two_ink_poster.svg -o out.png

The recipe lives in this docstring, not in a separate file, so it stays in front of you
while you change parameters and re-run.

RECIPE
  subject:    one bird, cropped by two edges
  intent:     announce
  text:       "夜 航" (locked) + two lines of 10px latin (locked)
  format:     poster, A5 portrait 559x794
  inks:       ink #15151A + blue #3F6FA8; paper warm white #F1EAD8
  division:   blue = the sky, one full-bleed plate and nothing else;
              ink = the bird, the rule, the small type
  layout:     image-dominant - the body crosses the left and bottom edges
  focus:      one abnormal scale relation: the head is larger than the title block
  air:        the upper right of the sky - nothing in it at all; the two lines of
              small type sit on the paper margin at the foot
  paper:      ~30% (head, eye, the breast highlight and the display type are all paper showing through)
  texture:    paper grain + misregistration, two items

WHY IT IS BUILT THIS WAY
  - Geometry first, filters second: the taper and the nicks are cut into the points;
    the SVG filter only adds high-frequency chatter. A filter cannot make a taper.
  - The second ink gets one job (the sky) and never appears anywhere else. An accent
    ink sprinkled evenly across a page is decoration, not a plate.
  - Paper is a shape inside the image, not the margin around it: the highlights are
    holes cut in the ink plate.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from woodcut import (cut_shape, cut_stroke, d_of, ellipse, hatch_field,  # noqa: E402
                     limb, smooth)
from printlab import defs, group, svg_document                                   # noqa: E402

W, H = 559, 794
INK = "#15151A"
BLUE = "#3F6FA8"
PAPER = "#F1EAD8"


def bird_body():
    """The body, crossing the left and bottom edges.

    Place the joints first and grow flesh after - an outline guessed directly is the
    single most common way this kind of drawing goes soft.
    """
    ctrl = [(-40, 520), (60, 430), (200, 400), (330, 450), (405, 560),
            (415, 690), (360, 820), (180, 850), (20, 800), (-50, 660)]
    return cut_shape(smooth(ctrl, 18), seed=4, wobble=2.6)


def neck():
    """Head and body must read as one animal; a tapering limb does that, two blobs do not.

    `limb` returns (d, spine_points) - taking the tuple straight into an f-string paints
    nothing and raises nothing. Same trap as `ribbon`, which returns points, not a `d`.
    """
    return limb((300, 430), (372, 300), 78, 54, seed=6, bow=16.0, wobble=2.0)[0]


def bird_head():
    """The focus: bigger than the display type, sitting alone in the air."""
    ctrl = [(318, 250), (386, 214), (452, 240), (474, 300), (444, 356),
            (372, 372), (318, 336), (302, 290)]
    return cut_shape(smooth(ctrl, 16), seed=9, wobble=2.2)


def beak():
    """Geometry makes the taper; the filter only adds chatter on top of it."""
    return cut_stroke([(468, 288), (528, 272), (556, 264)], 30, 3, seed=3, wobble=1.5)


def build() -> str:
    body_d = bird_body()
    head_d = bird_head()

    # --- blue plate: the sky, one shape, nothing else -------------------------
    # The sky stops short of the trim on three sides: the paper edge is part of the image.
    sky = f'<path d="{cut_shape(smooth([(34, 168), (W - 34, 160), (W - 28, H - 150), (30, H - 158)], 10), seed=2, wobble=3.0)}" fill="{BLUE}"/>'

    # --- ink plate -----------------------------------------------------------
    ink_parts = [
        f'<path d="{body_d}" fill="{INK}"/>',
        f'<path d="{neck()}" fill="{INK}"/>',
        f'<path d="{head_d}" fill="{INK}"/>',
        f'<path d="{beak()}" fill="{INK}"/>',
        # Feather cuts: parallel families build volume, scattered lines build mud.
        # Cut in paper colour, so the light comes from the paper, not from a third ink.
        # Two things to know: `hatch_field` returns a LIST of `d` strings, one per cut,
        # and it does NOT clip itself - unclipped, the cuts run straight across the sky.
        # Clip them to the shape they belong to.
        f'<g clip-path="url(#bodyclip)">'
        + "".join(f'<path d="{d}" fill="{PAPER}"/>'
                  for d in hatch_field(body_d, 58, 19.0, seed=5, w=3.6, keep=(0.10, 0.52)))
        + '</g>',
        # the rule that splits the page, drawn as a cut stroke so it has a hand
        f'<path d="{cut_stroke([(52, 150), (507, 146)], 3.4, 2.2, seed=7, wobble=1.1)}" fill="{INK}"/>',
    ]

    # --- paper showing through from inside the image --------------------------
    paper_parts = [
        # the eye: a hole, not a dot of a third ink
        f'<path d="{d_of(ellipse(410, 288, 14, 12))}" fill="{PAPER}"/>',
    ]
    ink_parts += paper_parts

    # --- type: system CJK stack, so screen and export agree -------------------
    type_parts = [
        f'<text x="52" y="122" fill="{INK}" font-size="104" letter-spacing="-6" '
        f'font-family="Songti SC, STSong, Noto Serif CJK SC, serif">夜 航</text>',
        f'<text x="352" y="762" fill="{INK}" font-size="10" letter-spacing="2.4" '
        f'font-family="Helvetica Neue, Arial, sans-serif">NIGHT PASSAGE</text>',
        f'<text x="352" y="776" fill="{INK}" font-size="10" letter-spacing="2.4" '
        f'font-family="Helvetica Neue, Arial, sans-serif">ONE PLATE, ONE BIRD</text>',
    ]

    inner = (sky
             + group("".join(ink_parts))
             # misregistration lives here: 1-4px on one group, never more
             + group("".join(type_parts), dx=1.5, dy=-1.0))
    extra_defs = f'<clipPath id="bodyclip"><path d="{body_d}"/></clipPath>'
    return svg_document("example_two_ink_poster", W, H, PAPER, inner,
                        defs(seed=6, grain=0.12) + extra_defs)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "example_two_ink_poster.svg")
    svg = build()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"{out}  ({len(svg) / 1024:.1f} KB)")
    print("render:  rsvg-convert -z 2 example_two_ink_poster.svg -o out.png")
