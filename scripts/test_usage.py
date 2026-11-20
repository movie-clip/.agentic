#!/usr/bin/env python3
"""Tests for usage.py. Run: python scripts/test_usage.py"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import usage  # noqa: E402

results: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, detail: object = "") -> None:
    results.append((name, bool(cond), str(detail)))
    print(("  ok   " if cond else "  FAIL ") + name
          + ("" if cond else f"\n       {detail}"))


def order(run: str, slot: str, ts: str, as_blocks: bool = False) -> dict:
    text = f"WORK ORDER {run}/{slot}\nlane:        backend\n"
    content = [{"type": "text", "text": text}] if as_blocks else text
    return {"type": "user", "timestamp": ts, "message": {"content": content}}


def reply(mid: str, ts: str, out: int, read: int = 0, write: int = 0) -> dict:
    return {"type": "assistant", "timestamp": ts,
            "message": {"id": mid, "model": "claude-sonnet-5-5",
                        "usage": {"input_tokens": 3, "output_tokens": out,
                                  "cache_read_input_tokens": read,
                                  "cache_creation_input_tokens": write}}}


def tool_result(text: str, ts: str) -> dict:
    return {"type": "user", "timestamp": ts, "message": {"content": [
        {"type": "tool_result", "content": text}]}}


def transcript(entries: list, name: str = "agent-abc.jsonl") -> Path:
    p = Path(tempfile.mkdtemp()) / name
    p.write_text("\n".join(e if isinstance(e, str) else json.dumps(e)
                           for e in entries), encoding="utf-8")
    return p


print("A - one order, one slot")
t = transcript([
    order("2026-01-01-demo", "04", "2026-01-01T10:00:00.000Z"),
    reply("m1", "2026-01-01T10:00:10.000Z", 100, read=5000, write=700),
    reply("m1", "2026-01-01T10:00:10.500Z", 100, read=5000, write=700),
    tool_result("WORK ORDER 2026-01-01-other/09\n", "2026-01-01T10:00:20.000Z"),
    "this line is not json",
    reply("m2", "2026-01-01T10:02:30.000Z", 40, read=6000),
])
s = usage.slots(t)
check("one slot is found", len(s) == 1, s)
check("it carries the run id and slot from the order",
      (s[0]["run"], s[0]["slot"]) == ("2026-01-01-demo", "04"), s[0])
check("a response logged twice is counted once",
      s[0]["requests"] == 2 and s[0]["output_tokens"] == 140, s[0])
check("the token kinds stay apart",
      (s[0]["cache_read_input_tokens"], s[0]["cache_creation_input_tokens"],
       s[0]["input_tokens"]) == (11000, 700, 6), s[0])
check("duration runs from the order to the last entry",
      s[0]["duration_s"] == 150, s[0]["duration_s"])
check("a work order quoted in a tool result does not cut a new slot",
      all(r["run"] != "2026-01-01-other" for r in s))
check("a line that is not JSON is skipped, not fatal", s[0]["model"])

print("B - a lane resumed for a second order")
t = transcript([
    order("2026-01-01-demo", "04", "2026-01-01T10:00:00.000Z"),
    reply("m1", "2026-01-01T10:01:00.000Z", 100),
    order("2026-01-01-demo", "07", "2026-01-01T11:00:00.000Z", as_blocks=True),
    reply("m2", "2026-01-01T11:00:30.000Z", 25),
])
s = usage.slots(t)
check("the transcript is cut into two slots",
      [r["slot"] for r in s] == ["04", "07"], s)
check("each keeps only its own usage",
      [r["output_tokens"] for r in s] == [100, 25], s)
check("the first slot ends before the second order",
      s[0]["duration_s"] == 60, s[0]["duration_s"])

print("C - writing")
root = Path(tempfile.mkdtemp())
run = root / "2026-01-01-demo"
run.mkdir()
n = usage.record(t, run)
check("record writes one file per slot of that run", n == 2, n)
got = json.loads((run / "07-usage.json").read_text(encoding="utf-8"))
check("the file holds the slot's numbers",
      got["output_tokens"] == 25 and got["source"] == t.name, got)
check("a transcript for another run writes nothing here",
      usage.record(t, root / "2026-01-01-other") == 0)
check("a slot whose run dir is missing is skipped",
      usage.write_slot(root / "no-such-run", s[0]) is None)

print("D - what it does when the source is not what it expects")
check("a missing transcript yields no slots",
      usage.slots(root / "nope.jsonl") == [])
check("a transcript with no work order yields no slots",
      usage.slots(transcript([reply("m1", "2026-01-01T10:00:00Z", 5)])) == [])
check("an order with no reply after it is not a measured slot",
      usage.slots(transcript([order("r", "01", "2026-01-01T10:00:00Z")])) == [])
t = transcript([order("r", "01", None), reply("m1", None, 5)])
check("entries with no timestamp still count, with no duration",
      usage.slots(t)[0]["duration_s"] is None)

n_fail = sum(1 for _, c, _ in results if not c)
print(f"\n{len(results) - n_fail}/{len(results)} passed")
sys.exit(1 if n_fail else 0)
