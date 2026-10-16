REPORT 2026-10-07-s2-animation-bridge-contract/10
status:      DONE
verdict:     PASS

changed:
  - C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-s2-animation-bridge-contract\10-review.md — this acceptance report; no repo file touched

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Read-only gate, order verification was NONE. No tests run by this gate (09-integration.md ran EditMode -CoreOnly 164/164 and PlayMode -CoreOnly 27/27). Anchor used: the story's AC text and test plan read against the test source and production source in Impact/Assets/Tests and Impact/Packages/athena.shared, not against the lanes' own reports. Suite counts are 09's, not re-observed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Close-out: human decides the 150-character cost from § Cost record. The gap is 0.496 ms before and 0.218 / 0.122 ms after, with noise near 0.1 ms and animators likely culled. D-1 sets no threshold
  - Close-out, human: git rm CharacterAnimationAuthoring.cs and its .meta under athena.shared/Runtime/Components/Authoring once the obsolete stub has shipped. Two tests in CharacterAnimationAuthoringEditModeTests must then be edited or dropped
  - Close-out, human: TestResults-EditMode.xml and TestResults-PlayMode.xml are tracked and modified by the runs. Revert or commit deliberately; the story changed no golden artifact
  - Close-out, docs lane: CHARACTER_ANIMATION_SETUP.md, athena.shared PACKAGE_DOCUMENTATION.md and ARCHITECTURE_REVIEW.md still describe the pull model and two authoring components (02 and 04 contract_notes)
  - Producer, S3 or S4 planning: the AC-10 with-camera path and the AC-12 bookkeeping-release path need a test once strafing exists or a seam to observe the warned map. See § Findings per AC

skill_calls:
  - none

risks:
  - AC-7 has no real bake. BakingUtility is internal to Unity.Entities.Hybrid. The both-authoring-components visible-error path (CharacterAnimationAuthoring.cs:18-23) is read, not run. Accepted by the plan the human approved in D-6; the human should know it is by construction
  - AC-12 third sentence cannot go red on a leak. The warned map is keyed by Entity, whose version changes on reuse, so a later character warns once even if the map were never trimmed. The story prescribed log counting, so this is the AC's limit, not a lane defect
  - AC-10 is thin. The camera lookup runs only for a strafing character and isStrafing is hard-coded false (CharacterAnimationStateUpdateSystem.cs:~112), so the neutral camera values hold trivially. The with-camera path is unreachable and untested until S4
  - AC-6 is met per D-6 (reference 7), not by GroundMaxSpeed (10 on BaseCharacter). Raising GroundMaxSpeed does not move the gait or the normalised speed. The AC text literally says maximum movement speed; the human accepted the reading
  - Test name SpeedReference_IsPerCharacter_TwoCharactersSameSpeedDifferentGait asserts gait 2 for both characters (CharacterAnimationStateUpdateEditModeTests.cs:400-401). The assertions are valid and differ on MoveSpeedNormalized; the name overstates it. Not blocking
  - The CR-2 regression test (MoveSpeed_TargetChangedOnTheFrameTheSettleSnaps_...) and the AC-8 sort test were argued red on old code but not observed red (08 risks, 05 risks). A green run proves them present, not discriminating
  - Cost figures are Editor wall-clock frame deltas with animators likely culled (CullUpdateTransforms, no visible renderers). A minus B mixes state system, bridge, apply and settle Update. The idle result (0.37 to 0.05 ms) is the clearest effect
  - Trust-state spot checks (synthetic badges, nullable dashes, market-data mocks) from the reviewer brief have no counterpart in this Unity project. Not applied; no UI or market-data caller is in scope
  - Story file 01-story.md still carries no approved status; D-2 records the human's approval. Status field is consistent with the run, only the file text lags
  - Fixture bodies of the ten S1 tests are unedited: git diff of the three modified test files shows additions only (bridge tests +115, EditMode world +99, PlayMode harness +123, zero lines removed)

## Orchestrator brief
- Verdict PASS. All 15 AC met; three carry a stated caveat (AC-7 no real bake, AC-10 thin, AC-12 release unobservable). None is routable to a lane as a defect.
- Test plan delivered item by item; see § Test plan delivery. Only the Authoring row is partial, as the plan said it would be.
- AC-14 and AC-15 are recorded figures per D-1 and D-5, both present in 03-test.md and 05-test.md. No threshold judged.
- Sections: Findings per AC · Test plan delivery · Cost record · Repo hygiene.

