REPORT 2026-08-31-probe-engine-hardening/08
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q
  result:    PASS
  detail:    63 passed, 5 warnings in 0.78s. The 5 warnings are one pre-existing datetime.utcnow DeprecationWarning in app/services/portfolio_snapshot_builder.py surfacing through the probe tests; no test-side warning. External anchor: FastAPI live-app introspection re-exercised by the probe tests — APIRoute.body_field.type_ resolves the bound model for flat / snapshot-wrapped / bare-snapshot routes exactly as 04 § 2 specified.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No change requests. PASS with no BLOCKING findings; no CR files written.
  - WO-F docs close-out (T-43.1.5 / T-43.2.4) still owed; the three pack-lag notes in run.md Open remain accurate against the landed code. see § What was checked
  - Three run.md Open should_fix/note rows all weighed as SHOULD_FIX, non-blocking. see § Open items weighed

risks:
  - Open item 1 (extra="forbid" reliance): SHOULD_FIX, test lane, non-blocking. Tests assert warn-at-200 because engine models accept extras; not a defect. see § Open items weighed
  - Open item 2 (row count not pinned to MIN_DAILY_OBSERVATIONS): SHOULD_FIX, test lane, non-blocking. 60 rows vs floor 20 is 3x headroom. see § Open items weighed
  - Open item 3 (verified/degraded non-downgrade at helper level only): SHOULD_FIX / note, review 09 to confirm. _trust_downgrade is the seam encoding AC-F1.5 and is exhaustively unit-covered. see § Open items weighed
  - Depth-1 trust scan only: nested per-episode / per-scenario trust does not downgrade ok. In-spec per 04 § 1d / AC-F1.4-F1.5; a reader expecting nested gating reads it as under-strict.
  - detect_deadcode.py --strict was not run (order verification is the one test file). New probing.py helpers are all reached; vulture file-scoped false-positives are pre-existing. Human's run_all_tests.py is the authority. see § What was checked

## Orchestrator brief

- Verdict: PASS. The three build lanes (WO-A probing.py + server.py, WO-C testing.py, WO-E test_mcp_tools.py) integrate coherently against the 04 technical plan; no BLOCKING findings, no CR files.
- Envelope (04 § 1): all 9 new keys present in both the main return and the refusal return; ok narrowed by trust-downgrade; refusal is a structured dict, not a raise; 1c unmocked disclosure correct.
- Shape classification (04 § 2): live-app APIRoute introspection + 3-step fallback + model->shape rule; returns "unclassified" rather than guessing; shape_mismatch is warn-only and never raises.
- fields= (§ 3), truncation sentinel (§ 5), allow_unmocked + loud typo raise (§ 4): all match the plan.
- testing.py: _run gained only `*, timeout=None` (extra_env still positional 2); TIMEOUTS is a local dict; check_gates wraps each of its 3 _run calls individually (AC-F4.5 held); reset_goldens captures diff --stat + bounded diff before checkout, survives checkout failure, handles no-drift.
- server.py: probe_engine wrapper gained exactly 2 params, one delegating call, 2-line docstring, no branching; other 4 wrappers untouched.
- Constraints held: no app/schemas/ change, no new Pydantic model, mcp pin not bumped, starlette untouched, testing.py still imports its constants from run_all_tests.
- Struck "five-tool registration check" is genuinely absent (grep clean); drawdown test repointed to a flat payload with a separate wrong-shape case (TestProbeShapeClassification::test_wrong_shape_payload_warns_without_raising).
- Verification: 63 passed locally. Guardrails 1-5 not engaged; quant-audit stays SKIPPED.
- 3 Open should_fix/note items all weighed as SHOULD_FIX (non-blocking) — see § Open items weighed and the risks bullets.
- Sections below: § Open items weighed (the three run.md Open rows, classified with reasoning) · § What was checked (the field-by-field integration checks).
- Blocks dispatch: none. Next: 09 review (acceptance).

---

## Open items weighed

