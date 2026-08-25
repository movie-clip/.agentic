REPORT 2026-08-21-epic38-followups-and-etf/14
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py (run fresh by this lane, from portfolio root)
  result:    PASS
  detail:    backend 878 passed; frontend 331 tests / 37 files passed; tsc clean; dead-code gate (ruff+vulture+knip) clean; git status shows no dashboardGoldens.ts drift and no stray files, only the expected story-doc + code diffs

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - exposure-fields.md's "Sector labels" row cites a UI symbol that no longer exists — pre-existing drift, not from this story, see § Non-blocking observations
  - a pre-existing, untouched test assertion at test_analytics.py:4748 is stale but not a coverage gap, see § Non-blocking observations
  - both story files still read Status: Backlog — expected pre-close-out, see § Non-blocking observations

## Orchestrator brief

- verdict: PASS. All 9 ACs of US-38.1 and all 8 ACs of US-38.2 traced individually to landed code (file:line) and a specific passing test — verified by direct reads, not by trusting 12-quant-audit.md or 13-integration.md's own claims (both independently reproduced and cross-checked against this lane's own code/test reads, and agree).
- Full suite re-run fresh by this lane: 878 backend + 331 frontend passed, dead-code gate clean, tsc clean, no golden/stray-file drift.
- Trust-state spot check: "Unclassified" is a real, distinct `str` value (schema: `LookThroughSectorExposure.sector: str`, no nullable/Optional shortcut), never the literal "Other", always itemized in `build_lookthrough_sector_exposure`'s return regardless of `MIN_SECTOR_WEIGHT` (AC8, code read at risk.py:1095, numeric test at test_analytics.py:4997), and never fabricated via a live market-data call in either `build_lookthrough_sector_exposure` (no `market_data` param at all — structurally unreachable) or `_build_shared_sector_overlap` (`market_data` param present but unreferenced in body, confirmed by direct read + a spy-based no-network-call test).
- Test-plan fidelity: every bullet in both stories' test plans is backed by a named, existing test function — cross-referenced by name and by reading test bodies, not just titles (see § Test-plan cross-reference below).
- No frontend ticket in either story is correct: `lookthrough_sector_exposure` (the field this story adds "Unclassified" to) is not currently rendered by any UI component at all (confirmed by exhaustive grep across `apps/desktop/src`) — the only sector-facing UI component, `SectorPieCard.tsx`, reads a different field (`sector_allocation`) with its own separate, already-shipped US-37.1 Unclassified precedent.
- Three non-blocking observations, all pre-existing and out of this story's scope, detailed in § Non-blocking observations.
- sections below: AC-by-AC trace (US-38.1) · AC-by-AC trace (US-38.2) · Test-plan cross-reference · Non-blocking observations

---

## AC-by-AC trace — US-38.1

