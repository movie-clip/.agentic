REPORT 2026-08-31-probe-engine-hardening/09
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q
  result:    PASS
  detail:    63 passed, 5 warnings in 0.79s. The 5 warnings are one pre-existing datetime.utcnow DeprecationWarning in app/services/portfolio_snapshot_builder.py surfacing through the probe tests; no test-side warning. Anchor used: the four changed source files read directly plus the story ACs walked one by one against named test cases.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - WO-F docs close-out still owed (T-43.1.5 / T-43.2.4): the three pack-lag notes (backend.md:166 / quant.md:166-169 "not truncated"; testing.md:154-156 "does not validate payload shape") stay accurate against the landed code.

risks:
  - AC-F5.2 SHOULD_FIX (test lane): `_bound_diff` head/tail cap (testing.py:140-155) is wired at line 342 but no test exercises the truncation branch; 06 WO-E coverage listed a long-diff case not delivered. Story test plan for F5.2 (bounded diff invoked + in result) is met; mechanism correct on inspection.
  - AC-F1.3: no test exercises a real APIRoute whose model matches no shape predicate — per 04 § 2b all 14 engine routes classify, so no such route exists. Disclosure is exercised via a 404 no-match route and `_shape_of(None)`; the criterion cannot be tested the way it reads.
  - AC-F1.5: literal verified/degraded/withheld non-downgrade is asserted only at `_trust_downgrade` helper level (test lines 246-248), not via an engine route (08 Open item 3). Adequate — the helper is the single code path narrowing `ok` (probe_engine_impl:379-381).
  - 08's three SHOULD_FIX items (extra="forbid" reliance; row counts not pinned to MIN_DAILY_OBSERVATIONS; verified/degraded helper-only) were weighed non-blocking by integration and are not re-litigated here per the order.
  - Struck "five-tool registration check" (04 § 8): confirmed genuinely absent from the test file; all 5 `@server.tool()` decorators are visible in server.py; MCP transport registration is the human handshake check, out of scope.

## Orchestrator brief

- Verdict: PASS. Every AC in US-43.1 (F1.1-F1.6, F2.1-F2.5, F3.1-F3.4, G1, G2)
  and US-43.2 (F4.1-F4.6, F5.1-F5.4, G1, G2) is MET; none GAP or DRIFTED.
- Verification re-run: 63 passed — matches 07 / 08.
- Scope clean: only the 4 in-scope files changed; no app/schemas/, no engine
  route/service, no mcp/starlette move. AC-G2 (both stories) confirmed.
- MCP-transport-not-verified limitation is stated in both story drafts and the
  test docstring; no lane claimed end-to-end MCP verification. Out of scope.
- Struck "five-tool registration check" (04 § 8): confirmed absent, not failed
  for; wrapper-thinness (AC-G1) confirmed by direct read of server.py.
- 2 SHOULD_FIX notes for the human, both non-blocking: AC-F5.2 `_bound_diff`
  cap branch untested; F1.3 / F1.5 coverage thin but adequate (see risks).
- Sections below: § Acceptance walk US-43.1 · § Acceptance walk US-43.2 ·
  § MCP-transport limitation · § Trust-rendering honesty spot checks.

## Acceptance walk — US-43.1 (probe_engine, F-1/F-2/F-3)

### F-1 — the success signal means the route answered

- **AC-F1.1 MET** — probing.py:390-391 returns `request_shape` + `request_model`;
  `_request_model_for` (89-112) + `_shape_of` (115-133). Test
  `TestProbeShapeClassification::test_flat_route_shape_and_model` asserts
  `request_shape == "flat"`, `request_model == "DrawdownEngineRequest"`.
- **AC-F1.2 MET** — `_shape_mismatch` (136-163) returns `{expected, supplied, note}`;
  applied at probing.py:360, surfaced at :392. Test
  `test_wrong_shape_payload_warns_without_raising`: shape_mismatch populated,
  `expected=="flat"`, `supplied=="snapshot-wrapped"`, `status==200`, body not None,
  no raise.
- **AC-F1.3 MET** (see risks) — `_shape_of` returns `"unclassified"` for a
  non-matching / absent model, `request_model` None. Test
  `test_unclassified_route_is_disclosed_not_guessed` (404 no-match route):
  request_shape `"unclassified"`, request_model None. Disclosure is explicit, not
  a guessed default.
