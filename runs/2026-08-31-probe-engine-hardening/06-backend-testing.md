REPORT 2026-08-31-probe-engine-hardening/06
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/mcp_server/tools/testing.py — `_run` gains keyword-only `timeout=None`, passed to `subprocess.run`; `TimeoutExpired` propagates. see § testing.py changes
  - services/quant-engine/app/mcp_server/tools/testing.py — new local `TIMEOUTS` dict + `DIFF_MAX_LINES`; new helpers `_partial_output`, `_timeout_result`, `_bound_diff`. see § testing.py changes
  - services/quant-engine/app/mcp_server/tools/testing.py — `run_tests_impl` catches `TimeoutExpired` -> structured timeout result; normal path gains `timed_out: False`. see § testing.py changes
  - services/quant-engine/app/mcp_server/tools/testing.py — `check_gates_impl` wraps each of its 3 `_run` calls in its own try/except; gains top-level `timeouts` list + per-gate `timed_out`. see § testing.py changes
  - services/quant-engine/app/mcp_server/tools/testing.py — `reset_goldens_impl` captures `git diff --stat` then a bounded `git diff` before `git checkout --`; returns `discarded` / `diff_stat` / `diff` / `diff_truncated` / `timed_out`. see § testing.py changes

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q
  result:    FAIL
  detail:    2 failed, 31 passed in 0.78s. Both failures are class (a) predicted by 04 § 6 / § 8 / risks and are WO-E's: TestGates::test_check_gates_reports_every_gate (exhaustive key-set now sees added `timeouts`) and TestGates::test_check_gates_flags_goldens_drift (local `fake_run` stub rejects the new `timeout=` kwarg). No class (b) unexpected failures.

contract_notes:
  - No schema touched — app/schemas/ untouched (AC-G2). testing.py still imports BACKEND_DIR / FRONTEND_DIR / TEST_PASS_MARKER / npx_command from scripts/run_all_tests.py, import line unchanged.
  - .agentic backend.md + testing.md suite-runner tool descriptions now lag: they must name the structured `timed_out` result and `reset_goldens`'s `diff_stat` / `diff` capture. Owned by docs close-out WO-F (T-43.2.4); non-goals forbid me editing packs.

pack_corrections:
  - none

handoff:
  - WO-E: update TestGates::test_check_gates_reports_every_gate key-set to `{deadcode, typecheck, goldens_drifted, timeouts, commit_gate}` (was 4 keys). Per 04 § 8.
  - WO-E: update the local `fake_run` stub in TestGates::test_check_gates_flags_goldens_drift to accept `*, timeout=None` (or `**kwargs`). Per 04 § 6a / § 8.
  - `_run` signature is now `_run(command, cwd, extra_env=None, *, timeout=None)`; `extra_env` stays positional index 2. TestRunTestsParsing `run.call_args[0][2]` assertions (lines 195, 204) still pass — verified this run.
  - `run_tests_impl` unknown-scope early return is unchanged and deliberately carries no `timed_out` key (never reaches `_run`).
  - New coverage WO-E should add — see § WO-E coverage.
  - Timeout result / bounded-diff shapes WO-E asserts against — see § result shapes.

risks:
  - `full` 1800s budget was NOT measured against a real `python scripts/run_all_tests.py` wallclock — that run is the full 5-stage gate and not cheap to spend here. Left as designed; 1800s is well above a typical local full-suite duration. If CI's full-suite wallclock nears 30 min, raise `TIMEOUTS["full"]`.
  - Core protocol § 6 says `status: DONE` requires `verification.result: PASS`. This order's DoD instead defines completion as "no class (b) failure remains" and 04 § 10 expects WO-C to "report done" so WO-E can follow. Reporting DONE per the order; the 2 red tests are class (a) and WO-E's. Flagging the tension per protocol.
  - `check_gates_impl` return-dict key order changed (`timeouts` inserted before `commit_gate`). No test asserts order and dict order is not contractual; noted because WO-E already touches the key-set test.
  - `_timeout_result` uses `TIMEOUTS[scope]` for `timeout_seconds`; only reachable for the four real scopes (unknown scope returns earlier), so the lookup is always safe.

## Orchestrator brief

