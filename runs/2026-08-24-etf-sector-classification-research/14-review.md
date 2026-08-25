REPORT 2026-08-24-etf-sector-classification-research/14
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd /c/projects/investments/portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    905 backend passed (0 failed), 331 frontend passed (37 files), tsc clean, dead-code gate clean (ruff/vulture/knip). Independently re-run by me, not trusted from prior lanes; identical counts to 12-quant-audit.md and 13-integration.md.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Story status field still "Backlog" and all AC/ticket checkboxes unchecked — expected pre-close-out state per this story's own filing note; docs/human update at close-out, not a defect.

risks:
  - T-39.1.7 (unplanned, already evaluated BLOCKING-clear by tech-lead/quant-audit): the committed golden no longer exercises SBIO's positive resolution path, only the fail-closed path — carried forward as context, not re-litigated (out of my scope per this order's non_goals).
  - FrozenMarketData/RecordingMarketData lack get_company_profile/get_etf_sector_weightings, so no golden-level regression test would catch a future FMP field-rename on the positive path — pre-existing test-infra gap, not introduced by this story, already flagged by both prior gates as a non-blocking follow-up.

## Orchestrator brief
- VERDICT: PASS. All 12 ACs traced to specific code + a specific passing test I read myself (assertions, not names). See § AC-by-AC trace.
- Test plan fully delivered: every named bullet in the story's Test plan section maps to an actual test function with matching assertions. See § Test plan cross-reference.
- Trust-state spot check: "Unclassified" is a real, distinct outcome — `resolve_etf_sector` never returns a plausible-looking string on any failure path, only `(None, "unavailable")`; `classification_source` has 4 distinct literals, never collapsed. See § Trust-state spot check.
- SBIO traced end to end: `symbols.py`'s rule has no bare `"SBIO"` candidate → `market_data.get_company_profile("SBIO")` only ever tries `SBIO.L` → `resolve_etf_sector`'s ISIN gate confirmed by a dedicated unit test that fakes the wrong-ISIN scenario directly. See § SBIO trace.
- AC12 regression confirmed independently by me (not trusted from other gates): `git diff` on `equity_sector_resolution.py` and `analytics/risk.py` is empty; `category`'s 10-branch elif chain in `registry.py` read directly, only interleaved `sector =` lines removed.
- Ran `python scripts/run_all_tests.py` myself, full green, matching prior lanes' counts exactly.
- Sections below: § AC-by-AC trace · § Test plan cross-reference · § Trust-state spot check · § SBIO trace

---

## § AC-by-AC trace

