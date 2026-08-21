REPORT 2026-08-21-dynamic-sector-classification/14
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest app/tests/test_instrument_registry.py app/tests/test_analytics.py app/tests/test_equity_sector_resolution.py app/tests/test_instrument_identity.py app/tests/test_fmp_client.py -q
  result:    PASS
  detail:    264 passed, 1 warning (pre-existing unrelated datetime.utcnow() DeprecationWarning); also independently re-ran cd apps/desktop && npx tsc --noEmit (clean) and python scripts/detect_deadcode.py --strict (clean, ruff+vulture+knip)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Carried forward, non-blocking: quant-audit FINDING 2 (MINOR, taxonomy-lookup casing/whitespace) is still open. Not re-litigated per this order's non_goals — see § Coverage adequacy.
  - Housekeeping, outside the four tickets: docs/product/stories/US-24.12-...md is an untracked tombstone file (pre-dates this order) with its own "delete me" banner.
  - Recommend `git rm docs/product/stories/US-24.12-dynamic-equity-sector-classification.md` before this slice is committed, so the stray file doesn't ship alongside US-37.1.

risks:
  - The technical plan's own § Risks examined only the metadata.get() None case and missed the catch-all's own hardcoded "Other" — a design-pass blind spot, not a lane defect. See § Correctness against design.
  - Caught by quant-audit FINDING 1, closed by CR-1 — the pattern worth carrying forward: trace every producer of a seam's input value, not just the seam's own null-check.
  - MarketDataAuthError is deliberately swallowed inside resolve_equity_sector; a misconfigured FMP_API_KEY degrades every non-static equity with no distinct disclosure. Pre-existing, already surfaced by quant-audit, not new here.

## Orchestrator brief

- Verdict: PASS. No BLOCKING findings. Code matches 05-technical-plan.md's contract, reuse map and lane split field-for-field; CR-1's fix matches the design's stated intent for that branch.
- One SHOULD_FIX carried forward unchanged: quant-audit FINDING 2 (taxonomy-lookup casing/whitespace, equity_sector_resolution.py:74) — not re-litigated, still open for a future pass.
- One housekeeping item found via `git status`, unrelated to the four tickets: an untracked story tombstone file (US-24.12) should be `git rm`'d before commit — see handoff.
- Verification: re-ran the order's named pytest set (264 passed) plus tsc --noEmit and the dead-code strict gate independently — both clean. dashboardGoldens.ts confirmed untouched via git diff --stat.
- Sections below, in order: Contract alignment; Correctness against design (incl. CR-1); Reuse and consistency; Guardrails; Coverage adequacy. No CR files opened by this review.

---

## Contract alignment

Field-by-field, against `05-technical-plan.md` § Contract and `docs/contracts/exposure-fields.md`:

- `Instrument.classification_source: Literal["static","fmp_identity_confirmed","unavailable"] | None` (`schemas/instruments.py`) — matches the plan's naming exactly, including the deliberate avoidance of `"verified"`. Confirmed backend-internal: no `Instrument`-shaped type in `apps/desktop/src/features/portfolio/types.ts`; `ExposureResult.snapshot.instruments` is the unrelated `ImportedInstrument`. `exposure-fields.md`'s new subsection states this explicitly and correctly (not a missing contract row, a deliberate non-serialization).
- `PortfolioOverview.sector_allocation` / `sector_position_breakdown` — type declarations (`list[dict[str, float | str]]`, `dict[str, list[dict[str, float | str]]]`) unchanged, as planned. New value `"Unclassified"` is a plain string, requires no schema or TS change. Confirmed via `git diff` — `schemas/reconciliation.py` was not touched by any of the four tickets or CR-1.
- `docs/contracts/exposure-fields.md` — sector rows' Notes columns updated to name the Unclassified bucket; `classification_source` documented in its own non-contract-row subsection. Matches the plan's contract_notes exactly.
- No new route, no router registration to check — this story touches no `app/api/routes/` file or `app/api/main.py`. Confirmed via `git diff --stat`.

## Correctness against design (including CR-1)

Read the full diff of every changed file (`schemas/instruments.py`, `instruments/registry.py`, `instruments/equity_sector_resolution.py` (new), `services/instrument_identity.py`, `analytics/overview.py`, `core/settings.py`, `clients/fmp.py`) against `05-technical-plan.md` § Contract, § Resolution logic, § Decisions.

