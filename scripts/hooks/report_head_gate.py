#!/usr/bin/env python3
"""SubagentStop hook: a lane does not finish on an invalid report or head.

Exit 2 at SubagentStop prevents the subagent from stopping -- it keeps working
and sees the reason on stderr. That makes PROTOCOL.md section 4 enforceable for
the first time: until now "end your run with exactly this block" was an
instruction, and a head whose counts disagreed with its artifact silently
dropped whatever the orchestrator would have routed from the difference.

On a clean pass it also writes `<nn>-head.txt` beside the artifact -- the file
the close-out sweep demands and that run 2026-09-09 recorded nobody saving
("Bash-less lanes, heads not persisted earlier"). Derived from the head the
lane actually returned, after that head has been checked against the artifact,
so persisting it cannot launder a wrong one.

This is the gate. report_artifact_gate.py is the early warning that fires on
each write; a lane may legitimately ignore that one mid-construction, and
cannot ignore this one.

Scope. It filters on agent type, read from the plugin's own agents/ directory
rather than a hardcoded list, so adding a lane does not silently exempt it.
Every other subagent -- Explore, general-purpose, anything the human runs
directly -- exits 0 untouched.

Bounded. Two blocks per subagent, then it allows the stop and says so. A hook
that can refuse forever is a hook that can hang a run, and the close-out sweep
(`check_report.py <run_dir>/ --require-heads`) is still there to catch what got
through -- a missing head file fails it.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_report as cr  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
LANE_DIR = ROOT / "plugins" / "agentic-core" / "agents"
MAX_BLOCKS = 2


def _lanes() -> set[str]:
    """Agent names the network defines, or empty if the plugin dir is absent."""
    try:
        return {p.stem for p in LANE_DIR.glob("*.md")}
    except OSError:
        return set()


def _blocks_so_far(agent_id: str) -> int:
    """How many times this subagent has already been held back."""
    if not agent_id:
        return 0
    safe = re.sub(r"[^A-Za-z0-9_-]", "", agent_id)[:64] or "anon"
    counter = Path(tempfile.gettempdir()) / "agentic-head-gate" / safe
    try:
        counter.parent.mkdir(parents=True, exist_ok=True)
        n = int(counter.read_text(encoding="utf-8")) if counter.is_file() else 0
        counter.write_text(str(n + 1), encoding="utf-8")
        return n
    except (OSError, ValueError):
        return 0


def _head_block(message: str) -> str | None:
    """The REPORT HEAD block, from its first line to the end of the message."""
    lines = message.splitlines()
    i = next((k for k, ln in enumerate(lines)
              if ln.strip().startswith("REPORT HEAD ")), None)
    if i is None:
        return None
    head = "\n".join(lines[i:]).strip()
    return head[:-3].rstrip() if head.endswith("```") else head


def _hold(agent_id: str, lines: list[str]) -> None:
    """Refuse the stop, unless this subagent has already been held twice."""
    if _blocks_so_far(agent_id) >= MAX_BLOCKS:
        print("REPORT HEAD still invalid after two attempts - letting this "
              "lane stop. The close-out sweep will fail on it.", file=sys.stderr)
        sys.exit(0)
    for ln in lines:
        print(ln, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.exit(0)

    # Plugin-scoped types arrive as `agentic-core:scout`; bare ones as `scout`.
    lane = (payload.get("agent_type") or "").split(":")[-1]
    if lane not in _lanes():
        sys.exit(0)

    agent_id = payload.get("agent_id") or ""
    head = _head_block(payload.get("last_assistant_message") or "")
    if head is None:
        _hold(agent_id, [
            "NO REPORT HEAD - PROTOCOL.md section 4 requires your final message "
            "to be the REPORT HEAD block and nothing after it. The orchestrator "
            "routes from the head; without one your work is invisible to it.",
            "Derive it rather than typing it: the counts must match your "
            "artifact.",
        ])

    raw = cr._scalar(head, "artifact")
    if not raw:
        _hold(agent_id, ["REPORT HEAD has no 'artifact:' line - it must carry "
                         "the absolute path you wrote the report to."])

    artifact = Path(raw)
    if not artifact.is_file() or not cr._is_report(artifact):
        _hold(agent_id, [
            f"REPORT HEAD names artifact {raw!r}, which is not a report file on "
            "disk. Write the full report to your order's report_to path first; "
            "the head is a summary of it, not a replacement for it."])

    # Artifact first, head second. They fail for unrelated reasons and the fix
    # differs: a malformed artifact is the lane's own writing, a wrong head is
    # arithmetic it should not have been doing by hand in the first place.
    lane_of = cr.lane_from_name(artifact)
    art_bad = cr.check(artifact, lane=lane_of)
    if art_bad:
        _hold(agent_id, [f"{artifact.name} does not satisfy PROTOCOL.md "
                         "section 3, so its head cannot be trusted either:"]
              + [f"  - {b}" for b in art_bad])

    head_bad = cr._check_head(head, artifact.read_text(encoding="utf-8"))
    if head_bad:
        # Hand over the derived head rather than only the diffs. A head is a
        # count of list items and a string sliced to an exact length - the two
        # things PROTOCOL.md section 4 records a model getting wrong in 26 of
        # 59 closed heads - and the three lanes with no Bash cannot run
        # --emit-head to get it. Telling them what is wrong without telling
        # them the answer just buys another guess.
        _hold(agent_id,
              [f"REPORT HEAD does not match {artifact.name}:"]
              + [f"  - {b}" for b in head_bad]
              + ["", "Return this head instead, filling in only what is left "
                 "in angle brackets:", ""]
              + cr.head_for(artifact).splitlines())

    slot = cr.head_path_for(artifact)
    if slot is not None:
        try:
            # Platform-native newlines, deliberately: every head already on disk
            # was written by redirecting --emit-head on this machine, and forcing
            # LF here would rewrite every one of them as modified.
            slot.write_text(head + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"could not save {slot.name}: {exc}", file=sys.stderr)
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
