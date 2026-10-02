#!/usr/bin/env python3
"""Stop hook: the `.agentic` session does not finish quietly on an unlinted network edit.

TD-05 is that `protocol-linter` runs when someone asks. Every other rule in this
network is enforced where the work happens -- `report_artifact_gate.py` on each
write, `report_head_gate.py` at `SubagentStop`, the close-out sweep at close --
and the authoring gate alone depended on the orchestrator remembering. v0.7.16's
contradiction in `protocol/authoring.md` is what that costs: live for a day, and
found only because `ROADMAP.md` told someone to look.

The close-out sweep cannot be the home for this. It runs inside a run, and the
edits that reach these files most often are main-session edits with no run at
all -- which is the case the debt row names.

So it fires at `Stop`, in the one session that edits them.

A reminder, not the enforcement point, and the distinction is load-bearing.
Claude Code's own guidance is that a hook is for *deterministic control* -- "certain
actions always happen rather than relying on the LLM to choose to run them" -- and
that for a hard allow or deny you use the permission system, not a hook, because a
hook that times out does not block. This one also releases after one hold, and it
is one line in `.claude/settings.json` away from not existing. What it guarantees is
that the fact is in front of whoever is finishing. The enforcement point is the
commit: `python scripts/check_network_edit.py --strict` exits 1 on the same
condition with no hook involved, and that is ROADMAP item 5.

Why a command hook and not a `prompt` or `agent` hook. The split is the one the
docs draw: deterministic rules go in a command hook, judgment goes to a model.
"Is there a passing lint artifact naming this file?" is deterministic, so it is
here. "Is this edit sound?" is judgment, so it stays with the `protocol-linter`
lane -- and agent hooks are documented as experimental, with command hooks
preferred for production, so the judgment half is dispatched, not hooked.

Bounded twice over. `stop_hook_active` is the documented bound and is checked
first: Claude Code sets it once a Stop hook has already blocked this turn, and a
hook that ignores it loops until the platform's hard cap (9) overrides it. The
local counter behind it exists because that flag has been observed not to
propagate when system reminders interleave with stop attempts, and a wedged
session is a worse failure than a missed reminder. One hold either way, then it
releases and says so -- sometimes the right answer is a lint run, and sometimes
it is that the edit is being reverted anyway.
"""

from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_network_edit as ne  # noqa: E402

MAX_BLOCKS = 1
_STATE = Path(tempfile.gettempdir()) / "agentic_network_edit_gate"
# A marker is per-session state, so it is dead the moment that session ends.
# Nothing tells a hook when that happened, so they age out instead -- otherwise
# the directory grows one file per session for the life of the machine.
_STALE_SECONDS = 24 * 60 * 60


def _marker(session_id: str) -> Path | None:
    """This session's hold counter, or None when there is no session to key on.

    Deliberately not a shared `"nosession"` bucket: that file would be written by
    the first session to be held and read by every later one, so a single hold
    would silently exempt every session after it. With no id, `stop_hook_active`
    is the only bound, which is the bound the platform documents anyway.
    """
    return _STATE / session_id if session_id else None


def _prune() -> None:
    cutoff = time.time() - _STALE_SECONDS
    try:
        for old in _STATE.iterdir():
            if old.is_file() and old.stat().st_mtime < cutoff:
                old.unlink()
    except OSError:
        pass


def _blocks_so_far(session_id: str) -> int:
    """How many times this session has already been held."""
    marker = _marker(session_id)
    if marker is None:
        return 0
    try:
        return int(marker.read_text(encoding="utf-8").strip() or 0)
    except (OSError, ValueError):
        return 0


def _record_block(session_id: str) -> None:
    marker = _marker(session_id)
    if marker is None:
        return
    try:
        _STATE.mkdir(parents=True, exist_ok=True)
        _prune()
        marker.write_text(str(_blocks_so_far(session_id) + 1), encoding="utf-8")
    except OSError:
        pass


def main() -> None:
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.exit(0)

    # Set once a Stop hook has blocked this turn. Honouring it is the documented
    # way not to loop, and it is what keeps two independent hooks from compounding.
    if payload.get("stop_hook_active"):
        sys.exit(0)

    try:
        rows = ne.report()
    except Exception as exc:  # a broken gate must not wedge the session
        print(f"network_edit_gate could not run: {exc}", file=sys.stderr)
        sys.exit(0)

    if not rows:
        sys.exit(0)

    session_id = payload.get("session_id") or ""
    if _blocks_so_far(session_id) >= MAX_BLOCKS:
        print("Network files still unlinted - letting this session stop. "
              "They are listed above; `protocol-lint` has not judged them.",
              file=sys.stderr)
        sys.exit(0)

    print("UNLINTED NETWORK EDIT - these files are a lane's instructions, and "
          "`protocol-linter` is the gate on them (TD-05):", file=sys.stderr)
    for row in rows:
        print(f"  {row}", file=sys.stderr)
    print("Dispatch `protocol-linter` over them from a BOUND REPO session - "
          "portfolio, budget, impact, tradingview or datoro. Not from here: "
          "`.agentic` carries no `.agentic.json`, so the linter's bind step "
          "reports BLOCKED. Or say plainly that this edit is shipping ungated "
          "and why. When the subject is `authoring.md` or `protocol-linter.md` "
          "itself, the anchor is the other agent files, not the rule text.",
          file=sys.stderr)
    _record_block(session_id)
    sys.exit(2)


if __name__ == "__main__":
    main()