The three rows the order handed me from run.md's Open table (WO-E risks). None is BLOCKING; all three are thin-but-not-wrong test coverage.

### 1. Shape/trust probes ride on engine request models not setting `extra="forbid"`

**Classification: SHOULD_FIX. Owner: test lane. Non-blocking.**

`TestProbeTrustGating::test_unavailable_trust_downgrades_ok_despite_2xx` and the wrong-shape
cases assert the probe gets a `200` + `trust: "unavailable"` (fail-closed) rather than a `422`.
That holds only because `DrawdownEngineRequest` (and peers) accept unknown / missing fields.

Why it is not BLOCKING:

- The tests exercise the **actual current contract**. Today the engine request models do not
  forbid extras; the probe's F-1 value proposition (04 § 2c) is precisely that a wrong shape
  *still validates on defaults and answers nothing*, which is what `shape_mismatch` + the
  trust downgrade exist to catch. Testing that at `200` is correct.
- Adding `extra="forbid"` to engine request models is a schema change — it routes through the
  backend and quant lanes with its own test pass, at which point these probe tests are updated
  as part of that work. It is not a silent future break of *this* slice.
- The dependency is already called out in code comments and in the WO-E report risks.

Cheap optional hardening (not required to pass): the wrong-shape test could assert only
`shape_mismatch is not None and body is not None` without pinning the status to `200`.

### 2. Synthetic-history row counts not pinned to `MIN_DAILY_OBSERVATIONS`

**Classification: SHOULD_FIX. Owner: test lane. Non-blocking.**

`price_rows_from_returns([...] * 15)` = 60 valuation rows (clears the analytics minimum) and
`* 150` = 600 rows (drives `underwater_series` truncation). The minimum is
`MIN_DAILY_OBSERVATIONS = 20`, imported nowhere in the test.

Why it is not BLOCKING:

- 60 against a floor of 20 is 3x headroom — a "large rise" in the constant is required to
  break it, and that constant is a methodology parameter that only moves through the quant
  lane (its own test pass).
- The 600-row case is about array length crossing `PROBE_ARRAY_HEAD + PROBE_ARRAY_TAIL + 1`
  (= 11), which is a probing.py constant, not the observation floor — that half is robust.

Cheap optional hardening: `[...] * (probing-independent multiple of MIN_DAILY_OBSERVATIONS)`
with the constant imported, so the pass-case row count tracks the floor.

### 3. verified / degraded / withheld non-downgrade covered at helper level only

**Classification: SHOULD_FIX / note. Owner: review 09 to confirm acceptable.**

`_trust_downgrade` is unit-tested directly with `verified`, `degraded`, `withheld`,
`synthetic`, the `*_trust` suffix, a nested per-row dict, and a non-dict (test lines
240-252). The integration-level non-downgrade assertion uses drawdown's `trust: "synthetic"`
because no cheap engine route emits a top-level `trust: "verified"`.

Why it is not BLOCKING:

