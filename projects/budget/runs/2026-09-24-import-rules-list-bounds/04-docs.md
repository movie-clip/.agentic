REPORT 2026-09-24-import-rules-list-bounds/04
status:      DONE
verdict:     NONE

changed:
  - docs/RELEASE_NOTES.md — inserted 2026-09-24 entry at top (Bug Fixes, Known Issues, Validation); existing entries untouched

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; validation figures copied from 03-integration (builds 0/0, 56 tests passed)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Human visual check of Import tab at 1200x760 and 1400x900 remains open; release note says so plainly.
  - Ledger tab Border missing Grid.Row is recorded in the entry as not fixed; carry to close-out.

skill_calls:
  - none

risks:
  - PROJECT_GUIDE.md and TECHNICAL_DESIGN.md were grepped for scroll, pager, paging and Potential New Rules; no layout statements exist, so neither was edited.
