REPORT 2026-08-24-etf-sector-classification-research/10
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_etf_sector_resolution.py — new: 17 tests for resolve_etf_sector, see § Test inventory
  - services/quant-engine/app/tests/fixtures.py — FakeMarketData extended with sector_weightings/raise_for_weightings + get_etf_sector_weightings
  - services/quant-engine/app/tests/test_instrument_registry.py — rewrote 2 pinned-defect tests; added 3 ETF-branch wiring tests
  - services/quant-engine/app/tests/test_analytics.py — new aggregation case: unclassified direct-held ETF, weight counted in total
  - services/quant-engine/app/tests/test_symbols.py — new file: SBIO candidates + whole-table collision-freedom check

verification:
  command:   cd /c/projects/investments/portfolio && python scripts/run_all_tests.py 2>&1 | tail -100
  result:    FAIL
  detail:    904 passed, 1 failed (backend pytest) — the 1 failure is test_golden_pipeline_determinism.py::test_generated_matches_committed_goldens, a pre-existing defect unrelated to any file in this lane's scope; see § Verification detail and risks. Frontend/tsc/dead-code steps never ran (pipeline stops on backend failure); dead-code gate confirmed separately clean (see § Verification detail).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FakeMarketData extended with get_etf_sector_weightings/.weightings_calls, sector_weightings/raise_for_weightings kwargs — mirrors get_company_profile/.calls/raise_for shape. No new fake class — see § Handoff detail.
  - New file test_symbols.py — first test module for app.core.symbols; a "no duplicate canonical/alias key" regression any future SymbolResolutionRule must keep passing — see § Handoff detail.
  - The 2 work-order-named pinned-defect tests are rewritten AND renamed, not left alongside new ones — see § Handoff detail for old/new names.

