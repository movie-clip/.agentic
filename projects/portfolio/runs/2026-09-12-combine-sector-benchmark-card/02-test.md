REPORT 2026-09-12-combine-sector-benchmark-card/02
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/SectorPieCard.test.tsx — new file; no such spec existed before this order despite the work order and the frontend lane's handoff assuming one did (see risks).
  - apps/desktop/src/features/portfolio/SectorPieCard.test.tsx — covers `getByRole('group', { name: 'Sector Composition' })`, legend content from exposureResult, dashboard-result fallback path, the unavailable state, and holdings-panel selection on legend click.
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.test.tsx — added `mockExposureView` (via `composeExposureView` + shared fixtures) and a `getToggle()` helper mirroring RiskSummaryCard's fold-test pattern.
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.test.tsx — added a new `describe('BenchmarkPositioningCard — fold/expand')` block: default-expanded, click collapses the metrics/lists detail block, a second click re-expands it, the coverageNote line stays visible while collapsed, and `aria-controls` resolves to a real element.
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.test.tsx — updated one existing trust-derivation assertion to query via `getByRole('group', { name: 'Benchmark Positioning' })` instead of `getByLabelText`, demonstrating the DOM-shape query update without touching its content assertion.

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    43 test files passed, 390 tests passed, 0 failed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SectorPieCard.test.tsx is a new shared spec, not a rename — no old file existed to remove; future orders touching SectorPieCard should extend this file rather than assume prior coverage lived elsewhere.
  - DashboardPanel.test.tsx needed no changes: its existing assertions already used `getByLabelText('Sector Composition')` / `getByLabelText('Benchmark Positioning')`, which match `aria-label` on any element regardless of `role`, so they kept passing unmodified against the new `role="group"` divs.

risks:
  - The work order and 01-frontend.md's handoff both state SectorPieCard.test.tsx "still asserts the old two-`summary-card` DOM shape," but no such file existed anywhere in git history before this order.
  - It had to be authored from scratch rather than updated; correct the pack/handoff wording so a future lane does not search for a file that was never there.
  - BenchmarkPositioningCard.test.tsx's pre-existing trust-derivation tests already passed unmodified against the new DOM shape before I touched anything.
  - That is because they query via `getByLabelText`, which matches `aria-label` on non-form elements too, not only via role or a `summary-card` class selector.
  - So the DOM-shape "break" the order anticipated for that file did not actually occur; only the fold-toggle coverage was a genuine net-new gap.