- **AC1 SATISFIED** — `registry.py:341-349` (`attach_snapshot_metadata`): a static-registry hit (`instrument is not None`) routes through `_merge_known_instrument_metadata` and `continue`s before `classify_imported_instrument` is ever called. Test: `test_static_registry_etf_never_calls_fmp_even_when_market_data_supplied` (`test_instrument_registry.py:269`) asserts `market_data.calls == []` and `market_data.weightings_calls == []` for SPY even with `market_data` supplied.
- **AC2 SATISFIED** — `registry.py:280` (`if market_data is not None:` gates the ETF branch's dynamic lookup). Tests: `test_etf_branch_with_market_data_attempts_dynamic_lookup_and_falls_through` (calls attempted) and `test_etf_branch_without_market_data_yields_no_classification_not_broad_market` (`test_instrument_registry.py:206`, no `market_data` → `classification_source is None`, dynamic gate never entered).
- **AC3 SATISFIED** — `etf_sector_resolution.py:92-95`: `statement_isin != profile_isin` (or either missing) → `(None, "unavailable")` before the weights fetch. Test: `test_etf_branch_with_market_data_and_isin_match_resolves_fmp_sector` (`test_instrument_registry.py:290`) — resolves via the exchange-suffixed candidate, asserts `sector == "Health Care"`.
- **AC4 SATISFIED** — `symbols.py`'s SBIO `SymbolResolutionRule`: `quote_candidates=("SBIO.L",)`, no bare `"SBIO"`. Test: `test_sbio_bare_ticker_wrong_security_is_rejected_before_weights_fetch` (`test_etf_sector_resolution.py:63`) fakes bare-`"SBIO"` returning the wrong ISIN and asserts `sector is None`, `source == "unavailable"`, `weightings_calls == []`; `test_sbio_quote_candidates_resolve_only_to_the_exchange_suffixed_symbol` (`test_symbols.py:49`) asserts `resolve_symbol_candidates("SBIO", kind="quote") == ["SBIO.L"]`.
- **AC5 SATISFIED** — `etf_sector_resolution.py:92-95`, same guard as AC3, covers both-sides-missing. Test: `test_missing_isin_evidence_either_side_yields_no_classification` (`test_etf_sector_resolution.py:110`), parametrized over statement-missing, profile-missing, both-missing, both-blank-string (`normalize_isin("")` folds to `None`, confirmed at `instrument_identity.py:42-45`).
- **AC6 SATISFIED** — `etf_sector_resolution.py:115-118`: `top_share < DOMINANCE_THRESHOLD` (0.55) → no classification, else accepted. Tests: `test_dominance_threshold_pass_at_exactly_the_threshold` (55.0/100.0 passes, `>=`) and `test_dominance_threshold_pass_just_above_the_threshold` (55.1) both assert `sector == "Health Care"`.
- **AC7 SATISFIED** — same guard, `etf_sector_resolution.py:118` comment: "never Broad Market". Test: `test_dominance_threshold_fail_just_below_the_threshold_never_broad_market` (54.9%) asserts `sector is None` AND `sector != "Broad Market"` explicitly.
- **AC8 SATISFIED** — `etf_sector_resolution.py:123-125`: unmapped `top_sector` → `(None, "unavailable")`, never passed through raw. Test: `test_unmapped_top_sector_bucket_never_passed_through_raw` (`"Cash & Others"` at 99% weight) asserts `sector is None` and `sector != "Cash & Others"`.
- **AC9 SATISFIED** — `etf_sector_resolution.py:102-113`: empty `weights`, or `total <= 0` after coercion, → no classification. Three tests: `test_empty_weights_list_yields_no_classification`, `test_no_coverage_symbol_yields_no_classification` (fake's default `[]`), `test_zero_total_weight_yields_no_classification`.
- **AC10 SATISFIED** — `etf_sector_resolution.py:84-87` and `97-100`, both wrapped in bare `except Exception`. Two tests exercising the two distinct call sites separately: `test_get_company_profile_exception_is_swallowed_not_propagated` (asserts `weightings_calls == []`, i.e. never reached) and `test_get_etf_sector_weightings_exception_is_swallowed_not_propagated` (asserts the profile call did happen first, `weightings_calls == ["XYZ1"]`).
- **AC11 SATISFIED** — `overview.py`'s `UNCLASSIFIED_SECTOR_LABEL` fallback (same mechanism as US-37.1's equity branch). Test: `test_build_portfolio_overview_discloses_unclassified_direct_held_etf_bucket` (`test_analytics.py:442`) asserts `"Unclassified" in sectors`, `"Broad Market" not in sectors`, weight preserved (`0.25` not dropped), and total across all buckets still sums to `1.0`.
- **AC12 SATISFIED** — confirmed independently, not trusted from 13-integration.md: `git diff --stat HEAD -- equity_sector_resolution.py analytics/risk.py` is empty (both untouched). `registry.py`'s `category` 10-branch elif chain read directly (lines 249-270) — only the interleaved `sector = ...` statements from the pre-fix version are gone; every condition and category string is unchanged. Static-registry ETFs (SPY) confirmed unaffected by `test_static_registry_etf_never_calls_fmp_even_when_market_data_supplied`.

## § Test plan cross-reference

Every bullet in the story's Test plan section maps to a real test I read the assertions of, not just the name:

- Static-registry fast path unaffected → `test_static_registry_etf_never_calls_fmp_even_when_market_data_supplied`.
- Identity-match success case → `test_isin_match_and_dominant_sector_resolves_mapped_taxonomy_sector`.
- SBIO-collision-prevented case, dedicated standalone test → `test_sbio_bare_ticker_wrong_security_is_rejected_before_weights_fetch`.
- ISIN-mismatch case → `test_isin_mismatch_yields_no_classification_not_the_fmp_value`.
- No-ISIN-evidence case → `test_missing_isin_evidence_either_side_yields_no_classification` (4 parametrized cases).
- Dominance-threshold pass case → `test_dominance_threshold_pass_at_exactly_the_threshold` + `..._just_above_the_threshold`.
- Dominance-threshold fail case → `test_dominance_threshold_fail_just_below_the_threshold_never_broad_market`.
- Unmapped-sector-bucket case → `test_unmapped_top_sector_bucket_never_passed_through_raw`.
- Empty-weights-response case → `test_empty_weights_list_yields_no_classification`, `test_no_coverage_symbol_yields_no_classification`, `test_zero_total_weight_yields_no_classification`.
- Lookup-exception case → `test_get_company_profile_exception_is_swallowed_not_propagated`, `test_get_etf_sector_weightings_exception_is_swallowed_not_propagated`.
- Aggregation coverage → `test_build_portfolio_overview_discloses_unclassified_direct_held_etf_bucket`.
- Regression (static, equity, look-through unchanged) → confirmed by empty `git diff` on the two untouched modules plus the full 905-test green backend run.
- Frontend: none anticipated — confirmed `SectorPieCard.tsx` has no sector-name special-casing (only a generic `MIN_SLICE_WEIGHT` filter applied uniformly), consistent with the story's own reasoning.
- No-fabrication regression → explicit `sector != "Broad Market"` / `sector != "Cash & Others"` assertions present in the relevant tests, not just implicit `None` checks.
- `run_all_tests.py` green → confirmed by my own independent run, matching 12-quant-audit.md and 13-integration.md's counts exactly.

## § Trust-state spot check

`resolve_etf_sector` (`etf_sector_resolution.py`) has exactly one success return (`mapped_sector, "fmp_etf_sector_weighting_confirmed"`, line 127) and every other path returns `(None, "unavailable")` — no intermediate "plausible guess" state exists in the function's control flow. `classification_source` on `Instrument` carries 4 distinct literals (`"static"`, `"fmp_identity_confirmed"`, `"fmp_etf_sector_weighting_confirmed"`, `"unavailable"`) per `schemas/instruments.py:29` — the new ETF-dynamic-tier literal is not reused from the equity tier, preserving the provenance distinction the story's Context section argues for. `overview.py`'s `sector or UNCLASSIFIED_SECTOR_LABEL` pattern (same as US-37.1) renders `None` sectors as a distinct "Unclassified" bucket, confirmed by `test_build_portfolio_overview_discloses_unclassified_direct_held_etf_bucket` explicitly asserting `"Broad Market" not in sectors`. The new market-data caller (`get_etf_sector_weightings`) has a mock throughout: `FakeMarketData` (`app/tests/fixtures.py`) was extended with `sector_weightings`/`raise_for_weightings`/`get_etf_sector_weightings`/`.weightings_calls`, used across all 17 tests in `test_etf_sector_resolution.py`.

## § SBIO trace

End-to-end chain read directly, not assumed: `registry.py`'s ETF branch calls `resolve_etf_sector(imported, market_data)` (`imported.symbol == "SBIO"`) → `resolve_etf_sector` calls `market_data.get_company_profile("SBIO")` → `market_data.py:503-523`'s `get_company_profile` iterates `resolve_symbol_candidates("SBIO", kind="quote")` → `symbols.py`'s SBIO rule returns exactly `["SBIO.L"]` (no bare `"SBIO"` candidate exists in the table at all, confirmed by `test_sbio_quote_candidates_resolve_only_to_the_exchange_suffixed_symbol`), so production code never even attempts the bare, wrong-security ticker — the collision is prevented at the candidate-list level, and the identity gate (`etf_sector_resolution.py:92-95`) is the second, independent layer of defense, exercised directly by `test_sbio_bare_ticker_wrong_security_is_rejected_before_weights_fetch`'s fake scenario. Both layers hold.
