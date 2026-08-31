REPORT 2026-08-31-probe-engine-hardening/07
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_mcp_tools.py — imports gain `sys` and `price_rows`; only this file changed
  - services/quant-engine/app/tests/test_mcp_tools.py — `TestGates::test_check_gates_reports_every_gate` key-set now includes `timeouts`, asserts `timeouts == []`
  - services/quant-engine/app/tests/test_mcp_tools.py — `TestGates::test_check_gates_flags_goldens_drift` `fake_run` stub gains `*, timeout=None`
  - services/quant-engine/app/tests/test_mcp_tools.py — `test_drawdown_route_returns_a_response_with_mocked_market_data` repointed to a FLAT payload (snapshot splatted top-level + `benchmark_symbol`), asserts `request_shape == "flat"` and `shape_mismatch is None`
  - services/quant-engine/app/tests/test_mcp_tools.py — new class `TestProbeShapeClassification` (F-1): flat / snapshot-wrapped / bare-snapshot shape+model, wrong-shape warns at 200 without raising, misspelled action segment => `unclassified` + `request_model None` and the probe still POSTs
  - services/quant-engine/app/tests/test_mcp_tools.py — new class `TestProbeTrustGating` (F-1): `trust == "unavailable"` downgrades `ok` at 200 with `ok_downgraded_by`; `synthetic` keeps `ok True`; `_trust_downgrade` unit-covers verified/degraded/withheld/synthetic/`*_trust`/nested/non-dict
  - services/quant-engine/app/tests/test_mcp_tools.py — new class `TestProbeBodyBounding` (F-2): `_bound_arrays` head/tail+sentinel, short untouched, empty/null/`[]` pass-through, dotted nested path; `_apply_fields` keeps named+trust keys and counts omissions; long-history drawdown probe bounds `underwater_series` to 11; `fields=` filters before truncation
  - services/quant-engine/app/tests/test_mcp_tools.py — new class `TestProbeAllowUnmocked` (F-3): default refusal (`reason` names `allow_unmocked`, route not run), `allow_unmocked=True` runs with `unmocked True`, typo'd explicit module and typo'd route segment both raise `ModuleNotFoundError`, normal route unaffected
  - services/quant-engine/app/tests/test_mcp_tools.py — new class `TestRunTestsTimeout` (F-4): scope-appropriate `timeout=` (full != backend != gate); `TimeoutExpired` => structured result, no raise; distinguishable from pass and parsed-failure
  - services/quant-engine/app/tests/test_mcp_tools.py — new classes `TestGatesTimeout` (F-4) and `TestResetGoldensRecordsDiscard` (F-5): per-gate timeout keeps completed gates; reset_goldens captures stat+bounded diff before `git checkout --`, survives a failed checkout, reports nothing discarded on no drift

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q
  result:    PASS
  detail:    63 passed, 5 warnings in 0.82s. The 5 warnings are one pre-existing production DeprecationWarning (datetime.utcnow in app/services/portfolio_snapshot_builder.py) surfacing through the probe tests; no test-side warning.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No new shared fixture added. Reused `build_snapshot_impl`, `price_rows`, `price_rows_from_returns`, `mocker.patch.object(testing, "_run", ...)` with `subprocess.CompletedProcess` fakes.
  - Probe payload convention exercised: FLAT routes get `{**build_snapshot_impl(...), "benchmark_symbol": "SPY"}`; snapshot-wrapped routes get `{"snapshot": build_snapshot_impl(...)}`; bare-snapshot routes get `build_snapshot_impl(...)` directly.
  - Helper-level unit tests call `probing._trust_downgrade`, `probing._bound_arrays`, `probing._apply_fields` directly — these are the stable seams for future probe-envelope regression coverage.
  - `_run` timeout is asserted as a keyword arg via `run.call_args.kwargs["timeout"]`; `extra_env` stays positional index 2, so the existing `run.call_args[0][2]` assertions are untouched.
  - Fake `_run` stubs that patch `testing._run` must now accept `*, timeout=None` (or `**kwargs`); two such stubs live in this file (`TestGates::test_check_gates_flags_goldens_drift`, `TestGatesTimeout::test_one_gate_timing_out_still_reports_the_others`).

risks:
  - Tool-registration test intentionally NOT added: 04 § 8 struck the "five-tool registration check", and the US-43.1 test-plan line implying one is deliberately left uncovered because exercising registration means importing the `mcp` SDK the requirements-dev pin ringfences. Registration stays a human MCP-handshake check.
  - The "verified/degraded stays ok=True" case uses drawdown's `trust == "synthetic"` (that engine emits only `synthetic | unavailable`); the literal `verified` / `degraded` / `withheld` non-downgrade is covered at the `_trust_downgrade` helper level only, since no engine-route probe yields a top-level `trust: "verified"` cheaply.
  - The shape / trust probes assume the drawdown engine fails closed (200 + `trust: "unavailable"`) on a wrong-shape or position-less payload rather than 422-ing — this rides `DrawdownEngineRequest` not setting `extra="forbid"`. Adding `extra="forbid"` to the engine request models would flip these to 422.
  - Drawdown synthetic-history probes get one valuation date per `price_rows_from_returns` row (mock ignores date args); `*15` = 60 rows clears MIN_DAILY_OBSERVATIONS=20, `*150` = 600 rows drives truncation. Not pinned to the constant — a large rise in MIN_DAILY_OBSERVATIONS would make the 60-row case return `unavailable`.
