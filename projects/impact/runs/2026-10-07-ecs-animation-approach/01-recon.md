REPORT 2026-10-07-ecs-animation-approach/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon, order verification was NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Animation is 100% one hybrid pattern: ECS computes CharacterAnimationState, a MonoBehaviour (CharacterAnimatorSync) pulls it every Update and writes Mecanim parameters on an instantiated prefab GameObject; no Entities Graphics / Rigging / DOTS animation code exists, see § Animation inventory and § ECS to presentation bridge
  - Design lane should treat the skin swap path as the highest-risk seam: the bridge marker is never cleared on swap, so a swapped skin loses animation, see § Problems
  - Doc corrections owed: CHARACTER_ANIMATION_SETUP.md is largely stale versus code (parameter names, JumpTriggered meaning, system order, "NEW" authoring step), see § Doc claims verified
  - Packages installed but unused by code: entities.graphics 6.4.0, animation.rigging 1.4.1, cinemachine 2.10.6, timeline 1.8.11, see § Packages
  - Test gap: zero tests touch the animation systems, bridge, sync, hybrid spawn or skin-change system, see § Problems

skill_calls:
  - none

risks:
  - Runtime behaviour not executed: the skin-swap animation loss and the ghost-entity leak are derived from query definitions and cleanup-component semantics, not observed in Play mode
  - Not verified whether Viking skin prefabs carry CharacterAnimatorSync or only an Animator (asset config is recon 02 scope); the bridge handles both, so code-path conclusions hold either way
  - Player loop placement of the local world (MonoBehaviour Update before or after SimulationSystemGroup, hence 1-frame latency) is from memory of Entities behaviour, not read from Library/PackageCache docs
  - Not verified whether Entities Graphics renders anything in this project (it is installed and no code references it); no Unity.Rendering reference exists in any asmdef or script
  - Could not confirm whether baking throws when CharacterAuthoring and CharacterAnimationAuthoring are both on one prefab (both AddComponent CharacterAnimationState on the same entity)
  - Assets/Synty/**/SamplePlayerAnimationController.cs was read only as the parameter-name reference; it is vendor sample code, not Impact code

## Orchestrator brief
- Established: character animation = ECS state computation + MonoBehaviour pull into Mecanim Animator on an instantiated prefab GameObject (hybrid, hand-rolled). No Entities Graphics, Rigging, Playables or DOTS animation code anywhere in athena.*/com.ai.*/Assets/Scripts.
- Established: all animation code lives in athena.shared (11 files); charactercontroller, ai, gameplay contain no animation code. The Animator is driven from main-thread MonoBehaviour.Update, pulling via EntityManager.GetComponentData per character per frame.
- Established: animator parameter contract is the Synty AnimationBaseLocomotion controller (20 params, names hard-coded as inspector strings in CharacterAnimatorSync).
- Verdict: BLOCKING-class bug found, CharacterAnimationBridgeInitialized (cleanup component) is never removed, so after a skin swap the new GameObject is never linked, and it also keeps destroyed characters alive as ghost entities.
- Verdict: Strafing, turn-in-place, ForwardStrafe, CameraRotationOffset are dead (isStrafing hard-coded false); several state fields are never read by the sync (JumpTriggered, MoveDirection, VerticalVelocity, MovementInput*).
- Verdict: CHARACTER_ANIMATION_SETUP.md is mostly contradicted by code; ARCHITECTURE_REVIEW.md animation claims are mostly accurate but "covered by tests" is overstated (no animation/hybrid-spawn tests).
- Premise check: the order assumes possible "companion/hybrid or custom baking"; reality is neither Unity companion components nor Entities Graphics, but a custom HybridGameObject prefab instantiation system.
- Sections below: § Animation inventory (every component/system/authoring/MB with file:line), § ECS to presentation bridge (spawn to Animator trace), § Skin swap path, § Input to animation flow, § Packages (versions, used or not), § Doc claims verified (per-claim table), § Problems (numbered facts), § Where else animation is not (negative search results).
- Blocks dispatch: nothing. Unknowns are in risks (runtime not executed, Entities Graphics render use not checked).

## Animation inventory
All in `Impact/Packages/athena.shared/Runtime/` (asmdef `Athena.Shared.Runtime`, refs Unity.Entities.Hybrid, Entities, CharacterController, Physics; no Animation/Rigging/Graphics reference).

