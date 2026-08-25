REPORT 2026-08-21-epic38-followups-and-etf/07
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/clients/fmp.py — added `build_cache_identifier(path, params)` and `is_cached(namespace, path, params, ttl_seconds)` to FmpClient
  - services/quant-engine/app/clients/fmp.py — `_get` and `get_etf_holders` now both call `build_cache_identifier` instead of constructing the identifier inline
  - services/quant-engine/app/clients/yfinance_client.py — added `_build_cache_identifier` (static) and `is_cached(symbol, from_date, to_date)` to YFinanceClient
  - services/quant-engine/app/clients/yfinance_client.py — `get_historical_price_light` now reuses `_build_cache_identifier` instead of its own inline `json.dumps`
  - services/quant-engine/app/services/market_data.py — renamed `_profile_will_be_served_from_cache` to `_will_be_served_from_cache(namespace, path, params, ttl_seconds)`, delegates to `self.client.is_cached`
  - services/quant-engine/app/services/market_data.py — removed now-unused `import json`
  - services/quant-engine/app/services/market_data.py — `get_latest_quotes` pre-checks cache before fetch; `cached` now reports the real per-call hit/miss
  - services/quant-engine/app/services/market_data.py — `get_historical_prices` FMP branch pre-checks via `_will_be_served_from_cache`; reports real hit/miss
  - services/quant-engine/app/services/market_data.py — `get_historical_prices` yfinance branch pre-checks via `self._yfinance().is_cached(...)`; reports real hit/miss
  - services/quant-engine/app/services/market_data.py — `get_direct_verified_benchmark_history` reports `cached=True` only when both underlying (full + dividend-adjusted) pre-checks hit
  - services/quant-engine/app/services/market_data.py — `get_etf_holdings` pre-checks via `_will_be_served_from_cache`; reports real hit/miss
  - services/quant-engine/app/services/market_data.py — `get_etf_holdings_for_date` needs no separate fix — confirmed its non-history branch inherits the fix via delegation to `get_etf_holdings`
  - services/quant-engine/app/services/market_data.py — `get_company_profile`'s call site updated to the new `_will_be_served_from_cache` signature; outcome unchanged (AC8)

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_market_data.py app/tests/test_fmp_client.py -x -q (then re-run without -x for full failure list)
  result:    FAIL
  detail:    45 passed, 8 failed — all 8 are the pre-existing tests named in 06-technical-plan.md § Decisions #5, see § Expected failures below. No other test regressed. Pinned test_get_etf_holders_cache_identity_is_unchanged_by_url_refactor stayed green. detect_deadcode.py --strict ran clean (ruff/vulture/knip).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - the 8 failing tests are EXPECTED per plan § Decisions #5, T-38.2.3's job — see § Expected failures for names and the prescribed one-line fix
  - T-38.2.3's test plan wants a same-formula regression test; `FmpClient.build_cache_identifier` is now the single source both `_get`/`get_etf_holders` and `market_data.py`'s helper call into, suitable for an identity/reference assertion
  - AC1-AC8 all satisfied — see § AC trace below for the per-AC mapping to the changed bullets above

risks:
  - none

## Orchestrator brief

Implemented T-38.2.1 + T-38.2.2 per 06-technical-plan.md § Decisions #4
exactly, no deviation. Two named sections below: § Expected failures (the 8
pre-existing tests that break under this change, per the plan's own
prediction — test-engineer's T-38.2.3 job, not a regression) and § AC trace
(per-AC verification mapping). Dead-code gate and the pinned
get_etf_holders identity test both confirmed clean/green.

## Expected failures (T-38.2.3 scope, not a regression here)

Per 06-technical-plan.md § Decisions #5, these 8 tests mock `FmpClient` wholesale
and assert hardcoded `cached: True` with no mock configured for the new
`is_cached` pre-check call, so it now resolves to a truthy `MagicMock` instead
of `True`:

- test_get_historical_prices_uses_etf_holdings_proxy_fallback
- test_get_historical_prices_uses_gld_proxy_fallback_for_sgld
- test_get_historical_prices_uses_dbc_proxy_fallback_for_icom
- test_get_historical_prices_uses_slv_proxy_fallback_for_isln
- test_get_historical_prices_uses_proxy_for_continuous_future_roots
- test_get_direct_spy_benchmark_history_records_direct_vendor_scope_metadata
- test_get_direct_verified_benchmark_history_records_direct_vendor_scope_metadata_for_qqq
- test_verified_benchmark_overlapping_windows_share_canonical_call

Prescribed fix (test-engineer, T-38.2.3): add `instance.is_cached.return_value
= True` immediately after `instance = client_mock.return_value` in each.

## AC trace

- AC1 `get_latest_quotes` — pre-check added, real hit/miss reported
- AC2 `get_historical_prices` — both branches (FMP + yfinance fallback) pre-check
- AC3 `get_direct_verified_benchmark_history` — AND'd two-call pre-check
- AC4 `get_etf_holdings` — pre-check added, real hit/miss reported
- AC5 `get_etf_holdings_for_date` — inherits via delegation, verified not duplicated
- AC6 — pre-check reads live cache state per call, so a repeat call within TTL flips to `True`
- AC7 — `FmpClient.build_cache_identifier` is the one formula; `market_data.py`'s
  helper delegates to `FmpClient.is_cached`; `YFinanceClient` has its own
  independent twin, matching AC7's fmp.py-only scoping
- AC8 — `get_company_profile` call site updated to new signature, outcome unchanged
