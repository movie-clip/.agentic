REPORT 2026-08-24-etf-sector-classification-research/12
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_etf_sector_resolution.py -v
  result:    PASS
  detail:    17 passed, 0 failed. Also spot-ran app/tests/test_instrument_registry.py (32 passed), app/tests/test_symbols.py (6 passed, included in the 32), app/tests/test_analytics.py -k unclassified (6 passed) — all green, matching 11-backend.md's summary count.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Golden fixture now shows SBIO "Unclassified" via FrozenMarketData's fail-closed path (correct, guardrail 4) — no longer exercises the resolved-sector path end-to-end. See § T-39.1.7 assessment.
  - I did not independently re-run the yfinance second-provider corroboration myself (no live network in this audit); relying on 03-quant-research.md's account for that leg only.
  - 11-backend.md says the post-fix golden's "Health Care" bucket is "AAPL's actual weight" — it is actually CRSP+EDIT. Narrative error in that report only, not in the committed data. See § T-39.1.7 assessment.

## Orchestrator brief
- VERDICT: PASS. No CRITICAL or MATERIAL findings — the identity gate, dominance-threshold, taxonomy reuse, and classification_source semantics all match `financial-methodology.md` § "Direct-held ETF branch classification (US-39.1)" exactly, and the doc's landed pseudocode is byte-identical to what shipped.
- Anchor used, per pack convention: `anchor: external` — real, ground-truth data (broker statement ISIN in `docs/IB2026.csv`, raw on-disk FMP cache JSON in `data/raw/fmp-cache/`), independently cross-referenced by me, then the real production `resolve_etf_sector` run end-to-end (no mocks) against that cache — see § Independent recomputation. `pytest` run is `anchor: methodology-doc` (consistency), reported as that, not as independent proof.
- `category` derivation in `registry.py`'s ETF branch confirmed byte-identical pre/post via `git diff HEAD` — only `sector =` lines were removed from each keyword branch; conditions/values untouched.
- SBIO collision fix confirmed two ways: `symbols.py`'s rule has no bare `"SBIO"` candidate (code read), and a live cache-backed run of `resolve_etf_sector` resolved only via `SBIO.L`, matching the statement ISIN.
- `SECTOR_TAXONOMY_MAP` reuse confirmed genuine (single definition in `equity_sector_resolution.py`, imported not copied) — see § Duplication check.
- T-39.1.7's golden-determinism fix judged methodologically sound — see § T-39.1.7 assessment for the explicit reasoning the work order asked for.
- Sections below: § Independent recomputation (anchor: external) · § Doc-vs-code cross-check · § Duplication check · § Edge cases exercised · § T-39.1.7 assessment

## Independent recomputation (anchor: external)

The story's central claim is that bare `"SBIO"` and `"SBIO.L"` resolve to two
different securities on FMP, and that the identity gate must (and does) admit
only the latter. Rather than trust the research brief's narrative, I derived
the expected answer myself from primary sources already on disk, before
looking at what the code produces:

