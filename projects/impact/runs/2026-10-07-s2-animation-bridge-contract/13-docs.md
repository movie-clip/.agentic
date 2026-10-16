REPORT 2026-10-07-s2-animation-bridge-contract/13
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — F-1: no-pipe instruction scoped to PowerShell as its own bullet
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — F-1: new bullet stating Run-UnityTests.ps1 wins over AGENTS.md's raw Unity.exe -runTests lines for test runs
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — SF-2: TestResults-*.xml tracked-in-git fact moved to its own bullet
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — SF-3: "on every run in the S2 run" provenance sentence deleted
  - C:\projects\investments\.agentic\projects\impact\capabilities\testing.md — SF-4: Is.AnyOf bullet split from the compile-error presentation bullet

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Docs lane has no Bash and the order's verification was NONE.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Carried SF-1 (testing.md package table omits Unity.Entities, which the TimeData bullet relies on) and the .\Tools\ commands in Running the suite stay open, per the non-goals

skill_calls:
  - none

risks:
  - The statement that an unpiped Unity.exe call "returns at once and $LASTEXITCODE is not set" follows the script comment at Run-UnityTests.ps1:71-72; it was not re-run
  - The F-1 fix keeps edits inside lines 34-45 as fenced; project.md:187-188 and AGENTS.md were not touched
