#!/usr/bin/env python3
"""Validate an agent report against PROTOCOL.md Shape 2.

    python scripts/check_report.py runs/<run-id>/01-scout.md [--lane recon]
    python scripts/check_report.py runs/<run-id>/            # every artifact

Exit 0 = valid. Exit 1 = violations, printed one per line.

This exists because "reports are structured" was, until v0.3.2, enforced by
asking agents nicely. A format nothing checks is a format that drifts, and the
orchestrator routes from these fields — an unparseable contract_notes block is
a downstream order that never gets written.

Dependency-free by design: it runs anywhere the network runs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

STATUS = {"DONE", "PARTIAL", "BLOCKED", "REFUSED"}
VERDICT = {"PASS", "FAIL", "CHANGES_REQUESTED", "NONE"}
RESULT = {"PASS", "FAIL", "NOT_RUN"}

SECTIONS = ["changed", "verification", "contract_notes",
            "pack_corrections", "handoff", "risks"]

# Lanes permitted to render a judgment. Everyone else writes verdict: NONE.
GATE_LANES = {"integration", "review", "quant-audit"}
# Only the tech lead's integration pass may request changes.
CR_LANES = {"integration"}


def _scalar(text: str, key: str) -> str | None:
    # command/result/detail are indented under `verification:`, so leading
    # whitespace is expected — matching at column 0 only was the first bug
    # this script found, in itself.
    m = re.search(rf"^[ \t]*{re.escape(key)}:[ \t]*(.*)$", text, re.M)
    return m.group(1).strip() if m else None


def _section(text: str, name: str) -> list[str] | None:
    """Body lines of a top-level section, or None if the heading is absent."""
    m = re.search(rf"^{re.escape(name)}:[ \t]*$", text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    stop = re.search(r"^\S+:", rest, re.M)
    body = rest[: stop.start()] if stop else rest
    return [ln.strip() for ln in body.splitlines() if ln.strip()]


def check(path: Path, lane: str | None = None) -> list[str]:
    text = path.read_text(encoding="utf-8")
    bad: list[str] = []

    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    if not first.startswith("REPORT "):
        bad.append(f"first non-blank line must be 'REPORT <id>', got {first!r}")

    status = _scalar(text, "status")
    if status is None:
        bad.append("missing 'status:'")
    elif status not in STATUS:
        bad.append(f"status {status!r} not in {sorted(STATUS)}"
                   + (" - CHANGES_REQUESTED is a verdict, not a status"
                      if status == "CHANGES_REQUESTED" else ""))

    verdict = _scalar(text, "verdict")
    if verdict is None:
        bad.append("missing 'verdict:' (write NONE if this lane is not a gate)")
    elif verdict not in VERDICT:
        bad.append(f"verdict {verdict!r} not in {sorted(VERDICT)}")

    for name in SECTIONS:
        lines = _section(text, name)
        if lines is None:
            bad.append(f"missing section '{name}:'")
        elif not lines:
            bad.append(f"section '{name}:' is empty - write '- none', "
                       "silence is ambiguous")

    result = _scalar(text, "result")
    command = _scalar(text, "command")
    if result is None:
        bad.append("missing 'result:' under verification")
    elif result not in RESULT:
        bad.append(f"verification.result {result!r} not in {sorted(RESULT)}")

    # The rule that catches the expensive failure: claiming DONE on unverified
    # work. A read-only order (command NONE) is exempt.
    read_only = command is None or command.strip().upper() in {"NONE", "-"}
    if status == "DONE" and result == "NOT_RUN" and not read_only:
        bad.append(f"status DONE with result NOT_RUN and command {command!r} - "
                   "an order that named a command must run it")

    if lane:
        if verdict and verdict != "NONE" and lane not in GATE_LANES:
            bad.append(f"lane {lane!r} emitted verdict {verdict!r}; only "
                       f"{sorted(GATE_LANES)} may judge")
        if verdict == "CHANGES_REQUESTED" and lane not in CR_LANES:
            bad.append(f"lane {lane!r} emitted CHANGES_REQUESTED; only "
                       f"{sorted(CR_LANES)} may")

    return bad


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    lane = None
    if "--lane" in argv:
        i = argv.index("--lane")
        if i + 1 < len(argv):
            lane = argv[i + 1]
            args = [a for a in args if a != lane]
    if not args:
        print(__doc__)
        return 2

    target = Path(args[0])
    if target.is_dir():
        # Report artifacts are numbered: 01-scout.md, 02-delivery-brief.md.
        # run.md is the ledger and pack-corrections.md is a queue; neither is
        # a report and neither should be validated as one.
        files = sorted(p for p in target.glob("*.md")
                       if re.match(r"^\d{2}-", p.name))
    else:
        files = [target]
    if not files:
        print(f"no report artifacts found in {target}")
        return 2

    failed = False
    for f in files:
        problems = check(f, lane)
        if problems:
            failed = True
            print(f"FAIL {f}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"ok   {f}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
