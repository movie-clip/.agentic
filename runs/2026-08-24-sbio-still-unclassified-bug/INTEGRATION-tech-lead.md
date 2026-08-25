REPORT 2026-08-24-sbio-still-unclassified-bug/INTEGRATION
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd /c/projects/investments/portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    backend 905 passed; frontend 38 files / 341 tests passed; dead-code gate (ruff+vulture+knip) clean; tsc --noEmit clean; dashboardGoldens.ts unmodified (git status confirmed after regen). Re-run myself, not just trusted lane reports.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - T0(PARTIAL/FAIL) vs T1(DONE/PASS) reported the same by-design interim tsc breakage differently — already logged OPEN in run.md, not a code defect, no action needed here.

## Orchestrator brief
- Verdict: PASS. All 6 DoD items verified directly against code/diffs, not just lane self-reports.
- T0/T0-docs/T1/T2 landed exactly per 03-technical-plan.md: schema/composer/engine diffs, TS mirrors, `ImportedExposureOverride` Pick type, all call-site wiring in App.tsx/portfolioWorkspaceStorage.ts/importedBootstrapMapper.ts match the plan's named files/lines. See § Contract alignment.
- No trace of 02's superseded design: `importedOverview` does not appear anywhere in apps/desktop/src (grepped). See § Superseded-design check.
- CR-1 closes AUDIT Finding 1: `getBenchmarkTrust` (BenchmarkPositioningCard.tsx:37-45) now reads only `exposure_availability.benchmark_overlap_status`/`.benchmark_overlap_confidence`; repo-wide grep confirms no other production code reads `run_metadata.source_status.benchmark_holdings` for trust purposes. See § Finding 1 closure.
- CR-1's self-disclosed test-writing conflict: content reviewed directly (BenchmarkPositioningCard.test.tsx, DashboardPanel.test.tsx diff) — correctly scoped, tests the contract (single-vintage derivation) not the implementation, appropriately placed alongside the component. See § Test content review.
- No duplicated logic: `ImportedExposureOverride` stays in sync with `ExposureEngineResponse` by construction (Pick-based); no FUND_CATEGORY_OVERRIDE-style hand-duplicated shape found anywhere in this diff.
- Both deliberate exclusions verified accurate: add_snapshot (`saveImportedSnapshotNode`) untouched, confirmed by direct read; Finding 2 (staleness disclosure) untouched, confirmed OPEN/CARRIED in run.md, no silent partial build.
- `docs/contracts/exposure-fields.md`'s new subsection (T0-docs) verified accurate against final landed schema; CR-1 did not change any backend-contract-visible surface, so no update was needed there.
- `run_all_tests.py` re-run by me end-to-end: green. Full detail in verification above.
- No BLOCKING or SHOULD_FIX change requests. One informational note in risks (self-reporting style inconsistency, already tracked, not actionable as a code fix).

---

## Contract alignment

**Backend schema (`import_bootstrap.py`).** `git diff` shows exactly the plan's spec: `lookthrough: LookThroughOverview`, `lookthrough_sector_exposure: list[LookThroughSectorExposure]`, `market_overlap: MarketOverlapSummary`, `current_state_concentration: ExposureCurrentStateConcentration`, `availability: ExposureAvailability` added to `ImportedBootstrapResponse`, all non-optional, imports from `app.schemas.reconciliation` and `app.schemas.exposure` exactly as planned. `import_engine.py` passes all 5 from the already-held `exposure_result` local; `import_engine_composer.py` accepts and forwards them unconditionally, matching the `overview` pattern. No new computation introduced — confirmed by reading both files' diffs directly.

**TS mirror (`types.ts`).** Both `ImportedBootstrapResponse` and `ImportedPortfolioSnapshotSource` gained the identical 5 fields, non-optional, using the pre-existing TS types (`LookThroughOverview`, `LookThroughSectorExposure`, `MarketOverlapSummary`, `ExposureCurrentStateConcentration`, `ExposureAvailability`) — spot-checked `ExposureAvailability`/`ExposureCurrentStateConcentration`'s TS shape field-by-field against the Pydantic source; identical field names, nullability, and enum members. No new TS types needed, per plan.

**`ImportedExposureOverride`.** Declared exactly as `Pick<ExposureEngineResponse, 'overview' | 'lookthrough' | 'lookthrough_sector_exposure' | 'market_overlap' | 'current_state_concentration' | 'availability'>` at types.ts:1339 — this is the one widened parameter the plan called for (not 5-6 parallel optional fields). `workspaceTypes.ts`'s `ImportedNodeSource` gained exactly one new optional field, `importedExposureOverride?: ImportedExposureOverride | null`.

**Call sites in `portfolioWorkspaceStorage.ts`.** `buildPersistedImportedSource` and `sanitizeImportedNodeSource` both use the identical `!== undefined` guard pattern the plan specified (matching the existing `admissionSummary` convention). `createWorkspaceFromImport` populates all 6 override fields from `input.analysis` verbatim. `saveImportedSnapshotNode` — read directly — has zero references to `importedExposureOverride`; its `buildPersistedImportedSource` call does not set it, so it stays `undefined` on add_snapshot nodes, exactly the plan's add_snapshot exclusion.

**`importedBootstrapMapper.ts`.** `projectImportedBootstrap` forwards all 5 new fields into the returned `workspace` object — this was the file T0 flagged as a tsc failure (by-design interim state) and T1 closed it exactly as instructed.

