REPORT 2026-10-07-s2-animation-bridge-contract/09
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd Impact; dotnet build Impact.sln; Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly (Git Bash, forward slashes, sequential, waited for Unity.exe to exit)
  result:    PASS
  detail:    dotnet build 0 errors, 17 warnings. EditMode -CoreOnly total=164 passed=164 failed=0. PlayMode -CoreOnly total=27 passed=27 failed=0 (26 plus the new CR-2 regression test, which passed). Counts read from the results XML test-run element.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-1 satisfied: tdd was called, its outcome is recorded in 08-test.md skill_calls. 05-test.md was left unedited by the order, so its own skill_calls line stays superseded rather than corrected. See § CR-1
  - CR-2 satisfied: the one-line fix is in CharacterAnimatorSync.cs and a PlayMode regression test for the exact sequence passes. See § CR-2
  - No new change request. The slice is ready for the reviewer gate; the 06 rulings (settle-only Update, HasApplied on a controller-less Animator) stand

skill_calls:
  - mattpocock-skills:codebase-design — not called, this re-run writes no new reuse or consistency judgment; it checks two fixes against the change requests I wrote after calling it in 06

risks:
  - The CR-2 test was not run against the pre-07 code. 08 argues red by reasoning and I agree with it from the code, but it is not an observed red
  - The CR-2 test needs the settle Update to run before the coroutine resumes in a frame. If that order changed it fails at its stated precondition instead of passing vacuously, so it cannot silently stop covering the sequence
  - 05-test.md still reads "tdd not called" next to the coupling bullets. 08 supersedes it in the ledger; anyone reading 05 alone sees the old contradiction
  - Mapping_* and the AC-5 MoveSpeed branch still poll up to 10 s of real time; 08 kept them on purpose after the tdd call and they converge in under a second here
  - OnEnable cache reset, the HasApplied limitation, and the human WIP are unchanged from 06 and not re-judged. TestResults-EditMode.xml and TestResults-PlayMode.xml were rewritten again by my runs

## Orchestrator brief
- Verdict: PASS. Build 0 errors. EditMode -CoreOnly 164/164, PlayMode -CoreOnly 27/27, read from the results XML.
- CR-1 satisfied: 08-test.md called tdd, confirmed the coupled tests assert the converged value through Apply and real frames, changed none of them.
- CR-2 satisfied: Apply now recomputes settling after storing the target; guard unchanged. New PlayMode test covers the snap-then-Apply sequence and passes.
- No new change request. Re-judge of untouched parts skipped per the order; 06 rulings stand.
- Next: reviewer gate. Sections: CR-1 · CR-2 · Scope of 07 and 08.

## CR-1

Satisfied. The request asked for a tdd call on the coupled tests, a record in `skill_calls`, and test changes only if the skill called for them.
- 08-test.md `skill_calls` records `mattpocock-skills:tdd` as called, with the outcome: Mapping_* and the AC-5 MoveSpeed branch assert the converged Animator value through public `Apply` and real frames, so they are not tied to the private `Update`, and none was changed.
- The call is a real one with a stated consequence (confirmed, one regression test added), which is what the request asked the line to carry.
- Gap against the request as written: CR-1 named 05-test.md as the place for the record. The order for 08 told the lane not to edit 05, so the record lives in 08 and 05 is marked superseded in 08's handoff. The substance is met; the old artifact remains uncorrected, noted in risks.

## CR-2

Satisfied.
- Code: CharacterAnimatorSync.cs, in `Apply`, `settling = currentMoveSpeed != targetMoveSpeed;` now sits directly after `targetMoveSpeed = state.MoveSpeedNormalized;` and before `StepSmoothing()`. The one-step-per-frame guard is untouched, as requested. Traced against the CR-2 failure sequence: after a same-frame snap, Apply sets settling true, the next frame's Update steps toward the new target, so MoveSpeed no longer freezes.
- Test: `MoveSpeed_TargetChangedOnTheFrameTheSettleSnaps_KeepsApproachingTheNewTarget` in CharacterAnimationBackendPlayModeTests.cs finds the snap frame by observation (MoveSpeed equals the old target exactly with no group update running), applies a new target in that same frame, then expects MoveSpeed to reach it with no further Apply. It passes in the PlayMode XML. It asserts the Animator parameter, which is the consequence named in CR-2, not an internal flag.
- The order also asked for the test in addition to CR-1; CR-2 itself had said a test was a separate order, and it is delivered.

## Scope of 07 and 08

- 07-backend.md changed one production file, one statement plus a comment. No asmdef, no other file. 08-test.md changed one test file, one added test, no existing test edited. Both stay inside their fences.
- No blocking finding in either, so no new change request. Guardrails 1, 2, 5 unaffected by these two edits.
