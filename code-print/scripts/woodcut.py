# -*- coding: utf-8 -*-
"""刀口引擎：把干净几何变成「刻出来的」。
几何层负责收尖 / 手抖 / 崩口；滤镜层（SVG 侧）负责高频刀颤。纯程序化，零生图。"""
import math, random

# ---------- 相关噪声（不是白噪声：白噪声抖出来是数码毛边，不是手抖） ----------
def noise(seed, harmonics=4, base=1.0):
    rng = random.Random(seed)
    comps = []
    for k in range(harmonics):
        comps.append((base * (2 ** k) * rng.uniform(0.7, 1.4),
                      1.0 / (1.7 ** k), rng.uniform(0, 2 * math.pi)))
    norm = sum(a for _, a, _ in comps)
    def f(t):
        return sum(a * math.sin(2 * math.pi * fr * t + ph) for fr, a, ph in comps) / norm
    return f

# ---------- 基础几何 ----------
def bez(p0, p1, p2, p3, n=48):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
                    u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]))
    return out

def ellipse(cx, cy, rx, ry, rot=0.0, n=96):
    r = math.radians(rot); c, s = math.cos(r), math.sin(r)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts

def smooth(ctrl, n=16, closed=True):
    """Catmull-Rom 过一串手放的控制点，得到密点列（默认闭合）。交 cut_shape 前用。"""
    P = list(ctrl); m = len(P); out = []
    for i in range(m if closed else m - 1):
        p0 = P[(i-1) % m]; p1 = P[i]; p2 = P[(i+1) % m]; p3 = P[(i+2) % m]
        for k in range(n):
            t = k / n
            out.append((0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t*t + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t*t*t),
                        0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t*t + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t*t*t)))
    if not closed: out.append(P[-1])
    return out

def resample(pts, step=3.0, closed=False):
    p = pts + [pts[0]] if closed else pts
    segs, total = [], 0.0
    for i in range(len(p) - 1):
        d = math.hypot(p[i+1][0]-p[i][0], p[i+1][1]-p[i][1])
        segs.append(d); total += d
    if total < 1e-6: return pts
    n = max(8, int(total / step))
    out, acc, j = [], 0.0, 0
    for i in range(n):
        target = total * i / n
        while j < len(segs) and acc + segs[j] < target:
            acc += segs[j]; j += 1
        if j >= len(segs): break
        u = (target - acc) / segs[j] if segs[j] > 1e-9 else 0
        out.append((p[j][0] + (p[j+1][0]-p[j][0]) * u, p[j][1] + (p[j+1][1]-p[j][1]) * u))
    return out

def normals(pts, closed=False):
    n = len(pts); out = []
    for i in range(n):
        a = pts[i-1] if (i > 0 or closed) else pts[0]
        b = pts[(i+1) % n] if (i < n-1 or closed) else pts[-1]
        dx, dy = b[0]-a[0], b[1]-a[1]
        L = math.hypot(dx, dy) or 1.0
        out.append((-dy/L, dx/L))
    return out

def d_of(pts, close=True):
    s = "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % p for p in pts[1:])
    return s + ("Z" if close else "")

# ---------- 刀口：中线 + 宽度包络 -> 闭合轮廓，两端收尖，边缘崩口 ----------
def cut_stroke(pts, w0, w1=None, seed=1, wobble=2.4, chatter=0.9,
               taper=0.11, notches=2, step=3.0):
    w1 = w0 if w1 is None else w1
    P = resample(pts, step)
    if len(P) < 4: P = pts
    N = normals(P)
    n = len(P)
    nw = noise(seed, 4, 2.6)          # 低频手抖
    ne1 = noise(seed + 91, 3, 9.0)    # 边缘颤
    ne2 = noise(seed + 173, 3, 9.0)
    rng = random.Random(seed + 7)
    chips = [(rng.uniform(0.12, 0.88), rng.choice([0, 1]), rng.uniform(0.012, 0.03),
              rng.uniform(0.45, 0.95)) for _ in range(notches)]
    L, R = [], []
    for i, (p, nv) in enumerate(zip(P, N)):
        t = i / (n - 1)
        env = min(1.0, (t / taper) ** 0.5, ((1 - t) / taper) ** 0.5) if taper > 0 else 1.0
        w = (w0 + (w1 - w0) * t) * env
        off = wobble * nw(t)
        wl = w + chatter * ne1(t); wr = w + chatter * ne2(t)
        for ct, side, cw, depth in chips:              # 崩口
            if abs(t - ct) < cw:
                k = (1 - abs(t - ct) / cw) * depth
                if side == 0: wl *= (1 - k)
                else: wr *= (1 - k)
        L.append((p[0] + nv[0]*(wl+off), p[1] + nv[1]*(wl+off)))
        R.append((p[0] - nv[0]*(wr-off), p[1] - nv[1]*(wr-off)))
    return d_of(L + R[::-1])