- AC1 (registry-hit unaffected) — SATISFIED. `build_lookthrough_sector_exposure` (risk.py:1051-1096) resolves `constituent.symbol` via `InstrumentRegistry.get_instrument` unchanged from before. Test: `test_build_lookthrough_sector_exposure_registry_hit_resolves_via_static_registry` (test_analytics.py:4898).
- AC2 (fund-category override unaffected) — SATISFIED. Per-source loop (risk.py:1065-1071) reads `FUND_CATEGORY_OVERRIDE_CATEGORIES` unchanged in logic shape. Test: `test_build_lookthrough_sector_exposure_fund_category_override_still_classifies_by_fund_sector` (test_analytics.py:4921) + `..._uses_thematic_etf_source_sector` (4852).
- AC3 (unresolved → distinct "Unclassified", never "Other" or a guess) — SATISFIED. risk.py:1058 defaults to `UNCLASSIFIED_SECTOR_LABEL` (imported from `overview.py`, not redefined). Test: `test_build_lookthrough_sector_exposure_unresolved_constituent_lands_in_unclassified` (test_analytics.py:4943) asserts `set(by_sector) == {UNCLASSIFIED_SECTOR_LABEL}` on a real return value, not just the test name.
- AC4 (same treatment on `_build_shared_sector_overlap`, including the former ungated-profile path) — SATISFIED. risk.py:1672-1679: the ungated `get_company_profile` call is gone, replaced with `UNCLASSIFIED_SECTOR_LABEL`. Test: `test_build_shared_sector_overlap_unresolved_symbol_lands_unclassified_without_network_call` (test_analytics.py:5164).
- AC5 (no live market-data call to reach Unclassified) — SATISFIED. `build_lookthrough_sector_exposure`'s signature takes only `list[LookThroughConstituent]` — structurally cannot reach a client. `_build_shared_sector_overlap`'s `market_data` param is present but unreferenced in the body (confirmed by direct read of risk.py:1648-1686). Test: `_NoNetworkCallMarketData` spy (test_analytics.py:5119) raises `AssertionError` if either forbidden call is made; exercised by 3 tests at 5130/5148/5164.
- AC6 (reconciliation across sector buckets, no drop, no pro-rating) — SATISFIED. `total_market_value` computed once up front (risk.py:1053), suppression filter (risk.py:1095) trims only the itemized list, never the denominator. Test: `test_build_lookthrough_sector_exposure_partial_resolution_reconciles_total_and_weight` (test_analytics.py:4966) reproduces the research brief's exact worked-example numbers and asserts `sum(market_value) == 10000.0` / `sum(weight) == 1.0`.
- AC7 (Risk-tab factor tilts don't silently zero a real exposure) — SATISFIED. `build_factor_exposures` (risk.py:1099-1119) reads `lookthrough_sector_exposure` unchanged in shape; companion registry curation (AC9) is what keeps previously-guessed tilts (e.g. Defense) non-zero post-fix. Test: `test_build_factor_exposures_defense_tilt_reflects_companion_curated_ita_sector` (test_analytics.py:5074) asserts `defense_tilt.exposure == 0.2`, not zero.
- AC8 ("Unclassified" exempt from `MIN_SECTOR_WEIGHT`, every other bucket still filtered) — SATISFIED. risk.py:1095: `if sector == UNCLASSIFIED_SECTOR_LABEL or (... >= MIN_SECTOR_WEIGHT)`. Test: `test_build_lookthrough_sector_exposure_unclassified_exempt_from_suppression_threshold` (test_analytics.py:4997) proves asymmetry directly — a smaller *resolved* bucket (Health Care, 0.04%) is suppressed while a smaller Unclassified bucket (0.03%) is itemized, in the same fixture.
- AC9 (8 companion tickers resolve their curated sector, not Unclassified) — SATISFIED. All 8 (`XLF`/`XLV`/`IBB`/`ITA`/`PPA`/`BIL`/`VGSH`/`DBC`) present in `INSTRUMENT_DEFINITIONS` (registry.py:137-144) with real sector/category values. Test: parametrized `test_build_lookthrough_sector_exposure_companion_curated_tickers_resolve_their_sector` (test_analytics.py:5039-5052), 8 cases, all pass.

## AC-by-AC trace — US-38.2

- AC1 (`get_latest_quotes` real hit/miss) — SATISFIED. market_data.py:279-281 pre-checks via `_will_be_served_from_cache` before `get_quote_short`. Test: `test_get_latest_quotes_reports_true_miss_then_true_hit_within_ttl` (test_market_data.py:755), real `tmp_path`-backed cache, only HTTP stubbed.
- AC2 (`get_historical_prices`, both branches) — SATISFIED. FMP branch (market_data.py:337-342) and yfinance-fallback branch (364) each pre-check independently. Tests: `..._fmp_branch_..." (776) and `..._yfinance_branch_..." (798), the latter exercising the real `YFinanceClient` with only `yfinance.Ticker` stubbed.
- AC3 (`get_direct_verified_benchmark_history`) — SATISFIED, including the two-underlying-call AND semantics (market_data.py:407-414 ANDs both endpoint pre-checks). Tests: hit/miss pair (849) plus `..._requires_both_underlying_paths_cached` (873), which pre-warms only one of the two endpoints and asserts the reported flag is still `False`.
- AC4 (`get_etf_holdings`) — SATISFIED. market_data.py:528-530 pre-checks before `get_etf_holders`. Test: `test_get_etf_holdings_reports_true_miss_then_true_hit_within_ttl` (906).
- AC5 (`get_etf_holdings_for_date`, live/cached branch only) — SATISFIED. Non-history branch (market_data.py:560) delegates unchanged to `get_etf_holdings`; the holdings-history-snapshot branch (557) correctly keeps its hardcoded `"cached": True`, out of scope per the AC's own text. Test: `..._inherits_cache_flag_via_delegation` (932) spies on `get_etf_holdings` to prove delegation, not merely matching output.
- AC6 (miss-then-hit distinguished per call) — SATISFIED across all 5 methods' individual tests (same pattern: first call `False`, second `True`, within TTL).
- AC7 (one formula, in `fmp.py`, `market_data.py` derives from it) — SATISFIED. `FmpClient.build_cache_identifier` (fmp.py:167-175) is the sole formula; `is_cached` (177-185), `_get` (204-205), `get_etf_holders` (394) all call it; `market_data.py._will_be_served_from_cache` (482-501) delegates to `FmpClient.is_cached`, no re-derivation. Tests: `test_get_and_is_cached_derive_the_cache_key_from_the_same_formula` (test_fmp_client.py:261) spies on the bound method and asserts identical call args across both call sites; `test_will_be_served_from_cache_delegates_to_fmp_client_is_cached` (test_market_data.py:957) proves the passthrough structurally.
- AC8 (`get_company_profile` behaviour unchanged after AC7 refactor) — SATISFIED. Regression test `test_get_company_profile_reports_true_miss_then_true_hit_within_ttl` (test_market_data.py:669) still asserts real per-call hit/miss, unchanged in shape from US-37.2's own version, now sourced through the consolidated formula.

## Test-plan cross-reference

US-38.1 test plan (11 bullets) — every bullet has a named test: static-registry fast path (4898), fund-category override (4921/4852), unresolved→Unclassified (4943), partial-resolution reconciliation (4966), no-network-call regression (5119 spy + 5130/5148/5164), `_build_shared_sector_overlap` coverage (5130/5148/5164/5184), deletion-doesn't-regress-resolved (implicit in 4898/4921 passing against real registry data + full-statement regression at test_exposure_engine.py:125-160), suppression-exemption asymmetry (4997), companion-registry coverage (5039-5052, 8 parametrized cases). Frontend: none shipped, correctly — confirmed no current UI consumer of `lookthrough_sector_exposure` exists to need one (see § Non-blocking observations).

US-38.2 test plan (4 bullets + regression) — miss-then-hit pairs for all 5 methods (755/776/798/849/906/932), historical-prices' two branches each separately covered (776 + 798), `get_company_profile` regression after consolidation (669), formula-agreement-by-construction test (test_fmp_client.py:261) plus the passthrough proof (test_market_data.py:957). "No test asserts the old hardcoded True" — confirmed: grepped both test files, no remaining literal `"cached": True` assertion tied to a method this story fixed, other than the deliberately-untouched `get_etf_holdings_for_date` history-snapshot branch (AC5's own carve-out) and the delegation test's mocked-`True` fixture value (932), which is asserting the delegation passthrough, not a hardcoded regression.

