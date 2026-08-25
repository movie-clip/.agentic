REPORT 2026-08-24-etf-sector-classification-research/08
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/instruments/etf_sector_resolution.py — new module: resolve_etf_sector, DOMINANCE_THRESHOLD=0.55, taxonomy map, per plan T-39.1.4
  - services/quant-engine/app/instruments/registry.py — ETF branch: sector= lines removed, category unchanged, resolve_etf_sector wired, classification_source= threaded

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_instrument_registry.py -q (see § Verification detail for why the bypass was needed)
  result:    PASS
  detail:    2 failed, 21 passed — the 2 failures are the pre-identified pinned-behavior tests the order named as expected, both for the predicted reason; no other test's outcome changed

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - see § Verification detail for the 2 expected-failing tests, their assertion, and why each is expected (T-39.1.6's rewrite target, not touched here)

risks:
  - market_data.py:529's cache-freshness path string uses a backslash ("etf\sector-weightings") vs fmp.py's forward-slash path — see § Risks, out of my scope (non_goal), diagnostic-only
  - literal order verification command errors before reaching any registry test on a pre-existing, unrelated staleness gate — see § Verification detail
  - `_coerce_weight`'s string-percent defense is still unverified against a live raw JSON shape (carried risk from 06/07, network-free suite, one-off manual check)

## Orchestrator brief
- Implemented T-39.1.4 exactly per 06-technical-plan.md: new etf_sector_resolution.py verbatim, registry.py ETF branch rewired — see § Changes.
- Verified via SKIP_GOLDEN_FRESHNESS_CHECK=1 pytest bypass (literal order command hits an unrelated pre-existing gate first) — see § Verification detail.
- All AC1-AC12 satisfiability confirmed by reading, including AC11's overview.py aggregation seam (no code change needed there) — see § AC review.
- One out-of-scope defect found and flagged, not fixed (market_data.py cache-path typo) — see § Risks.

## § Changes

`etf_sector_resolution.py` is new, created verbatim per 06-technical-plan.md § T-39.1.4 (module docstring, DOMINANCE_THRESHOLD=0.55, `_NORMALIZED_ETF_SECTOR_TAXONOMY_MAP` from `equity_sector_resolution.SECTOR_TAXONOMY_MAP`, `_coerce_weight`, `resolve_etf_sector`).

`registry.py`'s ETF branch: every `sector = ...` line (the line-247 `"Broad Market"` default and all 9 elif-branch assignments) removed; every `category = ...` line kept byte-identical in condition, order and string value. Added, after the category chain: an opt-in `if market_data is not None:` block with a local import of `resolve_etf_sector` (breaks the registry → etf_sector_resolution → instrument_identity → registry cycle, same pattern the equity branch already uses one function below). `classification_source=classification_source` is now passed into the `_instrument(...)` call, which previously omitted it.

`attach_snapshot_metadata` needed no change — confirmed by reading (not assumed): it already threads `market_data` through both `classify_imported_instrument(...)` call sites (lines 352, 356), and its static-registry short-circuit (line 343, `if instrument is not None`) already guarantees a static-registry ETF never reaches `classify_imported_instrument` at all.

## § AC review

AC1 (static registry unaffected, no dynamic lookup) — satisfied: `attach_snapshot_metadata`'s existing static-hit short-circuit runs before `classify_imported_instrument` is ever called.
AC2 (dynamic lookup only when market_data supplied) — satisfied: `if market_data is not None:` gate.
AC3-AC5 (identity gate, ISIN match on correct candidate, no-evidence collapse) — satisfied: `resolve_etf_sector`'s `normalize_isin` comparison, reusing `instrument_identity.normalize_isin` (no second implementation).
AC6/AC7 (55% dominance threshold, never defaults to "Broad Market") — satisfied: `top_share < DOMINANCE_THRESHOLD` returns `(None, "unavailable")`; no code path returns the literal "Broad Market" anymore anywhere in the ETF branch.
AC8 (unmapped bucket never passed through raw) — satisfied: `_NORMALIZED_ETF_SECTOR_TAXONOMY_MAP.get(...)` is None guard.
AC9 (empty/zero-weight response) — satisfied: `if not weights` and `total <= 0` guards.
AC10 (lookup exception never crashes/blocks) — satisfied: both FMP calls wrapped in `try/except Exception`.
AC11 (Unclassified disclosure, weight not dropped) — satisfied with no code change needed: confirmed by reading `analytics/overview.py:58`, `sector = instrument.sector or UNCLASSIFIED_SECTOR_LABEL` already treats any `None` sector as "Unclassified" regardless of which branch produced it.
AC12 (equities, look-through, other statics unaffected) — satisfied: diff touches only the ETF branch's `sector` derivation; equity branch, look-through path, and static-registry merge path are untouched.

## § Verification detail

Ran `python scripts/detect_deadcode.py --strict` from repo root: clean (ruff, vulture, knip all clean).

Ran the literal order command:
```
cd services/quant-engine && python -m pytest app/tests/test_instrument_registry.py -x -q
```
Result: `ERROR at setup of test_common_us_etfs_map_to_canonical_sector[VTI-Broad Market]` — "Dashboard goldens are stale: backend output differs from apps\desktop\src\test\dashboardGoldens.ts." This is a session-level fixture check unrelated to sector resolution; confirmed via `git status` that `dashboardGoldens.ts` is untouched by any lane in this run, so the staleness predates this dispatch (most plausibly from the prior dispatch's `symbols.py`/`fmp.py`/`market_data.py` changes not yet regenerated).

Re-ran with the pytest suite's own documented narrow-run bypass (named in the error message itself):
```
SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_instrument_registry.py -q
```
Result: `2 failed, 21 passed`.

1. `test_enriched_etf_description_round_trips_to_broad_market_sector` — asserted `classified.sector == "Broad Market"` for an unknown ETF with no `market_data` supplied. Now fails: `AssertionError: assert None == 'Broad Market'`. Correct under the new logic: no `market_data` means the dynamic gate is never entered, so `sector` stays `None` (the honest "no lookup attempted" outcome), not the old keyword-fallthrough default. T-39.1.6 rewrites this test's assertion and name.

2. `test_etf_branch_ignores_market_data_and_makes_no_fmp_call` — asserted `market_data.calls == []`. Now fails: `AssertionError: assert ['ZZZ2'] == []`. Correct: `resolve_etf_sector` now calls `market_data.get_company_profile("ZZZ2")` (the fake returns nothing, so the outcome still degrades to `(None, "unavailable")`) — exactly the point of this story, the ETF branch no longer ignores `market_data`. T-39.1.6 rewrites this test's assertions and name.

No other test in the file changed outcome; no collection error or exception outside the two expected assertion failures.

## § Risks

`market_data.py:529`'s `get_etf_sector_weightings` passes `"etf\sector-weightings"` (backslash) to `_will_be_served_from_cache(...)`, while `fmp.py:355`'s actual `_get(...)` call (and the real cache-key formula, `FmpClient.build_cache_identifier`) uses `"etf/sector-weightings"` (forward slash). Landed in the prior dispatch (07-backend.md); `market_data.py` is an explicit non_goal of this order, so not fixed here. This only skews the advisory `was_cached` flag recorded in `last_fetch_meta` — the actual FMP fetch and its cache key are unaffected, since both are driven by `fmp.py`'s own `_get(...)` call, not by this mismatched string. Flagging for whichever lane next touches `market_data.py`.
