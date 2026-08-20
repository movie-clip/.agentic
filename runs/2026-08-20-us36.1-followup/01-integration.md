REPORT 2026-08-20-us36.1-followup/01
status:      DONE
verdict:     PASS

changed:
  - none (read-only integration review; this file is the only artifact written)

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_commit_gate.py -v ; python scripts/run_all_tests.py
  result:    PASS
  detail: |
    test_commit_gate.py: 14 passed in 4.14s. All 14 test names read directly
    from the file (not summarized):
      AC6 (original 10, unmodified, verified by exact match against the
      story's Test plan description — missing-marker/AC1-2, stale-file/AC1-2,
      fresh-tree/AC4, .md-exemption/AC5, Bash command-sniffing/AC3, wiring
      idempotency, one test each for both entry points where applicable):
        test_git_hook_blocks_when_marker_missing
        test_bash_hook_blocks_when_marker_missing
        test_git_hook_blocks_on_stale_file
        test_bash_hook_blocks_on_stale_file
        test_git_hook_allows_fresh_tree
        test_bash_hook_allows_fresh_tree
        test_git_hook_allows_md_only_change
        test_bash_hook_allows_md_only_change
        test_bash_hook_ignores_non_commit_commands
        test_ensure_git_hooks_wired_is_idempotent
      AC7 (new, real `git commit` through a `wired_repo` fixture that sets
      `core.hooksPath` to a live copy of the real `scripts/githooks/pre-commit`
      wrapper and calls `subprocess.run(["git","commit",...])` directly —
      not a script invocation):
        test_real_git_commit_is_blocked_when_marker_missing
        test_real_git_commit_is_blocked_on_stale_file
        test_real_git_commit_is_allowed_when_fresh
      AC8 (new, checks git index mode via `git ls-files --stage`, asserts
      `100755`, failure message names `git add --chmod=+x` as the fix):
        test_git_hook_is_tracked_and_executable

    python scripts/run_all_tests.py: exit 0, "All tests passed." Backend 806
    passed (802 pre-follow-up + 4 new AC7/AC8 tests — arithmetic matches
    14-integration.md's prior "802 passed" baseline exactly). Frontend 331
    passed (37 files). tsc clean. Dead-code gate (ruff/vulture/knip) strict-
    clean. `dashboardGoldens.ts` diff confirmed empty (`git diff --stat` /
    `git status --porcelain` both silent on that path) — this is doc/gate
    infrastructure only, no analytics touched, consistent with the epic's
    non-goals.

    Independent sanity checks beyond re-running the suite (this gate reads an
    anchor outside the test file itself, per PROTOCOL.md's "gate that reads
    only the same source the work was built from is not independent" rule):
      - `git ls-files --stage -- scripts/githooks/pre-commit` (run directly,
        not via the test) -> `100755 <sha> 0`, confirming AC8 independently
        of the assertion that checks the identical thing.
      - `git diff --stat .claude/settings.json` -> empty, confirming AC3
        holds at the wiring level, independently re-confirming what
        14-integration.md already established for the pre-follow-up tree.
      - Built a throwaway scratch repo (outside the tracked checkout, in the
        run's scratch dir, deleted after use) with a copy of the real wrapper
        modified so neither `python` nor `python3` name resolves, wired
        `core.hooksPath`, and ran a real `git commit`. Result: exit 1,
        "COMMIT BLOCKED: the commit gate could not find a working Python
        interpreter (tried: python, python3). Install Python or fix PATH."
        This confirms the wrapper's fail-closed behavior for real (a broken
        interpreter-discovery path blocks rather than silently no-ops) and,
        by extension, confirms `test_real_git_commit_is_allowed_when_fresh`
        would fail if that path regressed — the fresh-tree case would then
        also get incorrectly blocked.

contract_notes:
  - none. No `app/schemas/`, TS type, or `docs/contracts/<area>-fields.md`
    field touched by this follow-up. Gate/CI/test infrastructure only.

pack_corrections:
  - none. `capabilities/architecture.md` held up throughout this review —
    no false premise found.

handoff:
  - AC6, AC7, AC8 all genuinely satisfied, not just plausible-looking:
    - AC6 (corrected wording, "fails if the staleness LOGIC regresses"): the
      original 10 tests survive unmodified and still exercise both real
      entry points directly (`git_pre_commit.py`, `pre_commit_gate.py`) via
      `_invoke_git_hook`/`_invoke_bash_hook`, never a reimplementation of
      `_commit_gate.check()`.
    - AC7: `test_real_git_commit_is_blocked_when_marker_missing`,
      `test_real_git_commit_is_blocked_on_stale_file`,
      `test_real_git_commit_is_allowed_when_fresh` (lines 342-380) drive an
      actual `git commit` subprocess through a repo where `core.hooksPath`
      points at a live copy of `scripts/githooks/pre-commit`. This exercises
      git's own decision to invoke the hook, the wrapper's interpreter
      discovery, and `core.hooksPath` resolution — the exact three things
      AC7 names as what AC6's tests could not reach. Independently confirmed
      by my own scratch repro that a broken interpreter-discovery path
      produces a real, git-driven block rather than a pass-through.
    - AC8: `test_git_hook_is_tracked_and_executable` (lines 398-422) checks
      `git ls-files --stage -- scripts/githooks/pre-commit`, asserts mode
      `100755`, and both failure messages name `git add --chmod=+x
      scripts/githooks/pre-commit` as the fix. Currently passing because the
      file genuinely is staged at `100755` on this checkout (confirmed
      independently, not just via the test's own assertion).
  - Interpreter-discovery logic in `scripts/githooks/pre-commit` (lines
    24-28) is sound: tries `python` then `python3` in that order, and treats
    `command -v` success alone as insufficient — it also requires
    `"$PY" -c ""` to actually execute cleanly, which is specifically what
    defeats the Windows Python-Store-stub false positive the comment
    describes. Failure mode (neither works) is not a silent no-op: it prints
    a two-line stderr message naming both tried interpreters and exits 1,
    which git surfaces to the committer verbatim.
  - `ensure_git_hooks_wired()` (`scripts/run_all_tests.py:47-88`) genuinely
    checks `hook.is_file()` before calling `git config core.hooksPath
    scripts/githooks` (line 68), and on a missing target prints a WARNING
    naming exactly why (git silently ignores a hooksPath pointing at nothing)
    and returns without touching git config — it does not advertise a gate
    that cannot fire. This is a real fix, not merely a comment restating
    intent.
  - AC1-AC5 confirmed not regressed: `git diff scripts/hooks/pre_commit_gate.py`
    shows only the extraction into `_commit_gate.check()` — JSON-stdin
    parsing, `GIT_COMMIT_RE`, exit-code-2 contract, and both block-message
    strings are byte-identical to before the refactor. `.claude/settings.json`
    has zero diff. `_commit_gate.py` and `pre_commit_gate.py` were not
    touched by this specific follow-up (per the run's own framing and
    confirmed by content match against `06-backend-T36.1.1.md`'s original
    description) — only the wrapper's interpreter-discovery robustness,
    `run_all_tests.py`'s target-existence check, and the 4 new tests are new
    since the epic's original `14-integration.md` PASS.
  - Scope-creep check: this specific follow-up (the AC6/7/8 gap-closing work)
    touches only the commit-gate area — `scripts/githooks/pre-commit`,
    `scripts/run_all_tests.py`, `services/quant-engine/app/tests/test_commit_gate.py`,
    and the story file itself. The wider working-tree diff also carries
    US-36.2/US-36.3 changes (`.github/workflows/dependency-audit.yml`,
    `scripts/audit_dependencies.py`, `docs/contracts/cache-fields.md`,
    `docs/product/current-product-state.md`, etc.) — those are out of this
    order's scope per its `non_goals`, were already gated PASS by the
    original `14-integration.md`/`15-review.md` for the whole epic, and are
    unrelated to this follow-up.
  - The story file's own Outcome section already records two carried-forward
    SHOULD_FIX items from the original integration pass; I did not find any
    new ones. One of the two is in this order's area and still stands,
    unresolved, not blocking: `_commit_gate.changed_files()`'s rename-entry
    parsing (`git status --porcelain=v1 -z`'s two-field `R` entries) has no
    dedicated regression test — a `git mv`-then-edit path through the shared
    gate logic remains uncovered by either the original 10 or the 4 new
    tests. Worth a follow-up ticket, not this one.

risks:
  - none beyond the carried-forward SHOULD_FIX named above.