## Non-blocking observations

**exposure-fields.md's stale UI symbol citation.** The "Sector labels" row (docs/contracts/exposure-fields.md, ~line 207) cites `topLookthroughSectors` in `ExposurePanel.tsx`. Grepped the whole frontend tree — no such symbol exists anywhere, and `lookthrough_sector_exposure` (the field this story adds "Unclassified" to) is not rendered by any current UI component. The only sector-facing card, `SectorPieCard.tsx`, reads `sector_allocation`/`sector_position_breakdown` instead — a different field with its own separate, already-shipped US-37.1 "Unclassified" precedent. Confirmed via `git diff docs/contracts/exposure-fields.md` that T-38.1.3 only touched the Notes column on this row, not the source-code citation — so this drift predates this story. Not a finding against US-38.1: no AC requires frontend rendering, and the story's own "no frontend ticket" call is correct, though for a more literal reason than it stated ("data-driven off whatever bucket labels the engine returns" implied an existing renderer; there currently is none to update). Flagging for docs-engineer close-out to correct or remove the stale citation.

**Stale permissive test assertion.** `test_analytics.py:4748`, inside a large pre-existing smoke test untouched by this story's diff, asserts `sector_exposure[0].sector in {"Technology", "Broad Market", "Other"}`. This would not itself catch a regression that reintroduced literal "Other" fabrication. However: "Other" is confirmed unreachable anywhere in `app/analytics/` (grep-verified, zero hits outside a comment), and this story's own dedicated no-fabrication regressions (`test_analytics.py:434`, `test_analytics.py:473`, `test_exposure_engine.py:160`) all assert `"Other" not in sectors` directly against real statement/fixture data. Cosmetic test-quality nit on an untouched line, not a coverage gap this story introduced or was required to fix.

**Story status fields.** Both `US-38.1-etf-lookthrough-sector-classification.md` and `US-38.2-market-data-cache-diagnostic-accuracy.md` still read `**Status:** Backlog`, while comparable shipped stories (US-37.1, US-37.2) read `**Status:** Done`. Per this run's own `run.md` (`next:` field), flipping story status is part of the docs close-out step dispatched after this review passes — not yet run. Not a hygiene defect of this gate; noted so close-out doesn't miss it.
