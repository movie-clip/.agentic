REPORT 2026-09-23-dashboard-review/05
status:      DONE
verdict:     NONE

changed:
  - docs/PROJECT_GUIDE.md — Dashboard Review section (§4): KPI-card line now lists Income/Expenses/Net/Avg Monthly Savings Rate (D-2's ruling, no "uncategorized" card), and two new bullets document the shipped this-month-vs-last-month strip and the Needs Attention panel with its Review-in-Ledger action.
  - docs/TECHNICAL_DESIGN.md — `BuildDashboardSnapshotUseCase` bullet (§3) now names all 8 read-model sub-shapes and states that MonthComparison and the uncategorized queue are consumed by the Dashboard UI (month-comparison strip, Needs Attention panel), not merely computed.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE; docs-only change, no build/test command applicable.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test lane: docs/PROJECT_GUIDE.md and docs/TECHNICAL_DESIGN.md now describe the Needs Attention panel and month-comparison strip as shipped surfaces with no Presentation-layer test coverage backing them (per 01-recon.md § Test coverage and 03-frontend.md handoff) — naming FormatMonthDeltaSummary/FormatSignedAmount and ReviewUncategorizedAsync as the concrete gap, same as 03-frontend.md already flagged.

risks:
  - none
