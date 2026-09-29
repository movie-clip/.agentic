REPORT 2026-09-24-remove-multiplayer/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE (read-only design pass)

contract_notes:
  - GameAssetLoadFlags (Athena.Shared.Components) shrinks to `{ None = 0, SetActiveScene = 1 << 3 }`; Client/Server/Synchronize members deleted, remaining bit value unchanged, see § Target shapes
  - BaseGameCrate.LoadFlags (Athena.Shared.Authoring) shrinks to `{ DoNotLoad = 0, Development = 1 << 2, _ = 1 << 3 }`; Client/Server deleted, Development/`_` untouched (out of this request's scope), see § Target shapes
  - GameAssetLoadSingleton.RequestAsset drops RemoteLoadCount + RemoteSectionLoadCount; the singleton's own CriticalSyncVersion/NonCriticalSyncVersion fields are deleted outright (RequestVersion/LoadVersion/LocalLoadCount/LocalSectionLoadCount are untouched), see § Target shapes
  - GameCrateSingleton drops CriticalSyncVersion/NonCriticalSyncVersion properties (RegistrationVersion/StructuralVersion untouched), see § Target shapes
  - WorldType (Athena.Shared.Runtime, GameWorldStateRunner.cs) shrinks to `{ Local }`; Local's underlying value stays 0 so the one serialized `worldType: 0` in gameWorldStateRunner.prefab needs no migration, see § Target shapes
  - GameAssetLoadSystem.ShouldLoadRemotely/CanLoadLocally/GetWorldLoadFlags are all deleted; the CanLoadLocally-guarded local-load/unload bodies (register path ~L272, release path ~L440) become unconditional rather than removed, see § Target shapes and § Known weak spot this touches
  - Exactly one serialized asset needs a value migration for this whole run: Assets/Content/Core/gameWorldStateRunner.prefab `loadFlags: 3` -> `loadFlags: 0`. No GameCrate/LevelCrate/CharacterCrate/CharacterSkinCrate asset in the project carries a non-default LoadFlags value, see § Serialized asset inventory
  - Rename plan (D-4) settles four new names with call sites enumerated in § Rename plan: GameAuthoritativeConfiguration -> GameSessionConfiguration, ServiceProvider.AuthoritativeConfiguration -> SessionConfiguration, GameWorldStateRunner.ConfigureLocalAuthoritativeWorld -> ConfigureLocalWorldSession, AuthoritativeCharacterSkinLoadSystem -> CharacterSkinLoadSystem

pack_corrections:
  - architecture.md requires calling `mattpocock-skills:codebase-design` every DESIGN pass (§ Design pass checklist, § Technique skills); the Skill tool returned "Unknown skill: mattpocock-skills:codebase-design" in this session, so the call cannot be made as written.
  - project.md § Skills and Impact/CLAUDE.md both state `.claude/settings.json` enables `mattpocock-skills` for every dispatched lane; that premise did not hold in this session — replace with "confirm before relying on it; may be session-specific rather than a repo-wide drift."

handoff:
  - Lane split (budget-matching backend x2, test x1, see run.md): Backend-A = 02-delivery-brief steps 1+2 (package/manifest removal, WorldType.Client/Server + WorldFlags.GameClient/GameServer dead-branch collapse) — unchanged from the brief, no design input needed
  - Backend-B = step 4 (this order's target shapes) + the D-4 rename, dispatched together because both touch GameWorldStateRunner.cs and ServiceProvider.cs; full file list and exact edits in § Lanes and § Rename plan
  - Test lane = step 5, one dispatch: delete GameAssetLoadSystem_TracksAndReleasesRemoteOnlyRequests (CrateSystemEditModeTests.cs ~L210-263) entirely; fix up the renamed-symbol test names/call sites (same file, ~L522,545,563,591) in the same pass since it's the same file, see § Lanes
  - Docs lane (close-out): CRATE_ASSET_LOADING_FLOW.md, PLAYER_SESSION_CHARACTER_FLOW.md, CHARACTER_ANIMATION_SETUP.md, TEST_PLAN.md per recon's line list, plus the rename's doc mentions in ARCHITECTURE_REVIEW.md:162, PLAYER_SESSION_CHARACTER_FLOW.md:40+274, athena.shared/PACKAGE_DOCUMENTATION.md:69, CRATE_ASSET_LOADING_FLOW.md:318
  - D-3 package removal is safe to execute as originally planned in Backend-A: no local package.json, asmdef, or code anywhere in Assets/Packages references com.unity.multiplayer.center; re-verified independently of recon, see § Package removal (D-3)
  - Sequence correction: 02-delivery-brief's 6 steps stand, with one addition — the D-4 rename (not in the original 6 steps, ruled after the brief was written) folds into step 4/Backend-B and step 5/test rather than becoming a 7th step, see § Sequence

skill_calls:
  - mattpocock-skills:codebase-design — not called: the Skill tool call errored "Unknown skill: mattpocock-skills:codebase-design" (not present in this session's roster). See pack_corrections; this is a tooling gap, not a discretionary skip.

risks:
  - The same skill-availability gap will hit `tech-lead` INTEGRATION on this same run (architecture.md's Integration review checks also require the call before writing a reuse/consistency judgment) — worth checking before that gate runs, or its report will carry the identical gap
  - I left BaseGameCrate.LoadFlags.Development and the reserved `_ = 1 << 3` member untouched: both are already dead (Development is declared but never converted or read anywhere in the repo) but neither is multiplayer-related, and D-1/D-2 only ruled on Client/Server — removing them would be reopening scope no decision covers
  - I did not shrink WorldType down to removing the field/enum entirely (just Local); the brief already scoped step 2 as "delete Client/Server, prefab worldType 0 stays valid" with no design flag, and going further (deleting the enum/field outright) touches the prefab's serialized shape in a way no decision asked for — flagging as available future cleanup, not doing it here
  - GameAssetLoadSystem's CanLoadLocally/ShouldLoadRemotely removal is the one edit in this plan that touches the load-execution code path itself rather than just deleting flags — this is exactly the area architecture.md's Known weak spots section names as most likely to regress from an in-isolation fix; Backend-B's dispatch should get § Target shapes verbatim rather than re-deriving the cascade
  - UpdateVersions' signature shrinks from 4 bools to 2 (incrementCriticalSyncVersion/incrementNonCriticalSyncVersion params removed) — I named this in § Target shapes but left the exact refactor (inline vs. keep a 2-param helper) to Backend-B's judgment since it's mechanical, not a shape decision
  - Both GameCrate.asset instances in the project (Gameplay.asset, Viking_Possessed.asset) have empty entry arrays today, so ConvertToLoadFlags/CheckForInvalidLoadFlags removal in BaseGameCrate.cs is verified zero-behavior-change against every live asset, not just argued from the code

## Orchestrator brief
- Decisions taken: GameAssetLoadFlags -> {None, SetActiveScene}; BaseGameCrate.LoadFlags -> {DoNotLoad, Development, _}; both singletons drop their sync/remote fields; WorldType -> {Local} (zero-migration); rename map for D-4 fixed to 4 names.
- Only one serialized asset needs migration: gameWorldStateRunner.prefab loadFlags 3->0 (see § Serialized asset inventory). D-3 package removal re-confirmed clean.
- Lane split (matches run.md budget): Backend-A = brief steps 1+2 (no design). Backend-B = brief step 4 + D-4 rename, one dispatch (shared files). Test = brief step 5, one dispatch. Docs = close-out.
- Sections below: Target shapes (the contract) · Serialized asset inventory · Migration plan · Rename plan (D-4) · Package removal (D-3) · Lanes (dispatch-ready, with verification commands) · Sequence · Reuse.
- Blocks dispatch: no. Gap: `mattpocock-skills:codebase-design` is unreachable in this session (see pack_corrections) — likely to recur at the INTEGRATION gate on this same run.

## Target shapes

### `GameAssetLoadFlags` — `Impact/Packages/athena.shared/Runtime/Components/GameAssetLoadFlags.cs`
Before: `None=0, Client=1<<0, Server=1<<1, Synchronize=1<<2, SetActiveScene=1<<3`.
After:
```csharp
[Flags]
public enum GameAssetLoadFlags
{
    None = 0,
    SetActiveScene = 1 << 3,
}
```
Do not renumber `SetActiveScene` — its bit value must stay `8` because it is the one member every remaining caller (LevelCrate.cs:51) still sets, and it must keep decoding the same way against any not-yet-migrated data.

Why Synchronize goes too, even though D-1's wording named only Client/Server: `Synchronize` has exactly one consumer, `GameAssetLoadSystem.ShouldLoadRemotely` (L588-597), which is itself only reachable when `state.WorldUnmanaged.Flags == WorldFlags.GameServer` — a world that brief step 2 already deletes the last code path capable of creating (Player systems' `WorldFlags.GameServer` branches). A flag with no reachable consumer left is the same vestige as Client/Server, and this order's own `definition_of_done` names Synchronize explicitly alongside WorldType.Client/Server as "vestige removal ... what stays, what goes" — so it is inside this order's authority, not a reopening of D-1.

Cascading edits this forces (still `athena.shared`, still this order's authority since they all read the enum whose shape changed):
- `GameAssetLoadSystem.cs`: delete `ShouldLoadRemotely` (L588-597), `CanLoadLocally` (L599-602), `GetWorldLoadFlags` (L604-612) entirely.
  - Register path (~L236-270): delete the whole `if (ShouldLoadRemotely(...))` block, including the `RemoteSectionLoadCount` manipulation and the `incrementCriticalSyncVersion`/`incrementNonCriticalSyncVersion` sets inside it.
  - Register path (~L272-...): delete the `if (CanLoadLocally(...))` **condition** but keep its **body** — every request always executes the local-load branch now, because in a single `WorldFlags.Game` world every request always could load locally already (`GetWorldLoadFlags(Game)` was `Client|Server`, i.e. always non-zero against any real asset's flags).
  - Release path mirrors this exactly at ~L405-438 (delete, remote-guarded decrement block) and ~L440-506 (drop the `CanLoadLocally` condition, keep the body).
  - `UpdateVersions` (~L615-640): drop the `incrementCriticalSyncVersion`/`incrementNonCriticalSyncVersion` parameters and their bodies (L630-637); update its two call sites (~L349, ~L388) and the two `ReleaseRequests` overloads that thread those bools through (~L366-397) to match the shrunk signature.
  - Delete the already-fully-commented `CheckIfEntitySceneHasPrespawnGhosts` block (L642-658) — it references NetCode in a comment and has zero live code.
- `BaseGameCrate.cs`: delete `LoadFlags.Client`/`LoadFlags.Server` members (see next shape); delete `ConvertToLoadFlags` (L147-160) and `CheckForInvalidLoadFlags` (L179-186) entirely — both exist only to translate/guard the members being removed, and `CheckForInvalidLoadFlags`'s guard is against `GameAssetLoadFlags.Synchronize`, which no longer exists. Remove its 5 call sites in `CreateObjectSceneLoad`/`CreateEntitySceneLoad` (x2)/`CreateEntityPrefabLoad`/`CreateUnityObjectLoad`.
- `GameCrate.cs` (L73,85,97,109): replace each `ConvertToLoadFlags(entry.Flags)` argument with the literal `GameAssetLoadFlags.None`. Verified safe: both live `GameCrate` assets have empty entry arrays today (see § Serialized asset inventory), so this is a no-op against real data, not just a code-reading argument.
- `LevelCrate.cs:51`: `GameAssetLoadFlags.Client | GameAssetLoadFlags.SetActiveScene` -> `GameAssetLoadFlags.SetActiveScene`. `LevelCrate.cs:58`: `GameAssetLoadFlags.Client | GameAssetLoadFlags.Server` -> `GameAssetLoadFlags.None`.
- `CharacterCrate.cs:99`: `GameAssetLoadFlags.Client | GameAssetLoadFlags.Server` -> `GameAssetLoadFlags.None`.
- `CharacterSkinCrate.cs:39`: `GameAssetLoadFlags.Client` -> `GameAssetLoadFlags.None`.
- `GameWorldStateRunner.cs:28`: default field value `GameAssetLoadFlags.Client | GameAssetLoadFlags.Server` -> `GameAssetLoadFlags.None`. (Line 107's `LoadGameplayBootstrap` is already removed whole by brief step 2 — no edit needed here from this order.)

### `BaseGameCrate.LoadFlags` — `Impact/Packages/athena.shared/Runtime/Components/Authoring/Crates/BaseGameCrate.cs`
Before: `DoNotLoad=0, Client=1<<0, Server=1<<1, Development=1<<2, _=1<<3`.
After:
```csharp
[Flags]
public enum LoadFlags
{
    DoNotLoad = 0,
    Development = 1 << 2,
    _ = 1 << 3,
}
```
`ShouldInclude` (L161-168) is untouched — it only ever compares against `DoNotLoad`. `Development` and `_` are pre-existing dead code unrelated to multiplayer (never converted, never read anywhere in the repo); leaving them is a deliberate non-decision, not an oversight — see risks.

### `GameAssetLoadSingleton` — `Impact/Packages/athena.shared/Runtime/Components/GameAssetLoadSingleton.cs`
Delete from `RequestAsset`: `RemoteLoadCount` (L17), `RemoteSectionLoadCount` (L18). Delete from the outer struct: `CriticalSyncVersion` (L37), `NonCriticalSyncVersion` (L38). Everything else (`RequestCount`, `IsCritical`, `LocalLoadCount`, `LocalSectionLoadCount`, `SceneEntity`, `ArchiveObjectSceneHandle`, `ObjectScene`, `ReferenceId`, the three `Is*` properties, `RequestVersion`, `LoadVersion`, `RequestedAssetsMap`) is local-load bookkeeping, untouched.

### `GameCrateSingleton` — `Impact/Packages/athena.shared/Runtime/Components/GameCrateSingleton.cs`
Delete `CriticalSyncVersion`/`NonCriticalSyncVersion` (L15-16). `RegistrationVersion`/`StructuralVersion`, both `NativeList<GameCrateLoad>` fields and `RegisteredCratesMap` are untouched. In `GameCrateLoadSystem.cs` `UpdateActiveCrates` (L162-189): delete the two `unchecked { singleton.CriticalSyncVersion++; }` / `NonCriticalSyncVersion++` blocks (L174-177, L184-187) but keep the `if (criticalChanged) { Clear(); AddRange(...); }` / `if (nonCriticalChanged) {...}` structure around them — that part is real active-crate-list bookkeeping with no multiplayer content.

### `WorldType` — `Impact/Packages/athena.shared/Runtime/GameWorldStateRunner.cs`
Before: `enum WorldType { Local, Client, Server }`. After: `enum WorldType { Local }`. `Local`'s underlying value stays `0` (unchanged — it was already first), so the prefab's serialized `worldType: 0` needs no migration. This is brief step 2's item, already scoped as no-design; restated here only because this order's `definition_of_done` asked me to confirm it, and to confirm it does not interact with the step-4 shapes above (it doesn't — `Execute()` in the same file already has no branch for `Client`/`Server`, so removing the enum members changes zero runtime behavior).

## Serialized asset inventory
Every crate/prefab asset in `Impact/Assets` and `Impact/Packages` carrying a serialized `Flags`, `loadFlags`, or `worldType` value that step 4 touches (grep for the literal YAML keys `Flags:`, `loadFlags:`, `worldType:` across `*.asset`/`*.prefab`/`*.unity`, plus a guid-targeted check of every `BaseGameCrate` subclass asset):

| Asset | Type | Serialized value | Action |
|---|---|---|---|
| `Assets/Content/Core/gameWorldStateRunner.prefab` (L47-62) | `GameWorldStateRunner` | `worldType: 0`, `loadFlags: 3` | `worldType` unchanged (0 stays `Local`); `loadFlags` migrates `3 -> 0`, see § Migration plan |
| `Assets/Content/Gameplay/Core/Crates/Gameplay.asset` | `GameCrate` | `gameObjectScenes/entityScenes/entityPrefabs/unityObjects: []` (all empty) | none — no entry ever set a `Flags` value |
| `Assets/Content/Characters/Viking/Gameplay/Viking_Possessed.asset` | `GameCrate` | same, all entry arrays empty | none |
| `Assets/Content/Characters/Samurai/Gameplay/SamuraiCrate.asset` | `CharacterCrate` | no serialized `LoadFlags` field on this type (hardcodes `GameAssetLoadFlags` in code, see § Target shapes) | none |
| `Assets/Content/Characters/Viking/Gameplay/VikingCrate.asset` | `CharacterCrate` | same | none |
| `Assets/Content/Characters/Viking/Gameplay/Skins/Viking_BaseSkin.asset`, `Viking_WarriorSkin.asset` | `CharacterSkinCrate` | no serialized `LoadFlags` field on this type | none |
| `Assets/Content/Levels/Tests/Samurai/Samurai_Sandbox.asset`, `Viking/Viking_Sandbox.asset`, `Village/Village_Crate.asset` | `LevelCrate` | no serialized `LoadFlags` field on this type | none |

This is exhaustive: these 9 assets are every asset in the project whose script GUID matches `GameCrate`/`LevelCrate`/`CharacterCrate`/`CharacterSkinCrate` (`grep -rl <script-guid> --include=*.asset Assets Packages`), and a separate blind grep for the YAML keys `Flags:`/`loadFlags:` across every `*.asset`/`*.prefab`/`*.unity` in `Assets`/`Packages` returns only the prefab row above and the two boilerplate `m_ObjectHideFlags`/`m_EditorHideFlags` lines Unity writes into every asset (not this enum).

## Migration plan
One value, one asset: `Assets/Content/Core/gameWorldStateRunner.prefab` line 62, `loadFlags: 3` -> `loadFlags: 0`. Hand-edit, not an editor script — the inventory above is the whole migration surface for this run, and a one-time editor script would cost more to write and review than the single-line diff it replaces. Backend-B makes this edit alongside the `GameWorldStateRunner.cs` default-value change (L28) so the C# default and the one serialized override agree.

No other asset needs a value change: every `GameCrate` instance has empty entry arrays (nothing to migrate) and every `LevelCrate`/`CharacterCrate`/`CharacterSkinCrate` hardcodes its `GameAssetLoadFlags` in code, which is edited directly under § Target shapes, not migrated as data.

## Rename plan (D-4)
Backend-B renames the type/member in place with `Edit` (not a new file) and leaves each filename as-is — no lane has a delete/rename tool, so the filename-vs-type mismatch this creates is a `should_fix` handoff, not a blocker: `git mv Packages/athena.shared/Runtime/Simulation/GameAuthoritativeConfiguration.cs Packages/athena.shared/Runtime/Simulation/GameSessionConfiguration.cs` and `git mv Packages/athena.shared/Runtime/Systems/AuthoritativeCharacterSkinLoadSystem.cs Packages/athena.shared/Runtime/Systems/CharacterSkinLoadSystem.cs` for the human to run after review.

1. **`GameAuthoritativeConfiguration` -> `GameSessionConfiguration`** (class, `Athena.Shared.Runtime`, holds only `InitialSessionSetup`).
   - `Simulation/GameAuthoritativeConfiguration.cs:3` (class decl).
   - `ServiceProvider.cs:30` (field type), `:45` (`new GameAuthoritativeConfiguration()`).
   - `GameWorldStateRunner.cs:23` (field type `private GameAuthoritativeConfiguration authoritativeConfiguration;` — also rename this local field to `sessionConfiguration`, and its use at L38/L81).
2. **`ServiceProvider.AuthoritativeConfiguration` -> `SessionConfiguration`** (public field on `ServiceProvider`).
   - `ServiceProvider.cs:30` (decl), `:45`, `:71` (assignments).
   - `GameWorldStateRunner.cs:38`: `ServiceProvider.Instance.AuthoritativeConfiguration` -> `ServiceProvider.Instance.SessionConfiguration`.
   - `Assets/Scripts/Runtime/StandaloneGameplayContext.cs:53`: same rename.
3. **`ConfigureLocalAuthoritativeWorld` -> `ConfigureLocalWorldSession`** (private method, `GameWorldStateRunner.cs`).
   - Decl `:79`, call site `:53`, and the `Debug.Log` string at `:81` that names the method (`"[GameWorldStateRunner] ConfigureLocalAuthoritativeWorld. ..."` -> `"[GameWorldStateRunner] ConfigureLocalWorldSession. ..."`).
   - Doc mention: `Packages/athena.shared/PLAYER_SESSION_CHARACTER_FLOW.md:40` (docs lane).
4. **`AuthoritativeCharacterSkinLoadSystem` -> `CharacterSkinLoadSystem`** (`partial struct : ISystem`, static-helper-only, `Athena.Shared.Systems`). No name collision: no `CharacterSkinLoadSystem`/`SkinLoadSystem` type exists anywhere else in the repo.
   - Decl `Systems/AuthoritativeCharacterSkinLoadSystem.cs:8`; 3 `Debug.Log`/`LogWarning` strings at `:19,28,81` that repeat the type name.
   - Call sites: `Assets/Scripts/Runtime/Cheats/Commands/SkinCheatCommand.cs:65`; `Packages/athena.shared/Runtime/Systems/Debug/GameCrateDebugSystem.cs:151`.
   - Test lane: `Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs` — test method names `AuthoritativeCharacterSkinLoadSystem_StartSwitchSkinProcess_AddsPendingRequestForNonDefaultSkin` (`:522`) and `..._RemovesPendingRequestForDefaultSkin` (`:563`), plus the call sites at `:545,591`. Rename the test methods' `AuthoritativeCharacterSkinLoadSystem` prefix to `CharacterSkinLoadSystem` for consistency with the type; this is mechanical, not new coverage, so it stays inside the test lane's existing dispatch rather than needing a separate order.
   - Doc mentions (docs lane): `ARCHITECTURE_REVIEW.md:162`, `PLAYER_SESSION_CHARACTER_FLOW.md:274`, `athena.shared/PACKAGE_DOCUMENTATION.md:69`, `CRATE_ASSET_LOADING_FLOW.md:318`.

No assembly-boundary risk: every call site above is inside `athena.shared` itself, or in `Impact/Assets/Scripts/**` (the top-level app layer, which may reference any package), or in the EditMode test assembly. Nothing in `athena.gameplay` or `athena.charactercontroller` references any of these four symbols (checked directly, zero hits) — this rename crosses no package boundary the dependency graph in `project.md` § Hard guardrails restricts.

## Package removal (D-3)
Re-confirmed independently of `01-recon.md`: `grep -rn "multiplayer" Packages/manifest.json` returns only line 12 (`com.unity.multiplayer.center: 1.0.1`); no `Packages/*/package.json`, `.asmdef`, or `Assets` file references `multiplayer.center` in any form. Safe for Backend-A to remove `Packages/manifest.json:12` and `ProjectSettings/MultiplayerManager.asset`, letting Unity regenerate `packages-lock.json` — matches `02-delivery-brief.md` step 1 exactly, no correction needed.

## Lanes
Ordered; each ends in the mechanical gate named. `dotnet build Impact.sln` and `Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly` both run from `Impact/`.

1. **Backend-A** (no design input — `02-delivery-brief.md` step 1+2, unchanged by this order): remove `com.unity.multiplayer.center` from `manifest.json` + `ProjectSettings/MultiplayerManager.asset`; delete `WorldType.Client`/`.Server` and unused `LoadGameplayBootstrap` in `GameWorldStateRunner.cs`; collapse the `WorldFlags.GameClient`/`GameServer` branches in `PlayerSystem.cs:73-74`, `PlayerCharacterSystem.cs:73`, `PlayerCommandSystem.cs:52`, `HybridGameObjectSystemBase.cs:62-65`; drop the stale NetCode comment in `ThirdPersonPlayerSystems.cs:121-122`. Verify: `dotnet build Impact.sln`.
2. **Backend-B** (this order's shapes, § Target shapes + § Rename plan, one dispatch since both touch `GameWorldStateRunner.cs`/`ServiceProvider.cs`): every edit listed under § Target shapes and § Rename plan except the WorldType item (already Backend-A). Verify: `dotnet build Impact.sln`, then `Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly` (this touches the crate/asset-load pipeline directly — architecture.md § What integration must run says EditMode is the floor here; PlayMode is integration's call, not this lane's).
3. **Test** (`02-delivery-brief.md` step 5 + the rename's test-file edits, one dispatch, same file for both): delete `GameAssetLoadSystem_TracksAndReleasesRemoteOnlyRequests` (`CrateSystemEditModeTests.cs` ~L210-263) whole; replace `GameAssetLoadFlags.Client`/`.Server` with `GameAssetLoadFlags.None` at `CrateSystemEditModeTests.cs:167` and `LevelCrateEditModeTests.cs:156,193` (arbitrary-flag test setup, not testing removed semantics); replace `GameAssetLoadFlags.Client`/`.Server` with `GameAssetLoadFlags.SetActiveScene` at `CrateSystemEditModeTests.cs:308,313,321,327` (these assert flag round-trip, so need a flag that still exists); drop the `RemoteLoadCount = 1,` initializer line at `CrateSystemEditModeTests.cs:341`; rename the two `AuthoritativeCharacterSkinLoadSystem_*` test methods and their call sites at `:522,545,563,591` per § Rename plan item 4. Verify: `dotnet build Impact.sln`, then `Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly`.
4. **Integration** (tech-lead, engineering gate): full checklist in `architecture.md` § Integration review checks against Backend-A, Backend-B and Test's reports together — contract alignment matters here because Backend-B and Test both touch `GameAssetLoadFlags` call sites independently.
5. **Docs** (close-out): the file list in `handoff`, all mechanical once § Target shapes and § Rename plan are settled.

## Sequence
The brief's 6 steps stand; nothing in them was wrong. Two corrections given the settled shapes and the human's rulings since the brief was written:
- **D-4's rename was not in the brief's 6 steps** (it was still an open decision when the brief was written). It does not need a 7th step: it shares every file Backend-B and Test already touch for step 4/5, so it folds into those two dispatches rather than becoming a separate pass. Sequencing it separately would just mean two dispatches editing the same lines in `GameWorldStateRunner.cs`/`CrateSystemEditModeTests.cs` back to back for no benefit.
- **Step 3 (this design order) is done**; steps 1-2 (Backend-A) were never blocked on it and can dispatch immediately, same as the brief said. Steps 4-5 (Backend-B, Test) were blocked on this order and are now unblocked.
- Step 6 (docs) gains the rename's doc lines (§ Rename plan) on top of the brief's original list; otherwise unchanged.

## Reuse
No new pattern is introduced anywhere in this plan — every edit either deletes members from an existing enum/struct, deletes a now-unreachable private method, or renames a symbol in place. The one place an engineer could be tempted to invent something new is the `CanLoadLocally` removal: § Target shapes is explicit that the guarded body becomes unconditional in place, not rewritten or restructured, so the existing per-`GenerationType` load/unload switch (`SceneSystem.LoadSceneAsync`, `objectSceneLoader.RequestScene`, `RuntimeContentManager.LoadObjectAsync`, etc.) is reused verbatim.
