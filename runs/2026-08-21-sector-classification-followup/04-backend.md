REPORT 2026-08-21-sector-classification-followup/04
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/services/market_data.py — added `_profile_will_be_served_from_cache`, a read-only pre-fetch cache check reused inside `get_company_profile`.
  - services/quant-engine/app/services/market_data.py — `last_fetch_meta[symbol]["cached"]` for a profile call now carries the real hit/miss result instead of hardcoded `True`.

verification:
  command:   cd services/quant-engine && python -c "from app.services.market_data import MarketDataService; print('import ok')"
  result:    PASS
  detail:    printed "import ok" — module imports cleanly with the new helper and json import in place.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-37.2.4: point `MarketDataService.client.cache` at a tmp-dir `JsonFileCache` to test hit/miss without network — see § Cache pre-check mechanics.
  - T-37.2.4: first `get_company_profile` call for a symbol should report `cached: False`; a second call within TTL should report `cached: True`.
  - `_profile_will_be_served_from_cache(symbol)` is the new private helper backing the fix — see § Cache pre-check mechanics for how it works.

risks:
  - `app/clients/fmp.py` exposes no hit/miss signal anywhere (`_get()` only logs it) — see § Cache pre-check mechanics for the workaround and its limits.
  - The workaround re-derives `_get`'s internal cache-key formula from outside `fmp.py`; if that formula changes, this check silently drifts wrong — see § Cache pre-check mechanics.
  - Clean fix is `fmp.py` itself reporting hit/miss, but this ticket's scope excludes that file — flagging for a human call on a small follow-up ticket.
  - Edge case: a reported miss followed by a failed live fetch that falls back to stale cache is still reported `cached: False` though the data was cache-served — see § Cache pre-check mechanics.
  - Per story's Out of scope: the same hardcoded-`True` shape still exists in `get_quote`, `get_historical_prices`, `get_etf_holdings`, `get_etf_holdings_for_date` — untouched, as directed.

## Orchestrator brief

T-37.2.2 done: `get_company_profile`'s `cached` flag now reports real hit/miss
instead of hardcoded `True`. `fmp.py` exposes no hit/miss signal and is out of
this ticket's scope, so the fix pre-checks the cache directly from
`market_data.py` — mechanism, its coupling risk, and one stale-fallback edge
case are in § Cache pre-check mechanics. Verification passed. No contract or
doc changes. One open question in `risks` for a human/tech-lead: whether the
hit/miss signal belongs in `fmp.py` itself as a proper follow-up.

## Cache pre-check mechanics

`FmpClient.get_profile` -> `_get` has no return-side hit/miss signal — only a
log line (`logger.info("FMP cache hit/miss ...")`). Nothing on `FmpClient` or
`JsonFileCache` reports it to a caller either. The order's scope is
`services/market_data.py` only, so adding a signal to `fmp.py` was not an
option here.

The fix instead adds `MarketDataService._profile_will_be_served_from_cache
(symbol)`, called immediately before `self.client.get_profile(candidate)`
inside `get_company_profile`'s loop. It reuses the cache wrapper's own public
`build_key`/`get` (`self.client.cache.build_key("profile", identifier)` then
`.get(cache_key, max_age_seconds=self.client.profile_ttl_seconds)`), with
`identifier` built from the exact same `{"path": "profile", "params":
{"symbol": symbol}}` shape `_get` uses internally for a profile call. A
non-`None` result means the next fetch will be a cache hit; `None` means it
will require a live request. This must run *before* the fetch — after the
fetch, a fresh cache write would make every call look like a hit.

Two limits, both stemming from not being able to touch `fmp.py`:

1. **Coupling.** This duplicates `_get`'s cache-key construction (namespace
   `"profile"`, path `"profile"`, params `{"symbol": symbol}`) outside the
   file that owns it. If `_get`'s key formula changes, this check goes stale
   silently — no test failure would announce it since both sides currently
   agree, but nothing enforces they keep agreeing.
2. **Stale-fallback edge case.** `_get` has an exception path that serves
   stale cache data when a live request fails
   (`services/quant-engine/app/clients/fmp.py:252-267`). If the pre-check
   reports a miss (TTL expired) and the subsequent live fetch then throws,
   `_get` can still answer from that same stale entry — so the response was,
   in fact, cache-served, but `get_company_profile` will have already
   recorded `cached: False`. Not fixable from `market_data.py` alone: `_get`
   would need to report which branch it took.

Neither limit affects the primary hit/miss path the story's AC3/AC4 and test
plan describe (fresh miss then hit within TTL, no fetch failure), which is
exact.
