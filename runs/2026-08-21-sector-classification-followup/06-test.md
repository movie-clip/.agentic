REPORT 2026-08-21-sector-classification-followup/06
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_equity_sector_resolution.py — added AC1 parametrized casing/whitespace regression (5 cases) pinning `resolve_equity_sector` normalization.
  - services/quant-engine/app/tests/test_equity_sector_resolution.py — added AC2 regression: unmapped sector (with its own whitespace/casing) still falls through to unavailable.
  - services/quant-engine/app/tests/test_market_data.py — added AC3/AC4 test: `get_company_profile` reports `cached: False` on a miss, `cached: True` on a hit within TTL.
  - services/quant-engine/app/tests/test_market_data.py — added a second cache test proving cache status is tracked per-symbol, not a shared flag.

verification:
  command:   cd services/quant-engine && pytest app/tests/test_equity_sector_resolution.py app/tests/test_market_data.py -q
  result:    PASS
  detail:    77 passed (via `python -m pytest`, since bare `pytest` is not on PATH in this shell). Also ran `python scripts/run_all_tests.py` from repo root — full suite green (331 frontend tests, backend pytest, tsc --noEmit, dead-code gate strict all clean); no dashboardGoldens.ts diff.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Taxonomy tests reuse `app.tests.fixtures.FakeMarketData` + `SECTOR_TAXONOMY_MAP` — no new fixture added.
  - Cache tests reuse the module's existing `_mock_fmp_settings` helper — no new fixture added.
  - AC3/AC4 test builds a real `MarketDataService()`/`FmpClient()` against `tmp_path` via `_mock_fmp_settings(fmp_cache_dir=str(tmp_path))`.
  - That real-cache setup is needed because the fix's pre-check reads an on-disk `JsonFileCache`; mocking `FmpClient` wholesale would make every pre-check report a permanent miss.
  - Per the story's instruction, the cache test asserts only the reported `cached` value via `get_last_fetch_meta`, not `FmpClient`'s internal call count.
  - Both merged fixes (T-37.2.1, T-37.2.2) behaved exactly as their handoffs described; no defect found in either.

risks:
  - none