| Item | Kind | File:line | Role |
|---|---|---|---|
| CharacterAnimationState | IComponentData | Components/Character/CharacterAnimationState.cs:10 | 24-field Synty-shaped state, written by ECS system, read by MB |
| CharacterAnimationRuntimeState | IComponentData | same file:99 | Per-character smoothing/edge-detection scratch for the update system |
| CharacterAnimationBridgeInitialized | ICleanupComponentData | same file:113 | Marker that MB was linked; never removed (see Problems) |
| CharacterAnimationStateUpdateSystem | ISystem, [BurstCompile], SimulationSystemGroup | Systems/CharacterAnimationStateUpdateSystem.cs:15 (OnUpdate :39) | Derives state from KinematicCharacterBody, ThirdPersonCharacterControl, LocalTransform, OwnedByPlayerEntity, OrbitCamera |
| CharacterAnimationBridgeSystem | SystemBase (managed), PostEntityLifecycleGroup, UpdateAfter SpawnHybridCharacterSkinSystem | Systems/CharacterAnimationBridgeSystem.cs:14 (OnUpdate :16) | Finds/auto-adds CharacterAnimatorSync on spawned GO, calls Initialize(entity, world) |
| CharacterAnimatorSync | MonoBehaviour, [RequireComponent(Animator)] | Components/Character/CharacterAnimatorSync.cs:10 (Update :156, SyncAnimationState :164) | Pulls state with EntityManager.GetComponentData (:171), writes ~20 Animator params |
| CharacterAnimationAuthoring + Baker | MonoBehaviour + Baker | Components/Authoring/CharacterAnimationAuthoring.cs:10, Baker :15 | Adds CharacterAnimationState and RuntimeState; duplicate of CharacterAuthoring's baking |
| CharacterAuthoring + CharacterBaker | MonoBehaviour + Baker | Components/Authoring/CharacterAuthoring.cs:9, Bake :15; anim state :30-57 | Adds CharacterEntity, HybridGameObjectManualCreation (:29), CharacterAnimationState and RuntimeState (:30,:57) |
| HybridGameObject / HybridGameObjectManualCreation / HybridGameObjectSpawned | IComponentData(IEnableable) / tag / managed ICleanupComponentData | Components/Hybrid/HybridGameObject.cs:9,:15,:19 | Prefab ref (UnityObjectRef<GameObject>), opt-out of generic spawner marker, instance + transform key |
| HybridGameObjectAuthoring + HybridBaker | MonoBehaviour + Baker | Components/Hybrid/HybridGameObjectAuthoring.cs:7,:11 | Bakes default visual prefab ref onto the entity (TransformUsageFlags.None on its own entity, :24) |
| HybridGameObjectSystemBase | SystemBase (non-abstract despite name) | Systems/Hybrid/HybridGameObjectSystemBase.cs:13; Spawn :124, Despawn :155 | Generic spawner: Instantiate prefab, move to instance scene, register transform slot, add HybridGameObjectSpawned |
| HybridGameObjectTransformSystem | ISystem, [BurstCompile], UpdateAfter TransformSystemGroup | Systems/Hybrid/HybridGameObjectTransformSystem.cs:15; job :65 | IJobParallelForTransform copies LocalToWorld to the GO Transform (TransformAccessSlotMap) |
| SpawnHybridCharacterSkinSystem | ISystem (managed work), PostEntityLifecycleGroup | Systems/Player/SpawnHybridCharacterSkinSystem.cs:13 (OnUpdate :32) | Picks default or override skin prefab, calls HybridGameObjectSystemBase.SpawnGameObjectForEntity (:98), adds CharacterSkinInitialized |
| CharacterSkinChangeSystem | ISystem, PostEntityLifecycleGroup, UpdateBefore SpawnHybrid | Systems/Player/CharacterSkinChangeSystem.cs:13 (OnUpdate :30) | When desired skin differs: destroys GO, removes Spawned and SkinInitialized so Spawn system rebuilds |
| CharacterSkinCleanupSystem | ISystem | Systems/Player/CharacterSkinCleanupSystem.cs:10 | Releases skin refcount when character entity is destroyed |
| CharacterSkinSwitchCleanupSystem | ISystem | Systems/Player/CharacterSkinSwitchCleanupSystem.cs:7 | Not read in detail; cleans CharacterSkinSwitchRequest |
| CharacterSkinLoadSystem (static StartSwitchSkinProcess) | partial struct ISystem used as static helper (no OnUpdate) | Systems/CharacterSkinLoadSystem.cs:8, :10 | Sets desired skin on CharacterCameFromCrate, creates GameCrateLoadByGuid + CharacterSkinSwitchRequest |
| SkinCrateUpdateLoadedSystem | ISystem [BurstCompile], AssetLifecycleGroup | Systems/Crates/SkinCrateUpdateLoadedSystem.cs:13 | Registers SkinReference.skinPrefab into SkinCrateLoadedSingleton; TryGetSkinOverloadPrefabToUse :98 |
| SkinCrateLoadedSingleton | ICleanupComponentData with NativeHashMap | Components/SkinCrateLoadedSingleton.cs:19 | Skin guid to prefab ref and refcount/keep-alive crate entity |
| CharacterSkinCrate | ScriptableObject crate | Components/Authoring/Crates/CharacterSkinCrate.cs:14 | Holds EntityPrefabReference skinEntityPrefab (:19) plus child crates |
| CharacterSkinAuthoring + Baker | MonoBehaviour + Baker | Components/Authoring/Crates/CharacterSkinAuthoring.cs:8,:10 | Bakes SkinReference{skinPrefab = GameObject, skinAssetGuid} onto the skin entity prefab |
| SkinReference, CharacterSkinInitialized, CharacterSkinSwitchRequest, CharacterCameFromCrate | components | Components/Character/CharacterEntity.cs:33,:20,:26,:13 | Skin state; last two skin ones are cleanup components |
| EntityLifecycleGroup / PostEntityLifecycleGroup | system groups | Systems/EntityLifecycleGroup.cs:6,:13 | PostEntityLifecycle is OrderFirst in SimulationSystemGroup, UpdateBefore PredictedSimulationSystemGroup |
| SkinCheatCommand | cheat command (Assets) | Assets/Scripts/Runtime/Cheats/Commands/SkinCheatCommand.cs:7, calls StartSwitchSkinProcess :65 | Only first-party caller of the skin switch outside tests |
| Synty SamplePlayerAnimationController | vendor sample MB | Assets/Synty/AnimationBaseLocomotion/Samples/Scripts/SamplePlayerAnimationController.cs (hashes :39-76, writes :641-675) | Reference implementation whose parameter names and semantics CharacterAnimatorSync/State mirror |

