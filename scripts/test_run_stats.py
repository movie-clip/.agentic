#!/usr/bin/env python3
"""Tests for run_stats.py. Run: python scripts/test_run_stats.py"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_stats  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: object = "") -> None:
    results.append((name, bool(cond), str(detail)))
    print(("  ok   " if cond else "  FAIL ") + name
          + ("" if cond else f"\n       {detail}"))


LEDGER = """# RUN demo
project:      demo
status:       CLOSED
budget:       6 - build 2 + gates 2 + fix 1 + re-run 1
spent:        6

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | backend | - | engineer | sonnet | 01-backend.md | DONE | - |
| 02 | test | - | test-engineer | sonnet | 02-test.md | PARTIAL | - |
| 03 | integration | INTEGRATION | tech-lead | opus | 03-integration.md | DONE | CHANGES_REQUESTED |
| 04 | backend | - | engineer | sonnet | 04-backend.md | LOST | - |
| 05 | backend | - | engineer | sonnet | 05-backend.md | DONE | - |
| 06 | integration | INTEGRATION | tech-lead | opus | 06-integration.md | DONE | PASS |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 03 asked for a fix | budget 4 -> 5 |
| v3 | 04 was lost | budget 5 -> 6 |
"""

DECISIONS = """# Decisions - demo

## D-1 - framing
ruling:         "yes"

## D-2 - framing
ruling:         not objected (assumed list, round 1)

## D-3 - build
ruling:         "option b"
"""


def fixture(replans: bool = True) -> Path:
    project = Path(tempfile.mkdtemp())
    run = project / "runs" / "demo"
    (run / "cr").mkdir(parents=True)
    text = LEDGER if replans else LEDGER.split("## Replans")[0]
    (run / "run.md").write_text(text, encoding="utf-8")
    (run / "decisions.md").write_text(DECISIONS, encoding="utf-8")
    (run / "cr" / "CR-1.md").write_text("CHANGE REQUEST CR-1", encoding="utf-8")
    return project


print("A - one run's numbers come off the ledger")
project = fixture()
ledgers = run_stats.find_ledgers([project])
check("a folder holding `runs/` yields its ledgers", len(ledgers) == 1, ledgers)
s = run_stats.run_stats(ledgers[0])
check("intake is the first re-plan's old value, not the rewritten budget",
      s["intake"] == 4, s["intake"])
check("over is spent minus intake", s["over"] == 2, s["over"])
check("re-plans are counted", s["plans"] == 2, s["plans"])
check("a not-objected ruling counts as assumed, the rest as asked",
      (s["asked"], s["assumed"]) == (2, 1), (s["asked"], s["assumed"]))
check("change requests are the files in cr/", s["cr"] == 1, s["cr"])
check("CHANGES_REQUESTED on a gate lane is a gate FAIL",
      s["gate_fail"] == 1, s["gate_fail"])
check("PARTIAL and LOST are slots not DONE", s["not_done"] == 2, s["not_done"])

print("B - a run that never re-planned")
s = run_stats.run_stats(run_stats.find_ledgers([fixture(replans=False)])[0])
check("intake falls back to `budget:`", s["intake"] == 6, s["intake"])
check("and over is zero", s["over"] == 0, s["over"])

print("B2 - a ledger that `ledger.py` stamped")
project = fixture()
led = project / "runs" / "demo" / "run.md"
led.write_text(LEDGER.replace("spent:        6", "intake:       3\n"
                              "network:      9.9.9\nspent:        6"),
               encoding="utf-8")
s = run_stats.run_stats(led)
check("`intake:` wins over the re-plan chain", s["intake"] == 3, s["intake"])
check("`network:` is reported", s["network"] == "9.9.9", s["network"])
check("an unstamped run reports no version",
      run_stats.run_stats(ledgers[0])["network"] is None)

print("C - the ways a path can be given")
check("a run dir itself", len(run_stats.find_ledgers(
    [ledgers[0].parent])) == 1)
corpus = Path(tempfile.mkdtemp())
(corpus / "p" / "runs" / "r").mkdir(parents=True)
(corpus / "p" / "runs" / "r" / "run.md").write_text(LEDGER, encoding="utf-8")
check("a corpus root, one level above the projects",
      len(run_stats.find_ledgers([corpus])) == 1)

print("D - the lane table")
lanes = {ln["lane"]: ln for ln in run_stats.lane_table(
    [run_stats.run_stats(ledgers[0])])}
check("a gate lane carries PASS and FAIL counts",
      (lanes["integration"]["pass"], lanes["integration"]["fail"]) == (1, 1),
      lanes["integration"])
check("a build lane carries neither", lanes["backend"]["pass"] is None)
check("not-DONE slots land on the lane that had them",
      lanes["backend"]["not_done"] == 1 and lanes["test"]["not_done"] == 1)

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
