REPORT 2026-10-07-ecs-animation-approach/05
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design pass, order verification was NONE

contract_notes:
  - CharacterAnimationBridgeInitialized changes from empty struct tag to managed class cleanup component carrying GameObject LinkedInstance (Athena.Shared.Components). Only the bridge system reads it, grep-verified; no other package is affected, see § Contract
  - HybridGameObject.Prefab on a character becomes an invariant: the baked default visual, never written by a system after baking. Shape unchanged, behaviour of SpawnHybridCharacterSkinSystem changes, see § Contract
  - New public system CharacterAnimationBridgeCleanupSystem in Athena.Shared.Systems, PostEntityLifecycleGroup. No component read by athena.gameplay or athena.charactercontroller changes
  - Test asmdefs Impact.EditModeTests and Impact.PlayModeTests need a Unity.Transforms reference. It is an engine package, not an Athena assembly, so no guardrail 2 edge is added
  - CHARACTER_ANIMATION_SETUP.md and athena.shared PACKAGE_DOCUMENTATION.md:97 lag this change (the "initialized repeatedly" claim is inverted). Docs lane at close-out, S9 interim pass

pack_corrections:
  - none

handoff:
  - Dispatch order is test (red), backend (green), integration. This reverses the order's backend-then-test, because red-before-fix is only provable if tests exist first, see § Lane split and verification
  - Test lane writes fixtures and tests in § Test plan, runs them on UNMODIFIED code, and records each as RED by assertion, never by compile error. No test may reference a type or member the backend adds
  - Backend lane edits only the five files in § Backend plan, then runs dotnet build Impact.sln. It must not touch CharacterSkinChangeSystem.cs, CharacterAnimatorSync.cs or the authoring bakers
  - Test E3 (generic spawner honours HybridGameObjectManualCreation) is conditional: backend applies the one-line guard only if test lane reports E3 red, see § Backend plan item 5
  - Git status was clean at design time (HEAD 9bb46bb), so D-7's precondition looks met. All file:line below are HEAD. The orchestrator should confirm with the human before build dispatch
  - Integration runs dotnet build Impact.sln, then Run-UnityTests.ps1 EditMode -CoreOnly and PlayMode -CoreOnly, and reads total= from the results XML

skill_calls:
  - mattpocock-skills:codebase-design — called, before naming the marker shape and the lifecycle owner. Applied: the bridge module owns the link lifetime (deletion test, locality), tests cross its interface, the seam is left open

risks:
  - Not run in Play mode: all four defects are confirmed by code read plus Entities cleanup-component docs (components-cleanup.md), none by execution. The red test run is the execution proof; a defect that does not go red is reported as not confirmed
  - Marker struct to class adds one managed-component reference compare per linked character per frame in the bridge's second pass. About 15 microseconds at 150 characters by estimate, unmeasured. S2's cost work should treat it as an input
  - Defect 9 (generic spawner ignores HybridGameObjectManualCreation) is unproven. In normal flow the character is spawned in EntityLifecycleGroup before the generic spawner runs, so it may never fire. Conditional guard only
  - E1 and E2 build PostEntityLifecycleGroup from every system carrying UpdateInGroup(PostEntityLifecycleGroup) via TypeManager. If another system's OnCreate throws in an empty world, fall back to an explicit list that includes the new cleanup system by type name at backend time
  - EditMode cannot call Object.Destroy (logs an error), so swap and despawn tests that go through CharacterSkinChangeSystem or HybridGameObjectSystemBase are PlayMode. EditMode tests emulate a swap with DestroyImmediate plus manual cleanup-component edits
  - PlayMode tests use an in-memory UnityEditor.Animations.AnimatorController under #if UNITY_EDITOR. Not run here. If it will not drive an Animator in a test, fall back to the real AC_Polygon_Masculine asset, as P4 already does
  - Crate loading is bypassed: the tests give CharacterSkinSwitchRequest a null LoadRequestEntity, which CharacterSkinChangeSystem allows (:93-119). The load pipeline stays covered only by the existing StartSwitchSkinProcess tests, CrateSystemEditModeTests.cs:465-543
  - D-8 and D-9 are irrelevant to S1. Producer brief said no review gate fires for S1; integration is the only gate

