# -*- coding: utf-8 -*-
"""Poster: audit-anything.

RECIPE
  subject:  a column of findings, and the one that has a touchpoint under it
  intent:   notify
  text:     AUDIT ANYTHING (locked)
  inks:     ink #15151A + cinnabar #C1352C; paper cool grey #EAEAE6
  division: ink = the rows and the type; cinnabar = one verdict mark, nothing else
  layout:   notice - one rule across the page, title above, evidence below
  focus:    one concentrated collision: the single red mark against a page of grey rows
  air:      the right third below the rule
  paper:    ~50%
  texture:  paper grain + misregistration

WHY
  The skill's core line is that a finding without "what for, what it caused, whether it
  was worth it" is an observation, not an audit. So: many rows, one of them earning a mark.
"""
from poster_kit import (CINNABAR, H, INK, LATIN, MONO, W, COOL, cut_stroke, disc,  # noqa: F401
                        footer, rule, text, write)


def build():
    rows = []
    y = 390
    for i, (claim, mark) in enumerate([
            ("done", "no touchpoint"), ("verified", "no touchpoint"),
            ("passed", "exit code 0"), ("checked", "no touchpoint"),
            ("shipped", "no touchpoint")]):
        w = 520 if mark != "exit code 0" else 900
        rows.append(f'<rect x="70" y="{y}" width="{w}" height="26" fill="{INK}" opacity="0.86"/>')
        rows.append(text(70 + w + 24, y + 21, mark, 19, INK, MONO, track=0.6))
        y += 62
    # the one verdict: a mark you can only make when the row underneath holds
    # the mark sits on the one row that has something under it, not off on its own
    mark = (disc(1330, 527, 92, 92, fill=CINNABAR, seed=7, wobble=3.4)
            + text(1330, 560, "✓", 92, COOL, LATIN, anchor="middle"))

    inner = ("".join(rows) + mark
             + text(70, 176, "AUDIT ANYTHING", 118, INK, LATIN, track=-1.6, weight="700")
             + rule(70, 214, 1530, 210, 3.6, 2.4, seed=5)
             + text(70, 258, "a finding without a touchpoint is an observation, not an audit",
                    27, INK, LATIN, track=1.2)
             + text(70, 316, "claim", 17, INK, MONO, track=3.0)
             + text(640, 316, "what is under it", 17, INK, MONO, track=3.0)
             + footer("audit-anything", "what for · what it caused · whether it was worth it"))
    write("audit-anything", COOL, inner)


if __name__ == "__main__":
    build()
