REPORT 2026-09-23-fix-cr1-cr2/04
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — applied PC-1: replaced the stale `-CoreOnly` → `-testFilter "Core"` description (lines 36-40) with "`-CoreOnly` now passes `-testCategory \"Core\"`, a true NUnit category match, and selects the full 35-test Core suite; `-Filter` is unaffected." — matches pack-corrections.md's replacement wording verbatim.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field was NONE; no Bash tool granted to this lane per protocol.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Impact\Tools\TESTING.md checked per 02-test.md's handoff bullet — no stale `-CoreOnly`/`-testFilter` description found. The file's "Fast Commands" and "Current Core Test Targets" sections only show usage examples and category tagging; they never describe the internal `-testFilter` vs `-testCategory` mechanism, so nothing in it was made stale by the CR-1 fix. Left unchanged.

risks:
  - none
