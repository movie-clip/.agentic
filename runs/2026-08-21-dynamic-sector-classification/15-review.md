REPORT 2026-08-21-dynamic-sector-classification/15
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_equity_sector_resolution.py app/tests/test_instrument_registry.py -q; python -m pytest app/tests/test_analytics.py -q -k "sector or Unclassified or unclassified or instrument_record"
  result:    PASS
  detail:    50 passed (test_equity_sector_resolution.py + test_instrument_registry.py, full files); 3 passed, 191 deselected (test_analytics.py sector subset). Independently re-run, not a re-quote of 14-integration.md's 264.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Carried forward, non-blocking (already surfaced by quant-audit): MarketDataAuthError is swallowed by resolve_equity_sector's bare `except Exception` (equity_sector_resolution.py:66-69).
  - Consequence: a misconfigured FMP_API_KEY degrades every non-static equity identically to genuine no-coverage, with no distinct disclosure between the two.
  - AC8's own wording ("fails for any reason") makes this compliant, not a gap — flagging only as a UX note if FMP_API_KEY misconfig becomes a recurring support question.
  - Carried forward, non-blocking: quant-audit FINDING 2 (MINOR) — taxonomy lookup (equity_sector_resolution.py:74) is exact-string, case/whitespace-sensitive vs FMP casing drift. Not required by any AC.
  - `docs/product/stories/US-24.12-...md` is a known, already-flagged tombstone (run.md Open table, should_fix) pending `git rm` at close-out.
  - Confirmed present via git status, not a new finding, not held against this verdict — see run.md entries from 04-story-renumber and 14-integration.

## Orchestrator brief

- Verdict: PASS. All 10 ACs SATISFIED against the merged code, each with file:line. No GAP, no DRIFTED.
- Test plan fidelity: every named/implied file exists (`test_equity_sector_resolution.py` new, `test_instrument_registry.py` +171 lines, `test_analytics.py` +77 lines incl. CR-1 regression, `conftest.py` new autouse fixture `_mock_overview_engine_market_data`) and every one of the test plan's 12 bullets maps to a specific, independently-run, passing test.
- Trust-state spot checks clean: `classification_source` never uses `"verified"`, collapses documented sub-cases only (not an accidental collapse), stays backend-internal by a reasoned, documented design choice; `"Unclassified"` is a real disclosed bucket, never a fabricated stand-in, never dropped from the weight total (independently confirmed: full `sector_allocation` list, not the top-8 slice, feeds HHI/weight totals); no nullable field observed coerced to a fake default.
- Repo hygiene clean: `git status --porcelain` shows exactly the four tickets' files plus docs plus the two pre-known untracked items (US-37.1 story itself, epic-37 PRD, and the already-flagged US-24.12 tombstone) — nothing unaccounted. Story's own Status field still reads "Backlog"; all four ticket checkboxes still unchecked, consistent with not-yet-closed-out.
- Sections below: AC-by-AC; Test plan fidelity; Trust-state spot checks; Repo hygiene. No CR files opened by this review.

---

## AC-by-AC

