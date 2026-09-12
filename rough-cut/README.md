# rough-cut

A [Claude Code](https://claude.com/claude-code) skill for cutting **unscripted footage** —
interviews, podcasts, screen recordings, multiple voice-over takes, travel clips, meeting
and livestream recordings — into a rough cut.

The method in one sentence: **when footage has no script, the cut points have to be found in
the material, and the way to find them is to read a word-level transcript, not to look at
thirty thousand frames.**

Sampling frames for a model is enormously expensive and still does not answer the question,
because the cut information lives in the audio. So the agent reads a compressed word-level
transcript as its primary surface, and renders a timeline image only at decision points —
*can I cut in this pause, which of these two takes, did that cut land*.

Everything runs locally: ffmpeg, ffprobe, and OpenAI's open-source Whisper. No hosted
service, no API key, no per-minute cost.

## Install

Copy the `rough-cut` folder into your skills directory:

```bash
cp -r rough-cut ~/.claude/skills/
```

Then ask Claude Code for a rough cut of some footage, or invoke it with `/rough-cut`.
Project-scoped installs go to `.claude/skills/` inside the repo instead.

## Requirements

| Needed for | Requirement |
|---|---|
| everything | `ffmpeg` and `ffprobe` on PATH, Python 3.9+ |
| `transcribe.py` | `openai-whisper` (`pip install openai-whisper`) — the one manual install, because it pulls in PyTorch |
| `shots.py`, `to_nle.py`, `timeline_view.py` | nothing — they build a local venv on first run (`.venv-rough-cut`, deletable; rebuilds in ~25s) |

Verified on macOS, both on a fully-provisioned interpreter and in an empty `python -m venv`
(everything except transcription bootstraps itself). The scripts avoid platform-specific paths (font lookup walks macOS,
Linux and Windows locations, and the venv bootstrapper handles both layouts), but Linux and
Windows are untested — reports welcome.

## Verify it works

```bash
python3 rough-cut/scripts/selftest.py
```

It builds its own six-second fixture and checks 21 assertions with known answers
across `shots`, `to_nle`, `pack`, `timeline_view` and `render` — shot boundaries at the
right frames, EDL timecode in `HH:MM:SS:FF` rather than decimal seconds, segments
butt-joined on the timeline, video and audio tracks both present, the one known silence gap
detected, and render drift under half a second. Add `--with-whisper` to include
transcription (downloads model weights).

If a check fails, do not relax the assertion — find out whether the tool, the invocation or
the environment broke.

## What you get

```
your-footage/
  edit/
    transcripts/*.words.json    word-level timestamps, cached per source
    takes_packed.md             the read surface: every word, with times and gaps
    project.md                  what you decided and why
  edl.json                      the cut
  cut.mp4                       rendered
  cut.xml / cut.edl             optional, to keep editing in an NLE
```

`SKILL.md` carries the full process, the assembly rules (fade lengths, concat demuxer vs
filter, loudness and sample rate, padding around ASR drift), the self-check, the EDL schema,
the known gaps, and the anti-patterns.

## Honest limitations

- **No speaker diarisation.** Every word is labelled `S0`. Multi-person interviews have to
  be attributed by content.
- **No audio-event detection** (laughter, applause, sighs) — which would be the best beat
  signal available.
- **Filler-word removal is unverified**: Whisper tends to clean filler up before you see it.
- **Machines cannot judge whether a cut feels right.** The tools prove the waveform does not
  step at the boundary and the output length matches the plan. The rest is your ears.

## Credit

The transcript-first approach was informed by the open-source
[video-use](https://github.com/browser-use/video-use) project. This implementation is
independent: transcription is local Whisper rather than a paid API, and the assembly rules
and thresholds come from production use.

## License

MIT — see [LICENSE](LICENSE).
