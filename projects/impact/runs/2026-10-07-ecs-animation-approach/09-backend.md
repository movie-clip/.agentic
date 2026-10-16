REPORT 2026-10-07-ecs-animation-approach/09
status:      DONE
verdict:     NONE

changed:
  - Impact/Packages/athena.shared/Runtime/Systems/CharacterAnimationBridgeSystem.cs — per-entity warned-instance Dictionary; no-Animator warning fires once per spawned instance; stale entries trimmed each frame

verification:
  command:   cd C:\projects\impact\Impact; dotnet build Impact.sln; Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly
  result:    PASS
  detail:    dotnet build: 0 errors, 17 warnings (pre-existing MSB3277). EditMode Core 45/45 passed, 0 failed. PlayMode Core 8/8 passed, 0 failed. 0 "has no Animator" lines in either result XML.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Untested by the suite: the warn-once path itself (Animator-less instance stays silent after the first warning; swapped-in Animator-less instance warns once more). Test lane may cover it if wanted; no test was required by CR-1.
  - Untested: trimming (entry dropped when the entity loses CharacterEntity, is destroyed, or its warned GameObject is destroyed).

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, the cause was stated in CR-1 and the fix was a bounded edit

risks:
  - Behaviour change on the warned path: an instance that was warned about is no longer re-probed each frame, so an Animator added to it at runtime later is not linked. CR-1 asked for exactly this (remember the instance, stop re-entering); a swap to a new instance links normally.
  - TryLink is now an instance method (it writes the warned map); it was private static. No external callers, as it was private.
  - Trim walks the dictionary every frame only while it is non-empty; it allocates nothing (reused List, struct enumerator), and the already-warned path is one Entity-keyed dictionary lookup.
