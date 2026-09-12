---
name: rough-cut
description: Cut unscripted footage - interviews, podcasts, screen recordings, multiple VO takes, travel clips, meeting or livestream recordings - into a rough cut by reading a word-level transcript instead of looking at frames. Use when the user drops a folder of raw material and asks what to keep, where to cut, which take to use, how to strip filler, or asks to turn a recording into a short piece. Produces an EDL, a rendered mp4, and optionally an editable NLE timeline. Not for scripted material where the cut points are already known.
license: CC-BY-NC-SA-4.0
version: 1.0.0
---

# rough-cut

**One line:** when footage has no script, the cut points have to be found in the material, and the way to find them is to read a word-level transcript, not to look at thirty thousand frames.

## Does this apply?

| What you have | Where to go |
|---|---|
| Cut points are already known (storyboard locked, generated shots, TTS timing) | Not this skill - assemble to the plan you already have |
| No script; the cut points have to be found (interview, podcast, screen recording, VO takes, travel, meeting, livestream) | This skill |
| A script exists, but the footage is several live takes and one has to be chosen | This skill for take selection; the assembly rules below still apply |

The test is one question: **are the cut points known, or do they have to be found?**

## 1. Why not look at frames

Thirty thousand frames at roughly 1.5k tokens each is 45M tokens of noise, and after all of it the model still does not know where to cut - because the cut information is in the **audio**, not the picture.

So the toolchain has two layers:

1. **Text layer (always on).** `takes_packed.md` - every word of every source, with `[start-end]` and a speaker per line, compressed into tens of KB. Picking cut points is done here.
2. **Image layer (on demand).** `timeline_view` renders one PNG: filmstrip + waveform band + highlighted silence gaps + word labels. Call it **at decision points only** - can I cut in this pause, which of these two takes, did that cut land. It is not a scanning tool; rendering image after image to browse footage defeats the entire point.

## 2. The process

```
1 survey    ffprobe each source -> transcribe.py over the folder -> pack.py -> read takes_packed.md
            (many clips, little speech, need shot changes first? run shots.py)
2 pre-read  read the transcript once; note stumbles, repeats, dead passages, the peaks you must keep
3 talk      say in plain words what you see, and ask: what kind of piece, target length,
            aspect ratio, pace, must-keeps, must-cuts
4 plan      4-8 sentences: structure, which takes, how you will cut, estimated length - then wait
5 execute   write edl.json (call timeline_view where you are unsure) -> render.py
            want to keep editing by hand instead? -> to_nle.py
6 self-check verify every cut against the rendered file (section 5) before showing anyone
7 record    write <footage>/edit/project.md
```

Step 4's wait is not optional. **No cutting before the plan is agreed.**

## 3. The scripts (`scripts/`, all local, no API cost)

| Script | What it does | Notes |
|---|---|---|
| `transcribe.py <file\|dir> --edit-dir <dir>/edit` | word-level transcription | local `openai-whisper`, default `large-v3-turbo`; `--model base` when in a hurry; cached by mtime+size, unchanged sources are never re-transcribed |
| `pack.py --edit-dir <dir>/edit` | transcripts -> `takes_packed.md` | breaks a line on a gap >= 0.5s or a speaker change, and prints the gap at the end of the line |
| `timeline_view.py <src> <start> <end> -o x.png [--words w.json]` | one composite image | `--gap` sets the silence threshold (default 0.4s); audio-only sources skip the filmstrip |
| `render.py <edl.json> -o out.mp4 [--preview]` | EDL -> finished cut | assembly rules in section 4 |
| `shots.py <video> [--edl edl.json]` | video -> shot boundaries (frame precise) | start here when the material is a pile of clips with no speech. **It talks back**: long shots get "a machine cannot tell you what happens in here"; and if the boundary count changes across 0.75x/1x/1.3x of the threshold it says so - when it does, those boundaries are not settled |
| `to_nle.py <edl.json> -o name` | EDL -> editable timeline (FCP7 XML + CMX3600) | same EDL as `render.py`. Use `render.py` to deliver, this to keep cutting in DaVinci Resolve / Premiere / Final Cut. Let OTIO write the timecode; never hand-assemble it |
| `selftest.py` | proves the toolchain still works | zero footage: builds its own fixture. **Run it after changing anything in `scripts/`, or after a long gap.** `--with-whisper` adds the ASR leg. The `.venv-rough-cut` directory it creates can be deleted at any time; it rebuilds in about 25s |

Requirements: `ffmpeg`/`ffprobe` on PATH and Python 3.9+. `shots.py`, `to_nle.py` and `timeline_view.py` install what they need into a local venv on first run. `transcribe.py` is the exception - install `openai-whisper` yourself, because it pulls in PyTorch and that should be your decision.

## 4. Assembly rules (each one paid for)