# ---------- 闭合形：沿外法线做相关扰动 ----------
def cut_shape(pts, seed=1, wobble=2.6, step=3.5):
    P = resample(pts, step, closed=True)
    N = normals(P, closed=True)
    nw = noise(seed, 4, 3.2); nf = noise(seed + 55, 3, 11.0)
    n = len(P); out = []
    for i, (p, nv) in enumerate(zip(P, N)):
        t = i / n
        o = wobble * nw(t) + wobble * 0.35 * nf(t)
        out.append((p[0] + nv[0]*o, p[1] + nv[1]*o))
    return d_of(out)

# ---------- 骨架 -> 锥形肢体 ----------
def limb(p0, p1, w0, w1, seed=1, bow=0.0, wobble=1.8):
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy/L, dx/L
    ctrl = (mx + nx*bow, my + ny*bow)
    spine = bez(p0, (p0[0]+(ctrl[0]-p0[0])*0.8, p0[1]+(ctrl[1]-p0[1])*0.8),
                (p1[0]+(ctrl[0]-p1[0])*0.8, p1[1]+(ctrl[1]-p1[1])*0.8), p1, 32)
    P = resample(spine, 3.0); N = normals(P); n = len(P)
    nw = noise(seed, 3, 2.4)
    L_, R_ = [], []
    for i, (p, nv) in enumerate(zip(P, N)):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * t
        cap = min(1.0, (t / 0.05) ** 0.45, ((1 - t) / 0.05) ** 0.45)
        w *= (0.55 + 0.45 * cap)
        o = wobble * nw(t)
        L_.append((p[0] + nv[0]*(w+o), p[1] + nv[1]*(w+o)))
        R_.append((p[0] - nv[0]*(w-o), p[1] - nv[1]*(w-o)))
    return d_of(L_ + R_[::-1]), spine

def spine_of(p0, p1, bow=0.0):
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy/L, dx/L
    ctrl = (mx + nx*bow, my + ny*bow)
    return bez(p0, (p0[0]+(ctrl[0]-p0[0])*0.8, p0[1]+(ctrl[1]-p0[1])*0.8),
               (p1[0]+(ctrl[0]-p1[0])*0.8, p1[1]+(ctrl[1]-p1[1])*0.8), p1, 32)

# ---------- 程序化排线：沿骨骼方向、贴形体走 ----------
def hatch_along(p0, p1, half_w, count, length_frac=(0.12, 0.88), seed=1,
                w=1.7, bow=6.0, spread=0.82):
    """绕一根骨骼铺横向排线（衣褶/袜纹）。返回 cut_stroke 的 d 列表。"""
    sp = spine_of(p0, p1)
    P = resample(sp, 2.0); N = normals(P); n = len(P)
    rng = random.Random(seed)
    out = []
    for k in range(count):
        t = length_frac[0] + (length_frac[1]-length_frac[0]) * (k + 0.5) / count
        i = min(n - 1, int(t * (n - 1)))
        p, nv = P[i], N[i]
        hw = half_w * spread * rng.uniform(0.72, 1.0)
        a = (p[0] - nv[0]*hw, p[1] - nv[1]*hw)
        b = (p[0] + nv[0]*hw, p[1] + nv[1]*hw)
        mid = ((a[0]+b[0])/2 + (P[min(n-1,i+3)][0]-p[0])*bow*0.12,
               (a[1]+b[1])/2 + (P[min(n-1,i+3)][1]-p[1])*bow*0.12)
        arc = bez(a, ((a[0]+mid[0])/2, (a[1]+mid[1])/2),
                  ((b[0]+mid[0])/2, (b[1]+mid[1])/2), b, 18)
        out.append(cut_stroke(arc, w * rng.uniform(0.75, 1.25), seed=seed*13+k,
                              wobble=1.1, chatter=0.35, taper=0.3, notches=0))
    return out

