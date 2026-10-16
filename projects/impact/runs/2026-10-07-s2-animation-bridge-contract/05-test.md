REPORT 2026-10-07-s2-animation-bridge-contract/05
status:      DONE
verdict:     NONE

changed:
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationStateUpdateEditModeTests.cs — MoveSpeedNormalized_Characterization_AssumedRunSpeedSix replaced by MoveSpeedNormalized_FollowsSpeedReference (13 cases); adds AC-6 gait tests at scaled, explicit-7 and non-positive references
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationContractEditModeTests.cs — new, AC-5 field map reflection tests, Equals-covers-every-field test, CreateDefault pin (6 tests)
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationAuthoringEditModeTests.cs — new, AC-7 by construction, 4 tests, no real bake
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationBackendEditModeTests.cs — new, AC-3, AC-9 backend half, AC-11 system layer, G3 and lifecycle cases with the recording double (9 tests)
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationStateOrderingEditModeTests.cs — new, AC-8 sort and same-frame tests (8 cases), AC-9 and AC-10 state-world tests (4 tests), plus a stand-in mover system
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationBridgeEditModeTests.cs — appended 5 tests (AC-12 warn-once, swap, destroy; relink points at new backend); existing four test bodies untouched
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationEditModeWorld.cs — additive only: VisualKind.NoAnimator, CreateGameObjectlessCharacter, AttachBackend, GetLink, SetState/GetState, AddStateDriving, AddStateUpdateSystem, StepState
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationStateEditModeWorld.cs — additive only: CreateCharacterWithoutOwner, CreateCharacterOwnedByPlayer, SetSpeedReference
  - Impact/Assets/Tests/EditMode/Animation/RecordingAnimationBackend.cs (+.meta) — new test double implementing ICharacterAnimationBackend
  - Impact/Assets/Tests/EditMode/Animation/LogCapture.cs (+.meta) — new helper that counts captured log lines by type and text
  - Impact/Assets/Tests/PlayMode/Animation/RecordingAnimationBackend.cs (+.meta) — second copy of the double for the PlayMode assembly, on purpose (no shared test asmdef)
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationBackendPlayModeTests.cs (+.meta) — new, 4 PlayMode tests: AC-4 same sequence, AC-5 every field to its Animator parameter, AC-11 sentinel, G1/G3 skin swap
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationPlayModeHarness.cs — SetBridgeEnabled now also disables CharacterAnimationPresentationSystem; added CreateGameObjectlessCharacter, AttachBackend, GetAnimationState; stale comments updated

verification:
  command:   cd Impact; dotnet build Impact.sln; Run-UnityTests.ps1 EditMode -Filter Impact.EditModeTests.Animation; PlayMode -Filter Impact.PlayModeTests.Animation; EditMode -CoreOnly; PlayMode -CoreOnly (Git Bash, forward slashes)
  result:    PASS
  detail:    dotnet build 0 errors. EditMode Animation total=118 passed=118 failed=0. PlayMode Animation total=23 passed=23 failed=0. EditMode -CoreOnly total=164 passed=164 failed=0. PlayMode -CoreOnly total=26 passed=26 failed=0. No test red.

contract_notes:
  - none

pack_corrections:
  - capabilities/testing.md § Gotchas — add: "The NUnit in this project has no Is.AnyOf. Use Assert.That(new[] { a, b }, Does.Contain(x)). A compile error shows as 'Scripts have compiler errors', exit 1 after about 12 s; grep the log for 'error CS'"
  - capabilities/testing.md § Gotchas — add: "dotnet build Impact.sln cannot see new test files until a Unity run has regenerated the csproj, so the first Unity batchmode run is the real compile for new test files"

