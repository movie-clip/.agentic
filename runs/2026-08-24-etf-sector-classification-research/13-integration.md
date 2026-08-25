REPORT 2026-08-24-etf-sector-classification-research/13
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd /c/projects/investments/portfolio && python scripts/run_all_tests.py 2>&1 | tail -100
  result:    PASS
  detail:    905 backend passed (0 failed), 331 frontend passed (37 files), tsc clean, dead-code gate clean (ruff/vulture/knip). Re-ran independently, not trusted from 11-backend.md; identical counts. git status after the run shows no further drift beyond the run's own 19 files.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Golden no longer exercises SBIO's positive resolution path end-to-end (quant-audit's flag) — judged acceptable, not blocking, see § T-39.1.7 assessment.
  - Two lane-report narrative inaccuracies found and corrected during this review, not code defects — see § Report accuracy notes.
  - RecordingMarketData's docstring is misleading (claims full delegation, only forwards 4 methods) — pre-existing, untouched here, see § T-39.1.7 assessment.

## Orchestrator brief
- VERDICT: PASS. No BLOCKING or SHOULD_FIX change requests against any of T-39.1.1-7.
- T-39.1.1-6 confirmed landed exactly per 06-technical-plan.md — byte-identical code in the two places checked closest (etf_sector_resolution.py, registry.py's ETF-branch wiring) — see § Plan conformance.
- SECTOR_TAXONOMY_MAP and DOMINANCE_THRESHOLD confirmed single-sourced by grep; category derivation confirmed byte-identical pre/post — see § Duplication and category checks.
- T-39.1.7 (unplanned) evaluated on its own merits: narrowly scoped (2 production files + golden regen), both existing call sites confirmed backward-compatible by reading and by the full green suite — see § T-39.1.7 assessment.
- run_all_tests.py re-run independently by me, green end to end — see verification above.
- Docs (T-39.1.5) spot-checked against landed code — internally consistent, no drift found — see § Docs spot-check.
- Sections below: § Plan conformance · § Duplication and category checks · § T-39.1.7 assessment · § Docs spot-check · § Report accuracy notes

---

## § Plan conformance (T-39.1.1-6)

Checked the full diff against `06-technical-plan.md` field by field:

- **T-39.1.1** (`schemas/instruments.py`): `ClassificationSource` literal gains `"fmp_etf_sector_weighting_confirmed"`, docstring bullet added — matches plan § Contract verbatim.
- **T-39.1.2** (`core/symbols.py`): new SBIO `SymbolResolutionRule`, `SBIO.L`-only, no bare candidate, no proxy — matches plan § T-39.1.2 verbatim, including the comment.
- **T-39.1.3** (`clients/fmp.py`, `services/market_data.py`): `get_etf_sector_weightings` on both classes, same one-line `_get` delegation shape / same candidate-loop shape as `get_profile`/`get_company_profile` — matches plan § T-39.1.3.
- **T-39.1.4** (`instruments/etf_sector_resolution.py`, new module): read in full — byte-identical to the plan's given code block (docstring, `DOMINANCE_THRESHOLD = 0.55`, `_coerce_weight`, `resolve_etf_sector`'s exact guard sequence: profile lookup → ISIN match → weights lookup → dominance check → taxonomy map). No deviation.
- **`registry.py` wiring**: diffed directly. Every `sector = ...` line removed (the line-247 default and all 9 elif assignments); every `category = ...` line unchanged in condition, order and string value — confirmed by reading the full diff hunk, not by trusting the report's description. `classification_source=classification_source` newly threaded into the `_instrument(...)` call. Matches plan exactly, including the local-import comment for the cycle-break.
- **T-39.1.6** (tests): `test_etf_sector_resolution.py` (17 tests) covers every AC3-AC10 edge case named in the plan, including both exception surfaces and the exact-55%/just-above/just-below threshold triad. The two pinned pre-fix tests in `test_instrument_registry.py` were rewritten and renamed (not left alongside new ones), plus 3 new wiring tests added. `fixtures.py`'s `FakeMarketData` extended (not duplicated) with `sector_weightings`/`raise_for_weightings`/`get_etf_sector_weightings`/`.weightings_calls`, same shape as the existing `get_company_profile` support. `test_symbols.py` is new and adds a durable collision-freedom regression over the whole `DEFAULT_SYMBOL_RULES` table, not just SBIO. `test_analytics.py` adds one aggregation case mirroring the equity-branch precedent exactly.

No undeclared scope drift found anywhere in T-39.1.1-6.

## § Duplication and category checks

- `grep -rn "DOMINANCE_THRESHOLD\s*="` (excluding tests): exactly one definition, `etf_sector_resolution.py:42`.
- `grep -rn "^SECTOR_TAXONOMY_MAP"`: exactly one definition, `equity_sector_resolution.py:39`; `etf_sector_resolution.py` imports it, builds its own local `_NORMALIZED_...` casefold dict the same way the equity module does — no second taxonomy table.
- `git diff services/quant-engine/app/instruments/equity_sector_resolution.py`: empty — equity branch untouched.
- `git diff services/quant-engine/app/analytics/risk.py`: empty — look-through path untouched.
- `category`'s 10-branch elif chain in `registry.py`: confirmed condition-for-condition and string-for-string identical to the pre-diff version; only the interleaved `sector = ...` statements were deleted.

## § T-39.1.7 assessment (unplanned, evaluated on merits per this order's DoD)

**Root cause** (independently confirmed by reading, not taken from 10-test.md's account): pre-fix, `build_portfolio_overview` unconditionally constructed its own real `MarketDataService()` with no injection seam. `export_dashboard_goldens.py`'s bare-script export therefore resolved SBIO's sector from the live on-disk FMP cache (`"Health Care"`), while pytest's `test_generated_matches_committed_goldens` ran the same render through `conftest.py`'s autouse mock (`get_company_profile` always `None`), forcing `"Unclassified"` — two different sources of truth for the same committed file. Confirmed the mock and the unconditional construction both exist as described.

**The fix, read directly**: `overview.py`'s `build_portfolio_overview` gains one keyword-only parameter, `market_data: object | None = None`, defaulting to `MarketDataService()` only when `None` is passed — a strict superset of the prior behavior for any caller that omits it. `export_dashboard_goldens.py`'s `_build_fixture` now threads its own `market_data` argument through explicitly (previously dropped). Two-file diff, no other production file touched (`frozen_market_data.py` confirmed untouched by `git diff --stat`, honoring the order's non_goals).

**Backward compatibility of both existing call sites, confirmed by reading, not assumed:**
- `services/exposure_engine.py:48` — `build_portfolio_overview(snapshot)`, positional, no `market_data` kwarg. Unaffected: falls into the `if market_data is None` branch, constructs a live `MarketDataService()`, byte-identical to pre-fix behavior.
- `services/exposure_engine.py:4` imports `build_portfolio_overview` from `analytics/portfolio_imports.py`, a pure re-export (`from app.analytics.overview import build_portfolio_overview`) — unaffected, no wrapping logic to go stale.
- Every test call site (`test_analytics.py`, 6 call sites) also calls positionally with no `market_data` kwarg and is unaffected the same way — confirmed by grep across the whole tree, not just the two named sites.
- `render_dashboard_goldens_text` (shared by both the bare-script export and the in-process pytest render) already defaulted `market_data` to `FrozenMarketData.from_file()` before this fix — the fix's real effect is that this default now actually reaches `build_portfolio_overview`, instead of being silently dropped at `_build_fixture`'s boundary.

**Golden regeneration, confirmed narrow**: `git diff apps/desktop/src/test/dashboardGoldens.ts` — SBIO alone moves from a "Health Care"/"Consumer Discretionary" split into its own dedicated `"Unclassified"` bucket; weight (357.05, 0.55%) is preserved, not dropped; no other symbol's sector changed. Re-running `run_all_tests.py` a second time produced an identical diff (no further drift), confirming the regeneration is itself deterministic now.

**Judgment: methodologically sound and narrowly scoped — matches quant-audit's independent assessment.** The fix removes the nondeterminism by unifying both paths onto the same frozen, capability-limited provider and lets both fail closed identically, rather than baking a live-cache-derived value into a static fixture with no refresh mechanism (a real staleness risk given the 30-day profile TTL). This is guardrail 4 (trust semantics over fabrication) working as intended.

**On the flagged consequence — decision, not re-litigation of the math**: quant-audit correctly notes the committed golden no longer exercises SBIO's *positive* resolution path end-to-end; only the fail-closed path is covered by the golden diff. My assessment: **acceptable as-is, not blocking**, for three reasons — (1) the positive-path logic itself is not undercovered: 17 unit tests exercise `resolve_etf_sector` directly via `FakeMarketData`, including the exact success case, and quant-audit's own audit ran the real, unmocked resolver against the real on-disk FMP cache and got the same "Health Care" answer independently; (2) `FrozenMarketData`/`RecordingMarketData` lacking `get_company_profile`/`get_etf_sector_weightings` is a pre-existing gap in the frozen-fixture infrastructure (confirmed by reading `frozen_market_data.py`, untouched by this run), not something T-39.1.7 introduced or made worse — before the fix, the golden pipeline's "frozen, deterministic" contract was already broken for any dynamically-resolved sector, just silently; (3) the fail-closed outcome is the *correct* one per this project's own guardrails, so a golden that only exercises the fail-closed branch is not hiding a wrong answer, only a coverage gap in one specific integration surface. Recommend a light follow-up note (not a ticket blocking this slice): extending `FrozenMarketData`/`RecordingMarketData` with the two profile/weightings methods so a future `--capture` run can deterministically freeze a positive dynamic-resolution outcome too. This is a test-infrastructure enhancement, not a defect — leaving it unticketed does not block this story's acceptance.

**One RecordingMarketData side-effect, confirmed and correctly flagged by 11-backend.md, not itself a defect from this story**: `--capture`'s sector resolution now also fails closed (previously it silently used a second, independent live `MarketDataService()` for sector resolution — never recorded, so replaying that golden would never have reproduced the same "Health Care" answer anyway). The order asked to "confirm the RecordingMarketData capture path is unaffected" — strictly, it is narrowed, not unaffected, but the narrowing is a safe direction (fail-closed) and 11-backend.md disclosed this precisely rather than silently building past it, which is the correct protocol behavior for this kind of finding.

## § Docs spot-check (T-39.1.5)

- `financial-methodology.md`'s new "Direct-held ETF branch classification (US-39.1)" subsection's pseudocode and prose read line-for-line consistent with the landed `etf_sector_resolution.py` and `registry.py` diff — identity gate before the weights fetch (explicitly flagged in the doc as a deliberate simplification vs. its own pseudocode grouping), `DOMINANCE_THRESHOLD = 0.55` as a fraction, `>=` comparison, shared taxonomy table cross-referenced not duplicated, the new literal named and distinguished from `"fmp_identity_confirmed"`.
- `exposure-fields.md:222-227`'s enumeration prose lists all four `classification_source` values now, still correctly framed as backend-internal / not a contract row — matches the schema.
- `tech-debt-register.md:186` — narrowed correctly: the keyword-substring `sector` clause for the ETF branch is marked resolved; the futures-reference-data clause and `category`'s own keyword derivation are explicitly called out as untouched, matching the code.
- `current-product-state.md`'s Exposure-tab paragraph accurately describes the identity gate, the 55% threshold, the Unclassified fallback, and that `category` is unaffected — matches the code.
- Docs-engineer's own flagged pack conflict (`capabilities/docs.md`'s flag-for-human convention on new methodology sections vs. this order's explicit DoD instruction to write one) was handled correctly per protocol: `status: PARTIAL`, conflict named in `risks`, order followed. Nothing further needed from this gate; the methodology prose itself reads as sound and is independently corroborated by quant-audit's PASS.

## § Report accuracy notes

Two lane-report narrative inaccuracies were caught and corrected during this review. Neither affects the landed code; both are noted for report-writing hygiene, not as change requests:

1. **08-backend.md's flagged risk is not present in the code.** It claimed `market_data.py:529` used a backslash (`"etf\sector-weightings"`) in the `_will_be_served_from_cache(...)` cache-key string, vs. `fmp.py`'s forward-slash path. Read the actual line (`git diff` + `cat -A` byte check): it is `"etf/sector-weightings"`, forward slash, matching `fmp.py` exactly. No cache-key mismatch exists. This looks like a report-writing error in 08-backend.md, not a defect that was silently fixed later — no other lane touched `market_data.py` after 07-backend.md landed it.
2. **11-backend.md's narrative claim about the regenerated golden is imprecise**, already caught independently by 12-quant-audit.md and reconfirmed here: it describes the post-fix `"Health Care"` bucket as "AAPL's actual weight." Read the regenerated golden's `sector_position_breakdown["Health Care"]`: it contains CRSP, EDIT, and ALLO — no AAPL. The underlying data change (SBIO moving to `"Unclassified"`, weight preserved) is correct; only the report's own prose describing which symbols remain is wrong.
