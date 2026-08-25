REPORT 2026-08-21-epic38-followups-and-etf/13
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py (re-run twice by this lane, from portfolio root)
  result:    PASS
  detail:    backend 878 passed; frontend 331 tests / 37 files passed; tsc clean; dead-code gate (ruff+vulture+knip) clean; dashboardGoldens.ts untouched (git status confirmed) — matches 11-test.md's own numbers exactly, independently reproduced, not merely trusted

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - _build_shared_sector_overlap's market_data param (risk.py:1654) is confirmed dead in the body but left in the signature — decided SHOULD_FIX, not worth a CR round, see § Non-blocking notes decided
  - IBB's "Sector ETF" category label (registry.py) was my own design-pass call, landed verbatim — re-affirmed correct on review, see § Non-blocking notes decided

## Orchestrator brief

- verdict: PASS. All 7 tickets landed exactly per 06-technical-plan.md — no
  scope drift, no undeclared deviation, no skipped decision.
- decided both non-blocking quant-audit notes: leave the dead `market_data`
  param on `_build_shared_sector_overlap` (SHOULD_FIX, no CR round); IBB's
  "Sector ETF" label affirmed correct, no change.
- contract confirmed unchanged (no schema/route/type edits needed by either
  story) — verified against the diff itself, not the plan's claim alone.
- no duplicated logic found — one definition each for
  FUND_CATEGORY_OVERRIDE_CATEGORIES and the two clients' cache-key formulas.
- `run_all_tests.py` re-run twice by this lane, green both times, numbers
  match every prior lane's own report.
- sections below: Ticket-by-ticket conformance · Duplication check ·
  Non-blocking notes decided · Test quality · Docs consistency spot-check

---

## Ticket-by-ticket conformance

**T-38.2.1 + T-38.2.2 (fmp.py, yfinance_client.py, market_data.py).**
`FmpClient.build_cache_identifier` / `is_cached` added exactly as specified
(§ Decisions #4); `_get` and `get_etf_holders` both now call
`build_cache_identifier` — verified the pinned identity test
(`test_get_etf_holders_cache_identity_is_unchanged_by_url_refactor`) stayed
green. `YFinanceClient` got its own independent
`_build_cache_identifier`/`is_cached` twin, not routed through `FmpClient`,
matching the plan's explicit "different provider, different cache line"
call. `market_data.py`'s five call sites (`get_latest_quotes`,
`get_historical_prices` FMP + yfinance branches,
`get_direct_verified_benchmark_history`, `get_etf_holdings`) all pre-check
before the fetch, using the exact namespace/path/params/ttl table in
§ Decisions #4 — confirmed field-by-field against the corresponding `fmp.py`
methods' own `_get(...)` call arguments (`get_quote_short`,
`get_historical_price_light`, `get_historical_price_dividend_adjusted`'s two
internal `_get` calls, `get_etf_holders`). `get_direct_verified_benchmark_history`
correctly AND's both underlying pre-checks. `get_etf_holdings_for_date`'s
non-history branch delegates to `get_etf_holdings` unchanged (confirmed by
reading the method — its holdings-history-snapshot branch still hardcodes
`"cached": True`, correctly out of scope per AC5). `import json` removed
from `market_data.py`.

