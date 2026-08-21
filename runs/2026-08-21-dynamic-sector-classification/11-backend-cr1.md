REPORT 2026-08-21-dynamic-sector-classification/11
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/instruments/registry.py — no-imported-instrument catch-all in attach_snapshot_metadata (~line 337) no longer hardcodes sector="Other"; sector now defaults to None.

verification:
  command:   cd services/quant-engine && pytest app/tests/test_instrument_registry.py app/tests/test_analytics.py -q
  result:    PASS
  detail:    216 passed, 1 warning (unrelated pre-existing datetime.utcnow() DeprecationWarning) in 20.39s

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - No test asserts literal "Other" for this specific no-imported-instrument catch-all path (checked both named test files) — see § Test coverage gap.
  - test_build_portfolio_overview_returns_expected_totals's ZZZ9 case has a matching instrument entry, so it does not exercise this catch-all branch.
  - test-engineer: consider a regression test pinning "Unclassified" for a position with zero matching ImportedInstrument records specifically.
  - Fix direction chosen: registry.py constructor change (sector=None), not overview.py special-case — see § Fix direction rationale.
  - classification_source is unaffected — already defaulted to None on this branch before this fix, per schemas/instruments.py's own docstring for this catch-all.

risks:
  - none

## Orchestrator brief

CR-1 fix applied and independently reproduced fixed. Smaller diff chosen (registry.py sector=None), overview.py untouched. 216 tests pass, none pinned old "Other" behavior for this exact branch — test-engineer handoff for optional new coverage. Sections below: Independent reproduction; Fix direction rationale; Test coverage gap.

---

## Independent reproduction

Ran the audit's exact repro (one-position snapshot, symbol GHOST1, zero matching ImportedInstrument records) through build_portfolio_overview() after the fix:
`overview.sector_allocation == [{'sector': 'Unclassified', 'market_value': 100.0, 'weight': 1.0}]` — confirms the fix, matches definition_of_done.

## Fix direction rationale

CR-1 offered two directions: change the catch-all's Instrument constructor (registry.py) to not write sector="Other", or special-case it in overview.py. Chose the registry.py constructor change: `Instrument.sector` is already `str | None = None` in schemas/instruments.py, and overview.py's existing `instrument.sector or UNCLASSIFIED_SECTOR_LABEL` line already handles a None sector correctly — so the fix is a one-line deletion (drop the `sector="Other"` kwarg) with zero changes needed in overview.py, versus adding a new special case there. This also brings the catch-all in line with the equity branch a few lines above it in the same file, which this story already migrated from a literal "Other" to `sector=None` for the identical reason.

## Test coverage gap

Grepped both named test files for `"Other"` and for constructions of a snapshot position with zero matching `ImportedInstrument` records. `test_unknown_symbol_falls_back_to_other` (test_instrument_registry.py:115) pins a different mechanism (`registry.get_sector`, the static-dict-only lookup) and is unaffected by this change. `test_build_portfolio_overview_discloses_unclassified_equity_bucket` (test_analytics.py:402) uses ZZZ9 with a matching `ImportedInstrument` entry, so it exercises `classify_imported_instrument`'s equity branch, not the `attach_snapshot_metadata` catch-all this CR fixes. No test in either file constructs a position with zero matching instrument records, so nothing needed editing — but the exact branch this CR fixed has no direct regression coverage.
