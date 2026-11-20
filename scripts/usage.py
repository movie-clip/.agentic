#!/usr/bin/env python3
"""What a dispatch cost, read from the subagent's own transcript.

A ledger counts dispatches, and one dispatch can be ten times another. Claude
Code keeps a transcript per subagent, and every model request in it records its
token usage and a timestamp, so tokens and wall-clock time can be added up
instead of typed. This module does the adding; `report_head_gate.py` calls it
when a lane stops, and the command line backfills runs that already happened.

  usage.py <transcripts> <runs> [<runs> ...]

`<transcripts>` is a Claude Code project folder (`~/.claude/projects/<slug>`)
or any folder holding `agent-*.jsonl` below it. `<runs>` is a folder of run
dirs. Each slot found is written to `<runs>/<run-id>/<nn>-usage.json`; a slot
whose run dir is not there is counted and skipped.

A transcript is cut at every work order in it, because a lane that was resumed
for a second order keeps one transcript across both slots. Each cut is one
slot's usage.

Three things about the source, each of which is a way to be wrong:

- One model response is logged once per content block, so a plain sum counts
  it two or three times. Usage is counted once per message id.
- The four token kinds are kept apart. Cache reads outnumber output a hundred
  to one and are priced far below it, so a single total says nothing.
- The transcript layout is not a documented interface, and the file can trail
  the conversation by a message. So nothing here raises: an unreadable file or
  line yields no slot, and the caller carries on. A missing usage file means
  "not measured", never "free".

Only the lane's own requests are here. The orchestrator's are in the main
session's transcript, which one session shares across runs.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

TOKEN_KEYS = ("input_tokens", "cache_creation_input_tokens",
              "cache_read_input_tokens", "output_tokens")
ORDER = re.compile(r"^\s*WORK ORDER\s+(\S+)/(\d+)\b", re.M)


def _order_in(entry: dict) -> tuple[str, str] | None:
    """(run id, slot) if this entry is a work order handed to the lane.

    Only the text a lane was *sent* counts. A tool result that quotes a work
    order - a lane reading an earlier artifact - is not a new dispatch.
    """
    if entry.get("type") != "user":
        return None
    msg = entry.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, list):
        content = "\n".join(b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text")
    if not isinstance(content, str):
        return None
    m = ORDER.search(content)
    return (m.group(1), m.group(2)) if m else None


def _seconds(start: str | None, end: str | None) -> int | None:
    try:
        a = datetime.fromisoformat(start.replace("Z", "+00:00"))
        b = datetime.fromisoformat(end.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None
    return max(0, round((b - a).total_seconds()))


def slots(transcript: Path) -> list[dict]:
    """One record per work order found in this transcript, in order."""
    try:
        lines = transcript.read_text(encoding="utf-8",
                                     errors="replace").splitlines()
    except OSError:
        return []
    out: list[dict] = []
    cur: dict | None = None
    seen: set[str] = set()
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        ts = entry.get("timestamp")
        order = _order_in(entry)
        if order:
            cur = {"run": order[0], "slot": order[1], "model": None,
                   "requests": 0, **{k: 0 for k in TOKEN_KEYS},
                   "started": ts, "ended": ts}
            out.append(cur)
            continue
        if cur is None:
            continue
        if ts:
            cur["ended"] = ts
        msg = entry.get("message")
        if entry.get("type") != "assistant" or not isinstance(msg, dict):
            continue
        usage, mid = msg.get("usage"), msg.get("id")
        if not isinstance(usage, dict) or mid in seen:
            continue
        if mid:
            seen.add(mid)
        cur["requests"] += 1
        cur["model"] = msg.get("model") or cur["model"]
        for k in TOKEN_KEYS:
            v = usage.get(k)
            if isinstance(v, int):
                cur[k] += v
    for rec in out:
        rec["duration_s"] = _seconds(rec["started"], rec["ended"])
        rec["source"] = transcript.name
    return [r for r in out if r["requests"]]


def write_slot(run_dir: Path, rec: dict) -> Path | None:
    """Write `<nn>-usage.json` into an existing run dir. None if it is not there."""
    if not run_dir.is_dir():
        return None
    path = run_dir / f"{rec['slot']}-usage.json"
    try:
        path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    except OSError:
        return None
    return path


def record(transcript: Path, run_dir: Path) -> int:
    """Write every slot of this transcript that belongs to `run_dir`.

    The hook's entry point: it knows the run dir from the head it just
    checked, and a resumed lane's transcript may hold an earlier slot of the
    same run, which is rewritten with the same numbers.
    """
    n = 0
    for rec in slots(transcript):
        if rec["run"] == run_dir.name and write_slot(run_dir, rec):
            n += 1
    return n


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    source, roots = Path(argv[0]), [Path(a) for a in argv[1:]]
    transcripts = sorted(source.rglob("agent-*.jsonl"))
    found = written = 0
    missing: dict[str, int] = {}
    for t in transcripts:
        for rec in slots(t):
            found += 1
            for root in roots:
                if write_slot(root / rec["run"], rec):
                    written += 1
                    break
            else:
                missing[rec["run"]] = missing.get(rec["run"], 0) + 1
    print(f"{len(transcripts)} transcripts, {found} slots found, "
          f"{written} written")
    for run, n in sorted(missing.items()):
        print(f"  no run dir for {run} ({n} slot(s))")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
