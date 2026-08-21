#!/usr/bin/env python3
"""Regression suite for run_cost.py.

    python scripts/test_run_cost.py

No real ledger carries the `model` column yet, so the happy path exists only
here until the first v0.4.1 run. Dependency-free, like the thing it tests.
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_cost as rc

results = []


def check(name, cond, extra=""):
    results.append(cond)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{'' if cond else '  ' + extra}")


def ledger(body: str) -> Path:
    d = Path(tempfile.mkdtemp())
    (d / "run.md").write_text(body, encoding="utf-8")
    return d


HEADER = """# RUN test
status:       CLOSED
route:        full
express:      no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | haiku | 01-scout.md | DONE | — |
| 02 | backend | — | backend-engineer | sonnet | 02-backend.md | DONE | — |
| 03 | quant | AUDIT | quant-analyst | opus | 03-quant.md | DONE | PASS |
"""

ROUNDS = """
## Rounds
| finding | lane | round | of |
|---|---|---|---|
| CR-1 | backend | 1 | 2 |
"""

COST = """
## Cost
| metric | value |
|---|---|
| dispatches | 3 |
| rounds | 1 |
| by model | sonnet 1 · haiku 1 · opus 1 |
"""

print("happy path")
m, p = rc.derive(ledger(HEADER + ROUNDS + COST))
check("no problems", p == [], str(p))
check("dispatches counted", m["dispatches"] == 3, str(m.get("dispatches")))
check("rounds counted", m["rounds"] == 1, str(m.get("rounds")))
check("model spread correct",
      dict(m["by_model"]) == {"haiku": 1, "sonnet": 1, "opus": 1},
      str(dict(m["by_model"])))

print("Cost block disagreeing with the rows is caught")
m, p = rc.derive(ledger(HEADER + ROUNDS + COST.replace("| dispatches | 3 |",
                                                       "| dispatches | 9 |")))
check("wrong dispatch tally flagged", any("dispatches 9" in x for x in p), str(p))
m, p = rc.derive(ledger(HEADER + ROUNDS + COST.replace("sonnet 1", "sonnet 7")))
check("wrong model tally flagged", any("sonnet 7" in x for x in p), str(p))

print("missing and malformed records")
m, p = rc.derive(ledger(HEADER + ROUNDS))
check("missing Cost block flagged", any("no `## Cost`" in x for x in p), str(p))
m, p = rc.derive(ledger(HEADER.replace("| sonnet |", "| — |") + ROUNDS + COST))
check("unrecorded model flagged", any("records no model" in x for x in p), str(p))

print("escalations")
m, p = rc.derive(ledger(HEADER.replace("| sonnet |", "| sonnet↑ |") + ROUNDS + COST))
check("arrow counted as an escalation", m["escalations"] == 1, str(m["escalations"]))
check("arrow does not corrupt the model name", m["by_model"]["sonnet"] == 1,
      str(dict(m["by_model"])))
m, _ = rc.derive(ledger(HEADER.replace("| sonnet |", "| sonnet^ |") + ROUNDS + COST))
check("ascii fallback also counted", m["escalations"] == 1, str(m["escalations"]))

print("legacy ledger says one thing, not one per row")
legacy = HEADER.replace(" model |", " |").replace("|-------|", "") \
               .replace(" haiku |", "").replace(" sonnet |", "").replace(" opus |", "")
m, p = rc.derive(ledger(legacy + ROUNDS))
check("exactly one problem reported", len(p) == 1, f"{len(p)}: {p}")
check("names the missing column", "predates" in p[0], p[0])
check("still counts dispatches", m["dispatches"] == 3, str(m["dispatches"]))

print("edge cases")
m, p = rc.derive(Path(tempfile.mkdtemp()))
check("no run.md is an error", any("no run.md" in x for x in p))
check("nonexistent path exits 2", rc.main(["run_cost.py", "nope"]) == 2)
check("no args exits 2", rc.main(["run_cost.py"]) == 2)

print("the ledger path is accepted, not just the directory holding it")
_d = Path(tempfile.mkdtemp()) / "2026-01-01-a-run"
_d.mkdir()
(_d / "run.md").write_text(HEADER + ROUNDS + COST, encoding="utf-8")
check("run dir exits 0", rc.main(["run_cost.py", str(_d)]) == 0)
check("run.md exits 0 too", rc.main(["run_cost.py", str(_d / "run.md")]) == 0)
check("parent of runs exits 0", rc.main(["run_cost.py", str(_d.parent)]) == 0)
(_d / "01-scout.md").write_text("not a ledger", encoding="utf-8")
check("some other file exits 2, does not traceback",
      rc.main(["run_cost.py", str(_d / "01-scout.md")]) == 2)

n_fail = results.count(False)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
