REPORT 2026-08-20-health-review-fold-in/12
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_commit_gate.py — NEW. Regression test module (same directory as `test_docs_paths.py`, per T-36.1.1's handoff and the technical plan's placement instruction) proving the commit-freshness gate blocks a commit regardless of which tool issued it, and that the git-level and Bash-tool-level paths stay in agreement. 10 test cases: missing-marker blocks (both entry points), stale-file blocks with the offending filename named in the message (both entry points), fresh-tree allows (both), `.md`-only-change allows (both), a Bash-path command-sniffing guard (a non-`git commit` command must not trigger the check even with no marker present), and `run_all_tests.ensure_git_hooks_wired()` idempotency (calling it twice does not raise, and leaves `core.hooksPath` correctly set).

verification:
  command:   "cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_commit_gate.py -v   (narrow iteration)   then   python scripts/run_all_tests.py   (full suite, from repo root)"
  result:    PASS
  detail: |
    Narrow: `pytest app/tests/test_commit_gate.py -v` — 10 passed in 2.03s.
    Full: `python scripts/run_all_tests.py` completed with "All tests passed."
    (golden regen -> pytest -n auto -> vitest 37 files / 331 tests passed ->
    tsc --noEmit -> dead-code gate --strict: ruff/vulture/knip all clean).
    `.claude/.last-test-pass` was rewritten fresh
    (2026-08-20T16:23:33.482300+00:00) confirming a real green run, not a
    cached marker. `git diff --stat apps/desktop/src/test/dashboardGoldens.ts`
    is empty — no goldens drift to discard. `git status --porcelain` after
    both runs shows my only touched file is
    `services/quant-engine/app/tests/test_commit_gate.py`; every other
    modified/untracked path in the tree (CLAUDE.md, docs/*, scripts/hooks/*,
    scripts/audit_dependencies.py, .github/workflows/dependency-audit.yml,
    test_audit_dependencies.py, test_route_inventory.py,
    requirements-dev.txt, scripts/githooks/pre-commit) belongs to other
    concurrent lanes on this run (T-36.1.1, T-36.2.x, T-36.3.x per the
    technical plan) and was not created or edited by this order.

contract_notes:
  - none — no `app/schemas/`, TS type, or `docs/contracts/<area>-fields.md` field touched. Gate/CI infrastructure only.

pack_corrections:
  - none. `capabilities/testing.md`'s described conventions (narrow-run env var, `test_docs_paths.py`-style placement, containment-over-equality where applicable) matched what I needed; no false premise found.

handoff:
  - "New fixture pattern, not currently in `app/tests/fixtures.py` (deliberately NOT added there — it is specific to this one file's throwaway-git-repo need, not general portfolio/market-data scaffolding the shared module is for): `hook_repo(tmp_path)` in `test_commit_gate.py` builds an isolated git repo at `tmp_path/repo` with a *live copy* of `scripts/hooks/{git_pre_commit,pre_commit_gate,_commit_gate}.py` at the same relative depth (`<repo>/scripts/hooks/`) as the real repo. This is required, not stylistic: `_commit_gate.ROOT` is computed as `Path(__file__).resolve().parents[2]`, i.e. from wherever the module file itself lives, with no env-var or cwd override — so the only way to exercise the real entry points against an isolated tree is to give the tree its own copy of the module at the matching depth. The fixture copies the files fresh from `scripts/hooks/` on every test run (not hand-duplicated logic), so it can never silently drift from whatever the backend lane last shipped there. If a future test needs the same trick for another `scripts/`-rooted, path-relative-to-`__file__` script, this is the pattern to reuse (or promote into `fixtures.py` if a second consumer appears)."
  - "The fixture's baseline commit MUST include a `.gitignore` matching the real repo's (`.claude/.last-test-pass`, `__pycache__/`) — omitting it was my first draft's actual failure mode (4 of 10 tests failed: the untracked `.claude` directory and the `__pycache__` produced by running the copied hook scripts both showed up in `git status --porcelain` as 'changed' files with real-wall-clock mtimes, always newer than the fixed-past-epoch marker, so every 'should allow' scenario spuriously blocked). Anyone extending this fixture should keep it in sync with the real `.gitignore` for any path the hook's own execution or the marker file touches."
  - "`run_all_tests.ensure_git_hooks_wired()` is imported into the test via `sys.path.insert(0, str(scripts_dir))` then `import run_all_tests` — same pattern already used by `test_manage_cache_cli.py` (`manage_cache`) and the concurrently-landed `test_audit_dependencies.py` (`audit_dependencies`). `test_ensure_git_hooks_wired_is_idempotent` is the one test in this file that runs against the REAL repo's git config (not the fixture repo) — unavoidable, since the function under test has no isolation point of its own — but it is idempotent and is exactly what a normal `run_all_tests.py` invocation already does, so this is a no-op side effect in practice, not a new risk."

risks:
  - "I did not add a dedicated test for `git status --porcelain=v1 -z`'s rename-entry handling (`changed_files()`'s comment about `R  new -> old` two-field parsing) — none of this ticket's five ACs exercise a rename, and the technical plan's T-36.1.2 spec doesn't name it. Flagging as a real, currently-uncovered code path in `_commit_gate.changed_files()` if a future change to that function needs a regression net; out of scope for what this order asked for."
  - "Per T-36.1.1's own report, the environment is running other lanes concurrently against the same working tree (I observed `test_audit_dependencies.py` and `test_route_inventory.py` already present, `CLAUDE.md`/several docs files already modified, none of which I created). I did not touch any of those files, and `git status --porcelain` after my own run confirms `services/quant-engine/app/tests/test_commit_gate.py` is my only changed path — but the same shared-marker-file race the backend engineer flagged applies here too: my full `run_all_tests.py` run's fresh marker timestamp (16:23:33 UTC) is what I'm citing as this order's own PASS evidence, and a concurrent lane's simultaneous run against the same checkout could in principle interleave. I did not observe interleaving in my own terminal output this time (unlike the backend engineer's session), but the underlying footgun the backend engineer flagged in their `risks` is still live for this run as a whole, not something my order alone can close."

---