Nothing animation-related exists in `athena.charactercontroller`, `athena.gameplay`, `athena.ai`, `com.ai.shared`, `com.ai.utility`, `athena.core`, `athena.contentmanagement`, `athena.sceneslice`, or `Assets/Scripts` outside SkinCheatCommand (grep for Animator/Animation/Playable/SetFloat/SetBool: zero hits). `com.projectdawn.navigation` has only Samples~ (AgentLocomotionRootMotion, Zerg UnitAnimationSystem), not compiled into the game.

## ECS to presentation bridge
Spawn to animated mesh, end to end:
1. Authoring: character prefab has `CharacterAuthoring` (baker adds CharacterEntity, HybridGameObjectManualCreation, CharacterAnimationState, CharacterAnimationRuntimeState, :26-57) plus `HybridGameObjectAuthoring` that bakes `HybridGameObject{Prefab=UnityObjectRef<GameObject>}` (HybridGameObjectAuthoring.cs:25). The visual GameObject prefab (contains Animator and mesh) is a normal prefab, not baked to entity render components.
2. Instantiate: `CharacterUtility.SpawnCharacterWithDefaultSkin` instantiates the baked character entity prefab and adds CharacterCameFromCrate (Utils/CharacterUtility.cs:15,:66).
3. Visual spawn: `SpawnHybridCharacterSkinSystem` (query :20-23, needs CharacterEntity+HybridGameObject+ManualCreation, none of SkinInitialized/Spawned) optionally swaps `hybridGameObject.Prefab` for the override skin prefab (:64-70), then `HybridGameObjectSystemBase.SpawnGameObjectForEntity` does `Object.Instantiate(prefab)` (HybridGameObjectSystemBase.cs:131), moves it into a per-world instance scene (:137), inserts the Transform in `TransformAccessSlotMap` (:143), and ECB-adds managed `HybridGameObjectSpawned{Instance}` (:146).
4. Transform follow: `HybridGameObjectTransformSystem` job copies LocalToWorld to the GO Transform after TransformSystemGroup (:51-55, Execute :72-79). Position, rotation and lossy scale only, no bone/skeleton data crosses the boundary.
5. Animator link: `CharacterAnimationBridgeSystem` (query :21-25) finds `CharacterAnimatorSync` on the instance root (:32); if absent, finds first Animator in children and AddComponent<CharacterAnimatorSync> there (:41-44), calls `Initialize(entity, world)` (:36/:45), which caches EntityManager and forces `applyRootMotion=false` (CharacterAnimatorSync.cs:149-152). Adds CharacterAnimationBridgeInitialized.
6. Per-frame pull: `CharacterAnimatorSync.Update()` (:156) calls `SyncAnimationState()` which does `entityManager.GetComponentData<CharacterAnimationState>(linkedEntity)` (:171) then ~15 unconditional SetFloat/SetInteger/SetBool calls (:181-195) plus 5 optional ones gated by a one-time `animator.parameters` scan (:197-225, :234-266).
7. Mecanim plays clips; the Animator Controller, clips, avatar and renderers all live on the skin/visual prefab (asset config out of scope, recon 02).
Not used: Entities Graphics rendering of skinned meshes, companion components, UnityEngine.Animations.Rigging, Playables, Animator-in-entity (no `Animator` managed component on entities, no `AddComponentObject(animator)`). The only managed link is `HybridGameObjectSpawned.Instance` (HybridGameObject.cs:19-24).

