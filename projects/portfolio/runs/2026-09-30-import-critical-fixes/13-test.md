REPORT 2026-09-30-import-critical-fixes/13
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/test/combinedImportFixtures.ts — NEW shared fixtures: pinned IB/ESPP/FF truths, engine-shaped responses, roll-up admissions, legacy saved-workspace builders and seeder
  - apps/desktop/src/test/fakePortfolioDb.ts — NEW: in-memory IndexedDB fake extracted from portfolioWorkspaceStorage.test.ts, plus write recording, seed and read
  - apps/desktop/src/test/fetchHarness.ts — NEW: jsonResponse, requestPathname, requestMethod, requestJsonBody, matchingFetchCalls, installFetchMock, unhandledOrDrift extracted unchanged from App.test.tsx
  - apps/desktop/src/app/App.combinedImport.test.tsx — NEW: 21 App-level tests on real storage over the fake DB (add flow, falsifier, refused combines, legacy re-derive on load)
  - apps/desktop/src/app/rederiveSavedNodes.test.ts — NEW: 25 unit tests of the saved-node re-derive (ordering, carried lineage, failure paths, drafts, stability)
  - apps/desktop/src/features/portfolio/costBasisUnavailable.test.ts — NEW: type-level nullability, null survives projection and storage, no-coercion source guard
  - apps/desktop/src/app/App.test.tsx — six FE-1 reds rewritten to analyze-combined; buildImportedSource stamps derivationVersion 1 (legacy flag opts out); two new replace and multi-file tests
  - apps/desktop/src/features/portfolio/portfolioSnapshot.test.ts — nine overlay tests replaced by a retired-export guard and currency-aware dedupe tests
  - apps/desktop/src/features/portfolio/portfolioAnalysisAdapter.test.ts — six analyzeCombinedImport tests
  - apps/desktop/src/features/portfolio/ImportAdmissionReviewCard.test.tsx — ten roll-up rendering tests
  - apps/desktop/src/app/portfolioWorkspaceStorage.test.ts — local fake DB replaced by the shared one; six constituents, derivationVersion and roll-up round-trip tests

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run
  result:    PASS
  detail:    tsc clean. vitest: Test Files 46 passed (46); Tests 470 passed (470). Knip clean. dashboardGoldens.ts untouched. No remaining red, H-1 or otherwise.

contract_notes:
  - none

pack_corrections:
  - testing.md § Where things live — add src/test/combinedImportFixtures.ts, fakePortfolioDb.ts and fetchHarness.ts as the shared frontend scaffolding for App-level and storage tests
  - testing.md § Gotchas — add: a restore-path App test can use real storage over createFakePortfolioDb().install() and assert no write to portfolio_nodes, workspaces or working_drafts; workspace_state is written by restore by design

handoff:
  - Fixtures in src/test/combinedImportFixtures.ts: ibStatementSnapshot(), esppStatementSnapshot(), ffLegacyStatementSnapshot() (literal 3018.96 / 0.00), concatDistinctAccounts, sameAccountCombine, combinedResponse(), ibAdmission(), esppAdmission(), ibPlusEsppAdmission(), rolledUpAdmission(), buildSavedWorkspace(), seedSavedWorkspace(), IB_TRUTH
  - ffLegacyStatementSnapshot sets the fabricated basis literally, so H-1 regenerating dashboardGoldens.ts does not turn the legacy fixture null and does not break these tests
  - IB fixtures come from ib2026ImportedDashboardGoldenFixture.snapshot; only statement-derived numbers are asserted (18, 62843.22, VUAA 80, USD 146.07), which H-1 does not move
  - createFakePortfolioDb() in src/test/fakePortfolioDb.ts: install() spies withStore and withStores; writes[] records put, delete, clear; seed() writes without recording; read() returns stored values
  - App.test.tsx buildImportedSource now stamps derivationVersion 1; pass legacy: true for a pre-fix node, importedConstituents optionally
  - App.test.tsx installUS402FetchMock is replaced by installAddStatementFetchMock with onAnalyzeCombined; analyze-combined without a handler throws, so an unexpected call fails loudly
  - T-2 must not remove the derivationVersion stamp in buildImportedSource; golden-driven FF tests that use it stay non-legacy
  - Mutation evidence, each reverted and confirmed byte-identical: chained combine, client-side quantity doubling, client snapshot instead of engine, upload admission instead of roll-up, missing derivationVersion on add, skipped re-derive, failure keeping old figures, sanitizer dropping derivationVersion, symbol-only dedupe all turn named tests red
  - Scratch: none left in the repo; src/zz_scratch was removed; /tmp/mut backups are outside the repo
  - See § Coverage map below for the T-3 checklist to AC mapping

skill_calls:
  - mattpocock-skills:tdd — not called, the only mock is the engine at the fetch seam and the IndexedDB stand-in the pack already prescribes; storage and App code run for real
  - mattpocock-skills:diagnosing-bugs — not called, the two mid-run reds were faults in my own test premises and were found by reading the DOM and the design

