# -*- coding: utf-8 -*-
"""Poster: chinese-prose.

RECIPE
  subject:  一段稿子，和删掉的那几行
  intent:   observe
  text:     CHINESE PROSE (locked) + a vertical CUT
  inks:     ink #15151A + cinnabar #C1352C; paper warm white #F1EAD8
  division: ink = the specimen and the type; cinnabar = the strikes, and nothing else
  layout:   type-dominant - a vertical word governs the left, the edited page sits right
  focus:    the vertical CUT, eight times the size of the smallest type
  air:      the paper at lower left
  paper:    ~55%
  texture:  paper grain + misregistration

WHY
  The skill's test is "if the meaning did not shrink, the cut was right". So the poster is
  not a clean finished page - it is a page being edited: what stays in ink, what goes in red.
  The specimen stays in Chinese because the specimen *is* the subject; everything around it
  is English, so a reader who does not read Chinese can still see exactly what is happening.
"""
from poster_kit import (CINNABAR, CJK_SONG, H, INK, LATIN, MONO, W, WARM,  # noqa: F401
                        cut_stroke, footer, rule, text, write)

# A real paragraph, twice: what survives, and what a red pencil takes out. The struck
# lines are not "bad writing" in the abstract - they are the same content inflated, which
# is the only comparison that teaches anything.
LINES = [
    ("雨下了三天。", False),
    ("众所周知，降水是一种十分常见的自然现象", True),
    ("她把伞收起来，靠在门边。", False),
    ("在某种意义上来说，她做出了收伞这一动作", True),
    ("没什么可说的，钱已经放在了桌上。", False),
    ("他的内心充满了复杂而难以言喻的情绪", True),
    ("闷的人发慌，罐头一样的日子。", False),
]

def build():
    rows, y = [], 372
    for s, struck in LINES:
        rows.append(text(560, y, s, 40, INK, CJK_SONG, track=2.0))
        if struck:
            rows.append(f'<path d="{cut_stroke([(552, y - 15), (552 + len(s) * 39.4, y - 15)], 5, 3.4, seed=int(y), wobble=1.4)}" fill="{CINNABAR}"/>')
        y += 72

    # One vertical word - the vertical setting is the single disruption, so nothing else
    # breaks the grid. It says what the red marks do.
    vertical = "".join(text(206, 420 + i * 152, ch, 132, INK, LATIN, anchor="middle",
                            weight="700")
                       for i, ch in enumerate("CUT"))

    inner = ("".join(rows) + vertical
             + text(88, 176, "CHINESE PROSE", 96, INK, LATIN, track=-1.2, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 258, "fit the occasion first, then the facts, then the ear", 27, INK, LATIN, track=1.0)
             + text(1512, 302, "if the meaning did not shrink, the cut was right", 21, CINNABAR, LATIN, track=0.6, anchor="end")
             + text(560, 330, "one paragraph, and what the red pencil takes out", 19, INK, MONO, track=1.0)
             + footer("chinese-prose", "one checklist: drafting, revising, and judging a draft"))
    write("chinese-prose", WARM, inner)


if __name__ == "__main__":
    build()