- `_trust_downgrade` is a pure function and is the single seam that encodes AC-F1.5 ("only
  literal `unavailable` downgrades `ok`"). Exhaustive direct coverage of that function tests
  the rule itself, which is stronger than an incidental engine-route assertion.
- The integration path still confirms the wiring end-to-end with a real non-`unavailable`
  trust string (`synthetic`).
- Forcing an engine route that yields `trust: "verified"` would add fixture cost for no extra
  assurance about the rule.

This row is flagged in run.md as "review 09 to confirm acceptable" — from an engineering
coherence standpoint it is adequate; the acceptance reviewer owns the final call.

## What was checked

- Envelope field-by-field: `probing.py` lines 383-398 (main return) and 268-288 (`_refusal`)
  against 04 § 1a / § 1b / § 1c / § 1d. All 9 new keys present in both; `ok` = `status < 400`
  then narrowed by `_trust_downgrade`; refusal `reason` contains the literal `allow_unmocked`.
- Shape classification: `_request_model_for` (89-112) three-step fallback preserved
  (`type_` -> `field_info.annotation` -> `dependant.body_params[0].type_` -> `None`);
  `_shape_of` (115-133) flat / bare-snapshot / snapshot-wrapped / unclassified with no guess;
  `_shape_mismatch` (136-163) returns a dict or `None`, never raises; the probe POSTs
  unconditionally (362-364). Confirmed live by the 63-test run.
- `fields=` (§ 3): `_apply_fields` top-level keys only, always retains `trust` / `*_trust`,
  `fields_kept = sorted(kept)`, count = `len(body) - len(kept)`; runs before `_bound_arrays`
  (373-376).
- Truncation sentinel (§ 5): threshold `count > HEAD + TAIL + 1` (228); sentinel carries
  `original_count` / `dropped` / `kept_head` / `kept_tail` / `note`; array stays a list;
  empty / short / `None` pass through; depth guard `_MAX_TRAVERSAL_DEPTH = 20`.
- `allow_unmocked` + typos (§ 4): `importlib.import_module(target)` (348) raises
  `ModuleNotFoundError` before any context for a typo'd route segment *or* explicit module;
  non-derivable valid route + `allow_unmocked=False` returns `_refusal`; `allow_unmocked=True`
  runs under `nullcontext()` with `unmocked=True`.
- `_run` (testing.py 83-104): only `*, timeout=None` added; `extra_env` still positional
  index 2 (`run.call_args[0][2]` assertions still green). `TIMEOUTS` local dict (60-67), not
  imported; testing.py still imports `BACKEND_DIR` / `FRONTEND_DIR` / `TEST_PASS_MARKER` /
  `npx_command` from `run_all_tests` (40-45).
- `check_gates_impl` (248-319): three independent `try/except subprocess.TimeoutExpired`
  blocks, one per `_run` call — AC-F4.5 not regressed by a single outer try. New key-set
  `{deadcode, typecheck, goldens_drifted, timeouts, commit_gate}` matches the WO-E assertion
  (test 463-469).
- `run_tests_impl` timeout result: `timed_out=True`, `exit_code=None`, `failures=[]` — vs a
  pass (`timed_out=False`, `ok=True`) vs a parsed failure (`timed_out=False`, `exit_code` an
  int). Distinguishable, covered by `test_timeout_is_distinguishable_from_pass_and_from_failure`.
- `reset_goldens_impl` (322-369): `git diff --stat` then bounded `git diff` then
  `git checkout --`, strict order; capture computed before the checkout `try` block so a
  checkout failure still returns `diff_stat` / `diff` alongside `ok=False` + `stderr`;
  no-drift => `discarded=False`, `diff_stat=""`, `diff=""`. Call-order asserted by
  `test_diff_is_captured_before_the_checkout`.
- `server.py` (72-94): `probe_engine` wrapper gained exactly `fields` + `allow_unmocked`,
  passed through the one delegating call; docstring 2 lines; no branching. `run_tests`,
  `check_gates`, `reset_goldens`, `build_snapshot` wrappers byte-identical (diff is +4 lines).
- Constraints: `git diff --name-only` shows only the 4 in-scope files plus the 3 pre-existing
  out-of-scope paths (dashboardGoldens.ts, IB2026.csv, golden_market_data.json). No
  `app/schemas/` edit, no new Pydantic model, no requirements change (mcp pin / starlette
  untouched).
- Struck registration check: `grep -i "regist|five.tool|5.tool"` over the test file returns
  nothing — genuinely absent, not smuggled back. `test_drawdown_route_returns_a_response...`
  repointed to a flat payload asserting `request_shape == "flat"` /
  `shape_mismatch is None`; the wrong-shape case is a separate test.
- Guardrails 1-5: none engaged (04 § 12 stands). `_trust_downgrade` only string-matches the
  literal `"unavailable"`; `withheld` is never collapsed into `unavailable` (explicit
  assertion, test line 248); the body passes through unmodified except array bounding and
  optional field filtering. quant-audit correctly SKIPPED.
