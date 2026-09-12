# -*- coding: utf-8 -*-
"""Poster: prose.

RECIPE
  subject:  two specimens - one Chinese, one English - and what the red pencil takes out
  intent:   observe
  text:     PROSE (locked) + a vertical CUT
  inks:     ink #15151A + cinnabar #C1352C; paper warm white #F1EAD8
  division: ink = the specimen and the type; cinnabar = the strikes, and nothing else
  layout:   type-dominant - a vertical word governs the left, the edited page sits right
  focus:    the vertical CUT, seven times the size of the smallest type
  air:      the paper at lower left
  paper:    ~55%
  texture:  paper grain + misregistration

WHY
  The skill's test is "if the meaning did not shrink, the cut was right". So the poster is
  not a clean finished page - it is a page being edited: what stays in ink, what goes in red.
  Two languages on one sheet, because the skill treats both: the inflation that gets struck
  out looks different in Chinese and in English, and the cut is the same cut.
"""
from poster_kit import (CINNABAR, CJK_SONG, H, INK, LATIN, MONO, W, WARM,  # noqa: F401
                        cut_stroke, footer, rule, text, write)

# A real paragraph, twice: what survives, and what a red pencil takes out. The struck
# lines are not "bad writing" in the abstract - they are the same content inflated, which
# is the only comparison that teaches anything.
LINES = [
    ("雨下了三天。", False, "cjk"),
    ("众所周知，降水是一种十分常见的自然现象", True, "cjk"),
    ("没什么可说的，钱已经放在了桌上。", False, "cjk"),
    ("他的内心充满了复杂而难以言喻的情绪", True, "cjk"),
    ("It rained for three days.", False, "latin"),
    ("Precipitation events were observed to be ongoing", True, "latin"),
    ("Nothing to say. The money was already on the table.", False, "latin"),
]

def build():
    rows, y = [], 372
    for line, struck, script in LINES:
        cjk = script == "cjk"
        size = 40 if cjk else 34
        rows.append(text(560, y, line, size, INK, CJK_SONG if cjk else LATIN,
                         track=2.0 if cjk else 0.4))
        if struck:
            # character widths differ: a CJK glyph is square, Latin is roughly half
            width = len(line) * (39.4 if cjk else 16.4)
            rows.append(f'<path d="{cut_stroke([(552, y - 14), (552 + width, y - 14)], 5, 3.4, seed=int(y), wobble=1.4)}" fill="{CINNABAR}"/>')
        y += 72

    # One vertical word - the vertical setting is the single disruption, so nothing else
    # breaks the grid. It says what the red marks do.
    vertical = "".join(text(206, 420 + i * 152, ch, 132, INK, LATIN, anchor="middle",
                            weight="700")
                       for i, ch in enumerate("CUT"))

    inner = ("".join(rows) + vertical
             + text(88, 176, "PROSE", 132, INK, LATIN, track=-2.4, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 258, "fit the occasion first, then the facts, then the ear", 27, INK, LATIN, track=1.0)
             + text(1512, 302, "if the meaning did not shrink, the cut was right", 21, CINNABAR, LATIN, track=0.6, anchor="end")
             + text(560, 330, "two specimens, and what the red pencil takes out", 19, INK, MONO, track=1.0)
             + footer("prose", "one checklist, two languages: drafting, revising, judging"))
    write("prose", WARM, inner)


if __name__ == "__main__":
    build()
