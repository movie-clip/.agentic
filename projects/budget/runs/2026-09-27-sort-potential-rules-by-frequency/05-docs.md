REPORT 2026-09-27-sort-potential-rules-by-frequency/05
status:      DONE
verdict:     NONE

changed:
  - docs/PROJECT_GUIDE.md — § "Rule Management" gained a bullet stating the Potential New Rules list's default order: most-repeated suggested pattern first (count scoped to the current import file's unmatched rows only), ties broken by original parse order.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order specified verification: NONE — read-only docs accuracy fix, no command to run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The new bullet sits immediately after the list's existing opening bullet and before the per-row description bullet, so a future edit to that section should keep the ordering fact adjacent to the list's definition rather than moving it into the per-row bullet list.

skill_calls:
  - none

risks:
  - none
