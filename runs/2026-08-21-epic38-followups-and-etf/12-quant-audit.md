REPORT 2026-08-21-epic38-followups-and-etf/12
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_analytics.py -k "lookthrough or shared_sector or unclassified or proxy_sector or companion" -v
  result:    PASS
  detail:    24 passed, 190 deselected. Also spot-ran app/tests/test_market_data.py + test_fmp_client.py (62 passed, includes the 9 real-cache miss/hit tests for US-38.2) and my own independent re-derivation script (see § Independent recomputation) — did not re-run the full suite, per non_goals, after these spot-checks confirmed 11-test.md's PASS is trustworthy.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - _build_shared_sector_overlap's market_data param is now dead code — engineering-cleanliness note for tech-lead INTEGRATION, not a math/trust issue, see § Non-blocking notes
  - IBB's curated category label is debatable but numerically inert — see § Non-blocking notes

## Orchestrator brief

- verdict: PASS. No CRITICAL or MATERIAL findings on US-38.1 (aggregation rule, suppression exemption, companion curation, proxy_sector symmetry) or US-38.2 (cache-diagnostic side-effect check).
- independently re-derived build_lookthrough_sector_exposure and _build_shared_sector_overlap against hand-computed expected values (own fixtures, not the shipped test file) — see § Independent recomputation. All matched, including the exact worked-example numbers from 03-quant-research.md (Technology $6,000/60%, Unclassified $4,000/40%).
- verified AC5 (no live market-data call) by direct code read of both functions' bodies, not by trusting the story or tests — confirmed structurally: build_lookthrough_sector_exposure takes no market_data param at all; _build_shared_sector_overlap's market_data param is present but genuinely unreferenced in its body.
- verified MIN_SECTOR_WEIGHT/Unclassified suppression exemption numerically (tiny resolved sector suppressed, tiny Unclassified bucket itemized, denominator unaffected either way) — § Suppression exemption, numeric proof.
- verified the two fund-category-override predicates (per-source loop vs _fund_category_proxy_sector) are textually identical, both reading the one shared FUND_CATEGORY_OVERRIDE_CATEGORIES constant — no asymmetry, no duplication.
- companion registry entries (XLF/XLV/IBB/ITA/PPA/BIL/VGSH/DBC) checked against general real-world fund knowledge, independent of the story's own stated values — all 8 factually reasonable; anchor and caveats in § Companion registry sanity check.
- doc-vs-code check: financial-methodology.md's "ETF look-through constituent classification (US-38.1)" section matches the landed code exactly — no drift found.
- US-38.2: confirmed the cache pre-check (is_cached/build_cache_identifier) is read-only and runs strictly before the real fetch call at every call site — the actual data returned to analytics (quotes/prices/holdings/profile) is unaffected; last_fetch_meta stays backend-internal, never serialized. Spot-ran 9 real (non-fully-mocked, tmp_path-backed cache) miss-then-hit tests, including the AND-semantics test for the two-underlying-call benchmark method — all pass.
- sections below, in order: Independent recomputation · Suppression exemption, numeric proof · AC5 no-network-call verification · Fund-category-override symmetry · Companion registry sanity check · Doc-vs-code check · US-38.2 side-effect check · Non-blocking notes · Anchor summary

---

## Independent recomputation

Anchor: hand-computed / degenerate-case fixtures, constructed independently of `app/tests/test_analytics.py` (built before I read that file), calling the real `build_lookthrough_sector_exposure` and `_build_shared_sector_overlap` directly with `LookThroughConstituent`/`LookThroughSource` objects I wrote myself.

**Worked example reproduction** (from 03-quant-research.md § Worked example): ETF `XYZ`, $10,000 total, `AAPL` 60% (curated Technology) / `OBSCURECO` 40% (unresolved):

```
Technology  6000.0  0.6
Unclassified  4000.0  0.4
total: 10000.0 (expected 10000) — weight sum: 1.0 (expected 1.0)
```

Matches the research brief's hand-derived numbers exactly.

**Fund-category override on an unresolved constituent** — a constituent sourced entirely via `BIL` (curated Fixed Income / Bond ETF), the constituent itself not in the registry:

```
Fixed Income  1000.0  1.0
```

Correctly resolves via the override, not Unclassified — confirms the per-source override applies even when the constituent's own `default_sector` would be Unclassified.

**Empty portfolio**: `build_lookthrough_sector_exposure([])` → `[]`. No division-by-zero, no fabricated row.

## Suppression exemption, numeric proof

