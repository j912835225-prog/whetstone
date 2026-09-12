# -*- coding: utf-8 -*-
"""Poster: chinese-prose.

RECIPE
  subject:  一段稿子，和删掉的那几行
  intent:   observe
  text:     成稿检查（锁）
  inks:     ink #15151A + cinnabar #C1352C；纸 暖白 #F1EAD8
  division: 墨＝正文与标题；朱砂＝删改的那几笔，别的地方一点不出现
  layout:   字占版——竖排大字统治左侧，右侧是被改过的稿面
  focus:    竖排的两个大字「成稿」，是最小字的八倍
  air:      左下那片纸
  paper:    ~55%
  texture:  纸纹＋套版偏移

WHY
  这件 skill 的判据是「删完意思没少，删对了」。所以海报画的不是干净的成品，是改过的稿：
  留下的墨，划掉的朱砂。改稿的样子本身就是这件事的样子。
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

    # 竖排大字：竖排本身就是那唯一的打破点，不再加第二个
    vertical = "".join(text(224, 452 + i * 186, ch, 168, INK, CJK_SONG, anchor="middle")
                       for i, ch in enumerate("成稿"))

    inner = ("".join(rows) + vertical
             + text(88, 172, "CHINESE PROSE", 84, INK, LATIN, track=-0.8, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 254, "先合场合，再合事实，最后才合耳朵", 32, INK, CJK_SONG, track=3.0)
             + text(1512, 300, "删完意思没少 · 删对了", 19, CINNABAR, CJK_SONG, track=2.0, anchor="end")
             + footer("chinese-prose", "从动笔到交稿到评稿的一张检查表"))
    write("chinese-prose", WARM, inner)


if __name__ == "__main__":
    build()