- `docs/IB2026.csv`'s `Financial Instrument Information` row for SBIO:
  `ISIN IE00BQ70R696` (the statement's own broker-truth ISIN).
- `data/raw/fmp-cache/profile-ec71...json` (cached bare-`SBIO` FMP profile):
  `isin: "US00162Q5936"`, `"ALPS Medical Breakthroughs ETF"` — confirms this
  is a different security.
- `data/raw/fmp-cache/profile-c3f4...json` (cached `SBIO.L` FMP profile):
  `isin: "IE00BQ70R696"`, `"Invesco NASDAQ Biotech UCITS ETF"` — matches the
  statement exactly.
- `data/raw/fmp-cache/etf-sector-weightings-2cca...json`: `{"symbol":
  "SBIO.L", "sector": "Healthcare", "weightPercentage": 100}` — confirms the
  live-captured field name is literally `weightPercentage` (numeric, not a
  `"NN.NN%"` string), which is what `etf_sector_resolution.py:106` reads.

I then ran the real, unmodified `resolve_etf_sector` against the real
`MarketDataService` + real `FmpClient` (no mocks, no monkeypatching),
network-free (served from the disk cache above):

```
imported = ImportedInstrument(symbol="SBIO", isin="IE00BQ70R696")
resolve_etf_sector(imported, MarketDataService())
-> ("Health Care", "fmp_etf_sector_weighting_confirmed")
last_fetch_meta: {"resolved_symbol": "SBIO.L", ...}
```

This matches the value I derived independently from the primary-source ISIN
and cache data before running the code, and confirms the candidate actually
used in production is `SBIO.L`, never bare `SBIO`. This is the strongest
available anchor for a provider-sourced classification without live FMP
access (pack §"Audit mode": recompute against the local cache, not live FMP).

## Doc-vs-code cross-check

`financial-methodology.md`'s "Direct-held ETF branch classification (US-39.1)"
pseudocode and its "implementation detail" prose match
`etf_sector_resolution.py` line-for-line: identity gate before the
weightings fetch (not after, as the doc explicitly flags as a deliberate
ordering difference from its own simplified pseudocode); `DOMINANCE_THRESHOLD
= 0.55` as a fraction (scale-invariant, confirmed by the code comment and by
`test_dominance_threshold_constant_is_fifty_five_percent`); `>=` comparison
(confirmed by `test_dominance_threshold_pass_at_exactly_the_threshold`
passing at exactly 55.0/100.0); `SECTOR_TAXONOMY_MAP` reused verbatim, not
duplicated; new `classification_source` literal
`"fmp_etf_sector_weighting_confirmed"`, distinct from
`"fmp_identity_confirmed"`. `06-technical-plan.md § T-39.1.4`'s prescribed
code block is byte-identical to what actually shipped in
`etf_sector_resolution.py` — the implementation did not drift from the
reviewed design.

## Duplication check

`grep -rn "SECTOR_TAXONOMY_MAP"` across `app/` (excluding tests) shows exactly
one definition (`equity_sector_resolution.py:39`), imported by
`etf_sector_resolution.py:30` — not copied. `grep -rn "DOMINANCE_THRESHOLD"`
shows exactly one definition, in the new module only. `grep -rn
'"fmp_identity_confirmed"\|"fmp_etf_sector_weighting_confirmed"'` confirms
each literal is emitted from exactly one module — no cross-contamination
between the equity and ETF branches.

## Edge cases exercised

Ran `test_etf_sector_resolution.py` (17/17 pass) covering: identity match +
dominant sector; SBIO bare-ticker rejection (asserts
`weightings_calls == []`, i.e. the weights endpoint is never even called for
a rejected candidate); generic ISIN mismatch; missing ISIN on either/both
sides (4 parametrized cases, including both-blank-string, which
`normalize_isin("")` correctly folds to `None`); dominance threshold at
exactly 55.0%, just above, just below (never `"Broad Market"`, asserted
explicitly); unmapped bucket (`"Cash & Others"`); empty weights list;
no-coverage symbol; zero-total-weight; two independent exception surfaces
(`get_company_profile` raising, `get_etf_sector_weightings` raising, the
latter confirming the profile call still happened first). Also ran
`test_analytics.py::test_build_portfolio_overview_discloses_unclassified_direct_held_etf_bucket`
(AC11): confirms the Unclassified bucket's weight is not dropped from the
total (`sum(weights) == 1.0`) and is not folded into `"Broad Market"`.

## T-39.1.7 assessment (requested judgment)

**Root cause, confirmed by reading the code (not just 10-test.md's account):**
before this fix, `build_portfolio_overview` always constructed a real
`MarketDataService()` internally with no injection seam.
`export_dashboard_goldens.py`'s bare-script export therefore resolved SBIO's
sector from the real on-disk FMP cache (`"Health Care"`), while pytest's
`test_generated_matches_committed_goldens` ran the same render through
`conftest.py`'s `_mock_overview_engine_market_data` autouse fixture (which
patches `app.analytics.overview.MarketDataService` to always return `None`
for `get_company_profile`), forcing `"Unclassified"`. Two different sources
of truth for the same "committed" file — a genuine nondeterminism bug,
correctly diagnosed by the test lane as pre-existing and out of scope for a
test-only lane.

**The fix:** `build_portfolio_overview` gained a keyword-only `market_data`
parameter (`overview.py`, confirmed via `git diff`), defaulting to
constructing `MarketDataService()` only when `None` is passed.
`export_dashboard_goldens.py`'s `_build_fixture` now threads its own
`market_data` argument through explicitly. `render_dashboard_goldens_text`
(shared by both the bare-script export and the in-process pytest render)
already defaulted `market_data` to `FrozenMarketData.from_file()` — so both
paths now go through the *same* object. `FrozenMarketData` (confirmed by
`grep -n "def get_"`) implements only the four price-history methods
`run_imported_dashboard_history` needs; it has no `get_company_profile` or
`get_etf_sector_weightings`. Calling either raises `AttributeError`, caught
by `resolve_etf_sector`'s bare `except Exception` — the same fail-closed path
AC10 already requires — producing `"Unclassified"` deterministically on both
paths now. Confirmed live in the committed `dashboardGoldens.ts`: SBIO's
$357.05 (0.55%) sits under its own `"Unclassified"` bucket, included in the
total, never folded into `"Broad Market"` or any named sector; `"Health
Care"` in the same fixture is genuinely CRSP + EDIT, not SBIO.

**Judgment: methodologically sound, not a violation.** The fix resolves the
nondeterminism by unifying both paths onto the *same* frozen, capability-
limited data source and lets both fail closed identically, rather than by
inventing a way to bake a captured "Health Care" answer into a static fixture
that has no mechanism to ever refresh it (the doc's own note that FMP profile
lookups are cached up to 30 days makes a silently-stale hardcoded golden
value a real risk, not a hypothetical one). "Unclassified" is the honest
answer given what `FrozenMarketData` actually has access to — this is
guardrail 4 working as intended, not a workaround.

**Named consequence, not a defect:** the checked-in golden fixture no longer
exercises SBIO's *positive* resolution path (`"Health Care"`,
`"fmp_etf_sector_weighting_confirmed"`) at all — only the fail-closed path is
covered by `run_all_tests.py`'s golden diff. Coverage for the positive path
rests entirely on the isolated unit tests (which use `FakeMarketData`, not
the real FMP client/cache) and on this audit's own out-of-band recomputation
above. A future regression in the real field-name/candidate wiring (e.g. FMP
renaming `weightPercentage`) would not be caught by the golden diff — it
would simply keep failing closed to `"Unclassified"`, which is safe but
silent. Recorded in `risks` above; not blocking, since fail-closed is
strictly the correct failure direction per this project's guardrails.
