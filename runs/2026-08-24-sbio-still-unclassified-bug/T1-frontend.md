REPORT 2026-08-24-sbio-still-unclassified-bug/T1
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/types.ts — added ImportedExposureOverride = Pick<ExposureEngineResponse, 6 fields>, per plan's exact spec
  - apps/desktop/src/features/portfolio/workspaceTypes.ts — ImportedNodeSource gains importedExposureOverride?: ImportedExposureOverride | null
  - apps/desktop/src/app/portfolioWorkspaceStorage.ts — buildPersistedImportedSource/sanitizeImportedNodeSource pass through the new field, admissionSummary-guard pattern
  - apps/desktop/src/app/portfolioWorkspaceStorage.ts — createWorkspaceFromImport populates all 6 override fields from input.analysis
  - apps/desktop/src/app/portfolioWorkspaceStorage.ts — saveImportedSnapshotNode left untouched (add_snapshot exclusion); diff has zero lines mentioning that function
  - apps/desktop/src/features/portfolio/importedBootstrapMapper.ts — projectImportedBootstrap forwards the 5 new fields into workspace, resolving T0's flagged tsc error
  - apps/desktop/src/app/App.tsx — analyzeRestoredSnapshot gains 5th param importedExposureOverride, overrides exposure via spread after runExposureEngine
  - apps/desktop/src/app/App.tsx — restoreImportedWorkspaceFromPersistedState computes importedExposureOverride from getDirectNodeImportSource, gated on snapshot id !== 'draft'
  - apps/desktop/src/app/App.tsx — analyzeExposureSnapshot's options gains importedExposureOverride, same override-after-fetch pattern
  - apps/desktop/src/app/App.tsx — handleExposureSnapshotChange passes null on draft branch, directNodeSource?.importedExposureOverride ?? null on node branch

verification:
  command:   cd apps/desktop && npx tsc --noEmit ; npx vitest run
  result:    PASS
  detail:    tsc: exactly 1 error remaining, portfolioFixtures.ts(1241,3) — confirmed T2's, not mine (per T0-backend.md handoff); importedBootstrapMapper.ts(36,5) resolved. vitest: 37 files, 331 tests, all passed, 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T2: portfolioFixtures.ts's ImportedBootstrapResponse fixture (~line 1241) needs the 5 new fields; this is the one remaining tsc error, pre-existing/expected per T0-backend.md.
  - T2: the gate is exactly (a) resolved snapshot id !== 'draft', AND (b) getDirectNodeImportSource(node, workspace)?.importedExposureOverride is non-null.
  - T2: getEffectiveNodeImportSource is never used for the override gate — only getDirectNodeImportSource is.
  - T2: saveImportedSnapshotNode was deliberately left unchanged — add_snapshot nodes always have importedExposureOverride undefined, the known unfixed gap (plan's T2 coverage point 3).
  - T2: draft branch of handleExposureSnapshotChange always passes importedExposureOverride: null explicitly, even when the base node has one — worth its own assertion (coverage point 4).

risks:
  - none
