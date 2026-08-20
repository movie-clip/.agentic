REPORT 2026-08-20-health-review-fold-in/14
status:      DONE
verdict:     PASS

changed:
  - none (read-only integration review; this file is the only artifact written)

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail: |
    Full run against the complete working tree (all lanes' changes together,
    not per-lane isolation): golden regen -> backend pytest -> frontend
    vitest -> tsc --noEmit -> dead-code gate --strict. Exit code 0.
    Backend: "802 passed, 45 warnings in 20.36s". Frontend: "Test Files 37
    passed (37)", "Tests 331 passed (331)". Dead-code gate: ruff/vulture/knip
    all clean, STRICT clean. Final line: "All tests passed." Confirmed via
    `git ls-files --stage scripts/githooks/pre-commit` that the executable
    bit (100755) is preserved in the index, not just on disk. Confirmed
    `.claude/settings.json` has zero diff (AC3's "Bash path unchanged"
    holds at the wiring level, not just the message-text level). Confirmed
    `.github/workflows/ci.yml` has zero diff (US-36.2 AC4: the new scan is
    genuinely not wired into the existing gate).

contract_notes:
  - none. Confirmed across all 8 lane reports and my own design pass: no
    `app/schemas/` file, TS type, or `docs/contracts/<area>-fields.md` field
    is touched anywhere in this slice. Entirely gate/CI/doc infrastructure.

