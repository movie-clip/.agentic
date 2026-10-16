REPORT 2026-10-07-s2-animation-bridge-contract/08
status:      DONE
verdict:     NONE

changed:
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationBackendPlayModeTests.cs — added one regression test, MoveSpeed_TargetChangedOnTheFrameTheSettleSnaps_KeepsApproachingTheNewTarget (CR-2 sequence); no existing test changed

verification:
  command:   cd Impact; dotnet build Impact.sln; Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly (also -Filter on CharacterAnimationBackendPlayModeTests, 5/5)
  result:    PASS
  detail:    dotnet build 0 errors. EditMode -CoreOnly total=164 passed=164 failed=0. PlayMode -CoreOnly total=27 passed=27 failed=0.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The CR-2 test finds the snap frame by observation: with no group update, the first frame where Animator MoveSpeed equals the old target exactly is a frame the settle Update just snapped; it then writes the new state and runs harness.Tick().MoveNext() (Apply) in that same frame
  - PlayMode -CoreOnly is now 27 tests (was 26). EditMode unchanged at 164
  - 05-test.md was not edited, per the order; its skill_calls entry for tdd is superseded by this report

skill_calls:
  - mattpocock-skills:tdd — called for the coupled MoveSpeed tests. Confirmed Mapping_* and the AC-5 MoveSpeed branch unchanged: they assert the converged Animator value through public Apply and real frames, so any smoothing mechanism that converges passes; they are not coupled to the private Update itself. Added only the CR-2 regression test

risks:
  - tdd asks to confirm seams with the user first. Not possible in a dispatched lane; the seams (Apply plus the Animator MoveSpeed parameter) were fixed by the order and plan
  - The regression test would go red on the pre-07 code by reasoning: settling stays false after the same-frame snap, so MoveSpeed stays at 0.5 and the 10 s wait times out. Not run against old code, production not edited
  - The test depends on the settle Update running before the harness coroutine in a frame (coroutines resume after Update). If that order changed the precondition would not be reached and the test would fail at its precondition, not pass vacuously
  - The Mapping_* and AC-5 MoveSpeed waits still poll up to 10 s of real time. Kept deliberately; they converge in well under a second
