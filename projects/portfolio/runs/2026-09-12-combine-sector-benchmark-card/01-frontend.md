REPORT 2026-09-12-combine-sector-benchmark-card/01
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/SectorPieCard.tsx — outer element changed from `<section className="summary-card sector-pie-card">` to `<div className="sector-pie-card" role="group">`, so it renders as a sub-section, not its own card; `aria-label="Sector Composition"` preserved on that div.
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.tsx — outer element changed the same way (`role="group"`, `aria-label="Benchmark Positioning"` preserved); added a local `useState` fold toggle around the metrics/lists detail, copying RiskSummaryCard's US-45.1 pattern verbatim (`aria-expanded`, `aria-controls`, same inline-style token set on the toggle button).
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.tsx — the always-visible `coverageNote` line stays outside the fold, matching RiskSummaryCard's "trust line stays visible, detail folds" shape.
  - apps/desktop/src/features/portfolio/DashboardPanel.tsx — replaced the two-card `<div className="dashboard-composition-row">` with one `<section className="summary-card dashboard-composition-card" aria-label="Sector and Benchmark Composition">` wrapping both sub-components plus a divider.
  - apps/desktop/src/app/styles.css — replaced `.dashboard-composition-row` (2-column grid) with `.dashboard-composition-card` (flex column) and a new `.dashboard-composition-divider` rule, using existing `--border-thin` / `--color-border-subtle` tokens; removed the now-unused `.dashboard-composition-row` entry from the `max-width: 980px` media query.

verification:
  command:   cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    tsc --noEmit exited 0, no errors printed. Also confirmed via `check_gates`: ruff/vulture/knip dead-code clean, typecheck clean, dashboardGoldens not drifted.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SectorPieCard.test.tsx and BenchmarkPositioningCard.test.tsx still assert the old two-`<section className="summary-card">` DOM shape (top-level section per card) — they will fail against the new `role="group"` div sub-section shape until the test lane updates them; this was flagged out-of-scope by the work order.
  - Test lane should add/adjust coverage for the new Benchmark Positioning fold toggle (default expanded, `aria-expanded`, click collapses the metrics/lists block, `coverageNote` stays visible when collapsed) mirroring RiskSummaryCard's existing fold tests.
  - Test lane should verify both "Sector Composition" and "Benchmark Positioning" remain queryable via `getByRole('group', { name: ... })` (or equivalent) now that they are not top-level `<section>` elements.

risks:
  - I chose to fold Benchmark Positioning (not Sector Composition) since it carries more variable-length detail (metrics + two lists) that benefits most from collapsing; the order left the choice open, naming this so the tech lead can override if a different section was intended.
  - Rename/removal not applicable here — no file was renamed or deleted; both `SectorPieCard.tsx` and `BenchmarkPositioningCard.tsx` keep their exported component names and are both still directly imported by `DashboardPanel.tsx`, so there is no pending `git rm` to report.
