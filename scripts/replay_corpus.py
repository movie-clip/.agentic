#!/usr/bin/env python3
"""Replay `check_report.py` over a fixed corpus of real closed runs.

The unit tests pin the validator against fixtures written to make a point. This
pins it against what runs actually produced: every closed run in `corpus/` is
swept with `--require-heads`, and the exit code and failure lines are compared
with `corpus/baseline.json`. A script change that turns a passing real run into
a failing one, or the reverse, shows up here before it shows up in a live run.

`corpus/` is local and gitignored: run artifacts quote the bound projects'
product and design text, and this repo has a public-facing remote. With no
corpus the replay passes and says so.

  replay_corpus.py                    compare against the baseline; exit 1 on a difference
  replay_corpus.py --record           write the baseline from the current scripts
  replay_corpus.py --add <projectDir> copy that project's CLOSED runs and its profile in

`--add` copies `.md` and `.txt` only (screenshots are most of a run's bytes and
the validator reads none), skips a run already in the corpus, and rewrites the
copied ledger's `project_dir:` to the corpus copy - so the replay reads the
profile snapshot taken with the run, not the live one that keeps changing.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
BASELINE = CORPUS / "baseline.json"
CHECK = ROOT / "scripts" / "check_report.py"
PROFILE = ("project.md", "phases.md")


def runs() -> list[Path]:
    return sorted(p.parent for p in CORPUS.glob("*/runs/*/run.md"))


def sweep(run: Path) -> dict:
    rel = run.relative_to(CORPUS).as_posix()
    proc = subprocess.run(
        [sys.executable, str(CHECK), rel, "--require-heads"],
        cwd=CORPUS, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    lines = [ln.rstrip().replace("\\", "/")
             for ln in proc.stdout.splitlines()
             if ln.startswith("FAIL") or ln.startswith("  - ")]
    return {"exit": proc.returncode, "failures": lines}


def current() -> dict:
    return {r.relative_to(CORPUS).as_posix(): sweep(r) for r in runs()}


def add(project_dir: Path) -> int:
    name = project_dir.resolve().parent.name
    dest = CORPUS / name
    (dest / "runs").mkdir(parents=True, exist_ok=True)
    for f in PROFILE:
        if (project_dir / f).is_file() and not (dest / f).exists():
            shutil.copy2(project_dir / f, dest / f)
    added = 0
    for ledger in sorted(project_dir.glob("runs/*/run.md")):
        text = ledger.read_text(encoding="utf-8")
        if not re.search(r"^status:\s*CLOSED\s*$", text, re.M):
            continue
        out = dest / "runs" / ledger.parent.name
        if out.exists():
            continue
        for src in ledger.parent.rglob("*"):
            if src.suffix in (".md", ".txt") and src.is_file():
                tgt = out / src.relative_to(ledger.parent)
                tgt.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, tgt)
        text = re.sub(r"^(project_dir:\s*).*$",
                      lambda m: m.group(1) + str(dest), text, count=1,
                      flags=re.M)
        (out / "run.md").write_text(text, encoding="utf-8")
        added += 1
    print(f"{name}: {added} run(s) added - re-run with --record once "
          f"you have looked at how they replay")
    return 0


def main(argv: list[str]) -> int:
    if "--add" in argv:
        return add(Path(argv[argv.index("--add") + 1]))
    if not runs():
        print("no corpus - nothing to replay (corpus/ is local, see --add)")
        return 0
    now = current()
    if "--record" in argv:
        BASELINE.write_text(json.dumps(now, indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
        n_fail = sum(1 for v in now.values() if v["exit"])
        print(f"baseline recorded: {len(now)} runs, {n_fail} failing")
        return 0
    if not BASELINE.is_file():
        print("no baseline - run with --record first")
        return 1
    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    diff = 0
    for run in sorted(set(base) | set(now)):
        b, n = base.get(run), now.get(run)
        if b == n:
            continue
        diff += 1
        print(f"CHANGED {run}")
        if b is None:
            print("  not in the baseline - new run, --record to accept it")
            continue
        if n is None:
            print("  in the baseline, gone from the corpus")
            continue
        print(f"  exit {b['exit']} -> {n['exit']}")
        for ln in sorted(set(b["failures"]) - set(n["failures"])):
            print(f"  no longer reported: {ln.strip()}")
        for ln in sorted(set(n["failures"]) - set(b["failures"])):
            print(f"  newly reported:     {ln.strip()}")
    print(f"\n{len(now) - diff}/{len(now)} runs replay as the baseline")
    return 1 if diff else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