## Orchestrator brief
- Verdict: all four S1 defects CONFIRMED in code at HEAD (read, not run); a fifth (generic spawner ignoring ManualCreation) is UNCONFIRMED and conditional.
- Decision: the bridge system owns the animation link lifetime. Marker becomes a managed cleanup component holding the linked GameObject; the bridge relinks whenever Spawned.Instance differs. CharacterSkinChangeSystem is NOT edited.
- Decision: ghost shell fixed by a new CharacterAnimationBridgeCleanupSystem (PostEntityLifecycleGroup, after the bridge), same pattern as CharacterSkinCleanupSystem.
- Decision: default-skin return fixed by never writing HybridGameObject.Prefab; spawn from a local copy. No new component, no prefab or baker change.
- Contract: no component read across a package boundary changes. No new .asmdef reference in production. Test asmdefs add Unity.Transforms only.
- Lane split: test (fixtures + red tests, EditMode E1-E4, PlayMode P1-P5), then backend (5 files), then integration. Order deviates from the order text: tests first so red is provable.
- Blocks dispatch: only D-7, the human confirming the WIP commit. git status is clean now.
- Sections: Verified defects (4+1 with file:line) · Contract (shapes and invariants) · Backend plan (files, lifecycle, ordering, pseudocode) · Test plan (E1-E4, P1-P5, fixtures, red proof) · Lane split and verification (fences, commands) · S2 seam constraint.

## Verified defects

Read at HEAD 9bb46bb. Nothing run in Play mode; every claim below is from code plus the Entities docs.

**D1 Bridge marker never cleared on swap. CONFIRMED.**
- `CharacterAnimationBridgeInitialized` is added at `CharacterAnimationBridgeSystem.cs:37` and `:46`. A grep over all of `Impact/` shows no other use of the type except its declaration at `CharacterAnimationState.cs:113` and the query exclusion at `CharacterAnimationBridgeSystem.cs:24`.
- `CharacterSkinChangeSystem.cs:136` destroys the instance, and `:144-145` remove only `HybridGameObjectSpawned` and `CharacterSkinInitialized`.
- `SpawnHybridCharacterSkinSystem` then spawns the new instance and re-adds Spawned. The bridge query is `WithNone<CharacterAnimationBridgeInitialized>`, so the new instance is never linked.
- The Viking skin prefabs carry an Animator at the root and no `CharacterAnimatorSync` (02-recon line 87). The auto-add path therefore runs once and never again. The swapped character freezes.

**D2 Ghost entity shell. CONFIRMED.**
- The Entities docs (`com.unity.entities@d66668920c3f/Documentation~/components-cleanup.md`) state that destroying an entity removes only non-cleanup components, and the entity exists until every cleanup component is removed.
- A character carries four cleanup components: `HybridGameObjectSpawned` (removed by `HybridGameObjectSystemBase.HandleDespawns`, `:105-120`), `CharacterSkinInitialized` (removed by `CharacterSkinCleanupSystem`), `CharacterSkinSwitchRequest` (removed by `CharacterSkinSwitchCleanupSystem`) and `CharacterAnimationBridgeInitialized`.
- The last one has no remover, so every destroyed character stays alive as a shell. The shell no longer has `CharacterEntity`, which makes `WithNone<CharacterEntity>` the correct detector, exactly as `CharacterSkinCleanupSystem` already does.

**D3 Default-skin return spawns the previous override. CONFIRMED.**
- `SpawnHybridCharacterSkinSystem.cs:68` writes `hybridGameObject.ValueRW.Prefab = skinPrefabRefToUse`. The `else` branch for the default skin (`:62` condition, log only) never restores it.
- Nothing else stores the default prefab: the `CharacterSkinDefaultVisuals` block is commented out (`CharacterAuthoring.cs:73-76`).
- Trace Base to Warrior to Base. At the swap back, `CharacterSkinChangeSystem.cs:55-59` normalises the desired skin to `default` and rebuilds, then Spawn takes the default branch and instantiates `Prefab`, which still holds Warrior. The character is marked `CharacterSkinInitialized{default}` while showing Warrior, and the change system sees "equal" and stops.

