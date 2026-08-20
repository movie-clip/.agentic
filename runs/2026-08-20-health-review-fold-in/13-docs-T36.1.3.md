REPORT 2026-08-20-health-review-fold-in/13
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\portfolio\CLAUDE.md — "Mechanical gates" section, "Commit gate hook" bullet: replaced the interim "that gap is open, tracked under Epic 36 (F-R1)" wording with a description of the now-real mechanism — the git-level `scripts/githooks/pre-commit` (execing `scripts/hooks/git_pre_commit.py`) as the actual enforcement boundary wired via `git config core.hooksPath scripts/githooks`; how `core.hooksPath` gets set (the `scripts/run_all_tests.py` `ensure_git_hooks_wired()` bootstrap, run early in every suite invocation); the residual honest caveat that a clone which has never run the suite is not yet wired; and the existing `scripts/hooks/pre_commit_gate.py` Claude Code PreToolUse hook retained as a faster-feedback duplicate, not the boundary itself. Dropped the "(F-R1)" citation entirely.
  - C:\projects\investments\.agentic\projects\portfolio\project.md — "Mechanical gates — never bypass" section, "Commit gate hook" bullet: same update applied (this file had already been through one interim edit under order 03 in this run — this is the second edit named in the work order). Dropped the "(F-R1)" citation.

verification:
  command:   grep -n "core.hooksPath\|githooks\|git_pre_commit" CLAUDE.md ; grep -n "review-2026-08-20-findings" CLAUDE.md ; grep -n "core.hooksPath\|githooks\|git_pre_commit" project.md ; grep -n "review-2026-08-20-findings" project.md
  result:    PASS
  detail: |
    Ran as Grep-tool calls against each file individually (not a literal shell
    invocation with a repo-root cwd), one pattern per call, matching the work
    order's four named checks:

    (1) CLAUDE.md, `core.hooksPath|githooks|git_pre_commit` — 1 match, line 155
        (the rewritten "Commit gate hook" bullet):
        "- **Commit gate hook** — enforced at two layers, both checking the
        same thing (`.claude/.last-test-pass` exists and is fresher than
        every changed non-`.md` file; the marker is written only by a fully
        green `run_all_tests.py` run). The **git-level**
        `scripts/githooks/pre-commit` (a POSIX shell wrapper, wired via
        `git config core.hooksPath scripts/githooks`, execing
        `scripts/hooks/git_pre_commit.py`) is the actual enforcement
        boundary — it fires on every `git commit` regardless of which tool
        or terminal invoked git, because it runs inside git itself rather
        than inside any particular tool's interception layer.
        `core.hooksPath` is local git config, not something committed to the
        repo; `scripts/run_all_tests.py` idempotently sets it early in every
        run (`ensure_git_hooks_wired()`), so any dev or agent session that
        has run the suite at least once has the git-level hook wired — a
        clone that has never run the suite yet does not. The **Claude Code**
        `scripts/hooks/pre_commit_gate.py` (PreToolUse, wired in
        `.claude/settings.json`, matched on the `Bash` tool) remains as a
        faster-feedback duplicate inside agent sessions, not the boundary
        itself. If a commit is blocked, re-run the suite — do not try to
        bypass either hook."

    (2) CLAUDE.md, `review-2026-08-20-findings` — no matches (citation
        dropped, confirmed).

    (3) project.md, `core.hooksPath|githooks|git_pre_commit` — 3 matches,
        lines 192-193, 196-197 (within the rewritten "Commit gate hook"
        bullet, lines 189-203):
        line 192: "  `scripts/githooks/pre-commit` (wired via `git config core.hooksPath"
        line 193: "  scripts/githooks`, execing `scripts/hooks/git_pre_commit.py`) is the actual"
        line 196: "  inside a tool's interception layer. `core.hooksPath` is local git config,"

    (4) project.md, `review-2026-08-20-findings` — no matches (citation
        dropped, confirmed).

    All four checks match the work order's expected shape. I did not run
    `python scripts/run_all_tests.py` — this order is a doc-only edit to a
    repo-root markdown file and an agentic-root pack file, neither of which
    is inside the suite's scan scope, and the work order named only the
    grep-based check as verification.

contract_notes:
  - none. No schema, TS type, or `docs/contracts/<area>-fields.md` field is touched — this is a doc-only correction of the "Mechanical gates" section in two onboarding files.

pack_corrections:
  - none. This order's own scope *was* the pack correction (`project.md`'s "Mechanical gates — never bypass" section) named directly in the work order, not one arriving via `pack-corrections.md` — so it is applied here as an ordinary in-scope edit, not logged as a separate correction entry.

handoff:
  - "T-36.1.3 is closed. Both `CLAUDE.md` and `project.md` now describe the real, already-verified (per `06-backend-T36.1.1.md`) git-level commit-gate mechanism, including the `run_all_tests.py` bootstrap step that was previously unmentioned anywhere in either doc. Neither file references `docs/product/review-2026-08-20-findings.md` or 'F-R1' any longer — T-36.3.5 (retiring that findings doc, gated on the Epic 36 PRD existing) has one fewer inbound citation to worry about breaking."
  - "I did not touch the 'Tests — canonical entrypoint' comment block in CLAUDE.md (lines ~116-118, '# the pre_commit_gate hook (see \"Mechanical gates\" below) requires that marker...') — it was already accurate (it names the marker-freshness requirement generically, without claiming which hook enforces it) and the work order's scope was the 'Mechanical gates' section specifically, not this adjacent reference to it."
  - "Neither CLAUDE.md's nor project.md's Mechanical gates section makes any claim about it being 'impossible to bypass', a user manually unsetting `core.hooksPath`, or someone deleting `scripts/githooks/pre-commit` — per the work order's non_goals, I described only what T-36.1.1 actually built (the mechanism + its one named residual gap: a never-yet-run-suite clone isn't wired), not a stronger guarantee."

risks:
  - none.

---
