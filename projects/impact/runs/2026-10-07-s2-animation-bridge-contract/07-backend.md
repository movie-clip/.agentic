REPORT 2026-10-07-s2-animation-bridge-contract/07
status:      DONE
verdict:     NONE

changed:
  - Impact/Packages/athena.shared/Runtime/Components/Character/CharacterAnimatorSync.cs — Apply recomputes settling = currentMoveSpeed != targetMoveSpeed right after storing the new target, before StepSmoothing; the one-step-per-frame guard is unchanged

verification:
  command:   dotnet build Impact.sln; Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly
  result:    PASS
  detail:    dotnet build 0 errors. EditMode -CoreOnly total=164 passed=164 failed=0. PlayMode -CoreOnly total=26 passed=26 failed=0.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Regression test for CR-2 is a separate test-lane order: frame N the settle Update snaps to the old target and clears settling, then Apply in the same frame with a new MoveSpeedNormalized; the Animator MoveSpeed must keep approaching the new target on later frames with no further Apply
  - The sequence needs Update before Apply within one Time.frameCount; EditMode tests cannot reach it unless the test calls the private Update by reflection or runs in PlayMode

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, the change request named the exact line and the fix was one statement

risks:
  - The fix is verified by the existing suites and by reading the code. No test covers the CR-2 sequence, so a green run does not prove it
  - OnEnable cache reset and the HasApplied-on-controller-less limitation are untouched, per the order
  - TestResults-EditMode.xml and TestResults-PlayMode.xml were rewritten again by the runs (tracked run output, not S2 work)