**`App.tsx`.** All four call sites match the plan verbatim: `analyzeRestoredSnapshot` gains a 5th param and overrides via `{ ...rawExposure, ...importedExposureOverride }`; `restoreImportedWorkspaceFromPersistedState` computes the override from `selectedDirectSource` (never `selectedSource`/Effective) gated on `resolvedSnapshot.id !== 'draft'`; `analyzeExposureSnapshot`'s `options` gains the field with the identical override-after-fetch pattern; `handleExposureSnapshotChange`'s draft branch passes `importedExposureOverride: null` explicitly, its node branch passes `directNodeSource?.importedExposureOverride ?? null`. The gate is exactly (a) not `'draft'`, (b) direct (not effective) node source carries a non-null override — confirmed by reading the diff, matching T1's own handoff notes.

## Superseded-design check

`grep -rn "importedOverview" apps/desktop/src` returns zero matches. No trace of 02-technical-plan.md's narrower `importedOverview?: PortfolioOverview | null` design anywhere in the landed diff — 03 fully superseded it as intended, one bundled `ImportedExposureOverride`, not six parallel fields.

## Finding 1 closure

Read `BenchmarkPositioningCard.tsx` directly (post-CR-1). `getBenchmarkTrust` (lines 37-45):
```ts
function getBenchmarkTrust(result: ExposureAnalysis): BenchmarkTrust {
  const overlapStatus = result.exposure_availability?.benchmark_overlap_status ?? 'unavailable'
  if (overlapStatus === 'unavailable') return 'unavailable'
  if (overlapStatus === 'partial') return 'partial'
  const confidence = result.exposure_availability?.benchmark_overlap_confidence ?? 'low'
  if (confidence === 'high') return 'verified'
  if (confidence === 'medium') return 'degraded'
  return 'unavailable'
}
```
No reference to `run_metadata` anywhere in this function — the live cross-read AUDIT Finding 1 identified is gone. `buildBenchmarkState` (line 76-104) still reads `result.run_metadata?.reproducibility?.benchmark_symbol` at line 80, but only as a display-name fallback (`benchmarkSymbol`), never for trust classification — CR-1's own report calls this out explicitly and it is correct: this is the "expected: drop the run_metadata.source_status.benchmark_holdings branch... derive verified/degraded purely from availability.benchmark_overlap_confidence" option AUDIT named, applied exactly.

Repo-wide grep (`benchmark_holdings`, `source_status`) confirms: the only production reference to `benchmark_holdings` for trust purposes was the now-removed one in `getBenchmarkTrust`; no other card/component derives a trust badge from it. `DashboardPanel.test.tsx`'s one affected test was updated in the same pass to set `exposure_availability.benchmark_overlap_confidence` instead of the old `run_metadata` field, same assertion, correctly described as a mechanical consequence of the fix (not scope creep) — confirmed by reading the diff.

## Test content review

`BenchmarkPositioningCard.test.tsx` (new file, CR-1): 4 tests under "single-vintage derivation" — each deliberately sets `run_metadata.source_status.benchmark_holdings` to a value that *disagrees* with `exposure_availability`, and asserts the rendered badge text follows `availability` alone in all 4 branches (verified/degraded/partial/unavailable). This tests the contract (badge vintage consistency), not the implementation — it would still pass if `getBenchmarkTrust`'s internal structure changed, but would fail if a future edit reintroduced a live-data cross-read. Correctly placed next to the component, following the project's existing per-component test-file convention (matches `DashboardPanel.test.tsx`, `IndexedReturnChart.test.tsx`, etc. in the same directory).

The order-vs-pack conflict CR-1 flagged (frontend-engineer wrote/extended tests, violating "no test files touched — that is the test lane") is real per `frontend.md`'s DoD checklist, but is explicitly out of this review's re-dispatch scope per the work order ("orchestrator's own mistake in the CR's scope, already noted in the ledger, not something to re-dispatch"). Confirmed the ledger's `run.md` already carries this as an OPEN protocol_note. My own check is limited, per the order, to whether the test content itself is correct and appropriately placed — it is.

## Deliberate exclusions

**add_snapshot mode stays broken.** `saveImportedSnapshotNode` (portfolioWorkspaceStorage.ts:301-335) — read directly — has no `importedExposureOverride` in its input type or its `buildPersistedImportedSource` call. T2's coverage point 3 test (`'leaves an add_snapshot node without an exposure override...'`) asserts `'importedExposureOverride' in savedNodeInput` is `false` and that the rendered view still shows `'Unclassified'` — this documents the gap rather than silently half-fixing it, matching the plan's non-goal.

**Finding 2 stays unbuilt.** `run.md`'s ledger shows Finding 2 status `CARRIED` with an explicit `human_decision` entry: "leave as accepted, tracked gap — not added to this run's scope." No UI change touching the snapshot-picker label, `DataSourcesPanel`, or a staleness marker appears anywhere in `git status`'s changed-file list. Confirmed no silent partial implementation exists.

## Contract doc accuracy after CR-1

`docs/contracts/exposure-fields.md`'s new item 3 (added by T0-docs) documents `ImportedBootstrapResponse` as a second root source carrying the 6 frozen-at-import fields, with the frozen-vs-per-render truth-class distinction — verified accurate against the final landed schema (§ Contract alignment above). CR-1 changed only frontend component logic (`BenchmarkPositioningCard.tsx`) and did not touch `app/schemas/`, `ImportedBootstrapResponse`, or any field this doc tracks, so no update to this doc was triggered or needed by CR-1. Confirmed by `git diff --stat -- docs/` showing only the T0-docs change, nothing from CR-1.
