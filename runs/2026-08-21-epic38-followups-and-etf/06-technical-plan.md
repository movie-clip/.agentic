REPORT 2026-08-21-epic38-followups-and-etf/06
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    design pass; read-only, no code executed beyond reading source

contract_notes:
  - US-38.1 and US-38.2 both change zero schema/type shapes — see § Contract. No downstream TS/contract-doc field rename or nullability change is needed; only docs/contracts/exposure-fields.md's prose (not its field rows) and financial-methodology.md need the T-38.1.3 edits already drafted in 03-quant-research.md

pack_corrections:
  - none

handoff:
  - full contract, reuse map, per-ticket code-level instructions and decisions are in the sections below — dispatch backend/test/docs work orders directly from § Reuse and § Decisions, not from the story files alone
  - found and correcting a factual gap in both stories' own regression notes: 8 pre-existing tests in test_market_data.py assert hardcoded `cached: True` against a fully-mocked FmpClient and WILL break under T-38.2.1 — see § Decisions #5, named file:line list
  - `_build_shared_sector_overlap`'s fund-category proxy_sector needs a new implementation (the deleted `_infer_sector_from_resolved_pair` is not a 1:1 swap) — see § Decisions #2, exact code given

risks:
  - the two stories' own test plans/regression notes did not anticipate the 8-test breakage in § Decisions #5 — flagging so backend-engineer and test-engineer treat it as expected, not a build regression
  - sizing risk-6 in US-38.2 (`get_direct_verified_benchmark_history` issues 2 underlying FMP calls per fetch) required a joint-AND pre-check decision not spelled out in the story; a different implementer without this plan could reasonably build a single-call check and under-report cache misses — see § Decisions #4

## Orchestrator brief

