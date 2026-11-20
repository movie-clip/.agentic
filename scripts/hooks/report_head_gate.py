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

Bounded by a per-subagent counter: two holds, then it allows the stop and says
so. `stop_hook_active` -- set once a stop hook has already blocked this turn --
bounds only the case the counter cannot, a payload with no `agent_id`. It never
skips the check itself: it is set on exactly the attempt that follows a hold,
so releasing on sight of it let every corrected head through unchecked and
unsaved, and made the second hold unreachable. A hook that can refuse forever
is a hook that can hang a run, and the close-out sweep
(`check_report.py <run_dir>/ --require-heads`) is still there to catch what got
through -- a missing head file fails it, and so does an artifact whose block
is not on its first line.

Two events since Claude Code 2.1.329. A subagent there ends on a
`SubagentHandback({message})` tool call: the stop payload carries no
`last_assistant_message`, and an exit 2 at the stop no longer reaches the lane
(probed 2026-11-20, TECH-DEBT TD-27). So this script is wired twice:

- `PreToolUse`, matcher `SubagentHandback` -- the gate. The message is checked
  before it is delivered; exit 2 rejects the call and the lane hands back
  again. The same two-hold bound applies, and a clean pass saves the head.
- `SubagentStop` -- the record. It is the one event handed the lane's
  transcript, so usage is written here. After a handback it holds nothing.
  On an older Claude Code, which still sends `last_assistant_message`, it is
  the gate as before.

Advisories ride along, and never cause a hold. This is the only place the `~`
half of check_report.py reaches the two lanes with no Bash: the CLI is one
they cannot run and report_artifact_gate.py drops the notes on purpose. A lane
already being held is already editing, so the notes cost it nothing there. A
clean artifact is still a clean stop.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_report as cr  # noqa: E402
import usage  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
LANE_DIR = ROOT / "plugins" / "agentic-core" / "agents"
MAX_BLOCKS = 2
# Set at a stop that follows a SubagentHandback: the report is delivered, so a
# refusal reaches nobody. The run records usage, saves a valid head, and is
# otherwise silent.
_LATE = False
_STATE = Path(tempfile.gettempdir()) / "agentic-head-gate"
# A counter is per-subagent state, dead the moment that subagent ends. Nothing
# tells a hook when that happened, so they age out rather than accumulating one
# file per lane dispatch for the life of the machine.
_STALE_SECONDS = 24 * 60 * 60


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
    counter = _STATE / safe
    try:
        counter.parent.mkdir(parents=True, exist_ok=True)
        _prune()
        n = int(counter.read_text(encoding="utf-8")) if counter.is_file() else 0
        counter.write_text(str(n + 1), encoding="utf-8")
        return n
    except (OSError, ValueError):
        return 0


def _prune() -> None:
    cutoff = time.time() - _STALE_SECONDS
    try:
        for old in _STATE.iterdir():
            if old.is_file() and old.stat().st_mtime < cutoff:
                old.unlink()
    except OSError:
        pass


def _head_block(message: str) -> str | None:
    """The REPORT HEAD block, from its first line to the end of the message."""
    lines = message.splitlines()
    i = next((k for k, ln in enumerate(lines)
              if ln.strip().startswith("REPORT HEAD ")), None)
    if i is None:
        return None
    head = "\n".join(lines[i:]).strip()
    return head[:-3].rstrip() if head.endswith("```") else head


def _hold(agent_id: str, retry: bool, lines: list[str]) -> None:
    """Refuse the stop, unless this subagent has already been held twice."""
    if _LATE:
        sys.exit(0)
    if (retry and not agent_id) or _blocks_so_far(agent_id) >= MAX_BLOCKS:
        print("REPORT HEAD still invalid after two attempts - letting this "
              "lane stop. The close-out sweep will fail on it.", file=sys.stderr)
        sys.exit(0)
    for ln in lines:
        print(ln, file=sys.stderr)
    sys.exit(2)


def _handback(payload: dict, wait: float = 4.0) -> str:
    """The report a lane delivered through SubagentHandback, or "".

    Claude Code 2.1.329 ends a subagent on a `SubagentHandback({message})`
    tool call and sends this hook no `last_assistant_message`, so the head is
    in the transcript and nowhere in the payload. Measured on 2026-11-20: the
    hook fires about 70 ms after the call returns and the transcript line for
    it lands up to a few seconds later, hence the short wait. Only a handback
    after the lane's latest work order counts - a resumed lane's transcript
    still holds the one that closed its earlier slot.
    """
    raw = payload.get("agent_transcript_path")
    if not raw:
        return ""
    path = Path(raw).expanduser()
    deadline = time.time() + wait
    while True:
        found = ""
        try:
            lines = path.read_text(encoding="utf-8",
                                   errors="replace").splitlines()
        except OSError:
            lines = []
        for line in lines:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            if usage._order_in(entry):
                found = ""
                continue
            msg = entry.get("message")
            content = msg.get("content") if isinstance(msg, dict) else None
            if entry.get("type") != "assistant" or not isinstance(content, list):
                continue
            for block in content:
                if (isinstance(block, dict) and block.get("type") == "tool_use"
                        and block.get("name") == "SubagentHandback"):
                    message = (block.get("input") or {}).get("message")
                    if isinstance(message, str):
                        found = message
        if found or time.time() >= deadline:
            return found
        time.sleep(0.25)


