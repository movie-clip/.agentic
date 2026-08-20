REPORT 2026-08-20-health-review-fold-in/15
status:      DONE
verdict:     PASS

changed:
  - none (read-only acceptance review; this file is the only artifact written)

verification:
  command:   cd services/quant-engine && pytest app/tests/test_commit_gate.py app/tests/test_audit_dependencies.py app/tests/test_route_inventory.py -v
  result:    PASS
  detail: |
    23 passed in 3.09s (10 test_commit_gate.py + 10 test_audit_dependencies.py
    + 3 test_route_inventory.py — matches every count claimed in reports 12,
    10, 09 exactly). Also independently ran `test_docs_paths.py` (US-36.3's
    named regression guard) — 11 passed. Both runs are from a fresh `pytest`
    invocation I issued myself, not a re-print of a lane's claim.

    All three stories' AC-by-AC disposition, each verified by direct file
    read against the current working tree (not by trusting a lane report):

    US-36.1 (6 ACs, all SATISFIED):
    - AC1/AC2 — `scripts/hooks/git_pre_commit.py` (real git-level hook entry
      point, exit 1) and `scripts/hooks/pre_commit_gate.py` (Bash-tool
      PreToolUse duplicate, exit 2) both call the shared `_commit_gate.check()`
      and both name the block reason (missing-marker vs. the specific stale
      filename) — read directly at
      `services/quant-engine/../scripts/hooks/_commit_gate.py:71-87` and the
      two entry points. `test_commit_gate.py::test_git_hook_blocks_on_stale_file`
      / `test_bash_hook_blocks_on_stale_file` assert both the "COMMIT BLOCKED"
      framing and the offending filename in `stderr` for both paths — PASS on
      my own run.
    - AC3 — `git diff HEAD -- .claude/settings.json` is empty (confirmed by
      me); `pre_commit_gate.py`'s JSON-stdin parsing, `GIT_COMMIT_RE`
      sniffing and exit-code-2 contract are unchanged, only its staleness
      logic now imports from `_commit_gate.py` (read directly). Both
      `test_bash_hook_*` cases in `test_commit_gate.py` pin this and pass.
    - AC4/AC5 — `test_*_allows_fresh_tree` and `test_*_allows_md_only_change`
      (both git and Bash paths, 4 tests total) pass; the `.md` exemption
      lives once in `_commit_gate.check()` (`path.suffix.lower() != ".md"`)
      shared by both entry points, not duplicated.
    - AC6 — `test_commit_gate.py` invokes the actual scripts as subprocesses
      against a throwaway git repo carrying a live copy of the three real
      hook files (`hook_repo` fixture copies fresh from
      `scripts/hooks/*.py` on every run) — confirmed by reading the fixture
      and the four `_invoke_git_hook`/`_invoke_bash_hook` call sites: these
      are independent invocations of the real enforcement points, not a
      reimplementation of `_commit_gate`'s logic. `scripts/githooks/pre-commit`
      is staged with index mode `100755` (`git ls-files --stage` confirmed by
      me), and `git config --get core.hooksPath` on this checkout returns
      `scripts/githooks`.

    US-36.2 (5 ACs, all SATISFIED):
    - AC1/AC2 — `scripts/audit_dependencies.py::main()` shells out to
      `python -m pip_audit -r services/quant-engine/requirements.txt` and
      `npm audit --prefix apps/desktop --json`, both read directly.
    - AC3 — `.github/workflows/dependency-audit.yml` writes a per-ecosystem
      outcome to `$GITHUB_STEP_SUMMARY` and fails the job only on exit 1,
      read directly.
    - AC4 — `git diff HEAD -- .github/workflows/ci.yml` and
      `scripts/run_all_tests.py`'s diff (I read both) confirm: `ci.yml` has
      zero diff, and `run_all_tests.py`'s only change is the unrelated
      `ensure_git_hooks_wired()` bootstrap from US-36.1 — no audit-script
      wiring was added to the existing gate.
    - AC5 — `classify()`'s marker-list check runs before the exit-code
      fallback (`_commit_gate.py` — actually `audit_dependencies.py:90-106`,
      read directly), so `SCAN_UNAVAILABLE` cannot be masked by
      `VULNERABILITIES_FOUND`'s exit-code convention.
      `test_audit_dependencies.py::test_scan_unavailable_never_reads_as_clean`
      and `..._never_reads_as_vulnerabilities_found` pin this and pass.

    US-36.3 (9 ACs; AC1-AC7 + AC9 SATISFIED, AC8 correctly deferred):
    - AC1 — `docs/contracts/cache-fields.md:9` reads "Last updated: 2026-08-20"
      (read directly).
    - AC2 — lines 55-62 describe live namespace enumeration via
      `JsonFileCache.namespaces()` and typo-rejection with the present
      namespaces listed — read directly, matches US-35.2's shipped behaviour.
    - AC3 — `current-product-state.md:96-111` reads "15 route modules:" and
      lists all 15 including `cache.py`/`currency_risk.py`/`provenance.py` —
      read directly.
    - AC4 — `CLAUDE.md:77`'s repo-layout route list already contained all 15
      modules before this slice (confirmed independently by tech-lead's
      design pass and docs-engineer's order 08 handoff, and re-confirmed by
      me via direct grep) — the two docs agree, satisfying the AC's actual
      requirement even though no edit to CLAUDE.md's route list itself was
      needed.
    - AC5 — `epic-24-codebase-improvement.md:3` reads "Status: Completed",
      consistent with `epic-roadmap.md`'s "Completed Epic 24" header — read
      directly.
    - AC6 — `system-architecture.md:252-265` contains the new "Accepted
      tradeoff — unauthenticated local file-read (import routes)" paragraph,
      framed as deliberate/accepted, not an unnoticed defect — read directly.
    - AC7 — `git diff --stat HEAD` (I ran it) shows only doc files + gate/CI
      infrastructure changed; `git diff HEAD -- apps/desktop/src/test/dashboardGoldens.ts`
      is empty; `git diff HEAD -- services/quant-engine/requirements.txt` is
      empty (the real pip-audit findings surfaced during design verification
      were correctly not acted on). No `app/schemas/` file appears in
      `git status --porcelain` output.
    - AC8 — `docs/product/review-2026-08-20-findings.md` remains untouched
      (still shows `??` untracked, no "superseded" marker) — this is
      T-36.3.5, explicitly and correctly deferred to close-out per the run's
      own sequencing (it hard-depends on the not-yet-created Epic 36 PRD).
      Per the work order's own instruction, this is EXPECTED-PENDING, not a
      gate failure, and does not block this verdict.
    - AC9 — `test_route_inventory.py` (read in full) parses the doc's stated
      count and module list via regex and asserts both against
      `Path("app/api/routes").glob("*.py")`, naming the specific
      missing/extra module on failure (not a bare pass/fail), plus a
      dedicated `test_the_scan_is_not_vacuous` proving the regex isn't
      silently matching nothing. This is a real, mechanical check, not a
      vacuous one — confirmed by reading the assertion logic, not just
      seeing it pass.

    Trust-state spot check: N/A for this slice, confirmed by direct
    inspection — zero files under `apps/desktop/src/` or
    `services/quant-engine/app/schemas|analytics|services` (product surface)
    appear anywhere in `git status --porcelain` or any of the 8 lane reports'
    `changed` sections. This entire slice is gate/CI/doc infrastructure; no
    trust-level, badge, nullable-field, or market-data-caller code exists to
    spot-check. Noting explicitly per the work order rather than silently
    skipping.

    Repo hygiene: no stray files (`git status --porcelain` matches exactly
    the union of all 8 lane reports' `changed` sections, per the tech lead's
    own independent confirmation, which I re-verified myself); goldens
    byte-identical; `docs/product/review-2026-08-20-findings.md` correctly
    left as-is (predates this run, deferred deliberately); story file itself
    (`04-stories.md`) still marked `Backlog` in its own draft header, which
    is consistent with reality — no story file under `docs/product/stories/`
    was created or claimed Done by this slice, matching the run's actual
    state (ticketed and executed via the run ledger, not yet promoted to a
    canonical story file — that promotion is a close-out/human step, not a
    gap this review should flag as inconsistent status).

