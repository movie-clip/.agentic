#!/usr/bin/env python3
"""A network-layer edit with no `protocol-lint` artifact naming it.

PROTOCOL.md binds every lane to files this repo owns: the agent definitions and
skills under `plugins/`, and the core and its extensions under `protocol/`.
Project profiles and capability packs live in each project's own repo now, as
project docs reviewed in its pull requests. `protocol-linter` is the
gate on all of it -- and it only ever runs when someone asks for it, which is
TD-05. A hand edit to any of those files reaches every future dispatch ungated.

What that costs, measured. v0.7.16 shipped an edit to `protocol/authoring.md`
that said *"engines and tests get everything"* about the per-lane
`mcp__project__` grants, fifty lines below a section stating that
`frontend-engineer` was deliberately not given `probe_engine`. One of the two is
false -- the `tools:` lines give that lane three of the five -- and the
contradiction sat live for a day. It was found by `2026-10-01-lint-v0.7.16-
network-edit`, which happened only because `ROADMAP.md` told someone to look.

So this answers one question: for each network-layer file changed, is there a
`protocol-lint` artifact that passed and names it? Nothing here judges the edit.
It finds the absence of the gate, which is the one part of TD-05 a script can
settle.

Scope, and why each exclusion is deliberate:

  in    plugins/*/agents/**, plugins/*/skills/**, protocol/**, PROTOCOL.md
        -- which is `protocol-linter`'s own declared trigger, verbatim. A scope
        wider than the gate's subject reports files the gate would decline
  out   plugins/*/.claude-plugin/** -- the manifest's gate is `claude plugin
        validate`, which the linter runs but does not judge; a version bump is
        not an authoring change
  out   runs/** -- the lint runs themselves; artifacts and ledgers are judged
        by `check_report.py`, and a lint of them would be a category error
  out   README/ARCHITECTURE/ROADMAP/TECH-DEBT -- human-facing, read by
        no lane, and `authoring.md` sends provenance to them on purpose
  out   scripts/** -- code, and its gate is its tests

Evidence, deliberately literal. A `*-protocol-lint.md` artifact somewhere under
`runs/` - where every run that lints a network edit is filed - that (a) has `verdict: PASS`, (b) names the changed file by
repo-relative path or basename, and (c) is **no older than the file it covers**.
The linter's own output format earns (b): a `FAIL` must name the rule, the file
and the line, and a `PASS` names what it covered in `verification.detail`.

(c) is the one that took a bug to find. Without it, `protocol/authoring.md`
passed on a lint from run 2026-09-17-bind-datoro, which names that path only as
the *anchor* it judged a datoro profile against -- a 1990s-era "mentioned
somewhere, therefore covered". Any file ever cited by any passing lint would have
been exempt from every later edit, which is the same shape as the 40-character
window `check_gates` was reading a neighbouring gate's `skipped` through.

Matching on the path is weaker than understanding the artifact and stronger than
trusting that a lint happened.

It cannot be fooled into passing -- the path has to appear in an artifact that
passed. It can report a file a lint did cover without naming, which is why the
default is a warning and `--strict` is opt-in: a check that blocks on its own
false positives is a check people route around.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Repo-relative, forward-slashed, as `git diff --name-only` prints them.
NETWORK = (
    re.compile(r"^plugins/[^/]+/agents/.+\.md$"),
    re.compile(r"^plugins/[^/]+/skills/.+\.md$"),
    re.compile(r"^protocol/.+\.md$"),
    re.compile(r"^PROTOCOL\.md$"),
)


def is_network(path: str) -> bool:
    """True for a file some lane reads as its instructions."""
    return any(p.match(path) for p in NETWORK)


def _git(*args: str) -> list[str]:
    out = subprocess.run(("git", "-C", str(ROOT), *args),
                         capture_output=True, text=True)
    if out.returncode != 0:
        return []
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def changed(against: str = "HEAD") -> list[str]:
    """Network-layer files changed against `against`, staged or not, plus new ones.

    Untracked files count: a brand-new agent definition or capability pack is
    exactly the case that has never been linted, and `git diff` cannot see it.
    """
    paths = set(_git("diff", "--name-only", against))
    paths |= set(_git("diff", "--name-only", "--cached", against))
    paths |= set(_git("ls-files", "--others", "--exclude-standard"))
    return sorted(p for p in paths if is_network(p))


def lint_artifacts() -> list[tuple[Path, str, float]]:
    """Every `protocol-lint` artifact that returned PASS, with its text and mtime."""
    passed = []
    for art in sorted(ROOT.glob("runs/*/*protocol-lint.md")):
        try:
            text = art.read_text(encoding="utf-8", errors="replace")
            mtime = art.stat().st_mtime
        except OSError:
            continue
        verdict = re.search(r"^verdict:\s*(\S+)", text, re.M)
        if verdict and verdict.group(1).upper() == "PASS":
            passed.append((art, text, mtime))
    return passed


def unlinted(paths: list[str]) -> list[tuple[str, str | None]]:
    """Each path, with the artifact that covers it or None.

    A path is covered when a passing artifact names it -- by repo-relative path or
    by basename, since both spellings appear in real findings (`authoring.md:349`
    cites the basename, an order's scope fence cites the full path) -- and that
    artifact is no older than the file. The newest qualifying artifact wins, so
    the reported one is the lint that actually covered this edit.
    """
    arts = lint_artifacts()
    out = []
    for path in paths:
        base = path.rsplit("/", 1)[-1]
        try:
            edited = (ROOT / path).stat().st_mtime
        except OSError:
            edited = 0.0
        hits = [(mtime, art) for art, text, mtime in arts
                if (path in text or base in text) and mtime >= edited]
        best = max(hits)[1] if hits else None
        out.append((path,
                    str(best.relative_to(ROOT)).replace("\\", "/") if best else None))
    return out


def report(against: str = "HEAD") -> list[str]:
    """One line per network-layer file changed with no passing lint naming it."""
    return [f"{path} - changed, and no passing protocol-lint artifact names it"
            for path, hit in unlinted(changed(against)) if hit is None]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--against", default="HEAD",
                    help="git ref to diff against (default HEAD)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 on an unlinted edit instead of exit 0")
    ap.add_argument("--verbose", action="store_true",
                    help="also print the files a lint does cover")
    args = ap.parse_args()

    rows = unlinted(changed(args.against))
    if not rows:
        print("no network-layer file changed")
        return 0

    missing = [p for p, hit in rows if hit is None]
    if args.verbose:
        for path, hit in rows:
            if hit:
                print(f"ok   {path} - {hit}")
    for path in missing:
        print(f"UNLINTED {path}")
    if not missing:
        print(f"{len(rows)} network file(s) changed, each named by a passing lint")
        return 0

    print(f"\n{len(missing)} of {len(rows)} network file(s) changed have no "
          f"passing protocol-lint artifact naming them.")
    print("Dispatch `protocol-linter` over them from this repo before this "
          "ships; the run is filed under `runs/` here (`authoring.md` "
          "§ \"Linting a network edit\"). When the subject is "
          "`authoring.md` or `protocol-linter.md` itself, the anchor is the "
          "other agent files, not the rule text.")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
