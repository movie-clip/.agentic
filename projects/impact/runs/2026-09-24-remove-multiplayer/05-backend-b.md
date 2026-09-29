REPORT 2026-09-24-remove-multiplayer/05
status:      PARTIAL
verdict:     NONE

changed:
  - Impact/Packages/athena.shared/Runtime/Components/GameAssetLoadFlags.cs — shrank enum to `{ None = 0, SetActiveScene = 1 << 3 }`; deleted Client/Server/Synchronize
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/Crates/BaseGameCrate.cs — shrank `LoadFlags` to `{ DoNotLoad, Development, _ }`; deleted `ConvertToLoadFlags`/`CheckForInvalidLoadFlags` and removed their 9 call sites across Create*Load helpers
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/Crates/GameCrate.cs — replaced 4 `ConvertToLoadFlags(entry.Flags)` args with literal `GameAssetLoadFlags.None`
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/Crates/LevelCrate.cs — `Client|SetActiveScene` -> `SetActiveScene`; `Client|Server` -> `None`
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/Crates/CharacterCrate.cs — `Client|Server` -> `None`
  - Impact/Packages/athena.shared/Runtime/Components/Authoring/Crates/CharacterSkinCrate.cs — `Client` -> `None`
  - Impact/Packages/athena.shared/Runtime/Components/GameAssetLoadSingleton.cs — deleted `RemoteLoadCount`/`RemoteSectionLoadCount` from `RequestAsset`; deleted `CriticalSyncVersion`/`NonCriticalSyncVersion` from the singleton
  - Impact/Packages/athena.shared/Runtime/Components/GameCrateSingleton.cs — deleted `CriticalSyncVersion`/`NonCriticalSyncVersion` properties
  - Impact/Packages/athena.shared/Runtime/Systems/Crates/GameCrateLoadSystem.cs — removed the two `CriticalSyncVersion++`/`NonCriticalSyncVersion++` blocks in `UpdateActiveCrates`, kept the Clear/AddRange bookkeeping
  - Impact/Packages/athena.shared/Runtime/Systems/Crates/GameAssetLoadSystem.cs — deleted `ShouldLoadRemotely`/`CanLoadLocally`/`GetWorldLoadFlags`; register/release paths' remote-load blocks deleted, local-load blocks made unconditional
  - Impact/Packages/athena.shared/Runtime/Systems/Crates/GameAssetLoadSystem.cs — `UpdateVersions` shrunk to 2 bool params, both call sites and both `ReleaseRequests` overloads updated; deleted the fully-commented `CheckIfEntitySceneHasPrespawnGhosts` block
  - Impact/Packages/athena.shared/Runtime/GameWorldStateRunner.cs — default `loadFlags` field `Client|Server` -> `None`; D-4 rename: field `authoritativeConfiguration`(`GameAuthoritativeConfiguration`) -> `sessionConfiguration`(`GameSessionConfiguration`); method `ConfigureLocalAuthoritativeWorld` -> `ConfigureLocalWorldSession` (decl, call site, Debug.Log string)
  - Impact/Packages/athena.shared/Runtime/Simulation/GameAuthoritativeConfiguration.cs — class renamed `GameAuthoritativeConfiguration` -> `GameSessionConfiguration` (D-4); filename left as-is, see handoff
  - Impact/Packages/athena.shared/Runtime/ServiceProvider.cs — field `AuthoritativeConfiguration`(`GameAuthoritativeConfiguration`) -> `SessionConfiguration`(`GameSessionConfiguration`), decl + 2 assignments (D-4)
  - Impact/Packages/athena.shared/Runtime/Systems/AuthoritativeCharacterSkinLoadSystem.cs — struct renamed `AuthoritativeCharacterSkinLoadSystem` -> `CharacterSkinLoadSystem` (D-4), 3 Debug.Log/LogWarning strings updated; filename left as-is, see handoff
  - Impact/Assets/Scripts/Runtime/StandaloneGameplayContext.cs — call site updated to `ServiceProvider.Instance.SessionConfiguration` (D-4)
  - Impact/Assets/Scripts/Runtime/Cheats/Commands/SkinCheatCommand.cs — call site updated to `CharacterSkinLoadSystem.StartSwitchSkinProcess` (D-4)
  - Impact/Packages/athena.shared/Runtime/Systems/Debug/GameCrateDebugSystem.cs — call site updated to `CharacterSkinLoadSystem.StartSwitchSkinProcess` (D-4)
  - Impact/Assets/Content/Core/gameWorldStateRunner.prefab — migrated serialized `loadFlags: 3` -> `loadFlags: 0` (the run's one migration)

verification:
  command:   cd C:\projects\impact\Impact && dotnet build Impact.sln && powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly
  result:    FAIL
  detail:    `dotnet build Impact.sln` alone (first half of the compound command) already fails with 14 CS errors, all confined to Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs and LevelCrateEditModeTests.cs (GameAssetLoadFlags.Client/.Server/.Synchronize, RequestAsset.RemoteLoadCount, AuthoritativeCharacterSkinLoadSystem) — the Test lane's dispatch per 03-technical-plan.md § Lanes item 3, explicitly not mine to touch per this order's non_goals. Supplementary isolated builds confirm every file this order touched compiles clean: `dotnet build Athena.Shared.Runtime.csproj` -> 0 Error(s); `dotnet build Assembly-CSharp.csproj` -> 0 Error(s). Run-UnityTests.ps1 was not run since the compound command's build step failed first and Unity's own domain reload would hit the identical compile errors.

contract_notes:
  - GameAssetLoadFlags shrank to {None, SetActiveScene} and BaseGameCrate.LoadFlags to {DoNotLoad, Development, _} exactly as 03-technical-plan.md § Target shapes specified — any doc describing the old Client/Server/Synchronize semantics (docs lane's list in 03-technical-plan.md § handoff) is now stale
  - GameAssetLoadSingleton and GameCrateSingleton both dropped their CriticalSyncVersion/NonCriticalSyncVersion fields — any external reader of these singletons (none found in athena.gameplay or athena.charactercontroller by grep) would need updating, but none exists
  - The D-4 rename (GameAuthoritativeConfiguration/AuthoritativeConfiguration/ConfigureLocalAuthoritativeWorld/AuthoritativeCharacterSkinLoadSystem) is complete in every non-test file; CrateSystemEditModeTests.cs still references the old type/method names in 2 test method names + 2 call sites, per 03-technical-plan.md § Rename plan item 4 this is the Test lane's edit, not mine

pack_corrections:
  - none

handoff:
  - Rename incomplete — no lane has a delete/rename tool — run: `git mv Impact/Packages/athena.shared/Runtime/Simulation/GameAuthoritativeConfiguration.cs Impact/Packages/athena.shared/Runtime/Simulation/GameSessionConfiguration.cs`
  - Rename incomplete (second file) — run: `git mv Impact/Packages/athena.shared/Runtime/Systems/AuthoritativeCharacterSkinLoadSystem.cs Impact/Packages/athena.shared/Runtime/Systems/CharacterSkinLoadSystem.cs`
  - Test lane's dispatch (03-technical-plan.md § Lanes item 3) must land before `dotnet build Impact.sln` can pass — all 14 current compile errors are in CrateSystemEditModeTests.cs and LevelCrateEditModeTests.cs, exactly the file/line list that plan section names
  - Two scope-fence path corrections found identical to what 04-backend-a already flagged: `GameAssetLoadSystem.cs` and `GameCrateLoadSystem.cs` actually live under `Packages/athena.shared/Runtime/Systems/Crates/`, not directly under `Systems/` as the order's scope fence states; both are unique repo-wide and matched the order's line-level descriptions exactly, so I edited the real files
  - Docs lane (close-out, per 03-technical-plan.md § handoff): CRATE_ASSET_LOADING_FLOW.md and PLAYER_SESSION_CHARACTER_FLOW.md still describe Client/Server/Synchronize semantics and the old Authoritative-prefixed names; ARCHITECTURE_REVIEW.md:162, PLAYER_SESSION_CHARACTER_FLOW.md:40+274, athena.shared/PACKAGE_DOCUMENTATION.md:69, CRATE_ASSET_LOADING_FLOW.md:318 name the renamed symbols directly

skill_calls:
  - none

risks:
  - `dotnet build Impact.sln` (the order's own verification command) cannot pass until the Test lane's dispatch lands, since the two EditMode test files reference symbols this order was specifically instructed to delete/rename; I did not touch those test files per non_goals, and confirmed via isolated per-project builds that every file in this order's own scope compiles clean
  - I renamed the local variable `authoritativeConfiguration` to `sessionConfiguration` in StandaloneGameplayContext.cs (not explicitly named by the rename plan, which only specified the `ServiceProvider.Instance.AuthoritativeConfiguration` -> `SessionConfiguration` member rename) — kept for consistency with the new field name on the same line the plan already required editing, not a new call site
  - GameAssetLoadSystem.ProcessNewLoadRequests's old else-branch (added `GameAssetLoadFinished` directly, skipping in-progress) became unreachable once local-load went unconditional, so I removed the if/else split entirely
  - The plan's wording ("keep its body, drop the condition") didn't explicitly address that now-dead else branch — removing it was the only reading consistent with "unconditional," flagging the interpretation call

## Orchestrator brief
- All target-shape edits (GameAssetLoadFlags, BaseGameCrate.LoadFlags, both singletons, GameAssetLoadSystem's remote/local-load cascade) and the full D-4 rename are complete in every non-test file this order's scope covers.
- `dotnet build Impact.sln` fails with 14 errors, 100% confined to the two EditMode test files the plan assigns to the Test lane next — not a defect in this dispatch's own edits (confirmed via isolated `Athena.Shared.Runtime.csproj`/`Assembly-CSharp.csproj` builds, both 0 errors).
- Two `git mv` commands outstanding for the D-4 rename's filename/type mismatch (§ handoff).
- Blocks dispatch: no — Test lane can proceed immediately: 03-technical-plan.md § Lanes item 3 already names the exact lines to fix.
