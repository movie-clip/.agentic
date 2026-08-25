REPORT 2026-08-25-leftover-findings-fold-in/13
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_importer.py app/tests/test_exposure_engine.py -v ; cd apps/desktop && npx vitest run App.test.tsx variantLabels.test.ts runMetadataTrustSourceGuard.test.ts
  result:    PASS
  detail:    Backend: test_importer.py 28 passed, test_exposure_engine.py 23 passed (51 total). Frontend: 3 files / 37 tests passed (App.test.tsx 28, variantLabels.test.ts 6, runMetadataTrustSourceGuard.test.ts 3). Also spot-ran test_routes.py -k combine_snapshots: 2 passed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Working tree carries a second, unrelated uncommitted diff predating this run (10 files, HEAD 59387c7, the 2026-08-24 CR-1-frontend.md fix) — re-confirmed present via `git status`.
  - That diff is already flagged non-blocking by 11-integration.md, left untouched by 12-docs-closeout.md per its own non_goals — not this epic's scope, does not affect this verdict.
  - App.tsx:793's degraded-combination message names only "a differing base currency", not CR-1's newer account-identity failure mode, as its example.
  - Already flagged as non-blocking polish by 11-integration.md; the message is still truthful (generic, non-exhaustive "for example") and AC3 is met regardless.

## Orchestrator brief
Independent AC-by-AC trace of both stories against landed code/tests (not report prose): all 6 US-40.1 ACs and all 4 US-40.2 ACs are genuinely SATISFIED. Both stories' "Done" status is earned. Test plans were delivered as claimed, at the claimed counts, in the named files. Trust-state spot-checks (picker date label, degraded-combination disclosure) render distinguishably per guardrail 3, confirmed by direct render-path reads, not by trusting the story text. No GAP, no DRIFTED. See § US-40.1 AC trace, § US-40.2 AC trace, § Trust-state spot checks, § Test plan fidelity, § Repo hygiene.

---

## US-40.1 AC trace

- **AC1 (base node label discloses capture date) — SATISFIED.** `variantLabels.ts:34-38` (`formatVariantNodeLabel`) appends `resolveNodeImportDate`'s result in parens when present; App.tsx:890-891 wires this into the actual picker option labels (not just a helper left unused). `git diff` against the pre-story version confirms the prior behavior returned the bare path with no date. Tested: `variantLabels.test.ts:49-53` ("AC1: a base node label includes its importedMeta.importedAt date...") asserts `'base (2026-04-10)'`.
- **AC2 (variant continues to disclose base's date) — SATISFIED.** `resolveNodeImportDate` (`variantLabels.ts:17-32`) checks the node's own `importedMeta.importedAt` first, then walks the ancestor chain via `parentId` checking each ancestor's own date. Tested twice: `variantLabels.test.ts:55-69` (variant node with its own inherited snapshot) and `:71-85` (explicit ancestor-walk-fallback case for a node with `portfolioSnapshot: null`).
- **AC3 (no date -> renders exactly as before, no fabrication) — SATISFIED.** `formatVariantNodeLabel:38` returns the bare `path` when `resolveNodeImportDate` returns `null` — no placeholder. Confirmed via `git diff HEAD` on `variantLabels.ts`: the only change to the pre-story return path is the `importDate ? ... : path` conditional, i.e. the no-date branch is byte-identical to prior behavior. Tested: `variantLabels.test.ts:87-95` and `:97-100`.
- **AC4 (contract doc states the retirement) — SATISFIED.** `docs/contracts/exposure-fields.md:38` states `run_metadata.source_status.lookthrough_resolution`/`.benchmark_holdings`/`run_metadata.confidence` are live/per-render, redundant re-derivations of `availability`, and must never be read as a trust source — sibling to line 37's existing frozen-fields disclosure, cross-referencing the prior CR-1-frontend.md fix by name (confirmed as a *different*, earlier CR-1 than this epic's own, correctly distinguished).
- **AC5 (no component reads these fields for trust) — SATISFIED.** `runMetadataTrustSourceGuard.test.ts` recursively scans every non-test `.ts`/`.tsx` file under `apps/desktop/src/features/portfolio` (its own directory, `__dirname`) for `run_metadata.source_status`/`run_metadata?.confidence` property-access patterns and fails naming file:line on any hit. Independently re-confirmed via a direct grep across the whole `features/portfolio` tree (not just trusting the test): the only live reads of `run_metadata.*` are `reproducibility.benchmark_symbol`, `return_basis_contract.*`, `withheld_return_dates`, `withheld_return_impact_pct`, `investor_economics_status`, `section_trust.*` — none read `.source_status` or bare `.confidence`. Test passes (part of the 37-test run above).
- **AC6 (trust badges still sourced from frozen fields only) — SATISFIED.** `BenchmarkPositioningCard.tsx:37-45` (`getBenchmarkTrust`) reads only `result.exposure_availability.benchmark_overlap_status`/`.benchmark_overlap_confidence` — no `run_metadata` read anywhere in that function. Backend characterization test `test_exposure_engine_run_metadata_source_status_and_availability_are_self_consistent_within_one_call` (`test_exposure_engine.py:782-820`) pins that `_build_exposure_source_status` and `_build_exposure_availability` still agree within one call, i.e. no value a researcher sees changed.