- **AC-F1.4 MET** — `_trust_downgrade` (166-181) + `ok_downgraded_by`;
  probing.py:379-381 sets `ok=False`. Test
  `test_unavailable_trust_downgrades_ok_despite_2xx`: status 200, ok False,
  `ok_downgraded_by == {"trust": "unavailable"}`.
- **AC-F1.5 MET** (see risks) — `_trust_downgrade` only matches literal
  `"unavailable"`. Test `test_trust_downgrade_helper_fires_only_on_unavailable`
  covers verified / degraded / withheld / synthetic / nested / non-dict → None.
  Engine-route integration `test_non_unavailable_trust_keeps_ok` uses `synthetic`.
- **AC-F1.6 MET** — three real engine routes: `/engines/drawdown/run` → flat,
  `/engines/provenance/run` → snapshot-wrapped, `/engines/diagnostics/run-imported`
  → bare-snapshot; each asserts shape + model.

### F-2 — the response is bounded

- **AC-F2.1 MET** — `_bound_arrays` (202-259), HEAD=TAIL=5. Test
  `test_long_array_bounded_head_tail_with_sentinel`: `series[:5]==[0..4]`,
  `series[-5:]==[95..99]`, order preserved.
- **AC-F2.2 MET** — sentinel `__probe_truncated__` carries `original_count`,
  `dropped`, `kept_head`, `kept_tail`, note "probe_engine truncated this array;
  the route returned all elements". Same test asserts all five.
- **AC-F2.3 MET** — `test_short_array_is_untouched` (len 11 untouched),
  `test_empty_array_and_null_pass_through` (`[]` and `None` pass through, no
  marker).
- **AC-F2.4 MET** — `fields` param on `probe_engine_impl` + wrapper; `_apply_fields`
  (184-199) keeps named keys, always retains `trust` / `*_trust`; `fields_kept` /
  `fields_omitted_count` reported. Tests `test_apply_fields_keeps_named_keys_plus_trust`,
  `test_fields_filter_runs_before_truncation` (asserts `"trust" in body`).
  Omitted → bounded full body.
- **AC-F2.5 MET** — `test_drawdown_probe_over_long_history_is_bounded`:
  `"underwater_series" in result["truncation"]`, series len 11,
  `original_count > 100`.

### F-3 — non-derivable routes fail safe, not live

- **AC-F3.1 MET** — `_refusal` (262-288). Test
  `test_non_derivable_route_is_refused_by_default`: `refused True`, `ok False`,
  `status None`, `body None`, `"allow_unmocked" in reason`; route never POSTed.
- **AC-F3.2 MET** — `test_allow_unmocked_runs_and_is_disclosed`: `refused False`,
  `unmocked True`, `mocked False`, `engine_module None`, status is int.
- **AC-F3.3 MET** — `importlib.import_module(target)` at probing.py:348 raises
  `ModuleNotFoundError` before any context, for a typo'd explicit module or a
  typo'd route segment. Tests `test_typod_explicit_engine_module_raises_loudly`,
  `test_typod_route_segment_raises_loudly`. Not downgraded to unmocked.
- **AC-F3.4 MET** — `test_normal_engine_route_is_unaffected`; `TestProbeEngine` +
  `TestEngineModuleDerivation` classes still green in the 63-pass run.

### Guardrail guards

- **AC-G1 MET** — server.py:72-94 `probe_engine` wrapper: exactly `fields` +
  `allow_unmocked` added, one delegating `return probing.probe_engine_impl(...)`,
  no branching, docstring 2 lines. All new logic is in `tools/probing.py` helpers.
- **AC-G2 MET** — `git diff --name-only` shows only the 4 in-scope files (plus 3
  pre-existing out-of-scope paths the order excludes). No `app/schemas/` edit, no
  engine-route / service change, no requirements change (mcp pin / starlette
  untouched).

## Acceptance walk — US-43.2 (suite-runner tools, F-4/F-5)

### F-4 — a hanging subprocess returns, it does not hang

