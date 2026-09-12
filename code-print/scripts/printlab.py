# -*- coding: utf-8 -*-
"""Old-printed-matter kit: misregistration, paper grain, mottle, ink bite.

Shared by label, poster and screenprint work. Pure geometry + SVG filters, no dependencies.
"""
from woodcut import *

def defs(seed=1, grain=0.13, grain_freq=0.8, mottle=0.10, edge=1.1, edge_freq=0.05):
    return f'''
  <filter id="edgeR" x="-8%" y="-8%" width="116%" height="116%">
    <feTurbulence type="fractalNoise" baseFrequency="{edge_freq}" numOctaves="3" seed="{seed}" result="t"/>
    <feDisplacementMap in="SourceGraphic" in2="t" scale="{edge}" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="{grain_freq}" numOctaves="4" seed="{seed+3}" result="n"/>
    <feColorMatrix in="n" type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="{grain}"/></feComponentTransfer>
  </filter>
  <filter id="mottle" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="4" seed="{seed+7}" result="n"/>
    <feColorMatrix in="n" type="saturate" values="0"/>
    <feComponentTransfer><feFuncA type="linear" slope="{mottle}"/></feComponentTransfer>
  </filter>
  <filter id="speck" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.28" numOctaves="3" seed="{seed+11}" result="n"/>
    <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  2.4 0 0 0 -1.62" result="a"/>
    <feComposite in="SourceGraphic" in2="a" operator="in"/>
  </filter>'''

def blob(pts, wob=1.6, seed=1):
    return cut_shape(pts, seed=seed, wobble=wob)

def ell(cx, cy, rx, ry, rot=0, wob=1.5, seed=1, n=84):
    return cut_shape(ellipse(cx, cy, rx, ry, rot, n), seed=seed, wobble=wob)

def plate(ds, color, dx=0.0, dy=0.0, op=1.0, filt="edgeR"):
    """One colour plate from a list of path `d` strings.

    dx/dy is the misregistration - the whole character of old printed matter lives in
    those one or two pixels, so do not flatten them to zero.
    """
    return '<g fill="%s" opacity="%s" transform="translate(%s,%s)" filter="url(#%s)">%s</g>' % (
        color, op, dx, dy, filt, "".join('<path d="%s"/>' % d for d in ds))

def fur(outline, cx, cy, count, l0, l1, seed=1, w=1.5, out=0.0, jitter=0.5, depth=(0.0, 0.0)):
    """毛：沿轮廓（或轮廓内缩）长出短锥形刀线，方向背离体心。"""
    P = resample(outline, 2.0, closed=True)
    rng = random.Random(seed)
    n = len(P); res = []
    for k in range(count):
        i = int(rng.random() * n)
        p = P[i]
        if depth[1] > 0:                      # 往体内缩，让毛长满整块，不只长在边上
            f = rng.uniform(depth[0], depth[1]) ** 0.65
            p = (p[0] + (cx - p[0]) * f, p[1] + (cy - p[1]) * f)
        dx, dy = p[0] - cx, p[1] - cy
        L = math.hypot(dx, dy) or 1.0
        dx, dy = dx / L, dy / L
        ax = math.atan2(dy, dx) + rng.uniform(-jitter, jitter)
        ln = rng.uniform(l0, l1)
        bx = p[0] - dx * ln * out * 0.4 + rng.uniform(-3, 3)
        by = p[1] - dy * ln * out * 0.4 + rng.uniform(-3, 3)
        ex = bx + math.cos(ax) * ln
        ey = by + math.sin(ax) * ln
        mx = (bx + ex) / 2 + math.cos(ax + 1.57) * ln * rng.uniform(-0.18, 0.18)
        my = (by + ey) / 2 + math.sin(ax + 1.57) * ln * rng.uniform(-0.18, 0.18)
        res.append(cut_stroke(bez((bx, by), (mx, my), (mx, my), (ex, ey), 10),
                              w * rng.uniform(0.7, 1.3), w * 0.25, seed=seed * 3 + k,
                              wobble=0.5, chatter=0.15, taper=0.18, notches=0, step=6.0))
    return res

def group(markup, dx=0.0, dy=0.0, op=1.0, filt="edgeR"):
    """Like `plate`, but for markup you already built yourself (mixed fills, text).

    Use this when one plate carries both ink shapes and paper-coloured holes: `plate`
    paints everything one colour, this one leaves your fills alone.
    """
    return '<g opacity="%s" transform="translate(%s,%s)" filter="url(#%s)">%s</g>' % (
        op, dx, dy, filt, markup)


def svg_document(name, w, h, paper, svg_inner, defs_str):
    """A standalone SVG file: paper rectangle at the bottom, everything else on top.

    Standalone rather than embedded in HTML on purpose - an SVG opens in a browser, in
    Illustrator/Inkscape, and in `rsvg-convert`, and it is what a printer can take.
    """
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"
     role="img" aria-label="{name}">
<defs>{defs_str}</defs>
<rect x="0" y="0" width="{w}" height="{h}" fill="{paper}"/>
{svg_inner}
</svg>
'''


def fur_fast(outline, cx, cy, count, l0, l1, seed=1, w=1.6, jitter=0.5, depth=(0.0, 0.0), out=0.0, ox=None, oy=None):
    """一根毛＝五点的锥形薄片（带一点弯）。cx/cy 是「流场原点」——放在头顶之上，毛就向下外撇，不是炸开。"""
    if ox is None: ox, oy = cx, cy
    P = resample(outline, 2.5, closed=True)
    rng = random.Random(seed); n = len(P); res = []
    for _ in range(count):
        p = P[int(rng.random() * n)]
        if depth[1] > 0:
            f = rng.uniform(depth[0], depth[1]) ** 1.5
            p = (p[0] + (ox - p[0]) * f * 0.55, p[1] + (oy - p[1]) * f * 0.55)
        dx, dy = p[0] - cx, p[1] - cy
        L = math.hypot(dx, dy) or 1.0
        a = math.atan2(dy / L, dx / L) + rng.uniform(-jitter, jitter)
        ln = rng.uniform(l0, l1)
        bend = rng.uniform(-0.28, 0.28)
        bx = p[0] - math.cos(a) * ln * out * 0.35
        by = p[1] - math.sin(a) * ln * out * 0.35
        ww = w * rng.uniform(0.7, 1.35)
        nx, ny = -math.sin(a), math.cos(a)
        mx = bx + math.cos(a) * ln * 0.55 + nx * ln * bend * 0.5
        my = by + math.sin(a) * ln * 0.55 + ny * ln * bend * 0.5
        tx = bx + math.cos(a) * ln + nx * ln * bend
        ty = by + math.sin(a) * ln + ny * ln * bend
        res.append("M%.0f %.0fL%.0f %.0fL%.0f %.0fL%.0f %.0fL%.0f %.0fZ" % (
            bx + nx*ww, by + ny*ww, mx + nx*ww*0.55, my + ny*ww*0.55, tx, ty,
            mx - nx*ww*0.55, my - ny*ww*0.55, bx - nx*ww, by - ny*ww))
    return res
