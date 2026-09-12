#!/usr/bin/env python3
"""check - hold the records to the spec. The script does not care which model wrote them.

    check.py check <file>                          one file (score or dispersion)
    check.py pair --scores DIR --dispersions DIR   cross-check the two archives
    check.py gap --scores DIR [--days N]           how long since the last record

Paths come from the flags or from UNKNOWN_FIRST_SCORES / UNKNOWN_FIRST_DISPERSIONS in
the environment. Nothing is hard-coded: this archive lives wherever you keep it.

Exit codes: 0 = everything passed, 1 = at least one failure. Warnings never fail the run;
they are the things a person has to judge.

What it can and cannot do: it checks the literal surface - required sections, a score that
is not a summary, a real anchor path, banned phrasings. It cannot tell you whether the
piece handed anyone anything they did not have. That verdict is not automatable, and
pretending otherwise is how a spec turns into a template.
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

# Capability disclaimers. A dispersion guesses in the voice of a guess; it never
# excuses itself for being a model.
DISCLAIMERS = [
    "beyond my capabilities", "beyond my knowledge", "as an ai",
    "i cannot determine", "i am unable to", "i don't have the ability",
    "超出我的能力", "超出我的知识", "无法确定", "作为ai", "我没有能力",
]  # matched case-insensitively, so keep them lowercase and unique

# Audit vocabulary. Verification output goes into the reply, not into the piece.
AUDIT_WORDS = ["VERIFIED", "CONFIRMED", "PASS ✅", "✅", "已确认", "核实通过"]

# Spec process words: written for whoever is writing, never for the reader.
PROCESS_WORDS = [
    "go back to the scene", "change layer", "hang it back", "out of reach",
    "free zone", "回现场", "换层", "意近", "够不到", "改看",
]

NAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}__.+\.md$")

# Section headings are matched by keyword so a record may be written in either language.
SECTIONS = [
    (("trajectory", "轨迹"), "trajectory"),
    (("arrival", "抵达"), "arrival"),
    (("score", "谱"), "score"),
    (("key lines", "quotes", "调", "原话"), "key lines"),
    (("known", "分界"), "known/unknown table"),
    (("openings", "弥补"), "openings"),
]


def fname_date(p: Path) -> date | None:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})__", p.name)
    return date(int(m[1]), int(m[2]), int(m[3])) if m else None


def sections(text: str) -> list[tuple[str, str]]:
    out, cur, buf = [], None, []
    for line in text.split("\n"):
        if line.startswith("## "):
            if cur is not None:
                out.append((cur, "\n".join(buf)))
            cur, buf = line[3:].strip(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out.append((cur, "\n".join(buf)))
    return out


def find_sec(secs, *keywords) -> str | None:
    hit = [body for title, body in secs
           if any(k.lower() in title.lower() for k in keywords)]
    return "\n".join(hit) if hit else None


# --------------------------------------------------------------------------- score
def check_score(p: Path, errors: list[str], warnings: list[str]) -> None:
    text = p.read_text(encoding="utf-8")
    if not NAME_RE.match(p.name):
        errors.append(f"{p.name}: filename must be YYYY-MM-DD__topic.md")
        return
    d = fname_date(p)
    if d and d > date.today():
        errors.append(f"{p.name}: dated in the future")

    head = "\n".join(text.split("\n")[:40])
    if not re.search(r"(?i)\bmodel\b|模型", head):
        errors.append(f"{p.name}: no model named in the first 40 lines")

    secs = sections(text)
    for keys, label in SECTIONS:
        if find_sec(secs, *keys) is None:
            errors.append(f"{p.name}: missing the '{label}' section")

    score = find_sec(secs, "score", "谱")
    quotes = find_sec(secs, "key lines", "quotes", "调", "原话")
    if score and quotes and len(score) < len(quotes):
        errors.append(f"{p.name}: the score ({len(score)} chars) is shorter than the quoted "
                      f"lines ({len(quotes)}) - the score is the substance; this looks summarised")

    openings = find_sec(secs, "openings", "弥补") or ""
    for bad in DISCLAIMERS + ["not verified", "would need checking", "需要核实"]:
        if bad.lower() in openings.lower():
            errors.append(f"{p.name}: an opening carries the disclaimer '{bad}' - "
                          f"an opening is a coordinate, not an excuse")
            break

    for m in re.finditer(r"data:image/png;base64,([A-Za-z0-9+/=]{24})", text):
        try:
            if base64.b64decode(m[1])[:4] != b"\x89PNG":
                errors.append(f"{p.name}: embedded base64 is not a PNG")
        except Exception:
            errors.append(f"{p.name}: embedded base64 will not decode")
    if find_sec(secs, "map", "地图") and "data:image/png;base64," not in text:
        warnings.append(f"{p.name}: has a map section but no embedded data URI")


# ---------------------------------------------------------------------- dispersion
def check_dispersion(p: Path, errors: list[str], warnings: list[str],
                     scores_dir: Path | None) -> None:
    text = p.read_text(encoding="utf-8")
    if not NAME_RE.match(p.name):
        errors.append(f"{p.name}: filename must be YYYY-MM-DD__topic.md")
        return
    if (d := fname_date(p)) and d > date.today():
        errors.append(f"{p.name}: dated in the future")

    for bad in DISCLAIMERS:
        if bad.lower() in text.lower():
            errors.append(f"{p.name}: carries the capability disclaimer '{bad}'")

    # The anchor: one line saying what was reopened, carrying a path that exists.
    anchor_lines = [l for l in text.split("\n")
                    if re.search(r"(?i)reopened|anchor|重看", l)]
    paths = [m for l in anchor_lines for m in re.findall(r"((?:/|\./|~/)[^\s`\"'）)]+)", l)]
    if not anchor_lines:
        errors.append(f"{p.name}: no anchor line - nothing proves the jump started on the ground")
    elif not paths:
        errors.append(f"{p.name}: the anchor names no path - it must point at real material")
    else:
        resolved = [Path(os.path.expanduser(x)) for x in paths]
        if not any(x.exists() for x in resolved):
            errors.append(f"{p.name}: the anchor path does not exist (moved, or never there): "
                          f"{paths[0]}")
        if scores_dir is not None:
            own_score = (scores_dir / f"{p.stem}.md").resolve()
            for x in resolved:
                if x.resolve() == own_score:
                    errors.append(f"{p.name}: the anchor points back at this session's own "
                                  f"score - returning to the scene means external material, "
                                  f"not reopening your own reasoning")
                    break

    for w in AUDIT_WORDS:
        if w in text:
            errors.append(f"{p.name}: carries audit vocabulary '{w}' - "
                          f"verification output belongs in the reply, not in the piece")

    body = text.split("---\nannotation")[0]
    body = "\n".join(l for l in body.split("\n")
                     if not re.search(r"(?i)reopened|anchor|重看", l))
    hits = [w for w in PROCESS_WORDS if w.lower() in body.lower()]
    if hits:
        warnings.append(f"{p.name}: the body uses spec process words {hits} - "
                        f"the method is not supposed to be visible; check for template-filling")

    if scores_dir is not None and not (scores_dir / f"{p.stem}.md").exists():
        warnings.append(f"{p.name}: no score of the same name - a dispersion with no "
                        f"pursuit behind it, or the pair has drifted apart")


# ---------------------------------------------------------------------- subcommands
def cmd_check(a) -> int:
    p = Path(a.file)
    if not p.exists():
        print(f"not found: {p}")
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    kind = a.kind or ("dispersion" if _in(p, a.dispersions) else "score")
    (check_dispersion(p, errors, warnings, _dir(a.scores))
     if kind == "dispersion" else check_score(p, errors, warnings))
    return _report(kind, errors, warnings)


def cmd_pair(a) -> int:
    scores, disp = _dir(a.scores), _dir(a.dispersions)
    if not scores or not disp:
        print("pair needs --scores and --dispersions (or the env vars)")
        return 1
    errors: list[str] = []
    warnings: list[str] = []
    s = {f.stem for f in scores.glob("*.md")}
    d = {f.stem for f in disp.glob("*.md")}
    for stem in sorted(s - d):
        warnings.append(f"{stem}: a score with no dispersion - the pursuit was recorded, "
                        f"the whip never cracked")
    for stem in sorted(d - s):
        warnings.append(f"{stem}: a dispersion with no score")
    for f in sorted(scores.glob("*.md")):
        check_score(f, errors, warnings)
    for f in sorted(disp.glob("*.md")):
        check_dispersion(f, errors, warnings, scores)
    print(f"{len(s)} scores, {len(d)} dispersions, {len(s & d)} paired")
    return _report("pair", errors, warnings)


def cmd_gap(a) -> int:
    scores = _dir(a.scores)
    if not scores:
        print("gap needs --scores (or UNKNOWN_FIRST_SCORES)")
        return 1
    files = sorted(scores.glob("*.md"))
    dates = sorted(x for x in (fname_date(f) for f in files) if x)
    if not dates:
        print("no records yet")
        return 0
    gap = (date.today() - dates[-1]).days
    print(f"most recent record: {dates[-1]} ({gap} days ago)")
    window = date.today() - timedelta(days=a.days)
    recent = [x for x in dates if x >= window]
    print(f"last {a.days} days: {len(recent)} record(s)")
    print("This only counts. Whether the quiet stretch should have been quiet is your call.")
    return 0


def _dir(x) -> Path | None:
    return Path(os.path.expanduser(x)) if x else None


def _in(p: Path, folder) -> bool:
    d = _dir(folder)
    return bool(d) and d.resolve() in p.resolve().parents


def _report(what: str, errors: list[str], warnings: list[str]) -> int:
    for w in warnings:
        print(f"warn · {w}")
    for e in errors:
        print(f"FAIL · {e}")
    if not errors and not warnings:
        print(f"ok · {what}: nothing the machine can see is wrong")
    elif not errors:
        print(f"ok · {what}: no failures ({len(warnings)} thing(s) for a person to judge)")
    return 1 if errors else 0


def main() -> int:
    # The folder flags are accepted on either side of the subcommand: putting them
    # only in front is the kind of CLI that makes people think the tool is broken.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--scores", default=os.environ.get("UNKNOWN_FIRST_SCORES"))
    common.add_argument("--dispersions", default=os.environ.get("UNKNOWN_FIRST_DISPERSIONS"))

    ap = argparse.ArgumentParser(description="check records against the unknown-first spec",
                                 parents=[common])
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="one file", parents=[common])
    c.add_argument("file")
    c.add_argument("--kind", choices=["score", "dispersion"],
                   help="default: inferred from which folder it is in")
    c.set_defaults(fn=cmd_check)

    p = sub.add_parser("pair", help="cross-check both archives", parents=[common])
    p.set_defaults(fn=cmd_pair)

    g = sub.add_parser("gap", help="how long since the last record", parents=[common])
    g.add_argument("--days", type=int, default=30)
    g.set_defaults(fn=cmd_gap)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