handoff:
  - Shared EditMode fixture additions on CharacterAnimationEditModeWorld: CreateGameObjectlessCharacter(), AttachBackend(entity) returning a RecordingAnimationBackend or AttachBackend(entity, backend), GetLink, SetState, GetState, AddStateDriving (no owner), AddStateUpdateSystem, StepState(entity, velocity), VisualKind.NoAnimator
  - Shared PlayMode harness additions: CreateGameObjectlessCharacter(), AttachBackend(entity, backend), GetAnimationState(entity). SetBridgeEnabled(false) now also stops CharacterAnimationPresentationSystem, which any later cost run needs
  - RecordingAnimationBackend (Recorded list, ApplyCount, Last) exists in both test assemblies, same name, one copy each. LogCapture(Count(type, text)) is EditMode only
  - CharacterAnimationStateEditModeWorld gains CreateCharacterWithoutOwner, CreateCharacterOwnedByPlayer(camera) and SetSpeedReference(entity, maxSpeed)., used with the component absent by simply not calling it
  - A stand-in mover (StandInCharacterMoverSystem, DisableAutoCreation, UpdateBefore ThirdPersonCharacterVariableUpdateSystem) lives in CharacterAnimationStateOrderingEditModeTests.cs. S3 can reuse the pattern to prove ordering
  - Human follow-up unchanged from the plan: git rm Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs and its .meta once the stub has shipped. Its tests (RetiredAuthoring_IsObsolete..., BaseCharacterPrefab_Has...) must then be dropped or edited
  - TestResults-EditMode.xml and TestResults-PlayMode.xml are tracked and now hold the last CoreOnly runs (164 and 26). Unity also touched generated .meta files. No scratch file was left in the repo; logs are under the session scratchpad
  - Integration gate: re-run the two -CoreOnly commands. Both were green here, and order 03's StartupRepro flake did not reproduce in the one PlayMode -CoreOnly run

skill_calls:
  - mattpocock-skills:tdd — not called, the order and plan § Reuse fixed the double and the real systems, so no fake-versus-real choice was open
  - mattpocock-skills:diagnosing-bugs — not called, no test resisted diagnosis; the only failure was a compile error (Is.AnyOf), fixed at once

risks:
  - AC-7 is unproved by a real bake: BakingUtility.BakeGameObjects is internal to Unity.Entities.Hybrid. Evidence is the prefab-content, obsolete-attribute, default-value and CreateDefault tests. The reviewer should know the double-authoring bake error path is by construction only
  - AC-6 says the single source is the character's maximum movement speed. Built and tested to D-6: an animation reference of 7, not GroundMaxSpeed (10 on BaseCharacter). A raised GroundMaxSpeed does not change the animation scale. Reviewer may read AC-6 differently
  - AC-10 is thin: the camera lookup runs only for a strafing character and IsStrafing is hard-coded false, so the test can only show neutral CameraRotationOffset and IsTurningInPlace. The with-camera path is unreachable and untested until S4
  - Shipped deviation tested as-is: CharacterAnimatorSync keeps a settle-only Update (order 04). Mapping_* tests and AC-5 MoveSpeed rely on it. No AC contradicts it, but plan § Contract said no Update
  - HasApplied becomes true even when the Animator adapter returned early for a controller-less Animator (order 04 risk). Not tested, because a test would pin a questionable behaviour. A controller assigned later gets nothing until the state next changes
  - The AC-8 sort test would go red without the UpdateAfter attribute (the state,variable insertion order) but I could not prove red by editing production. Red-on-old-code is by reasoning, not run
  - Cost figures are Editor batchmode with animators likely culled (cullingMode CullUpdateTransforms, no visible renderers), so Animator evaluation cost is mostly absent from A and B. See § Cost measurement for noise
  - Mapping and AC-5 tests wait up to 10 s of real time for the smoothed MoveSpeed to converge. A stalled Editor could time them out. It converged in well under a second here
  - AC-13 fixture edits: SetBridgeEnabled in the PlayMode harness was modified (a body change, not only additive), as the order required. No S1 test body was edited and no order 03 test was deleted except the one named

## Orchestrator brief
- Order 05 done: every AC-3..AC-12 has a green test, AC-13 S1 tests unchanged and green, the expected-red test is replaced by MoveSpeedNormalized_FollowsSpeedReference.
- Counts: EditMode Animation 118/118, PlayMode Animation 23/23, EditMode -CoreOnly 164/164, PlayMode -CoreOnly 26/26, dotnet build 0 errors.
- No production file touched. No finding that needs a backend fix. Findings for the reviewer are in risks (AC-6 reading, AC-7 no real bake, AC-10 thin, settle Update).
- Section "Cost measurement (before and after)": 150 characters, same N, repeats, machine. A minus B (mean) fell from 0.496 ms to 0.218 ms (second sample 0.122 ms). Noise is the same size as the gap; no threshold asserted.
- Section "Coverage table": maps AC-1..AC-15 to test names or recorded sections. AC-7 is partial by construction, nothing else is unproved.

## Cost measurement (before and after)

Same fixture, unchanged except that the bridge-off switch also disables CharacterAnimationPresentationSystem. Same machine (AMD Ryzen 7 7800X3D, RTX 4080 SUPER), Unity 6000.4.0f1, Editor PlayMode via batchmode, Editor otherwise idle, 150 characters, real Viking_BaseSkin_Visuals.prefab and AC_Polygon_Masculine, cullingMode CullUpdateTransforms (untouched), 60 warm-up frames, 300 sampled frames, 3 repeats per scenario. Wall-clock ms per frame. A is bridge on, B is bridge off (control). No time is asserted anywhere.