1. **Extract each segment, then join with the concat demuxer and `-c copy`.** Not the concat *filter* - the filter loops the first segment's audio across the whole file, and the picture gives you no hint that it happened.
2. **60ms `afade` at both ends of every segment.** Not `acrossfade`. A hard cut at a segment boundary pops.
3. **`loudnorm=I=-16:TP=-1.5:LRA=11` over the whole file, and mux with `-ar 48000`.** loudnorm raises the sample rate to 192k; without the explicit rate the output lands at 96k AAC.
4. **Pin frame rate and dimensions per segment.** Mixed sources (30fps + 60fps) break `-c copy`.
5. **Never cut mid-word.** Snap every edge to a transcript word boundary.
6. **Leave 30-200ms of padding at each edge.** ASR timestamps drift 50-100ms; the padding absorbs it. Tight for fast pacing, loose for a cinematic feel.
7. **Gaps >= 400ms are the cleanest cut points.** 150-400ms sentence boundaries deserve one `timeline_view` look. Under 150ms is unsafe - you are probably inside a sentence.
8. **Protect the peaks**: laughs, punchlines, emphasis. If you cut to just after a punchline, carry the reaction - the laugh *is* the beat.
9. **Leave breathing room on speaker changes**, typically 400-600ms.
10. **Never reason about audio and picture separately.** Every cut has to work on both tracks.
11. **Subtitles go on last**, after every overlay - otherwise overlays cover them, and it fails silently. Offset SRT into the output timeline: `output_time = word.start - segment.start + segment_position_in_cut`, or the whole file is misaligned.

## 5. Self-check (before anyone sees it)

Against the **rendered file**, not the source, run `timeline_view` at each cut (±1.5s) and look:

1. Does the picture jump or flash? **A composition change is a real cut; a subject snapping back to a previous position is a bad one.**
2. Does the waveform spike or step at the boundary? You should see it **narrow and rise again** - that is the fade working.
3. With overlays: is anything covering the subtitles, is anything misplaced?

Plus: check the first 2s, last 2s, and 2-3 points in between for consistent grading and readability. `render.py` reports `drift_s` (output length vs EDL) - **anything over 0.5s means a segment was truncated**.

**Fix -> re-render -> re-check, three rounds maximum.** If it is not right after three, describe the problem instead of looping.

Whether it *sounds* right is not a machine question. The tools can prove the waveform does not step; they cannot prove the cut feels good.

## 6. EDL format

```json
{
  "version": 1,
  "sources": {"A01": "/abs/path/A01.mp4", "A02": "/abs/path/A02.mp4"},
  "height": 1080,
  "fps": "24/1",
  "grade": "neutral_punch",
  "ranges": [
    {"source": "A01", "start": 2.42, "end": 6.85, "beat": "HOOK",
     "quote": "the transcript line", "reason": "cleanest take; ends at 6.85 to avoid the stumble after it"}
  ]
}
```

`grade` accepts `none` / `neutral_punch` / `warm_cinematic`, or a raw ffmpeg filter string.
`reason` is mandatory - it is the only way to know later why the cut is where it is.

## 7. Known gaps (stated, not hidden)

| Capability | Status |
|---|---|
| Word-level timestamps | Present, local, free |
| **Speaker diarisation** | **Missing.** Every word is labelled `S0`. Multi-person interviews have to be attributed by content |
| **Audio events** (laughter, applause, sighs) | **Missing.** Whisper does not emit them, and they would be the best beat signal there is |
| Filler words | Partial. Whisper tends to clean up filler, so "cut the ums" may not have the material to work with. Unverified |

To close the diarisation gap, pyannote (needs a HuggingFace token) or F0-based segmentation are the usual routes. Ask before adding a dependency of that weight.

One tool that did **not** earn its place: WhisperX as a drop-in accuracy upgrade. Tested on English and Chinese samples it did not beat plain whisper on word timing, and its per-word confidences collapsed toward zero with evenly spaced timestamps - interpolated filler rather than alignment. Measure it on your own material before adopting it; absorb the drift with rule 6 until you have.

## 8. Anti-patterns

- Pre-computing metadata (emotion tags, shot layers, usability scores). Derive at the decision point instead.
- Hand-writing a "highlight score" function. A model picks better than any heuristic you will write.
- Using sentence-level or SRT transcripts. They discard sub-second gaps, and the gaps are the cut points.
- Rendering `timeline_view` repeatedly to browse. It is a decision tool, not a viewer.
- Cutting before the plan is agreed.
- Re-transcribing cached sources.
- Assuming what kind of piece this is. **Look, then ask, then cut.**

---

Licensed CC BY-NC-SA 4.0 — free to use, adapt and share for non-commercial purposes, with attribution, under the same licence. Commercial use is not permitted. The transcript-first approach was informed by the open-source
[video-use](https://github.com/browser-use/video-use) project; this implementation is
independent and runs entirely locally. Assembly rules and thresholds come from
production use - if one of them costs you something, change it and say why.
