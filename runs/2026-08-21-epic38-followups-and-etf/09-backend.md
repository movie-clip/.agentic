REPORT 2026-08-21-epic38-followups-and-etf/09
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/analytics/risk.py — deleted _infer_sector_from_sources, _infer_sector_from_resolved_pair, ungated get_company_profile fallback
  - services/quant-engine/app/analytics/risk.py — added FUND_CATEGORY_OVERRIDE_CATEGORIES constant, _fund_category_proxy_sector helper, Unclassified suppression exemption
  - services/quant-engine/app/instruments/registry.py — added 8 curated entries (XLF, XLV, IBB, ITA, PPA, BIL, VGSH, DBC) to INSTRUMENT_DEFINITIONS

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -x -q; python -m pytest -q (full suite); python scripts/detect_deadcode.py --strict
  result:    PASS
  detail:    app/tests/test_risk.py does not exist (T-38.1.4 not yet dispatched) — ran the closest existing coverage instead: test_analytics.py 194 passed; full backend suite 858 passed, 0 failed; detect_deadcode --strict clean (ruff/vulture/knip all clean)

contract_notes:
  - docs/contracts/exposure-fields.md (203-219) and financial-methodology.md need the Unclassified-bucket prose update — already scoped as T-38.1.3, no schema change

pack_corrections:
  - none

handoff:
  - app/tests/test_risk.py does not exist yet — T-38.1.4 creates it, or extends test_analytics.py, whichever pattern the existing sector-exposure tests already use
  - build_lookthrough_sector_exposure, _build_shared_sector_overlap, _fund_category_proxy_sector ready for T-38.1.4's full test-plan coverage, incl. no-network-call and companion-curation regressions
  - the 8 new registry entries (XLF, XLV, IBB, ITA, PPA, BIL, VGSH, DBC) are live in INSTRUMENT_DEFINITIONS for T-38.1.4's companion-curation coverage

risks:
  - order's verification named app/tests/test_risk.py, which does not exist — ran test_analytics.py + full pytest suite instead
  - _build_shared_sector_overlap's market_data param is now unused (its only use was the deleted get_company_profile call) but left in the signature per minimal-diff scope discipline