**D4 Possible second CharacterAnimatorSync. CONFIRMED by code, only when the sync sits on a child.**
- `CharacterAnimationBridgeSystem.cs:32` uses `GetComponent<CharacterAnimatorSync>()` on the instance root only. `:41-44` then finds the first child Animator and `AddComponent`s a sync on it.
- A prefab with Animator and sync both on a child gets a second sync. Today's Viking prefabs have the Animator on the root, so this is latent, not live.

**D5 Generic spawner ignores HybridGameObjectManualCreation. UNCONFIRMED.**
- `HybridGameObjectSystemBase.cs:54` and `:82` select any `HybridGameObject` without Spawned and do not exclude `HybridGameObjectManualCreation` (`HybridGameObject.cs:15`).
- Whether it fires depends on where the character is created. The player systems sit in `EntityLifecycleGroup`, which runs before `PostEntityLifecycleGroup`, so Spawn probably wins. Not provable by reading. Test E3 decides.

**Not a defect, checked.** The swap frame ordering is fine. In one frame: `CharacterSkinChangeSystem` removes Spawned (ECB played back inside OnUpdate), then `SpawnHybridCharacterSkinSystem` respawns, then the bridge sees the new Spawned. The old sync lives to end of frame (`Object.Destroy` is deferred) and links the same entity for that one frame, which is harmless.

## Contract

No component or singleton that another package reads changes shape. The reads are all inside `athena.shared` (`Athena.Shared.Components` and `Athena.Shared.Runtime`). `athena.gameplay` and `athena.charactercontroller` contain no reference to any type below (grep over `Impact/Packages` and `Assets`).

| Type | Assembly | Change |
|---|---|---|
| `CharacterAnimationBridgeInitialized` | `Athena.Shared.Components` (`CharacterAnimationState.cs:113`) | `struct : ICleanupComponentData` (empty) becomes `class : ICleanupComponentData { public GameObject LinkedInstance; }`. Same name, same file, add `using UnityEngine;`. Precedent for a managed cleanup component: `HybridGameObjectSpawned` (`HybridGameObject.cs:19`). Callers of the generic `AddComponent<CharacterAnimationBridgeInitialized>()` (two, both in the bridge) are rewritten. |
| `CharacterAnimationBridgeCleanupSystem` | `Athena.Shared.Runtime`, namespace `Athena.Shared.Systems` | New file, new public `partial struct : ISystem`. |
| `HybridGameObject` | `Athena.Shared.Components` | Shape unchanged. Invariant added: `Prefab` is the baked default visual and no system writes it after baking. |
| `CharacterAnimationState`, `CharacterAnimationRuntimeState`, `HybridGameObjectSpawned`, `CharacterSkinInitialized`, `CharacterSkinSwitchRequest`, `CharacterCameFromCrate`, `SkinCrateLoadedSingleton` | | Unchanged. |
| `CharacterAnimatorSync` | | Unchanged. No new public member, so S1 tests observe it only through Animator parameters. |

Lifecycle invariants backend must make true and tests assert:

- **I1 Link on change.** In the `PostEntityLifecycleGroup` update where a character's `HybridGameObjectSpawned.Instance` first holds a new, non-null instance containing an Animator, that instance gets exactly one `CharacterAnimatorSync`, initialised with that entity and the entity's world. This holds for the first spawn and for every later respawn, regardless of which system changed Spawned.
- **I2 Marker tracks the instance.** After the bridge runs, `marker.LinkedInstance == Spawned.Instance` for every linked character. A mismatch means relink.
- **I3 One sync per instance.** The root-or-child lookup finds an existing sync before adding one.
- **I4 No shell.** Within one `PostEntityLifecycleGroup` update after a character entity is destroyed, the marker is removed. Entity existence then depends only on the other cleanup components, which their own systems remove.
- **I5 Default is stable.** `HybridGameObject.Prefab` equals its baked value for the life of the entity. A spawn for the default skin instantiates that value.

Decisions engineers must not make themselves:

- Marker is a managed class holding the GameObject, compared with the UnityEngine `==` operator. Do not use `GetInstanceID()`: its status in 6000.4 was not verified, and the object comparison needs no ID.
- Marker removal on swap belongs to the bridge, not to `CharacterSkinChangeSystem`.
- The cleanup removal uses the whole-query `EntityManager.RemoveComponent<T>(query)`, not a per-entity loop.
- Auto-add keeps `Debug.Log("Auto-added ...")` unchanged. No new logging beyond one `Debug.LogWarning` when an instance has no Animator and no sync (see Backend plan item 2).
- No `[BurstCompile]` on the new system: it queries a managed component.

## Backend plan

File fence (all under `Impact/Packages/athena.shared/Runtime/`):

1. `Components/Character/CharacterAnimationState.cs` — change the marker as in § Contract. Nothing else in the file.
2. `Systems/CharacterAnimationBridgeSystem.cs` — keep `SystemBase`, group `PostEntityLifecycleGroup`, `[UpdateAfter(typeof(SpawnHybridCharacterSkinSystem))]`. New body:
   - Create `ecb` as today.
   - Pass 1, unlinked: the existing query minus the marker, `WithAll<CharacterEntity>`. For each with `spawned.Instance != null`: call `TryLink`; on success `ecb.AddComponent(entity, new CharacterAnimationBridgeInitialized { LinkedInstance = spawned.Instance })`. This mirrors the `HybridGameObjectSpawned` add in `HybridGameObjectSystemBase.cs:146`.
   - Pass 2, stale: `SystemAPI.Query<CharacterAnimationBridgeInitialized, HybridGameObjectSpawned>().WithAll<CharacterEntity, CharacterAnimationState>().WithEntityAccess()`. For each: skip when `spawned.Instance == null` (respawn pending) or `marker.LinkedInstance == spawned.Instance`. Otherwise `TryLink`; on success set `marker.LinkedInstance = spawned.Instance` in place. This is a reference mutation, not a structural change.
   - `TryLink(GameObject instance, Entity entity, World world)` private helper:
     1. `var sync = instance.GetComponentInChildren<CharacterAnimatorSync>();` (self plus children, active only, same visibility as the Animator lookup below).
     2. If null: `var animator = instance.GetComponentInChildren<Animator>();` unchanged; if found, `sync = animator.gameObject.AddComponent<CharacterAnimatorSync>()` and keep the existing auto-add log.
     3. If a sync exists: `sync.Initialize(entity, world); return true`. Else `return false`.
   - `ecb.Playback(EntityManager)` and `Dispose()` as today. Keep structural changes in the ECB so they happen outside iteration.
3. `Systems/CharacterAnimationBridgeCleanupSystem.cs` — NEW, one type per file.
   - `[UpdateInGroup(typeof(PostEntityLifecycleGroup))]`, `[UpdateAfter(typeof(CharacterAnimationBridgeSystem))]`, `public partial struct CharacterAnimationBridgeCleanupSystem : ISystem`.
   - `OnCreate`: cache `destroyedLinkQuery = SystemAPI.QueryBuilder().WithAll<CharacterAnimationBridgeInitialized>().WithNone<CharacterEntity>().Build();` and `state.RequireForUpdate(destroyedLinkQuery);`. This is the same shape as `CharacterSkinCleanupSystem.cs:15-22`.
   - `OnUpdate`: `if (destroyedLinkQuery.IsEmptyIgnoreFilter) return; state.EntityManager.RemoveComponent<CharacterAnimationBridgeInitialized>(destroyedLinkQuery);`
   - Namespaces and usings follow the neighbours: `Athena.Shared.Components`, `Unity.Entities`.
4. `Systems/Player/SpawnHybridCharacterSkinSystem.cs` — stop mutating the default prefab:
   - Query `RefRW<HybridGameObject>` becomes `RefRO<HybridGameObject>` (`:48`). The `OnCreate` query at `:20-23` needs no change.
   - Replace `hybridGameObject.ValueRW.Prefab = skinPrefabRefToUse;` (`:68`) with a local `var hybridToSpawn = hybridGameObject.ValueRO;` declared before the `if`, and `hybridToSpawn.Prefab = skinPrefabRefToUse;` in the override branch. Pass `hybridToSpawn` to `SpawnAndAssignHybridGameObject`.
   - Change that method's first parameter from `ref HybridGameObject` to `in HybridGameObject` (`:91`); `SpawnGameObjectForEntity` already takes `in`.
   - Result: the default branch spawns the baked prefab, and the not-ready fallback now also spawns the baked default instead of a stale override. No other logic changes (no refactor of the unused parameters).
