#!/usr/bin/env python3
"""_env - build a tool venv on demand and re-exec into it.

Each script declares only the packages it actually needs; missing ones are
installed, installed ones are not reinstalled. First run takes 10-30s, later
runs are instant. The venv lives next to the skill, so it travels with it and
can be deleted at any time (it rebuilds itself).

    from _env import ensure; ensure("opentimelineio", "opentimelineio-plugins")

Three failure modes this guards against, all observed in practice:
  - Checking only "does the venv exist" is not enough: the script that ran
    first installed A, the next one needs B, the directory already exists, and
    the re-exec lands in an ImportError. So the ledger tracks *packages*.
  - A ledger alone is still not enough: when the system interpreter moves
    (3.9 -> 3.11 after a toolchain upgrade) the `bin/python` symlink and the
    ledger both survive, but site-packages has moved. So the ledger's first
    line pins the interpreter version and a mismatch forces a rebuild.
  - Two scripts starting at once both pass `not py.exists()` and build the
    venv twice. A file lock serialises the first run.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

VENV = Path(__file__).resolve().parent.parent / ".venv-rough-cut"
LEDGER = VENV / "installed.txt"
MARK = "_ROUGH_CUT_VENV"


def _pyver() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def _installed() -> set[str]:
    if not LEDGER.exists():
        return set()
    lines = LEDGER.read_text().split()
    if not lines or lines[0] != f"py={_pyver()}":      # interpreter moved, ledger void
        return set()
    return set(lines[1:])


def _write(pkgs: set[str]) -> None:
    tmp = LEDGER.with_suffix(".tmp")
    tmp.write_text("\n".join([f"py={_pyver()}", *sorted(pkgs)]))
    os.replace(tmp, LEDGER)                            # atomic: never a half ledger


def ensure(*pkgs: str) -> None:
    py = VENV / ("Scripts" if os.name == "nt" else "bin") / (
        "python.exe" if os.name == "nt" else "python")
    if os.environ.get(MARK):
        return
    VENV.parent.mkdir(parents=True, exist_ok=True)
    lock_path = VENV.parent / ".env.lock"
    with open(lock_path, "w") as fh:
        _lock(fh)
        if py.exists() and not _installed() and LEDGER.exists():
            print("interpreter changed, rebuilding tool venv ...", file=sys.stderr)
            subprocess.run([sys.executable, "-c",
                            f"import shutil;shutil.rmtree({str(VENV)!r},ignore_errors=True)"])
        if not py.exists():
            print(f"first run, creating tool venv at {VENV} ...", file=sys.stderr)
            subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
            subprocess.check_call([str(py), "-m", "pip", "-q", "install", "--upgrade", "pip"])
        have = _installed()
        missing = [p for p in pkgs if p not in have]
        if missing:
            print(f"installing {' '.join(missing)} ...", file=sys.stderr)
            subprocess.check_call([str(py), "-m", "pip", "-q", "install", *missing])
            _write(have | set(missing))
    os.environ[MARK] = "1"
    os.execv(str(py), [str(py), *sys.argv])


def _lock(fh) -> None:
    """Exclusive lock where the platform has one; a no-op elsewhere."""
    try:
        import fcntl
        fcntl.flock(fh, fcntl.LOCK_EX)
    except ImportError:                                # Windows: best effort
        pass