Ordering facts (code): PostEntityLifecycleGroup is first in SimulationSystemGroup (EntityLifecycleGroup.cs:10-13). Inside it: CharacterSkinChangeSystem, then SpawnHybridCharacterSkinSystem, then CharacterAnimationBridgeSystem (`UpdateBefore`/`UpdateAfter` attributes). HybridGameObjectSystemBase and HybridGameObjectTransformSystem carry no UpdateInGroup (default SimulationSystemGroup; the transform system has UpdateAfter TransformSystemGroup). CharacterAnimationStateUpdateSystem is in SimulationSystemGroup with no ordering attributes (:14).

## Skin swap path
1. Trigger: `SkinCheatCommand` (Assets/Scripts/.../SkinCheatCommand.cs:65) calls `CharacterSkinLoadSystem.StartSwitchSkinProcess` (Systems/CharacterSkinLoadSystem.cs:10): sets `PlayerResolvedCharacterCrates.SkinCrateGuid`, writes `CharacterCameFromCrate.SkinCrateGuid` (:33-34), creates a `GameCrateLoadByGuid` entity (:47) and adds/updates `CharacterSkinSwitchRequest` (:53-68).
2. Load: crate load pipeline loads `CharacterSkinCrate.skinEntityPrefab` (CharacterSkinCrate.cs:19, :36-41); baked `CharacterSkinAuthoring` makes `SkinReference{skinPrefab}` (CharacterSkinAuthoring.cs:18-21); `SkinCrateUpdateLoadedSystem` registers it in `SkinCrateLoadedSingleton` (SkinCrateUpdateLoadedSystem.cs:80).
3. Rebuild: `CharacterSkinChangeSystem` waits for crate loaded and registered prefab (:93-119), releases old skin ref (:125), erases transform slot (:129-132), `Object.Destroy(instance)` (:136), re-enables HybridGameObject (:139-142), removes HybridGameObjectSpawned and CharacterSkinInitialized (:144-145).
4. Respawn: next tick `SpawnHybridCharacterSkinSystem` picks the new prefab (:62-70), instantiates, re-adds CharacterSkinInitialized.
5. Animation touchpoint: nothing in the swap path removes or re-creates the animation link. `CharacterAnimationBridgeInitialized` stays on the entity, and the bridge query is `WithNone<CharacterAnimationBridgeInitialized>` (CharacterAnimationBridgeSystem.cs:24). The old CharacterAnimatorSync dies with the destroyed GO (its OnDestroy nulls fields, :268-273); the new GO gets no sync. See § Problems item 1.
Note the default prefab: SpawnHybrid overwrites `hybridGameObject.Prefab` on the entity with the override (:68) and the swap system only ever re-resolves from CharacterCameFromCrate; returning to the default skin relies on `IsDefaultSkin` and the entity's Prefab field having been overwritten earlier (default prefab ref is lost after the first override unless the default is re-resolved; not traced further, flagged in risks of design work, see § Problems item 11).

