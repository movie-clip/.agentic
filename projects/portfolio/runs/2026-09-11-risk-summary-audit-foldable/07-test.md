REPORT 2026-09-11-risk-summary-audit-foldable/07
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/RiskSummaryCard.test.tsx — new colocated file: default-expanded rendering, toggle collapse/hide/re-expand, collapsed header summary, aria-expanded/aria-controls, unavailable empty state has no toggle, AC7 value/trust regression pin
  - apps/desktop/src/features/portfolio/DashboardPanel.test.tsx — added one test: collapsing Risk Summary leaves Performance & Benchmark, Sector Composition, Benchmark Positioning cards' rendered output unchanged (AC6)

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    42 test files passed, 380 tests passed (includes designSystem.audit.test.ts and the two files above); also ran mcp__project__check_gates — deadcode clean, typecheck clean, goldens not drifted

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - RiskSummaryCard.test.tsx's getToggle() helper matches the button by accessible name regex /(Collapse|Expand) Risk Summary/i — reuse this pattern if a future card adopts the same one-off aria-expanded/aria-label convention (per story, no shared primitive exists yet).
  - No new shared fixture was needed; createDiagnosticsEngineFixture() from apps/desktop/src/test/portfolioFixtures.ts covered every case, including the volatility_summary/drawdown_summary/risk_concentration_summary-undefined unavailable variant already used elsewhere.

risks:
  - none
