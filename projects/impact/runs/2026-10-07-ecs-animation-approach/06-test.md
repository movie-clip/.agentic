REPORT 2026-10-07-ecs-animation-approach/06
status:      DONE
verdict:     NONE

changed:
  - Impact/Assets/Tests/EditMode/Impact.EditModeTests.asmdef — added Unity.Transforms reference (LocalToWorld); nothing else
  - Impact/Assets/Tests/PlayMode/Impact.PlayModeTests.asmdef — added Unity.Transforms reference; nothing else
  - Impact/Assets/Tests/EditMode/TestSupport/CharacterCrateLookupTestFactory.cs — NEW internal static helper, extracted from CharacterCrateLookupEditModeTests.CreateLookupSingleton
  - Impact/Assets/Tests/EditMode/CharacterCrateLookupEditModeTests.cs — private builder removed, now calls the shared factory; both existing tests still green
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationEditModeWorld.cs — NEW fixture: real PostEntityLifecycleGroup built from UpdateInGroup attributes, reuses LevelCrateTestContext
  - Impact/Assets/Tests/EditMode/Animation/CharacterAnimationBridgeEditModeTests.cs — E1, E2, E2b (child-sync variant) and one green control test
  - Impact/Assets/Tests/EditMode/Animation/HybridGameObjectSystemBaseEditModeTests.cs — E3 generic spawner vs HybridGameObjectManualCreation
  - Impact/Assets/Tests/EditMode/Animation/SpawnHybridCharacterSkinSystemEditModeTests.cs — E4 return to default skin
  - Impact/Assets/Tests/PlayMode/Animation/CharacterAnimationPlayModeHarness.cs — NEW harness: world, real group, in-memory AnimatorController prefabs, SetAnimationState / ReadAnimatorInt seams
  - Impact/Assets/Tests/PlayMode/Animation/SkinSwapAnimationPlayModeTests.cs — P1 to P5, all [UnityTest]; PlayMode because Object.Destroy and frames are needed
  - Unity generated .meta files for the new Animation and TestSupport folders and files (not hand-edited)

verification:
  command:   cd Impact; dotnet build Impact.sln; Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly (results to XML)
  result:    PASS
  detail:    dotnet build 0 errors. EditMode total=45 passed=40 failed=5; PlayMode total=8 passed=3 failed=5. All 10 failures are the new fixtures failing by assertion, matching 05 exactly; 42 pre-existing tests green.

contract_notes:
  - none

pack_corrections:
  - testing.md § Which packages a test can see — row Impact.PlayModeTests lacks Unity.Transforms. Replace with: "shared (Runtime, Components), contentmanagement, Unity.Transforms" and add Unity.Transforms to the EditMode row

handoff:
  - Backend lane 07 turns green: all E1 E2 E2b E3 E4 and P1 to P5. Item 5 of 05 § Backend plan (HybridGameObjectSystemBase guard) IS needed: E3 is red, so D5 is confirmed
  - Run command for either platform: Run-UnityTests.ps1 -Platform X -Filter "Impact.EditModeTests.Animation" (or Impact.PlayModeTests.Animation) -ResultsFile <abs path>. Filter prefix works
  - Run-UnityTests.ps1 returns before Unity exits (Unity.exe is not awaited): poll for the Unity.exe process to end, then read the XML. Exit code prints blank
  - New shared helper: Impact.EditModeTests.TestSupport.CharacterCrateLookupTestFactory.Create(...), same signature as the old private builder; caller disposes CharacterRootBlobData
  - New EditMode fixture CharacterAnimationEditModeWorld (internal, IDisposable): CreateVisual, Instantiate, RegisterSkinPrefab, CreateCharacter, Tick, ReplaceInstance, RemoveInstanceForRespawn, DestroyCharacter, CountEntitiesWith(Type)
  - New PlayMode harness CharacterAnimationPlayModeHarness: Tick(frames), SwapSkin (drives the real CharacterSkinChangeSystem), SetAnimationState, ReadAnimatorInt/Bool, LiveInstanceCount, CountAllEntities, GetSkinRefCount
  - Tests reference the marker only as typeof(CharacterAnimationBridgeInitialized); they compile on both sides of the fix and add no reference to the new cleanup system
  - Scratch result XMLs were removed from Impact/. Copies of the red run results are in the OS temp dir, not in the repo; the Red run table below is the record
  - Integration should expect P5 to stop at its first failing assertion today (entity count); the marker, instance and RefCount assertions after it only become exercised once the count assertion passes

skill_calls:
  - mattpocock-skills:tdd — called, before writing fixtures. Applied: seams fixed by 05 Test plan (bridge, spawn system, generic spawner, Animator parameters), one behaviour per test, red proven on unmodified code

