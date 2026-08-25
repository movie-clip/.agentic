REPORT 2026-08-21-epic38-followups-and-etf/08
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_market_data.py — fixed 8 pre-existing tests: added `instance.is_cached.return_value = True` after `instance = client_mock.return_value` in each
  - services/quant-engine/app/tests/test_market_data.py — added get_latest_quotes real-cache miss-then-hit pair (AC1/AC6)
  - services/quant-engine/app/tests/test_market_data.py — added get_historical_prices FMP-branch real-cache miss-then-hit pair (AC2/AC6)
  - services/quant-engine/app/tests/test_market_data.py — added get_historical_prices yfinance-branch real-cache miss-then-hit pair, real YFinanceClient + real cache, only yf.Ticker stubbed (AC2/AC6)
  - services/quant-engine/app/tests/test_market_data.py — added get_direct_verified_benchmark_history real-cache miss-then-hit pair (AC3/AC6)
  - services/quant-engine/app/tests/test_market_data.py — added test proving cached:True requires BOTH underlying pre-checks (one pre-warmed hit + one live miss still reports False) (AC3)
  - services/quant-engine/app/tests/test_market_data.py — added get_etf_holdings real-cache miss-then-hit pair (AC4/AC6)
  - services/quant-engine/app/tests/test_market_data.py — added get_etf_holdings_for_date delegation test, spies on get_etf_holdings to prove inheritance not a second implementation (AC5)
  - services/quant-engine/app/tests/test_market_data.py — added structural test proving `_will_be_served_from_cache` is a pure passthrough to `FmpClient.is_cached` (AC7)
  - services/quant-engine/app/tests/test_fmp_client.py — added structural formula-agreement test: spies on `build_cache_identifier`, asserts `_get` and `is_cached` invoke it with identical args (AC7), see § Formula-agreement test

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail:    backend 858 passed; frontend 331 test files/tests passed; dead-code gate (ruff/vulture/knip) clean; tsc clean; dashboardGoldens.ts unchanged (git status confirms no drift)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - all 8 previously-broken tests pass with the plan's prescribed one-line fix — no deviation needed
  - get_company_profile's existing US-37.2 cache-flag tests stayed green untouched — AC8 regression confirmed, see § AC8 regression
  - AC1-AC5 real-cache pattern mirrors get_company_profile's own shape (`_mock_fmp_settings` + tmp_path + mocked httpx.Client.get, no FmpClient mock) — reuse for future per-call cache-flag coverage instead of mocking FmpClient wholesale
  - yfinance-branch test needs `monkeypatch.setattr(..., YFinanceClient)` plus a separate `app.clients.yfinance_client.get_settings` patch — see § Yfinance-branch test setup

risks:
  - none

## Orchestrator brief

T-38.2.3 complete: all 8 tests named in 07-backend.md § Expected failures pass
again (prescribed one-line fix, no deviation), and full AC1-AC8 test-plan
coverage added to test_market_data.py + one structural test in
test_fmp_client.py per the work order's own file-choice discretion.
`python scripts/run_all_tests.py` green end to end, including the dead-code
gate. No production code touched — this lane's scope was test files only, and
no defect was found in the landed T-38.2.1/T-38.2.2 implementation. Named
sections below: § Formula-agreement test (AC7 structural proof), § AC8
regression (get_company_profile unchanged), § Yfinance-branch test setup
(fixture-override mechanics).

## Formula-agreement test

`test_get_and_is_cached_derive_the_cache_key_from_the_same_formula`
(test_fmp_client.py) spies on the bound `build_cache_identifier` method,
calls `_get` then `is_cached` with matching params, and asserts both spy
calls received identical `(path, params)` args plus that the real cache
entry `_get` wrote is reported as a hit by `is_cached` — proves identity by
construction, not just today's fixture output.

## AC8 regression

`test_get_company_profile_reports_true_miss_then_true_hit_within_ttl` and
`test_get_company_profile_reports_miss_for_different_symbols_independently`
(both pre-existing, US-37.2) required no edits and passed unchanged in the
same full-suite run, confirming AC7's formula consolidation is
behaviour-preserving for `get_company_profile`.

## Yfinance-branch test setup

`test_get_historical_prices_yfinance_branch_reports_true_miss_then_true_hit_within_ttl`
overrides the autouse `_disable_yfinance_fallback` fixture (test-body patch
wins, per that fixture's own docstring) via
`monkeypatch.setattr("app.services.market_data.YFinanceClient", YFinanceClient)`,
then separately patches `app.clients.yfinance_client.get_settings` (a
different import from `app.clients.fmp.get_settings`) to point its own real
`JsonFileCache` at a distinct tmp_path subdir, and stubs `yfinance.Ticker`
only.
