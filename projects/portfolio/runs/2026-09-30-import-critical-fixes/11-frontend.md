REPORT 2026-09-30-import-critical-fixes/11
status:      PARTIAL
verdict:     NONE

changed:
  - apps/desktop/src/app/rederiveSavedNodes.ts — new; rederiveSavedNodes() re-derives legacy import nodes through analyze-combined, ancestor first, in memory only, failure path nulls snapshot, admission and override
  - apps/desktop/src/app/App.tsx — restoreImportedWorkspaceFromPersistedState calls rederiveSavedNodes once after startup validation and continues with the returned workspace, node, nodes and draft; a failure detail goes to setImportError

verification:
  command:   cd apps/desktop && npx tsc --noEmit && npx vitest run
  result:    FAIL
  detail:    tsc: 11 errors, all portfolioSnapshot.test.ts (FE-1 overlay tests), none elsewhere. vitest: 2 files failed, 41 passed (43); 26 failed, 368 passed (394). Reds: 9 overlay (FE-1), 5 FE-1 App add tests, 12 newly red App tests on legacy fixtures. see § Verification detail

contract_notes:
  - docs/contracts/imports-fields.md (T-46.4.5) must state the on-load re-derive: a node without derivationVersion is re-run through analyze-combined in memory, never written back, and a failed node shows no snapshot, admission or override
  - docs/contracts/import-admission-fields.md (T-46.3.5) must state that a legacy node's roll-up carries the lineage admissions as carried_admissions constituents (origin carried)
  - App.test.tsx fixture helper buildImportedSource does not stamp derivationVersion, so 12 restore tests now take the legacy path and are red until T-3 stamps it (see § Verification detail)

pack_corrections:
  - none

handoff:
  - T-3 helper: stamp derivationVersion 1 in App.test.tsx buildImportedSource (and mockImportedWorkspace, child-node fixtures) for non-legacy fixtures; this clears the 12 newly red App tests without touching the app
  - T-3 legacy fixtures: no derivationVersion on workspace.source or node.source; mock POST /api/portfolios/import/analyze-combined and assert one call per legacy node, root first, root body has no carried_admissions
  - T-3: for an add node the body carries snapshots of length 1 (the stored importedHistorySnapshot) and carried_admissions = admissions of root, intermediate add nodes and the node itself, root first
  - T-3 AC 10-11: doubled IB+IB node opens showing the mocked response (18 positions, 62,843.22, VUAA 80, USD 146.07); reopen twice and assert the same figures and that no IndexedDB put is called (no write-back)
  - T-3 AC 12/15: mock analyze-combined 400 with a detail; assert the Dashboard shows that detail via importError, Exposure holds no stale holdings, the old admission label is absent and Add Statement is hidden
  - T-3 AC 13-14: IB then ESPP node persisted admitted/verified opens with the mocked roll-up (degraded/degraded, constituents incl. origin carried); a lineage node with admissionSummary null fails without calling the engine for that node
  - T-3 AC 11 (US-46.4): FF node with cost_basis 3018.96 and unrealized_pnl 0.00 opens with the mocked response showing null; the frontend must not scrub, so the mock is the only source of null
  - T-3: a stored history_context-only or none historySource fails with the no-stored-statement message and the engine is never called; a node with derivationVersion 1 triggers no call
  - T-3: clean WorkingDraft on a re-derived node is re-cloned from it; on a failed node the draft is dropped; a dirty draft is left as saved
  - T-3: falsifier — analyze-combined mock response differs from stored figures, assert the UI shows the response; stored IB2026 figures must not appear
  - Baseline note: App test 'refreshes dashboard allocation and cards after adding a statement snapshot' was red in FE-1's run and passes with FE-2 in place; not investigated, T-3 to confirm it is not order-dependent

skill_calls:
  - ui-polish — not called, no card or UI file touched
  - mattpocock-skills:diagnosing-bugs — not called, no fix attempt failed