risks:
  - portfolioWorkspaceStorage.ts:346 falls back to workspace.source.admissionSummary when saveImportedSnapshotNode gets a null admission, so a null roll-up would show the ROOT statement's label on the add node; not reachable today because the engine always returns one; not pinned
  - portfolioSnapshot.ts:31 sums two null quantities to 0 in normalizePortfolioSnapshot (existing.quantity ?? 0), turning unknown into zero; pre-existing, out of scope, not pinned
  - rederiveSavedNodes.ts: a root with a null admission still re-derives but every descendant fails, because lineage is read from stored nodes; pinned as designed, worth a human glance
  - Restore writes the workspace_state pointer (setSelectedExposureSnapshot) on every load; the no-write-back assertions therefore cover only portfolio_nodes, workspaces and working_drafts
  - A dirty draft is asserted to survive by selecting it in the Snapshot dropdown; startup lands on the re-derived base node, not the draft
  - Not covered by design: a legacy base without constituents plus a same-account add (engine chained-input guard, backend-tested); a variant node built on a legacy doubled ancestor is left untouched and unasserted beyond the unit test
  - The US-46.4 AC 9 falsifier is type-level plus a regex source guard, because no component renders cost basis; the first component that does must add a render test
  - Pack gap: testing.md does not say vitest App tests can run on real storage over a fake DB, nor that CardShell titles are p elements in a region, so getByRole heading fails for card titles

## Orchestrator brief
- T-3 delivered: 470 tests pass, tsc and knip clean; the 26 reds are all rewritten to the new behaviour, none deleted without a replacement.
- The falsifier exists at App level for both add and restore: mocked analyze-combined answers (VUAA 77, an engine-only line, a withheld/unavailable label) differ from any client sum and the UI inputs follow them.
- Legacy fixtures are built from real engine-shaped output: doubled IB+IB, IB+ESPP saved admitted/verified, FF 3018.96/0.00, null stored snapshot, missing lineage admission, dirty and clean drafts.
- Repeated load is stable and writes nothing back to nodes, workspaces or drafts.
- No production file was edited; three findings in risks are pre-existing or design-level, none blocks.
- Sections: Coverage map (T-3 checklist to ACs), Red resolution (the 26 reds).

## Coverage map

| 05-design T-3 item | Test | AC |
|---|---|---|
| Overlay tests replaced by currency-aware dedupe | portfolioSnapshot.test.ts: retired-export guard; never sums two currencies; same-currency still sums | 46.1 AC 5, 8 |
| App: IB then IB | App.combinedImport.test.tsx: IB2026 then IB2026 | 46.1 AC 1-4, 6 |
| App: IB then ESPP degraded/degraded as the user reads it | App.combinedImport.test.tsx: IB2026 then ESPP2026; card tests | 46.3 AC 1, 8 |
| Refused combine, currency mismatch and missing account id | App.combinedImport.test.tsx it.each; App.test.tsx it.each | 46.1 AC 7; 46.3 AC 11 |
| Base with no replay refuses | App.combinedImport.test.tsx: no stored statement history | 46.1 AC 7 |
| combine-snapshots mocks repointed to analyze-combined | App.test.tsx: six tests plus installAddStatementFetchMock | 46.1 AC 6 |
| derivationVersion stamped on non-legacy fixtures | App.test.tsx buildImportedSource | 46.1 AC 11 |
| Legacy doubled IB+IB node | App.combinedImport.test.tsx: opens a doubled IB + IB node | 46.1 AC 10 |
| Legacy IB+ESPP node persisted admitted/verified | App.combinedImport.test.tsx and rederiveSavedNodes.test.ts | 46.3 AC 13, 14 |
| Legacy FF 3018.96 / 0.00 node | App.combinedImport.test.tsx and rederiveSavedNodes.test.ts | 46.4 AC 11 |
| Null stored snapshot node | App.combinedImport.test.tsx it.each; rederiveSavedNodes.test.ts | 46.1 AC 12; 46.3 AC 15 |
| Repeated-load stability | App.combinedImport.test.tsx: stable across repeated loads, no write-back; rederiveSavedNodes.test.ts stability | 46.1 AC 11 |
| Sanitizer round trip | portfolioWorkspaceStorage.test.ts: constituents and derivationVersion | C6 |
| Label survives reload | portfolioWorkspaceStorage.test.ts: roll-up persisted | 46.3 AC 12 |
| Type-level null total_unrealized_pnl | costBasisUnavailable.test.ts | 46.4 AC 3, 4, 9 |
| Falsifier | App.combinedImport.test.tsx: engine result differs from any client sum (add) and falsifier (restore) | 46.1 AC 6 |
| Path independence | App.combinedImport.test.tsx: several files stored as constituents; App.test.tsx multi-file | 46.3 AC 5 |
| Card renders roll-up, never derives it | ImportAdmissionReviewCard.test.tsx | 46.3 AC 8, 10 |
| Distinct accounts still sum | portfolioSnapshot.test.ts same-currency sum; engine sum shown in IB+ESPP test | 46.1 AC 5 |
| Single statement unchanged | replace-mode App test; card no-rollup tests | 46.1 AC 9; 46.3 AC 10 |

## Red resolution

- 9 overlayImportedSnapshot cases in portfolioSnapshot.test.ts — replaced by the retired-export guard and four normalizePortfolioSnapshot dedupe tests
- 6 FE-1 App add-flow reds — adds a new node; refreshes dashboard; AC1/AC2 combine; AC3 degradation (now refused-combine saves nothing, two variants); sequential chain (now flat from constituents); leaves add node without override — all rewritten to analyze-combined
- 12 FE-2 restore reds — cleared by stamping derivationVersion 1 in buildImportedSource; legacy behaviour is asserted separately with legacy: true or seeded legacy workspaces
- FE-2 baseline note: refreshes dashboard allocation and cards passes on the route-based mock and in isolation, so it is not order-dependent
