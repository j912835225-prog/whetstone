#!/usr/bin/env python3
"""timeline_view - compress a span of video into one image you can cut against.

Filmstrip (evenly spaced frames) + waveform band (RMS envelope) + highlighted
silence gaps + word labels (when a transcript is supplied). ffmpeg + PIL + numpy,
nothing hosted, no API cost.

Usage:
    timeline_view.py <video> <start> <end> -o out.png
    timeline_view.py <video> 12.0 25.0 -o v.png --words edit/transcripts/a.words.json

This is not a scanning tool. Call it at decision points - "can I cut in this
pause", "which of these two takes", "did that cut land" - and read
takes_packed.md when you want to see everything. Rendering image after image to
browse the footage is the failure mode it exists to prevent.

Needs: ffmpeg/ffprobe on PATH, plus pillow and numpy.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _env import ensure
ensure("pillow", "numpy")

import numpy as np                                              # noqa: E402
from PIL import Image, ImageDraw, ImageFont                     # noqa: E402

# Visual constants: near-black ground, one accent, no chrome.
BG = (14, 14, 16)
FG = (232, 232, 232)
DIM = (110, 110, 116)
WAVE = (150, 150, 158)
ACCENT = (255, 90, 0)        # silence gaps / cut candidates
GRID = (46, 46, 52)
PAD = 24

# Font lookup walks these in order and falls back to PIL's bitmap font. CJK
# transcripts need a CJK face or the word labels render as boxes.
FONT_MONO = [
    "/System/Library/Fonts/Menlo.ttc",                                  # macOS
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",              # Debian/Ubuntu
    "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",                       # Fedora/Arch
    "C:/Windows/Fonts/consola.ttf",                                     # Windows
]
FONT_CJK = [
    "/System/Library/Fonts/Hiragino Sans GB.ttc",                       # macOS
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",           # Debian/Ubuntu
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",         # Fedora
    "C:/Windows/Fonts/msyh.ttc",                                        # Windows
]


def _font(size: int, cjk: bool = False) -> ImageFont.FreeTypeFont:
    for path in (FONT_CJK + FONT_MONO) if cjk else (FONT_MONO + FONT_CJK):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _run(cmd: list[str]) -> bool:
    return subprocess.run(cmd, capture_output=True, text=True).returncode == 0


def has_video(path: Path) -> bool:
    """Audio-only sources (meeting recordings, podcasts, stripped tracks) have no
    video stream; the filmstrip is skipped entirely for those."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return "video" in r.stdout


# -- frames -------------------------------------------------------------------
def extract_frames(video: Path, start: float, end: float, n: int, dest: Path) -> list[Path]:
    """Evenly spaced frames. Seeking per frame is more controllable than an fps filter."""
    if not has_video(video):
        return []
    out = []
    span = max(end - start, 0.001)
    for i in range(n):
        t = start + span * (i + 0.5) / n
        p = dest / f"f{i:03d}.jpg"
        _run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video),
              "-frames:v", "1", "-q:v", "3", "-vf", "scale=320:-2", str(p)])
        if p.exists():
            out.append(p)
    return out


# -- audio envelope -----------------------------------------------------------
def envelope(video: Path, start: float, end: float, buckets: int) -> np.ndarray:
    """Dump mono 16k PCM, take RMS per bucket, normalise to 0-1. No audio -> zeros."""
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-to", f"{end:.3f}",
             "-i", str(video), "-vn", "-ac", "1", "-ar", "16000",
             "-f", "wav", "-acodec", "pcm_s16le", str(wav)],
            capture_output=True, text=True)
        if r.returncode != 0 or not wav.exists() or wav.stat().st_size < 200:
            return np.zeros(buckets)
        raw = np.frombuffer(wav.read_bytes()[44:], dtype="<i2").astype(np.float32) / 32768.0
    if raw.size == 0:
        return np.zeros(buckets)
    edges = np.linspace(0, raw.size, buckets + 1).astype(int)
    rms = np.array([np.sqrt(np.mean(raw[a:b] ** 2)) if b > a else 0.0
                    for a, b in zip(edges[:-1], edges[1:])])
    peak = rms.max()
    return rms / peak if peak > 1e-9 else rms


# -- transcript ---------------------------------------------------------------
def load_words(path: Path | None, start: float, end: float) -> list[dict]:
    """Read {"words":[{"word","start","end","speaker"?}]} and keep what is in the window."""
    if not path or not path.exists():
        return []
    data = json.loads(path.read_text())
    words = data.get("words", data if isinstance(data, list) else [])
    return [w for w in words
            if float(w.get("end", 0)) > start and float(w.get("start", 0)) < end]


def silence_gaps(words: list[dict], start: float, end: float,
                 threshold: float) -> list[tuple[float, float]]:
    """Gaps of >= threshold between words are cut candidates, including the
    leading and trailing gap of the window."""
    if not words:
        return []
    gaps, cursor = [], start
    for w in sorted(words, key=lambda x: float(x["start"])):
        ws = float(w["start"])
        if ws - cursor >= threshold:
            gaps.append((cursor, ws))
        cursor = max(cursor, float(w["end"]))
    if end - cursor >= threshold:
        gaps.append((cursor, end))
    return gaps