**T-38.2.3 (tests).** All 8 pre-existing tests fixed with the prescribed
one-line `instance.is_cached.return_value = True`, no restructuring beyond
that. New coverage uses real `JsonFileCache` + real client with only HTTP
transport stubbed (mirrors `get_company_profile`'s own AC3/AC4 shape) — a
materially stronger anchor than the fully-mocked pattern the 8 fixed tests
use, correctly reserved for genuine miss/hit assertions rather than the
"pin last_fetch_meta's other fields" tests that don't care about cache
behavior. The AND-semantics test
(`test_get_direct_verified_benchmark_history_requires_both_underlying_paths_cached`)
directly proves the two-call joint requirement, not just today's fixture
output. AC7's structural test spies on `build_cache_identifier` itself,
proving formula identity by construction.

**T-38.1.1 (risk.py).** `_infer_sector_from_sources` and
`_infer_sector_from_resolved_pair` both deleted; `UNCLASSIFIED_SECTOR_LABEL`
imported from `overview.py`, not redefined. `_fund_category_proxy_sector`
replaces `proxy_sector`'s only source exactly per § Decisions #2, reading
the shared `FUND_CATEGORY_OVERRIDE_CATEGORIES` constant — both call sites
(the per-source loop and the new helper) now read one list, confirmed
textually identical predicates. The `MIN_SECTOR_WEIGHT` exemption is the
exact one-line filter-condition change specified in § Decisions #3, applied
only to `build_lookthrough_sector_exposure` (the only function with a
suppression filter) — `_build_shared_sector_overlap`'s return stayed
unconditional, matching the plan's note that the exemption applies to
exactly one place. The ungated `get_company_profile` fallback in
`_build_shared_sector_overlap` is gone, replaced with
`UNCLASSIFIED_SECTOR_LABEL` — AC4/AC5 satisfied, no live/cached call
possible on that path (confirmed by direct read, `market_data` param now
unreferenced in the body — see § Non-blocking notes).

**T-38.1.2 (registry.py).** All 8 companion tickers (XLF, XLV, IBB, ITA,
PPA, BIL, VGSH, DBC) added to `INSTRUMENT_DEFINITIONS` with the exact
sector/category values § Decisions #1 specified, no `classification_source`,
no `isin` — matches the SLV/ICOM/SGLD/ISLN/IEF precedent. No duplicate
registry keys (grep-verified against all 97 entries).

**T-38.1.3 (docs).** `financial-methodology.md`'s new "ETF look-through
constituent classification (US-38.1)" subsection matches the landed code
(spot-checked the "two tiers, not three" claim, the suppression-exemption
scoping claim, and the `_fund_category_proxy_sector` description against
the actual functions). `exposure-fields.md`'s look-through-sector rows now
document the "Unclassified" bucket, mirroring the existing
current-state-concentration rows' treatment as instructed.
`tech-debt-register.md:177`'s citation corrected and marked RESOLVED with
the narrower FMP-reliability sub-finding correctly left open. This lane's
own `status: PARTIAL` (flagging that writing methodology-doc prose directly
conflicts with `capabilities/docs.md`'s flag-for-human convention) is the
correct behavior per PROTOCOL.md § 3 — order explicit, guardrail not
violated, conflict named, not silently followed as DONE. No further action
needed from this gate; the human reviewing this run's close-out should treat
the methodology section as provisional per that lane's own risk note, but
the text itself checks out against the code.

**T-38.1.4 (tests).** 20 new tests in `test_analytics.py` cover AC1-AC9
individually and in combination (registry-hit, fund-category-override,
unresolved-to-Unclassified, partial-resolution reconciliation,
suppression-exemption asymmetry, all 8 companion tickers parametrized, a
Defense-Tilt factor-exposure regression proving AC7's "no silent zeroing"
claim end-to-end, `_build_shared_sector_overlap`'s three resolution paths
via a no-network-call spy, and `_fund_category_proxy_sector`'s left-wins
precedence). Plus a regression assertion in `test_exposure_engine.py`
proving no literal `"Other"` reaches the full-statement exposure test.
Matches the story's test plan section-for-section.

## Duplication check

```
FUND_CATEGORY_OVERRIDE_CATEGORIES  → risk.py:1039 (definition), read at
  risk.py:1068 (per-source loop) and risk.py:1643 (_fund_category_proxy_sector)
  — one definition, two readers, textually identical predicates.
build_cache_identifier             → fmp.py:167 (definition), called at
  fmp.py:184 (is_cached), fmp.py:205 (_get), fmp.py:394 (get_etf_holders)
  — one definition, three callers, all in FmpClient.
_build_cache_identifier (yfinance) → yfinance_client.py:42 (definition),
  called at yfinance_client.py:63 (is_cached), yfinance_client.py:72
  (get_historical_price_light) — one definition, two callers, deliberately
  independent of FmpClient's per AC7's fmp.py-only scope.
```

No second, hand-copied instance of either constant/formula anywhere in
`services/quant-engine/app/` (grep across the full tree, non-test files).

## Non-blocking notes decided

**Dead `market_data` parameter, `_build_shared_sector_overlap` (risk.py:1654).**
Confirmed dead inside the function body (its only use was the deleted
`get_company_profile` call). Decision: **leave it, SHOULD_FIX, not worth a
change-request round.** Reasoning — the single call site
(`build_etf_overlap_pairs`, risk.py:1531) already has a live `market_data`
value in scope for a legitimate reason (`get_etf_holdings` at line 1492), so
trimming the parameter is a genuinely trivial two-line diff (signature +
call site) with zero behavioral effect and zero risk, but also zero value:
`detect_deadcode --strict` does not flag unused parameters on functions with
live call sites (confirmed — the gate passed clean with the param still
present), so there is no mechanical pressure to fix it, and an isolated
one-parameter trim is not worth spending a change-request round or blocking
this slice over. Noting it here is sufficient; a future touch of this
function (the next time `_build_shared_sector_overlap` is edited for an
unrelated reason) is the natural point to drop it.

**IBB's category label, "Sector ETF" vs "Thematic ETF" (registry.py).**
This was my own design-pass call (06-technical-plan.md § Decisions #1),
landed verbatim by backend-engineer. Re-examined on review: IBB tracks the
ICE Biotechnology Index, a broad, GICS-anchored Health Care sub-industry
basket — closer in kind to XLV's Health-Care-sector tracking than to
ITA/PPA's Aerospace & Defense grouping, which spans multiple GICS sectors
and is a project-specific, non-GICS "Defense" bucket by construction (per
the existing Defense Tilt factor). **Decision: affirm "Sector ETF" as
correct, no change.** It is also, independently, numerically inert either
way — both `"Sector ETF"` and `"Thematic ETF"` are members of
`FUND_CATEGORY_OVERRIDE_CATEGORIES` and are read only for set-membership by
both call sites (confirmed by re-reading both predicates), never for the
specific category string, so no published number depends on which label
IBB carries.

## Test quality

The new US-38.2 cache tests are the stronger anchor of the two stories'
suites: real `JsonFileCache` + real client, only HTTP/yfinance-`Ticker`
stubbed, so they would fail if the requirement changed (unlike a
fully-mocked test that returns whatever it's told). The US-38.1 tests assert
via `{item.sector: item for item in sector_exposure}` dict lookups rather
than exact-equality on the full ordered list — resilient to the response
list growing a new bucket, which is exactly the brittleness pattern
`capabilities/architecture.md` names as something this repo has been bitten
by before. No instance of either brittleness pattern (exact-equality on a
growable structure, or an assertion pinning an implicit default the test
never set) found in the new test code.

## Docs consistency spot-check

Read `docs/finance/financial-methodology.md`'s new subsection,
`docs/contracts/exposure-fields.md`'s edited rows, and
`docs/tech-debt-register.md:177`'s corrected row directly against the
landed `risk.py`/`registry.py` diff (not merely against 10-docs.md's own
claims). All three are accurate: the "two tiers, not three" claim, the
suppression-exemption's function-scoping claim (`build_lookthrough_sector_exposure`
only, not `_build_shared_sector_overlap`), and the tech-debt row's RESOLVED
framing (with the narrower FMP-reliability sub-finding correctly left open,
not conflated) all match the code exactly. No drift in either direction.
