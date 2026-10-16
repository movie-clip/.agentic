REPORT 2026-10-07-s2-animation-bridge-contract/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design pass, order verification was NONE

contract_notes:
  - New public interface ICharacterAnimationBackend (one method, Apply) in Athena.Shared.Components. Every backend, including the test double, implements it. See § Contract
  - CharacterAnimationBridgeInitialized (S1 managed cleanup component) gains Backend, LastApplied, HasApplied. Same name and file, so S1 tests that use typeof(...) still compile. See § Contract
  - CharacterAnimationState gains IEquatable, CreateDefault() and a field map (CharacterAnimationContract). Struct layout and field names are unchanged, so S1 tests that set CurrentGait and IsJumping still compile. See § Contract
  - New optional component CharacterAnimationSpeedReference (Athena.Shared.Components) is the single speed source. A character without it behaves exactly as today. See § Single speed source
  - CharacterAnimatorSync loses its Update pull, its entity link and its inspector parameter-name fields. No prefab, scene or asset serialises it (GUID grep, zero hits). Its Initialize signature changes to no arguments. See § Contract
  - Test asmdefs Impact.EditModeTests and Impact.PlayModeTests need references to Athena.CharacterController.Runtime and Unity.CharacterController for T-1. Test assemblies are not in the guardrail-2 graph and nothing references them, so no cycle. See § Consumers
  - CHARACTER_ANIMATION_SETUP.md, athena.shared PACKAGE_DOCUMENTATION.md, ARCHITECTURE_REVIEW.md lag this design (pull model, two authoring components, maxMoveSpeed field). Docs lane at close-out

pack_corrections:
  - none

handoff:
  - Dispatch is exactly three build orders in the requested sequence: test (T-1 + T-2) on unmodified code, backend (T-3 + T-4), test (T-5 + T-6). The grouping works; see § Dispatch plan
  - Order 1 must name the T-1 test MoveSpeedNormalized_Characterization_AssumedRunSpeedSix. It is the one test that is expected red after order 2, because MoveSpeedNormalized moves from /6 to /7 on purpose. See § Dispatch plan
  - Order 1 must NOT pin the no-owner or no-camera behaviour of today's state system. AC-9 reverses it and order 2 cannot edit tests. See § Dispatch plan
  - Order 2 file fence is the nine athena.shared Runtime files listed in § Dispatch plan. No asmdef, no test, no prefab, no CharacterSkinChangeSystem, no SpawnHybridCharacterSkinSystem edits
  - Order 2 verification expects every Impact.*Tests.Animation test green except the one named above, which must fail by assertion. Order 3 replaces that test
  - Order 3 owns the harness additions: AttachBackend helper, RecordingAnimationBackend double, bridge-off switch extended to the presentation system. The S1 harnesses discover the new presentation system by attribute, so no Tick change is needed
  - Human follow-ups with exact commands: git rm Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs (and its .meta) once the obsolete stub has shipped; a later cleanup removes the three retired fields
  - Open for the human, no blocker: MoveSpeed normalisation stays at 7 (not GroundMaxSpeed 10) to honour D-4. See § Single speed source and risks

skill_calls:
  - mattpocock-skills:codebase-design — called, before naming the backend seam. Applied: one small interface (Apply) with gating, relink and lifecycle behind it; two adapters exist (Animator MonoBehaviour, test double), so the seam is real; the S1 deletion test keeps the bridge as the single owner of link lifetime

risks:
  - AC-6 reads "the character's maximum movement speed". I made the single source an animation reference speed (default 7), not ThirdPersonCharacterComponent.GroundMaxSpeed (10 on BaseCharacter.prefab). Using 10 would change the Animator MoveSpeed blend by 30 percent and breach D-4 and AC-2. The reviewer may read AC-6 differently
  - AC-7 cannot be proved by baking the real prefab in a test. BakingUtility.BakeGameObjects and BakingSettings are internal to Unity.Entities.Hybrid (Library/PackageCache/com.unity.entities@d66668920c3f/Unity.Entities.Hybrid/Baking/BakingUtility.cs:194, BakingSettings.cs:15). Evidence is by construction plus prefab-content and factory tests; the reviewer should know that
  - MoveSpeedNormalized changes value on purpose (raw/6 to raw/7). It was unread by the Animator path except as a fallback, so no visible change, but AC-1 recordings of it differ before and after
  - Retired fields (MoveDirection, VerticalVelocity, JumpTriggered) stay in the struct and stay computed. Deleting them in order 2 would break order 1 tests at compile time and the backend lane cannot edit tests. Removal is a follow-up
  - Presentation keeps today's one-frame latency on purpose (it runs at the start of the frame and applies last frame's state, as the MonoBehaviour pull did). Same-frame presentation is a one-attribute change for S5 or S6 if latency matters
  - Exact gait boundaries at default depend on scale = maxSpeed / 7 evaluating to exactly 1 and on Burst not reassociating. Order 1 pins speeds 1.75 and 8 exactly and just below; order 2 must keep them green
  - The 150-character figure is a difference of two noisy Editor frame times. The control run (bridge off, Animators still evaluating) is my choice; the story did not specify one. Noise may swamp a small saving, and the record must say so
  - Gating can hide a defect on relink: a new backend must receive the full current state even when the state did not change. This is invariant G3 and has its own test in order 3
  - Authoring: Unity cannot delete or rename, so CharacterAnimationAuthoring stays as an obsolete stub whose baker only logs an error. Prefabs carrying both components get a visible error instead of a silent double bake
  - 150 Debug.Log lines ("Auto-added CharacterAnimatorSync") appear when the measurement scenario spawns 150 characters. Not changed here; log lines do not fail Unity tests