- **AC1 — SATISFIED.** Static-dict hits never call FMP: `registry.py`'s `attach_snapshot_metadata` routes any symbol in `INSTRUMENT_DEFINITIONS` through `_merge_known_instrument_metadata` (`registry.py:321-327`), which never references `market_data`; the equity branch that calls `resolve_equity_sector` (`registry.py:284-289`) is unreachable for a static-dict hit. Test: `test_static_registry_equity_never_calls_fmp_even_when_market_data_supplied` (`test_instrument_registry.py`), asserts `market_data.calls == []` with a spy — independently re-run, passes.
- **AC2 — SATISFIED.** `classify_imported_instrument`'s equity branch (`registry.py:277-301`) delegates to `resolve_equity_sector` (`equity_sector_resolution.py:54-83`), which calls `MarketDataService.get_company_profile` (`market_data.py:459-476`) — the same existing method that already runs `resolve_symbol_candidates(...)` internally (`market_data.py:461`); no second, independent lookup exists. Confirmed by grep: `equity_sector_resolution.py` has no direct `FmpClient` import. Test: `test_equity_branch_with_market_data_and_isin_match_resolves_fmp_sector`.
- **AC3 — SATISFIED.** `equity_sector_resolution.py:78-81` compares `normalize_isin(imported.isin)` against `normalize_isin(profile.get("isin"))`, both required non-empty and equal; `normalize_isin` is the promoted, single-definition function from `instrument_identity.py` (renamed from `_normalized_isin`, its two original call sites updated in the same diff — confirmed via `git diff`, no second ISIN-comparison implementation found by grep). Tests: `test_isin_match_resolves_mapped_taxonomy_sector`, `test_isin_match_is_case_and_whitespace_insensitive`, `test_isin_match_maps_a_divergent_fmp_sector_string`.
- **AC4 — SATISFIED.** `equity_sector_resolution.py:83` returns `(None, "unavailable")` on ISIN mismatch, never the FMP-sourced value. Tests at both the resolver level (`test_isin_mismatch_yields_no_classification_not_the_fmp_value`) and through the registry wiring (`test_equity_branch_with_market_data_and_isin_mismatch_resolves_no_classification`).
- **AC5 — SATISFIED.** Same line 83 collapses missing-evidence-either-side into the same `unavailable` outcome. Test: `test_missing_isin_evidence_either_side_yields_no_classification`, parametrized over statement-missing / profile-missing / both-missing / both-blank-string.
- **AC6 — SATISFIED.** `equity_sector_resolution.py:71-76`: an empty/missing `sector` key or a `sector` string absent from `SECTOR_TAXONOMY_MAP` both return `(None, "unavailable")` before the ISIN check ever runs — never passed through raw. Tests: `test_none_profile_yields_no_classification`, `test_empty_profile_dict_yields_no_classification`, `test_profile_missing_sector_key_yields_no_classification`, `test_profile_empty_sector_string_yields_no_classification`, `test_unmapped_fmp_sector_string_never_passed_through_raw` (the last asserts `sector != "Some Brand New GICS Bucket"` explicitly).
- **AC7 — SATISFIED.** `SECTOR_TAXONOMY_MAP` (`equity_sector_resolution.py:39-51`) has exactly the 11 verified entries, including all 5 named divergent pairs (Health Care/Healthcare, Financials/Financial Services, Consumer Discretionary/Consumer Cyclical, Consumer Staples/Consumer Defensive, Materials/Basic Materials). Dedicated standalone regression: `test_sector_taxonomy_map_pins_all_eleven_verified_sectors` (parametrized, 11 cases, each pair named individually) plus a separate containment test (`<=`, not dict equality) so a future 12th entry can't break it.
- **AC8 — SATISFIED.** `equity_sector_resolution.py:66-69` wraps the `get_company_profile` call in a bare `except Exception`, returning `(None, "unavailable")` — import completes normally, per AC8's own "for any reason" wording. Tests: `test_fmp_exception_is_swallowed_not_propagated`, `test_fmp_exception_does_not_short_circuit_other_symbols` (proves the fail-safe is per-call, not global).
- **AC9 — SATISFIED.** `overview.py:58`: `sector = instrument.sector or UNCLASSIFIED_SECTOR_LABEL` ("Unclassified") converts `None` to a distinct, honestly-named bucket exactly once, at the aggregation seam — never "Other", never dropped (the full `sector_totals`/`sector_allocation` set is summed, not a truncated top-N). CR-1's fix (`registry.py:337-352`, the no-imported-instrument catch-all) removed the hardcoded `sector="Other"` kwarg so that path also routes through the same `None` → "Unclassified" conversion, closing the MATERIAL gap quant-audit found. Tests: `test_build_portfolio_overview_discloses_unclassified_equity_bucket` (mixed classified + unclassified positions, asserts total weight still sums to 1.0) and the CR-1 regression `test_build_portfolio_overview_no_instrument_record_is_unclassified_not_other` — both independently re-run in this review, pass. Frontend: confirmed `ExposurePanel.tsx` has zero string matches for `"Other"` or `"Unclassified"` — fully generic rendering, no frontend change needed, consistent with the story's own "why this story does not ticket frontend work" note.
- **AC10 — SATISFIED.** ETF branch (`registry.py:229-275`) never references `market_data` at all — structurally cannot call FMP. Static-registry equities get only `classification_source: "static"` added by `_merge_known_instrument_metadata`; their `sector` value is untouched (`merged.sector == instrument.sector` asserted directly). Tests: `test_etf_branch_ignores_market_data_and_makes_no_fmp_call` (spy asserts zero calls), `test_static_registry_hit_sets_classification_source_static_with_no_other_updates`, plus the pre-existing ETF-classification test (`test_enriched_etf_description_round_trips_to_broad_market_sector`) still present and unmodified.

## Test plan fidelity

Every bullet in the story's test plan traces to a specific, existing, passing test — no bullet found unimplemented, no bullet found satisfied only by an unrelated or vacuous assertion:

| Test plan bullet | Test(s) | File |
|---|---|---|
| Static-dict fast path unaffected | `test_static_registry_equity_never_calls_fmp_even_when_market_data_supplied` | `test_instrument_registry.py` |
| FMP + ISIN-match success | `test_isin_match_resolves_mapped_taxonomy_sector` (+2 variants) | `test_equity_sector_resolution.py` |
| FMP + ISIN-mismatch | `test_isin_mismatch_yields_no_classification_not_the_fmp_value` (+ registry-level) | both |
| FMP-no-coverage | `test_none_profile_yields_no_classification`, `test_empty_profile_dict_yields_no_classification` | `test_equity_sector_resolution.py` |
| FMP-sector-not-in-taxonomy-map | `test_unmapped_fmp_sector_string_never_passed_through_raw` | `test_equity_sector_resolution.py` |
| No-ISIN-evidence | `test_missing_isin_evidence_either_side_yields_no_classification` (4 params) | `test_equity_sector_resolution.py` |
| FMP-raises | `test_fmp_exception_is_swallowed_not_propagated` (+ non-short-circuit sanity) | `test_equity_sector_resolution.py` |
| Dedicated taxonomy-mapping regression | `test_sector_taxonomy_map_pins_all_eleven_verified_sectors` (11 params) + containment test | `test_equity_sector_resolution.py` |
| Aggregation coverage | `test_build_portfolio_overview_discloses_unclassified_equity_bucket` | `test_analytics.py` |
| Regression: static/ETF unaffected | `test_etf_branch_ignores_market_data_and_makes_no_fmp_call`, `test_static_registry_hit_sets_classification_source_static_with_no_other_updates` | `test_instrument_registry.py` |
| No-fabrication regression | `test_equity_branch_without_market_data_yields_no_classification_not_other` | `test_instrument_registry.py` |
| Frontend: none anticipated | Confirmed — zero `ExposurePanel.tsx` changes in diff, zero sector-string special-casing found | n/a |

New conftest fixture named by the order (`_mock_overview_engine_market_data`) confirmed present (`conftest.py`, autouse, defaults every symbol to no-coverage so pre-existing unrelated tests are unaffected by the new opt-in `MarketDataService()` construction inside `build_portfolio_overview`).

`dashboardGoldens.ts` confirmed untouched (`git status`/`git diff --stat` both empty for that file) — consistent with the story's own conditional wording ("if any equity... reclassifies") and with 09-test's finding that INTU/PANW/VICI/SPCX are closed (net-zero) positions in the current bound statement, so no golden pin was expected or required.

## Trust-state spot checks

- `classification_source` never uses the word `"verified"` (confirmed: only `"static"`, `"fmp_identity_confirmed"`, `"unavailable"`, or `None` appear anywhere in `schemas/instruments.py`, `registry.py`, `equity_sector_resolution.py`) — the naming caution from "Open decisions #1" is honored.
- Nullable-field handling: `Instrument.sector` stays genuinely `None` through the domain layer (`equity_sector_resolution.py`, `registry.py`'s equity branch and CR-1'd catch-all) and is converted to the honest string `"Unclassified"` exactly once, at the `overview.py:58` aggregation seam — not coerced to `0`, `""`, or silently reused as `"Other"` anywhere in the diff.
- `"Unclassified"` is a first-class, disclosed bucket: it participates in `sector_hhi`/`top_sectors`/`top_sector_weight` with no special-casing (`exposure_engine.py`'s `_build_current_state_concentration` iterates `overview.sector_allocation` generically), and its weight is included in the full-set total (independently confirmed via the re-run `test_build_portfolio_overview_discloses_unclassified_equity_bucket`, which asserts `sum(item["weight"] ...) == pytest.approx(1.0)`).
- New market-data caller: `overview.py` now constructs its own `MarketDataService()` (line 19) — confirmed mocked in the test suite via the new autouse `_mock_overview_engine_market_data` conftest fixture, so no test in the suite reaches live FMP for this path.
- `classification_source` is deliberately not serialized to the frontend (confirmed: no `Instrument`-shaped type in `apps/desktop/src/features/portfolio/types.ts`) — documented as a reasoned design choice in both `docs/contracts/exposure-fields.md`'s new subsection and `financial-methodology.md`'s new section, not an omission. AC9 does not require a client-visible provenance badge, only a distinct named unclassified sector state, which is what ships.

## Repo hygiene

- `git status --porcelain` shows 11 modified + 5 untracked files, all accounted for: the 11 modified map to the four tickets plus docs; of the 5 untracked, 3 are this story's own new files (`equity_sector_resolution.py`, `test_equity_sector_resolution.py`, the US-37.1 story itself) plus the new epic-37 PRD, and the 5th is the already-flagged US-24.12 tombstone (per the order's own note, not a new finding).
- Story's own `Status:` field (line 7) reads "Backlog", not prematurely "Done" — consistent with all four ticket checkboxes in the Tickets section still unchecked.
- No stray debug artifacts, no leftover scratch files, no accidental commits of cache/build output found.