def hatch_drape(top_l, top_r, bot_l, bot_r, count, seed=1, w=1.9, bow=14.0):
    """衣褶：从肩线到下摆的一族竖向刀线，两端收尖。"""
    rng = random.Random(seed)
    out = []
    for k in range(count):
        u = (k + 0.5) / count
        a = (top_l[0] + (top_r[0]-top_l[0])*u, top_l[1] + (top_r[1]-top_l[1])*u)
        b = (bot_l[0] + (bot_r[0]-bot_l[0])*u, bot_l[1] + (bot_r[1]-bot_l[1])*u)
        s = (u - 0.5) * 2.0
        c1 = (a[0] + s*bow*0.5, a[1] + (b[1]-a[1])*0.34)
        c2 = (b[0] + s*bow, a[1] + (b[1]-a[1])*0.70)
        arc = bez(a, c1, c2, b, 30)
        out.append(cut_stroke(arc, w * rng.uniform(0.7, 1.3), seed=seed*7+k,
                              wobble=1.3, chatter=0.4, taper=0.16, notches=1))
    return out

# ---------- 区域裁切的平行刀线场（木刻建体积的正法） ----------
import re as _re
def bbox_of_d(d):
    v = [float(x) for x in _re.findall(r'-?\d+\.?\d*', d)]
    xs, ys = v[0::2], v[1::2]
    return min(xs), min(ys), max(xs), max(ys)

def hatch_field(d, angle_deg, spacing, seed, w=2.1, keep=(0.0, 1.0), bow=2.2):
    x0, y0, x1, y1 = bbox_of_d(d)
    cx, cy = (x0+x1)/2, (y0+y1)/2
    R = math.hypot(x1-x0, y1-y0)/2 + 10
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    rng = random.Random(seed)
    n = max(2, int(2*R/spacing))
    out = []
    for i in range(n+1):
        f = i/n
        if not (keep[0] <= f <= keep[1]): continue
        off = -R + i*spacing + rng.uniform(-0.28, 0.28)*spacing
        p0 = (cx+nx*off-dx*R, cy+ny*off-dy*R)
        p1 = (cx+nx*off+dx*R, cy+ny*off+dy*R)
        m = ((p0[0]+p1[0])/2 + nx*rng.uniform(-bow, bow),
             (p0[1]+p1[1])/2 + ny*rng.uniform(-bow, bow))
        arc = bez(p0, ((p0[0]+m[0])/2, (p0[1]+m[1])/2),
                  ((p1[0]+m[0])/2, (p1[1]+m[1])/2), p1, 26)
        out.append(cut_stroke(arc, w*rng.uniform(0.82, 1.18), seed=seed*37+i,
                              wobble=1.0, chatter=0.3, taper=0.02, notches=0))
    return out

def ang(p0, p1):
    return math.degrees(math.atan2(p1[1]-p0[1], p1[0]-p0[0]))

# ---------- 卷涡语汇：一缕「锁」= 渐细的带子，末端收成螺旋 ----------
def coil(x, y, a0_deg, s0=9.0, decay=0.963, turn=0.13, n=90, ramp=0.34, ccw=1, drift=0.0):
    """turtle 走线：起手近直，转率渐上，末端成对数螺旋。drift 给起手段一点弧度。"""
    a = math.radians(a0_deg); s = s0; pts = [(x, y)]
    for i in range(n):
        t = i / n
        r = min(1.0, t / ramp)
        a += turn * r * ccw + math.radians(drift) * (1 - r)
        if t >= ramp: s *= decay   # 甩出的那一段等步长走直，进涡才收
        x += s * math.cos(a); y += s * math.sin(a)
        pts.append((x, y))
    return pts

