REPORT 2026-09-30-import-critical-fixes/09
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/types.ts — PortfolioOverview totals and top_positions unrealized_pnl nullable, cost_basis_trust added (C2); ImportAdmissionRollup, ImportAdmissionConstituent and check/decision/trust aliases (C3); constituent_snapshots on ImportedBootstrapResponse; CombinedImportBootstrapRequest (C4)
  - apps/desktop/src/features/portfolio/workspaceTypes.ts — ImportedNodeSource gains importedConstituents and derivationVersion (C6)
  - apps/desktop/src/features/portfolio/portfolioAnalysisAdapter.ts — analyzeCombinedImport (POST /api/portfolios/import/analyze-combined, non-ok throws detail) replaces combineImportedSnapshots
  - apps/desktop/src/features/portfolio/portfolioSnapshot.ts — overlayImportedSnapshot deleted; normalizePortfolioSnapshot dedupes on symbol plus currency
  - apps/desktop/src/features/portfolio/ImportAdmissionReviewCard.tsx — renders summary.rollup: rule text, combined-snapshot labels, each constituent's title, labels and checks; top-level checks headed as combined snapshot checks; no rollup renders as before
  - apps/desktop/src/app/App.tsx — add branch calls analyzeCombinedImport over flat constituents; replace branch stamps importedConstituents and derivationVersion 1; failure restores prior exposure state and shows importError
  - apps/desktop/src/app/portfolioWorkspaceStorage.ts — buildPersistedImportedSource, sanitizeImportedNodeSource, createWorkspaceFromImport and saveImportedSnapshotNode carry importedConstituents and derivationVersion
  - no other src file rendered total_cost_basis, total_unrealized_pnl or top_positions unrealized_pnl; tsc found none to change

verification:
  command:   cd apps/desktop && npx tsc --noEmit; npx vitest run src/features/portfolio/ImportAdmissionReviewCard src/test/designSystem.audit; npx vitest run; python scripts/detect_deadcode.py --strict
  result:    PASS
  detail:    card plus audit: 2 files, 12 tests passed. tsc: only 11 errors, all in portfolioSnapshot.test.ts (overlayImportedSnapshot gone). Full vitest: 15 failed, 379 passed (394), 2 files failed, all expected-red. Dead-code strict clean. see § Verification detail

contract_notes:
  - docs/contracts/import-admission-fields.md must add rollup, constituent and combined_snapshot_* fields as mirrored in types.ts (T-46.3.5)
  - docs/contracts/imports-fields.md (to be created) must list importedConstituents and derivationVersion on ImportedNodeSource and analyze-combined as the only merge source (T-46.4.5)
  - portfolioSnapshot.test.ts overlay tests and the App.test.tsx combine-snapshots mocks now reference retired code and must be rewritten in T-3
  - docs/contracts/dashboard-fields.md § Combine Imported Snapshots: the desktop no longer calls combine-snapshots, its only in-app caller is gone
  - dashboardGoldens.ts overview blocks regenerate in H-1; the TS type now allows total_unrealized_pnl null and optional cost_basis_trust so the satisfies clause still holds

pack_corrections:
  - none

handoff:
  - Expected-red vitest, portfolioSnapshot.test.ts: nine overlayImportedSnapshot cases (three sequential overlays, no duplicate symbols, sourceFileNames, sums marketValue, sums quantity, null quantity as zero, both null keeps null, preserves sector, sums cash)
  - Expected-red vitest, App.test.tsx: adds a new imported snapshot node from Dashboard Add Statement; refreshes dashboard allocation and cards after adding a statement snapshot; add_snapshot combines base history (AC1, AC2); discloses degradation when combine-snapshots fails (AC3); sequential-add chain regression; leaves an add_snapshot node without an exposure override
  - Expected-red tsc: the 11 errors in portfolioSnapshot.test.ts only; no other file
  - T-3: mock POST /api/portfolios/import/analyze-combined in the add tests; assert the request body carries base constituents plus the new file and carried_admissions only for a base without importedConstituents
  - T-3: helper fixtures must stamp derivationVersion 1 on non-legacy sources so FE-2 does not re-derive them
  - T-3: falsifier — an analyze-combined mock response differing from any client sum, assert the UI shows the response
  - T-3: failure cases — analyze-combined 400, and a base with no stored imported_replay snapshot: no node saved, prior portfolio and exposure kept, importError shows the server detail or the no-history message
  - T-3: sanitizer round trip keeps importedConstituents and derivationVersion; normalizePortfolioSnapshot keeps two currencies of one symbol apart and sums same-currency rows
  - T-3: card tests with a rollup fixture (two statement constituents, one carried), no-rollup unchanged; labels appear once per constituent so use scoped queries by group aria-label
  - T-3: type-level test that PortfolioOverview.total_unrealized_pnl and top_positions unrealized_pnl accept null
  - FE-2: the App restore path and rederiveSavedNodes.ts are untouched; a legacy node has derivationVersion undefined and no importedConstituents
  - Add flow input shape: snapshots = base.importedConstituents ?? [base replay snapshot], then the upload's constituent_snapshots or its single snapshot