## Findings per AC

| AC | Result | Evidence |
|---|---|---|
| AC-1 | met | EditMode CharacterAnimationStateUpdateEditModeTests: Idle_GroundedAtRest_ReportsRestingLocomotion, Gait_AtSpeedBoundary_ReportsObservedGaitAndWalkFlag (9 boundary cases incl. 1.75, 5.0, 8.0), JumpAscent_*, Falling_*, Landing_RaisesJumpTriggeredForExactlyOneFrame, MovementInput_*, MovementStart_*, Movement_StartThenStop_*. Written green on unmodified code per 03 (36/36); 04 then showed only the two named expected reds. |
| AC-2 | met | PlayMode CharacterAnimationMappingPlayModeTests Mapping_* (12) on the real Viking prefab and AC_Polygon_Masculine, authored in 03 on unmodified code, not edited in 05, green after the refactor (PlayMode -CoreOnly 27/27 in 09). Discrete parameters exact, MoveSpeed within 1e-3. |
| AC-3 | met | EditMode CharacterAnimationBackendEditModeTests.Double_WithNoGameObject_ReceivesEveryStateChangeInOrder asserts zero HybridGameObjectSpawned in the world and the double's sequence equals the written one. |
| AC-4 | met | PlayMode CharacterAnimationBackendPlayModeTests.AnimatorAndDouble_ReceiveTheSameStateSequence: real Viking Animator and the double in one run, discrete parameters per step, Recorded equals the written sequence with consecutive duplicates collapsed. |
| AC-5 | met | EditMode CharacterAnimationContractEditModeTests.FieldMap_CoversEveryStateField_WithNoMissingStaleOrDuplicateEntry (reflection over the struct against CharacterAnimationContract.Fields; kinds Parameter, OptionalParameter, EcsOnly, Retired), Equals_IsFalseWhenAnySingleFieldDiffers; PlayMode EveryMappedField_ReachesItsAnimatorParameter reads each parameter back and counts tested plus skipped against the map. |
| AC-6 | met per D-6 | EditMode MoveSpeedNormalized_FollowsSpeedReference (13 cases), Gait_WithScaledSpeedReference_BoundariesFollowTheReference (references 14 and 3.5, boundaries tested exactly), Gait_WithDefaultSpeedReference_EqualsAc1Recording (27 cases). Source: CharacterAnimationStateUpdateSystem.cs scales both gait literals by maxSpeed / 7 and normalises by the same maxSpeed. Caveat: reference 7, not GroundMaxSpeed. |
| AC-7 | met with caveat | Single path: CharacterAuthoring.cs:33-35 bakes CreateDefault, the speed reference and runtime state. Both-path: CharacterAnimationAuthoring.cs:18-23 bakes nothing and logs an error naming the object. Tests: CharacterAnimationAuthoringEditModeTests (4), CreateDefault_IsTheDocumentedNeutralState. No bake was run; stated by the test lane and by the plan. |
| AC-8 | met | CharacterAnimationStateOrderingEditModeTests.StateSystem_SortsAfterTheCharacterUpdate_WhateverTheInsertionOrder (5 orders) and StateComputedInFrameN_ReflectsTheMovementWrittenInFrameN (3 orders, real state system, real ThirdPersonCharacterVariableUpdateSystem type, stand-in mover). Declared by [UpdateAfter(typeof(ThirdPersonCharacterVariableUpdateSystem))] at CharacterAnimationStateUpdateSystem.cs:17. |
| AC-9 | met | CharacterWithNoOwnerComponent_StillReceivesStateUpdates (no owner component, no player, no camera) and CharacterAnimationBackendEditModeTests.CharacterWithNoOwnerAndNoCamera_UpdatesAndReachesTheBackend. The query at CharacterAnimationStateUpdateSystem.cs no longer lists OwnedByPlayerEntity. |
| AC-10 | met with caveat | CharacterAnimationStateIndependenceEditModeTests: PlayerCharacter_WithNoOrbitCamera_UpdatesWithNeutralCameraValues, ..._WhoseCameraEntityHasNoOrbitCamera_..., StandingPlayerCharacter_.... Each asserts the update happened and CameraRotationOffset 0 and IsTurningInPlace false. Thin: see risks. |
| AC-11 | met | EditMode UnchangedState_IsAppliedOnceAndThenNeverAgain (count 1 after six unchanged frames and a rewrite), OnlyTheCharacterWhoseStateChanged_ReceivesAWrite, ReturningToAnEarlierState_IsAppliedAgain. PlayMode AnimatorBackend_DoesNotRewriteDiscreteParametersWhoseValueDidNotChange with sentinels on IsGrounded, IsJumping and CurrentGait, plus a changed-value control. Gate: CharacterAnimationPresentationSystem.cs and the write cache in CharacterAnimatorSync.cs:136-177. |
| AC-12 | met with caveat | CharacterAnimationBridgeEditModeTests: AnimatorlessInstance_WarnsOnce_AndTheStateKeepsUpdating (count 1 over 5 frames, MoveSpeed 5 and gait 2), ..._SwappedForAnotherAnimatorlessOne_WarnsOnceMore (2), AfterTheAnimatorlessCharacterIsDestroyed_ALaterAnimatorlessCharacterWarnsOnceForItself (2), ..._DoesNotStopOtherCharactersFromLinking. Warnings counted by captured log text via LogCapture. Caveat: release is behavioural only. |
| AC-13 | met | The ten S1 tests plus the green control are unedited (git diff of the modified test files is additions only) and green in 09's EditMode 164/164 and PlayMode 27/27. Fixture edits are additive. |
| AC-14 | met | 03-test.md § Before-side measurement: figure, AMD Ryzen 7 7800X3D and RTX 4080 SUPER, Unity 6000.4.0f1 Editor PlayMode batchmode (D-5), real Viking prefab and AC_Polygon_Masculine, 150 characters, 60 warm-up and 300 sampled frames, 3 repeats, on unmodified code. |
| AC-15 | met | 05-test.md § Cost measurement (before and after): same fixture, machine, N and repeats; both figures and the difference stated, with a second after-sample, the noise read and the culling note. No threshold and no scale slice raised (D-1). |

