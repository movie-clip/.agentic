#!/usr/bin/env python3
"""Tests for check_network_edit.py -- the TD-05 gate.

Two of these pin bugs the check had on its first run against a real tree, both
of the same shape as `check_gates`'s 40-character window: evidence that looked
like coverage and was not.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_network_edit as ne  # noqa: E402

_passed = 0
_failed = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _passed, _failed
    if ok:
        _passed += 1
        print(f"  PASS  {name}")
    else:
        _failed += 1
        print(f"  FAIL  {name}  {detail}")


PASS_ART = """REPORT 2026-01-01-a-lint/01
status:      DONE
verdict:     PASS

changed:
  - none
"""

FAIL_ART = PASS_ART.replace("verdict:     PASS", "verdict:     FAIL")


def _tree(artifacts, subject="protocol/authoring.md", art_newer=True):
    """A fake agenticRoot: one changed subject file plus the artifacts given.

    `artifacts` is a list of (relative run-dir path, body). mtimes are set so the
    artifacts are newer than the subject, or older when `art_newer` is False.
    """
    root = Path(tempfile.mkdtemp())
    subj = root / subject
    subj.parent.mkdir(parents=True, exist_ok=True)
    subj.write_text("rules\n", encoding="utf-8")
    os.utime(subj, (1_000_000, 1_000_000))
    for rel, body in artifacts:
        art = root / rel
        art.parent.mkdir(parents=True, exist_ok=True)
        art.write_text(body, encoding="utf-8")
        stamp = 2_000_000 if art_newer else 500_000
        os.utime(art, (stamp, stamp))
    return root


def _unlinted(root, subject="protocol/authoring.md"):
    """`unlinted` against a fake root, with the real ROOT swapped out."""
    real = ne.ROOT
    ne.ROOT = root
    try:
        return ne.unlinted([subject])
    finally:
        ne.ROOT = real


print("scope is protocol-linter's declared trigger, and nothing wider")

check("an agent definition is in scope",
      ne.is_network("plugins/agentic-core/agents/scout.md"))
check("a skill is in scope",
      ne.is_network("plugins/agentic-core/skills/orchestrate-feature/SKILL.md"))
check("the core and its extensions are in scope",
      ne.is_network("PROTOCOL.md") and ne.is_network("protocol/gates.md"))
check("a profile, its phases and a pack are in scope",
      ne.is_network("projects/budget/project.md")
      and ne.is_network("projects/budget/phases.md")
      and ne.is_network("projects/budget/capabilities/testing.md"))

# The manifest's gate is `claude plugin validate`, not an authoring judgment, so
# a version bump must not ask for a lint round.
check("the plugin manifest is out of scope",
      not ne.is_network("plugins/agentic-core/.claude-plugin/plugin.json"))
check("run artifacts and ledgers are out of scope",
      not ne.is_network("projects/budget/runs/2026-01-01-x/run.md"))
check("human-facing docs are out of scope",
      not any(ne.is_network(p) for p in
              ("README.md", "ROADMAP.md", "TECH-DEBT.md", "CHANGELOG.md")))
check("scripts are out of scope - their gate is their tests",
      not ne.is_network("scripts/ledger.py"))

print("a passing artifact that names the file is coverage")

_ok = _unlinted(_tree([("projects/p/runs/2026-01-02-lint/01-protocol-lint.md",
                        PASS_ART + "\n`protocol/authoring.md:349` is fine\n")]))
check("named by full path, PASS, newer than the edit", _ok[0][1] is not None,
      str(_ok))

_base = _unlinted(_tree([("projects/p/runs/2026-01-02-lint/01-protocol-lint.md",
                          PASS_ART + "\n`authoring.md:349` is fine\n")]))
check("the basename spelling counts too", _base[0][1] is not None, str(_base))

print("and these three are not")

_none = _unlinted(_tree([]))
check("no artifact at all is reported", _none[0][1] is None, str(_none))

_fail = _unlinted(_tree([("projects/p/runs/2026-01-02-lint/01-protocol-lint.md",
                          FAIL_ART + "\n`protocol/authoring.md:349` is wrong\n")]))
check("a FAIL verdict is not coverage", _fail[0][1] is None, str(_fail))

_other = _unlinted(_tree([("projects/p/runs/2026-01-02-lint/01-protocol-lint.md",
                           PASS_ART + "\n`protocol/gates.md:12` is fine\n")]))
check("an artifact naming a different file is not coverage",
      _other[0][1] is None, str(_other))

# The bug this check shipped with. `protocol/authoring.md` passed on
# 2026-09-17-bind-datoro/02-protocol-lint.md, which names that path only as the
# anchor it judged a datoro profile against - so any file ever cited by any
# passing lint would have been exempt from every later edit.
print("an artifact older than the edit is not evidence for it")

_stale = _unlinted(_tree([("projects/p/runs/2026-09-17-bind/02-protocol-lint.md",
                           PASS_ART + "\nAnchor: protocol/authoring.md\n")],
                         art_newer=False))
check("a lint that predates the edit does not cover it",
      _stale[0][1] is None, str(_stale))

# And with both present the newest wins, so the line printed names the lint that
# actually looked at this edit rather than whichever glob came first.
_both = _tree([("projects/p/runs/2026-09-17-bind/02-protocol-lint.md",
                PASS_ART + "\nAnchor: protocol/authoring.md\n")])
_new = _both / "projects/p/runs/2026-10-01-lint/02-protocol-lint.md"
_new.parent.mkdir(parents=True, exist_ok=True)
_new.write_text(PASS_ART + "\n`protocol/authoring.md:349` re-judged\n",
                encoding="utf-8")
os.utime(_new, (3_000_000, 3_000_000))
_pick = _unlinted(_both)
check("the newest qualifying artifact is the one reported",
      _pick[0][1] is not None and "2026-10-01-lint" in _pick[0][1], str(_pick))

print(f"\n{_passed}/{_passed + _failed} passed")
sys.exit(1 if _failed else 0)