risks:
  - Assert.Multiple does not exist in this project's NUnit (3.5 engine); first attempt failed to compile and ran no tests. Use sequential asserts; the pack should say so
  - dotnet build only sees new test files after Unity regenerates the .csproj. Before the first Unity run it errored on the modified existing file referencing the new TestSupport namespace; clean after Unity ran
  - EntityQuery objects disposed after World.Dispose throw NullReferenceException in TearDown (hit in the PlayMode harness, fixed by disposing queries first). Worth a Gotchas line in the pack
  - E3 red uses a world with only the transform system and the generic spawner, as 05 specified. Red proves D5 for that setup; whether the full game flow ever hits it stays unproven, as 05 noted
  - PlayMode prefabs are active hidden templates using an in-memory UnityEditor AnimatorController. It drove the Animator correctly (precondition reads of CurrentGait passed), so 05's fallback to the real controller was not needed except in P4 where it was planned
  - Unity touched ProjectSettings/ProjectSettings.asset (git shows modified, diff is line-ending noise only). Not mine, not reverted; the human may want to discard it
  - EditMode extra test PrefabWithAnimatorAndSyncOnRoot_StaysSingleSyncAcrossTicks is not in 05. It is a green control that passes today and must stay green after the fix
  - Only one hero and two skin crates are modelled; the skin crate load request is bypassed (null LoadRequestEntity) per 05, so crate loading stays covered by the existing tests only

## Orchestrator brief
- Outcome: all S1 tests exist and fail by assertion on unmodified code, exactly as 05 predicted: E1, E2, E2b, E4, P1 to P5 red.
- E3 is RED: D5 is confirmed, so backend must apply 05 Backend plan item 5 (WithNone<HybridGameObjectManualCreation> on the spawn query and HandleSpawns).
- One green control test (sync on root, two ticks) is extra to 05 and must stay green.
- Build clean (0 errors); existing Core tests all still pass (EditMode 40 of 45, PlayMode 3 of 8; the failures are the 10 new tests).
- Section Red run: per-test expected vs actual table with failing assertion text.
- Pack gaps in risks: no Assert.Multiple in this NUnit, new files invisible to dotnet build until Unity regenerates csproj, Run-UnityTests.ps1 does not wait for Unity.

## Red run

Unmodified production code (HEAD 9bb46bb plus tests only). Expected per 05 § Test plan against actual. Every actual failure is an assertion, none a compile or setup error.

| Test | Expected (05) | Actual | Failing assertion |
|---|---|---|---|
| E1 DestroyedCharacter_LeavesNoCleanupShell | RED (D2) | RED | shell exists: Expected False, was True |
| E2 InstanceReplaced_RelinksNewInstance_SingleSyncPerInstance | RED (D1) | RED | replacement linked once: Expected 1, was 0 |
| E2b PrefabWithAnimatorAndSyncOnChild_GetsSingleSync | RED (D4) | RED | Expected 1 sync, was 2 |
| E3 ManualCreationCharacter_IsNotSpawnedByGenericSpawner | either | RED | generic spawner spawned it: Expected False, was True. D5 confirmed, backend item 5 required |
| E4 ReturnToDefaultSkin_SpawnsDefaultPrefab | RED (D3) | RED | Expected DefaultVisual(Clone), was SkinVisual(Clone) |
| control PrefabWithAnimatorAndSyncOnRoot_StaysSingleSyncAcrossTicks | not in 05 | GREEN | n/a |
| P1 SkinSwap_AnimatorOnlyPrefab_NewInstanceIsLinkedAndDriven | RED (D1) | RED | new animator CurrentGait: Expected 3, was 0 |
| P2 SkinSwap_PrefabWithPreAttachedSync_NewInstanceIsLinkedAndDriven | RED (D1) | RED | new animator CurrentGait: Expected 3, was 0 |
| P3 SkinSwap_BackToDefault_ShowsDefaultPrefabAndStaysDriven | RED (D1, D3) | RED | SkinVisual(Clone) did not follow state: Expected 2, was 0 (stops at D1; D3 not reached) |
| P4 SkinSwap_RealVikingPrefabs_BaseToWarriorToBase | RED (D1, D3) | RED | Viking_WarriorSkin_Visuals(Clone) did not follow state: Expected 2, was 0 |
| P5 CharacterLifecycle_SpawnSwapDestroyCycles_LeaveNoShells | RED (D2) | RED | entity count: Expected 6 (baseline), was 26, i.e. 20 shells from 20 cycles |

Existing Core suite: EditMode 45 total, 40 passed, 5 failed (all new). PlayMode 8 total, 3 passed (the 3 pre-existing), 5 failed (all new). No pre-existing test newly broken; CharacterCrateLookupEditModeTests both green after the helper extraction.