- Resolution order, taxonomy map (11 entries, all 5 divergent pairs), identity gate (`normalize_isin` reused, not reimplemented), fail-safe `except Exception` pattern, opt-in `market_data` threading, and the 30-day `fmp_profile_cache_ttl_seconds` — all match the plan's pseudocode and settled decisions verbatim. `resolve_equity_sector` in the repo is character-for-character consistent with the plan's § Resolution logic block.
- `attach_snapshot_metadata` threads `market_data` into both its equity-and-ETF-typed call sites (the ETF branch inside `classify_imported_instrument` ignores the parameter and returns early on keyword-inferred sector) — matches the plan's "threaded only into the equity-branch call sites" instruction; confirmed by a dedicated test (`test_etf_branch_ignores_market_data_and_makes_no_fmp_call`) and by reading the branch order in `classify_imported_instrument` (ETF check precedes the equity fallback).
- The import-cycle fix (lazy `from app.instruments.equity_sector_resolution import resolve_equity_sector` inside `classify_imported_instrument`, not at module level) is a structural necessity not covered by the plan; T-37.1.1's report explains it correctly and it is confirmed safe (dead-code gate and full suite both clean, no ImportError at any point).
- **CR-1's fix matches the design's stated intent.** FINDING 1 (quant-audit, MATERIAL) was that `attach_snapshot_metadata`'s pre-existing no-imported-instrument catch-all (`registry.py:337-346`) still hardcoded `sector="Other"`, a literal that survives `overview.py`'s new `instrument.sector or UNCLASSIFIED_SECTOR_LABEL` check because `"Other"` is truthy. CR-1's fix (`11-backend-cr1.md`) removes the `sector="Other"` constructor kwarg so the field defaults to `None` — routing through the exact same unresolved-outcome path the design already built for every other case, with zero change to `overview.py`. This is the minimal, design-consistent fix, not a new mechanism. Independently reproduced in this review: a one-position snapshot with `instruments=[]` yields `sector_allocation == [{'sector': 'Unclassified', ...}]`, `"Other"` absent — confirmed via direct read of the current `registry.py` (lines 337-352) and cross-checked against the passing regression test `test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other`.
- This was a genuine blind spot in my own design pass (05), not a lane defect — noted in risks above, not held against any engineering lane.

## Reuse and consistency

- `equity_sector_resolution.py` mirrors `instrument_enrichment.py::_enrich_one`'s bare `try/except Exception` fail-safe shape exactly, as instructed.
- `normalize_isin` (promoted from `instrument_identity._normalized_isin`) is imported and reused, not reimplemented; its 2 original call sites were updated in the same diff, and `equity_sector_resolution.py` is its only new consumer.
- `MarketDataService.get_company_profile` is reused via the existing service, never `FmpClient.get_profile()` called directly from the new module — confirmed by grep, no direct `FmpClient` import in `equity_sector_resolution.py`.
- No duplicated computation found: grepped the repo for `SECTOR_TAXONOMY_MAP` and for a second ISIN-comparison implementation — `equity_sector_resolution.py` is the sole definition of both. `risk.py`'s ETF look-through sector inference remains a separate, pre-existing, explicitly out-of-scope mechanism (both the new methodology section and the story's "Out of scope" list say so consistently).
- Test-file patterns are internally consistent with the existing suite: `_FakeMarketData` / `_SpyMarketData` duck-typed stand-ins mirror `test_instrument_enrichment.py`'s established pattern; the new `_mock_overview_engine_market_data` autouse conftest fixture mirrors the four existing per-engine fixtures exactly.

## Guardrails

- **No fabrication.** An FMP `sector` string not in `SECTOR_TAXONOMY_MAP` never passes through raw (tested: `test_unmapped_fmp_sector_string_never_passed_through_raw`). An ISIN mismatch never uses the FMP-sourced sector (tested at both the resolver and registry-wiring level).
- **Trust semantics honest.** `classification_source` never uses `"verified"` (reserved for `verified_total_return`); `"unavailable"` is never assigned to `Instrument.sector` itself — `sector` stays `None`, converted to the honestly-named `"Unclassified"` string exactly once, at the aggregation seam. Confirmed by reading every `return` statement in `resolve_equity_sector` and every write site of `Instrument.sector` in the diff.
- **Truth-class separation.** The new methodology section correctly labels this mechanism "snapshot analytics" (current market-data lookup at import time), distinct from broker truth — matches the module's own docstring.
- **No execution.** N/A, not touched.
- `"Unclassified"` correctly participates in `sector_hhi` / `top_sectors` / `top_sector_weight` with zero special-casing needed in `exposure_engine.py` (confirmed unchanged by `git diff`, and by quant-audit's independent HHI hand-derivation, which this review did not need to re-derive a third time).

## Coverage adequacy

Reviewed `test_equity_sector_resolution.py`, the `test_instrument_registry.py` additions, and the `test_analytics.py` additions (including the CR-1 regression) against the pack's own two brittleness patterns:

- No exact-equality assertion on a structure designed to grow: `test_sector_taxonomy_map_covers_at_least_the_eleven_verified_sectors` deliberately uses set containment (`<=`), not dict equality, so a future 12th taxonomy entry does not fail an unrelated test — while a separate, explicit test still pins the current 11 mappings by value.
- No assertion pinning an implicit, never-set default: the AC1/AC10 tests use a `_SpyMarketData` that records calls, asserting `market_data.calls == []` to prove non-invocation directly, rather than inferring it from an unrelated field.
- Tests assert observable contract behavior (`sector`, `classification_source`, `sector_allocation` bucket membership, weight totals) rather than internal call shape, with one narrow, justified exception (`_SpyMarketData.calls`, which is itself the AC1/AC10 claim being tested — "no call is made" — not an implementation detail).
- The CR-1 regression test (`test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other`) was independently confirmed (by the quant-audit recheck, and again in this review by reading it directly) to be a real pin: it would fail against the pre-fix code, not a vacuous assertion.

No coverage gaps found beyond the already-carried-forward FINDING 2 (untested casing/whitespace drift on the taxonomy lookup — MINOR, non-blocking, not re-litigated).
