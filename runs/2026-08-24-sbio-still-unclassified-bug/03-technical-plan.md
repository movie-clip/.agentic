REPORT 2026-08-24-sbio-still-unclassified-bug/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (design/planning artifact).

contract_notes:
  - ImportedBootstrapResponse (import_bootstrap.py) gains 5 required fields — see § Schema change, T0.
  - ImportedPortfolioSnapshotSource and ImportedBootstrapResponse (types.ts) must mirror the same 5 fields — see § Schema change, T0.
  - docs/contracts/exposure-fields.md needs a new subsection for the analyze-upload root source — see § Lanes, T0-docs.

pack_corrections:
  - none

handoff:
  - T0 (backend-engineer): add lookthrough/lookthrough_sector_exposure/market_overlap/current_state_concentration/availability to ImportedBootstrapResponse, forwarded from the already-computed exposure_result — see § Lanes, T0.
  - T0-docs (docs-engineer): document the widened ImportedBootstrapResponse in docs/contracts/exposure-fields.md — see § Lanes, T0-docs. Can run in parallel with T1, must land before close-out.
  - T1 (frontend-engineer): SUPERSEDES 02-technical-plan.md's T1 — implements the .overview mechanism AND the 5 new fields together, in one pass, at the same call sites — see § Lanes, T1 and § Decisions, "T1/T2 are superseded, not additive."
  - T2 (test-engineer): SUPERSEDES 02-technical-plan.md's T2 — same 5 coverage points, widened to assert all 6 overridden fields — see § Lanes, T2.
  - Sequence: T0 → T1 → T2, with T0-docs parallel to T1 (needs T0's shapes, does not block it). Do NOT dispatch 02's narrower T1/T2 separately — see § Decisions.

risks:
  - availability is included in the override though the order left it as "your call" — reasoned in § Decisions, "availability must travel with lookthrough/market_overlap."
  - run_metadata.source_status.lookthrough_resolution remains a residual, un-overridden trust-descriptor mismatch on the runExposureEngine path — see § Risk detail, "run_metadata is a smaller residual of the same class."
  - currency_exposure/fx-tier fields confirmed unaffected by the bug and excluded — see § Decisions, "currency/fx fields excluded."
  - This design changes T1's parameter shape (a typed override object instead of a bare PortfolioOverview) rather than adding 5 parallel parameters — a judgment call, reasoned in § Decisions, "one widened parameter, not five parallel ones."

## Orchestrator brief
- Confirmed by reading code directly: `build_exposure_result` (exposure_engine.py:71) already returns a full `ExposureResult` with lookthrough/lookthrough_sector_exposure/market_overlap/current_state_concentration/availability all computed; `import_engine.py:28-33` currently discards everything but `.overview`. No new engine call needed.
- Decision: add all 5 fields (not just the DoD's 4) to `ImportedBootstrapResponse` — `availability` must travel with `lookthrough`/`market_overlap` or its trust badge will describe the wrong (freshly re-derived, still-lossy) data. See § Decisions.
- Decision: `currency_exposure`/fx-tier fields excluded — confirmed unaffected by the `instruments=[]` bug (no `attach_snapshot_metadata` dependency). See § Decisions.
- Decision: this plan SUPERSEDES 02's T1/T2 scope rather than adding a T3 alongside them — same files, same functions, same lines; a separate later ticket would re-edit code T1 just wrote. See § Decisions, "T1/T2 are superseded, not additive."
- Lane split: T0 backend (schema, first) → T1 frontend (widened persist+reuse mechanism) → T2 test (widened coverage); T0-docs (contract doc) parallel to T1. See § Lanes.
- add_snapshot mode confirmed still out of scope, same reasoning as 02, gated by the same mechanism. See § Decisions, "add_snapshot exclusion carries over."
- Blocks dispatch: nothing technical; orchestrator must choose to route this plan's T1/T2 instead of 02's when dispatching.

---

# Technical plan

## Schema change, T0

**No new computation — exposing more of an already-computed object.** Confirmed by reading `import_engine.py:23-47` directly: `build_import_bootstrap_from_snapshot` calls `build_exposure_result(snapshot, benchmark_symbol, symbol_overrides)` (line 28) and gets back a full `ExposureResult` (exposure.py:101-118), which already carries `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration`, `availability`, `currency_exposure`, `fx_static_rate_currencies`, `fx_fallback_currencies`, `provenance`, `run_metadata` — all computed at line 28, all discarded except `.overview` (line 33) when building the `ImportedBootstrapResponse`. `compose_import_bootstrap_response` (import_engine_composer.py:7-19) is a pure field-by-field constructor with no logic to touch.

**Fields to add to `ImportedBootstrapResponse` (import_bootstrap.py:52-57):**
```python
lookthrough: LookThroughOverview
lookthrough_sector_exposure: list[LookThroughSectorExposure]
market_overlap: MarketOverlapSummary
current_state_concentration: ExposureCurrentStateConcentration
availability: ExposureAvailability
```
All non-optional — `build_exposure_result` always produces them, matching `ExposureResult`'s own non-optional typing for the same fields (exposure.py:106-110). New imports needed in `import_bootstrap.py`: `LookThroughOverview, LookThroughSectorExposure, MarketOverlapSummary` from `app.schemas.reconciliation` (already the source — confirmed reconciliation.py:113/140/169), `ExposureCurrentStateConcentration, ExposureAvailability` from `app.schemas.exposure`. No import cycle: `app.schemas.exposure` does not import `app.schemas.import_bootstrap` (confirmed by reading its import block — exposure.py:1-12).

**Fields deliberately NOT added** (see § Decisions for reasoning): `currency_exposure`, `fx_static_rate_currencies`, `fx_fallback_currencies`, `provenance`, `run_metadata`.

**Call-site changes:**
- `import_engine.py:23-47` (`build_import_bootstrap_from_snapshot`): pass the 5 new fields from the already-held `exposure_result` local variable through to `compose_import_bootstrap_response(...)` — `exposure_result.lookthrough`, `.lookthrough_sector_exposure`, `.market_overlap`, `.current_state_concentration`, `.availability`.
- `import_engine_composer.py:7-19` (`compose_import_bootstrap_response`): add the 5 fields as parameters, forwarded straight into the `ImportedBootstrapResponse(...)` constructor call — same pattern as `overview`, no branching.

**TS mirror (`apps/desktop/src/features/portfolio/types.ts`):**
- `ImportedBootstrapResponse` (line 1168-1174): add the same 5 fields, non-optional, using the TS types that already exist and already mirror the Pydantic ones 1:1 — `LookThroughOverview` (line 104), `LookThroughSectorExposure` (line 124), `MarketOverlapSummary` (line 130), `ExposureCurrentStateConcentration` (line 1219), `ExposureAvailability` (line 1205). No new TS types needed for the field values themselves.
- `ImportedPortfolioSnapshotSource` (line 1176-1182): add the same 5 fields, non-optional (mirrors `ImportedBootstrapResponse`'s required-ness — the existing `admission_summary?: ... | null` on this type is already looser than its backend counterpart, an existing asymmetry this plan does not touch or extend).

**`docs/contracts/exposure-fields.md`:** confirmed by reading the file (grep for "analyze-upload"/"ImportedBootstrapResponse"/"import_bootstrap" — no matches) that the analyze-upload → `ImportedBootstrapResponse` path is not documented as a root source at all today; only `runExposureEngine`'s `ExposureResult`-shaped path is (§ "Current Root Sources", lines 17-28). This is docs debt independent of this fix, but the schema addition makes it load-bearing: `docs-engineer` should add a short subsection naming `ImportedBootstrapResponse` as a second root that feeds the same 5 fields (plus `overview`), with the truth-class note that its values are computed once at import time and replayed (via T1's mechanism) rather than re-fetched on every render — distinct from `ExposureResult`'s own per-render truth class. This is what `schema_edit_reminder.py` will fire on after the `import_bootstrap.py` edit.

## Reuse

- `build_exposure_result` (exposure_engine.py:71) — unchanged, already called, already returns everything needed. No duplicate computation introduced.
- `compose_import_bootstrap_response` (import_engine_composer.py:7) — extended with more pass-through parameters, same pattern as `overview`/`risk_summary`/`admission_summary` today.
- `Pick`-style reuse on the frontend: rather than hand-declare a duplicate shape, the new override type is expressed against the fields `ExposureEngineResponse` (types.ts:1310-1330) already declares — see § Lanes, T1.
- `composeExposureView` (portfolioAnalysisAdapter.ts:215-247) — confirmed by reading it directly: it reads `exposure.lookthrough`, `.lookthrough_sector_exposure`, `.market_overlap`, `.current_state_concentration`, `.availability` (aliased to `exposure_availability`) straight off the `exposure: ExposureEngineResponse` argument it is passed, by reference, field by field. No changes needed to this function — overriding the fields on the `exposure` object *before* this function is called (mirroring T1's `.overview` override) is sufficient, exactly as T1 already established for `.overview`.
- `buildPortfolioBaselineView` (portfolioAnalysisAdapter.ts:499-504) and `composeDashboardAnalysisFromEngines`/`composeDashboardAnalysisWithHistory` — confirmed by reading them: all three read only `.snapshot` and `.overview`, never `.lookthrough`/`.market_overlap`/etc. The Dashboard tab and `PortfolioBaselineView` do not need any part of this extension — do not touch them.

## Lanes

### T0 — backend-engineer: widen `ImportedBootstrapResponse`

**Files:**
- `services/quant-engine/app/schemas/import_bootstrap.py` — add the 5 fields to `ImportedBootstrapResponse` (line 52-57) and the corresponding imports, per § Schema change.
- `services/quant-engine/app/services/import_engine.py` — pass the 5 fields from `exposure_result` into `compose_import_bootstrap_response(...)` (line 31-47).
- `services/quant-engine/app/services/import_engine_composer.py` — accept and forward the 5 new parameters (line 7-19).

**Non-goals for T0:** do not touch `runExposureEngine`'s route or `ExposureResult` itself — that schema is unchanged, only what `ImportedBootstrapResponse` forwards from it changes. Do not touch `analytics/risk.py` (registry catch-all, `instruments=[]` root cause) — unchanged from 02's deferral.

**Verification:** `cd services/quant-engine && pytest` (existing `import_bootstrap`/`import_engine` tests must still pass with the wider response; T0 does not need to add new backend tests beyond keeping existing serialization tests green — new regression coverage for the *frontend* reuse behavior is T2's job, not T0's).

### T0-docs — docs-engineer: contract doc

**Files:** `docs/contracts/exposure-fields.md` — add the analyze-upload/`ImportedBootstrapResponse` root-source subsection per § Schema change's last paragraph.

**Sequencing:** depends on T0 (needs the final field list/shapes); does not block T1 — the frontend lane works from this plan's field list directly, not from the doc. Should land before the human commits the slice (schema hook reminder), not necessarily before T1 starts.

**Verification:** NONE (docs-only; no code to run).

### T1 — frontend-engineer: persist and reuse `.overview` AND the 4 exposure fields together

**This supersedes 02-technical-plan.md's T1 entirely — implement this version, not that one.** Same mechanism, same gate, same call sites T1 already named; widened to carry more of the exposure_result. See § Decisions for why this is one ticket, not two.

**New TS type** (`apps/desktop/src/features/portfolio/types.ts`, near `ExposureEngineResponse` at line 1310):
```ts
export type ImportedExposureOverride = Pick<
  ExposureEngineResponse,
  'overview' | 'lookthrough' | 'lookthrough_sector_exposure' | 'market_overlap' | 'current_state_concentration' | 'availability'
>
```
Expressed as a `Pick` off the type that already mirrors `ExposureResult` 1:1, so it cannot silently drift from the shape `runExposureEngine` actually returns.

**Files and changes:**
- `apps/desktop/src/features/portfolio/workspaceTypes.ts` — import `ImportedExposureOverride` from `./types`; add ONE field to `ImportedNodeSource` (line ~72-79): `importedExposureOverride?: ImportedExposureOverride | null`. (This replaces 02's `importedOverview?: PortfolioOverview | null` — do not add both; see § Decisions, "one widened parameter, not five parallel ones.")
- `apps/desktop/src/app/portfolioWorkspaceStorage.ts`:
  - `buildPersistedImportedSource` (line 9-32): add `importedExposureOverride?: ImportedExposureOverride | null` to its input type; assign guarded by `if (input.importedExposureOverride !== undefined)`, matching the existing `admissionSummary` pattern exactly (line 28-30).
  - `sanitizeImportedNodeSource` (line 34-46): matching read-side passthrough — `if (value.importedExposureOverride !== undefined) { source.importedExposureOverride = structuredClone(value.importedExposureOverride) }`.
  - `createWorkspaceFromImport` (line 88-116): in its `buildPersistedImportedSource(...)` call (line 107-115), add:
    ```ts
    importedExposureOverride: {
      overview: input.analysis.overview,
      lookthrough: input.analysis.lookthrough,
      lookthrough_sector_exposure: input.analysis.lookthrough_sector_exposure,
      market_overlap: input.analysis.market_overlap,
      current_state_concentration: input.analysis.current_state_concentration,
      availability: input.analysis.availability,
    },
    ```
    `input.analysis: ImportedPortfolioSnapshotSource` carries all 6 fields once T0's TS mirror lands (§ Schema change).
  - `saveImportedSnapshotNode` (line 286-335): **no change** — its `buildPersistedImportedSource` call (line 303-311) deliberately omits `importedExposureOverride`, leaving it `undefined`. This is the add_snapshot exclusion, unchanged from 02 — see § Decisions, "add_snapshot exclusion carries over."
- `apps/desktop/src/features/portfolio/importedBootstrapMapper.ts` — **new file for this scope, not touched by 02's T1.** `projectImportedBootstrap` (line 34-45) currently builds `workspace: ImportedPortfolioSnapshotSource` field-by-field (`snapshot`, `overview`, `risk_summary`, `admission_summary`, `benchmark: null`) from `bootstrap: ImportedBootstrapResponse` — confirmed by reading it directly, resolving 02's "unverified mapper passthrough" risk for `.overview` (it does pass through unchanged) but the function does NOT yet forward the 4 new fields, because they don't exist on `ImportedBootstrapResponse` today. Add them to the returned `workspace` object: `lookthrough: bootstrap.lookthrough`, `lookthrough_sector_exposure: bootstrap.lookthrough_sector_exposure`, `market_overlap: bootstrap.market_overlap`, `current_state_concentration: bootstrap.current_state_concentration`, `availability: bootstrap.availability`.
- `apps/desktop/src/app/App.tsx`:
  - Add `ImportedExposureOverride` to the type import list at line 11.
  - `analyzeRestoredSnapshot` (line 536-591): add a 5th parameter `importedExposureOverride: import('../features/portfolio/types').ImportedExposureOverride | null`. Immediately after `const exposure = await runExposureEngine(snapshot)` (line 565), replace its use with:
    ```ts
    const rawExposure = await runExposureEngine(snapshot)
    const exposure = importedExposureOverride ? { ...rawExposure, ...importedExposureOverride } : rawExposure
    ```
    Every downstream use in this function (`composeExposureView(exposure, ...)` line 567, `composeDashboardAnalysisWithHistory(exposure, ...)` / `composeDashboardAnalysisFromEngines(exposure, diagnostics)` line 574-576, `buildPortfolioBaselineView(exposure)` line 577) is unchanged — they consume `exposure` by reference, and `buildPortfolioBaselineView` only reads `.snapshot`/`.overview` off it (confirmed — see § Reuse), so the wider spread does not change its behavior.
  - `restoreImportedWorkspaceFromPersistedState` (line 341-465): at the `analyzeRestoredSnapshot(...)` call (line 431-436), compute and pass the 5th argument:
    ```ts
    const importedExposureOverride = resolvedSnapshot.id !== 'draft' ? (selectedDirectSource?.importedExposureOverride ?? null) : null
    ```
    `selectedDirectSource` is already computed at line 430 (`getDirectNodeImportSource`) — no new lookup.
  - `analyzeExposureSnapshot` (line 467-509): add `importedExposureOverride?: ImportedExposureOverride | null` to its `options` parameter. Restructure `const [exposure, diagnostics] = await Promise.all([runExposureEngine(snapshot), ...])` (line 480-485) to `const [rawExposure, diagnostics] = await Promise.all([...])`, then apply the identical override line.
  - `handleExposureSnapshotChange` (line 511-534): the `snapshotId === 'draft'` branch (513-523) passes `importedExposureOverride: null` explicitly. The node branch (526-533) passes `importedExposureOverride: directNodeSource?.importedExposureOverride ?? null` — `directNodeSource` is already computed at line 529.

**Gate, unchanged from 02:** the resolved snapshot is not `'draft'`, AND the resolved node's OWN (`getDirectNodeImportSource`, never `getEffectiveNodeImportSource`) import source carries a non-null `importedExposureOverride`. `restoredSession` does not gate reuse — same reasoning as 02: this is durable local storage, not in-memory call-stack state.

**Verification:** `cd apps/desktop && npx vitest run` and `npx tsc --noEmit`; full close-out gate is `python scripts/run_all_tests.py`, run by the lane per its own report (per project.md commands).

### T2 — test-engineer: widened regression coverage

**This supersedes 02-technical-plan.md's T2 — same 5 coverage points, widened to assert all 6 fields of `ImportedExposureOverride`, not just `.overview`.**

**Files:** `apps/desktop/src/app/App.test.tsx` (primary) and/or `apps/desktop/src/app/portfolioWorkspaceStorage.test.ts` (persistence). Fixtures: check `apps/desktop/src/test/portfolioFixtures.ts`/`dashboardGoldens.ts` for an existing SBIO-shaped `ExposureResult`/`ImportedBootstrapResponse` stub with non-trivial `lookthrough`/`market_overlap` values before hand-rolling one.

**Coverage needed (test-engineer's call on structure; this is the behavior to prove):**
1. Replace-mode import: the persisted `workspace.source.importedExposureOverride` equals `{overview, lookthrough, lookthrough_sector_exposure, market_overlap, current_state_concentration, availability}` from the `analyze-upload` response, verbatim, for all 6 fields.
2. Immediately after a replace-mode import, and again after a simulated session-restore (`restoredSession: true`), the rendered `ExposureAnalysis`'s `overview`, `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration`, and `exposure_availability` all equal the persisted override — NOT whatever a mocked `runExposureEngine` would return. Stub `runExposureEngine` to return SBIO as `asset_class: 'other'`/`sector: null` (mirroring the real lossy path) with a correspondingly degraded `lookthrough`/`market_overlap`, and assert the rendered result shows the persisted correct data instead on all 6 fields — this is the key regression proof, and it also proves `availability` doesn't end up describing the stale data (see § Decisions).
3. add_snapshot mode: `saveImportedSnapshotNode`'s resulting node's `source.importedExposureOverride` is `undefined`, and the rendered view for that node reflects the un-overridden (still-lossy for SBIO) `runExposureEngine` output on all 6 fields — documents the known, unfixed gap, not a false claim of coverage.
4. Draft / snapshot-switching to `'draft'`: `importedExposureOverride` is never applied even when the draft's base node has one — both `analyzeRestoredSnapshot`'s and `analyzeExposureSnapshot`'s draft branches force `null`.
5. Snapshot-switching (`handleExposureSnapshotChange`) to a non-draft, replace-mode-imported root node reuses `importedExposureOverride` the same way restore does — one parity test, not full duplication of test 2.

**Verification:** `cd apps/desktop && npx vitest run`, then `python scripts/run_all_tests.py` as the final close-out gate — no agent commits; the human runs this and commits.

## Decisions

- **`availability` must travel with `lookthrough`/`market_overlap`, so it is added even though the order left it as "your call."** Confirmed by reading `_build_exposure_availability` (exposure_engine.py:165-215): it is computed FROM `lookthrough_constituents`/`uncovered_positions`/`benchmark_holdings` — the exact same inputs that produce `lookthrough`/`market_overlap`. If those two are overridden with the correct, persisted values but `availability` is left to be freshly recomputed on the still-lossy `runExposureEngine` path, the trust badge would describe data that is no longer what's rendered next to it (e.g. a `partial`/`medium` badge sitting beside a fully-resolved look-through table) — a direct instance of guardrail 4 ("trust semantics over fabrication... surface the level") being violated by omission, not by design. Including it costs nothing extra (same object, same gate).
- **`currency_exposure`, `fx_static_rate_currencies`, `fx_fallback_currencies` are excluded.** Confirmed by reading `currency_exposure.py` and `currency.py` directly: neither references `registry.attach_snapshot_metadata` or `asset_class` at all — they derive purely from `position.currency` and the snapshot's FX rates. Not affected by the `instruments=[]` bug, so they are already correct on every render via `runExposureEngine`; persisting them would add schema surface for no behavioral gain.
- **`provenance` and `run_metadata` are excluded**, per the order's own DoD scope (it names only the 4 fields plus explicitly leaves `availability`/`currency_exposure`/fx-tier as a judgment call — `provenance`/`run_metadata` were never in scope). `run_metadata.source_status.lookthrough_resolution` has the identical trust-descriptor coupling problem `availability` has (see § Risk detail) but is a broader object also carrying legitimately per-render fields (`reproducibility.snapshot_as_of_date`, `dataset_version`); pulling it in is a larger, separate design not exercised here.
- **T1/T2 are superseded, not additive.** 02's T1 and this plan's T1 touch the identical files, functions, and lines (`analyzeRestoredSnapshot`, `restoreImportedWorkspaceFromPersistedState`, `analyzeExposureSnapshot`, `handleExposureSnapshotChange`, `buildPersistedImportedSource`, `sanitizeImportedNodeSource`, `createWorkspaceFromImport`). 02's T1 has not been dispatched yet. Dispatching it first and then a second ticket to widen the same lines is pure rework — the second lane re-edits code the first lane just wrote, and risks a diff-ordering conflict if T3 is dispatched before T1's diff lands. The orchestrator should dispatch this plan's T1 (which implements the union of both) instead of 02's narrower T1, and likewise this plan's T2 instead of 02's T2.
- **One widened parameter, not five parallel ones.** Rather than adding `importedOverview`, `importedLookthrough`, `importedLookthroughSectorExposure`, `importedMarketOverlap`, `importedCurrentStateConcentration`, `importedExposureAvailability` as six independent optional fields/parameters (which would force every call site to thread six variables that must always be set or unset together, since they all originate from one `exposure_result` at one import instant), this design uses one `ImportedExposureOverride` object carrying all 6. They are never independently valid — `overview` without `lookthrough` would be exactly the same class of trust-mismatch bug as `lookthrough` without `availability` (see above). Bundling makes that invariant structural instead of a convention six call sites have to individually honor. This changes the *shape* of what 02 called `importedOverview: PortfolioOverview | null`, but not the decision `.overview` reuse encoded (the gate, the durability, the add_snapshot exclusion) — the non-goal against re-litigating T1 is read as protecting that decision, not the literal parameter type of a not-yet-dispatched ticket.
- **`restoredSession` does not gate reuse — carries over unchanged from 02.** Same reasoning: this design persists at creation time to durable local storage, so a later session-restore can still reuse it. The gate remains (a) resolved snapshot is not `'draft'`, (b) the resolved node's direct import source carries a non-null override.
- **add_snapshot exclusion carries over unchanged from 02.** `saveImportedSnapshotNode`'s resulting snapshot is a merge (`overlayImportedSnapshot`); the fresh `exposure_result` at import time was computed for the newly-imported statement's positions alone. Substituting any of the 6 fields (not just `.overview`) into the merged view would render silently wrong totals/weights/look-through for the combined portfolio — worse than today's honest "Unclassified." No mechanism here touches `saveImportedSnapshotNode`'s derivation.

## Risk detail

**run_metadata is a smaller residual of the same class.** `run_metadata.source_status.lookthrough_resolution` and `run_metadata.confidence` (exposure_engine.py:79-91, `_build_exposure_source_status`/`_combine_exposure_confidence`) are computed from the same `lookthrough_constituents`/`uncovered_positions`/`benchmark_holdings` as `availability`, so they have the identical potential to describe stale data once `lookthrough` is overridden but `run_metadata` is not. Deliberately out of scope here (not named in the order's DoD, and `run_metadata` also carries legitimately per-render fields like `reproducibility.snapshot_as_of_date` that should NOT be frozen at import time). Flagging as a candidate follow-up for the human/producer, same posture 02 took on the wider blast radius before this ticket closed part of it.

**This plan closes the blast-radius risk 02 flagged, for the fields 02 named, but not completely.** 02's "Blast radius wider than sector" risk named `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration` as unfixed; this plan closes all 4 (plus `availability`) for the analyze-upload/replace-import/session-restore/snapshot-switch paths. It does NOT close: add_snapshot mode (unchanged non-goal), the `run_metadata` residual above, or `risk.py:612`/`risk.py:1483` (deferred by 02, unchanged — those call sites still only read `.asset_class`, not `.sector`, so still harmless for this specific symptom).

**Mapper passthrough risk from 02 is resolved for `.overview`, open for the new fields until T1 lands.** Read `importedBootstrapMapper.ts` directly (02 had not): `projectImportedBootstrap` does forward `bootstrap.overview` unchanged into `workspace.overview` — 02's "unverified mapper passthrough" risk is closed for that field. It does not yet forward the 4-5 new fields, because they don't exist on `ImportedBootstrapResponse` until T0 lands; T1 must add them to this same function (see § Lanes, T1) or the new backend fields will be silently dropped before reaching workspace storage — the exact Epic 25 failure mode `composeExposureView`'s own comment (portfolioAnalysisAdapter.ts:227-229) warns about.