# -- composite ----------------------------------------------------------------
def render(video: Path, start: float, end: float, out: Path,
           n_frames: int, words_path: Path | None, gap_threshold: float,
           width: int) -> dict:
    span = end - start
    inner = width - 2 * PAD

    with tempfile.TemporaryDirectory() as td:
        frames = extract_frames(video, start, end, n_frames, Path(td))
        strip_h = 0
        thumbs = []
        if frames:
            fw = inner // len(frames)
            for p in frames:
                im = Image.open(p).convert("RGB")
                h = max(1, round(im.height * fw / im.width))
                thumbs.append(im.resize((fw, h), Image.LANCZOS))
            strip_h = max(t.height for t in thumbs)

        env = envelope(video, start, end, inner)
        words = load_words(words_path, start, end)
        gaps = silence_gaps(words, start, end, gap_threshold)

        wave_h = 150
        label_h = 62 if words else 0
        head_h = 34
        height = PAD + head_h + strip_h + 12 + wave_h + 10 + label_h + PAD

        canvas = Image.new("RGB", (width, height), BG)
        d = ImageDraw.Draw(canvas, "RGBA")
        f_small, f_tiny = _font(13), _font(11)
        f_word = _font(12, cjk=True)

        def x_of(t: float) -> int:
            return PAD + int(inner * (t - start) / span)

        # header
        d.text((PAD, PAD - 6),
               f"{video.name}   {start:.2f}s -> {end:.2f}s   ({span:.2f}s)",
               font=f_small, fill=FG)
        meta = f"{len(frames)} frames · {len(words)} words · {len(gaps)} gaps >={gap_threshold}s"
        d.text((width - PAD - d.textlength(meta, font=f_tiny), PAD - 4),
               meta, font=f_tiny, fill=DIM)

        y = PAD + head_h

        # filmstrip
        cursor = PAD
        for t in thumbs:
            canvas.paste(t, (cursor, y))
            cursor += t.width
        for i in range(1, len(thumbs)):
            gx = PAD + i * (inner // max(len(thumbs), 1))
            d.line([(gx, y), (gx, y + strip_h)], fill=(0, 0, 0), width=1)
        y += strip_h + 12

        # silence gaps: bars through the waveform band (cut candidates)
        wave_top, wave_mid = y, y + wave_h // 2
        for gs, ge in gaps:
            d.rectangle([x_of(gs), wave_top, max(x_of(ge), x_of(gs) + 1), wave_top + wave_h],
                        fill=(*ACCENT, 46))
            d.line([(x_of(gs), wave_top), (x_of(gs), wave_top + wave_h)], fill=ACCENT, width=1)
            d.line([(x_of(ge), wave_top), (x_of(ge), wave_top + wave_h)], fill=ACCENT, width=1)

        # waveform (mirrored RMS)
        d.line([(PAD, wave_mid), (PAD + inner, wave_mid)], fill=GRID, width=1)
        for i, v in enumerate(env):
            h = int(v * (wave_h / 2 - 4))
            if h:
                d.line([(PAD + i, wave_mid - h), (PAD + i, wave_mid + h)], fill=WAVE)

        # second ticks
        step = 1.0 if span <= 12 else (2.0 if span <= 30 else 5.0)
        tick = start - (start % step) + step
        while tick < end:
            tx = x_of(tick)
            d.line([(tx, wave_top + wave_h), (tx, wave_top + wave_h + 5)], fill=DIM)
            d.text((tx + 3, wave_top + wave_h - 13), f"{tick:.0f}", font=f_tiny, fill=DIM)
            tick += step
        y = wave_top + wave_h + 10

        # word labels on two staggered rows so they do not collide
        if words:
            last_x = [-1e9, -1e9]
            for i, w in enumerate(sorted(words, key=lambda x: float(x["start"]))):
                wx = x_of(float(w["start"]))
                txt = str(w.get("word", "")).strip()
                if not txt:
                    continue
                row = i % 2
                tw = d.textlength(txt, font=f_word)
                if wx < last_x[row] + 4:
                    continue
                ty = y + row * 24
                d.line([(wx, y - 8), (wx, ty)], fill=GRID, width=1)
                spk = w.get("speaker")
                d.text((wx + 2, ty), txt, font=f_word,
                       fill=FG if spk in (None, "S0") else ACCENT)
                last_x[row] = wx + tw

        out.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out)

    return {"png": str(out), "frames": len(frames), "words": len(words),
            "gaps": [(round(a, 2), round(b, 2)) for a, b in gaps],
            "size": f"{width}x{height}"}


def main() -> None:
    ap = argparse.ArgumentParser(
        description="timeline composite: filmstrip + waveform + silence gaps + words")
    ap.add_argument("video", type=Path)
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--words", type=Path, default=None, help="word-level transcript json")
    ap.add_argument("--n-frames", type=int, default=10)
    ap.add_argument("--gap", type=float, default=0.4, help="silence gap threshold, seconds")
    ap.add_argument("--width", type=int, default=1600)
    a = ap.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is not on PATH")
    if not a.video.exists():
        sys.exit(f"not found: {a.video}")

    info = render(a.video, a.start, a.end, a.out, a.n_frames, a.words, a.gap, a.width)
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