def _record_usage(payload: dict, artifact: Path) -> None:
    """Write `<nn>-usage.json` for this lane's slots. Never affects the gate.

    The stop is the one moment the hook is handed the lane's transcript, so
    the cost of the dispatch is read here and nowhere typed. It is recorded
    before the artifact and head are judged: a lane held back and stopping
    again rewrites the file with the larger numbers, and a lane released on a
    bad head has still been paid for. Only into a real run dir, and any
    failure is swallowed - a transcript this cannot read is a slot left
    unmeasured, not a lane left hanging.
    """
    try:
        transcript = payload.get("agent_transcript_path")
        run_dir = artifact.parent
        if transcript and (run_dir / "run.md").is_file():
            usage.record(Path(transcript).expanduser(), run_dir)
    except Exception:  # noqa: BLE001
        pass


def main() -> None:
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.exit(0)

    # Set once a stop hook has already blocked this turn. It bounds holds only
    # where the counter cannot (no agent_id) - see the module docstring.
    retry = bool(payload.get("stop_hook_active"))

    # Plugin-scoped types arrive as `agentic-core:scout`; bare ones as `scout`.
    lane = (payload.get("agent_type") or "").split(":")[-1]
    if lane not in _lanes():
        sys.exit(0)

    agent_id = payload.get("agent_id") or ""
    global _LATE
    if payload.get("hook_event_name") == "PreToolUse":
        if payload.get("tool_name") != "SubagentHandback":
            sys.exit(0)
        message = (payload.get("tool_input") or {}).get("message")
        message = message if isinstance(message, str) else ""
    else:
        message = payload.get("last_assistant_message") or ""
        if not message:
            message, _LATE = _handback(payload), True
    head = _head_block(message)
    if head is None:
        _hold(agent_id, retry, [
            "NO REPORT HEAD - PROTOCOL.md section 4 requires your final message "
            "to be the REPORT HEAD block and nothing after it. The orchestrator "
            "routes from the head; without one your work is invisible to it.",
            "Derive it rather than typing it: the counts must match your "
            "artifact.",
        ])

    raw = cr._scalar(head, "artifact")
    if not raw:
        _hold(agent_id, retry, ["REPORT HEAD has no 'artifact:' line - it must carry "
                         "the absolute path you wrote the report to."])

    artifact = Path(raw)
    if not artifact.is_file():
        _hold(agent_id, retry, [
            f"REPORT HEAD names artifact {raw!r}, which does not exist. Write "
            "the full report to your order's report_to path first; the head is "
            "a summary of it, not a replacement for it."])
    _record_usage(payload, artifact)
    # The file exists but carries no REPORT line. Say what is in it: the old
    # message ("not a report file on disk") read as a path problem, and the
    # scout it held in run 2026-09-27-sort-potential-rules-by-frequency re-read
    # the file, found it present, and resent the same head twice.
    if not cr._is_report(artifact):
        _hold(agent_id, retry, [
            f"{artifact.name} exists but has no 'REPORT <id>' line, so it is not "
            "a report. Its first line must be the report block's 'REPORT "
            "<run id>/<nn>' (PROTOCOL.md section 3); any document goes below "
            "the block."])

    # Artifact first, head second. They fail for unrelated reasons and the fix
    # differs: a malformed artifact is the lane's own writing, a wrong head is
    # arithmetic it should not have been doing by hand in the first place.
    lane_of = cr.lane_from_name(artifact)
    # Advisories ride along with a hold, and never cause one. `scout`
    # and `docs-engineer` have no Bash, so the only half of
    # check_report.py that has ever reached them is the blocking half -- both
    # hooks drop the `~` notes, and the CLI is one they cannot run. A lane
    # already being held is already editing, which is the one moment the notes
    # cost it nothing. On a clean artifact nothing is said: an advisory is by
    # definition not worth stopping a lane for.
    notes: list[str] = []
    art_bad = cr.check(artifact, lane=lane_of, warn=notes)
    if art_bad:
        _hold(agent_id, retry, [f"{artifact.name} does not satisfy PROTOCOL.md "
                         "section 3, so its head cannot be trusted either:"]
              + [f"  - {b}" for b in art_bad]
              + ([""] + ["Advisory, while you are here (these do not block):"]
                 + [f"  ~ {n}" for n in notes] if notes else []))

    head_bad = cr._check_head(head, artifact.read_text(encoding="utf-8"))
    if head_bad:
        # Hand over the derived head rather than only the diffs. A head is a
        # count of list items and a string sliced to an exact length - the two
        # things PROTOCOL.md section 4 records a model getting wrong in 26 of
        # 59 closed heads - and the two lanes with no Bash cannot run
        # --emit-head to get it. Telling them what is wrong without telling
        # them the answer just buys another guess.
        _hold(agent_id, retry,
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