WO-C (F-4 / F-5) complete in one file: `services/quant-engine/app/mcp_server/tools/testing.py`.
Verification is FAIL with exactly the 2 predicted class (a) failures, both owned by WO-E
(test lane) — no class (b). Sections below: § testing.py changes (what landed, key by key),
§ WO-E coverage (cases the test lane must add), § result shapes (dict shapes WO-E asserts
against). Route the two `handoff` WO-E bullets and the `contract_notes` pack-lag bullet.

## testing.py changes

`_run(command, cwd, extra_env=None, *, timeout=None)` — `timeout` keyword-only so
positional call sites and `run.call_args[0][2]` (extra_env) assertions are
untouched. `subprocess.run(..., timeout=timeout)`; `TimeoutExpired` propagates,
`_run` does not catch. `timeout=None` is the documented no-op.

`TIMEOUTS` (local dict, seconds): `full 1800 / backend 600 / frontend 600 /
typecheck 300 / gate 300 / git 30`. Not imported, restates nothing
`scripts/run_all_tests.py` owns (it has no per-call timeout). `DIFF_MAX_LINES =
120`.

Helpers: `_partial_output(exc)` — `(exc.stdout or "") + "\n" + (exc.stderr or
"")`, stripped. `_timeout_result(scope, command, cwd, exc)` — the structured
dict. `_bound_diff(text) -> (text, truncated)` — whole at/under
`2*DIFF_MAX_LINES+1` (241) lines, else head 120 + `... <n> lines elided ...` +
tail 120, `truncated=True`.

`run_tests_impl` — `_run` call wrapped in `try/except subprocess.TimeoutExpired`
-> `return _timeout_result(...)`. Normal return dict gains `"timed_out": False`;
all other keys unchanged.

`check_gates_impl` — deadcode / typecheck / drift each in their own
`try/except`. `timeouts: list[str]` collects `"deadcode"` / `"typecheck"` /
`"goldens"` per whichever timed out (`[]` normally). `deadcode` and `typecheck`
sub-dicts gain `"timed_out": bool`. `goldens_drifted` stays `bool`, `False` if
its `git status` timed out. New top-level key `timeouts`. Full key-set:
`{deadcode, typecheck, goldens_drifted, timeouts, commit_gate}`.

`reset_goldens_impl` — three `_run` calls in strict order, each
`timeout=TIMEOUTS["git"]`: `git diff --stat` -> `diff_stat`; `git diff` ->
`_bound_diff` -> `diff` + `diff_truncated`; then `git checkout --`. Steps 1-2
run before step 3, so a checkout failure still returns the pre-checkout
`diff_stat` / `diff` alongside `ok: False` + `stderr`. No drift =>
`discarded: False`, `diff_stat: ""`, `diff: ""`. `timed_out` True if any of the
three git calls expired.

## WO-E coverage

- `run_tests_impl` TimeoutExpired path returns `timed_out: True`,
  `exit_code: None`, `timeout_seconds` set, `failures: []`, `ok: False`.
- `check_gates_impl` per-gate timeout: one gate raises `TimeoutExpired`, the
  other two still return real results, the timed-out gate is named in
  `timeouts`.
- `reset_goldens_impl` no-drift => `discarded: False`, `diff_stat: ""`,
  `diff: ""`, `diff_truncated: False`.
- `reset_goldens_impl` with drift => `diff_stat` / `diff` populated; assert the
  two capture `_run` calls happen before the `git checkout` call (call order).
- `reset_goldens_impl` checkout failure still returns the pre-checkout
  `diff_stat` / `diff`, with `ok: False`.
- `reset_goldens_impl` long diff (> 241 lines) => `diff_truncated: True` and the
  elision marker present.

## result shapes

`run_tests_impl` timeout result:
`ok=False, timed_out=True, scope, command, cwd, timeout_seconds, exit_code=None,
failure_count=0, failures=[], failures_truncated=False, tail`.

`run_tests_impl` normal result: exactly as before plus `timed_out=False`.

`reset_goldens_impl`:
`ok, path, stderr, discarded, diff_stat, diff, diff_truncated, timed_out`.

`check_gates_impl`:
`deadcode={ok,timed_out,tail}, typecheck={ok,timed_out,errors},
goldens_drifted, timeouts, commit_gate={marker_present,marker_path,note}`.
