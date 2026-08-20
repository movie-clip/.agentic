#!/usr/bin/env python3
"""Derive what a run cost from its ledger, and check the Cost block agrees.

    python scripts/run_cost.py runs/<run-id>/          # one run
    python scripts/run_cost.py runs/                   # every run, newest last

Exit 0 = the ledger's Cost block matches the Artifacts and Rounds tables.
Exit 1 = they disagree, or a dispatch has no model recorded.

Why this exists: until v0.4.1 every lane ran on whatever the main session
happened to be, and nothing recorded it. A cost tally the orchestrator writes
from memory at close-out is the same class of artifact as a report nobody
validates — it drifts, and the drift is invisible precisely because nobody
re-derives it. So the numbers come from the rows, not from the tally.

Dependency-free by design: it runs anywhere the network runs.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

# Escalations are marked `opus↑` in the model column. Both the plain arrow and
# an ASCII fallback are accepted; the model name is what matters.
ESCALATED = ("↑", "^")


def _table(text: str, heading: str) -> list[list[str]]:
    """Rows of the markdown table under `## <heading>`, header/rule dropped."""
    m = re.search(rf"^## {re.escape(heading)}[ \t]*$", text, re.M)
    if not m:
        return []
    rows: list[list[str]] = []
    for ln in text[m.end():].splitlines():
        s = ln.strip()
        if s.startswith("## "):
            break
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c) <= {"-", ":"} and c for c in cells):
            continue          # the |---|---| rule
        rows.append(cells)
    return rows[1:] if rows else []   # drop the header row


def _model(cell: str) -> tuple[str, bool]:
    up = any(a in cell for a in ESCALATED)
    name = cell
    for a in ESCALATED:
        name = name.replace(a, "")
    return name.strip().lower(), up


def derive(run_dir: Path) -> tuple[dict, list[str]]:
    """Return (metrics, problems) for one run directory."""
    ledger = run_dir / "run.md"
    if not ledger.is_file():
        return {}, [f"no run.md in {run_dir}"]
    text = ledger.read_text(encoding="utf-8")
    problems: list[str] = []

    arts = _table(text, "Artifacts")
    by_model: Counter[str] = Counter()
    escalations = 0

    # A ledger written before v0.4.1 has no `model` column at all. That is one
    # fact about the run, not one fact per row — saying it sixteen times buries
    # everything else this script found.
    legacy = bool(arts) and all(len(r) == 7 for r in arts)
    if legacy:
        problems.append("ledger predates the `model` column (v0.4.1) - "
                        "dispatches and rounds are still counted, model spread "
                        "is unknowable for this run")
        arts_ok = []
    else:
        arts_ok = arts

    for row in arts_ok:
        # | # | lane | mode | agent | model | artifact | status | verdict |
        if len(row) < 8:
            problems.append(f"dispatch {row[0] if row else '?'} has "
                            f"{len(row)} columns, expected 8 - "
                            "the `model` column is missing from this row")
            continue
        name, up = _model(row[4])
        if not name or name in {"—", "-", ""}:
            problems.append(f"dispatch {row[0]} ({row[1]}) records no model - "
                            "an unrecorded model is an unmeasurable run")
            continue
        by_model[name] += 1
        escalations += up

    rounds = _table(text, "Rounds")
    metrics = {
        "dispatches": len(arts),
        "rounds": len(rounds),
        "by_model": by_model,
        "escalations": escalations,
    }

    # Cross-check the human-written Cost block, when there is one.
    cost = {r[0].strip().lower(): r[1].strip()
            for r in _table(text, "Cost") if len(r) >= 2}
    if cost:
        for key, got in (("dispatches", metrics["dispatches"]),
                         ("rounds", metrics["rounds"])):
            if key in cost and cost[key].isdigit() and int(cost[key]) != got:
                problems.append(f"Cost says {key} {cost[key]}, rows say {got}")
        if "by model" in cost:
            stated = dict(re.findall(r"([a-z0-9.\-]+)\s+(\d+)", cost["by model"], re.I))
            for m, n in by_model.items():
                if m in stated and int(stated[m]) != n:
                    problems.append(f"Cost says {m} {stated[m]}, rows say {n}")
    elif arts and not legacy:
        problems.append("no `## Cost` block - fill it at close-out, even on a "
                        "one-dispatch express run")

    return metrics, problems


def report(run_dir: Path) -> bool:
    metrics, problems = derive(run_dir)
    print(f"\n{run_dir.name}")
    if metrics:
        bm = metrics["by_model"]
        spread = " · ".join(f"{m} {n}" for m, n in bm.most_common()) or "not recorded"
        print(f"  dispatches   {metrics['dispatches']}")
        print(f"  rounds       {metrics['rounds']}")
        print(f"  by model     {spread}")
        if metrics["escalations"]:
            print(f"  escalations  {metrics['escalations']}")
    for p in problems:
        print(f"  - {p}")
    return not problems


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    target = Path(argv[1])
    if not target.exists():
        print(f"no such path: {target}")
        return 2

    runs = ([target] if (target / "run.md").is_file()
            else sorted(p for p in target.iterdir()
                        if p.is_dir() and (p / "run.md").is_file()))
    if not runs:
        print(f"no run ledgers under {target}")
        return 2

    ok = True
    for r in runs:
        ok &= report(r)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