pack_corrections:
  - none new from this review. The one outstanding entry
    (`<agenticRoot>/runs/2026-08-20-health-review-fold-in/pack-corrections.md`,
    "New learning... core.filemode=false") is present, complete, and still
    correctly unapplied (it's a queued close-out item, not a live defect) —
    see risks below for confirmation detail.

handoff:
  - "No change requests filed. Every AC across US-36.1 (AC1-AC6), US-36.2
    (AC1-AC5), and US-36.3 (AC1-AC9) is satisfied by what's actually in the
    working tree, verified by direct read of the code/docs/workflow — not
    just by trusting the lane reports' claims. Detail below."
  - "Cross-lane coherence, all four DoD-named checks confirmed by direct
    code read (not just report-trusting): (a) `_commit_gate.py`'s `check()`
    is the single shared entrypoint; `git_pre_commit.py` and
    `pre_commit_gate.py` both import it and neither re-derives the
    staleness rule (confirmed via `git diff scripts/hooks/pre_commit_gate.py`
    — the refactor removed the duplicated logic cleanly, preserved message
    text verbatim); `test_commit_gate.py` exercises both real entry points
    against a throwaway git repo carrying a live copy of the three hook
    files, not a reimplementation. (b) `audit_dependencies.py`'s
    `classify(returncode, stdout, stderr) -> Outcome` and its
    `EXIT_CLEAN=0 / EXIT_VULNERABILITIES_FOUND=1 / EXIT_SCAN_UNAVAILABLE=3`
    contract is consumed by `dependency-audit.yml` exactly as documented —
    the workflow captures `audit_dependencies.py`'s real exit code via
    `$GITHUB_OUTPUT`, fails the job only on `1`, and writes a distinct
    non-failing summary line on `3`. (c) T-36.3.2a's doc fix
    (`current-product-state.md` '12'->'15 route modules', three new rows)
    and T-36.3.2b's `test_route_inventory.py` were read together: the test's
    regex-parsed doc state and the actual `app/api/routes/` directory match
    today, and report 09 confirms the test landed green on first run against
    the already-corrected doc (no red-then-fixed step). (d) T-36.1.3's
    `CLAUDE.md`/`project.md` correction was diffed directly
    (`git diff CLAUDE.md`) — it accurately names the real mechanism
    including the `run_all_tests.py` `ensure_git_hooks_wired()` bootstrap
    (confirmed present at `scripts/run_all_tests.py:47-68`, called at
    line 145) and correctly omits the Windows-filemode gotcha, which
    belongs in the agent-facing capability pack (queued in
    `pack-corrections.md`) rather than in the reader-facing 'how the gate
    works' doc section — that's the right routing, not a gap."
  - "No lane touched a file outside its declared scope. `git status
    --porcelain=v1` / `git diff --stat` on the full working tree matches
    exactly the union of what all 8 reports' `changed` sections claim, with
    zero unexplained entries: CLAUDE.md, project.md (agentic root, T-36.1.3's
    named exception), 4 docs/** files, scripts/githooks/pre-commit (new,
    +x), scripts/hooks/{_commit_gate,git_pre_commit}.py (new),
    scripts/hooks/pre_commit_gate.py (edit), scripts/run_all_tests.py
    (edit), scripts/audit_dependencies.py (new),
    .github/workflows/dependency-audit.yml (new),
    requirements-dev.txt (edit), and three new app/tests/**.py files —
    all test-engineer-authored, none touching production code.
    `docs/product/review-2026-08-20-findings.md` remains untouched
    (confirmed still untracked, predates this run, correctly deferred to
    T-36.3.5 which is out of scope for this pass)."
  - "pack_corrections queue confirmed complete: the Windows
    `core.filemode=false` gotcha from order 06 is present in
    `pack-corrections.md` verbatim with a concrete replacement/addition
    instruction, and is correctly still unapplied (queued for the close-out
    docs dispatch, not a mid-run defect). Verified the actual staged file
    (`git ls-files --stage scripts/githooks/pre-commit` -> `100755`) shows
    the workaround the note describes was applied correctly in practice,
    not just described."
  - "Real vulnerability findings (starlette, pypdf, python-multipart,
    pydantic-settings, python-dotenv, @babel/core) surfaced by order 07's
    and order 11's live design-verification runs are correctly un-acted-
    upon: `requirements.txt` does not appear in `git status` at all
    (zero diff), and neither order's `changed` section touches it. This is
    exactly what every relevant ticket's non_goals required."

risks:
  - "SHOULD_FIX (not blocking): `audit_dependencies.py`'s `main()` contains
    the cross-ecosystem priority rule (`VULNERABILITIES_FOUND` beats
    `SCAN_UNAVAILABLE` when the two ecosystems disagree, lines 149-153) but
    no test exercises `main()` itself — only `classify()` is unit-tested
    (order 10's own risks section flagged this explicitly). `main()` is
    thin today, but a future edit to the priority ordering would not be
    caught by the existing suite. Worth a small follow-up test mocking
    `_run_pip_audit`/`_run_npm_audit`, not urgent enough to block this
    slice."
  - "SHOULD_FIX (not blocking): `_commit_gate.changed_files()`'s
    rename-entry parsing (`git status --porcelain=v1 -z`'s two-field `R`
    entries, handled by the `entry[3:]` slicing plus the code comment at
    lines 55-57) has no regression test (order 12's own risks section
    flagged this). A `git mv`-then-edit scenario is a real, currently-
    uncovered path through the shared gate logic both hook entry points
    depend on."
  - "Non-blocking maintenance note, surfaced by both order 07 and order 10
    independently: the npm-audit-network-failure marker text in both
    `audit_dependencies.py`'s `_UNAVAILABLE_MARKERS` list and
    `test_audit_dependencies.py`'s `_NPM_AUDIT_NETWORK_ERROR_STDERR`
    fixture is written from documented npm/Node conventions, not an
    observed real failure (network was reachable in both sessions). Worth
    diffing against `dependency-audit.yml`'s first real scan-unavailable
    run, whenever one occurs, per order 10's own handoff note — recorded
    here so it isn't lost before that happens."
  - "Operational note, not an engineering defect in this slice: order 06's
    report flagged that multiple lanes ran `python scripts/run_all_tests.py`
    concurrently against the same shared working tree and the same
    `.claude/.last-test-pass` marker file during this run, and that it
    observed (but correctly did not rely on) interleaved terminal output
    from what appeared to be a concurrent invocation. Every lane's actual
    PASS claim in this run was independently re-verified by me against the
    current tree state, so nothing here is unverified — but the
    shared-marker race the backend engineer flagged is a real footgun for
    future concurrent-lane dispatches in this network, worth the
    orchestrator's attention outside this specific review."
  - "I did not re-derive or independently recompute anything quant/
    methodology-related, per this slice's own cross-cutting note (confirmed
    by my own prior design pass and independently reconfirmed here): no
    ticket in Epic 36 touches `analytics/`, a formula, a weighting basis, or
    a trust classification, so no quant-audit gate was warranted or
    dispatched for this slice, consistent with the gate-ordering rule in
    PROTOCOL.md."

---