skill_calls:
  - ui-polish — called, before editing ImportAdmissionReviewCard.tsx; design-system audit test passes (5 tests)
  - mattpocock-skills:diagnosing-bugs — not called, no fix attempt failed

risks:
  - Deviation, order scope: processImportedFiles catch now restores the prior exposureAnalysis and factor model that the shared preamble nulls; without it a refused combine left the Exposure tab empty. Shared code outside the add and replace branches, tiny; revert if the fence is strict
  - A base with no importedConstituents and a null admissionSummary contributes no carried evidence, so its old label is not folded in; design wrote carried = [base.admissionSummary] without covering null. Stored single statements are unaffected since the base snapshot is itself an input
  - If restoreImportedWorkspaceFromPersistedState throws after the node is saved, the catch restores the prior exposure state over a newly saved node; failure after save is unchanged otherwise
  - A base with no stored imported_replay snapshot now refuses with an importError message of my wording (reverses the old adopt-the-new-file-alone path per design decision); wording for the human to review
  - A legacy base (no constituents) produces a new node with derivationVersion 1 but no importedConstituents; a later add treats it as one input plus carried admission, and a same-account statement then hits the backend chained-input guard and is refused
  - mergeHistoryContext is kept per design and now merges the base context with an already-combined response context; the result matches the combined response by construction but is not verified in a test
  - importedAt on an add node is taken from the newly uploaded snapshot as ordered; a multi-file add uses the combined upload's first statement time
  - Pack gap: frontend.md does not warn that no test is expected to stay green after retiring overlayImportedSnapshot, nor that knip fails on exported-but-unused types, so new exported types must be used by the card or adapter

## Orchestrator brief
- FE-1 built to 05-design C2, C3, C4, C6: mirrored types, analyzeCombinedImport, add and replace flows stamping importedConstituents and derivationVersion 1, card renders the engine roll-up.
- overlayImportedSnapshot and combineImportedSnapshots are deleted; normalizePortfolioSnapshot dedupes on symbol plus currency.
- A refused combine saves nothing and keeps the prior portfolio and Exposure state; importError shows the server detail.
- Null cost basis and unrealized P&L are typed nullable; no TSX renders them, so no render change was needed.
- Expected-red for T-3: 9 overlay tests and 6 App add-flow tests (15 failed, 379 passed); tsc errors are confined to portfolioSnapshot.test.ts.
- One scope deviation: the shared catch restores prior exposure state; see risks.
- Section Verification detail: exact counts.

## Verification detail

- tsc --noEmit: 11 errors, all src/features/portfolio/portfolioSnapshot.test.ts (TS2305 missing overlayImportedSnapshot export, ten TS7006 knock-ons). Zero errors in non-test files.
- npx vitest run src/features/portfolio/ImportAdmissionReviewCard src/test/designSystem.audit: Test Files 2 passed, Tests 12 passed (card 7, audit 5).
- npx vitest run (full): Test Files 2 failed, 41 passed (43); Tests 15 failed, 379 passed (394). Failures: 9 overlayImportedSnapshot, 6 App.test.tsx add-flow tests, all listed in handoff.
- python scripts/detect_deadcode.py --strict: ruff, vulture, knip clean.
- dashboardGoldens.ts unchanged; run_all_tests.py and reset_goldens not run, per order.
