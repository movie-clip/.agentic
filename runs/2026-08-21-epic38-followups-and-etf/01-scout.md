REPORT 2026-08-21-epic38-followups-and-etf/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only exploration

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - **Finding 1 (cached:True hardcoded bug shape)**: 5 distinct MarketDataService methods carry hardcoded `cached: True` in last_fetch_meta assignments, not reflecting real cache hit/miss status — see § Methods with Hardcoded Cache Flags
  - **Finding 2 (fmp.py cache-key logic)**: T-37.2.2's fix re-derives cache-key formula from fmp.py's internal `_get` method; canonical location identified at fmp.py:186-187 (build_key call within `_get`), re-derivation at market_data.py:481 — see § Cache-Key Logic Location & Coupling
  - **Finding 3 (ETF look-through F-B)**: Explicitly unaddressed in analytics/risk.py; two functions with hardcoded proxy-ticker lists identified at lines 1613–1627 and 1665–1677 — see § ETF Look-Through Sector Inference (F-B), Still Open
  - **Finding 4 (methodology section)**: New section "Sector/Industry Classification — Source and Resolution (US-37.1)" added to financial-methodology.md at line 1257; no separate "flag for human review" entry in quant-research artifact, section shipped as normal story delivery in Epic 37 close-out (2026-08-21) — see § Methodology Section Added, Review Status

risks:
  - Finding 1 (cached:True): 5 methods have hardcoded cached flags; one method has two branches (line 350 vs 371); unclear if count matches original "4 other methods" claim — see § Methods with Hardcoded Cache Flags
  - Finding 2 (cache-key logic): cache_identifier construction is identical between locations but has no test enforcing they stay in sync if fmp.py's _get changes — see § Cache-Key Logic Location & Coupling
  - Finding 4 (methodology section): quant-research identified gap but didn't draft section; no explicit "flag for review" marker beyond normal review gate — see § Methodology Section Added, Review Status

## Orchestrator brief

Four Epic 37 carried findings verified against current source and documentation state:

1. **Finding 1 (cached:True hardcoding)** — Five MarketDataService methods hardcode `cached: True` instead of reflecting real cache hit/miss, per the original run.md finding. One method (`get_historical_prices`) has two branches (FMP vs yfinance); unclear if this was counted as one or two in the "4 other methods" claim.

2. **Finding 2 (cache-key logic coupling)** — T-37.2.2's fix (market_data.py:481) re-derives cache-key formula from fmp.py's internal `_get` (fmp.py:186-187). Formula is identical but has no test enforcing they stay in sync across future changes to either location.

3. **Finding 3 (ETF look-through F-B, unaddressed)** — Two hardcoded proxy-ticker list functions in analytics/risk.py (lines 1613–1627 and 1665–1677) remain unaddressed; explicitly out of scope for Epic 37 per tech-debt registry.

4. **Finding 4 (methodology section shipped)** — New "Sector/Industry Classification" section added to financial-methodology.md at line 1257. Quant-research identified the gap but did not draft the section; it shipped with normal review gate (no separate flag-for-human-review marker).

Details below in § Methods with Hardcoded Cache Flags, § Cache-Key Logic Location & Coupling, § ETF Look-Through Sector Inference (F-B), Still Open, § Methodology Section Added, Review Status.

---

## Methods with Hardcoded Cache Flags

Five distinct MarketDataService methods currently hardcode `cached: True` in their `last_fetch_meta` assignments, rather than tracking actual cache hit/miss:

| Method | Line(s) | Signature (partial) | Current behavior |
|---|---|---|---|
| `get_latest_quotes` | 293 | `get_latest_quotes(symbols: Iterable[str], ...) → dict[str, dict]` | Hardcoded `"cached": True` on successful quote fetch |
| `get_historical_prices` | 350, 371 | `get_historical_prices(symbol: str, from_date: str, to_date: str, ...) → list[dict]` | Hardcoded `"cached": True` for both FMP (line 350) and yfinance fallback (line 371) branches |
| `get_direct_verified_benchmark_history` | 412 | `get_direct_verified_benchmark_history(symbol: str, from_date: str, to_date: str) → list[dict]` | Hardcoded `"cached": True` in the verified benchmark path |
| `get_etf_holdings` | 521 | `get_etf_holdings(symbol: str, ...) → tuple[str \| None, list[dict]]` | Hardcoded `"cached": True` on successful ETF holdings fetch |
| `get_etf_holdings_for_date` | 534 | `get_etf_holdings_for_date(symbol: str, as_of_date: str, ...) → tuple[str \| None, list[dict]]` | Hardcoded `"cached": True` when snapshot is found |

By contrast, `get_company_profile` (line 501) was fixed in T-37.2.2 to track real cache status via the `_profile_will_be_served_from_cache()` helper (line 460–483), and now correctly reports `"cached": was_cached` where `was_cached` is computed from an actual pre-fetch cache check.

## Cache-Key Logic Location & Coupling

**Canonical location in fmp.py (lines 184–187):**
```python
cache_key = None
if self.cache is not None:
    cache_identifier = json.dumps({"path": path, "params": params}, sort_keys=True)
    cache_key = self.cache.build_key(namespace, cache_identifier)
```

