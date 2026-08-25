REPORT 2026-08-24-etf-sector-classification-research/11
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/analytics/overview.py — build_portfolio_overview gains keyword-only `market_data: object | None = None`, defaults to MarketDataService() when None
  - services/quant-engine/app/scripts/export_dashboard_goldens.py — `_build_fixture` now passes `market_data=market_data` into build_portfolio_overview (was previously dropped)
  - apps/desktop/src/test/dashboardGoldens.ts — regenerated; SBIO now renders "Unclassified" not "Health Care" — see § Regeneration detail

verification:
  command:   cd /c/projects/investments/portfolio && python scripts/run_all_tests.py 2>&1 | tail -100
  result:    PASS
  detail:    905 backend passed (was 904 passed, 1 failed pre-fix); 331 frontend passed (37 files); tsc clean; dead-code gate clean; test_generated_matches_committed_goldens now green

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test_generated_matches_committed_goldens confirmed green standalone (4 passed) and in the full suite; no new test written, per non_goals
  - RecordingMarketData (--capture path) narrowly changed behavior for future dynamic-lookup symbols — see § Risk detail

risks:
  - DoD asked to confirm the RecordingMarketData capture path is unaffected; reading shows it is narrowly affected — see § Risk detail
  - Two existing call sites (exposure_engine.py:48, portfolio_imports.py re-export) confirmed unchanged by reading and by the full green suite

## Orchestrator brief
- T-39.1.7 landed: build_portfolio_overview gained the keyword-only `market_data` seam; export_dashboard_goldens.py now threads its own frozen/recording provider through it.
- Full suite is green: `run_all_tests.py` PASS end to end (905 backend, 331 frontend, tsc, dead-code all clean). The prior blocking defect (10-test.md) is resolved.
- dashboardGoldens.ts regenerated and committed-in-place: SBIO now correctly renders "Unclassified" instead of stale live-cache-derived "Health Care"/"Consumer Discretionary" weight — see § Regeneration detail.
- One finding beyond the order's literal DoD: the `--capture` path (RecordingMarketData) now also fails closed for any future dynamic-lookup symbol, since it lacks get_company_profile/get_etf_sector_weightings passthrough — see § Risk detail. Not fixed (frozen_market_data.py is out of this order's scope); flagged for a possible follow-up ticket.

## § Regeneration detail

`run_all_tests.py`'s golden-generation step (`python -m app.scripts.export_dashboard_goldens`) now routes sector resolution through `FrozenMarketData.from_file()` for both statements. `git diff apps/desktop/src/test/dashboardGoldens.ts` shows SBIO moving from a 1.6%/1.1% split across "Health Care"/"Consumer Discretionary" (stale, live-cache-derived) to its own dedicated "Unclassified" bucket (357.05, 0.55%), with "Health Care" now correctly showing only AAPL's actual weight (1.1%). No other symbol's sector changed — SBIO is the only instrument in the golden statement reaching the dynamic-lookup branch (confirmed by test-engineer's prior diagnosis and reconfirmed by the diff's narrow scope).

## § Risk detail

`FrozenMarketData` (the default, non-`--capture` provider) does not implement `get_company_profile` or `get_etf_sector_weightings` — it only duck-types the four price-history methods `run_imported_dashboard_history` consumes (`get_historical_prices`, `get_direct_verified_benchmark_history`, `get_historical_prices_for_symbols`, `get_last_fetch_meta`). Calling either missing method raises `AttributeError`, which `resolve_etf_sector`/`resolve_equity_sector` both catch via a bare `except Exception` (AC10/AC8), returning `(None, "unavailable")` — this is the exact fail-closed path that produces SBIO's correct "Unclassified" result, and matches this order's own non_goals framing of that behavior as correct, not a defect.

`RecordingMarketData` (the `--capture` provider, wraps a real `MarketDataService`) has the identical gap: it implements only the same four price-history methods, no `__getattr__` passthrough to the wrapped real service, and no company-profile/sector-weightings recording at all. Before this fix, `build_portfolio_overview` never received `market_data` at all, so sector resolution during `--capture` ran through a second, independent, real `MarketDataService()` instance — meaning a live `--capture` run with a warm FMP cache/API key could resolve a real sector for any dynamic-lookup symbol. After this fix, `--capture` routes sector resolution through the same `RecordingMarketData` instance used for prices, which lacks the two profile/weightings methods — so a future dynamic-lookup symbol (SBIO today, or any new one added later) will also fail closed to "Unclassified" during `--capture`, even with a live key, until `RecordingMarketData`/`FrozenMarketData` gain those two methods.

This does not break anything today: SBIO already resolves to "Unclassified" via the frozen path (the DoD's stated goal), no test currently exercises `--capture`'s sector-resolution behavior, and the change is consistent with the project's fail-closed guardrail. But the order's framing — "confirm ... is unaffected" — does not hold under a strict reading; the capture path's sector-resolution capability is now narrower than before. `frozen_market_data.py` is outside this order's scope (non_goals names it explicitly), so no code change was made here. Flagging per protocol § 6 rather than silently building past the order's stated premise.