## Input to animation flow
1. Keyboard: `ThirdPersonPlayerInputsSystem` (SystemBase, SimulationSystemGroup OrderFirst, UpdateBefore FixedStep) reads `Keyboard.current` WASD/space and `Mouse.current` (charactercontroller ThirdPersonPlayerSystems.cs:15-46) into ThirdPersonPlayerInputs; no null-check on Keyboard.current/Mouse.current.
2. Fixed step: `ThirdPersonPlayerFixedStepControlSystem` (:86-138) converts input to camera-relative world `ThirdPersonCharacterControl.MoveVector` (:128-129) and Jump (:132), unless `ThirdPersonCharacterExternalInput.IsActive`. AI/move-to-target path: `ThirdPersonCharacterMoveToTargetSystem` writes ExternalInput.WorldMoveVector, `ThirdPersonCharacterExternalInputSystem` copies it to MoveVector (ThirdPersonCharacterExternalInputSystem.cs:34).
3. Physics/movement: `ThirdPersonCharacterPhysicsUpdateSystem` (KinematicCharacterPhysicsUpdateGroup) and `ThirdPersonCharacterVariableUpdateSystem` (after FixedStep, before TransformSystemGroup, ThirdPersonCharacterSystems.cs:74-79) move the character and update `KinematicCharacterBody` (IsGrounded, RelativeVelocity).
4. Animation state: `CharacterAnimationStateUpdateSystem` (Burst, main-thread foreach, not a job) reads MoveVector (:54), RelativeVelocity (:59), IsGrounded (:63), LocalTransform rotation (:68-70), owning player's OrbitCamera.PlanarForward via EntityManager lookups (:233-250), and writes CharacterAnimationState (:130-167): MoveSpeed, VerticalVelocity, IsGrounded, IsJumping (!grounded && vy>0.1), FallingDuration, IsWalking, CurrentGait (thresholds 1.75/5/8, :17-19, :271-289), MovementInput Tapped/Pressed/Held, IsStarting, LocomotionStartDirection, Strafe/Shuffle/Forward values.
5. Pull: `CharacterAnimatorSync.Update()` reads it (above). MoveSpeed is re-normalised in the MB by `maxMoveSpeed=7` (:77-78, :173-175) with an extra smoothing lerp (:177-179); the ECS system also computes MoveSpeedNormalized with AssumedRunSpeed=6 (:25,:131), which the MB ignores unless maxMoveSpeed<=0.
6. Written Animator params (all names are inspector strings, :14-67): MoveSpeed, CurrentGait, IsGrounded, IsJumping, FallingDuration, IsWalking, LocomotionStartDirection, StrafeDirectionX/Z, ShuffleDirectionX/Z, ForwardStrafe, IsStrafing (as float), CameraRotationOffset, IsTurningInPlace; optional IsStarting, IsStopped, MovementInputTapped/Pressed/Held. Synty sample also uses InclineAngle, IsCrouching, LeanValue, HeadLook/BodyLook which Impact never writes.
7. Edge: the query requires `ThirdPersonCharacterControl` and `OwnedByPlayerEntity` (:48), so a character without an owner entity (or AI character lacking ThirdPersonCharacterControl) gets no animation updates. OwnedByPlayerEntity is baked on all CharacterAuthoring entities (CharacterAuthoring.cs:27).
8. Latency (unverified): MonoBehaviour Update vs. appended SimulationSystemGroup placement in the player loop probably means the MB reads last frame's state.

## Packages
Source: Impact/Packages/manifest.json and packages-lock.json. "Used" means referenced by any asmdef or first-party .cs.

| Package | Version (lock) | Used in code? |
|---|---|---|
| com.unity.entities | 6.4.0 (manifest 6.4.0) | Yes, everywhere |
| com.unity.entities.graphics | 6.4.0 | No: zero references to Unity.Rendering/Entities.Graphics in any asmdef/.cs. Whether it renders any subscene content is unverified |
| com.unity.feature.characters-animation | 1.0.0 (builtin feature set) | Pulls Animation Rigging 1.4.1, Timeline 1.8.11, Cinemachine 2.10.6, FBX Exporter 5.1.5; none used by code |
| com.unity.animation.rigging | 1.4.1 (depth 1, via feature) | No (no UnityEngine.Animations.Rigging reference) |
| com.unity.timeline | 1.8.11 | No code reference found |
| com.unity.cinemachine | 2.10.6 (transitive) | No code reference found; camera is the custom OrbitCamera system |
| com.unity.modules.animation | 1.0.0 | Used implicitly via UnityEngine.Animator in athena.shared (noEngineReferences false) |
| com.unity.render-pipelines.universal | 17.4.0 | Not referenced from code (rendering config only) |
| com.unity.charactercontroller | 1.4.1 (manifest); lock shows its deps as physics 1.3.14/entities 1.3.14 while physics resolves to 1.4.2 | Yes (KinematicCharacterBody) |
| com.unity.physics | 1.4.2 (transitive, depth 1) | Yes |
| com.unity.inputsystem | 1.19.0 | Yes (ThirdPersonPlayerInputsSystem under ENABLE_INPUT_SYSTEM) |
| com.unity.burst / mathematics / collections | 1.8.28 / 1.3.3 / 6.4.0 | Yes |
| com.projectdawn.navigation | embedded 4.1.1 | Not animation-related in-game; Samples~ include root-motion and Zerg animation samples (not compiled) |
| com.unity.pipeline | 0.7.0-exp.1 | Editor tooling, unrelated |
No third-party animation library (Rukhanka, Kinematica, Animation package for DOTS, GPU instancing animation) is installed. Not checked in Library/PackageCache docs for Entities Graphics skinning capabilities, since design is out of scope.

