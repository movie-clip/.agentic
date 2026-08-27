REPORT 2026-08-26-performance-benchmark-chart-audit/14
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\portfolio\capabilities\testing.md — added a new "Gotchas that will bite you" bullet documenting the local `vi.mock('recharts', ...)` pattern (stub `LineChart` to expose `data` via a `data-testid`, read via async `getChartData()`) for asserting exact chart-line values against an unexported transform, alongside the existing shim-warning bullet.

verification:
  command:   grep -n "vi.mock('recharts'\|getChartData\|LineChart" C:\projects\investments\.agentic\projects\portfolio\capabilities\testing.md
  result:    NOT_RUN
  detail:    Docs lane has no Bash tool. Confirmed by direct read that the new bullet contains the strings `vi.mock('recharts', ...)`, `getChartData()`, and `LineChart` after the edit.

contract_notes:
  - none

pack_corrections:
  - none — this order itself applies the one pending correction from pack-corrections.md; no new corrections found while doing so.

handoff:
  - none

risks:
  - none
