REPORT 2026-10-07-s2-animation-bridge-contract/14
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core; testing.md:34-51 re-read against 12-protocol-lint.md § Finding F-1, project.md:187-188, AGENTS.md:48-75; bullet lengths measured by script
  result:    PASS
  detail:    plugin validate passed; F-1 resolved; SF-2, SF-3, SF-4 applied; 0 BLOCKING, 1 new SHOULD_FIX (rule 8); anchor: F-1 satisfy text, project.md:187-188, AGENTS.md:48-75, Run-UnityTests.ps1:71-79; 1 UNVERIFIED premise

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F-1 resolved: testing.md:38-39 scopes the no-pipe rule to PowerShell, and testing.md:40-42 states the script wins over AGENTS.md's raw -runTests lines; both halves of the F-1 fix are present
  - SF-2 applied: the TestResults-*.xml tracked-in-git fact is its own bullet at testing.md:43-44
  - SF-3 applied: the "every run in the S2 run" provenance sentence is gone from testing.md:34-37
  - SF-4 applied: Is.AnyOf (testing.md:45-46) and the compile-error presentation (testing.md:47-48) are separate bullets
  - SHOULD_FIX SF-5 (authoring.md § Writing for the reader, under 200 characters) testing.md:34-37 is 274 characters; drop its "because..." clause, which testing.md:38-39 now carries
  - Carried, unchanged: SF-1 (package table omits Unity.Entities, now testing.md:94-97) and the backend-only forward-slash risk from order 12

skill_calls:
  - none

risks:
  - testing.md:41-42 "a raw call needs the same pipe" is not scoped to PowerShell, unlike :38. No instruction says not to pipe, so it directs no conflicting action and is not a rule 9 finding
  - AGENTS.md:48's batchmode compile check (-quit, not -runTests) is outside :40's "for test runs". From PowerShell, :38 still tells the lane to pipe it, and project.md:187 tells it to run it plain
  - That compile-check case falls under the PowerShell scoping that F-1 accepted on its own; lanes run Git Bash, so it was not raised as a new finding
  - UNVERIFIED: an unpiped Unity.exe in PowerShell "returns at once and $LASTEXITCODE is not set" (testing.md:38-39); rests on the script comment at Run-UnityTests.ps1:71-72, not run

## Orchestrator brief
- Verdict PASS. CR-3 can be closed. F-1 is resolved by testing.md:38-42, see the handoff lines for the evidence.
- SF-2, SF-3 and SF-4 were all applied inside the CR-3 fence (testing.md:34-48).
- No new contradiction: the new bullets read consistently with Gotchas :21-33 and :49-51, Running the suite, and project.md Mechanical gates.
- One new SHOULD_FIX, SF-5 (bullet length, rule 8). It becomes an `Open` row, not a change request.
- Carried SF-1 and the forward-slash risk from order 12 stand, per this order's non-goals.