## Doc claims verified
CHARACTER_ANIMATION_SETUP.md (Impact/CHARACTER_ANIMATION_SETUP.md):
| Claim (line) | Status | Evidence |
|---|---|---|
| ECS owns state selection, clip playback stays in Mecanim (:10) | Verified | State system + CharacterAnimatorSync |
| Architecture diagram StateUpdate to CharacterAnimationState to CharacterAnimatorSync to Animator (:14-26) | Verified | See § Animation inventory |
| "If your prefab uses CharacterAuthoring, animation state components are baked automatically" (:41) | Verified | CharacterAuthoring.cs:30,:57 |
| CharacterAnimationAuthoring still available for standalone prefabs (:43) | Partly: exists but duplicates CharacterAuthoring's AddComponent of the same types; "Example: Full Character Setup" (:371-375) and Next Steps (:406) tell you to add both | Contradicted by the doc's own example; baking behaviour on duplicate AddComponent unverified |
| Controller params table: MoveSpeed, CurrentGait, IsGrounded, IsJumping, FallingDuration, IsWalking, LocomotionStartDirection (:49-57) | Verified (subset of the 20 actually written) | CharacterAnimatorSync.cs:181-195 |
| Example Animator transitions: "Speed > 0.1", "Jump trigger", "VerticalVelocity < -0.5" (:70-76) | Contradicted | No Jump trigger, no Speed or VerticalVelocity parameter is written by code |
| Sync settings: "Speed Parameter: Speed", MoveX, MoveZ, "Jump Trigger", "VerticalVelocity Parameter", "Speed Smooth Time" (:92-100) | Contradicted | Fields are moveSpeedParameter="MoveSpeed" etc.; no MoveX/MoveZ/Jump/VerticalVelocity fields; smoothing field is speedDamping (:75) |
| "Option A: system will auto-add CharacterAnimatorSync" (:80-81) | Verified | Bridge :41-44 |
| StateUpdate system "runs every frame, reads KinematicCharacterBody/ControlStatus/LocalTransform" (:109-113) | Verified (also reads OrbitCamera and OwnedByPlayerEntity, undocumented) | StateUpdate :47-48, :233-250 |
| Bridge "runs once when character spawns" (:115) | Contradicted | SystemBase runs every frame (no RequireForUpdate); it relies on the marker to stop re-linking, and the marker is never cleared on respawn |
| CharacterAnimatorSync.Update reads state every frame (:122) | Verified | :156-171 |
| CharacterAnimationState fields table incl. JumpTriggered "Jump input this frame?" (:133-141) | Contradicted for JumpTriggered | Computed as landing edge `isGrounded && !runtime.WasGrounded` (StateUpdate :137); also the table omits 17 of 24 fields; MoveDirection comment says X/Z but it is float2 X/Y |
| System update order: VariableUpdate, TransformSystemGroup, StateUpdate, PostEntityLifecycle (Spawn then Bridge), MB Update (:329-348) | Contradicted | StateUpdate has no ordering attribute (:14); PostEntityLifecycleGroup is OrderFirst (EntityLifecycleGroup.cs:10), i.e. before VariableUpdate and Transform |
| Files created list (:354-365) | Verified | All five files exist |
| Root motion: No, applyRootMotion off (:416) | Verified | Initialize sets applyRootMotion=false (:151) |
| Multiplayer: "Yes, as long as each client runs the animation systems" (:425-426) | Unverifiable | No netcode package; single local world; PredictedSimulationSystemGroup exists as a custom group only |
| "Disable CharacterAnimatorSync to stop animation" (:429) | Verified (trivially) | |
| Performance tip: "Already implemented - we cache StringToHash in Awake" (:316-317) | Verified | Awake :117-141 |
| Status "Production Ready", created Nov 2025, "Last Updated Nov 1, 2025" (:433-435) | Contradicted | File has been edited since (Synty parameters); the doc is internally split between a Speed/MoveX/Jump era and the Synty era |

ARCHITECTURE_REVIEW.md (Impact/ARCHITECTURE_REVIEW.md):
| Claim | Status | Evidence |
|---|---|---|
| Hybrid visual pipeline files list (:188-191) | Verified | all four exist |
| "ECS gameplay state and GameObject visuals are clearly separated" (:194) | Verified, with caveat | Separation exists; the MB reads ECS directly through EntityManager so the dependency is bi-directional |
| "still very stateful and order-sensitive; depends on manual hybrid markers and cleanup components" (:197-199) | Verified | HybridGameObjectManualCreation, 3 cleanup components, see § Problems |
| Skin switching "performs real on-demand crate loading and deferred visual rebuild" (:167,:178) | Verified | CharacterSkinLoadSystem :47, CharacterSkinChangeSystem :93-119 |
| Lists `Systems/AuthoritativeCharacterSkinLoadSystem.cs` (:162) | Contradicted (stale) | Renamed to CharacterSkinLoadSystem.cs (git status shows rename) |
| "Targeted EditMode coverage exists for crates, skins..." and "should keep explicit logging/tests around core transitions" (:211,:204) | Partly contradicted | Skin tests cover only StartSwitchSkinProcess and SkinCrateLoadedSingleton refcounting (CrateSystemEditModeTests.cs:332-542); no test covers SpawnHybridCharacterSkinSystem, CharacterSkinChangeSystem, bridge, state update or sync |
| "ECS singleton state heavy" (:259) | Verified | SkinCrateLoadedSingleton, HybridGameObjectSingleton, etc. |
| `CharacterPossessionSystem` still a stub (:171) | Not checked (not animation) | |
Other docs: athena.shared/PACKAGE_DOCUMENTATION.md:97 says the bridge "is initialized repeatedly instead of being marked as initialized once" (Contradicted: the marker exists at CharacterAnimationState.cs:113, the real defect is the opposite, it is never reset); :69 and PACKAGE_ARCHITECTURE.md reference the renamed `AuthoritativeCharacterSkinLoadSystem` (stale); PACKAGE_ARCHITECTURE.md:169-173 lists SpawnHybrid before HybridGameObjectSystemBase as sequential steps (not an enforced order).