def ribbon(spine, w0, w1, seed=1, wobble=0.9):
    """把中线变成两侧渐细的闭合带（锁的外形）。"""
    P = resample(spine, 2.4); N = normals(P); n = len(P)
    nw = noise(seed, 3, 2.2)
    L, R = [], []
    for i, (p, nv) in enumerate(zip(P, N)):
        t = i / (n - 1)
        w = w0 + (w1 - w0) * (t ** 0.85)
        cap = min(1.0, (t / 0.04) ** 0.5)
        w *= (0.4 + 0.6 * cap)
        o = wobble * nw(t)
        L.append((p[0] + nv[0]*(w+o), p[1] + nv[1]*(w+o)))
        R.append((p[0] - nv[0]*(w-o), p[1] - nv[1]*(w-o)))
    return L + R[::-1]

def curvature(pts, closed=False):
    n = len(pts); out = []
    for i in range(n):
        a = pts[(i-1) % n] if closed else pts[max(0, i-1)]
        b = pts[i]
        c = pts[(i+1) % n] if closed else pts[min(n-1, i+1)]
        v1 = (b[0]-a[0], b[1]-a[1]); v2 = (c[0]-b[0], c[1]-b[1])
        l1 = math.hypot(*v1) or 1e-6; l2 = math.hypot(*v2) or 1e-6
        cr = (v1[0]*v2[1] - v1[1]*v2[0]) / (l1*l2)
        out.append(abs(max(-1.0, min(1.0, cr))))
    # 平滑
    sm = []
    for i in range(n):
        w = [out[(i+k) % n] if closed else out[max(0, min(n-1, i+k))] for k in range(-4, 5)]
        sm.append(sum(w)/len(w))
    return sm

def ink_line(pts, w=2.4, closed=False, seed=1, curve_gain=0.9, taper=0.06,
             wobble=0.8, chatter=0.25, notches=0):
    """墨线：粗细跟着曲率走（转折处顿，平缓处细）——这是上一轮欠的那件事。"""
    P = resample(pts, 2.2, closed=closed)
    if closed: P = P + [P[0]]
    N = normals(P, closed=False)
    cv = curvature(P, closed=False)
    _sv = sorted(cv); mx = _sv[int(0.88*(len(_sv)-1))] or (max(cv) or 1.0)
    n = len(P)
    nw = noise(seed, 4, 2.4); ne = noise(seed+77, 3, 8.0)
    L, R = [], []
    for i, (p, nv) in enumerate(zip(P, N)):
        t = i / (n - 1)
        k = min(1.35, cv[i] / mx) ** 0.6
        ww = w * (1.0 - curve_gain*0.5 + curve_gain * k * 1.15)
        if not closed and taper > 0:
            ww *= min(1.0, (t/taper)**0.5, ((1-t)/taper)**0.5)
        o = wobble * nw(t); c = chatter * ne(t)
        L.append((p[0] + nv[0]*(ww+c+o), p[1] + nv[1]*(ww+c+o)))
        R.append((p[0] - nv[0]*(ww+c-o), p[1] - nv[1]*(ww+c-o)))
    return d_of(L + R[::-1])

def scallop(pts, n_lobes, depth, closed=True, phase=0.0, seed=1, keep=None):
    """把一条边缘揉成鳞状/花瓣状（发团、髯团的外缘就是被卷缕顶出来的）。"""
    P = resample(pts, 3.0, closed=closed)
    N = normals(P, closed=closed)
    n = len(P); rng = random.Random(seed); jit = [rng.uniform(0.75, 1.25) for _ in range(n_lobes + 2)]
    out = []
    for i, (p, nv) in enumerate(zip(P, N)):
        t = i / n
        if keep and not (keep[0] <= t <= keep[1]):
            out.append(p); continue
        u = (t * n_lobes + phase) % n_lobes
        k = jit[int(u) % len(jit)]
        d = depth * k * (math.sin(math.pi * (t * n_lobes + phase)) ** 2)
        out.append((p[0] + nv[0]*d, p[1] + nv[1]*d))
    return out