5. `Systems/Hybrid/HybridGameObjectSystemBase.cs` — CONDITIONAL on test E3 being red. Add `.WithNone<HybridGameObjectManualCreation>()` to `spawnedHybridQuery` (`:52-55`) and to the `HandleSpawns` foreach (`:81-83`). Do NOT add it to the despawn query (`:57-60`, `:106-109`): that path is what destroys a destroyed character's GameObject, and the shell cannot finish without it. If E3 is green on current code, leave this file untouched and record that in `risks`.

Not edited: `CharacterSkinChangeSystem.cs`, `CharacterAnimatorSync.cs`, both authoring bakers, `HybridGameObject.cs`, `CharacterEntity.cs`, any `.asmdef`, any prefab, the Animator controller.

System ordering this change relies on (all `PostEntityLifecycleGroup`, which is `OrderFirst` in `SimulationSystemGroup`, `EntityLifecycleGroup.cs:10-13`):
`CharacterSkinChangeSystem` (UpdateBefore Spawn) → `SpawnHybridCharacterSkinSystem` → `CharacterAnimationBridgeSystem` (UpdateAfter Spawn) → `CharacterAnimationBridgeCleanupSystem` (UpdateAfter Bridge). `CharacterSkinCleanupSystem` (UpdateAfter Spawn) and `CharacterSkinSwitchCleanupSystem` (UpdateAfter SkinCleanup) are unordered against the new cleanup system, and that is fine: they remove independent components. Each system plays back its own ECB before returning, so the next system in the group sees the structural changes in the same frame. `HybridGameObjectSystemBase` stays in the default group and runs after the whole group, as it does now.

Structural changes: ECB add in the bridge (pass 1), in-place class mutation (pass 2), `EntityManager.RemoveComponent(query)` in the cleanup system. All on the main thread inside `PostEntityLifecycleGroup`, with no job dependency, matching the neighbours.

## Test plan

Which assemblies reach the change: `Impact.EditModeTests` and `Impact.PlayModeTests` both reference `Athena.Shared.Runtime` and `Athena.Shared.Components` (testing.md § Which packages a test can see). Everything under change is in `athena.shared`, so both reach it. `Unity.Transforms` is the one new asmdef reference needed, in both test asmdefs, for `LocalToWorld`. State it in `changed`.

**Reuse, by name:**
- `Assets/Tests/EditMode/Crates/LevelCrateTestContext.cs` (internal sealed, namespace `Impact.EditModeTests.Crates`): creates the world, `GameCrateSingleton` via `GameCrateLoadSystem`, and `RegisterCrate(guid, name)`. EditMode animation tests use it as the world owner.
- `CharacterCrateLookupEditModeTests.CreateLookupSingleton(...)` (private static, `:90-onward`): builds the `CharacterCrateLookupSingleton` blob. Extract it to a shared internal static helper under `Assets/Tests/EditMode/TestSupport/` and call it from both fixtures. That edit changes an existing green fixture; the test lane reports it in `changed` and keeps those two tests green.
- `CrateSystemEditModeTests.cs:331-375`: the pattern for registering a skin crate so `CreateSkinInitialized` can instantiate the keep-loaded entity.
- `LevelCratePlayModeTestHarness.cs` (internal sealed, IDisposable, `new World(..., WorldFlags.Game)`, handle-driven updates, `#if UNITY_EDITOR` for asset lookup): the pattern for the PlayMode harness. The PlayMode assembly cannot see EditMode helpers, so the small crate-registration code is duplicated on purpose. Do not create a shared test asmdef for this.
- `SkinCrateUpdateLoadedSystem` `OnCreate` (`:29-31`) creates `SkinCrateLoadedSingleton`: create that system, do not update it, to get the singleton and its `OnDestroy` dispose.
- `HybridGameObjectTransformSystem` `OnCreate` creates its Singleton and `HybridGameObjectSystemBase.OnCreate` creates `HybridGameObjectSingleton`: create both systems to satisfy `RequireForUpdate`.