## Orchestrator brief
- Decision: seam is ICharacterAnimationBackend.Apply(in CharacterAnimationState), in Athena.Shared.Components. No asmdef change in production, no guardrail crossed, status DONE.
- Decision: push model. A new CharacterAnimationPresentationSystem (PostEntityLifecycleGroup, after the bridge) applies state to each link's Backend. CharacterAnimatorSync becomes a passive adapter with no Update.
- Decision: single speed source is optional component CharacterAnimationSpeedReference, default 7. It reproduces today's gait and Animator MoveSpeed exactly (D-4). Not GroundMaxSpeed; see risks.
- Decision: CharacterAuthoring's baker survives; CharacterAnimationAuthoring becomes an obsolete stub that logs a visible error.
- Decision: state system ordered UpdateAfter ThirdPersonCharacterVariableUpdateSystem; owner and camera no longer required.
- Decision: gating in two layers: system-level compare against LastApplied (backend-agnostic), and Animator per-parameter cache.
- Lane split: exactly three orders: test (T-1 + T-2) on unmodified code, backend (T-3 + T-4), test (T-5 + T-6). It works.
- Blocks dispatch: nothing.
- Sections: Contract · Single speed source · Authoring · Ordering · Change-gating · Degraded cases · Consumers · Measurement harness · Reuse · Dispatch plan · Extension points · Guardrail check · Decisions engineers must not make independently.

## Contract

**Seam (the backend interface).** New file `Packages/athena.shared/Runtime/Components/Character/ICharacterAnimationBackend.cs`, namespace `Athena.Shared.Components`, assembly `Athena.Shared.Components`.

```csharp
public interface ICharacterAnimationBackend
{
    // Called on the main thread, inside PostEntityLifecycleGroup.
    // Called when (a) this backend has just become a character's backend, with the full current state,
    // even if that state did not change; (b) the character's state differs from the last state
    // applied to this backend. Never called otherwise. Exceptions propagate (no try/catch).
    void Apply(in CharacterAnimationState state);
}
```

- Location against the project.md graph: `Athena.Shared.Components` already references everything the interface needs. `athena.gameplay` may reference `Athena.Shared.Components`, so a gameplay-side backend could implement it later. `athena.charactercontroller` cannot see it and does not need to. No `.asmdef` edit, no new reference.
- Deliberately one method. Return channels (S5 clip events, S6 root motion) are added as separate optional interfaces the bridge checks with `is`; see § Extension points. Do not add default interface methods.
- Two adapters exist now (Animator MonoBehaviour, test double), so the seam is real, not hypothetical.

