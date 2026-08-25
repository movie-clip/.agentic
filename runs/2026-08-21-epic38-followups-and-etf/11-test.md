REPORT 2026-08-21-epic38-followups-and-etf/11
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_analytics.py — added 20 tests covering AC1-AC9 of US-38.1 look-through sector classification (see § Test inventory)
  - services/quant-engine/app/tests/test_exposure_engine.py — added a "no literal Other anywhere" regression assertion to the existing full-IB2026-statement exposure test

verification:
  command:   cd services/quant-engine && python scripts/run_all_tests.py (run from repo root per work order)
  result:    PASS
  detail:    backend 878 passed (up from 858 in 09-backend.md, +20 new tests); frontend 331 passed / 37 files; tsc clean; dead-code gate clean (ruff/vulture/knip all clean); dashboardGoldens.ts untouched

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test_risk.py was never created — extended app/tests/test_analytics.py instead, matching the existing sector-exposure test already there, per 09-backend.md's own handoff note
  - new private-function imports added to test_analytics.py's risk import line: _build_shared_sector_overlap, _fund_category_proxy_sector (mirrors the file's existing underscore-import pattern)
  - _NoNetworkCallMarketData (local class in test_analytics.py) is a spy raising AssertionError on get_company_profile/get_etf_holdings, proving AC5 for _build_shared_sector_overlap
  - build_lookthrough_sector_exposure needs no network-call spy — it takes no market_data param at all; covered by a signature-introspection test instead
  - all 8 companion-curated tickers (XLF, XLV, IBB, ITA, PPA, BIL, VGSH, DBC) covered via one parametrized test, each exercised as an actual source ETF

risks:
  - none
