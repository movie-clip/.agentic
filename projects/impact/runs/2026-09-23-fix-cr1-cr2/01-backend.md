REPORT 2026-09-23-fix-cr1-cr2/01
status:      DONE
verdict:     NONE

changed:
  - Impact\Packages\athena.core\Runtime\Systems\SessionStartDiagnosticSystem.cs — added `state.Enabled = false;` as the last line of `OnCreate`, matching `GameSessionSystem.cs:25`'s precedent for a one-shot, no-`OnUpdate` `ISystem`.

verification:
  command:   dotnet build Impact.sln && powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -Filter "Impact.EditModeTests.Core.SessionStartDiagnosticSystemEditModeTests"
  result:    PASS
  detail:    dotnet build: 0 Error(s), 17 pre-existing dependency-conflict warnings unrelated to this change. Run-UnityTests.ps1: test-run result="Passed" total="1" passed="1" failed="0" skipped="0", exit code 0.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - none