Constructed a $1,000,000 total with three constituents: `AAPL` ($999,950, Technology, dominant), `TINYRESOLVED` ($30 via `XLF`→Financials, 0.003% of total — below the 0.05% `MIN_SECTOR_WEIGHT` floor), `TINYUNRESOLVED` ($20, no resolution anywhere, 0.002% of total — also below the floor):

```
Technology    999950.0  1.0
Unclassified      20.0  0.0
```

`TINYRESOLVED`'s $30 Financials bucket is correctly suppressed from the itemized list (below floor, real sector) but **is still counted in the weight denominator** — `total_market_value` is computed once, up front, from every constituent's `effective_market_value`, before the suppression filter runs; the filter only trims the *returned list*, never the denominator. `TINYUNRESOLVED`'s Unclassified bucket, despite being even smaller, is **not** suppressed — proves AC8's exemption is live and correctly scoped to the `sector == UNCLASSIFIED_SECTOR_LABEL` branch of the filter condition (risk.py:1095), not a blanket "always show small buckets" change.

Directly confirmed by code read that `_build_shared_sector_overlap`'s return (risk.py:1683-1686) has **no filter condition at all** — unconditional list comprehension, matching the design decision that only `build_lookthrough_sector_exposure` carries the exemption logic because only it has a suppression filter to exempt from in the first place.

## AC5 no-network-call verification

Constructed an `ExplodingMarketData`/`_NoNetworkCallMarketData`-style spy (raises `AssertionError` on `get_company_profile`/`get_etf_holdings`) and called `_build_shared_sector_overlap` through every resolution branch (registry hit, fund-category proxy hit, fully unresolved → Unclassified) — no exception raised in any case, confirming no live call occurs anywhere in the unresolved path. This matches the shipped test file's own `_NoNetworkCallMarketData` (test_analytics.py:5119), which I did not read until after writing my own equivalent.

`build_lookthrough_sector_exposure`'s signature (risk.py:1051) takes only `lookthrough_constituents: list[LookThroughConstituent]` — structurally cannot reach a market-data client at all, confirmed by direct signature read, not inference.

## Fund-category-override symmetry

Per-source loop (risk.py:1065-1071): `source_instrument.asset_class == "etf" and source_instrument.category in FUND_CATEGORY_OVERRIDE_CATEGORIES and source_instrument.sector`.
`_fund_category_proxy_sector` (risk.py:1643): `instrument.asset_class == "etf" and instrument.category in FUND_CATEGORY_OVERRIDE_CATEGORIES and instrument.sector`.

Textually identical predicate, both reading the one module-level `FUND_CATEGORY_OVERRIDE_CATEGORIES` constant (risk.py:1039-1048) — no duplicated list, no asymmetry. Confirmed the precedence test numerically: `_fund_category_proxy_sector(registry, "XLF", "XLV")` → `"Financials"` (left wins when both qualify); `("SPY", "XLV")` → `"Health Care"` (SPY is curated "Broad Market", outside the override set, so it falls through to XLV); `("SPY", "VUAA")` → `None` (neither qualifies). All three match the technical plan's stated intent exactly.

## Companion registry sanity check

Anchor: general/public knowledge of these funds' actual composition and sponsor classification, checked independently of the story/technical-plan's stated values (not a live data pull — these are well-known, long-listed index products).

| Ticker | Landed sector | Landed category | Assessment |
|---|---|---|---|
| XLF | Financials | Sector ETF | Correct — Financial Select Sector SPDR tracks the S&P 500 Financials GICS sector |
| XLV | Health Care | Sector ETF | Correct — Health Care Select Sector SPDR tracks the S&P 500 Health Care GICS sector |
| IBB | Health Care | Sector ETF | Sector correct (biotech is a GICS Health Care sub-industry); category is a defensible-but-debatable choice — see risks bullet, zero numeric effect either way |
| ITA | Defense | Thematic ETF | Correct — tracks the Aerospace & Defense group, a project-specific (non-GICS) "Defense" bucket already used elsewhere (Defense Tilt factor) |
| PPA | Defense | Thematic ETF | Correct — same aerospace/defense basket, different sponsor (Invesco/SPADE index) |
| BIL | Fixed Income | Bond ETF | Correct — SPDR 1-3 Month T-Bill ETF |
| VGSH | Fixed Income | Bond ETF | Correct — Vanguard Short-Term Treasury ETF |
| DBC | Commodities | Commodity ETF | Correct — Invesco DB Commodity Index Tracking Fund |