Before is copied from 03-test.md § Before-side measurement (unmodified production code). After is the PlayMode `-Filter "Impact.PlayModeTests.Animation"` run of this order. After (run 2) is the PlayMode `-CoreOnly` run, a second independent sample on the same machine.

Mean ms per frame, per repeat (1 / 2 / 3), then mean of the three:

| scenario | before | after (run 1) | after (run 2) |
|---|---|---|---|
| A moving, bridge on | 1.763 / 1.369 / 1.414 = 1.515 | 1.095 / 1.170 / 1.186 = 1.150 | 1.086 / 1.093 / 1.126 = 1.102 |
| B moving, bridge off | 1.116 / 0.969 / 0.972 = 1.019 | 0.920 / 0.953 / 0.923 = 0.932 | 0.919 / 1.000 / 1.021 = 0.980 |
| C idle, bridge on | 1.302 / 1.290 / 1.439 = 1.344 | 1.015 / 0.943 / 0.969 = 0.976 | 0.946 / 0.953 / 0.985 = 0.961 |
| C idle, bridge off | 0.953 / 0.979 / 0.979 = 0.970 | 0.922 / 0.900 / 0.962 = 0.928 | 0.880 / 0.905 / 0.932 = 0.906 |

Animation-path cost, A minus B (mean of means; per repeat in brackets):

| | before | after (run 1) | after (run 2) |
|---|---|---|---|
| moving, A minus B | 0.496 ms [0.647, 0.400, 0.442] | 0.218 ms [0.175, 0.217, 0.263] | 0.122 ms [0.167, 0.093, 0.105] |
| idle, C-on minus C-off | 0.374 ms [0.349, 0.311, 0.460] | 0.048 ms [0.093, 0.043, 0.007] | 0.056 ms [0.066, 0.048, 0.053] |

Difference (after minus before), moving: run 1 is minus 0.278 ms (56 percent lower), run 2 is minus 0.374 ms (75 percent lower). Idle: run 1 is minus 0.326 ms, run 2 is minus 0.318 ms. By median instead of mean the moving gap is 0.488 ms before, 0.186 ms (run 1) and 0.128 ms (run 2) after; the idle gap is 0.403 ms before and 0.049 ms (run 1) after.

Read the figures with this in mind:
- Noise. The A and B absolute means moved between sessions on their own: B (the control, same work in every session) read 1.019, 0.932 and 0.980 ms. That drift of 0.05 to 0.09 ms is a sizeable fraction of the after-side moving gap. The before-side A repeat 1 (1.763 ms) is a visible outlier that inflates the before mean; without it the before gap is about 0.42 ms. Per-repeat gaps after range 0.093 to 0.263 ms. The direction (lower after, much lower when idle) holds in all six after-side moving repeats and all six idle repeats; the size does not hold to better than about 0.1 ms.
- Animator culling. Every Animator reports CullUpdateTransforms and batchmode PlayMode has no visible renderers, so Animator evaluation is most likely culled in A and B alike. The gap measures mainly the state system, the bridge, the per-character apply and the settle Update, not clip evaluation of visible characters. A player build or visible characters would read higher on both sides. Culling was not changed (D-1).
- What the idle result shows. With nothing changing, the gap fell from about 0.37 ms to about 0.05 ms. That is what gating (AC-11) is meant to buy: before, the pull wrote the Animator parameters every frame whether or not they changed, and now an unchanged character is skipped entirely.
- GC. The recorder reads about 529 bytes per frame in every run including bridge-off, so it reports a constant floor and not the animation path. Treat it as non-informative.
- Each wall-clock delta includes the test's own per-frame driving of 150 bodies, in A and B alike, so it cancels in A minus B but sits inside every absolute figure.
- No threshold, no pass or fail, no scale slice raised (D-1). The human decides from the two figures.

## Coverage table

