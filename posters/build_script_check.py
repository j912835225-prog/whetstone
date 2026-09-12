# -*- coding: utf-8 -*-
"""Poster: script-check.

RECIPE
  subject:  一个人，一件事，其余都是陪衬
  intent:   announce
  text:     剧本检查（锁）
  inks:     ink #15151A + 靛青 #1B3FA0；纸 冷灰 #EAEAE6
  division: 墨＝主角与标题；靛青＝那件事（一束光），别处不出现
  layout:   图占版——人立在光里，光跨出下边
  focus:    一个巨大的物：那束光，宽过画面三分之一
  air:      右侧整片灰
  paper:    ~45%
  texture:  纸纹＋套版偏移

WHY
  「一场戏为一个人的一件事而写」——所以画面上只许站一个人，只许有一束光。
  陪衬全删：这张海报本身就得过它自己那一条。
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
    rows = [("一人", "一事"), ("埋了的", "要收"), ("支线", "为主线服务，否则删"),
            ("写完", "问这场怎么演")]
    right, y = [], 392
    for a, b in rows:
        right.append(text(980, y, a, 40, INK, CJK_SONG, track=2.0))
        right.append(text(1180, y, b, 40, INK, CJK_SONG, track=2.0))
        right.append(f'<path d="{cut_stroke([(980, y + 22), (1512, y + 20)], 2.4, 1.6, seed=int(y), wobble=0.9)}" fill="{INK}" opacity="0.35"/>')
        y += 104

    inner = (spotlight() + figure() + "".join(right)
             + text(88, 172, "SCRIPT CHECK", 84, INK, LATIN, track=-0.8, weight="700")
             + rule(88, 210, 1512, 206, 3.6, 2.4, seed=5)
             + text(88, 254, "一场戏为一个人的一件事而写，其余都是陪衬", 32, INK, CJK_SONG, track=3.0)
             + footer("script-check", "结构 · 伏笔 · 对白八查 · 三处收口"))
    write("script-check", COOL, inner)


if __name__ == "__main__":
    build()