No factually wrong entry. `classification_source` correctly left unset (defaults `None`, stamped `"static"` at merge — verified against `_merge_known_instrument_metadata`, registry.py:222), matching the 5 pre-existing curated overrides' own pattern.

## Doc-vs-code check

Read `docs/finance/financial-methodology.md`'s "ETF look-through constituent classification (US-38.1)" section (lines 1463-1519) against the landed code, in the doc-is-spec direction:

- "no dynamic FMP lookup is attempted... at any point" — confirmed structurally (§ AC5 above).
- "only two tiers... static registry, or Unclassified" — confirmed; no third tier exists in either function.
- Fund-category-override description and its `_fund_category_proxy_sector` mention match the landed function exactly, including "checking each side's resolved ETF in turn."
- MIN_SECTOR_WEIGHT exemption text ("exempt... every other sector bucket remains subject to it... `_build_shared_sector_overlap` has none") matches code exactly — confirmed both halves independently (§ Suppression exemption above).

No drift found between doc and code in either direction.

## US-38.2 side-effect check

Read `market_data.py`'s five changed call sites (`get_latest_quotes`, `get_historical_prices` FMP + yfinance branches, `get_direct_verified_benchmark_history`, `get_etf_holdings`). In every case `was_cached = self._will_be_served_from_cache(...)` (or the yfinance twin) is computed **before**, and independently of, the real fetch call (`self.client.get_quote_short`, `.get_historical_price_light`, `.get_historical_price_dividend_adjusted`, `.get_etf_holders`) — the pre-check never gates, short-circuits, or substitutes for the real call. `last_fetch_meta[...]["cached"]` is the only thing that changes; the returned rows/quotes/holdings that feed `risk.py`'s look-through analytics are computed identically to before. `last_fetch_meta` remains backend-internal (confirmed no route serializes it — matches 06-technical-plan.md's own contract note).

Spot-ran 9 real (non-fully-mocked) tests using an on-disk tmp_path cache — genuine miss-then-hit assertions per method, plus the AND-semantics test for `get_direct_verified_benchmark_history`'s two-underlying-call case: all 9 pass, none inspected by the shipped test file's own mocking (these bypass the `FmpClient`-wholesale-mock pattern used by the 8 corrected regression tests, so they are a stronger anchor than "the mock returns what I told it to").

## Non-blocking notes

**Dead parameter.** `_build_shared_sector_overlap`'s `market_data: HoldingsMarketData` parameter (risk.py:1654) is unreferenced in the function body — its only use was the deleted ungated `get_company_profile` call. 09-backend.md already flagged this as a deliberate minimal-diff choice. `detect_deadcode --strict` passed anyway (unused function parameters on a function with live call sites aren't the class of thing ruff/vulture flag the way unused locals are). Not a math or trust-class issue — an engineering-cleanliness item for tech-lead INTEGRATION to decide whether to trim, not mine to block on.

**IBB's category label.** IBB is curated `category="Sector ETF"` (matching XLF/XLV), rather than `"Thematic ETF"` (matching ITA/PPA). IBB's underlying index (NASDAQ Biotechnology) is arguably a narrower thematic basket, closer in spirit to ITA/PPA's own categorization than to XLF/XLV's broad-GICS-sector tracking. This has zero numeric consequence: both `"Sector ETF"` and `"Thematic ETF"` are members of `FUND_CATEGORY_OVERRIDE_CATEGORIES` and are treated identically by both call sites (verified by reading the predicate at risk.py:1065-1071 and risk.py:1643 — both test only category-membership, never which specific category). Noted for completeness, not as a finding — no published number depends on which of the two labels IBB carries.

## Anchor summary

- Aggregation/suppression/override logic (US-38.1 math): `anchor: external (hand-computed/degenerate-case fixtures)` — independently constructed inputs and expected outputs, not read from the shipped test file until after my own recomputation matched.
- Companion registry sector/category values: `anchor: external (general/public fund-classification knowledge)` — independent of the story/plan's stated values, not a live re-fetch from the removed FMP path (correctly inapplicable here since no FMP call exists in this surface any more).
- financial-methodology.md vs code: `anchor: methodology-doc` — this is a consistency check in the doc-is-spec direction, not independent evidence; reported as such, not as "verified."
- US-38.2 diagnostic accuracy: `anchor: external (real on-disk cache, non-mocked miss/hit behavior)` — stronger than a mock-consistency check, genuinely exercises the on-disk cache read/write path.