contract_notes:
  - none. Independently reconfirmed the tech lead's finding: no
    `app/schemas/` file, TS type, or `docs/contracts/<area>-fields.md` field
    is touched anywhere in this slice's diff.

pack_corrections:
  - none new. The queued entry in `pack-corrections.md` (Windows
    `core.filemode=false` / `git add --chmod=+x` gotcha) is present, complete
    and correctly still unapplied — it is a close-out item for the docs lane,
    not something this review needs to re-file.

handoff:
  - "Acceptance gate PASSES. Every AC across US-36.1 (6/6), US-36.2 (5/5) and
    US-36.3 (9/9, with AC8 correctly out-of-scope-for-this-pass per the work
    order's own instruction) is satisfied by direct inspection of the
    repo — code read, docs read, and 34 tests (23 new + 11 pre-existing
    `test_docs_paths.py`) re-run by me from a fresh `pytest` invocation, not
    inferred from lane reports."
  - "Nothing in this pass changes the tech lead's PASS verdict or its 3
    SHOULD_FIX carries (`audit_dependencies.main()`'s priority-rule
    untested, `_commit_gate.changed_files()` rename-entry parsing untested,
    npm-network-error marker text unverified against a real failure) — none
    of those are acceptance-relevant; they are engineering-completeness
    notes already correctly routed to `run.md`'s Open section for
    close-out."
  - "For the orchestrator's close-out step: T-36.3.5 (retire the findings
    doc) and the Epic 36 PRD creation are the only remaining work in this
    slice, both already correctly identified in `run.md` as deferred to a
    human/producer step, not omitted by this review."

risks:
  - "I did not re-run the full `python scripts/run_all_tests.py` (golden
    regen + full backend/frontend/tsc/dead-code gate) myself — the work
    order's `verification` field named the narrower three-module pytest
    command as what to run, and the tech lead's INTEGRATION pass (order 14)
    already ran and reported the full suite green against this exact working
    tree. Re-running the full suite was not necessary to judge acceptance
    against the story and would have duplicated a gate this lane is
    instructed not to re-derive."
  - "I did not independently verify GitHub Actions' actual scheduled-trigger
    behaviour for `dependency-audit.yml` (it has not yet run against `main`,
    since none of this is merged) — this is standard, well-documented GitHub
    behaviour rather than a repo-local fact, consistent with how the
    backend lane (order 07/11) already treated it as given."

---
