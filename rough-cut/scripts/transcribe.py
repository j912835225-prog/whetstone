#!/usr/bin/env python3
"""transcribe - word-level timestamps, locally, with no API cost.

Writes one word table per source:
    {"source","duration","language","words":[{"word","start","end","speaker"}]}
That schema is the only input contract the rest of this toolchain has
(timeline_view / pack / subtitle building in render all read it).

Usage:
    transcribe.py <video|audio> --edit-dir <footage>/edit
    transcribe.py <dir> --edit-dir <footage>/edit          # whole folder
    transcribe.py a.mp4 --edit-dir edit --model base       # faster, rougher

Two rules that matter:
  - Ask for word-level verbatim output, never sentence-level or SRT. Sentence
    level throws away sub-second gaps, and the gaps are where the cuts are.
  - Cache by source. If mtime+size have not changed, never re-transcribe.

Requires `openai-whisper` (pip install openai-whisper) and ffmpeg on PATH.
The first run downloads the model weights; `--model base` is ~150MB,
`large-v3-turbo` is ~1.5GB.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MEDIA_EXT = {".mp4", ".mov", ".mkv", ".m4v", ".avi", ".webm",
             ".wav", ".mp3", ".m4a", ".aac", ".flac"}


def probe_duration(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def extract_audio(src: Path, dest: Path) -> None:
    """Whisper wants 16k mono. Video gets demuxed; audio files go through too."""
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vn", "-ac", "1",
         "-ar", "16000", "-acodec", "pcm_s16le", str(dest)],
        capture_output=True, text=True)
    if r.returncode != 0 or not dest.exists():
        sys.exit(f"audio extraction failed for {src.name}: {r.stderr[-800:]}")


def stamp(src: Path) -> str:
    st = src.stat()
    return f"{int(st.st_mtime)}:{st.st_size}"


def transcribe_one(src: Path, edit_dir: Path, model_name: str,
                   language: str | None, force: bool) -> Path:
    out = edit_dir / "transcripts" / f"{src.stem}.words.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.exists() and not force:
        try:
            if json.loads(out.read_text()).get("_stamp") == stamp(src):
                print(f"cached {src.name} -> {out.name}")
                return out
        except Exception:
            pass

    try:
        import whisper  # imported late so path errors surface first
    except ImportError:
        sys.exit("openai-whisper is not installed. `pip install openai-whisper`")

    print(f"transcribing {src.name} (model={model_name}) ...", flush=True)
    model = whisper.load_model(model_name)
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "a.wav"
        extract_audio(src, wav)
        result = model.transcribe(str(wav), word_timestamps=True,
                                  language=language, verbose=False)

    words: list[dict] = []
    for seg in result.get("segments", []):
        for w in seg.get("words", []) or []:
            token = str(w.get("word", "")).strip()
            if not token:
                continue
            words.append({"word": token,
                          "start": round(float(w["start"]), 3),
                          "end": round(float(w["end"]), 3),
                          "speaker": "S0"})

    payload = {
        "source": str(src.resolve()),
        "stem": src.stem,
        "duration": round(probe_duration(src), 3),
        "language": result.get("language"),
        "model": model_name,
        "text": result.get("text", "").strip(),
        "words": words,
        "_stamp": stamp(src),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"  -> {len(words)} words / {payload['duration']:.1f}s / {out}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="word-level transcription (local whisper)")
    ap.add_argument("target", type=Path, help="media file or a folder of them")
    ap.add_argument("--edit-dir", type=Path, required=True)
    ap.add_argument("--model", default="large-v3-turbo",
                    help="large-v3-turbo (default) / base / tiny")
    ap.add_argument("--language", default=None, help="e.g. en, zh; omit to auto-detect")
    ap.add_argument("--force", action="store_true", help="ignore the cache")
    a = ap.parse_args()

    if not a.target.exists():
        sys.exit(f"not found: {a.target}")
    srcs = (sorted(p for p in a.target.iterdir() if p.suffix.lower() in MEDIA_EXT)
            if a.target.is_dir() else [a.target])
    if not srcs:
        sys.exit("no media files in that folder")

    outs = [transcribe_one(s, a.edit_dir, a.model, a.language, a.force) for s in srcs]
    print(json.dumps({"transcripts": [str(p) for p in outs]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