**New fixtures:**
- EditMode `Assets/Tests/EditMode/Animation/CharacterAnimationEditModeWorld.cs`, internal sealed, IDisposable. It wraps `LevelCrateTestContext`, creates the singletons above, and builds a real `PostEntityLifecycleGroup`: add it with `world.GetOrCreateSystemManaged<PostEntityLifecycleGroup>()`, then add each system type whose `UpdateInGroup` attribute names `PostEntityLifecycleGroup` (enumerate with `TypeManager.GetSystems(WorldSystemFilterFlags.Default)`), then `SortSystems()`. Driving the real group is deliberate: it exercises the `UpdateBefore/After` attributes, which is where this repo regresses, and it picks up the backend's new cleanup system with no test edit. Members: `CreateCharacter(defaultPrefab, crateGuid, skinGuid)` building an entity with `CharacterEntity, CharacterCameFromCrate, HybridGameObject, HybridGameObjectManualCreation, CharacterAnimationState, LocalToWorld`; `Tick()` that calls `group.Update()` then updates the generic spawner; `Dispose()` that `DestroyImmediate`s every GameObject the world's `HybridGameObjectSpawned` components hold, then disposes the world.
- PlayMode `Assets/Tests/PlayMode/Animation/CharacterAnimationPlayModeHarness.cs`, same shape, plus: a `SetAnimationState(entity, state)` helper, an `AnimatorParam` read helper, and a frame-advancing `IEnumerator Tick()` that calls the group and the generic spawner, then `yield return null` so `Object.Destroy` completes and the sync's `Update` runs. Keep "write state" and "read presentation" behind these two helpers so S2 can swap the read side.
- Prefab builders in the harness, all `#if UNITY_EDITOR`: (a) Animator on root, no sync; (b) Animator and sync both on root; (c) Animator and sync on a child. Each has an in-memory `UnityEditor.Animations.AnimatorController` with parameters `CurrentGait` (Int) and `IsJumping` (Bool), plus one state so the controller is valid. Give each prefab a distinct name (`DefaultVisual`, `SkinVisual`) so the test can tell which one a spawned instance came from by `instance.name == "<name>(Clone)"`.

**Tests. Red means fails by assertion on current HEAD.**

EditMode, fixture folder `Assets/Tests/EditMode/Animation/`:

| Id | Fixture.Test | Asserts | Today |
|---|---|---|---|
| E1 | `CharacterAnimationBridgeEditModeTests.DestroyedCharacter_LeavesNoCleanupShell` | Link a character (Spawned with an Animator instance, tick). Destroy the entity. Remove `HybridGameObjectSpawned` from the shell by hand (this stands in for `HandleDespawns`, which cannot run here because `Object.Destroy` is illegal in EditMode). Tick. Assert `!Exists(entity)`, and a query on `ComponentType.ReadOnly(typeof(CharacterAnimationBridgeInitialized))` over all entities returns 0. Reference the marker by `typeof` only, never by field. | RED: shell remains because of the marker (D2) |
| E2 | same fixture, `InstanceReplaced_RelinksNewInstance_SingleSyncPerInstance` | Link instance A (Animator on root, no sync). Emulate the swap exactly as `CharacterSkinChangeSystem` ends it: `DestroyImmediate(A)`, remove Spawned, then add Spawned holding new instance B. Tick. Assert B contains exactly one `CharacterAnimatorSync` (`GetComponentsInChildren<CharacterAnimatorSync>().Length == 1`). Variant on a prefab with Animator and sync on a child: after the first tick, assert still exactly one. The swap system is not in this test, so it pins I1 and I3 as properties of the bridge. | RED for B (D1); RED for the child variant (D4: two syncs) |
| E3 | `HybridGameObjectSystemBaseEditModeTests.ManualCreationCharacter_IsNotSpawnedByGenericSpawner` | World with only the transform system and `HybridGameObjectSystemBase`. Character entity has `HybridGameObjectManualCreation` and a valid prefab. Update the generic spawner once. Assert the entity has no `HybridGameObjectSpawned`. `DestroyImmediate` anything it did spawn. | UNKNOWN. Report the result either way. Red means backend item 5 is applied |
| E4 | `SpawnHybridCharacterSkinSystemEditModeTests.ReturnToDefaultSkin_SpawnsDefaultPrefab` | Singletons and a registered skin crate and prefab (registered with `RegisterObjectRef`). Spawn with a skin set: assert instance name is `SkinVisual(Clone)`. Emulate the swap-back: `DestroyImmediate`, remove Spawned and `CharacterSkinInitialized`, set `CharacterCameFromCrate.SkinCrateGuid = default`, tick. Assert instance name is `DefaultVisual(Clone)`. Also assert `GetComponentData<HybridGameObject>(entity).Prefab` still equals the baked default. | RED (D3): respawns `SkinVisual` |

