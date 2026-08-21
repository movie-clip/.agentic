REPORT 2026-08-21-sector-classification-followup/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_equity_sector_resolution.py app/tests/test_market_data.py app/tests/test_instrument_enrichment.py app/tests/test_instrument_registry.py -q
  result:    PASS
  detail:    107 passed in 3.23s — the four files the story's test plan names (T-37.2.4's two new files' worth of coverage plus the two AC5-migrated files). No full-suite run per non_goals; targeted per AC below.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - fixtures.py's DEFAULT_COMPANY_PROFILE constant is unreferenced by executable code today — see § Dead-code note. Not a gate failure, not an AC gap.

## Orchestrator brief

All 5 ACs SATISFIED with file:line evidence; verdict PASS, no follow-up
required. Sections below: **AC-by-AC** (per-criterion evidence), **Test plan
fidelity**, **T-37.2.2 / T-37.2.4 cross-check** and **T-37.2.3 fixture-reuse
cross-check** (the two sanity checks the work order asked for in place of the
skipped tech-lead pass), **Repo hygiene**, **Dead-code note** (the one risks
bullet, expanded). Nothing here needs routing to another lane.

## AC-by-AC

- AC1 (casing/whitespace variant resolves to the mapped sector) — SATISFIED.
  `services/quant-engine/app/instruments/equity_sector_resolution.py:62-64`
  builds `_NORMALIZED_SECTOR_TAXONOMY_MAP` via `key.strip().casefold()`;
  line 87 looks up `profile["sector"].strip().casefold()` against it, mirroring
  the ISIN side's `normalize_isin` discipline the finding asked for. Pinned by
  `test_equity_sector_resolution.py:252-274`, parametrized over all four of
  FINDING 2's reproduced variants (`"TECHNOLOGY"`, `" Technology"`,
  `"Technology "`, `"technology"`) plus a combined case+whitespace case, all
  asserting resolution to `SECTOR_TAXONOMY_MAP["Technology"]` and
  `"fmp_identity_confirmed"`.