risks:
  - BLOCKING DEFECT found, not fixed (out of scope): app/analytics/overview.py's build_portfolio_overview is non-deterministic, breaking run_all_tests.py — see § Risk detail for full diagnosis.
  - Defect predates this story (latent since US-37.1's equity branch) but was inert until SBIO's new ETF dynamic lookup became the first case to expose it — see § Risk detail.
  - Isolation proof: git-stash of all 5 files this lane touched still reproduces the identical failure on the untouched tree — see § Risk detail.
  - Every test this lane authored passes, narrowly and in the 905-item full suite; the one FAIL is entirely the pre-existing defect, not lane work — see § Risk detail.

## Orchestrator brief
- All T-39.1.6 coverage delivered and passing: 17 new resolver tests, 2 pinned-defect tests rewritten + 3 new wiring tests, 1 new aggregation test, 1 new symbols regression module, FakeMarketData extended per plan — see § Test inventory.
- `python scripts/run_all_tests.py` is NOT green: 1 pre-existing, out-of-scope backend defect (`app/analytics/overview.py`'s non-deterministic MarketDataService construction) blocks it — see § Verification detail and § Risk detail for full diagnosis, root cause, and isolation proof.
- This is a genuine defect finding, not a chore — route to backend-engineer; fixing it requires either injecting a frozen/deterministic market_data into `build_portfolio_overview` for the golden-export path, or an equivalent fix inside `app/analytics/overview.py` / `app/scripts/export_dashboard_goldens.py`, both outside this lane's scope.
- No production code was touched by this dispatch; scope discipline held throughout.
- New/renamed test names and fixture shapes for the next lane: see § Handoff detail.

## § Test inventory

`test_etf_sector_resolution.py` (17 tests): identity-match + above-threshold success; SBIO-collision-prevented (bare "SBIO" wrong-ISIN candidate rejected before the weights fetch); ISIN mismatch; no-ISIN-evidence (4 parametrized cases); dominance-threshold pass at exactly 55% and just above; dominance-threshold fail just below 55% (explicit `!= "Broad Market"`); the 0.55 constant itself; unmapped bucket; empty weights list; no-coverage symbol; zero-total-weight; both `get_company_profile` and `get_etf_sector_weightings` exception cases (2 distinct).

`test_instrument_registry.py`: rewrote `test_enriched_etf_description_round_trips_to_broad_market_sector` -> `test_enriched_etf_description_with_no_market_data_yields_no_classification` (asserts `sector is None`, `classification_source is None`, `category == "ETF"` unchanged); rewrote `test_etf_branch_ignores_market_data_and_makes_no_fmp_call` -> `test_etf_branch_with_market_data_attempts_dynamic_lookup_and_falls_through` (asserts `market_data.calls == ["ZZZ2"]`, `sector is None`, `classification_source == "unavailable"`, `category == "Sector UCITS ETF"` unchanged); added `test_etf_branch_without_market_data_yields_no_classification_not_broad_market` (the old test's original no-market_data premise); added `test_static_registry_etf_never_calls_fmp_even_when_market_data_supplied` (AC1, SPY through `attach_snapshot_metadata`); added `test_etf_branch_with_market_data_and_isin_match_resolves_fmp_sector` (AC2/AC3 full wiring success).

`test_analytics.py`: `test_build_portfolio_overview_discloses_unclassified_direct_held_etf_bucket` — a direct-held ETF with no FMP coverage lands in "Unclassified", never "Broad Market", weight included in the 1.0 total.

`test_symbols.py` (new module, no prior test_symbols.py existed): SBIO's quote/history/holdings candidates all resolve to `["SBIO.L"]` only; no dedicated proxy; canonicalization; plus 2 general regression tests (no duplicate canonical/alias key across `DEFAULT_SYMBOL_RULES`, and the built `rule_index`'s size matches the expected disjoint-key count).

## § Handoff detail

`app.tests.fixtures.FakeMarketData` gained `get_etf_sector_weightings(symbol)` + `.weightings_calls`, gated by new `sector_weightings: dict[str, list[dict]]` and `raise_for_weightings: set[str]` constructor kwargs — same shape and calling convention as the existing `get_company_profile`/`.calls`/`raise_for`. No second fake class was created; every ETF-branch test in this lane's scope uses this one extended class.

`test_symbols.py` is a new file — no `test_symbols.py` or equivalent existed before this lane. It establishes a general "no duplicate canonical/alias key across `DEFAULT_SYMBOL_RULES`" regression that any future `SymbolResolutionRule` addition (not just SBIO) must keep passing.

The 2 tests the work order named as pinning the removed pre-fix defect were rewritten AND renamed, not left alongside new tests: `test_enriched_etf_description_round_trips_to_broad_market_sector` -> `test_enriched_etf_description_with_no_market_data_yields_no_classification`; `test_etf_branch_ignores_market_data_and_makes_no_fmp_call` -> `test_etf_branch_with_market_data_attempts_dynamic_lookup_and_falls_through`, with a new sibling `test_etf_branch_without_market_data_yields_no_classification_not_broad_market` covering the old test's original no-`market_data` premise (per the technical plan's explicit instruction to add this if not already covered).

## § Risk detail

**The defect.** `app/analytics/overview.py:19`'s `build_portfolio_overview` always constructs a real, unmocked `MarketDataService()` for sector classification, with no parameter to inject a frozen/deterministic fixture — unlike the rest of the golden-export pipeline's stated "frozen, network-free, deterministic" contract (`app/tests/conftest.py:24-31`, US-21.4 docstring). `app/scripts/export_dashboard_goldens.py:197` calls `build_portfolio_overview(snapshot_model)` directly, so the golden-export step never routes sector classification through `FrozenMarketData` at all.

**Why it was inert until now.** `app/tests/conftest.py:304-326`'s autouse `_mock_overview_engine_market_data` (added for US-37.1) patches `app.analytics.overview.MarketDataService` inside pytest to always return `get_company_profile() -> None`, forcing every dynamically-resolved sector to fail closed. Outside pytest (the bare `python -m app.scripts.export_dashboard_goldens` step `run_all_tests.py` itself runs), no such mock exists, so the real client is used — apparently resolving SBIO's identity + sector weightings from a local FMP disk cache. No equity/ETF in `docs/IB2026.csv`'s golden statement previously triggered a dynamic lookup at all (AAPL etc. are static-registry hits); SBIO's new ETF-branch dynamic lookup (this story) is the first case that does, so the divergence between "real client" and "always-None mock" first becomes observable now.

**Effect and why it can't be fixed in this lane.** The bare-script export writes SBIO as Health Care/Consumer Discretionary-bearing; the in-process `test_generated_matches_committed_goldens` (running under the autouse mock) renders SBIO as Unclassified. `run_all_tests.py` cannot go green without either fixing `overview.py`'s determinism gap (production code, out of scope) or changing the golden statement/fixture (also out of scope for a test-only lane per this order's non_goals discipline).

**Isolation proof.** `git stash push -u` on all 5 files this lane touched/created (`fixtures.py`, `test_analytics.py`, `test_instrument_registry.py`, `test_etf_sector_resolution.py`, `test_symbols.py`), then `SKIP_GOLDEN_FRESHNESS_CHECK=1 pytest app/tests/test_golden_pipeline_determinism.py -q` against the now-untouched tree (only 07/08-backend.md's landed production code present): identical `1 failed, 3 passed`, byte-for-byte same diff (`"Health Care": "1.6%"` / `"Consumer Discretionary": "1.1%"` present in committed, absent in fresh). `git stash pop` restored all 5 files afterward; restoration verified via targeted grep on each file's new symbols.

**Confirmed clean otherwise.** `SKIP_GOLDEN_FRESHNESS_CHECK=1 pytest` across every file this lane touched plus `test_equity_sector_resolution.py`/`test_fixtures.py` (regression check on the shared fixture): `300 passed`. The full backend suite (`python -m pytest -n auto`, the same invocation `run_all_tests.py` uses): `904 passed, 1 failed` — the one failure is exactly `test_generated_matches_committed_goldens`.

## § Verification detail

Ran the order's exact verification command twice (once before, once after isolating my changes) — both times: `904 passed, 1 failed` at the backend pytest step, pipeline then halts (frontend/tsc/dead-code steps in `run_all_tests.py` never execute on a failed backend step).

The one failure: `app/tests/test_golden_pipeline_determinism.py::test_generated_matches_committed_goldens`.

```
E       assert 'import type ...boardSource\n' == 'import type ...boardSource\n'
E         [92% weight bucket...] "Health Care": "1.6%",   <- present in committed, absent in fresh
E                                "Communication Services": "1.5%",
E                                "Financials": "1.2%",
E         [...]                  "Consumer Discretionary": "1.1%"  <- present in committed, absent in fresh
```

Root cause, confirmed by reading:
- `app/analytics/overview.py:19`, `build_portfolio_overview` does `market_data = MarketDataService()` unconditionally — a real client, with no parameter to inject a frozen/deterministic fixture.
- `app/scripts/export_dashboard_goldens.py:197` calls `build_portfolio_overview(snapshot_model)` directly for the golden-export step, so this path is NEVER routed through `FrozenMarketData` even though the module's own docstring (`app/tests/conftest.py:24-31`, US-21.4) promises the whole golden pipeline is "frozen, network-free, deterministic".
- `app/tests/conftest.py:304-326`'s `_mock_overview_engine_market_data` (added for US-37.1, autouse) patches `app.analytics.overview.MarketDataService` inside pytest to always return `get_company_profile() -> None` — so inside pytest, every dynamically-resolved sector (equity OR, as of this story, ETF) always fails closed to "Unclassified".
- Outside pytest (the bare `python -m app.scripts.export_dashboard_goldens` step `run_all_tests.py` itself runs), no such mock exists — the real `MarketDataService()` is used, apparently able to resolve SBIO's identity + sector weightings from a local FMP disk cache (no live network call observed; the process exited cleanly under `--disable-socket`-equivalent conditions when tested standalone) — its result becomes the "committed" file.
- The in-process `render_dashboard_goldens_text()` call inside `test_generated_matches_committed_goldens` runs UNDER pytest, so it goes through the same autouse mock, forcing SBIO to Unclassified — disagreeing with the just-written "committed" file.

This is a **pre-existing defect independent of this story's tests**, isolated as follows: stashed all 5 files this lane touched/created (`fixtures.py`, `test_analytics.py`, `test_instrument_registry.py`, `test_etf_sector_resolution.py`, `test_symbols.py`), re-ran `SKIP_GOLDEN_FRESHNESS_CHECK=1 pytest app/tests/test_golden_pipeline_determinism.py -q` against the unmodified tree (only 07/08-backend.md's landed production code present) — **identical failure, byte-for-byte same diff**. Popped the stash to restore all 5 files afterward (verified restored via grep).

Also ran, standalone (outside pytest, to confirm the two render paths individually):
```
python -c "from app.scripts.export_dashboard_goldens import render_dashboard_goldens_text, _dashboard_golden_output_path, _repo_root; ..."
```
→ `EQUAL` (bare script's fresh render matches the committed file it just wrote) — confirms the divergence is specifically pytest's autouse mock vs. bare-script's real `MarketDataService()`, not a second source of nondeterminism.

Ran `python scripts/detect_deadcode.py --strict` standalone (never reached by the halted `run_all_tests.py` run): `ruff clean, vulture clean, knip clean — "STRICT: no dead-code findings — clean."` All 5 new/changed test files are dead-code-gate clean.

Narrow-mode confirmation that every test this lane wrote passes (bypassing the unrelated golden-freshness precondition per the pack's documented escape hatch):
```
SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_etf_sector_resolution.py app/tests/test_instrument_registry.py app/tests/test_analytics.py app/tests/test_symbols.py app/tests/test_equity_sector_resolution.py app/tests/test_fixtures.py -q
```
→ `300 passed`. Full backend suite the same way (`SKIP_GOLDEN_FRESHNESS_CHECK=1 pytest -q` equivalent via the full-suite pytest invocation minus the one autouse freshness fixture): `905 passed` — the ONE test that fails is exactly `test_generated_matches_committed_goldens`, which the skip flag does not bypass (it is a separate, non-fixture test, not the `conftest.py` autouse fixture the env var targets) — so its dedicated narrow run above (`app/tests/test_golden_pipeline_determinism.py`) is the only way to isolate it, and that also reproduces `1 failed, 3 passed` deterministically on both the pre-lane and post-lane tree.

`git status --short apps/desktop/src/test/dashboardGoldens.ts` after the full `run_all_tests.py` run: empty (no diff) — the export step's bare-script output already matches the committed file on disk; the divergence is entirely between that committed file and pytest's in-process, autouse-mocked render, not a stale-commit issue the pack's "goldens drift is usually noise, `git checkout --` it" guidance covers.
