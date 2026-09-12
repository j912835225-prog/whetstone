# claude-skills

[![English](https://img.shields.io/badge/English-current-1B3FA0?style=for-the-badge)](README.md)
[![中文](https://img.shields.io/badge/中文-切换-C1352C?style=for-the-badge)](README.zh.md)
[![Licence](https://img.shields.io/badge/licence-CC%20BY--NC--SA%204.0-2A2A2D?style=for-the-badge)](LICENSE)

**English** · [中文说明请点这里 / Chinese version here](README.zh.md)

Nine skills for [Claude Code](https://claude.com/claude-code), distilled from a working
skill library. Each one is a task class, not a preference: a procedure a stranger can run
on their own material, with the traps named and the costs stated.

> **Built for Claude Code. Only Claude Code.** These use Claude Code's skill format and
> its loading behaviour, and that is the only setup they are tested on. If you run another
> agent and want to use them, you are welcome to — but adapting them is your job, not
> something this repo claims to support.

> **Licence in one line:** free to use, adapt and share for **non-commercial** purposes,
> with attribution, under the same licence. **Commercial use is not permitted.**
> Details in [Licence](#licence).

![rough-cut](posters/png/rough-cut.png)

## Install

```bash
git clone https://github.com/j912835225-prog/claude-skills.git
cp -r claude-skills/rough-cut ~/.claude/skills/      # one skill
cp -r claude-skills/*/ ~/.claude/skills/             # all nine
```

`~/.claude/skills/` makes a skill available everywhere; `.claude/skills/` inside a
repository scopes it to that project. Both paths are Claude Code's. Each folder is self-contained - there are no
cross-references between them, so take only what you want. Restart Claude Code, or start a
new session, and ask for the kind of work the skill covers; it loads itself when the
request matches.

## The nine

| Skill | What it is for | Language |
|---|---|---|
| [**rough-cut**](rough-cut/) | Cut unscripted footage — interviews, podcasts, screen recordings, VO takes — by reading a word-level transcript instead of looking at frames. Seven working scripts and a self-test | English |
| [**audit-anything**](audit-anything/) | Audit a deliverable, an action, or a chain of reasoning, and come out with a verdict rather than a list of observations. Evidence hierarchy, three tracks, verdict tiers, auditor self-audit | English |
| [**visual-contract**](visual-contract/) | State what you are and are not borrowing before designing, so a reference screenshot or the word "modern" cannot quietly overwrite a design language. Anti-slop avoid list and a drift check | English |
| [**tame-sprawl**](tame-sprawl/) | Tidy a sprawling docs set, skill library, prompt collection or config pile — four steps that may not be skipped, and an acceptance test that is not a file count | English |
| [**code-print**](code-print/) | Draw printed matter in code instead of generating it — posters, covers, zine pages, tickets, labels. Vector out, type that is never wrong, same input same file. Two drawing engines, a worked example, a self-test | English |
| [**unknown-first**](unknown-first/) | A standing obligation to hand the person something they did not know, the known/unknown map that records it, and two archives a future model instance can read. Ships a checker | English |
| [**chinese-prose**](chinese-prose/) | 中文成稿检查表：场合与语气档、大纲三问、删改判据、用字四查、交前五挑错、评稿六看 | 中文 |
| [**script-check**](script-check/) | 剧本与叙事的结构与对白检查表：一人一事、伏笔成对、对白八查、三处收口、旧本翻新 | 中文 |
| [**classical-chinese-translation**](classical-chinese-translation/) | 古籍整本译白话的工序与防漂移闸：底本纪律、回目交叉核、四条漂移触发点、pandoc 出书、收工三验 | 中文 |

Language per skill is a decision, not a default. The three Chinese ones encode Chinese
writing and translation craft; translating them would flatten what they are about. The
other six apply to any material, so they are in English. A Chinese reader who wants the
English six explained in Chinese will find that in [README.zh.md](README.zh.md).

## What these have in common

- **A trigger a stranger actually has.** Not "always be careful" — a specific kind of job.
- **Traps, not principles.** Every rule that cost something says what it cost, in a form
  you can check against your own material.
- **Stated limits.** Where a skill cannot do something it says so instead of hedging:
  `rough-cut` has no speaker diarisation, `audit-anything` does not rule on taste.
- **Nothing hosted, nothing private.** No API keys, no accounts, no paths into anyone
  else's machine, no calls home.

## Verifying the ones with code

Three skills ship executables, and each can prove it still works:

```bash
python3 rough-cut/scripts/selftest.py          # 21 assertions, builds its own fixture
python3 code-print/scripts/selftest.py         # 22 assertions, draws its own test piece
python3 unknown-first/scripts/check.py --help  # checks records against the spec
```

Verified on macOS, on both a fully provisioned interpreter and an empty `python -m venv`.
Linux and Windows are untested — reports welcome. `rough-cut` needs `ffmpeg`; its
transcription step needs `openai-whisper`, which is the one manual install because it
pulls in PyTorch.

## Posters

Every skill has a landscape poster in [posters/](posters/), ready to use as a README
header or a social card. They are drawn by `code-print`'s own engines - the same
`woodcut.py` and `printlab.py` that ship inside that skill - not generated by an image
model. Each build script carries its recipe in its docstring.

```bash
cd posters && python3 build_rough_cut.py && rsvg-convert -w 1600 -h 900 rough-cut.svg -o png/rough-cut.png
```

## Licence

**[CC BY-NC-SA 4.0](LICENSE)** (Attribution — NonCommercial — ShareAlike).

You may: use these skills in your own work, change them, and pass them on.
You must: credit the source, and license what you pass on under the same terms.
You may not: **use them commercially** — no selling them, no bundling them into a paid
product or a paid service, no using them as part of a commercial offering.

Not sure whether your use is commercial? Ask before you ship. Because commercial use is
excluded, this is *source-available*, not open source in the OSI sense — a deliberate
choice, stated plainly rather than hidden behind a familiar badge.

**Third-party credit.** `rough-cut`'s transcript-first approach was informed by the
open-source [video-use](https://github.com/browser-use/video-use) project; the
implementation here is independent. `code-print` took the recipe-before-drawing idea, the
per-plate job rule and one-focus-one-area-of-air from
[mono-color-skill](https://github.com/yanliudesign/mono-color-skill) and rewrote them.
`unknown-first` builds on Korzybski's map/territory distinction and inverts the direction of
Thariq Shihipar's *A Field Guide to Fable: Finding Your Unknowns* (Anthropic, 2026). The Chinese three draw on
classical Chinese criticism (Liu Xie, Li Yu) and `code-print`'s audit section on Fu Shan's
four negations — all long in the public domain. No third-party example images, fonts or
datasets are redistributed here.

## Contributing

If a rule costs you something on real material, change it and say why. Rules that cannot
survive someone else's material do not deserve to be in a shared skill. Issues and pull
requests welcome; by contributing you agree your contribution is licensed the same way.
