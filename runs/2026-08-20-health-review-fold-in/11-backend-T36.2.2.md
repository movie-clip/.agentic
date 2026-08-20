REPORT 2026-08-20-health-review-fold-in/11
status:      DONE
verdict:     NONE

changed:
  - .github/workflows/dependency-audit.yml — NEW. Triggers `schedule` (weekly, Monday 06:00 UTC) + `workflow_dispatch` only (no `pull_request`/`push`). Steps mirror ci.yml's setup shape (checkout, setup-python 3.12 + pip cache, setup-node 22 + npm cache, `pip install -r services/quant-engine/requirements-dev.txt`, `npm ci` in `apps/desktop`), then runs `python scripts/audit_dependencies.py`, captures its stdout and exit code, writes a human-readable summary (per-ecosystem output plus an explicit outcome line) to `$GITHUB_STEP_SUMMARY`, and fails the job (`exit 1`) only when the script's exit code is `1` (VULNERABILITIES_FOUND). Exit code `3` (SCAN_UNAVAILABLE) writes a plain "scan unavailable, not a vulnerability finding" line to the summary but does not fail the job; any other exit code (in practice only `0`) is reported as clean and does not fail the job either.

verification:
  command:   python -c "import yaml; ..." (parse dependency-audit.yml + check trigger keys) && git diff --stat -- .github/workflows/ci.yml scripts/run_all_tests.py && python scripts/run_all_tests.py
  result:    PASS
  detail: |
    1. YAML validity: `.github/workflows/dependency-audit.yml` parses cleanly via Python's `yaml.safe_load`.
    2. Trigger block: parsed `on:` (PyYAML 1.1 reads the bare `on` key as boolean `True`, which is expected YAML behaviour, not a workflow bug) resolves to exactly `{'schedule', 'workflow_dispatch'}` — no `pull_request`, no `push`.
    3. `git diff --stat -- .github/workflows/ci.yml` — zero output, confirming zero diff from before this order. `git status --porcelain -- .github/workflows/` shows only `dependency-audit.yml` as untracked/new; `ci.yml` does not appear as modified.
    4. `scripts/run_all_tests.py` shows as modified in `git status`, but that diff (26 insertions, a `core.hooksPath` self-install bootstrap) predates and is disjoint from this order — it belongs to the concurrent US-36.1 backend track (T-36.1.1/1.2), already present in the working tree before this ticket started. This order made zero edits to that file (confirmed: my only new/changed file is `.github/workflows/dependency-audit.yml`).
    5. `python scripts/run_all_tests.py` — full green run: backend pytest all passed, frontend vitest "37 passed (37)" test files / "331 passed (331)" tests, tsc clean, dead-code gate (ruff + vulture + knip) clean, dashboard goldens regenerated, final line "All tests passed." Confirms this order introduced no regression to the network-free suite. (The new workflow itself cannot be executed locally — no `act`/runner assumed available, per the order's own verification framing — so it is not exercised end-to-end here; its GitHub Actions execution is scheduled/on-demand only, per design.)

contract_notes:
  - none. No `app/schemas/` file touched, no TS type, no `docs/contracts/<area>-fields.md` field — this ticket is CI/workflow infrastructure only, consuming T-36.2.1's already-built `scripts/audit_dependencies.py` (exit codes 0/1/3) without modifying it.

pack_corrections:
  - none. `capabilities/backend.md` held for this ticket: no schema touched, no test files touched, dead-code gate unaffected (workflow YAML is outside its scanned paths, same non-coverage class as every other `scripts/`-adjacent file).

handoff:
  - "The workflow cannot be triggered or observed end-to-end from this sandbox (no live GitHub Actions runner, no `act`). Its first real execution will be either the initial `schedule` firing or a manual `workflow_dispatch` after this change merges to `main` (`schedule` triggers only evaluate against the default branch). Whoever reviews that first run should expect real findings — order 07's handoff already flagged that live pip-audit/npm-audit runs against this repo's actual pinned dependencies surface genuine advisories (starlette, pypdf, python-multipart, pydantic-settings, python-dotenv, @babel/core) — those are expected first-run findings, not a tooling bug, and per this ticket's non_goals I did not act on any of them."
  - "The job's exit-code branching intentionally treats any code other than exactly `1` as non-failing (including a hypothetical exit code outside the documented 0/1/3 contract) — this is a literal reading of the order's DoD (\"Fail the job ONLY on exit code 1\"), not a defensive catch-all for tooling bugs in `audit_dependencies.py` itself. If that script's exit-code contract ever changes, this workflow's branching would need a matching update."
  - "Summary formatting: the workflow writes the raw combined stdout of `scripts/audit_dependencies.py` (its two `ecosystem: OUTCOME` lines) verbatim inside a fenced code block in `$GITHUB_STEP_SUMMARY`, plus one additional plain-English outcome sentence beneath it (clean / vulnerabilities found / scan unavailable) — this is the full extent of the 'human-readable summary naming which ecosystem and outcome' required by the DoD; no per-package detail is rendered (that detail exists in the raw pip-audit/npm-audit output, which the script does not currently forward beyond its own summary lines — a possible future enhancement, out of this ticket's scope)."

risks:
  - "I did not verify GitHub's actual cron-scheduling behavior for a workflow that has not yet been merged to `main` (schedule triggers are read from the default branch, so this workflow only starts firing weekly once this change lands there) — this is standard GitHub Actions behavior, not something requiring repo-local verification, consistent with how order 07 treated GitHub-hosted-runner network access as given."
  - "The workflow's `working-directory: apps/desktop` step for `npm ci` and its `cache-dependency-path` both assume `apps/desktop/package-lock.json` is committed and current, mirroring ci.yml's own assumption — I did not independently re-verify that file's presence beyond noting ci.yml already depends on it identically."