## US-40.2 AC trace

- **AC1 (add_snapshot no longer discards history) — SATISFIED.** `App.tsx:767-808`: the `add_snapshot` branch now computes `baseImportedHistorySnapshot` from the effective base node's frozen `historySource.importedHistorySnapshot`, and when present calls `combineImportedSnapshots([baseImportedHistorySnapshot, nextAnalysis.snapshot])` via the new `POST /portfolios/import/combine-snapshots` route (`imports.py:49-56`, wraps `combine_imported_snapshots` verbatim) instead of the pre-story literal `null`. Confirmed by direct read; matches `git diff`'s only material change to this branch. Tested: App.test.tsx:982-1052 asserts the combined result (deliberately distinct from either input) is what gets persisted, not `null` and not either input alone.
- **AC2 (combination reflected in history-derived views, not fallback-to-one-side) — SATISFIED.** The combined snapshot is threaded into `saveImportedSnapshotNode`'s `importedHistorySnapshot` field exactly as the `replace` path already does for its own snapshot, so it feeds the same downstream `historySource.importedHistorySnapshot` consumption path Dashboard's history-backed cards already use (unaffected code path, per the story's own framing that this is a data-flow fix, not a new consumption path). Also spot-checked the sequential-add-chain case (App.test.tsx:1115-1176): a chained add_snapshot combines against the previous step's own already-accumulated `chainAccumulatedSnapshot`, not the workspace root's raw single-statement snapshot — confirms combination compounds through a chain rather than resetting at each step.
- **AC3 (incompatible combine discloses degradation, no silent drop/fabrication) — SATISFIED.** On a combine failure, `App.tsx:791-794` sets `combinedHistorySnapshot = null` (never a fabricated partial merge) and calls `setImportError(...)` with a disclosure message; the node is still saved (positions preserved) with the null history rather than blocking the import outright. Traced the full render path: `applyDashboardSession` (App.tsx:328-334, called after the catch via `restoreImportedWorkspaceFromPersistedState`) never touches `importError` state, so the disclosure is not silently cleared before render. `DashboardPanel.tsx:155` renders it as `<p className="error">{importError}</p>` — a visually distinct class from the adjacent `"helper"` notes, satisfying guardrail 3 (not silently suppressed, not collapsed into a neutral note). Tested: App.test.tsx:1054-1113 asserts both the null persistence and the rendered error text.
  - CR-1's new account-identity ValueError (`statement_importer.py:141-147`) surfaces through the identical channel as the pre-existing currency-mismatch ValueError — independently re-traced (not trusting 11-integration.md's claim): `imports.py:53-56`'s `except ValueError as exc: raise HTTPException(400, str(exc))` is unedited and catches both raise sites identically; `portfolioAnalysisAdapter.ts:183-186`'s `combineImportedSnapshots` throws generically on any non-2xx; `App.tsx:789-794`'s catch has no error-type discrimination. No special-casing exists or was needed for the new failure mode to reach the same disclosure path.
