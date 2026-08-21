REPORT 2026-08-21-dynamic-sector-classification/06
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/instruments.py — added ClassificationSource Literal and Instrument.classification_source field, per plan § Contract
  - services/quant-engine/app/instruments/equity_sector_resolution.py — new module: SECTOR_TAXONOMY_MAP (11 entries) + resolve_equity_sector, per plan § Resolution logic
  - services/quant-engine/app/instruments/registry.py — _instrument gains classification_source kwarg, sector now str|None
  - services/quant-engine/app/instruments/registry.py — classify_imported_instrument gains keyword-only market_data param; equity branch calls resolve_equity_sector when supplied
  - services/quant-engine/app/instruments/registry.py — attach_snapshot_metadata gains keyword-only market_data param, threaded to both equity-branch call sites only
  - services/quant-engine/app/instruments/registry.py — _merge_known_instrument_metadata now always sets classification_source="static" on static-dict hits
  - services/quant-engine/app/services/instrument_identity.py — _normalized_isin promoted to public normalize_isin, its 2 internal call sites updated

verification:
  command:   cd services/quant-engine && pytest app/tests/test_instrument_registry.py app/tests/test_instrument_identity.py -q
  result:    PASS
  detail:    28 passed in 1.38s (also re-ran with test_importer.py added: 53 passed, no regressions)

contract_notes:
  - classification_source is backend-internal, never serialized (no Instrument-shaped TS type exists) — no TS mirror needed, see § Detail
  - docs/finance/financial-methodology.md needs a new "Sector/Industry Classification" section — T-37.1.3, per plan's own contract_notes
  - docs/contracts/exposure-fields.md sector rows need the "Unclassified" bucket note once T-37.1.2 lands — T-37.1.3

pack_corrections:
  - none

handoff:
  - T-37.1.2 (overview.py): equity branch now returns sector=None (not "Other") only when market_data is supplied to attach_snapshot_metadata
  - T-37.1.2 must construct MarketDataService() and pass market_data=... into attach_snapshot_metadata; signature ready, defaults to None
  - A real import cycle (registry -> equity_sector_resolution -> instrument_identity -> registry) exists and was resolved — see § Detail
  - test-engineer: resolve_equity_sector's market_data param is duck-typed; any object with get_company_profile(symbol) works for mocking, see § Detail
  - test-engineer: _merge_known_instrument_metadata behavior change (always copies now) — see § Detail

risks:
  - Import-cycle fix is load-bearing; see § Detail for why the lazy import inside classify_imported_instrument must not move to module level
  - _merge_known_instrument_metadata no longer short-circuits to the same object instance when there are no other updates — see § Detail

## Orchestrator brief

- T-37.1.1 done: schema field added, new resolution module created, registry.py equity branch + attach_snapshot_metadata threaded with opt-in market_data, normalize_isin promoted. Verification green (28 passed).
- One load-bearing structural finding not in the plan text: a real circular import (registry -> equity_sector_resolution -> instrument_identity -> registry, since instrument_identity.py imports InstrumentRegistry) required a local/lazy import inside classify_imported_instrument instead of a module-level import. Verified safe under all plausible import orderings. See § Detail below.
- No AC/DoD conflicts found; ETF branch, futures, and risk.py's two attach_snapshot_metadata call sites confirmed untouched by diff review.

## Detail

**Import cycle.** `equity_sector_resolution.py` imports `normalize_isin` from `instrument_identity.py`, which imports `InstrumentRegistry` from `registry.py`. A module-level `from app.instruments.equity_sector_resolution import resolve_equity_sector` at the top of `registry.py` therefore cycles back to itself before `InstrumentRegistry` is defined, raising `ImportError: cannot import name 'InstrumentRegistry' from partially initialized module`. Fixed by importing `resolve_equity_sector` locally, inside `classify_imported_instrument`, only when `market_data is not None`. Verified by direct reproduction and by testing all 3 plausible first-import orderings (`equity_sector_resolution` first, `instrument_identity` first, `registry` first) — all succeed with the lazy import in place. Do not move that import back to module level in a future change.

**classification_source is backend-internal.** Confirmed no `Instrument`-shaped TS type exists in `apps/desktop/src/features/portfolio/types.ts`; `ExposureResult.snapshot.instruments` is the separate `ImportedInstrument` type (raw broker-parsed, pre-classification). This was already settled by the tech lead in `05-technical-plan.md` § Contract — restated here only so the schema-edit hook's reminder isn't misread as a gap.

**resolve_equity_sector's market_data typing.** The parameter is annotated `MarketDataService` under `TYPE_CHECKING` (no runtime import, to avoid re-triggering any future cycle), but the function only calls `.get_company_profile(symbol)` on it — any duck-typed object with that method works, matching how `instrument_enrichment.py`'s existing tests already mock `MarketDataService`.

**_merge_known_instrument_metadata behavior change.** Previously: `return instrument.model_copy(update=updates) if updates else instrument` — when there was nothing to merge (no imported record, no currency), the exact same `Instrument` object instance was returned. Now `updates` always contains `classification_source: "static"`, so `model_copy` always runs — same field values, but a new instance every time. Only matters if a test asserts identity (`is`) rather than equality (`==`) on the returned instrument for a static-registry hit; none found in the two test files run for this ticket's verification command.