| AC | Proved by | Notes |
|---|---|---|
| AC-1 | EditMode CharacterAnimationStateUpdateEditModeTests (order 03, unchanged): Idle_GroundedAtRest_ReportsRestingLocomotion, Gait_AtSpeedBoundary_ReportsObservedGaitAndWalkFlag, and the jump, fall, landing, input-edge and start/stop cases | green after the refactor; gait boundaries held (D-4) |
| AC-2 | PlayMode CharacterAnimationMappingPlayModeTests Mapping_* (12, order 03, unchanged) | green after the refactor with the same expected values |
| AC-3 | EditMode CharacterAnimationBackendEditModeTests.Double_WithNoGameObject_ReceivesEveryStateChangeInOrder; CharacterAnimationBackendEditModeTests.CharacterWithNoOwnerAndNoCamera_UpdatesAndReachesTheBackend | no HybridGameObjectSpawned in the world |
| AC-4 | PlayMode CharacterAnimationBackendPlayModeTests.AnimatorAndDouble_ReceiveTheSameStateSequence | real Viking Animator and the double in one run; discrete parameters compared per step |
| AC-5 | EditMode CharacterAnimationContractEditModeTests: FieldMap_CoversEveryStateField_WithNoMissingStaleOrDuplicateEntry, FieldMap_OnlyParameterKindsCarryAnAnimatorParameter, FieldMap_ParameterTypeIsCompatibleWithTheFieldType, FieldMap_NamingTraps_StayAsDesigned, Equals_IsFalseWhenAnySingleFieldDiffers; PlayMode CharacterAnimationBackendPlayModeTests.EveryMappedField_ReachesItsAnimatorParameter | all 19 parameter-bound fields tested on the real controller, 0 skipped (no [S2-AC5] skip line logged) |
| AC-6 | EditMode MoveSpeedNormalized_FollowsSpeedReference, Gait_WithScaledSpeedReference_BoundariesFollowTheReference, Gait_WithDefaultSpeedReference_EqualsAc1Recording, SpeedReference_IsPerCharacter_TwoCharactersSameSpeedDifferentGait | reference 7 per D-6, not GroundMaxSpeed; see risks |
| AC-7 | EditMode CharacterAnimationAuthoringEditModeTests (4) and CharacterAnimationContractEditModeTests.CreateDefault_IsTheDocumentedNeutralState | PARTIAL by construction (plan § Authoring). Real bake not run, BakingUtility is internal. The visible-error path of the retired baker is not exercised |
| AC-8 | EditMode CharacterAnimationStateOrderingEditModeTests.StateSystem_SortsAfterTheCharacterUpdate_WhateverTheInsertionOrder (5 orders), StateComputedInFrameN_ReflectsTheMovementWrittenInFrameN (3 orders) | real state system and real ThirdPersonCharacterVariableUpdateSystem type in a real SimulationSystemGroup |
| AC-9 | EditMode CharacterAnimationStateIndependenceEditModeTests.CharacterWithNoOwnerComponent_StillReceivesStateUpdates; CharacterAnimationBackendEditModeTests.CharacterWithNoOwnerAndNoCamera_UpdatesAndReachesTheBackend | population at scale is S3 |
| AC-10 | EditMode CharacterAnimationStateIndependenceEditModeTests: PlayerCharacter_WithNoOrbitCamera_UpdatesWithNeutralCameraValues, PlayerCharacter_WhoseCameraEntityHasNoOrbitCamera_..., StandingPlayerCharacter_WithNoOrbitCamera_KeepsNeutralCameraValues | thin by design, see risks |
| AC-11 | EditMode UnchangedState_IsAppliedOnceAndThenNeverAgain, OnlyTheCharacterWhoseStateChanged_ReceivesAWrite, ReturningToAnEarlierState_IsAppliedAgain; PlayMode AnimatorBackend_DoesNotRewriteDiscreteParametersWhoseValueDidNotChange (gait, jumping, grounded sentinels); G3 in BackendAttachedLate_..., ReplacedBackendWithHasAppliedFalse_..., SkinSwap_WithUnchangedState_DeliversTheFullStateToTheNewInstance | the cost effect is in § Cost measurement, idle gap |
| AC-12 | EditMode CharacterAnimationBridgeEditModeTests: AnimatorlessInstance_WarnsOnce_AndTheStateKeepsUpdating, AnimatorlessInstance_SwappedForAnotherAnimatorlessOne_WarnsOnceMore, AfterTheAnimatorlessCharacterIsDestroyed_ALaterAnimatorlessCharacterWarnsOnceForItself, AnimatorlessInstance_DoesNotStopOtherCharactersFromLinking | warnings counted by captured log text, not private state; bookkeeping release is observed by behaviour only |
| AC-13 | the ten S1 tests (CharacterAnimationBridgeEditModeTests four, HybridGameObjectSystemBaseEditModeTests, SpawnHybridCharacterSkinSystemEditModeTests, SkinSwapAnimationPlayModeTests) | unchanged bodies, all green in both CoreOnly runs. Fixture edits additive except SetBridgeEnabled |
| AC-14 | 03-test.md § Before-side measurement | recorded by order 03 |
| AC-15 | this report § Cost measurement (before and after) | before, after (two samples), difference, noise and culling note; no threshold |
