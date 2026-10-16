REPORT 2026-10-07-s2-animation-bridge-contract/04
status:      DONE
verdict:     NONE

changed:
  - Impact/Packages/athena.shared/Runtime/Components/Character/CharacterAnimationState.cs — IEquatable with hand-written Equals, CreateDefault(), link class gains Backend, LastApplied, HasApplied
  - Impact/Packages/athena.shared/Runtime/Components/Character/ICharacterAnimationBackend.cs (+.meta) — new, one method Apply(in CharacterAnimationState)
  - Impact/Packages/athena.shared/Runtime/Components/Character/CharacterAnimationContract.cs (+.meta) — new, field map (24 rows), parameter-name constants, FieldKind enum, mapping struct
  - Impact/Packages/athena.shared/Runtime/Components/Character/CharacterAnimationSpeedReference.cs (+.meta) — new optional component, DefaultMaxSpeed 7, MaxSpeed <= 0 means default
  - Impact/Packages/athena.shared/Runtime/Components/Character/CharacterAnimatorSync.cs — now a passive ICharacterAnimationBackend adapter: Initialize(), Apply with per-parameter write cache, smoothing and snap; no entity or world access
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAuthoring.cs — AnimationMaxSpeed field, baker uses CreateDefault() and adds CharacterAnimationSpeedReference
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs — obsolete stub, hidden from the Add Component menu, baker only logs an error
  - Impact/Packages/athena.shared/Runtime/Systems/CharacterAnimationBridgeSystem.cs — TryLink returns the backend, sets Backend and HasApplied=false on link and relink, no longer passes entity or world to the adapter
  - Impact/Packages/athena.shared/Runtime/Systems/CharacterAnimationStateUpdateSystem.cs — UpdateAfter ThirdPersonCharacterVariableUpdateSystem, owner and camera not required, speed from the reference component, AssumedRunSpeed and RunSpeedThreshold deleted
  - Impact/Packages/athena.shared/Runtime/Systems/CharacterAnimationPresentationSystem.cs (+.meta) — new SystemBase in PostEntityLifecycleGroup after the bridge, system-layer gate against LastApplied

verification:
  command:   dotnet build Impact.sln (twice); Run-UnityTests.ps1 -Platform EditMode -Filter Impact.EditModeTests.Animation; -Platform PlayMode -Filter Impact.PlayModeTests.Animation
  result:    PASS
  detail:    EditMode Animation total=36 passed=34 failed=2; the 2 are MoveSpeedNormalized_Characterization_AssumedRunSpeedSix (3f,0.5f) and (6f,1f), by assertion, as expected. PlayMode Animation 19/19. dotnet build 0 errors after Unity regenerated csproj.

contract_notes:
  - New public interface ICharacterAnimationBackend.Apply(in CharacterAnimationState) in Athena.Shared.Components. The test double in order 05 implements it
  - CharacterAnimationBridgeInitialized gains Backend, LastApplied, HasApplied (same class and file). A double is attached with new CharacterAnimationBridgeInitialized { Backend = double } on an entity that has CharacterEntity and CharacterAnimationState (G3)
  - CharacterAnimatorSync.Initialize(Entity, World) is gone; Initialize() takes no arguments. Update no longer pulls from the entity world. Order 05 helpers must not call the old signature
  - CharacterAnimatorSync inspector fields removed: all 20 parameter-name strings, maxMoveSpeed, writeOptionalParameters, speedDamping (now a const). Only showDebug remains. No prefab serialises them (plan GUID grep)
  - CharacterAnimationState implements IEquatable, gains CreateDefault(). Struct layout and field names unchanged, so the order 1 tests compile unchanged
  - New CharacterAnimationContract.Fields (24 rows: 14 Parameter, 5 OptionalParameter, 1 EcsOnly, 3 Retired) plus CharacterAnimationFieldKind and CharacterAnimationFieldMapping. The AC-5 test reflects over it
  - New optional component CharacterAnimationSpeedReference; CharacterAuthoring gains public float AnimationMaxSpeed (default 7). MoveSpeedNormalized is now saturate(speed / maxSpeed), 7 by default instead of 6
  - Test helper to adapt in order 05: CharacterAnimationPlayModeHarness.SetBridgeEnabled only toggles CharacterAnimatorSync.enabled and the state-system step. Apply still runs while a sync is disabled, so it must also disable the presentation system for the T-6 control run
  - CharacterAnimationAuthoring is [Obsolete] with the animator field and OnValidate removed. Nothing in tests or prefabs references it (grep and plan GUID check)
  - CharacterAnimationStateUpdateSystem query no longer requires OwnedByPlayerEntity. The harness comment saying the system requires it is now stale. CHARACTER_ANIMATION_SETUP.md, athena.shared PACKAGE_DOCUMENTATION.md, ARCHITECTURE_REVIEW.md lag (docs lane)

