#!/usr/bin/env python3
"""PostToolUse hook: check a run artifact the moment a lane writes it.

Wired on `Write|Edit`. Silent unless the file is a report artifact under a run
directory -- first non-blank line `REPORT `, which is PROTOCOL.md section 3's
own definition and the same test the directory sweep uses.

Exit 2 on PostToolUse feeds stderr back to the agent without undoing the write;
the tool already ran. Exit 0 stays silent.

Why this exists. `scout`, `story-author` and `docs-engineer` are granted no
Bash, so the "check your own artifact" line in every agent definition is one
they cannot follow. Their reports were first validated by the orchestrator,
after the only session that could cheaply fix them had ended -- run
2026-09-09 records exactly that, for slots 03 and 04. A hook needs no tool
grant, so it reaches those three lanes on equal terms with the rest.

This is early warning, not the gate. A lane building its report over several
edits will trip it on an intermediate state, which is why the message says so.
The gate that actually blocks is report_head_gate.py at SubagentStop.

Advisory notes (`~` in the CLI) are deliberately dropped: they do not fail a
close-out sweep, and a hook that fires on every write is the wrong place to
spend a lane's attention on them.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_report as cr  # noqa: E402


def _artifact(payload: dict) -> Path | None:
    """The report artifact this write touched, or None if it was not one."""
    raw = (payload.get("tool_input") or {}).get("file_path") or ""
    if not raw:
        return None
    path = Path(raw)
    # Under <agenticRoot>/runs/<run-id>/. run.md and pack-corrections.md are a
    # ledger and a queue; neither opens with REPORT, so _is_report drops them.
    if path.suffix != ".md" or path.parent.parent.name != "runs":
        return None
    if not path.is_file() or not cr._is_report(path):
        return None
    return path


def main() -> None:
    # Reports quote arrows and dashes. Windows encodes stderr as cp1252 and
    # raises on the first character outside it, which would turn a violation
    # into a traceback the lane cannot act on.
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.exit(0)

    artifact = _artifact(payload)
    if artifact is None:
        sys.exit(0)

    bad = cr.check(artifact, lane=cr.lane_from_name(artifact))
    if not bad:
        sys.exit(0)

    print(f"REPORT INVALID -- {artifact.name} does not satisfy PROTOCOL.md "
          f"section 3:", file=sys.stderr)
    for b in bad:
        print(f"  - {b}", file=sys.stderr)
    print("Fix these before you finish. If you are still building the file, "
          "this is expected and you can carry on; it has to be clean when you "
          "return your REPORT HEAD.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