- decisions taken: proxy_sector reimplementation for `_build_shared_sector_overlap` (§Decisions#2) · MIN_SECTOR_WEIGHT exemption is a one-line filter-condition change, Unclassified-only (§Decisions#3) · companion registry curation sources its 8 sector values from the fallback functions' own existing mapping, not a fresh lookup, `classification_source` left unset like its 5 precedents (§Decisions#1) · FmpClient exposes `build_cache_identifier`+`is_cached`, YFinanceClient gets its own independent twin (§Decisions#4) · get_etf_holdings_for_date needs no separate fix, inherits via delegation (§Decisions#4)
- BLOCKING-adjacent finding: 8 existing tests will break under T-38.2.1 unless updated in the same pass — named list in §Decisions#5, must reach both backend-engineer and test-engineer
- lane sequence (7 tickets, no schema change either story): T-38.2.2+T-38.2.1 (backend, effectively one PR) → T-38.2.3 (test) → T-38.1.1+T-38.1.2 (backend, no order dependency) → T-38.1.3 (docs, can run anytime after) → T-38.1.4 (test) — see §Lane sequence
- sections below, in order: Contract · Reuse · Lane sequence · Decisions (1-5) · Risks (detail)

---

## Contract

**US-38.1.** No schema, type, or response-shape change. `LookThroughSectorExposure.sector` (`schemas/reconciliation.py:169-172`) stays `str`; `EtfOverlapPair.sector_overlap` stays `list[LookThroughSectorExposure]`. The only change is which *string values* `sector` can now take: `"Unclassified"` (the existing `UNCLASSIFIED_SECTOR_LABEL` from `app/analytics/overview.py:13`, imported into `risk.py`, not a new constant) replaces the guessed labels and the literal `"Other"` at three fallback sites. `docs/contracts/exposure-fields.md:207-209` needs its prose updated to name the Unclassified possibility (mirroring line 216's treatment) — this is a T-38.1.3 docs edit, not a contract-row/field change.

**US-38.2.** No schema, type, or response-shape change. `last_fetch_meta` (`dict[str, dict[str, object]]`) is backend-internal, never serialized to a route response, and carries no contract-doc row today — confirmed by the story's own out-of-scope note. `cached`'s *meaning* becomes accurate; its type (`bool`) and key (`"cached"`) are unchanged.

## Reuse

- **US-38.1**: `UNCLASSIFIED_SECTOR_LABEL` (`app/analytics/overview.py:13`) — import into `risk.py`, do not redefine. The existing per-source fund-category override category whitelist at `risk.py:1045-1053` — extract to a module-level constant and reuse it in `_build_shared_sector_overlap`'s new proxy_sector logic (§Decisions#2) instead of leaving a second, hand-copied list. The existing `_instrument(...)` helper and curated-entry shape (`registry.py:114-148`, specifically the SLV/ICOM/SGLD/ISLN/IEF pattern) for T-38.1.2 — same helper call, same "no `classification_source`, no `isin` for US-listed" shape.
- **US-38.2**: the existing `get_company_profile`/`_profile_will_be_served_from_cache` pattern (`market_data.py:460-503`) is the template every other method's fix mirrors — pre-check called *before* the fetch, inside the same candidate-resolution loop iteration, per candidate. `fmp.py`'s `_get` (`clients/fmp.py:167-220`) is the one place the cache-key-identifier formula must be extracted from, not reinvented.

## Lane sequence

No hard dependency between the two stories (disjoint files: `risk.py`/`registry.py` vs `market_data.py`/`fmp.py`/`yfinance_client.py`). Confirming the delivery brief's B-then-A recommendation — now that both stories are fully designed here, the original reason ("A's quant-routing question may take longer") no longer applies, but B-first still reads better: it is the tighter, more mechanical change, and keeping its diff free of A's registry edits keeps the 8-test-breakage fix (§Decisions#5) legible on its own.

1. **T-38.2.2 + T-38.2.1** (backend-engineer, one dispatch — see §Decisions#4 on why these are practically one PR despite the story's "no ordering dependency" framing: T-38.2.1's five call sites are written in terms of the shared method T-38.2.2 introduces).
2. **T-38.2.3** (test-engineer). Depends on 1. Must also fix the 8 pre-existing tests named in §Decisions#5 — not itself an AC, but required for `run_all_tests.py` to stay green.
3. **T-38.1.1 + T-38.1.2** (backend-engineer). No order dependency between them (disjoint: risk.py fallback logic vs. registry.py static dict), may be one dispatch or two.
4. **T-38.1.3** (docs-engineer). Can run any time after step 3 lands — the methodology-doc text is already drafted verbatim in `03-quant-research.md` § Draft methodology-doc section, ready to apply.
5. **T-38.1.4** (test-engineer). Depends on step 3 (both T-38.1.1 and T-38.1.2 — the companion-curation regression test needs the curated entries to exist).

## Decisions

### 1. T-38.1.2 — companion registry curation: source and provenance

**Source the 8 sector/category values from the fallback functions' own existing mapping, not a fresh FMP/registry lookup.** `_infer_sector_from_sources` (risk.py:1613-1627) and `_infer_sector_from_resolved_pair` (risk.py:1665-1677) already encode real-world-accurate classifications for these well-known, single-sector index ETFs. A fresh FMP lookup is explicitly the wrong source per this story's own "Out of scope" section (FMP's `sector` field for an ETF ticker returns the fund sponsor's own classification, not a thematic category — Epic 37 verified SPY and GRID both return `"Financial Services"`). Use:

```python
"XLF":  _instrument("etf-xlf",  "XLF",  "Financial Select Sector SPDR Fund",       "etf", "Financials",   "Sector ETF",   "USD"),
"XLV":  _instrument("etf-xlv",  "XLV",  "Health Care Select Sector SPDR Fund",     "etf", "Health Care",  "Sector ETF",   "USD"),
"IBB":  _instrument("etf-ibb",  "IBB",  "iShares Biotechnology ETF",               "etf", "Health Care",  "Sector ETF",   "USD"),
"ITA":  _instrument("etf-ita",  "ITA",  "iShares U.S. Aerospace & Defense ETF",    "etf", "Defense",      "Thematic ETF", "USD"),
"PPA":  _instrument("etf-ppa",  "PPA",  "Invesco Aerospace & Defense ETF",         "etf", "Defense",      "Thematic ETF", "USD"),
"BIL":  _instrument("etf-bil",  "BIL",  "SPDR Bloomberg 1-3 Month T-Bill ETF",     "etf", "Fixed Income", "Bond ETF",     "USD"),
"VGSH": _instrument("etf-vgsh", "VGSH", "Vanguard Short-Term Treasury ETF",        "etf", "Fixed Income", "Bond ETF",     "USD"),
"DBC":  _instrument("etf-dbc",  "DBC",  "Invesco DB Commodity Index Tracking Fund","etf", "Commodities",  "Commodity ETF","USD"),
```

Category values are drawn from the existing whitelist set (risk.py:1045-1053) so the per-source override actually matches them; sectors mirror what the deleted functions already returned for these exact tickers (XLF→Financials, XLV/IBB→Health Care, ITA/PPA→Defense, BIL/VGSH→Fixed Income, DBC→Commodities — all confirmed against both `_infer_sector_from_sources` and `_infer_sector_from_resolved_pair`'s token tables). No `isin=` (all 8 are US-listed, matching SPY/GLD/SLV/IEF/TLT/AGG/BND/QQQ's precedent — only the UCITS/European lines carry an ISIN). **No `classification_source=` argument** — leave it at the `_instrument` helper's default (`None`), exactly like the 5 existing curated overrides (SLV/ICOM/SGLD/ISLN/IEF, none of which pass it either); it gets stamped `"static"` at merge time by `_merge_known_instrument_metadata` (registry.py:196-213), same tier as every other static-dict hit.

### 2. `_build_shared_sector_overlap`'s proxy_sector — not a 1:1 swap

Deleting `_infer_sector_from_resolved_pair` removes `_build_shared_sector_overlap`'s only source of `proxy_sector` (risk.py:1642). The research brief's pseudocode says proxy_sector should mean "a curated fund-category match" going forward, but does not give the replacement code — this is a real implementation gap, not just a deletion. Replace:

```python
proxy_sector = _infer_sector_from_resolved_pair(left_resolved, right_resolved)
```

with a lookup against the same curated-override mechanism `build_lookthrough_sector_exposure`'s per-source loop already uses, checking `left_resolved` then `right_resolved` (left takes precedence on a tie, matching the deleted function's own no-precedence "either token matches" behavior collapsed to a deterministic order):

```python
FUND_CATEGORY_OVERRIDE_CATEGORIES = {
    "Thematic UCITS ETF", "Thematic ETF", "Sector UCITS ETF", "Sector ETF",
    "Bond UCITS ETF", "Bond ETF", "Commodity UCITS ETF", "Commodity ETF",
}  # module-level constant, risk.py — reused by build_lookthrough_sector_exposure's
   # existing inline check (risk.py:1045-1053) so both functions read one list

def _fund_category_proxy_sector(registry: InstrumentRegistry, left_resolved: str, right_resolved: str) -> str | None:
    for resolved_symbol in (left_resolved, right_resolved):
        instrument = registry.get_instrument(resolved_symbol)
        if instrument and instrument.asset_class == "etf" and instrument.category in FUND_CATEGORY_OVERRIDE_CATEGORIES and instrument.sector:
            return instrument.sector
    return None
```

Also replace `build_lookthrough_sector_exposure`'s own inline `{"Thematic UCITS ETF", ...}` set literal (risk.py:1045-1053) with a reference to the same `FUND_CATEGORY_OVERRIDE_CATEGORIES` constant — leaving both as separately-typed literals is exactly the "duplicated computation" class of defect the tech-lead integration review greps for (architecture.md §4).

### 3. MIN_SECTOR_WEIGHT / Unclassified suppression exemption — exact filter change

Only `build_lookthrough_sector_exposure`'s return comprehension (risk.py:1068-1076) has a suppression filter; `_build_shared_sector_overlap` has none (its return at risk.py:1659-1662 is unconditional) — the AC8 exemption applies to exactly one place. Change:

```python
if total_market_value and market_value / total_market_value >= MIN_SECTOR_WEIGHT
```

to:

```python
if sector == UNCLASSIFIED_SECTOR_LABEL or (total_market_value and market_value / total_market_value >= MIN_SECTOR_WEIGHT)
```

Every other bucket keeps the existing threshold unchanged, per AC8's own wording.

### 4. US-38.2 — the shared cache-key-check method (fmp.py) and its call sites

Add two methods to `FmpClient` (`clients/fmp.py`), and have `_get` (line 184-187) and `get_etf_holders` (line 376, which does **not** go through `_get` and has its own second, independent copy of the identifier-building line — a fact neither story surfaced) both call the first one instead of building the identifier inline:

```python
def build_cache_identifier(self, path: str, params: dict[str, Any]) -> str:
    return json.dumps({"path": path, "params": params}, sort_keys=True)

def is_cached(self, namespace: str, path: str, params: dict[str, Any], ttl_seconds: int) -> bool:
    """Read-only pre-check: would a call with this exact (namespace, path,
    params, ttl) be served from cache right now, with no live request."""
    if self.cache is None:
        return False
    cache_key = self.cache.build_key(namespace, self.build_cache_identifier(path, params))
    return self.cache.get(cache_key, max_age_seconds=ttl_seconds) is not None
```

`_get` line 186 becomes `cache_identifier = self.build_cache_identifier(path, params)`; `get_etf_holders` line 376 becomes `cache_identifier = self.build_cache_identifier(f"api/v3/etf-holder/{symbol}", {})`. Both keep byte-identical identifier *values* (verify against the existing pinned test `test_get_etf_holders_cache_identity_is_unchanged_by_url_refactor`, test_market_data.py:571-596, which asserts the literal string — must stay green unchanged).

`market_data.py`: rename `_profile_will_be_served_from_cache` to a generalized `_will_be_served_from_cache(self, namespace: str, path: str, params: dict, ttl_seconds: int) -> bool`, body `return self.client.is_cached(namespace, path, params, ttl_seconds)`. Call it, in the same before-the-fetch position `get_company_profile` already uses, at each site:

| Method | namespace | path | params | ttl |
|---|---|---|---|---|
| `get_latest_quotes` | `"quote"` | `"quote-short"` | `{"symbol": candidate}` | `self.client.quote_ttl_seconds` |
| `get_historical_prices` (FMP branch) | `"history"` if not `candidate.endswith("USD")` else `"fx"` | `"historical-price-eod/light"` | `{"symbol": candidate, "from": canonical_from, "to": canonical_to}` | `self.client.history_ttl_seconds` |
| `get_direct_verified_benchmark_history` | `"history"` | **both** `"historical-price-eod/full"` and `"historical-price-eod/dividend-adjusted"` | `{"symbol": requested_symbol, "from": canonical_from, "to": canonical_to}` | `self.client.history_ttl_seconds` |
| `get_etf_holdings` | `"holdings"` | `f"api/v3/etf-holder/{candidate}"` | `{}` | `self.client.history_ttl_seconds` |

**`get_direct_verified_benchmark_history` issues two underlying `_get` calls per fetch (full + dividend-adjusted, same params, different path) — report `cached=True` only if BOTH pre-checks hit**, since a live request happens if either misses:
```python
was_cached = (
    self._will_be_served_from_cache("history", "historical-price-eod/full", params, self.client.history_ttl_seconds)
    and self._will_be_served_from_cache("history", "historical-price-eod/dividend-adjusted", params, self.client.history_ttl_seconds)
)
```

**`get_historical_prices`'s yfinance-fallback branch is a different client with a different cache/formula — do not route it through `FmpClient`.** `YFinanceClient.get_historical_price_light` (`clients/yfinance_client.py:41-63`) has its own third, independent inline `json.dumps({"path": "yfinance/history", ...})` construction. AC7 scopes the single-formula requirement to `fmp.py` only; give `YFinanceClient` its own narrow twin, extracted from its own inline construction (not shared with `FmpClient`, since it is a genuinely different provider/cache line, but internally single-sourced the same way):
```python
def is_cached(self, symbol: str, from_date: str, to_date: str) -> bool:
    if self.cache is None:
        return False
    cache_identifier = json.dumps({"path": "yfinance/history", "params": {"symbol": symbol, "from": from_date, "to": to_date}}, sort_keys=True)
    cache_key = self.cache.build_key(_CACHE_NAMESPACE, cache_identifier)
    return self.cache.get(cache_key, max_age_seconds=self.history_ttl_seconds) is not None
```
and have `get_historical_price_light` reuse this same identifier-building line rather than keeping its own separate copy. Call `self._yfinance().is_cached(candidate, canonical_from, canonical_to)` from `market_data.py` before `self._yfinance().get_historical_price_light(...)`.

**`get_etf_holdings_for_date` needs no separate fix.** Its non-history-cache branch (line 537) delegates to `self.get_etf_holdings(...)`, which already writes `last_fetch_meta` under the right key once T-38.2.1 lands — AC5 is satisfied by inheritance, not a second implementation. Its holdings-history-snapshot branch (lines 532-535) is explicitly out of scope (AC5).

`market_data.py`'s `import json` becomes unused once its own inline `json.dumps` is removed — remove the import too, or the dead-code gate (`ruff`) will flag it.

### 5. Existing tests that will break under T-38.2.1 — correcting both stories' regression notes

Both US-38.2's and US-37.2's "no existing test asserts the hardcoded True" claims are **wrong for two of the five methods.** Verified directly against `test_market_data.py`: **8 existing tests** mock `FmpClient` wholesale (`mocker.patch("app.services.market_data.FmpClient")`) and assert a hardcoded `"cached": True` with no mock configured for the new pre-check call — once T-38.2.1 makes these methods call `self._will_be_served_from_cache(...)` → `self.client.is_cached(...)`, that call resolves to a `MagicMock` return (truthy, not `True`) on these tests' mocked client, and every one of these assertions fails:

- `test_get_historical_prices_uses_etf_holdings_proxy_fallback` — line 79 (assert at 93)
- `test_get_historical_prices_uses_gld_proxy_fallback_for_sgld` — line 108 (assert at 118)
- `test_get_historical_prices_uses_dbc_proxy_fallback_for_icom` — line 121 (assert at 131)
- `test_get_historical_prices_uses_slv_proxy_fallback_for_isln` — line 134 (assert at 144)
- `test_get_historical_prices_uses_proxy_for_continuous_future_roots` — line 147 (assert at 157)
- `test_get_direct_spy_benchmark_history_records_direct_vendor_scope_metadata` — line 233 (assert at 252, exact-equality dict)
- `test_get_direct_verified_benchmark_history_records_direct_vendor_scope_metadata_for_qqq` — line 263 (assert at 278, exact-equality dict)
- `test_verified_benchmark_overlapping_windows_share_canonical_call` — line 409 (assert at 435)

No equivalent pre-existing test exists for `get_latest_quotes` or `get_etf_holdings` (confirmed by grep — clean). **Fix (T-38.2.3, test-engineer's file):** add `instance.is_cached.return_value = True` immediately after `instance = client_mock.return_value` in each of the 8 tests above — one line each, preserves each test's existing intent (they were never testing cache behaviour, just pinning `last_fetch_meta`'s other fields) without restructuring them. Flagging this in `handoff` as well since it is required for `run_all_tests.py` to stay green and neither story's own test plan names it.

## Risks (detail)

`get_direct_verified_benchmark_history`'s two-call joint-AND semantics (§Decisions#4) is a genuine judgment call the story leaves open — an implementer building only a single-call pre-check would under-report cache misses (report a hit when only the first of two calls actually hit), which is a real but narrow diagnostic-accuracy gap the AND'd version closes. Recording it here so it is a deliberate design choice, not an accidental one, consistent with this project's "flag deliberate choices explicitly" convention (see US-38.1's own suppression-threshold precedent).
