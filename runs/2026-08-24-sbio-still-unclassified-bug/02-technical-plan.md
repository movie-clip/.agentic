REPORT 2026-08-24-sbio-still-unclassified-bug/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (design/planning artifact).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T1 (frontend-engineer): implement the importedOverview persist+reuse mechanism — see § Technical plan, lanes.
  - T2 (test-engineer): regression coverage for T1's behavior, including the deliberately-unfixed add_snapshot case — see § Technical plan, lanes.
  - No backend-engineer ticket — this fix requires zero backend/schema changes; confirmed after full design, see § Contract change verdict.

risks:
  - Root-cause blast radius is wider than "sector" (asset_class also lost) — this ticket set does not close it, see § Risk detail, "Blast radius wider than sector".
  - add_snapshot mode is deliberately left unfixed, not silently dropped — see § Risk detail, "add_snapshot mode is out of scope".
  - Considered and rejected a purely client-side sector re-derivation as a duplicated-formula risk — see § Risk detail, "Client-side re-derivation rejected".
  - Deferring the risk.py:612/1483 finding per the order's own non-goal boundary — see § Risk detail, "risk.py:612/1483 deferred".
  - Unverified assumption about projectImportedBootstrap's passthrough of `.overview` — see § Risk detail, "Unverified mapper passthrough".