This is the single source of truth for FMP's cache-key formula. When `get_profile(symbol)` is called (line 332), it invokes `_get("profile", "profile", {"symbol": symbol}, ...)`, which applies the above formula with `namespace="profile"`, `path="profile"`, `params={"symbol": symbol}`.

**Re-derivation in market_data.py (lines 481–482):**
```python
cache_identifier = json.dumps({"path": "profile", "params": {"symbol": symbol}}, sort_keys=True)
cache_key = cache.build_key("profile", cache_identifier)
```

This duplicates the cache-key construction outside fmp.py, in the `_profile_will_be_served_from_cache()` helper (lines 460–483). The duplication was necessary because fmp.py exposes no hit/miss signal on its return path — only a log line — and T-37.2.2's scope excluded changes to fmp.py itself.

**Structural implication:** The T-37.2.2 risks section (04-backend.md lines 26–28) notes that "the clean fix belongs in fmp.py itself" and flags this as a coupling risk: if `_get`'s cache-key formula changes in the future, this pre-check goes silently stale. No test currently enforces the two implementations stay in sync.

**What a proper fix would look like:** Expose a method in FmpClient or JsonFileCache that reports cache hit/miss status, so MarketDataService can call it after the fetch (or FmpClient can return it in a metadata wrapper) rather than re-deriving the cache-key logic externally.

## ETF Look-Through Sector Inference (F-B), Still Open

**From US-37.1 story (lines 253–258):**
> **F-B: ETF look-through constituent classification**
> (`analytics/risk.py`'s `build_lookthrough_sector_exposure` /
> `_infer_sector_from_sources`, and the duplicated hardcoded proxy-ticker
> list). A separate, already-catalogued tech-debt item
> (`docs/tech-debt-register.md`, `risk.py:1485-1499,1537-1549`); deliberately
> deferred, not this story.

**Current state in analytics/risk.py (confirmed):**

The hardcoded proxy-ticker lists are still present and unchanged:

1. **`_infer_sector_from_sources` (lines 1613–1627)**: Maps hardcoded ticker lists to sector labels.
   ```python
   if any(token in resolved for token in ["XLF"]):
       return "Financials"
   if any(token in resolved for token in ["XLV", "IBB"]):
       return "Health Care"
   if any(token in resolved for token in ["ITA", "PPA"]):
       return "Defense"
   if any(token in resolved for token in ["BIL", "VGSH"]):
       return "Fixed Income"
   if any(token in resolved for token in ["ICOM", "SGLD", "ISLN", "SLV"]):
       return "Commodities"
   if any(token in resolved for token in ["SPY", "VUAA"]):
       return "Broad Market"
   return "Other"
   ```

2. **`_infer_sector_from_resolved_pair` (lines 1665–1677)**: Parallel hardcoded lists for paired ETF overlap sector inference.
   ```python
   if any(token in resolved for token in ["ITA", "PPA"]):
       return "Defense"
   if any(token in resolved for token in ["XLF"]):
       return "Financials"
   # ... similar pattern
   ```

**Tech-debt registry entry (docs/tech-debt-register.md, line 177):**
> `analytics/risk.py:1485-1499,1537-1549` | hardcode / fragile-coupling | med | med | epic-24 | Sector inference from hardcoded proxy-ticker lists (`_infer_sector_from_sources`, `_infer_sector_from_resolved_pair`): e.g. `["XLF"]→Financials`, `["ITA","PPA"]→Defense`, `["BIL","VGSH"]→Fixed Income`. Duplicated across two functions; overlaps the `InstrumentRegistry` sector source of truth.

**Status:** This work item remains unaddressed and is explicitly not part of Epic 37 / US-37.1.

## Methodology Section Added, Review Status

**Location:** `docs/finance/financial-methodology.md`, lines 1257–1404

**Section title:** "Sector/Industry Classification — Source and Resolution (US-37.1)"

**Content scope:**
- Resolution order (static registry → identity-gated FMP lookup → unavailable)
- Sector-taxonomy mapping table (11 GICS sectors, FMP ↔ project string divergences)
- `classification_source` enum semantics (static / fmp_identity_confirmed / unavailable)
- Identity gate rationale (ticker-collision risk, ISIN evidence requirement)
- Opt-in wiring notes (which routes invoke FMP, which don't)
- Unclassified bucket discussion

**Human review status:**

The quant-research artifact (02-quant-research.md § Methodology-doc gap, lines 468–485) identifies the gap and recommends adding this section, but explicitly does NOT draft it:
> "Recommend a new short methodology-doc section ("Sector/Industry Classification — Source and Resolution") covering the resolution order in § Recommended resolution logic once a story implements it; not drafted here per this order's non-goals (no story text)."

No explicit `pack_corrections` flag appears in the quant-research artifact requiring human review of the methodology section before it becomes final. The section was written by the docs-engineer (lane: docs) as part of the normal close-out pass (ticket: implied by story T-37.1.3), went through the review gate (07-review.md verdict: PASS, 2026-08-21), and shipped in Epic 37's close-out on 2026-08-21 (epic-roadmap.md confirms status: "Closed 2026-08-21. All 2 stories Done.").

**Conclusion:** No separate, flagged human review occurred beyond the normal review gate. The section is treated as shipped final, not provisional.
