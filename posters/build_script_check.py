# -*- coding: utf-8 -*-
"""Poster: script-check.

RECIPE
  subject:  一个人，一件事，其余都是陪衬
  intent:   announce
  text:     SCRIPT CHECK (locked)
  inks:     ink #15151A + indigo #1B3FA0; paper cool grey #EAEAE6
  division: ink = the figure and the type; indigo = the one thing (a shaft of light), nowhere else
  layout:   image-dominant - the figure stands in the light, the light crosses the bottom edge
  focus:    one enormous object: the shaft, wider than a third of the sheet
  air:      the grey to the right
  paper:    ~45%
  texture:  paper grain + misregistration

WHY
  "A scene is written for one person and one thing." So exactly one figure stands here and
  exactly one light falls. Every support element is cut - the poster has to pass its own rule.
"""
from poster_kit import (CJK_SONG, H, INDIGO, INK, LATIN, MONO, W, COOL,  # noqa: F401
                        blob, cut_shape, cut_stroke, disc, footer, limb, rule, smooth,
                        text, write)


def spotlight():
    """一束光：窄口在上，敞口跨出下边。"""
    return (f'<path d="{cut_shape([(470, 300), (610, 300), (860, 900), (250, 900)], seed=4, wobble=3.6)}" '
            f'fill="{INDIGO}" opacity="0.90"/>')


def figure():
    """一个人：头一个圆，身体一个锥，手臂两条。不画手指——手是一个拳。"""
    head = disc(540, 452, 42, 48, fill=INK, seed=7, wobble=1.8)
    torso = blob([(540, 506), (600, 560), (612, 720), (582, 836), (498, 836), (468, 720), (480, 560)],
                 seed=9, wobble=2.2, fill=INK)
    arm_l = f'<path d="{limb((500, 556), (438, 690), 26, 16, seed=3, bow=12.0)[0]}" fill="{INK}"/>'
    arm_r = f'<path d="{limb((582, 556), (648, 676), 26, 16, seed=4, bow=-14.0)[0]}" fill="{INK}"/>'
    fist = disc(650, 682, 17, 15, fill=INK, seed=6, wobble=1.6)
    return head + torso + arm_l + arm_r + fist


def build():
    rows = [("ONE", "person, one thing"), ("PLANTED", "must be paid off"),
            ("A SUBPLOT", "serves the spine, or goes"),
            ("FINISHED?", "ask how it gets played")]
    right, y = [], 392
    for a, b in rows:
        right.append(text(980, y, a, 34, INK, MONO, track=2.4))
        right.append(text(1206, y, b, 34, INK, LATIN, track=0.4))
        right.append(f'<path d="{cut_stroke([(980, y + 22), (1512, y + 20)], 2.4, 1.6, seed=int(y), wobble=0.9)}" fill="{INK}" opacity="0.35"/>')
        y += 104

    inner = (spotlight() + figure() + "".join(right)
             + text(88, 176, "SCRIPT CHECK", 96, INK, LATIN, track=-1.2, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 258, "a scene is written for one person and one thing; everything else is support", 27, INK, LATIN, track=1.0)
             + footer("script-check", "structure · planting · eight dialogue checks · three closes"))
    write("script-check", COOL, inner)


if __name__ == "__main__":
    build()
