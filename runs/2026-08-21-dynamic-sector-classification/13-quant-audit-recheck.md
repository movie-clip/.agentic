REPORT 2026-08-21-dynamic-sector-classification/13
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   independent recomputation of FINDING 1's exact reproduction case (new script, different symbol NOREC1 vs. the shipped test's GHOST1) via build_portfolio_overview(); targeted pytest -q on the one new regression test; sanity grep of adjacent attach_snapshot_metadata consumers in risk.py
  result:    PASS
  detail:    anchor: independent re-derivation (own script, own symbol, not copied from the shipped test) — overview.sector_allocation == [{'sector': 'Unclassified', 'market_value': 100.0, 'weight': 1.0}], 'Other' absent. pytest test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other: 1 passed in 1.75s.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - none

## Orchestrator brief

- Verdict: PASS. FINDING 1 (10-quant-audit.md) is resolved by CR-1's fix; independently re-derived, not just re-read — see § Independent re-derivation.
- Fix is minimal and exactly scoped: `registry.py`'s no-imported-instrument catch-all now omits the `sector="Other"` kwarg (schema default `None`), letting `overview.py`'s pre-existing `instrument.sector or UNCLASSIFIED_SECTOR_LABEL` do its job. `overview.py` itself is untouched, confirmed via `git diff`.
- Sanity check on adjacent `attach_snapshot_metadata` callers (`risk.py:611`, `risk.py:1463`): both read only `.asset_class`, never `.sector`, from the metadata dict — no regression surface from this change. `risk.py`'s two other `.sector`-reading call sites (`registry.get_instrument`, lines 1038/1649) use a different registry method entirely, unaffected.
- New regression test (`12-test-cr1.md`) reviewed: it exercises the exact catch-all branch (GHOST1, `instruments=[]`, not statically registered — confirmed by grep), asserts both `sector_allocation` and `sector_position_breakdown`, and would fail against the pre-fix code (the assertion `"Other" not in sectors` is a real pin, not vacuous). Not passing for the wrong reason.
- FINDING 2 (MINOR, taxonomy casing/whitespace, `equity_sector_resolution.py:74`) — status unchanged, confirmed untouched by CR-1 (`git status` shows it untracked/unmodified by this CR), not re-litigated per non_goals.
- No new findings. Nothing else outstanding from the quant gate on this story.
- Sections below: Independent re-derivation; Adjacent-path sanity check; Test review.

---

## Independent re-derivation

Wrote a standalone script (not copied from `12-test-cr1.md`'s test — different symbol, written directly from `10-quant-audit.md` FINDING 1's reproduction description) against the current merged code:

- One-position `ImportedPortfolioSnapshot`, symbol `NOREC1`, `instruments=[]` (zero matching `ImportedInstrument` records — the exact gap).
- Ran through `build_portfolio_overview(snapshot)`.

Result:
```
overview.sector_allocation == [{'sector': 'Unclassified', 'market_value': 100.0, 'weight': 1.0}]
```
`"Other"` is absent from the sector set; `Unclassified` carries the full market value and weight=1.0. This matches `definition_of_done` exactly and is the inverse of the audit's original repro (`[{'sector': 'Other', 'market_value': 100.0, 'weight': 1.0}]`).

Confirmed via `git diff -- services/quant-engine/app/instruments/registry.py` that the only change in the catch-all (lines ~337-346) is the removal of the `sector="Other"` constructor kwarg — `Instrument.sector` defaults to `None` per `schemas/instruments.py:31`. No other line in the catch-all changed. `overview.py`'s consuming line (`sector = instrument.sector or UNCLASSIFIED_SECTOR_LABEL`, `overview.py:58`) is unchanged from the original story's diff, pre-dating CR-1 — confirmed CR-1 touched only `registry.py`, consistent with `11-backend-cr1.md`'s stated fix direction and CR-1's own non_goals ("do not touch anything else in registry.py or overview.py beyond what this fix requires").

## Adjacent-path sanity check

`attach_snapshot_metadata` has three other call sites besides `overview.py`:
- `risk.py:611` (`build_lookthrough_exposure`'s coverage calc) — reads only `instrument.asset_class`, never `.sector`. Unaffected.
- `risk.py:1463` (`build_etf_overlap_pairs`) — reads only `instrument.asset_class`. Unaffected.
- Two test files (`test_importer.py`, `test_instrument_registry.py`) — pre-existing, unrelated to this branch.

`risk.py`'s two `.sector`-reading sites (line 1038 in `build_lookthrough_sector_exposure`, line 1649 in `_build_shared_sector_overlap`) call `registry.get_instrument(symbol)` — the static-dict lookup method — not `attach_snapshot_metadata`'s per-snapshot catch-all. These are a structurally separate mechanism (confirmed in the original audit, `10-quant-audit.md`: "`risk.py`'s ETF look-through mechanism is a separate, pre-existing, keyword-based path"), and their own `"Other"` literal fallback is pre-existing and out of scope for this story and this CR. No regression introduced by CR-1 in either path.

## Test review

`test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other` (`test_analytics.py:442`):
- Constructs a snapshot shaped identically to FINDING 1's repro (one position, symbol not in the static registry, `instruments=[]`) — confirmed `GHOST1` is not present anywhere in `app/instruments/` static definitions (grep), so the test genuinely reaches the catch-all branch rather than an earlier one.
- Asserts `"Other" not in sectors` — a real regression pin: reverting the fix (re-adding `sector="Other"`) would fail this exact assertion, not just an unrelated one.
- Also asserts `UNCLASSIFIED_SECTOR_LABEL in sectors`, correct `market_value`/`weight`, and that `GHOST1` appears in `sector_position_breakdown[UNCLASSIFIED_SECTOR_LABEL]` — broader than the minimal repro, catching a regression in the breakdown map too.
- The `mocker.patch("app.analytics.overview.MarketDataService")` is inert for this specific branch (the catch-all never invokes `resolve_equity_sector`), as the test author's own handoff note says — harmless, not a flaw.
- Verdict: pins the right behaviour at the right seam (`build_portfolio_overview`, matching this order's `definition_of_done` entry point), would fail without the fix, does not pass for the wrong reason.

Ran narrowly: `pytest app/tests/test_analytics.py::test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other -q` → `1 passed in 1.75s`. Full suite intentionally not run, per this order's non_goals.