## Test plan delivery

- State update characterization (EditMode): delivered, CharacterAnimationStateUpdateEditModeTests, about 36 cases plus 40 expansions after 05. Covers every item the plan lists.
- Animator parity (PlayMode): delivered, CharacterAnimationMappingPlayModeTests, 12 tests.
- Contract and mapping: delivered, EditMode CharacterAnimationContractEditModeTests (6) and CharacterAnimationBackendEditModeTests (9); PlayMode CharacterAnimationBackendPlayModeTests (5).
- Single source of speed: delivered inside CharacterAnimationStateUpdateEditModeTests (MoveSpeedNormalized_FollowsSpeedReference, Gait_* and SpeedReference_IsPerCharacter).
- Authoring: partial by plan. CharacterAnimationAuthoringEditModeTests (4) chosen over a bake test; the test lane said which, as the story required.
- Ordering and independence: delivered, CharacterAnimationStateOrderingEditModeTests (8 cases) and CharacterAnimationStateIndependenceEditModeTests (4).
- Change-gating: delivered in EditMode with the double and in PlayMode with the sentinel technique.
- Degraded bridge: delivered, four new tests in CharacterAnimationBridgeEditModeTests plus the relink-backend test; log-counted.
- S1 regression: delivered, existing fixtures unedited, green.
- Measurement: delivered, CharacterAnimationCostMeasurement (2 tests); assertions are counts and gait coverage only, never a time.
- Invariants: boundary speeds, same-frame ordering and zero writes each have a dedicated test.
- The CR-2 regression test (08) is an addition beyond the plan and passes.

## Cost record

- Moving, A minus B, mean ms: 0.496 before; 0.218 after (run 1); 0.122 after (run 2). Idle: 0.374 before; 0.048 and 0.056 after. Source 05-test.md. Noise near 0.1 ms; the direction held in every after-side repeat. The human decides from these figures.

## Repo hygiene

- No stray files found in the animation test or athena.shared trees; every untracked file is a named deliverable with its .meta.
- Tracked TestResults-EditMode.xml and TestResults-PlayMode.xml are modified by the runs. Not an S2 output; see handoff.
- Human WIP (athena.contentmanagement, GameAssetLoad.cs, packages-lock.json) is not judged here.
