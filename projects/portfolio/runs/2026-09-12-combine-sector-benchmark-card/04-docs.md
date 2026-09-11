REPORT 2026-09-12-combine-sector-benchmark-card/04
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/dashboard-fields.md — "Factor / Composition cards" table: Sector composition and Benchmark Positioning rows now describe them as `role="group"` sub-sections of one combined `summary-card` (Benchmark Positioning foldable, default expanded), not two top-level cards; added a "Sector/Benchmark card merge" note below the table naming the new `DashboardPanel.tsx` wrapper markup, sourced from 01-frontend.md § changed.
  - C:\projects\investments\.agentic\runs\2026-09-12-combine-sector-benchmark-card\pack-corrections.md — created; records that no lane emitted a pack_corrections entry and that neither capabilities/frontend.md nor capabilities/backend.md mentions these two components at all, so no false premise exists there to correct.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE; no command specified for a docs-only close-out.

contract_notes:
  - none

pack_corrections:
  - none — verified capabilities/frontend.md and capabilities/backend.md against the code; neither documents Sector Composition or Benchmark Positioning as separate cards (no mention of either component or the affected CSS classes at all), so there is no false premise to correct.

handoff:
  - docs/product/current-product-state.md needed no edit: it never described Sector Composition or Benchmark Positioning as cards, or even by name, at Dashboard-tab or Exposure-tab granularity — it is tab-level feature prose, not card-level, so the merge does not touch it. Confirmed no data/field change occurred (01-frontend and 02-test both report 0 contract_notes, no schema changed).
  - Left the SectorPieCard.test.tsx "rename vs net-new" wording slip (01-frontend.md § handoff vs 02-test.md § risks) out of this change as directed: it is a note about this run's own transient artifacts, not a doc or a pack, and reports are immutable once written.

risks:
  - none
