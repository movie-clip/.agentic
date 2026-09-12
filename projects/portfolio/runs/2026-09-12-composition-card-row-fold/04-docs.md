REPORT 2026-09-12-composition-card-row-fold/04
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/dashboard-fields.md — "Factor / Composition cards" table: Sector composition donut and Benchmark Positioning rows rewritten to state side-by-side layout and shared-card fold ownership; Benchmark Positioning row explicitly states it is no longer independently foldable, per frontend lane's (01) contract note and integration lane's (03) description of `compositionExpanded`/`dashboard-composition-row`.
  - docs/contracts/dashboard-fields.md — "Sector/Benchmark card merge" note updated to describe the `.dashboard-composition-row` grid (`1fr auto 1fr`, vertical divider, 1100px breakpoint collapsing to one column) and the single `compositionExpanded` state/toggle in `DashboardPanel.tsx` governing both sub-sections together.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE; doc-only change, no code touched

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - none