PlayMode, folder `Assets/Tests/PlayMode/Animation/`, fixture `SkinSwapAnimationPlayModeTests`, all `[UnityTest]`:

| Id | Test | Asserts | Today |
|---|---|---|---|
| P1 | `SkinSwap_AnimatorOnlyPrefab_NewInstanceIsLinkedAndDriven` | Spawn default, tick: set `CharacterAnimationState.CurrentGait = 2`, `IsJumping = true`, yield a few frames, assert the first instance's animator reads `CurrentGait == 2`. Run the real `CharacterSkinChangeSystem` swap (set `CharacterCameFromCrate.SkinCrateGuid`, add `CharacterSkinSwitchRequest` with a null `LoadRequestEntity`). After the swap: the new instance is `SkinVisual(Clone)`, change state to `CurrentGait = 3`, yield frames, assert the NEW animator reads 3. Use discrete parameters only. `MoveSpeed` is smoothed in `CharacterAnimatorSync.cs:177-179` and would need a tolerance. | RED (D1) |
| P2 | `SkinSwap_PrefabWithPreAttachedSync_NewInstanceIsLinkedAndDriven` | Same as P1 with prefab (b). | RED (D1: marker blocks `Initialize`) |
| P3 | `SkinSwap_BackToDefault_ShowsDefaultPrefabAndStaysDriven` | Default, then skin, then default again, using the real change system both times. Assert instance names `DefaultVisual`, `SkinVisual`, `DefaultVisual`, and that each live instance's animator follows the state. Assert exactly one live instance exists under the harness's instance scene after each step. | RED (D1, D3) |
| P4 | `SkinSwap_RealVikingPrefabs_BaseToWarriorToBase` | Done-criterion (2) on real content: load `Assets/Content/Characters/Viking/Gameplay/Skins/Viking_BaseSkin_Visuals.prefab` and `Viking_WarriorSkin_Visuals.prefab` with `AssetDatabase`, `#if UNITY_EDITOR`, same precedent as the harness. Default prefab is Base, skin prefab is Warrior (synthetic crate guids). Base, Warrior, Base. Each step: instance name matches, the live Animator uses `AC_Polygon_Masculine`, and `CurrentGait` set from ECS appears on it. | RED (D1, D3) |
| P5 | `CharacterLifecycle_SpawnSwapDestroyCycles_LeaveNoShells` | Record `GetAllEntities().Length` as the baseline (it includes every entity, shells too). Run 20 cycles of spawn, link, swap, destroy, yielding frames so `HandleDespawns` runs and `Object.Destroy` completes. After the last tick assert: entity count equals the baseline, no entity matches the marker query, every spawned instance is destroyed, and `SkinCrateLoadedSingleton` shows `RefCount == 0` for the skin guid. This is done-criterion (3), including the loop the producer asked for. | RED (D2), since shells accumulate to 20 |

Red proof: the test lane runs the new tests with `Run-UnityTests.ps1 -Platform EditMode -Filter "Impact.EditModeTests.Animation"` and `-Platform PlayMode -Filter "Impact.PlayModeTests.Animation"` on unmodified production code, and records the failing assertion text for each of E1, E2, E4, P1-P5, and the E3 outcome. A test that fails to compile, throws in setup, or fails on a log message instead of an assertion is a fixture bug, not a red. Existing tests must stay green in the same run.