- AC2 (normalization narrows unmapped, does not widen mapped) — SATISFIED,
  verified precisely per the work order's flag that this is easy to get
  backwards. `_NORMALIZED_SECTOR_TAXONOMY_MAP` (equity_sector_resolution.py:62-64)
  is derived *only* from `SECTOR_TAXONOMY_MAP`'s existing 11 keys — no new key
  is introduced, so a genuinely novel sector string still produces no match
  after `strip().casefold()`, regardless of its own casing/whitespace. Line
  88-89 falls through to `(None, "unavailable")` exactly as before.
  `test_equity_sector_resolution.py:277-291` pins this directly with
  `"  Some Brand New GICS Bucket  "` (deliberately carrying whitespace of its
  own, to prove the *string* is what's checked, not merely trimming) resolving
  to `unavailable`. Confirmed no key-collision risk in the map: all 11 exact
  keys remain distinct after `strip().casefold()`.

- AC3 (`cached` reflects true cache-hit/miss for `get_company_profile`) —
  SATISFIED. `services/quant-engine/app/services/market_data.py:460-483`
  (`_profile_will_be_served_from_cache`) reconstructs the identical
  namespace/path/params/TTL that `FmpClient._get`'s cache lookup uses for a
  profile call (`app/clients/fmp.py:167,184-188,331-332`: namespace
  `"profile"`, path `"profile"`, `{"symbol": symbol}` params,
  `self.client.profile_ttl_seconds`) and performs a read-only pre-check via
  the cache's own public `build_key`/`get` before the fetch — confirmed
  read-only by reading `JsonFileCache.get` (`app/core/cache.py:68-81`, no
  writes). `get_company_profile` (market_data.py:485-503) uses this to set
  `"cached": was_cached` at line 501, replacing the old hardcoded `True`.
  Pinned end-to-end (real `JsonFileCache`, mocked HTTP only) by
  `test_market_data.py:660-684`.

- AC4 (first call False, second call within TTL True, per-symbol) —
  SATISFIED. Same call sites as AC3. `test_market_data.py:660-684` asserts
  `first_meta["cached"] is False` then `second_meta["cached"] is True` for the
  same symbol within TTL; `test_market_data.py:687-712` asserts a hit on one
  symbol does not leak into a different symbol's status (`aapl_meta["cached"]
  is False` and `msft_meta["cached"] is False` when both are first-seen).

- AC5 (shared FMP-profile fake in `fixtures.py`, all three files import it) —
  SATISFIED. `app/tests/fixtures.py:126-159` (`FakeMarketData`) supports the
  union the story asked for: per-symbol `responses`, a `profile` default for
  unconfigured symbols (documented divergence from the old `_FakeMarketData`'s
  implicit `None` default vs `_SpyMarketData`'s implicit fixed default,
  resolved via an explicit `profile=` kwarg — `DEFAULT_COMPANY_PROFILE` at
  fixtures.py:36 preserves the old `_SpyMarketData` default for a caller that
  wants it), `raise_for`, and `.calls` recording. Confirmed by grep
  (`^class _(Fake|Spy)MarketData`) that no local duplicate class remains
  anywhere under `app/tests/`. All three named files import it:
  `test_instrument_enrichment.py:16`, `test_equity_sector_resolution.py:23`,
  `test_instrument_registry.py:34` — each as `FakeMarketData as
  _<Fake|Spy>MarketData`, preserving each file's original call-site name so no
  test body changed shape, only the import (verified by diff: the enrichment
  file's diff is a pure class-removal + import-add, no call-site changes).

## Test plan fidelity

- `test_equity_sector_resolution.py` — casing-variant regression present
  (5 parametrized cases, AC1) and unmapped-still-falls-through case present
  (AC2), both at lines 252-291. Matches the story's test plan exactly.
- `test_market_data.py` — new `get_company_profile` coverage present: a
  cache-miss-then-hit test and a per-symbol-independence test, both using a
  real `JsonFileCache` against `tmp_path` with only HTTP mocked (stronger than
  the plan's minimum — this doesn't mock away the cache layer the fix
  actually touches). Asserts only the *reported* `cached` value, not FMP call
  sequence, per the plan's explicit instruction.
- `fixtures.py` / migration — `FakeMarketData` added; all three named files
  migrated with no shape change to any existing test's setup (spot-checked
  `test_instrument_enrichment.py`'s `raise_for={"ERR"}` keyword call against
  the new keyword-only `raise_for` param — compatible). Full 107-test run
  across the four touched/added files is green (see verification above).
- Regression/guardrail bullet ("no existing test asserts the old hardcoded
  `cached: True` for `profile`") — re-confirmed true: no such assertion exists
  anywhere in the pre-fix files' diff or surviving code.

## T-37.2.2 / T-37.2.4 cross-check (requested in the work order)

Traced `_profile_will_be_served_from_cache`'s cache-key construction against
`FmpClient._get`'s own construction line-by-line (namespace, path, params
dict, TTL source) — they match exactly, so the pre-check answers the same
question `_get` will ask a moment later. `test_market_data.py`'s two new
tests exercise this through the real cache (not a mock of the cache layer),
so the test is verifying the fix's actual behaviour, not a mocked stand-in
for it. No mismatch found.

## T-37.2.3 fixture-reuse cross-check (requested in the work order)

Grepped for any surviving local `_FakeMarketData` / `_SpyMarketData` class
definition anywhere under `app/tests/` — none found. All three named files
(`test_instrument_enrichment.py`, `test_equity_sector_resolution.py`,
`test_instrument_registry.py`) import `FakeMarketData` from
`app.tests.fixtures` and use it under their original local alias. No file
kept a local duplicate alongside the import.

## Repo hygiene

- Story `Status:` field reads `Backlog` (US-37.2-sector-classification-followups.md:6)
  — not prematurely `Done`. AC and ticket checkboxes are unticked, consistent
  with Backlog.
- No stray files: `git status --porcelain` shows only the files the four
  tickets would be expected to touch, plus US-37.1's own still-uncommitted
  files (pre-existing, out of this story's authorship, not introduced by
  this gate's scope).
- No golden-artifact drift: no `dashboardGoldens.ts` or similar generated
  file appears in the diff.
- Scope discipline confirmed: `market_data.py`'s other four `"cached": True`
  call sites (`get_latest_quotes`, `get_historical_prices` x2,
  `get_direct_verified_benchmark_history`, `get_etf_holdings`,
  `get_etf_holdings_for_date`) are untouched, matching the story's explicit
  Out-of-scope list. `fmp.py`'s diff (profile TTL wiring) is attributed to
  US-37.1 decision #4 in its own comment, not this story's T-37.2.2, and
  T-37.2.2's own docstring explicitly disclaims touching `fmp.py`.
- No methodology-doc or contract-doc edit attributable to US-37.2 (grepped
  `docs/finance/financial-methodology.md`'s diff for "37.2" / cache-flag /
  casing/whitespace language — none found), consistent with the story's
  explicit "no docs ticket is cut here" scoping.

## Dead-code note

`fixtures.py`'s new `DEFAULT_COMPANY_PROFILE` constant (line 36) is
referenced only in docstrings/comments, never by executable code in any of
the three consuming test files (confirmed by grep). `vulture app
vulture_allowlist.py --min-confidence 60` flags it; the actual gate runs at
`--min-confidence 80` (per `scripts/detect_deadcode.py`), where it is silent
(confirmed by running both commands directly). Not a gate failure. Not an AC
gap — AC5 only requires the shared fake support the union of what the three
files need, and none of the three currently exercises the "no-arg-and-called"
case the constant exists for (documented explicitly in
`test_instrument_registry.py:36-43`). Worth a human eyeball only if the
dead-code confidence threshold is ever tightened.
