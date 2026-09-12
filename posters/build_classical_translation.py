# -*- coding: utf-8 -*-
"""Poster: classical-chinese-translation.

RECIPE
  subject:  一百回的书脊，和第七十八回那一道缺口
  intent:   notify
  text:     译古书（锁）
  inks:     ink #15151A + 赭石 #B45A33；纸 暖白 #F1EAD8
  division: 墨＝一百道书脊与标题；赭石＝缺的那一回，只此一处
  layout:   物件场——同一个物件重复一百次，变高矮
  focus:    一个反常：整齐的一百道里，第七十八道是空的
  air:      标题下那条横带
  paper:    ~50%
  texture:  纸纹

WHY
  这件 skill 的核心不是「怎么译」，是「译到第七十八回时禁令已经静默失效」。
  缺口不会报错，它只是安静地把位置腾出来。所以海报画一百道，让那一道空着。
"""
import math
import random

from poster_kit import (CJK_SONG, H, INK, LATIN, MONO, OCHRE, W, WARM,  # noqa: F401
                        cut_stroke, footer, rule, text, write)

MISSING = 78


def spines():
    rng = random.Random(3)
    out = []
    x0, gap = 92, 14.4
    for i in range(1, 101):
        x = x0 + (i - 1) * gap
        h = 200 + 150 * abs(math.sin(i / 9.0)) + rng.uniform(-24, 24)
        y = 810 - h
        if i == MISSING:
            # the gap: drawn in the second ink, at full height, so the absence is loud
            out.append(f'<path d="{cut_stroke([(x + 4, 330), (x + 4, 812)], 9, 7, seed=11, wobble=1.8)}" fill="{OCHRE}"/>')
            out.append(text(x + 4, 314, "78", 21, OCHRE, MONO, track=1.0, anchor="middle"))
            continue
        out.append(f'<rect x="{x:.1f}" y="{y:.0f}" width="9" height="{h:.0f}" fill="{INK}" '
                   f'opacity="{rng.uniform(0.72, 0.95):.2f}"/>')
    return "".join(out)


def build():
    inner = (spines()
             + text(88, 172, "CLASSICAL TRANSLATION", 76, INK, LATIN, track=-0.6, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 254, "失败不在译不动，在译到第七十八回时禁令已经静默失效",
                    32, INK, CJK_SONG, track=3.0)
             + text(1512, 862, "缺口不会报错，它只是把位置腾出来让记忆去填",
                    21, OCHRE, CJK_SONG, track=1.6, anchor="end")
             + footer("classical-chinese-translation", "底本纪律 · 回目交叉核 · 四条防漂移"))
    write("classical-chinese-translation", WARM, inner)


if __name__ == "__main__":
    build()
