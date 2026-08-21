REPORT 2026-08-21-dynamic-sector-classification/12
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_analytics.py — new test test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other, pinning CR-1's fix.
  - services/quant-engine/app/tests/test_analytics.py — added import of UNCLASSIFIED_SECTOR_LABEL from app.analytics.overview.

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py app/tests/test_instrument_registry.py -q
  result:    PASS
  detail:    217 passed, 1 warning (pre-existing unrelated datetime.utcnow() DeprecationWarning) in 18.73s

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New test targets the exact gap 11-backend-cr1.md's handoff named: GHOST1, zero matching ImportedInstrument records — see § File choice.
  - No new shared fixture added; matched the existing sibling AC9 test's local construction pattern rather than fixtures.py's imported_snapshot() — see § File choice.
  - app.analytics.overview.MarketDataService is already autouse-mocked (conftest.py); the new test's explicit mocker.patch mirrors its sibling test, redundant but harmless.

risks:
  - none

## Orchestrator brief

- Added one regression test (test_analytics.py) pinning CR-1: a position with zero matching ImportedInstrument records lands in "Unclassified", never "Other".
- Test reproduces 10-quant-audit.md's exact GHOST1 repro shape and asserts via the UNCLASSIFIED_SECTOR_LABEL constant, not a hardcoded string.
- Fix confirmed complete for this reproduction shape — no discrepancy found, not filing PARTIAL.
- Verification command from the work order run and green: 217 passed (216 baseline + 1 new).
- No production code touched; no other existing test modified.
- Sections below: File choice (why test_analytics.py over test_instrument_registry.py).

---

## File choice

Placed the new test in `test_analytics.py`, adjacent to the existing AC9 test
(`test_build_portfolio_overview_discloses_unclassified_equity_bucket`), not
`test_instrument_registry.py`. CR-1's own fix (11-backend-cr1.md § Fix
direction rationale) changes `attach_snapshot_metadata`'s catch-all to
construct `Instrument(sector=None)` either way it's tested at the registry
level — the bug CR-1 fixed was specifically that `overview.py`'s
`instrument.sector or UNCLASSIFIED_SECTOR_LABEL` line saw a truthy `"Other"`
instead of a falsy `None`. A registry-level unit test would pin the
mechanism but not the observable contract violation (the literal string
reaching `sector_allocation`) that CR-1, AC9, and this work order's
`definition_of_done` all specify at the `build_portfolio_overview()` seam —
which is also the exact entry point the work order names.