- **AC-F4.1 MET** — `_run` (testing.py:83-104) forwards `timeout=` to
  `subprocess.run`; all 7 call sites pass an explicit `timeout=` (run_tests:227,
  check_gates:263/280/297, reset_goldens:331/340/349). `subprocess.run` kills the
  child on expiry. Tests `test_run_tests_passes_a_scope_appropriate_timeout`,
  `test_gate_and_git_subprocesses_get_their_own_timeouts`.
- **AC-F4.2 MET** — local `TIMEOUTS` dict (60-67): full 1800 / backend 600 /
  gate 300 / git 30. Test asserts `full != backend` and `full != gate`. Not
  imported from run_all_tests.
- **AC-F4.3 MET** — `run_tests_impl` catches `TimeoutExpired` → `_timeout_result`
  (116-137) with `scope`, `command`, `timeout_seconds`. Test
  `test_timeout_result_is_structured_and_does_not_raise`.
- **AC-F4.4 MET** — `timed_out` bool on every return path (normal path adds
  `timed_out: False` at :236). timeout → exit_code None; pass → ok True; failure →
  exit_code int. Test `test_timeout_is_distinguishable_from_pass_and_from_failure`.
- **AC-F4.5 MET** — check_gates_impl wraps each of its 3 `_run` calls in its own
  try/except; `timeouts` list names the failed gate; completed gates keep real
  results. Test `test_one_gate_timing_out_still_reports_the_others`.
- **AC-F4.6 MET** — fast path unchanged except `timed_out: False`. Tests
  `test_fast_gate_run_carries_no_timeout_marker`; `TestRunTestsParsing` /
  `TestGates` still green.

### F-5 — reset_goldens records what it discarded

- **AC-F5.1 MET** — reset_goldens_impl:330-333 runs `git diff --stat` →
  `diff_stat` in result (:365). Test `test_diff_is_captured_before_the_checkout`
  asserts `calls[0][:3] == ["git","diff","--stat"]` and `result["diff_stat"]`.
- **AC-F5.2 MET** (see risks) — `git diff` → `_bound_diff` (140-155) →
  `diff` + `diff_truncated`. Test asserts `"+b" in result["diff"]`. The head/tail
  cap branch itself is not directly tested; mechanism wired at :342 and correct on
  inspection.
- **AC-F5.3 MET** — code order stat(329) → diff(338) → checkout(347); capture is
  computed before the checkout try block. Test
  `test_checkout_failure_still_carries_the_capture`: `ok False`,
  `stderr == "error: pathspec"`, `diff_stat`/`diff` still populated.
- **AC-F5.4 MET** — `discarded = bool(diff_stat)`. Test
  `test_no_drift_reports_nothing_discarded`: `discarded False`, `diff_stat ""`,
  `diff ""`, `ok True`.

### Guardrail guards

- **AC-G1 MET** — server.py `run_tests` / `check_gates` / `reset_goldens` wrappers
  (31-50) unchanged: single delegating calls, 2-line docstrings, no signature
  change. All new logic in `tools/testing.py` `*_impl` / helpers.
- **AC-G2 MET** — testing.py:40-45 still imports `BACKEND_DIR`, `FRONTEND_DIR`,
  `TEST_PASS_MARKER`, `npx_command` from `run_all_tests`. `TIMEOUTS` is a per-call
  budget the runner does not own (04 § 6b). No schema, no mcp pin bump, no
  starlette move.

## MCP-transport limitation

- Stated where required: both story drafts (02-stories.md) list it under
  **Out of scope**; test_mcp_tools.py docstring (lines 8-9) records it as a human
  check. No lane (05 / 06 / 07 / 08) claimed end-to-end MCP verification — every
  run exercised only `pytest app/tests/test_mcp_tools.py`. Genuinely out of scope.

## Trust-rendering honesty spot checks

- `ok_downgraded_by` surfaces the reason — `{"trust": "unavailable"}` names the
  key and value (test line 226).
- Refusal names `allow_unmocked` — literal string in `_refusal` reason (test
  line 351).
- A shape mismatch warns without suppressing the body — status 200 + body not
  None alongside the warning (`test_wrong_shape_payload_warns_without_raising`).
- `trust: "unavailable"` → not `ok`; verified / degraded / withheld / synthetic
  stay `ok` — `_trust_downgrade` helper test (lines 240-252); `withheld` is never
  collapsed into `unavailable`.
