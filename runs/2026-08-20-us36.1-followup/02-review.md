REPORT 2026-08-20-us36.1-followup/02
status:      DONE
verdict:     PASS

changed:
  - none (read-only acceptance review; this file is the only artifact written)

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_commit_gate.py -v
  result:    PASS
  detail: |
    Independently re-run (not trusted from 01-integration.md's cached count):
    14 passed in 4.22s. All 14 collected and named:
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
      test_real_git_commit_is_blocked_when_marker_missing
      test_real_git_commit_is_blocked_on_stale_file
      test_real_git_commit_is_allowed_when_fresh
      test_git_hook_is_tracked_and_executable

    Read directly, not summarized from 01-integration.md:
    services/quant-engine/app/tests/test_commit_gate.py (423 lines),
    scripts/githooks/pre-commit, scripts/hooks/git_pre_commit.py,
    scripts/hooks/pre_commit_gate.py, scripts/hooks/_commit_gate.py,
    scripts/run_all_tests.py.

    AC6 (corrected wording — "fails if the staleness LOGIC regresses"):
    the original 10 tests (lines 145-295) invoke `_invoke_git_hook` /
    `_invoke_bash_hook`, which run `git_pre_commit.py` and
    `pre_commit_gate.py` as real subprocesses against a fixture-repo copy of
    the actual hook files at the correct relative depth — never a
    reimplementation of `_commit_gate.check()`. Confirmed by reading the
    fixture (`hook_repo`, lines 67-106): it copies `HOOK_FILES =
    ["git_pre_commit.py", "pre_commit_gate.py", "_commit_gate.py"]` verbatim
    from `REAL_HOOKS_DIR`. Genuinely satisfied.

    AC7 ("a regression test drives a real git commit... fails if the gate
    does not fire"): `test_real_git_commit_is_blocked_when_marker_missing`,
    `test_real_git_commit_is_blocked_on_stale_file`,
    `test_real_git_commit_is_allowed_when_fresh` (lines 342-380), via the
    `wired_repo` fixture (lines 316-329) which copies the REAL
    `scripts/githooks/pre-commit` wrapper byte-for-byte
    (`wrapper.write_text(REAL_GITHOOK.read_text(...))`), sets
    `core.hooksPath` to point at it, and drives
    `subprocess.run(["git","commit","-m","attempt"], cwd=repo, ...)` — a real
    git-issued commit, not a script call. Independently reasoned through
    what each of AC7's four named parts would need to break for these three
    tests, collectively, to catch it:
      - wrapper: block tests need it to run and exit nonzero — a
        no-op/broken wrapper fails them.
      - core.hooksPath resolution / git's invocation decision: if
        `core.hooksPath` weren't wired, this throwaway repo has no
        `.git/hooks/pre-commit` (a bare `git init`), so `git commit` would
        silently succeed — both block tests assert `returncode != 0` and
        would fail. Caught.
      - interpreter discovery: if totally broken (neither `python` nor
        `python3` resolves), the wrapper's fail-closed branch fires
        unconditionally, so `test_real_git_commit_is_allowed_when_fresh`
        (which requires `returncode == 0`) would fail. Caught.
    Genuinely satisfied as a set, though see one asymmetry noted in `risks`
    below (not a FAIL — the property AC7 exists to prove is still covered).

    AC8 ("fails if the wrapper is not tracked, or tracked non-executable"):
    `test_git_hook_is_tracked_and_executable` (lines 398-423) runs `git
    ls-files --stage -- scripts/githooks/pre-commit` — the git INDEX entry,
    not `os.stat` on the filesystem, correctly avoiding the
    `core.filemode=false` trap this checkout has (confirmed:
    `git config --get core.filemode` -> `false` on this machine). Asserts
    `mode == "100755"`. Both failure messages (untracked case and wrong-mode
    case) name `git add --chmod=+x scripts/githooks/pre-commit` verbatim.
    Independently re-ran the same git command outside the test:
    `git ls-files --stage -- scripts/githooks/pre-commit` ->
    `100755 6965e5edee9e96b4edf30afb214f87974cee0007 0 scripts/githooks/pre-commit`.
    Genuinely satisfied.

    AC3 spot-check: `git diff 20015e3 -- scripts/hooks/pre_commit_gate.py`
    shows the refactor removed only the inline staleness body (`changed_files()`,
    the two block-message string literals) and replaced it with
    `from _commit_gate import check` + `message = check(); if message:
    block(message)`. `json.load(sys.stdin)` parsing, `GIT_COMMIT_RE =
    re.compile(r"\bgit\b[^|;&]*\bcommit\b")`, and `block()`'s `sys.exit(2)`
    are byte-identical before/after. The two message strings moved into
    `_commit_gate.py`'s `MISSING_MARKER_MESSAGE` / `stale_files_message()`
    are character-identical to what was removed. `git diff --stat
    .claude/settings.json` and `git status --porcelain=v1 -- .claude/settings.json`
    both empty — zero diff, `"matcher": "Bash"` unchanged, still calling
    `pre_commit_gate.py`. AC3 not weakened.

    AC5 spot-check: the `.md` exemption lives once, in
    `_commit_gate.check()` (`path.suffix.lower() != ".md"`, line 80 of
    `_commit_gate.py`) — not duplicated per entry point. Both
    `test_git_hook_allows_md_only_change` and `test_bash_hook_allows_md_only_change`
    exist and pass. AC5 not weakened.

contract_notes:
  - none. No schema, TS type, or contracts doc touched by this follow-up.

pack_corrections:
  - none.

handoff:
  - AC6, AC7, AC8 all genuinely satisfied against the story's own wording,
    not superficially. Independent verification (re-run test file, read
    every hook script directly, re-ran the two anchor git commands outside
    pytest, diffed pre_commit_gate.py against its pre-follow-up commit,
    reasoned through what each of AC7's four named parts would need to break
    to be caught) found no case where an AC's test could pass despite the
    underlying property being false.
  - AC1-AC5 not silently weakened by this follow-up. AC3 and AC5 spot-checked
    per the order; the other three (AC1/AC2/AC4) also hold on inspection —
    message text and exit-code contracts in `_commit_gate.py` are unchanged
    from what `pre_commit_gate.py` inlined before, and the fresh-tree-allows
    tests (`test_*_allows_fresh_tree`, `test_real_git_commit_is_allowed_when_fresh`)
    all pass.

risks:
  - Minor test-precision asymmetry in AC7's tests, not a FAIL:
    `test_real_git_commit_is_blocked_when_marker_missing` (test_commit_gate.py:342-352)
    asserts only `result.returncode != 0` and `"COMMIT BLOCKED" in
    result.stderr` — it does not assert the specific `"no test-pass marker
    found"` substring the way `test_real_git_commit_is_blocked_on_stale_file`
    asserts `"code.py"` for its case. Both the staleness-block message and
    the wrapper's own fail-closed "could not find a working Python
    interpreter" message share the `"COMMIT BLOCKED"` prefix, so in
    isolation this one test could pass even if the real block reason were a
    fully broken interpreter path rather than a missing marker. This does
    not leave the underlying property unguarded: (a) a totally broken
    interpreter path is still caught by `test_real_git_commit_is_allowed_when_fresh`
    failing (it requires the full chain to succeed, including interpreter
    discovery), and (b) the exact "no test-pass marker found" message
    content is independently pinned by `test_git_hook_blocks_when_marker_missing`
    / `test_bash_hook_blocks_when_marker_missing` (AC6, direct-invocation).
    Worth tightening (add the specific message-substring assertion) in a
    follow-up ticket for symmetry with its sibling test, not blocking.
  - Repo-state observation, not an AC violation: as of this review,
    `scripts/hooks/_commit_gate.py`, `scripts/hooks/git_pre_commit.py`, and
    `services/quant-engine/app/tests/test_commit_gate.py` are untracked
    (`??` in `git status`) and `scripts/hooks/pre_commit_gate.py` /
    `scripts/run_all_tests.py` are modified-but-unstaged; only
    `scripts/githooks/pre-commit` is staged (`A`). Nothing from this
    follow-up is committed to `HEAD` yet. AC8's "tracked by git" reads as
    satisfied by the git INDEX state (staged = tracked in git's own
    vocabulary), which the test correctly checks and which is genuinely true
    right now — so this is not an AC8 failure. Flagging only because the
    story's `Status: Done (2026-08-20)` and `Outcome` section read as
    describing shipped, committed work; per this project's "no agent
    commits" convention that gap is expected to close when the human commits,
    but a human reading "Done" without checking `git status` could be
    surprised nothing is on `HEAD` yet.
