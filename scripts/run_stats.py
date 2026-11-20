#!/usr/bin/env python3
"""What the runs cost and where they bent - read off the ledgers, nothing else.

A ledger ends `spent == budget` because every re-plan rewrites the budget, so a
closed run cannot say by itself whether intake estimated it well. This reads
the figures a ledger does keep and puts them side by side, per run and in
total, so a change to the network can be compared with the runs before it.

  run_stats.py                      the corpus (`corpus/*/runs/*`)
  run_stats.py <path> [<path> ...]  a run dir, a project's `agentic/` folder,
                                    or any folder holding `runs/`
  run_stats.py --json [...]         the same numbers as JSON

Read-only. It writes nothing and judges nothing: a run this cannot parse is
listed with what was missing, not dropped.

Columns, and where each comes from:

  ver       `network:` - the plugin version the run started on, stamped by
            `ledger.py`; `-` on a run older than the stamp
  intake    the budget intake derived - `intake:` where `ledger.py` stamped
            it; on an older run, the old value in the first `## Replans` row,
            or `budget:` itself if the run never re-planned
  spent     `spent:`
  over      spent - intake
  plans     `## Replans` rows
  asked     `decisions.md` entries the human ruled on
  assumed   entries whose ruling is `not objected` (the grill's assumed list)
  CR        files in `cr/`
  gateFAIL  gate-lane rows with verdict FAIL or CHANGES_REQUESTED
  notDONE   rows whose status is PARTIAL, BLOCKED, REFUSED, LOST or INVALID
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_report import (GATE_LANES, _budget_chain, _leading_int,  # noqa: E402
                          _ledger_field, _ledger_table)

ROOT = Path(__file__).resolve().parent.parent
NOT_DONE = ("PARTIAL", "BLOCKED", "REFUSED", "LOST", "INVALID")
GATE_FAIL = ("FAIL", "CHANGES_REQUESTED")


def find_ledgers(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        if (p / "run.md").is_file():
            found.append(p / "run.md")
        elif (p / "runs").is_dir():
            found += sorted((p / "runs").glob("*/run.md"))
        else:
            found += sorted(p.glob("*/runs/*/run.md"))
    return found


def run_stats(ledger: Path) -> dict:
    text = ledger.read_text(encoding="utf-8")
    arts = [r for r in _ledger_table(text, "Artifacts") if len(r) >= 8]
    replans = _ledger_table(text, "Replans")
    budget = _leading_int(_ledger_field(text, "budget"))
    spent = _leading_int(_ledger_field(text, "spent"))
    intake = _leading_int(_ledger_field(text, "intake"))
    if intake is None:
        intake = _budget_chain(replans)[0] if replans else budget
    dec = ledger.parent / "decisions.md"
    dtext = dec.read_text(encoding="utf-8") if dec.is_file() else ""
    total = len(re.findall(r"^## D-", dtext, re.M))
    assumed = len(re.findall(r"^ruling:\s*not objected", dtext, re.M | re.I))
    cr_dir = ledger.parent / "cr"
    return {
        "project": _ledger_field(text, "project") or "?",
        "run": ledger.parent.name,
        "status": _ledger_field(text, "status") or "?",
        "network": _ledger_field(text, "network"),
        "intake": intake,
        "spent": spent,
        "over": spent - intake if None not in (spent, intake) else None,
        "plans": len(replans),
        "asked": total - assumed,
        "assumed": assumed,
        "cr": len(list(cr_dir.glob("*.md"))) if cr_dir.is_dir() else 0,
        "gate_fail": sum(1 for r in arts if r[1] in GATE_LANES
                         and r[7].upper() in GATE_FAIL),
        "not_done": sum(1 for r in arts if r[6].upper() in NOT_DONE),
        "rows": [{"lane": r[1], "agent": r[3], "model": r[4],
                  "status": r[6].upper(), "verdict": r[7].upper()}
                 for r in arts],
    }


def lane_table(runs: list[dict]) -> list[dict]:
    by: dict[str, Counter] = {}
    for run in runs:
        for row in run["rows"]:
            c = by.setdefault(row["lane"], Counter())
            c["n"] += 1
            c[row["status"]] += 1
            if row["lane"] in GATE_LANES:
                c["v:" + row["verdict"]] += 1
    out = []
    for lane, c in sorted(by.items(), key=lambda kv: -kv[1]["n"]):
        out.append({
            "lane": lane, "dispatches": c["n"], "done": c["DONE"],
            "not_done": sum(c[s] for s in NOT_DONE),
            "pass": c["v:PASS"] if lane in GATE_LANES else None,
            "fail": (sum(c["v:" + v] for v in GATE_FAIL)
                     if lane in GATE_LANES else None),
        })
    return out


def _cell(v) -> str:
    return "-" if v is None else str(v)


def _print_table(headers: list[str], rows: list[list]) -> None:
    cells = [[_cell(v) for v in r] for r in rows]
    widths = [max(len(h), *(len(r[i]) for r in cells)) if cells else len(h)
              for i, h in enumerate(headers)]
    def line(vals):
        return "  ".join(v.ljust(widths[0]) if i == 0 else v.rjust(widths[i])
                         for i, v in enumerate(vals))
    print(line(headers))
    print(line(["-" * w for w in widths]))
    for r in cells:
        print(line(r))


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    paths = [Path(a) for a in argv if not a.startswith("--")]
    ledgers = find_ledgers(paths or [ROOT / "corpus"])
    if not ledgers:
        print("no ledgers found - pass a run dir, or a folder holding `runs/`")
        return 2
    runs = [run_stats(p) for p in ledgers]
    lanes = lane_table(runs)

    def total(key):
        vals = [r[key] for r in runs if r[key] is not None]
        return sum(vals)

    summary = {
        "runs": len(runs),
        "dispatches": sum(len(r["rows"]) for r in runs),
        "intake": total("intake"), "spent": total("spent"),
        "replanned_runs": sum(1 for r in runs if r["plans"]),
        "asked": total("asked"), "assumed": total("assumed"),
        "cr": total("cr"), "gate_fail": total("gate_fail"),
        "not_done": total("not_done"),
    }
    if as_json:
        for r in runs:
            del r["rows"]
        print(json.dumps({"summary": summary, "runs": runs, "lanes": lanes},
                         indent=1))
        return 0

    keys = ["network", "intake", "spent", "over", "plans", "asked", "assumed",
            "cr", "gate_fail", "not_done"]
    heads = ["run", "ver", "intake", "spent", "over", "plans", "asked",
             "assumed", "CR", "gateFAIL", "notDONE"]
    for project in sorted({r["project"] for r in runs}):
        print(f"\n{project}")
        mine = [r for r in runs if r["project"] == project]
        _print_table(heads, [[r["run"] + ("" if r["status"] == "CLOSED"
                                          else f" [{r['status']}]")]
                             + [r[k] for k in keys] for r in mine])

    n = summary["runs"]
    print(f"\ntotal - {n} runs, {summary['dispatches']} dispatches")
    if summary["intake"]:
        ratio = summary["spent"] / summary["intake"]
        print(f"  intake {summary['intake']}, spent {summary['spent']} "
              f"({ratio:.2f}x), {summary['replanned_runs']} of {n} runs "
              f"re-planned")
    rulings = summary["asked"] + summary["assumed"]
    if rulings:
        print(f"  rulings {rulings}: asked {summary['asked']} "
              f"({summary['asked'] / n:.1f} a run), assumed "
              f"{summary['assumed']} ({summary['assumed'] / rulings:.0%})")
    print(f"  change requests {summary['cr']}, gate FAILs "
          f"{summary['gate_fail']}, slots not DONE {summary['not_done']} "
          f"({summary['not_done'] / max(summary['dispatches'], 1):.0%})")

    print("\nby lane")
    _print_table(["lane", "dispatches", "DONE", "notDONE", "PASS", "FAIL"],
                 [[ln["lane"], ln["dispatches"], ln["done"], ln["not_done"],
                   ln["pass"], ln["fail"]] for ln in lanes])
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