risks:
  - Legacy base without constituents (09 risks 5): not solved client-side, no split of a combined snapshot is possible. A re-derived multi-account base (IB+ESPP) is one input, so adding a statement for an account inside it is refused by the engine chained-input guard; the user sees that server detail and must re-import the originals. Single-account legacy bases add correctly
  - Consequence of no write-back: a legacy workspace calls the engine for every legacy node on every open (one call per node, sequential). Slow opens on long chains; nothing is cached
  - A dirty WorkingDraft on a legacy node is left alone per design 05 step 3, so its edited figures still derive from the saved doubled snapshot; a dirty draft on a failed node still renders
  - Variant nodes are untouched per design; a variant built on a legacy doubled node keeps its own saved snapshot, though its ancestor admission is re-derived or nulled
  - A legacy node with no stored imported_replay snapshot (history_context-only or none) is now non-re-derivable and shows nothing, per design step 4; older workspaces without replay data lose their figures until re-imported. Wording of the two client-side messages is mine, for the human to review
  - Several failed nodes are joined with '; ' into one importError string; a failed non-active ancestor shows the banner even when the active node is fine. Design named only the existing importError
  - Selecting a failed node in the Exposure selector does nothing (handleExposureSnapshotChange returns silently on a null snapshot); that code is outside the restore path and was not touched
  - Deviation in App.tsx: I renamed the first reads to storedWorkspace, storedNode and storedNodes so the re-derived values keep the names workspace, node, nodes and draft for the unchanged code below; the change is confined to the top of the restore function
  - Scratch verification: a temporary src/zz_scratch unit test (5 cases: ancestor order, carried lineage, 400, missing lineage admission, no replay snapshot) passed and was removed with rm before the final run; no file of it remains
  - getNodeImportSource logic is duplicated as importSourceOf in rederiveSavedNodes.ts because App.tsx does not export it and exporting was outside the fence

## Orchestrator brief
- FE-2 built to 05-design § Saved-node re-derive steps 1-5: one shared step, called once from the restore choke point in App.tsx, in memory only, ancestor first, variants untouched.
- carried_admissions per D-11: root..node persisted admissions for add nodes, none for the root; a null admission on the lineage fails the node without an engine call.
- The Freedom24 scrub (D-12) is engine-side; the frontend adds no scrub logic and computes no value or label.
- Failure path: portfolioSnapshot, admissionSummary and importedExposureOverride nulled; clean draft dropped; server detail goes to importError.
- Verification is FAIL only because of known and newly red tests: 12 App restore tests red until T-3 stamps derivationVersion on fixtures; no non-test tsc error.
- Legacy base without constituents: reported, not handled; see risks bullet 1.
- Section Verification detail: exact counts and the red lists.

## Verification detail

- npx tsc --noEmit: 11 errors, all in src/features/portfolio/portfolioSnapshot.test.ts (unchanged from FE-1); zero in non-test files.
- npx vitest run: Test Files 2 failed, 41 passed (43); Tests 26 failed, 368 passed (394). FE-1 left 15 red; this lane adds 12 and clears 1.
- Expected-red from FE-1 (unchanged): 9 overlayImportedSnapshot cases in portfolioSnapshot.test.ts; App.test.tsx: adds a new imported snapshot node from Dashboard Add Statement, add_snapshot combines the base history (AC1, AC2), discloses degradation when combine-snapshots fails (AC3), sequential-add chain regression, leaves an add_snapshot node without an exposure override.
- Newly red in App.test.tsx, all because the fixtures carry no derivationVersion and no analyze-combined mock exists: restores IB2026 dashboard values; restores FF2026 dashboard values; keeps the dashboard tab landing-only after importing a portfolio; shows base and child variant lineage in Exposure snapshot options; reuses imported diagnostics when selecting the base snapshot after reload; shows an Exposure header exit CTA after selecting a draft; uses history-aware snapshot diagnostics for saved variants; returns a saved variant selection to the nearest imported ancestor; uses snapshot-history diagnostics instead of imported replay for a child variant; applies the persisted exposure override after a replace-mode import; applies the persisted exposure override after a session restore; never applies the persisted exposure override on the draft branch.
- Baseline check: with the re-derive filter temporarily disabled, App.test.tsx had exactly the 6 FE-1 reds, so the 12 are attributable to this lane; the filter was restored (grep confirms).
- python scripts/detect_deadcode.py --strict: ruff, vulture, knip clean.
- dashboardGoldens.ts, tests, backend files untouched; run_all_tests.py and reset_goldens not run.