## Problems
Facts only.
1. Bridge marker never cleared: `CharacterAnimationBridgeInitialized` is `ICleanupComponentData` (CharacterAnimationState.cs:113). It is added at Bridge :37/:46 and removed by no system (grep: only those two writes). `CharacterSkinChangeSystem` removes HybridGameObjectSpawned and CharacterSkinInitialized (:144-145) but not the bridge marker, and the bridge query is `WithNone<CharacterAnimationBridgeInitialized>` (Bridge :24). After any skin swap the new GO has no linked CharacterAnimatorSync.
2. Ghost entities: because the marker is a cleanup component never removed, destroying a character entity leaves it alive as a cleanup-only shell permanently (DestroyEntity cannot finish until all cleanup components are removed). CharacterSkinCleanupSystem and HybridGameObjectSystemBase despawn only remove their own cleanup components. Not run-verified.
3. Dead strafing path: `var isStrafing = false;` (StateUpdate :156) then used throughout; the strafe branch (:180-208), ForwardStrafe damping, CameraRotationOffset and IsTurningInPlace (:224) never activate; ShuffleDirection is forced to (0,1). The OrbitCamera lookup (:83, :233-250) therefore only feeds dead code. Unused locals: `cameraForward`, `moveDirectionWorld` partially.
4. Redundant/odd gait logic: GetCurrentGait returns 2 for speeds in [1.75,5) and again for [5,8) (:283, :288); the RunSpeedThreshold constant (:18) is only ever used for that duplicate, gait 3 only at >=8. Thresholds (1.75/5/8, AssumedRunSpeed 6) are hard-coded and independent of ThirdPersonCharacterComponent.GroundMaxSpeed (ThirdPersonCharacterComponent.cs:12) and of CharacterAnimatorSync.maxMoveSpeed=7 (:78). Three separate speed normalisation constants.
5. Unread state fields: CharacterAnimationState.JumpTriggered, MoveDirection, VerticalVelocity, MoveSpeedNormalized (fallback only), and the MB writes IsStarting etc. only if the controller exposes them. JumpTriggered is a landing edge despite its name (StateUpdate :137). Duplicate field maintenance between state struct, authoring bakers (two copies of a 24-field initializer: CharacterAuthoring.cs:30-56, CharacterAnimationAuthoring.cs:22-48) and MB.
6. Duplicate baking: CharacterAuthoring and CharacterAnimationAuthoring both AddComponent CharacterAnimationState and RuntimeState. Both on one prefab is what CHARACTER_ANIMATION_SETUP.md:371-375 recommends; consequence unverified (see risks).
7. Per-frame managed cost: one MonoBehaviour per character does `EntityManager.GetComponentData` in Update (:171), which forces a sync point on pending jobs touching that component (the Burst state system is main-thread, so the cost is the structural sync, not a job). ~15 to 20 Animator parameter sets per character per frame, unconditional even when values are unchanged. `animator.parameters` allocates once per Initialize (:241). The state update itself iterates on the main thread, uses `state.EntityManager.Exists/HasComponent/GetComponentData` per character per frame for the camera (:237-248) and is not a job. All animation, hybrid spawn and skin systems except the transform copy and the state system are managed `SystemBase`/non-Burst.
8. Initialization race/fragility: Bridge uses `GetComponent<CharacterAnimatorSync>()` on the instance root only (:32); if sync lives on a child Animator object it is not found, then `GetComponentInChildren<Animator>` plus AddComponent could create a second sync on the same object. `Debug.Log` on each auto-add (:48) and ~12 `Debug.Log/LogWarning` per spawn/switch in SpawnHybrid, SkinChange, SkinCrateLoadedSingleton.
9. Two spawners for the same component: `HybridGameObjectSystemBase` HandleSpawns query is any `HybridGameObject` without `HybridGameObjectSpawned` (:52-55, :81-83) and does not exclude `HybridGameObjectManualCreation`, which characters carry (CharacterAuthoring.cs:29). It is non-abstract, placed in default SimulationSystemGroup and has no order relative to PostEntityLifecycleGroup; SpawnHybridCharacterSkinSystem requires SkinCrateLoadedSingleton and GameCrateSingleton (:25-29) to run. If those singletons are absent when the character appears, the generic spawner could instantiate the default prefab without creating CharacterSkinInitialized. Not run-verified; ManualCreation's purpose is documented in PACKAGE_DOCUMENTATION.md:77 as the opt-in to the manual path, but nothing in the generic query honours it.
10. Name/shape incoherence: `HybridGameObjectSystemBase` is concrete; `CharacterSkinLoadSystem` is an ISystem with no OnUpdate used as a static helper (CharacterSkinLoadSystem.cs:8-10), which the engine will still instantiate; Burst attribute missing on `HybridGameObjectTransformSystem.OnUpdate`/OnCreate (:13 only on struct); `SpawnHybridCharacterSkinSystem` is not Burst and carries unused parameters (`gameCrateSingleton`, `skinCrateLoadedSingleton` mostly passed through, `timeElapsedTime`). `CharacterUtility.cs:64` has a commented-out RemoveComponent<HybridGameObjectManualCreation>; CharacterAuthoring.cs:73-76 has a commented-out CharacterSkinDefaultVisuals block (dead code).
11. Default-skin return path: SpawnHybrid assigns the override prefab into `HybridGameObject.Prefab` (:68). The prefab field is the only stored default reference (CharacterSkinDefaultVisuals is commented out, CharacterAuthoring.cs:73-76). The code path that restores the default visuals when desiredSkin becomes default (`CharacterSkinChangeSystem` :55-59) re-enables the component but nothing in code restores the original prefab ref. Could not confirm whether this is handled elsewhere; worth a targeted check.
12. Test gap: no EditMode/PlayMode test references CharacterAnimationStateUpdateSystem, CharacterAnimationBridgeSystem, CharacterAnimatorSync, HybridGameObjectSystemBase, HybridGameObjectTransformSystem, SpawnHybridCharacterSkinSystem or CharacterSkinChangeSystem (grep over Assets/Tests for Animat|Animator|HybridGameObject|CharacterSkin returns only StartSwitchSkinProcess and SkinCrateLoadedSingleton tests, CharacterCrateLookupEditModeTests.cs:35).
13. Package surface mismatch: manifest pulls the characters-animation feature set (Rigging, Timeline, Cinemachine, FBX Exporter) and Entities Graphics with no code use; AGENTS.md package list does not mention animation at all.
14. Doc incoherence: CHARACTER_ANIMATION_SETUP.md mixes two parameter vocabularies (Speed/MoveX/MoveZ/Jump trigger versus Synty MoveSpeed/CurrentGait), see § Doc claims verified; stale rename in two docs.
15. Input system fragility (adjacent): ThirdPersonPlayerInputsSystem dereferences `Keyboard.current`/`Mouse.current` with no null check (ThirdPersonPlayerSystems.cs:33-37), runs for every ThirdPersonPlayer, and is inside `#if ENABLE_INPUT_SYSTEM`.
16. Update-time semantics: the state system uses `SystemAPI.Time.DeltaTime` in SimulationSystemGroup, but input/movement comes from FixedStep plus variable systems; no ordering attribute ties StateUpdate to ThirdPersonCharacterVariableUpdateSystem/TransformSystemGroup, so whether it sees this frame's body or last frame's depends on sort order (sorted deterministically but not guaranteed by attribute).
17. One shared mutable animation default: `CharacterAnimatorSync` speedDamping (:75) and ECS Damp both smooth movement (AnimationDampTime=5, StateUpdate :26), so MoveSpeed is smoothed once in MB; direction params only in ECS.

## Where else animation is not
- athena.charactercontroller: no Animator/animation references; it exposes KinematicCharacterBody-based motion only. It must not reference athena.shared (guardrail 2), so the Animator bridge cannot move into it without inverting the dependency.
- athena.ai / com.ai.shared / com.ai.utility: no animation, no Animator parameter writes. AI characters can only drive movement via ThirdPersonCharacterExternalInput/MoveToTarget, which feeds MoveVector and therefore the same animation state path.
- athena.gameplay, athena.sceneslice, athena.core, athena.contentmanagement: zero animation hits.
- Assets/Scripts: only SkinCheatCommand touches skin switching.
- Entities Graphics, Animation Rigging, Timeline, Cinemachine: no first-party code references (asmdef and .cs grep over Packages/athena.*, Packages/com.ai.*, Assets).
- Guardrails: nothing in this order touched a vendored package or any file outside report_to; all PackageCache reads were avoided entirely (no version-exact API question required).
