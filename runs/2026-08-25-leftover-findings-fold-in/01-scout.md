REPORT 2026-08-25-leftover-findings-fold-in/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - "The 3 points" reading confirmed: the 3 CARRIED findings (not protocol_notes) in 2026-08-24-sbio-still-unclassified-bug/run.md § Open — see § The 3 CARRIED items.
  - No other doc enumerates exactly 3 open items — epic-roadmap.md § Open items (lines 15-53) has 5 bullets covering 6+ distinct sub-items (US-26.3/26.4, 3 Epic-34 findings, Epic-35 framing note, 4 Epic-36 carries, 6 dependency advisories) — see § Other doc candidates ruled out.
  - Item 1 (Finding 2/MATERIAL, no freeze-date UI signal) reconfirmed live: apps/desktop/src/features/portfolio/variantLabels.ts:4,10,23 labels a base-import node only as the literal string "base", no date/timestamp anywhere in that string.
  - Item 2 (source_status staleness residual) reconfirmed live: services/quant-engine/app/services/exposure_engine.py:131-149 (_build_exposure_source_status) and :165-209 (_build_exposure_availability) both recompute live per engine run from current market_data, not frozen at import; CR-1 only touched the frontend consumer, not this backend function (confirmed via CR-1-frontend.md's own grep note).
  - Item 3 (add_snapshot lossy) reconfirmed live: apps/desktop/src/app/App.tsx:789 passes importedHistorySnapshot: null on the add_snapshot path, vs :801 which passes nextAnalysis.snapshot on the replace path — the T1 fix (persisting the analyze-upload response instead of re-deriving) only reaches the replace path.
  - 4th scope item (risk.py:612/1483 attach_snapshot_metadata, no market_data arg) reconfirmed live at those exact line numbers; registry.py:325-330 confirms market_data is an Optional[MarketDataService]=None kwarg silently defaulted.
  - None of the 3 (or the 4th) have an existing tech-debt-register.md row or epic-roadmap.md Open-items mention — all four are undocumented outside the 2026-08-24 run.md itself; producer must add them fresh, not dedupe.
  - Every other currently-open item found, with file:line/doc-line and confirmed-still-present status, is catalogued in § Other open/carried items below (RecordingMarketData gap, dead market_data param, tech-debt-register open rows, epic-roadmap Open-items bullets, 2 protocol_notes).
  - Sequencing risk: items 2 and 4 both touch registry/metadata plumbing feeding sector/trust classification in exposure_engine.py and risk.py respectively but are independent functions with no shared line range — no direct code conflict found, see § Blast-radius / conflict notes.

risks:
  - tech-debt-register.md is 360 lines with ~90 individual rows; I did not re-quote every RESOLVED row verbatim (those are closed, not "currently-open/carried") — only open/unresolved rows are listed in § tech-debt-register open rows. If the producer needs the resolved rows too, they are all in the file as-is.
  - I did not open docs/product/prd/epic-34-answerable-dashboard-and-reachable-trust.md itself to re-verify F-1a/F-10/F-12's exact wording — epic-roadmap.md's summary of them (lines 19-22) is quoted, not independently re-confirmed against the PRD body.
  - Epic-36 close-out carries (4 items, roadmap lines 27-44) and the 6 dependency-vulnerability advisories (lines 45-53) were not independently re-verified against code (no code location given by the order for these) — reported as roadmap-doc claims only, not re-grounded.

## Orchestrator brief
The "3 points" reading is confirmed correct — no other doc enumerates exactly 3 open items; epic-roadmap's "Open items" section has far more. All 3 named CARRIED findings plus the explicitly-scoped 4th (risk.py:612/1483) were independently re-verified against current code and still hold exactly as described, with none tracked in tech-debt-register.md or epic-roadmap.md today. Two more prior-run leftovers (RecordingMarketData missing methods, dead market_data param in _build_shared_sector_overlap) were independently reconfirmed live. § The 3 CARRIED items, § 4th scope item, § Other open/carried items, § tech-debt-register open rows, § epic-roadmap Open-items bullets, § Blast-radius / conflict notes below carry the full detail.

## The 3 CARRIED items (verbatim from run.md § Open, lines 32/33/35)

1. **Finding 2 (MATERIAL)** — "no end-user UI signal that a base-import node's frozen data isn't live — snapshot picker labels it just \"base\", no date. Human explicitly deferred as accepted gap, not part of this run." Class: real UX/product decision (a design choice — what signal, where — not just a code change). Location: `apps/desktop/src/features/portfolio/variantLabels.ts:4,10,23` (the label string), rendered via `apps/desktop/src/app/App.tsx:876-877` (snapshot picker options). No date/timestamp field is threaded into either.
2. **Trust-descriptor staleness residual** — "run_metadata.source_status.lookthrough_resolution / .confidence retain the identical trust-descriptor staleness risk availability had (Finding 1's class) — not fixed here, candidate follow-up." Class: real design-bearing code change (same shape as the already-fixed Finding 1, i.e. moving a badge/consumer off a live-recomputed field onto a frozen one, but on the backend `run_metadata.source_status` producer this time, not a frontend consumer swap). Location: `services/quant-engine/app/services/exposure_engine.py:131-149` (`_build_exposure_source_status`) and `:165-209` (`_build_exposure_availability`), both called fresh from `build_exposure_result` at `:83-89` on every engine run.
3. **add_snapshot mode stays broken** — "deliberately excluded both times scope was decided; a future fix needs client-side recombination of two PortfolioOverview-shaped objects, not designed here." Class: real design-bearing code change, previously explicitly scoped out twice already (02 and 03 technical-plan). Location: `apps/desktop/src/app/App.tsx:767-795` (the `add_snapshot` branch of `processImportedFiles`), specifically `:789` `importedHistorySnapshot: null` vs the replace path's `:801` `nextAnalysis.snapshot`; feeds `apps/desktop/src/app/portfolioWorkspaceStorage.ts:301-324` (`saveImportedSnapshotNode`).

## 4th scope item (explicitly named in this order's scope, from 01-scout § handoff of the prior run)

`risk.py:612` (`build_lookthrough_exposure`) and `risk.py:1483` (inside `build_etf_overlap_pairs`) both call `registry.attach_snapshot_metadata(snapshot)` with no `market_data` kwarg. `attach_snapshot_metadata` (`services/quant-engine/app/instruments/registry.py:325-330`) accepts `market_data: MarketDataService | None = None` and threads it into `classify_imported_instrument(..., market_data=market_data)` for ETF-branch sector resolution (the US-39.1 mechanism). Both call sites default to `None`, so any instrument metadata built there gets no dynamic sector resolution. Confirmed inert today — at `risk.py:612` only asset-class-adjacent fields are read downstream in `build_lookthrough_exposure`, not `.sector`. Class: tiny-to-small code change (add one kwarg at two call sites) IF the producer decides sector-awareness should extend there — currently a latent gap, not a bug.

## Other open/carried items found independently

- **RecordingMarketData missing `get_company_profile` / `get_etf_sector_weightings`** (Epic 39 run leftover, not in run.md's Open table but referenced by this order). `services/quant-engine/app/scripts/frozen_market_data.py:131-186` (class `RecordingMarketData`) implements only `get_historical_prices`, `get_direct_verified_benchmark_history`, `get_historical_prices_for_symbols`, `get_last_fetch_meta` — confirmed no `get_company_profile`/`get_etf_sector_weightings` method exists there, while the real `services/market_data.py:503,525` and `app/tests/fixtures.py:170,176` both implement them. Class: real code change (test-infra gap) — the frozen-fixture recording harness cannot capture ETF sector-weighting calls made via the real service, which affects the golden-refresh workflow for any future story touching `resolve_etf_sector`.
- **Dead `market_data` param in `_build_shared_sector_overlap`** (Epic 38 run leftover). `services/quant-engine/app/analytics/risk.py:1648-1687` — the function signature accepts `market_data: HoldingsMarketData` (`:1654`) but the body never references it (the US-38.1 comment at `:1672-1678` explains a live FMP lookup here was deliberately removed in favor of "Unclassified" disclosure, leaving the parameter unused). Confirmed still present, called with a live `market_data` arg from `:1531`. Class: tiny code change (dead-param removal) — likely a `detect_deadcode.py`/vulture catch once ruff/vulture run on this signature, but the pack notes the dead-code gate treats unused params differently from unused locals; not independently confirmed whether it currently fails the gate.
- **Two protocol_notes CARRIED in run.md** (not code items — process/reporting conventions): (a) inconsistent self-reporting between T1-frontend (PARTIAL) and CR-1-frontend (DONE) for the same class of pre-scoped downstream-owned gap; (b) the orchestrator's own CR-1 asked a frontend-engineer to write tests, a lane-discipline conflict CR-1-frontend itself flagged (see CR-1-frontend.md § Test-writing conflict, quoted above). These are meta/process findings, not code — flagging per DoD's "every OTHER currently-open/carried item" instruction, since they were CARRIED, not CLOSED.

## tech-debt-register.md open rows (unresolved only — RESOLVED rows omitted as closed, not "open")

- Line 86, `US-26.3` (Med, NEW): `portfolio_snapshot_builder.py:43` coerces `currency=item.currency or request.base_currency or 'USD'` for currency-less positions from `PortfolioEngineRequest` — a silent fallback fabricating currency provenance on the request path (not the imported path). Needs a schema change to represent "currency unknown" — own story, not fixed. Class: real design-bearing (schema) change.
- Line 176, leaf per-token match scores in `_*_score` helpers (`risk.py`) stay inline post-US-24.2 — deferred, low value. Class: tiny.
- Line 178, `analytics/risk.py:1262-1267` volatility-regime percentile cutoffs (`<0.30`/`<=0.80`) inline, undocumented literal. Class: tiny.
- Line 179, `analytics/risk.py:1331` `len(common_dates) < 10` minimum-history gate, undocumented literal distinct from `WINDOW_MIN_OBSERVATIONS`. Class: tiny.
- Line 180, `analytics/risk.py:750-751,1441` top-N display slices hardcoded (`[:5]`, `[:15]`). Class: tiny.
- Line 181, `analytics/risk.py:1038,1040-1052` `build_factor_exposures` hardcodes growth-tilt sector composition + factor-exposure label/description/basis list inline. Class: small-med.
- Line 183, `analytics/drawdown.py:353` `abs(residual_pct) < 0.001` epsilon + `top_n` cap at :157 inline. Class: tiny.
- Line 184, `analytics/distribution.py:67-71` percentile fractions inline (documented/keyed — low concern per the row itself). Class: tiny.
- Line 215, `services/portfolio_proof.py:1264` `_terminal_totals_match(tolerance: float = 0.01)` reconciliation tolerance inline. Class: tiny.
- Line 216, `services/statement_importer.py:190` percent→fraction `/100` conversion inline in TWR compounding loop. Class: tiny.
- Line 168-172, `domain/ledger.py` broker-statement section labels hardcoded into domain layer (fragile-coupling, med severity); entry-type pseudo-enum with no shared Literal/Enum (missing-abstraction); `"USD"` default repeated across schema/ledger. Class: small-med, epic-24 backlog, unresolved.
- Line 173, `analytics/risk.py:138-142` `STRESS_SCENARIOS` three stress vectors hardcoded inline as tuple-of-dicts — methodology-documented but not reviewable config. Class: small-med.
- Line 121-129, "Over-exported (live, not dead)" — 71 TS exports used in-file only, unnecessary `export` keyword, owner US-23.4, optional/low priority, unresolved.
- Line 233-234, US-23.6 catalog: hand-rolled test-builder duplication across 9 backend test files (deferred, migrate opportunistically); one test (`test_build_portfolio_risk_summary_and_position_contributions`) missing its promised assertion coverage.
- Line 246-250, "Remaining (deferred within Epic 23)": empty feature dirs (resolved-as-intentional, not actionable); over-exported live types (same as above); 7 suspected-unused CSS tokens (not removed, needs careful pass).

## epic-roadmap.md § Open items (lines 15-53, verbatim bullets)

1. Line 17-18: "Tech debt **US-26.3** (currency-risk follow-up) and the optional **US-26.4** — see `docs/tech-debt-register.md`." (US-26.4 itself was not found as its own row inside tech-debt-register.md's current content — likely referenced only here; flagging as a possible doc-drift, not independently resolved.)
2. Line 19-22: Epic 34 findings left open with reasons in its PRD — F-1a (portfolio leg's exact-slice admission structurally unreachable), F-10's untouched half (drawdown family stays withheld), F-12 (bounded synthetic-path dividend exposure). Not independently re-verified against the PRD body (see risks).
3. Line 23-26: Epic 35's cache-hazard framing correction (bare `clear` does remove `history_yf`; the sharp edge is a 401 returned as data, not raised) — descriptive note, not an open defect per the roadmap's own text (Epic 35 is closed, all 3 fixed).
4. Line 27-44: Epic 36 close-out carries — 3 SHOULD_FIX + 1 operational note from `14-integration.md`: (1) `audit_dependencies.py main()`'s cross-ecosystem priority rule untested; (2) `_commit_gate.changed_files()`'s rename-entry parsing has no regression test; (3) npm-audit network-failure marker text unverified against a real failure; (4) shared `.claude/.last-test-pass` marker race under concurrent lane dispatch — a process footgun, not a code defect in this repo's product surface.
5. Line 45-53: Real dependency-vulnerability advisories (starlette, pypdf, python-multipart, pydantic-settings, python-dotenv, @babel/core) surfaced by live scans, deliberately not acted on in Epic 36 — expected to reappear on the scheduled `dependency-audit.yml` run.

## Other doc candidates ruled out for "the 3 points"

- `docs/tech-debt-register.md` — no section anywhere enumerates exactly 3 open items; it has ~15+ open individual rows across multiple catalogs (see above).
- `docs/product/epic-roadmap.md` § Open items — 5 top-level bullets, several containing multiple named sub-findings (3 Epic-34 findings alone, 4 Epic-36 carries, 6 dependency advisories) — not a set of exactly 3.
- `docs/product/current-product-state.md` — grepped for carried/open/deferred/follow-up language; no open-items list found, it is a shipped-state inventory, not a backlog.
- Conclusion: the run.md § Open table's 4 `finding`-kind CARRIED rows are the only place with a small, enumerable set, and the order's own wording ("Finding 2/MATERIAL", "the run_metadata.source_status staleness residual (same class as the fixed Finding 1", "add_snapshot mode still shows lossy...") matches 3 of those 4 rows verbatim — the 4th (risk.py:612/1483) is separately named in this order's own scope rather than folded into "the 3", confirming the order's own reading is internally consistent.

## Blast-radius / conflict notes

- Item 1 (freeze-date UI signal) is frontend-only: `variantLabels.ts` + wherever it's consumed in `App.tsx`. No backend schema change implied unless the producer wants to surface `imported_at`/`snapshot_as_of_date` (already present in `ExposureRunReproducibilityMetadata` per `exposure_engine.py:156-162`) through a new prop — that data already exists engine-side, just isn't threaded to the picker label.
- Item 2 (source_status staleness) is backend-only in `exposure_engine.py`; a fix in the same shape as CR-1 (make the field read from something frozen, or stop surfacing it as a trust signal) would touch `ExposureRunSourceStatus`/`ExposureRunMetadata` — both are documented in `docs/contracts/` (not opened this run — flag for producer to confirm which contract doc covers `run_metadata.source_status`).
- Item 3 (add_snapshot lossy) is frontend-only in `App.tsx` + `portfolioWorkspaceStorage.ts`, and per 02-technical-plan's own carried note, needs "client-side recombination of two PortfolioOverview-shaped objects" — a nontrivial design decision, not a one-line fix.
- Item 4 (risk.py market_data arg) and the dead-param finding (`_build_shared_sector_overlap`) both live in `analytics/risk.py` but touch different functions (`build_lookthrough_exposure`/`build_etf_overlap_pairs` vs `_build_shared_sector_overlap`) with no overlapping line ranges — no direct conflict, but both are in the same file and both concern how/whether `market_data` reaches sector-classification code paths in that module; a single story touching "risk.py market_data plumbing" broadly could plausibly bundle both, which the producer may want to weigh for scope/sequencing.
- No other cross-item conflicts found — the 3 CARRIED items span 3 different files/layers (variantLabels.ts, exposure_engine.py, App.tsx) with no shared function.