pack_corrections:
  - capabilities/backend.md § Definition of done for this lane — add: "From Git Bash, run the test script as powershell -ExecutionPolicy Bypass -File ./Tools/Run-UnityTests.ps1 ... with forward slashes. .\Tools\... loses its backslashes there and the script is not found (exit 127 or 1)"

handoff:
  - Convergence trap: the presentation gate stops Apply calls once state is steady, but the smoothed Animator MoveSpeed may not have reached its target. CharacterAnimatorSync therefore keeps a private Update that only finishes that approach (see risks). Mapping_* tests depend on it
  - Animator sentinel test (AC-11): after a first Apply set a discrete parameter such as IsGrounded to the opposite value, then Apply a state that changes only another discrete field, expect the sentinel to survive. Avoid changing MoveSpeedNormalized in that step, since smoothing writes MoveSpeed
  - Smoothing steps once per Time.frameCount, so repeated Apply calls in one frame (EditMode, a single editor frame) step it once. Tests of the MoveSpeed value should run across real PlayMode frames
  - G3 relink test: change the state, apply, replace the instance without changing the state; the bridge sets HasApplied=false so the new backend receives one full Apply
  - Controller-less warning text is [CharacterAnimatorSync] Animator on {name} has no runtime controller. Animation state is not applied. It fires once per adapter instance; S1 fixtures that use controller-less Animators now print it (4 plus 1 plus 2 lines in the runs here), no test asserts on logs
  - AC-8 sort test: type ThirdPersonCharacterVariableUpdateSystem is global-namespace in Athena.CharacterController.Runtime; the state system has UpdateAfter on it
  - AC-9, AC-10: the camera chain (owner, ThirdPersonPlayer, OrbitCamera) is read via ComponentLookup only inside the strafing branch, and isStrafing is hard-coded false. A test cannot reach that branch, so AC-10 reduces to neutral CameraRotationOffset and IsTurningInPlace=false with no camera
  - AC-6 boundary test: with MaxSpeed 14 the walk boundary is 3.5 and the sprint boundary 16 (1.75 and 8 times 2). Default stays exact because 7/7 = 1f
  - Human follow-ups: git rm Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs and its .meta once the stub has shipped; a later cleanup removes MoveDirection, VerticalVelocity, JumpTriggered
  - Full -CoreOnly runs were not part of this order's verification and were not run

skill_calls:
  - mattpocock-skills:diagnosing-bugs — not called, no fix attempt failed; the first Unity runs were green except the two expected reds

risks:
  - Deviation from plan § Contract (no Update): CharacterAnimatorSync has a private Update that does nothing unless MoveSpeed smoothing is unfinished. Without it the gate leaves the Animator MoveSpeed stuck short of target and the Mapping_* tests would time out. It reads no entity data and early-outs, but a reviewer may want a different fix
  - Because of the Update, an Animator output change versus today exists in one case: a target change in a frame where the adapter is settling is stepped one frame later (the frame guard prevents a double step). Within one frame, below any visible threshold
  - HasApplied becomes true even when the adapter returned early for a controller-less Animator. If a controller is assigned later the adapter gets nothing until the state next changes
  - Disabling a CharacterAnimatorSync no longer stops writes (Apply is pushed). It only stops the settle Update and resets the write cache on re-enable
  - dotnet build run before Unity regenerated the csproj failed with CS0246 on ICharacterAnimationBackend (new files invisible), as the plan warned. After the Unity run the build was clean, 0 errors, 17 warnings, none in my files
  - AC-6 still reads GroundMaxSpeed in the story; built to D-6 (reference 7). Unchanged from the plan's risk
  - OnEnable resets the cache, and Unity calls it when a sync is first added at runtime, so the first Apply is a full write. Intended, but it means the cache starts invalid regardless of Initialize
  - Unity regenerated generated meta details for the new files and touched TestResults-EditMode.xml and TestResults-PlayMode.xml (tracked run output); I edited none by hand

## Orchestrator brief
- Order 2 done: T-3 and T-4 implemented inside the fence; no file outside the scope list was touched.
- EditMode Animation 34/36: the only reds are MoveSpeedNormalized_Characterization_AssumedRunSpeedSix (3f,0.5f) and (6f,1f), as designed. PlayMode Animation 19/19.
- Gait D-4 held: all order 1 boundary tests stay green with the scaled boundaries at default.
- One declared deviation: CharacterAnimatorSync keeps a settle-only Update so smoothing converges under gating. See risks.
- Order 05 must extend SetBridgeEnabled to the presentation system and replace the expected-red test.