- **AC4 (replace-mode path unchanged) — SATISFIED.** `App.tsx:811-816` (the `replace`/initial-import path) is untouched — still passes `nextAnalysis.snapshot` directly to `createWorkspaceFromImport`'s `importedHistorySnapshot`, no `combineImportedSnapshots` call. Tested: App.test.tsx:1178-1197 asserts zero `/combine-snapshots` fetch calls on this path and that the fresh snapshot is passed through directly.

## Trust-state spot checks

- **Picker date label (US-40.1, guardrail 3).** No-date case renders with zero placeholder/fabricated text (confirmed above, AC3). Date case is visually additive (`(YYYY-MM-DD)` suffix), not a separate badge, which is an appropriate low-ceremony disclosure for a picker option string — no finding.
- **add_snapshot degraded-combination message (US-40.2, guardrail 3).** Renders with a distinct `className="error"` versus the neighboring `"helper"` notes (`DashboardPanel.tsx:152-156`) — visibly distinguishable, not silently suppressed, not collapsed into a generic status. Message text is truthful (generic "for example" framing covers the new CR-1 failure mode even though it isn't named verbatim — see risks for the minor polish opportunity, non-blocking).
- **New market-data caller mock check.** Not applicable to this epic — neither story adds a new market-data caller (US-40.1 is doc + picker-label + guard-test only; US-40.2 reuses the existing, already-tested `combine_imported_snapshots`, which is not a market-data call).

## Test plan fidelity

US-40.1: `variantLabels.test.ts` (6 tests, AC1-AC3 as promised) — new file, exists. `runMetadataTrustSourceGuard.test.ts` (3 tests, AC5 permanent regression scanner as promised, mirrors `BenchmarkPositioningCard.test.tsx`'s CR-1 pattern) — new file, exists. Backend characterization test in `test_exposure_engine.py` (AC4-AC6 self-consistency) — exists, confirmed above. All pass.

US-40.2: `App.test.tsx` gains exactly the 4 tests the story's test plan named — preserves-history (AC1/AC2), degraded-combination (AC3), sequential-add-chain regression, replace-mode regression (AC4) — cross-checked by name against T-40.1.4-T-40.2.3-test.md's own `changed` list and confirmed present by direct read. `test_routes.py` gains 2 thin-wrapper route tests (happy path + 400), correctly scoped per the plan's own instruction not to re-test merge math (already covered in `test_importer.py`). All pass.

Cross-checked T-40.1.4-T-40.2.3-test.md's claimed backend count (908) against a fresh count of the two named files independently (28 + 23 = 51) — consistent with 08-test.md's standalone 28-count for `test_importer.py`.

## Repo hygiene

- Both story files' `Status:` fields read `Done` — earned per the AC trace above, not merely ticked.
- `docs/tech-debt-register.md` correctly carries the 3 items routed there instead of fixed (dead `market_data` param, `_build_exposure_source_status`/`_build_exposure_availability` duplication, golden-PDF no-op gap) — confirmed present via diff.
- `docs/finance/financial-methodology.md` and `services/quant-engine/app/tests/fixtures.py` both carry the close-out's follow-up sentences from 10-quant-reaudit.md Finding 3 and 08-test.md's fixtures gotcha, respectively — confirmed present.
- `docs/contracts/dashboard-fields.md` gained the "Combine Imported Snapshots (US-40.2)" section for the new route — confirmed present, closing 11-integration.md's close-out item 1.
- No stray files introduced by this epic's own work (the two new test files and two new story files are the only untracked additions, all expected). The unrelated pre-existing uncommitted diff (10 files, prior epic) is not this epic's hygiene problem — see risks.
- No golden artifact (`dashboardGoldens.ts`) was touched — consistent with both prior gates' claims, not independently re-diffed here since quant math is out of this review's non_goals.