## Orchestrator brief
- Decision: no schema/contract change anywhere (backend or docs/contracts/*.md) — see § Contract change verdict. Non-goal (no ISIN/description/exchange threading) honored, not exercised.
- Decision: fix is frontend-only — persist ImportedBootstrapResponse.overview onto local node storage at import time; prefer it over re-deriving via runExposureEngine where still valid. See § Root cause, confirmed and § Reuse.
- Decision: reuse gated per-node via `getDirectNodeImportSource` only (never the ancestor-walking variant), durable across app restarts — a refinement beyond the order's framing. See § Decisions, "restoredSession does not gate this."
- Decision: add_snapshot mode is explicitly out of scope, not silently dropped. See § Decisions, "add_snapshot mode is out of scope" and § Risk detail.
- Lane split: T1 frontend-engineer (mechanism, exact files/types/call-sites), T2 test-engineer (regression coverage) — see § Lanes. Sequenced T1 → T2. No backend-engineer ticket.
- Five risks carried forward for the human/producer, one is a genuinely new wider-blast-radius finding (SBIO's asset_class/ETF-lookthrough is also broken, unfixed by this ticket) — see § Risk detail.
- Blocks dispatch: nothing. Ready to dispatch T1 as written.

---

# Technical plan

## Contract change verdict

**No backend/schema change is required, and none is made.** `ImportedBootstrapResponse.overview` (Pydantic, `app/schemas/import_bootstrap.py:54`) already carries the correctly-classified `PortfolioOverview` on every `analyze-upload` response — it always has, since `build_import_bootstrap_from_snapshot` (import_engine.py:28) builds it from the real, `import_statements`-derived snapshot (full `instruments`, no loss). The bug is that the frontend never persists or reuses this value; it is read once into `nextAnalysis` and then the entire object is thrown away as soon as `restoreImportedWorkspaceFromPersistedState` calls `runExposureEngine` again. Nothing on `services/quant-engine/app/schemas/**` changes. `docs/contracts/*.md` is unaffected — the wire shape between backend and frontend TS types is unchanged; only a purely-local, undocumented (not part of any contract doc) frontend storage shape (`ImportedNodeSource` in `workspaceTypes.ts`) gains one new optional field.

## Root cause, confirmed

Read `portfolio_snapshot_builder.py`, `registry.py`, `overview.py`, `exposure_engine.py`, `import_engine.py`, `imports.py` (routes), `App.tsx` (full 341-801 range), `portfolioAnalysisAdapter.ts`, `portfolioSnapshot.ts`, and `portfolioWorkspaceStorage.ts` directly (not just the scout's trace). Confirms the scout's account and extends it:

- `build_imported_snapshot_from_request` (portfolio_snapshot_builder.py:32) hardcodes `instruments=[]` on every `SnapshotAnalysisRequest`-derived snapshot.
- `InstrumentRegistry.attach_snapshot_metadata` (registry.py:325-376), when `snapshot.instruments` is empty, routes every position through the catch-all at line 359-374, which sets **both** `sector=None` **and** `asset_class="other"` unconditionally — the loss is not sector-only. This is confirmed by reading the catch-all, not just scout's summary.
- `build_portfolio_overview` (overview.py:16) is the ONE code path that produces `PortfolioOverview.sector_allocation`/`sector_position_breakdown` — called from both `build_exposure_result` (exposure_engine.py:48, the `runExposureEngine` path) and `build_import_bootstrap_from_snapshot` (import_engine.py:28, the `analyze-upload` path). Same function, same formula — the only variable is snapshot fidelity (real instruments vs `instruments=[]`). This means "one engine formula, one code path" (guardrail 2) already holds for sector classification; the bug is a frontend routing/reuse defect, not a duplicated-formula defect.
- `SectorPieCard.tsx:47-62` — the ONLY place `sector_allocation`/`sector_position_breakdown` render as "Unclassified" — reads `exposureResult.overview.sector_allocation` first, falling back to `result.overview.sector_allocation`. Both currently trace back to the SAME lossy `exposure.overview` object inside `analyzeRestoredSnapshot`/`analyzeExposureSnapshot` (both compose functions do a pure `overview: exposure.overview` passthrough — confirmed in `portfolioAnalysisAdapter.ts` lines 215-248, 462-488, 499-504). Fixing `.overview` alone, at the point it is about to be consumed, is therefore sufficient to close the reported symptom — no need to touch `lookthrough`/`market_overlap`/etc. for THIS bug.
- `ImportedBootstrapResponse` does NOT carry the full `ExposureResult` (no `lookthrough`, `market_overlap`, `current_state_concentration`, `currency_exposure`, `availability`) — only `.overview` and a stub `.risk_summary` (import_engine.py:34-45, all nulled fields). This rules out any design that tries to fully replace the exposure/diagnostics call with the analyze-upload response; those other fields still must come from `runExposureEngine`/diagnostics, on every path, always.

## Reuse

- `getDirectNodeImportSource` / `getEffectiveNodeImportSource` (App.tsx:85-117) — existing helpers, unchanged, reused as the lookup mechanism. Use the DIRECT variant only (see decisions).
- `buildPersistedImportedSource` / `sanitizeImportedNodeSource` (portfolioWorkspaceStorage.ts:9-46) — existing constructors for `ImportedNodeSource`, extended with one new optional field, following the exact pattern already used for `admissionSummary` (optional, `!== undefined` guard, `structuredClone` on read).
- `PortfolioOverview` TS type (types.ts:51) — already the mirror of the backend schema; reused as-is, no new type.
- `composeExposureView`, `composeDashboardAnalysisFromEngines`, `composeDashboardAnalysisWithHistory`, `buildPortfolioBaselineView` (portfolioAnalysisAdapter.ts) — all four already do a pure `overview: exposure.overview` (or `analysis.overview`) passthrough. Untouched; a single override of the `exposure.overview` field before it reaches these functions is sufficient because all four are downstream of that one object.

## Lanes

### T1 — frontend-engineer: persist and reuse the correctly-classified overview

**Files:**
- `apps/desktop/src/features/portfolio/workspaceTypes.ts` — import `PortfolioOverview` from `./types`; add `importedOverview?: PortfolioOverview | null` to `ImportedNodeSource` (line ~72-79).
- `apps/desktop/src/app/portfolioWorkspaceStorage.ts`:
  - `buildPersistedImportedSource` (line 9-32): add `importedOverview?: PortfolioOverview | null` to its input type; assign `source.importedOverview = input.importedOverview` guarded by `if (input.importedOverview !== undefined)`, matching the existing `admissionSummary` pattern exactly.
  - `sanitizeImportedNodeSource` (line 34-46): add the matching read-side passthrough — `if (value.importedOverview !== undefined) { source.importedOverview = structuredClone(value.importedOverview) }`.
  - `createWorkspaceFromImport` (line 88-116): in its call to `buildPersistedImportedSource(...)` (line 107-115), add `importedOverview: input.analysis.overview`. `input.analysis: ImportedPortfolioSnapshotSource` already carries `.overview` — no new parameter needed on `createWorkspaceFromImport` itself.
  - `saveImportedSnapshotNode` (line 286-335): **no change** — its call to `buildPersistedImportedSource` (line 303-311) deliberately does NOT pass `importedOverview`, leaving it `undefined`/absent. This is the add_snapshot exclusion — see risks.
- `apps/desktop/src/app/App.tsx`:
  - Add `PortfolioOverview` to the type import list at line 11.
  - `analyzeRestoredSnapshot` (line 536-591): add a 5th parameter `importedOverview: import('../features/portfolio/types').PortfolioOverview | null` (or import the name directly). Immediately after `const exposure = await runExposureEngine(snapshot)` (line 565), replace its use with:
    ```ts
    const rawExposure = await runExposureEngine(snapshot)
    const exposure = importedOverview ? { ...rawExposure, overview: importedOverview } : rawExposure
    ```
    Every downstream use in this function (`composeExposureView(exposure, ...)`, `composeDashboardAnalysisWithHistory(exposure, ...)`, `composeDashboardAnalysisFromEngines(exposure, ...)`, `buildPortfolioBaselineView(exposure)`) is unchanged — they already consume `exposure` by reference.
  - `restoreImportedWorkspaceFromPersistedState` (line 341-465): at the call to `analyzeRestoredSnapshot(...)` (line 431-436), compute and pass a 5th argument:
    ```ts
    const importedOverview = resolvedSnapshot.id !== 'draft' ? (selectedDirectSource?.importedOverview ?? null) : null
    ```
    `selectedDirectSource` is already computed at line 430 — no new lookup.
  - `analyzeExposureSnapshot` (line 467-509): add `importedOverview?: PortfolioOverview | null` to its `options` parameter. Apply the identical override pattern (`rawExposure` → `exposure`) right after `const [exposure, diagnostics] = await Promise.all([runExposureEngine(snapshot), ...])` — restructure to `const [rawExposure, diagnostics] = await Promise.all([...])` then the same override line.
  - `handleExposureSnapshotChange` (line 511-534): the `snapshotId === 'draft'` branch (513-523) passes `importedOverview: null` explicitly. The node branch (526-533) passes `importedOverview: directNodeSource?.importedOverview ?? null` — `directNodeSource` is already computed at line 529.

**Verification:** `cd apps/desktop && npx vitest run` and `npx tsc --noEmit` (per project.md commands) — full command set is `python scripts/run_all_tests.py`, but that is T1's own close-out verification, run by the lane per its own report.

### T2 — test-engineer: regression coverage

**Files:** `apps/desktop/src/app/App.test.tsx` (primary — exercises `processImportedFiles` → restore/switch flows) and/or `apps/desktop/src/app/portfolioWorkspaceStorage.test.ts` (for the `buildPersistedImportedSource`/`createWorkspaceFromImport` persistence itself). Fixture data: `apps/desktop/src/test/portfolioFixtures.ts` already has SBIO-shaped fixtures per the scout's note that `docs/IB2026.csv` (the golden statement) includes SBIO — check whether `dashboardGoldens.ts`/`portfolioFixtures.ts` already stub a `PortfolioOverview` with `sector_allocation` including an SBIO entry; reuse or extend rather than hand-rolling a new fixture.

**Coverage needed (test-engineer's call on exact test structure, this is the behavior to prove):**
1. Replace-mode import (`createWorkspaceFromImport` path): the persisted `workspace.source.importedOverview` equals the `analyze-upload` response's `.overview` verbatim.
2. Immediately after a replace-mode import, and again after a simulated session-restore of that same workspace (i.e., re-entering via `restoreImportedWorkspaceFromPersistedState` with `restoredSession: true`), the rendered `DashboardAnalysis.overview` and `ExposureAnalysis.overview` both equal the persisted `importedOverview` — NOT whatever a mocked/stubbed `runExposureEngine` would have returned for `.overview`. This is the key regression proof: stub `runExposureEngine` to return an `overview` with `sector_allocation: []`/`Unclassified` and assert the rendered result does NOT show that — it shows the persisted correct one instead.
3. add_snapshot mode: `saveImportedSnapshotNode`'s resulting node's `source.importedOverview` is `undefined`, and the rendered view for that node calls (or would call) `runExposureEngine` for its `.overview` — i.e., confirm the known gap stays a known, tested gap rather than an untested one. This test documents the residual limitation named in risks; it is expected to reflect current (unfixed for this case) behavior, not a false claim of full coverage.
4. Draft / snapshot-switching to `'draft'`: `importedOverview` is never applied even when the draft's base node has one — confirm `analyzeExposureSnapshot`'s draft branch and `analyzeRestoredSnapshot`'s draft branch both force `null`.
5. Snapshot-switching (`handleExposureSnapshotChange`) to a non-draft, replace-mode-imported root node reuses `importedOverview` the same way as restore does (same mechanism, different call site — one test asserting parity is enough, not full duplication of test 2).

**Verification:** `cd apps/desktop && npx vitest run`, then `python scripts/run_all_tests.py` as the final close-out gate (per project.md mechanical gates — no agent commits; the human runs this and commits).

## Decisions

- **`restoredSession` does NOT gate reuse, and should not.** The order's own framing (correctly) named session-restore as a case with "no fresh backend response to reuse" — true only if reuse depended on the in-memory `nextAnalysis` from the current call stack. This design persists `overview` to local storage at creation time instead, so a LATER session-restore of a replace-mode-imported, still-unedited node CAN reuse it — durably, across app restarts. The actual gate is: (a) the resolved snapshot is not `'draft'`, and (b) the resolved node's OWN (`getDirectNodeImportSource`, never the ancestor-walking `getEffectiveNodeImportSource`) import source carries a non-null `importedOverview`. This closes more of the bug's persistence than the order anticipated, using the same non-goal-respecting mechanism.
- **add_snapshot mode is explicitly out of scope**, not silently dropped. `saveImportedSnapshotNode`'s resulting `portfolioSnapshot` is `overlayImportedSnapshot(base, imported)` — a merge — while the fresh `nextAnalysis.overview` was computed for the newly-imported statement's positions alone (different totals, different weights, missing the base's sectors entirely). Substituting it directly would render silently wrong data, which is worse than today's honest (if unhelpful) "Unclassified." No mechanism in this ticket set touches that call site's `.overview` derivation; it keeps calling `runExposureEngine` exactly as today.
- **Only `.overview` is overridden, nothing else in the exposure result.** `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration`, `availability`, `currency_exposure` continue to come from the still-necessarily-called `runExposureEngine` on every path, including the "fixed" ones — those fields are not carried by `ImportedBootstrapResponse` at all, and adding them would be the contract change the human's direction avoids. See § Risk detail for the consequence (SBIO's ETF look-through classification remains wrong even where its sector label is now fixed).

## Risk detail

**Blast radius wider than sector.** `instruments=[]` zeroes both `sector` AND `asset_class` in registry.py's catch-all (registry.py:359-374, confirmed by reading it directly, not just scout's summary). So `build_lookthrough_exposure`'s `instrument.asset_class == "etf"` check (risk.py:626) also misfires for SBIO on every `runExposureEngine`-derived call — its look-through constituents and market-overlap contribution are silently wrong, not just its sector label. This ticket set fixes only `overview.sector_allocation`/`sector_position_breakdown` (the reported symptom, and the only field `SectorPieCard.tsx` reads). `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration` for SBIO remain wrong on every path that still calls `runExposureEngine` for those fields — which is every path, including the ones this ticket "fixes," because the override replaces only `.overview`. This is larger than, and separate from, the risk.py:612/1483 finding below. Flagging as a candidate follow-up for the human/producer; not designed here.

**add_snapshot mode is out of scope.** `saveImportedSnapshotNode`'s resulting `portfolioSnapshot` is `overlayImportedSnapshot(base, imported)` (App.tsx:768) — a merge of the existing workspace with the newly-imported statement. `nextAnalysis.overview` was computed server-side for the newly-imported statement's positions ALONE (different total market value, different weights, no entries for the base snapshot's pre-existing positions). Substituting it into the merged view would render silently wrong totals and weights — worse than today's honest-if-unhelpful "Unclassified." The order's own framing treated `processImportedFiles`'s two call sites (785 add_snapshot, 795 replace) as symmetric "fresh response available" cases; they are not, and this design corrects that. No mechanism in T1 touches `saveImportedSnapshotNode`'s `.overview` derivation — it keeps calling `runExposureEngine` exactly as today. A future ticket could close this by merging two already-correct `PortfolioOverview` objects client-side (summing per-sector market values, redividing by the new combined total) — bounded arithmetic recombination, no new backend call — but that is a new design, not scoped here.

**Client-side re-derivation rejected.** Considered computing `sector_allocation` directly from `PortfolioSnapshot.positions[].sector` + `.marketValue`, all already present on every persisted node, instead of persisting the backend's `overview` object. Rejected: it would duplicate the FX-to-base-currency conversion and weight arithmetic `overview.py` already implements (US-30.5a fixed exactly this class of bug — mixed-currency summing understated the portfolio by 4.33%), creating a second code path for the same metric. That is a BLOCKING finding under this project's own "no duplicated computation" / "one engine formula, one code path" guardrails (architecture.md, Integration review checklist #4). Reusing the server-computed `overview` object verbatim avoids this entirely — it is the same reason this design persists and replays a whole object rather than extracting and recombining its parts.

**risk.py:612/1483 deferred.** Per the order's own non-goal boundary (do not design a fix for this beyond stating include/defer), deferring. Rationale: unrelated code path (backend, not touched by this fix), currently confirmed harmless (only `.asset_class` read at those two call sites, not `.sector`), and fixing it now would pull `analytics/risk.py` — and therefore the quant-analyst gate — into what is otherwise a bounded, frontend-only fix. Trigger condition for revisiting: either call site's metadata use is extended to read `.sector`.

**Unverified mapper passthrough.** This design assumes `ImportedPortfolioSnapshotSource.overview` (consumed by `createWorkspaceFromImport` via `input.analysis.overview`) is exactly the same `PortfolioOverview` object `build_import_bootstrap_from_snapshot` attached to `ImportedBootstrapResponse`. Confirmed by reading `import_engine.py` and the `nextAnalysis`/`importedViews.workspace` call chain in `App.tsx`, but `projectImportedBootstrap` itself (`apps/desktop/src/features/portfolio/importedBootstrapMapper.ts`) was not opened in this pass. T1's frontend-engineer should confirm it does not remap or drop `.overview` before it reaches `importedViews.workspace`.