Not covered by S1 on purpose: crate loading (existing tests), state computation and gait (S2 characterization), strafe and NPC (S3, S4), the Keyboard null check (debt).

## Lane split and verification

Order: **test, then backend, then integration.** Reason: the producer's done criterion (1) requires a red test before any fix, and the red evidence is only obtainable if the tests exist while production code is still unmodified. No test references the new cleanup system, or any marker field, so the tests compile on both sides of the fix. If the orchestrator prefers backend-first, the red run is impossible without a second checkout of the Unity project, which is not practical, so the fallback is to accept green-only evidence and say so in the ledger.

| Lane | File fence | Verification |
|---|---|---|
| test (first) | `Impact/Assets/Tests/EditMode/**`, `Impact/Assets/Tests/PlayMode/**`, both test `.asmdef` files (add `Unity.Transforms`), `Impact/Tools/**` only if a script change is needed. No production code. | `dotnet build Impact.sln`, then the two `-Filter` runs above, results written to XML, red recorded. Then the full `-CoreOnly` EditMode run to show the existing tests stay green. |
| backend | The five files in § Backend plan, all under `Impact/Packages/athena.shared/Runtime/`. Item 5 only if E3 is red. No tests, no `.asmdef`, no prefab, no `Library/`. | `dotnet build Impact.sln` from `Impact/`. Then the `-Filter` runs for `Impact.EditModeTests.Animation` and `Impact.PlayModeTests.Animation`, expecting all green. |
| integration (tech-lead) | read plus run | `dotnet build Impact.sln`; `powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly`; `powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform PlayMode -CoreOnly`. Read `total=` and failures from the results XML. PlayMode is required: the change reaches runtime spawn and skin flow. Close the Editor first, since batchmode fails if the project is open. |

Integration review checklist for this slice:
- Marker class, two-pass bridge, cleanup system and the `SpawnHybridCharacterSkinSystem` edit match § Backend plan.
- No edit to `CharacterSkinChangeSystem.cs`, `CharacterAnimatorSync.cs`, any baker, any `.asmdef` outside the two test asmdefs.
- The tests assert behaviour (Animator parameter, instance name, entity existence), not implementation (no private-field reflection, no marker fields).
- Red evidence exists in the test report for E1, E2, E4, P1-P5.
- Doc lag is recorded for the docs lane: `PACKAGE_DOCUMENTATION.md:97` and `CHARACTER_ANIMATION_SETUP.md` ("runs once", marker semantics).

## S2 seam constraint

Constraints only. S2 designs the seam.

- S1 must not spread link ownership. The bridge system is the only code that adds, updates or removes the link. Do not add link clearing to `CharacterSkinChangeSystem`, the despawn path or the spawn system. A later backend then replaces one module, not three.
- S1 must not widen what other code can see. The marker and the new cleanup system stay readable only inside `athena.shared`. No new public member on `CharacterAnimatorSync`, no event, no accessor. S1 tests observe it through Animator parameters only, so replacing the MonoBehaviour does not break them.
- S1 must not bake "an Animator exists" into the lifecycle contract beyond the marker's one `GameObject LinkedInstance` field. I1 to I5 are phrased in terms of "presentation instance changed, relink" and "entity destroyed, unlink". They must stay valid when the linked thing is not a Mecanim Animator.
- S1 must not change `CharacterAnimationState`, parameter names, the parameter-writing code, or either baker. S2 owns the state shape and the mapping.
- S1 must not move the bridge out of `PostEntityLifecycleGroup` or change its position after `SpawnHybridCharacterSkinSystem`. S2 will turn that into an explicit contract.
- S1 must not add any `.asmdef` reference in production, and must not put new logic in `athena.charactercontroller`, `athena.gameplay` or `athena.ai`.
- S1 must keep steady-state cost flat: the cleanup system is archetype-gated by `RequireForUpdate`, and the bridge's added per-frame work is one reference compare per linked character. No per-frame allocation, no per-frame `GetComponent`. S2 measures against that baseline.
- The PlayMode harness keeps its two seams narrow: "write ECS animation state" and "read what the presentation shows". S2 reuses the harness by swapping the read helper for a test-double backend.