**Link component (extends S1's marker).** `CharacterAnimationBridgeInitialized` in `CharacterAnimationState.cs`, still a `class : ICleanupComponentData`:

| Field | Type | Meaning |
|---|---|---|
| `LinkedInstance` | `GameObject` | S1 field, unchanged. The presentation instance this link was made for. Null for a link that has no GameObject (test double). |
| `Backend` | `ICharacterAnimationBackend` | New. Never null on a live link. |
| `LastApplied` | `CharacterAnimationState` | New. Gating memory, owned by the presentation system. |
| `HasApplied` | `bool` | New. False means the next presentation update applies unconditionally. |

Invariants:
- G1. Whenever the bridge assigns or replaces `Backend` it also sets `HasApplied = false`. This is what delivers the full state to a new skin instance.
- G2. Only `CharacterAnimationBridgeSystem` assigns `LinkedInstance` or `Backend` for GameObject-backed links. Only the presentation system writes `LastApplied` and `HasApplied=true`.
- G3. A test double is attached by adding `new CharacterAnimationBridgeInitialized { Backend = double }` to an entity that has `CharacterEntity` and `CharacterAnimationState` and no `HybridGameObjectSpawned`. The bridge leaves it alone: pass 1 requires no marker, and pass 2 requires Spawned. The entity must carry `CharacterEntity`, otherwise the cleanup system removes the link as a destroyed character.

**State struct changes** (`CharacterAnimationState`, same file, field names and order unchanged):
- Implements `IEquatable<CharacterAnimationState>`. `Equals` compares every field with `==`, written by hand, not memcmp (struct padding is not guaranteed equal after a managed copy, which would make gating fail silently). Order 3 adds a reflection test that changes each field in turn and expects `Equals` to be false, so a field added later cannot be forgotten.
- `public static CharacterAnimationState CreateDefault()` returns the neutral state: `IsGrounded=true`, `StrafeDirectionZ=1`, `ShuffleDirectionZ=1`, `ForwardStrafe=1`, everything else zero. It is the only place initial values live; both bakers' 24-line initialisers go away.

**Field-by-field map.** One place: `Packages/athena.shared/Runtime/Components/Character/CharacterAnimationContract.cs` (new, namespace `Athena.Shared.Components`). It holds `public enum CharacterAnimationFieldKind { Parameter, OptionalParameter, EcsOnly, Retired }`, the Animator parameter-name string constants, and `public static readonly CharacterAnimationFieldMapping[] Fields` with `{ string Field; Kind; string AnimatorParameter; AnimatorControllerParameterType ParameterType }` per state field. The Animator adapter hashes the same constants. The AC-5 test reflects over `CharacterAnimationState` and fails on any field missing from `Fields`, any entry naming a missing field, and any duplicate.

| State field | Kind | Animator parameter (type) | Note |
|---|---|---|---|
| `MoveSpeed` | EcsOnly | none | raw planar speed, units per second; input to the normalised value; ECS and AI consumers read it |
| `MoveSpeedNormalized` | Parameter | `MoveSpeed` (Float) | adapter smooths it; naming trap: the parameter named MoveSpeed carries the normalised field |
| `MoveDirection` | Retired | none | unread; still computed this story |
| `VerticalVelocity` | Retired | none | unread; derivable from `KinematicCharacterBody` |
| `IsGrounded` | Parameter | `IsGrounded` (Bool) | |
| `JumpTriggered` | Retired | none | actually a landing edge (`isGrounded && !WasGrounded`); name kept so order 1 tests compile after order 2 |
| `IsMoving` | OptionalParameter | `IsStopped` (Bool) | written inverted (`!IsMoving`) |
| `FallingDuration` | Parameter | `FallingDuration` (Float) | |
| `IsJumping` | Parameter | `IsJumping` (Bool) | |
| `IsStarting` | OptionalParameter | `IsStarting` (Bool) | |
| `LocomotionStartDirection` | Parameter | `LocomotionStartDirection` (Float) | |
| `CurrentGait` | Parameter | `CurrentGait` (Int) | 0 idle, 1 walk, 2 run, 3 sprint |
| `IsWalking` | Parameter | `IsWalking` (Bool) | |
| `MovementInputPressed` | OptionalParameter | `MovementInputPressed` (Bool) | |
| `MovementInputHeld` | OptionalParameter | `MovementInputHeld` (Bool) | |
| `MovementInputTapped` | OptionalParameter | `MovementInputTapped` (Bool) | |
| `StrafeDirectionX` | Parameter | `StrafeDirectionX` (Float) | |
| `StrafeDirectionZ` | Parameter | `StrafeDirectionZ` (Float) | |
| `ShuffleDirectionX` | Parameter | `ShuffleDirectionX` (Float) | |
| `ShuffleDirectionZ` | Parameter | `ShuffleDirectionZ` (Float) | |
| `ForwardStrafe` | Parameter | `ForwardStrafe` (Float) | |
| `CameraRotationOffset` | Parameter | `CameraRotationOffset` (Float) | |
| `IsStrafing` | Parameter | `IsStrafing` (**Float**, 1 or 0) | float, not bool, today and after; do not "fix" it |
| `IsTurningInPlace` | Parameter | `IsTurningInPlace` (Bool) | |

Totals: 24 fields; 14 Parameter, 5 OptionalParameter (a controller may lack them; the adapter scans `animator.parameters` once at Initialize, as today), 1 EcsOnly, 3 Retired. Count them in the test; it must equal `typeof(CharacterAnimationState).GetFields().Length`.

Retired means: no adapter writes it, no ECS system reads it, and the list says so. The three are still computed this story so order 1's recordings stay valid across order 2. Removing them from the struct is a follow-up, once order 3's tests exist and S4 has confirmed it needs none of them.

**Animator adapter.** `CharacterAnimatorSync` (same file and type name, so S1's `GetComponentsInChildren<CharacterAnimatorSync>().Length == 1` assertions hold) becomes `MonoBehaviour, ICharacterAnimationBackend`:
- No `Update`, no `Awake` setup, no entity, no world, no `EntityManager` access.
- `public void Initialize()` is idempotent and does what Awake and the old Initialize did: `animator = GetComponent<Animator>()`, hash the parameter names from `CharacterAnimationContract`, set `applyRootMotion = false`, reset the optional-parameter scan and the write cache. The bridge calls it before the first Apply. Setup must not depend on Awake because EditMode does not run Awake for plain MonoBehaviours.
- `Apply` returns immediately when `animator == null` (Unity null, covers a destroyed instance) or `animator.runtimeAnimatorController == null`. In the second case it logs one warning per adapter instance and then stays silent.
- The inspector string fields, `maxMoveSpeed` and `writeOptionalParameters` are removed. `speedDamping` 0.15 becomes a private constant.
- `MoveSpeed` parameter: `target = state.MoveSpeedNormalized`; `current = Lerp(current, target, 1 - Exp(-0.15 * Time.deltaTime * 60))` exactly as today; when `abs(target - current) < 1e-4` set `current = target` so the value converges and stops being written. Smoothing stays in the adapter because it is presentation, and a second backend does not have to inherit it.

## Single speed source

Today there are three constants: `AssumedRunSpeed = 6` in the state system (feeds `MoveSpeedNormalized`, used by nothing except a fallback), `maxMoveSpeed = 7` in the MonoBehaviour (feeds the Animator `MoveSpeed`), and the gait thresholds 1.75 / 5 / 8 in the state system (independent of both). `GroundMaxSpeed` (10 on `BaseCharacter.prefab:204`) drives physics and never entered the animation path.

**Decision.** One optional component, one baked value, one constant for its default:

```csharp
// Athena.Shared.Components, new file Components/Character/CharacterAnimationSpeedReference.cs
public struct CharacterAnimationSpeedReference : IComponentData
{
    public const float DefaultMaxSpeed = 7f;   // the speed the Synty locomotion set is authored for
    public float MaxSpeed;                      // <= 0 means DefaultMaxSpeed
}
```

State system rules (the only code that uses the value; the MonoBehaviour no longer normalises):
- `maxSpeed = (lookup has component && MaxSpeed > 0) ? MaxSpeed : DefaultMaxSpeed`, read per character through a `ComponentLookup<CharacterAnimationSpeedReference>` (TryGetComponent) updated at the top of `OnUpdate`.
- `MoveSpeedNormalized = math.saturate(horizontalSpeed / maxSpeed)`.
- `scale = maxSpeed / CharacterAnimationSpeedReference.DefaultMaxSpeed`. Walk boundary = `1.75f * scale`; sprint boundary = `8f * scale`. These two literals (1.75 and 8) are the only gait constants left. `RunSpeedThreshold` (5) and `AssumedRunSpeed` (6) are deleted. Gait 2 therefore covers `[walk, sprint)`, which is today's behaviour, because today's two gait-2 bands are contiguous.
- `IsWalking` uses the scaled walk boundary. The absolute constants `MoveThreshold` 0.1, the start-speed limit 1.0, and the jump and fall velocity thresholds are not part of the profile and stay unscaled.

**How it reproduces today's gait (D-4).** For a character without the component, or with `MaxSpeed = 7`, `scale = 7/7 = 1` exactly and the boundaries are 1.75 and 8 exactly, so every speed lands in the same gait as now. The deleted threshold 5 never decided anything. `MoveSpeedNormalized` becomes `saturate(speed/7)`, which is the value the MonoBehaviour computed (`Clamp01(MoveSpeed/7)`), so the Animator `MoveSpeed` parameter is unchanged apart from the smoothing snap (under 1e-4).

**Authoring of the value.** `CharacterAuthoring` gets one serialised field `public float AnimationMaxSpeed = CharacterAnimationSpeedReference.DefaultMaxSpeed;` and its baker adds `CharacterAnimationSpeedReference { MaxSpeed = authoring.AnimationMaxSpeed }`. The existing `BaseCharacter.prefab` does not serialise the field, so it deserialises with the initialiser value 7. No prefab asset is edited.

**AC-6 as a test.** Two characters, `MaxSpeed` 7 and 14, same velocities: the gait boundaries sit at 1.75/8 and 3.5/16, `MoveSpeedNormalized` at `speed/7` and `speed/14`. For the default, all recordings equal order 1's.

**What this does not do.** It does not tie animation to `GroundMaxSpeed`. A character whose `GroundMaxSpeed` is raised keeps the same animation scale until someone changes `AnimationMaxSpeed`. That is the price of D-4; see risks.

## Authoring

Verified: `CharacterAuthoring`'s GUID `b618848414694e5abee2db7281867a2d` appears in `Assets/Content/Characters/Gameplay/Setup/BaseCharacter.prefab`. `CharacterAnimationAuthoring`'s GUID `1bab29185c4043439384b40bd592232c` appears in no prefab, scene or asset. `CharacterAnimatorSync`'s GUID appears in none either.

- **Survivor:** `CharacterAuthoring` and `CharacterBaker`. It already bakes `CharacterEntity`, ownership, crate and hybrid components, and `CharacterAnimationStateUpdateSystem` ignores entities without `CharacterEntity`, so the other baker could never produce a working character alone.
- **Baker body after:** `AddComponent(entity, CharacterAnimationState.CreateDefault())`, `AddComponent(entity, new CharacterAnimationRuntimeState())`, `AddComponent(entity, new CharacterAnimationSpeedReference { ... })`. No 24-line initialiser.
- **The other:** `CharacterAnimationAuthoring` keeps its file and class (no lane can delete). Mark the class `[Obsolete("...")]` and `[AddComponentMenu("")]`, remove the `animator` field and `OnValidate`, and replace its nested baker body with one `Debug.LogError` naming the GameObject and telling the user to remove the component because `CharacterAuthoring` bakes animation state. The baker adds nothing. A prefab carrying both therefore bakes once, with a visible error. Human follow-up (exact commands): `git rm Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs Impact/Packages/athena.shared/Runtime/Components/Authoring/CharacterAnimationAuthoring.cs.meta`, safe once the stub has shipped, since no asset references it.
- **Test shape for AC-7.** Not a bake test (internal API, see risks). Order 3 writes: an EditMode test loading `BaseCharacter.prefab` with `AssetDatabase` that asserts it has `CharacterAuthoring` and has no `CharacterAnimationAuthoring`; a test that `CharacterAnimationState.CreateDefault()` equals the documented neutral values; and a test that `AnimationMaxSpeed` defaults to `CharacterAnimationSpeedReference.DefaultMaxSpeed` on a freshly added `CharacterAuthoring`. The order 3 report states plainly that the real bake was not run.

## Ordering

All attributes explicit; nothing relies on sort order. The chain for one frame:

1. `ThirdPersonCharacterVariableUpdateSystem` (existing; `UpdateInGroup(SimulationSystemGroup)`, after FixedStep and after `ThirdPersonPlayerVariableStepControlSystem`, before `TransformSystemGroup`).
2. `CharacterAnimationStateUpdateSystem`: add `[UpdateAfter(typeof(ThirdPersonCharacterVariableUpdateSystem))]`; keep `[UpdateInGroup(typeof(SimulationSystemGroup))]`. The type is global-namespace in `Athena.CharacterController.Runtime`, already referenced by `Athena.Shared.Runtime`. This closes recon problem 16: the state is computed after the body moved in the same frame (AC-8). The AI move vector is written earlier (`ThirdPersonCharacterExternalInputSystem` in FixedStep), so it is also current.
3. Next frame, in `PostEntityLifecycleGroup` (OrderFirst in `SimulationSystemGroup`): `CharacterSkinChangeSystem`, then `SpawnHybridCharacterSkinSystem`, then `CharacterAnimationBridgeSystem` (existing `UpdateAfter(SpawnHybridCharacterSkinSystem)`), then new `CharacterAnimationPresentationSystem` (`[UpdateInGroup(typeof(PostEntityLifecycleGroup))] [UpdateAfter(typeof(CharacterAnimationBridgeSystem))]`). `CharacterAnimationBridgeCleanupSystem` keeps `UpdateAfter(Bridge)`; it needs no order against presentation because a destroyed character has no `CharacterAnimationState` and is not in presentation's query.

Presentation timing is on purpose identical to today. Today the MonoBehaviour's `Update` runs earlier in the Update phase than the ECS simulation group, so it reads the previous frame's state before the Animator evaluates. Presentation at the start of the next frame's `SimulationSystemGroup` also applies the previous frame's state before the Animator evaluates. The S1 harnesses build their group by scanning `UpdateInGroup(PostEntityLifecycleGroup)`, so they pick the new system up with no edit.

AC-8 test (order 3): build a `SimulationSystemGroup` holding the real `CharacterAnimationStateUpdateSystem` and the real `ThirdPersonCharacterVariableUpdateSystem` type, insert them in both orders, `SortSystems()`, and assert the state system's index is greater. Red on unmodified code for the insertion order that puts the state system first. Add a stand-in mover (test class) declared `UpdateBefore(typeof(ThirdPersonCharacterVariableUpdateSystem))` that writes `KinematicCharacterBody.RelativeVelocity`; the state read in the same `Update` must equal that velocity's speed.

## Change-gating

Two layers, both required. Nothing else is gated (no change filter; see below).

1. **System layer, backend-agnostic** (`CharacterAnimationPresentationSystem`, a non-Burst `SystemBase`, `SystemAPI.Query<RefRO<CharacterAnimationState>, CharacterAnimationBridgeInitialized>()`). Per character: skip when `link.Backend == null`; if `!link.HasApplied || !state.Equals(link.LastApplied)` then `link.Backend.Apply(in state); link.LastApplied = state; link.HasApplied = true`. The test double counts `Apply` calls and the count is zero for unchanged frames (AC-11). There is no per-character `EntityManager` read and no per-frame allocation. A character with no link yet is simply not in the query.
2. **Animator layer** (inside `CharacterAnimatorSync.Apply`). One cached last-written value per parameter plus a `cacheValid` flag. Write only when the value differs; floats compare with exact `!=`. `cacheValid` is false after `Initialize` and in `OnEnable` (an Animator that is disabled and re-enabled resets its parameters to defaults, so the cache would otherwise lie). The assertion for AC-11's second sentence uses the sentinel technique: after a first Apply, the test sets a discrete parameter (for example `IsGrounded`) on the Animator directly to the opposite value, then applies a state that changes only another field, and expects the sentinel to survive. That proves the adapter did not rewrite the unchanged parameter.

Rejected: a chunk change filter on `CharacterAnimationState`. The state system takes `RefRW` on every character each frame, which bumps the chunk version whether or not a value changed, so the filter would never skip. Making the state system write only when changed would be a second change for a saving the per-entity compare already gives.

G3 restated as a test (order 3): change the state, apply, then replace the character's instance (swap) without changing the state; the new backend must still receive one full `Apply`.

## Degraded cases

- No usable backend (instance has no Animator and no sync): `CharacterAnimationBridgeSystem.TryLink` keeps S1's behaviour (one warning per spawned instance, a per-entity `warnedInstances` map, trimmed each frame while non-empty). Only its return type changes: it returns the `ICharacterAnimationBackend` it found or auto-added (the `CharacterAnimatorSync`), or null. The state system does not read the link, so the ECS state keeps updating (AC-12).
- Pass 1 adds the marker with `Backend` set; pass 2 on an instance change sets `LinkedInstance`, `Backend` and `HasApplied=false` together (G1).
- `CharacterAnimatorSync.Initialize()` is called by the bridge once per backend, before assignment.
- Destroyed instance while the entity lives: `Apply` returns on the Unity-null animator; the bridge relinks when Spawned changes. No new try/catch (AGENTS.md: no broad try/catch without a recovery path).
- Warn-once and trim are unit-observable through captured log lines, not private state (S1 plan rule stands).

## Consumers

Every reader of `CharacterAnimationState`, `CharacterAnimationRuntimeState`, `CharacterAnimationBridgeInitialized` or `CharacterAnimatorSync`, found by a grep over `Packages` and `Assets` (including `*.md`) and a GUID search over `*.prefab`, `*.unity`, `*.asset`.

| Consumer | Assembly | Reads today | Changes under this plan |
|---|---|---|---|
| `CharacterAnimationStateUpdateSystem` | `Athena.Shared.Runtime` | writes state; reads `ThirdPersonCharacterControl`, `KinematicCharacterBody`, `LocalTransform`, `OwnedByPlayerEntity`, camera via `EntityManager` | query loses `OwnedByPlayerEntity`; camera read only if strafing; adds speed lookup and ordering attribute |
| `CharacterAnimationBridgeSystem`, `CharacterAnimationBridgeCleanupSystem` | `Athena.Shared.Runtime` | the S1 marker | bridge sets two more fields and `Initialize()` signature; cleanup unchanged |
| new `CharacterAnimationPresentationSystem` | `Athena.Shared.Runtime` | state, link | new |
| `CharacterAnimatorSync` | `Athena.Shared.Components` | pulled state through `EntityManager` | becomes a passive adapter, see § Contract |
| `CharacterAuthoring` baker, `CharacterAnimationAuthoring` baker | `Athena.Shared.Components` | write defaults | one default factory; second baker retired |
| `athena.charactercontroller` | `Athena.CharacterController.Runtime` | none (grep zero) | none. The state system now orders itself after its `ThirdPersonCharacterVariableUpdateSystem`; that is an `UpdateAfter` reference from shared to charactercontroller, the existing dependency direction, and charactercontroller is not edited |
| `athena.gameplay` | `Athena.Gameplay.Runtime` | none (grep zero) | none |
| `athena.ai`, `com.ai.shared`, `com.ai.utility` | | none (grep zero) | none. AI characters now get state updates (AC-9) with no change in AI code |
| `Impact.EditModeTests` (`CharacterAnimationEditModeWorld`, `CharacterAnimationBridgeEditModeTests`, the other S1 fixtures) | | `typeof(CharacterAnimationBridgeInitialized)`, `CharacterAnimatorSync` add/count, `CharacterAnimationState` component type | compiles unchanged. Behaviour: `Tick()` now also runs presentation; no assertion in these tests depends on the old pull. Asmdef gains `Athena.CharacterController.Runtime` and `Unity.CharacterController` for the state-system fixtures |
| `Impact.PlayModeTests` (`CharacterAnimationPlayModeHarness`, `SkinSwapAnimationPlayModeTests`) | | sets `CurrentGait`, `IsJumping`; reads Animator parameters; adds sync on prefabs | compiles unchanged; Animator values now arrive during `group.Update()` instead of the next MonoBehaviour `Update`. Same asmdef additions |
| `ARCHITECTURE_REVIEW.md`, `CHARACTER_ANIMATION_SETUP.md`, `athena.shared/PACKAGE_DOCUMENTATION.md`, `PLAYER_SESSION_CHARACTER_FLOW.md` | docs | describe the pull model and two authoring components | docs lane at close-out |

## Measurement harness

Per D-5: Editor only, dev machine, PlayMode, 150 continuously moving characters, timed over N frames, no threshold.

**Fixture.** `Assets/Tests/PlayMode/Animation/CharacterAnimationCostMeasurement.cs`, a `[UnityTest]` on `CharacterAnimationPlayModeHarness` (reuse; add a `CreateMovingCharacter` helper and a bridge-off switch). Built in order 1 so it compiles and runs on unmodified code, and re-run unchanged in order 3.

**Scenario A (moving, the required figure).**
- 150 characters spawned through the real hybrid spawn flow with the **real** `Viking_BaseSkin_Visuals.prefab` and the real `AC_Polygon_Masculine` controller (same asset lookup as S1's P4), not the in-memory single-state controller, which would make Animator cost trivial. Default culling mode is left as it is; do not change it (D-1).
- Each entity also has `CharacterAnimationRuntimeState`, `LocalTransform`, `KinematicCharacterBody`, `ThirdPersonCharacterControl`, `OwnedByPlayerEntity` (null owner), so the real `CharacterAnimationStateUpdateSystem` runs. Every frame the harness writes a per-character varied pattern into `RelativeVelocity` and `MoveVector` that sweeps idle, walk, run, sprint and a periodic jump, with a per-character phase offset, so state changes every frame for most characters. `world.SetTime` provides the delta time.
- Warm-up 60 frames, then N = 300 sampled frames. `QualitySettings.vSyncCount = 0` and `Application.targetFrameRate = -1` for the run and restored in teardown.

**Control run B (same scene, bridge off).** The bridge-off switch disables the state system (`SystemState.Enabled = false`) and every `CharacterAnimatorSync` (`enabled = false`). Animators still evaluate. After the refactor the switch also disables the presentation system (order 3 extends it, the only edit to the fixture). Reported animation-path cost = A minus B, with A and B each shown.

**What is timed.** Per-frame wall time between consecutive frames (`Time.realtimeSinceStartupAsDouble` deltas) taken at the same point of the coroutine, because the MonoBehaviour pull before the refactor runs inside Unity's own player-loop callbacks, outside any Stopwatch the test could wrap. Report mean, median and p95 per run, in milliseconds. GC allocation per frame via a `ProfilerRecorder` on `GC Allocated In Frame` is an optional extra; its absence is not a failure.

**Scenario C (idle, optional).** The same 150 characters with constant velocity zero, A and B again. Shows what AC-11 buys. Cheap, recommended, not required by the ACs.

**Output.** One log line per run, `[S2-MEASURE] {json}`, containing: scenario, character count, frames sampled, warm-up, mean/median/p95, `SystemInfo.processorType`, `SystemInfo.graphicsDeviceName`, `Application.unityVersion`, Editor PlayMode via batchmode, controller asset name, culling mode, bridge state. The lane copies it from the results XML into its report. No file is written into the repo (guardrail 5 and no-roadmap-doc guardrail 4).

**Assertions (the only ones).** 150 entities carry `CharacterAnimationBridgeInitialized`; N frames were sampled; at least one character reached each of gait 0, 1, 2, 3 and `IsJumping == true` during the run (proves "moving"). Never a time.

Order 1 records the "before" row (T-2); order 3 records the "after" row and the difference (T-6) on the same machine with the Editor otherwise idle, three repeats each so the spread is visible.

## Reuse

- Fixtures: `CharacterAnimationEditModeWorld` (EditMode, real `PostEntityLifecycleGroup`, `CreateCharacter`, `Tick`, `ReplaceInstance`, `RemoveInstanceForRespawn`, `DestroyCharacter`, `CountEntitiesWith`) and `CharacterAnimationPlayModeHarness` (`Tick(frames)`, `SwapSkin`, `SetAnimationState`, `ReadAnimatorInt/Bool`, `CreateVisual`, real-prefab pattern from `SkinSwapAnimationPlayModeTests` P4). The write-state and read-presentation helpers are the swap point for the double.
- Support: `LevelCrateTestContext`, `CharacterCrateLookupTestFactory.Create` (`Assets/Tests/EditMode/TestSupport/`).
- Production patterns: `CharacterSkinCleanupSystem` and `CharacterAnimationBridgeCleanupSystem` for the `WithNone<CharacterEntity>` cleanup query; `HybridGameObjectSpawned` for a managed cleanup component; the existing bridge `SystemAPI.Query<..., ManagedComponent>().WithEntityAccess()` shape for presentation; `ComponentLookup<T>` with `TryGetComponent` instead of `EntityManager.Exists/GetComponentData` in the state system.
- Do not reuse: `IAspect` (obsolete in Entities 6.4); `AgentAspect` and the character aspects are untouched.
- New in tests: `RecordingAnimationBackend : ICharacterAnimationBackend` (test assembly, records `List<CharacterAnimationState>` and an `ApplyCount`). Two copies, one per assembly, on purpose, as S1 did for harness code. Do not create a shared test asmdef.

## Dispatch plan

Grouping holds: **test (T-1 + T-2) → backend (T-3 + T-4) → test (T-5 + T-6)**. It works because T-1 and T-2 compile and run on code the backend has not touched, and nothing in them names a type the backend adds.

### Order 1: test lane, T-1 + T-2, unmodified production code

Fence: `Impact/Assets/Tests/EditMode/**`, `Impact/Assets/Tests/PlayMode/**`, both test `.asmdef` files (add `Athena.CharacterController.Runtime`, `Unity.CharacterController`; add `Unity.Physics` only if the compiler reports CS0012), `Impact/Tools/**` only if a script change is needed. No production file.

- T-1a, EditMode, new `CharacterAnimationStateEditModeWorld` plus `CharacterAnimationStateUpdateEditModeTests` in `Impact.EditModeTests.Animation`: a world with `CharacterAnimationStateUpdateSystem` (created and updated manually, `world.SetTime` with a fixed 1/60 delta). Entities carry `CharacterEntity`, `CharacterAnimationState`, `CharacterAnimationRuntimeState`, `LocalTransform`, `KinematicCharacterBody`, `ThirdPersonCharacterControl`, `OwnedByPlayerEntity` (null owner). Scripted inputs per AC-1: idle; gait boundaries at speeds 0.1, 0.11, 1.74, 1.75, 4.99, 5.0, 7.99, 8.0, 12 (gait 0, 1, 1, 2, 2, 2, 2, 3, 3; compute, then pin the real observed values); jump ascent (vertical velocity above 0.1, not grounded); fall duration growth; landing edge (`JumpTriggered`); movement input pressed, held, tapped; movement start and stop. Record observed values and assert them: exact for discrete fields, tolerance 1e-4 for damped floats. Keep the duplicate band visible: the test for speed 5.0 expects gait 2.
- T-1b: the dedicated test `MoveSpeedNormalized_Characterization_AssumedRunSpeedSix` asserts `MoveSpeedNormalized == saturate(speed / 6)`. This is the one test order 2 turns red on purpose. Nothing else in T-1 may assert `MoveSpeedNormalized`.
- T-1c: do not pin the no-owner or no-camera behaviours. They are defects AC-9 and AC-10 reverse.
- T-1d, PlayMode, `CharacterAnimationMappingPlayModeTests`: AC-2 before-side. On the **real** Viking prefab and `AC_Polygon_Masculine`, write the AC-1 state values for each scripted step with `SetAnimationState` (extend the helper to take a whole state), tick, assert the Animator parameter values. Discrete parameters exact; `MoveSpeed` with tolerance 1e-3 (smoothed against real `Time.deltaTime`, so wait enough frames to converge or compare against the same converged target).
- T-2: `CharacterAnimationCostMeasurement` per § Measurement harness, scenario A and control B (and C if cheap), three repeats, on unmodified code. Report the log lines and the machine.
- Verification: `dotnet build Impact.sln`; `Run-UnityTests.ps1 -Platform EditMode -Filter "Impact.EditModeTests.Animation"` and PlayMode `-Filter "Impact.PlayModeTests.Animation"`; then full `-CoreOnly` on both platforms to show all existing tests stay green. All new tests green on unmodified code.

### Order 2: backend lane, T-3 + T-4

Fence (all under `Impact/Packages/athena.shared/Runtime/`, nine files, new ones marked):
1. `Components/Character/CharacterAnimationState.cs` (IEquatable, CreateDefault, link fields)
2. `Components/Character/ICharacterAnimationBackend.cs` (new)
3. `Components/Character/CharacterAnimationContract.cs` (new)
4. `Components/Character/CharacterAnimationSpeedReference.cs` (new)
5. `Components/Character/CharacterAnimatorSync.cs`
6. `Components/Authoring/CharacterAuthoring.cs`
7. `Components/Authoring/CharacterAnimationAuthoring.cs`
8. `Systems/CharacterAnimationBridgeSystem.cs` and `Systems/CharacterAnimationStateUpdateSystem.cs`
9. `Systems/CharacterAnimationPresentationSystem.cs` (new)

Not to be touched: any `.asmdef`, any test, any prefab, `CharacterSkinChangeSystem.cs`, `SpawnHybridCharacterSkinSystem.cs`, `HybridGameObjectSystemBase.cs`, `CharacterAnimationBridgeCleanupSystem.cs`, anything in `athena.charactercontroller`.

- T-3 (AC-3 to AC-7): interface, link fields and G1 to G3, presentation system with the system-layer gate, Animator adapter conversion, contract map, `IEquatable` and `CreateDefault`, speed component and baker field, authoring retirement.
- T-4 (AC-8 to AC-12): `UpdateAfter` attribute, query without `OwnedByPlayerEntity`, lazy camera lookup via `ComponentLookup` only inside the strafing branch (the branch stays; `isStrafing` stays hard-coded false, S4 owns it), Animator parameter cache and snap, warn-once carried onto the new `TryLink` return type, deletion of `AssumedRunSpeed` and `RunSpeedThreshold`.
- Naming: components in `Athena.Shared.Components`, systems in `Athena.Shared.Systems`, one type per file, no `IAspect`, no new `Debug.Log` besides the existing "Auto-added" line and the single controller-less warning.
- Verification: `dotnet build Impact.sln` from `Impact/` (new files are invisible to `dotnet build` until Unity regenerates the csproj, so the Unity runs below are the real compile); then `-Filter "Impact.EditModeTests.Animation"` and `-Filter "Impact.PlayModeTests.Animation"`. Expected: all green except `MoveSpeedNormalized_Characterization_AssumedRunSpeedSix`, which must fail by assertion. Report any other red as a regression, not as expected.

### Order 3: test lane, T-5 + T-6

Fence: as order 1. Tests that exist after order 2:
- AC-3, AC-4: `RecordingAnimationBackend` attached by G3 to a character with no GameObject; assert it records the written sequence. Collapse consecutive identical writes in the expectation (gating). Same sequence on a second, Animator-backed character in the same run; compare Animator discrete parameters per step.
- AC-5: field-map reflection test; in PlayMode on the real Viking controller, set each Parameter and OptionalParameter field to a distinct value and read the parameter back by the table's name and type (sentinel for the optional ones that the controller lacks: skip with a recorded reason, never silently).
- Also: the `Equals`-covers-every-field reflection test.
- AC-6: two `MaxSpeed` values per § Single speed source; default recordings equal order 1.
- AC-7: per § Authoring.
- AC-8, AC-9, AC-10: § Ordering sort test; character with no `OwnedByPlayerEntity` and no camera updates and reaches the double; player character with owner and no `OrbitCamera` updates with `CameraRotationOffset == 0` and `IsTurningInPlace == false`.
- AC-11: double counts zero `Apply` over unchanged frames; sentinel test for the Animator layer; G3 relink test.
- AC-12: extend `CharacterAnimationBridgeEditModeTests`: Animator-less instance warns once over several ticks and the state keeps updating; swap to another Animator-less instance warns once more; after destroy a later Animator-less character warns once (bookkeeping released). Count log lines by captured log.
- AC-13: the ten S1 tests and the green control run unchanged. The expected edit to the S1 fixtures is zero lines; the only fixture edits are additive (`AttachBackend`, the bridge-off switch, the double).
- Replace `MoveSpeedNormalized_Characterization_AssumedRunSpeedSix` with `MoveSpeedNormalized_FollowsSpeedReference`.
- T-6: re-run `CharacterAnimationCostMeasurement` after extending the bridge-off switch to the presentation system; same machine, N, repeats; report both figures and the difference.
- Verification: `dotnet build Impact.sln`; the two `-Filter` runs; full `-CoreOnly` on EditMode and PlayMode, read `total=` and failures from the XML.

The integration gate (tech-lead INTEGRATION) runs after order 3: `dotnet build Impact.sln`, EditMode `-CoreOnly`, PlayMode `-CoreOnly`. The reviewer gate fires (the story carries acceptance criteria).

## Extension points

Designed for S3 to S6, not built.

- S3 (NPC at scale): nothing to add. AC-9 removes the player coupling; the double and the measurement fixture are its tools.
- S4 (strafe, lock-on): sets `isStrafing`, re-adds camera lookups in the existing branch; the fields and parameters already map. The activation model is not in this design.
- S5 (clip events, action layers): a second optional interface checked with `is` by the bridge at link time (for example `ICharacterAnimationEventSource` with a method taking the entity and an `EntityCommandBuffer`-like sink). A state field for the action request is added to `CharacterAnimationState`; the `Equals` reflection test and the field-map test fail until it is mapped or marked EcsOnly, which is the point of those tests.
- S6 (root motion): same mechanism for a return delta. Presentation latency (one frame) is the known cost; moving presentation to the end of `SimulationSystemGroup` is a one-attribute change if it matters.
- A second non-Animator backend: implement `ICharacterAnimationBackend`, and give the bridge a way to choose it (the bridge's `TryLink` is the only place that decides). Not designed here (D-2).

## Guardrail check

- Guardrail 1: no edit under `Library/PackageCache` or `com.projectdawn.navigation`. Entities docs were read only.
- Guardrail 2: production gains no `.asmdef` reference. The interface lives in `Athena.Shared.Components`, which `athena.gameplay` already sees. `Athena.Shared.Runtime` already references `Athena.CharacterController.Runtime` (the new `UpdateAfter` target). `athena.charactercontroller` is not edited and does not reference shared. Test asmdefs gain two references to existing runtime assemblies; no runtime assembly references the test assemblies, so no cycle.
- Guardrail 3: every order ends with `dotnet build Impact.sln` and the Unity runs above; baking is not exercised by `dotnet build`, which is why AC-7 evidence is stated as partial.
- Guardrail 4: no roadmap or ticket document is created; the measurement record lives in the run artifacts.
- Guardrail 5: no `Library/`, `Temp/`, `obj/`, `Logs/` or `.csproj` edit; the measurement writes no repo file.
- No decision here forces a REFUSED.

## Decisions engineers must not make independently

- Interface name, method name and signature: `ICharacterAnimationBackend.Apply(in CharacterAnimationState)`. No second method, no default interface methods.
- The presentation system lives in `PostEntityLifecycleGroup`, after the bridge. Not in `PresentationSystemGroup` and not at the end of `SimulationSystemGroup`.
- `MoveSpeedNormalized` is the unsmoothed `saturate(speed/maxSpeed)`; the Animator adapter smooths; nothing else smooths.
- The Animator parameter named `MoveSpeed` is fed by the field `MoveSpeedNormalized`. The field `MoveSpeed` is raw and EcsOnly.
- `IsStrafing` is written as a Float. `IsMoving` is written inverted as `IsStopped`. `IsStopped`, `IsStarting` and the three `MovementInput*` parameters stay optional.
- Speed default 7 lives only as `CharacterAnimationSpeedReference.DefaultMaxSpeed`; the gait literals 1.75 and 8 are scaled by `maxSpeed / DefaultMaxSpeed`; `MaxSpeed <= 0` means the default.
- Equality in gating is hand-written `Equals`, never memcmp. Float comparison is exact.
- The three retired fields stay in the struct and stay computed. `JumpTriggered` is not renamed.
- Error semantics: no new try/catch; a controller-less Animator warns once per adapter; a null `Backend` skips silently.
- Units: speeds in world units per second; angles in degrees as today; durations in seconds as today.
- Absent data: no `CharacterAnimationSpeedReference` means the default; no `OwnedByPlayerEntity` and no camera mean neutral camera values; no `Spawned` instance means no link and no warning.
- The double's attachment path is G3. Do not add a public registration API.
