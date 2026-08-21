REPORT 2026-08-21-dynamic-sector-classification/09
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_equity_sector_resolution.py — new module, direct unit tests of resolve_equity_sector covering AC3-AC8 + the AC7 taxonomy regression
  - services/quant-engine/app/tests/test_instrument_registry.py — added AC1/AC2/AC10 registry-wiring tests + a _merge_known_instrument_metadata identity-change regression test
  - services/quant-engine/app/tests/test_analytics.py — added an AC9 test: unclassified equity lands in a distinct "Unclassified" bucket, weight included in the total
  - services/quant-engine/app/tests/conftest.py — added autouse _mock_overview_engine_market_data fixture mocking app.analytics.overview.MarketDataService

verification:
  command:   cd services/quant-engine && pytest -q (narrow); then python scripts/run_all_tests.py (full, time allowed)
  result:    PASS
  detail:    Backend 840 passed (0:01:23, -n auto); frontend 331 passed (37 files); tsc clean; dead-code gate (ruff+vulture+knip) clean; dashboardGoldens.ts unchanged (git diff --stat shows no drift)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New autouse conftest fixture _mock_overview_engine_market_data mirrors the per-engine pattern; patches app.analytics.overview.MarketDataService, defaults get_company_profile to None
  - New module test_equity_sector_resolution.py matches test_instrument_enrichment.py's granularity (one module per resolver) and reuses its local _FakeMarketData pattern
  - test_instrument_registry.py gained a local _SpyMarketData helper (records get_company_profile calls); same small pattern now exists in 3 test files, see risks
  - Test-local _statement()/_one_position_snapshot() helpers added to test_instrument_registry.py; not promoted to fixtures.py, which was outside this order's scope

risks:
  - Confirmed via docs/IB2026.csv: INTU/PANW/VICI/SPCX have net-zero held quantity and are absent from Open Positions — not open positions today
  - Per non_goals, no statement_truths.py pins were added for INTU/PANW/VICI/SPCX; this resolves the design pass's flagged uncertainty as "closed, do not pin"
  - The get_company_profile fake/stub pattern is now duplicated across 3 test files with no shared scaffolding — a fixtures.py candidate, but fixtures.py was out of this order's scope
  - No genuine defect found in the merged T-37.1.1/T-37.1.2 code; every AC1-AC10 behaviour in the DoD is covered and passes against the shipped implementation

## Orchestrator brief

- Full US-37.1 test coverage added across 4 files (1 new module, 3 edited) per the work order's definition_of_done; every DoD bullet has a dedicated, passing test.
- No production code touched. No defects found in T-37.1.1/T-37.1.2's shipped code — all ACs behave as specified.
- Non-goal on statement_truths.py pins resolved by direct evidence: confirmed INTU/PANW/VICI/SPCX are closed positions in the current docs/IB2026.csv, so no pins were added (see risks).
- Both verification commands run and green: narrow pytest (840 passed) and the full python scripts/run_all_tests.py (backend+frontend+tsc+dead-code gate all clean, goldens undisturbed).
- Sections: none beyond this brief — report body is the standard block only.
