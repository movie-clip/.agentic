REPORT 2026-09-24-remove-multiplayer/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE

contract_notes:
  - GameAssetLoadFlags (Client/Server/Synchronize) is read by athena.shared crate authoring, GameAssetLoadSystem, GameWorldStateRunner and tests; any change to its shape is a cross-file contract, see § Inventory (c)
  - GameAssetLoadSingleton.RequestedAsset.RemoteLoadCount/RemoteSectionLoadCount and CriticalSyncVersion/NonCriticalSyncVersion (GameAssetLoadSingleton.cs:17,18,37,38; GameCrateSingleton.cs:15,16) are singleton fields; only athena.shared and CrateSystemEditModeTests read them
  - BaseGameCrate.LoadFlags enum (Client/Server) is serialized into crate assets; removing values needs a check of Assets with serialized Flags, see § Risks

pack_corrections:
  - none

handoff:
  - The repo contains NO netcode: no com.unity.netcode, no Unity.Transport, no ghosts, RPCs, GhostFields, connection code, or Server/Client world creation. The "multiplayer" surface is vestigial Client/Server flag plumbing, see § Inventory
  - Backend lane: edit athena.shared GameAssetLoadSystem.cs (ShouldLoadRemotely 588-597, GetWorldLoadFlags 604-612, remote counters 236-268 and 405-438), PlayerSystem.cs:73, PlayerCharacterSystem.cs:73, PlayerCommandSystem.cs:52, HybridGameObjectSystemBase.cs:62
  - Backend lane: edit GameAssetLoadFlags.cs, GameAssetLoad*.cs, BaseGameCrate.cs, LevelCrate.cs, CharacterCrate.cs, CharacterSkinCrate.cs, GameCrate.cs, GameWorldStateRunner.cs (WorldType enum + loadFlags field) and the gameWorldStateRunner.prefab serialized fields
  - Backend lane: manifest.json line 12 com.unity.multiplayer.center and packages-lock.json:246 and ProjectSettings/MultiplayerManager.asset are the only package-level multiplayer items (editor tooling, roles disabled)
  - Test lane: CrateSystemEditModeTests.cs (lines 167,214-253,308-341) and LevelCrateEditModeTests.cs (156,193) use Server/Client/Synchronize flags; new World(...WorldFlags.GameServer) at CrateSystemEditModeTests.cs:214
  - Docs lane: CRATE_ASSET_LOADING_FLOW.md (235,262-273,388), PLAYER_SESSION_CHARACTER_FLOW.md:322, CHARACTER_ANIMATION_SETUP.md:425-426, Assets/Tests/Crates/TEST_PLAN.md:34, Impact/CLAUDE.md:102 (generic plugin blurb, not game multiplayer)
  - MainBootstrap flow itself has no multiplayer branch; it needs no removal edit, see § How MainBootstrap works
  - Design trigger: yes for GameAssetLoadFlags, BaseGameCrate.LoadFlags and the GameAssetLoadSingleton / GameCrateSingleton sync fields (shared by athena.shared authoring, systems, tests, serialized crates)

skill_calls:
  - none

risks:
  - Serialized assets: I did not enumerate every crate .asset with a serialized BaseGameCrate Flags value or every scene/prefab holding GameAssetLoad flags; only gameWorldStateRunner.prefab (worldType 0 = Local, loadFlags 3 = Client|Server, lines 47-62) was checked
  - I could not tell whether Server/Client flags are intended to remain as a client-only / server-only content-filtering concept for single-player (e.g. Server-only prefabs); that is a decision, not a fact I could establish
  - Did not open the Application World's scene (StandaloneGameplay.unity) contents beyond locating StandaloneGameplayContext at line 163; the gameplayBootstrapRunner reference target was not resolved
  - Grep of docs used a glob that partly failed; docs list is from a second targeted grep and may miss lines using words like "peer"/"lobby"/"network" (a separate check for netcode|multiplayer over Assets and Packages was clean)
  - Vendored com.unity.entities@* and com.projectdawn.navigation were excluded from the netcode grep except manifests and asmdefs; no netcode/transport asmdef references were found in non-vendored code
  - MainBootstrap.unity GUID script identities for lines 151/163/330 were only partly resolved: guid ef98... is MainGameObjectCamera (athena.charactercontroller); a794... and 76c3... not resolved (likely AudioListener/camera/URP component)

## Orchestrator brief
- Premise contradicted: there is no netcode in this repo. No com.unity.netcode/transport in manifest.json, no asmdef refs, no ghosts/RPCs/GhostField/WorldSystemFilter client-server flags, no listen/connect code.
- Only package-level item: com.unity.multiplayer.center 1.0.1 (manifest.json:12, lock:246) plus ProjectSettings/MultiplayerManager.asset (roles disabled).
- Real surface is vestigial: WorldFlags.GameClient/GameServer branches and GameAssetLoadFlags Client/Server/Synchronize in athena.shared crate loading (all SHARED, need edit not deletion).
- MainBootstrap brings up exactly one "Application World" (WorldFlags.Game) then loads StandaloneGameplay additively, which creates one Local world (WorldFlags.Game) via GameWorldStateRunner. Single world path already.
- Design trigger: GameAssetLoadFlags, BaseGameCrate.LoadFlags, RemoteLoadCount/SyncVersion singleton fields are shared shapes.
- Section "How MainBootstrap works": entry points, worlds, filtering, scenes, flow with file:line.
- Section "Inventory": items a-g, each tagged ONLY vs SHARED with paths.
- Section "Blast radius": by lane backend/test/docs, and design trigger.
- Section "Sources of truth": which docs govern and whether current.
- Blocks dispatch: no. Ambiguity for the human: whether Client/Server load flags are removed or kept as content filters (see risks).

## How MainBootstrap works
Files: scene `Impact/Assets/Scenes/MainBootstrap.unity` (only entry in EditorBuildSettings.asset:9), script `Impact/Assets/Scripts/Runtime/MainBootstrap.cs`.

Scene contents (MainBootstrap.unity): Main Camera (line 136; MainGameObjectCamera script ef98a7c..., plus a second component), EventSystem (284, InputSystemUIInputModule), a GameObject "Bootstap" (362) carrying MainBootstrap (script guid 29a6aae4..., line 392) with serialized `gameSessionSetup` (Level crate guid 02ea673f..., Character/Skin/Player crates, lines 395-401) and `standaloneGameplayBootstrap` scene ref (545).

Script flow (MainBootstrap.cs):
- Static registration at SubsystemRegistration: `ResetStatistics` (105-110) resets `CurrentRunnableContext`/`WaitForGameplayAssetLoads`; `RegisterMainEntrySceneWithWorldBootstrap` (112-116) adds "Assets/Scenes/MainBootstrap.unity" to `WorldBootstrap.ApplicationEntryScenes`.
- `Start` (34-57): validates session/level, sets `StandaloneGameplayContext.InitialWorldSetup = new GameWorldSetup { Session = clone }` (49-52), sets `CurrentRunnableContext = Gameplay` (53), then `SetupServices` -> `ServiceProvider.Instance.InitServices()` (59-63) and `Init` (65-74).
- `Init`: `WorldBootstrap.CreateApplicationWorldIfNeeded()` (68), grabs `ServiceProvider.Instance.archiveObjectSceneService` (70), starts coroutine `LoadIntoGame` (73).
- `LoadIntoGame` (76-98): waits while `WaitForGameplayAssetLoads`, calls `standaloneGameplayBootstrap.LoadAsync` additive, `autoIntegrate=true`, `LocalPhysicsMode.None` (85-90), waits for `isLoaded`, `SceneManager.SetActiveScene`.
- `Update` pumps `objectSceneService.Update()` (100-103). `OnDestroy` disposes ServiceProvider and `WorldBootstrap.DisposeApplicationWorld()` (118-126).

Worlds (Impact/Packages/athena.shared/Runtime/Worlds/WorldBootstrap.cs):
- `WorldBootstrap : ICustomBootstrap` (13). `Initialize` (41-50) creates the "Application World" (const line 15) and returns true, so Unity's default world is replaced by it.
- `CreateApplicationWorld` (76-95): `new World(name, WorldFlags.Game)`, sets DefaultGameObjectInjectionWorld, gets systems with `WorldSystemFilterFlags.Default` (81), keeps only systems from Unity.Entities, Unity.Entities.Hybrid, Unity.Scenes assemblies (18-23, 83), adds TransformSystemGroup (27-30), removes systems under FixedStepSimulationSystemGroup, VariableRateSimulationSystemGroup, PresentationSystemGroup (32-37, 88-89); then `UpdateInGroupConditionalUtility.UpdateConditionalSystemLocations` (93; athena.core/Runtime/Utils/UpdateInGroupConditional.cs:16-21 maps Default to LocalSimulation|Presentation).
- `CreateLocalWorld(name)` (52-64): `WorldFlags.Game`, full default systems. Invoked by `GameWorldAdmin.CreateLocalWorld()` (GameWorldAdmin.cs:33-37, name "Local World").
- No client, server, thin-client or netcode-created worlds anywhere. Unused `CreateDefaultWorld` (97-107) is private, also WorldFlags.Game.

Scene load chain after MainBootstrap:
- `StandaloneGameplay.unity` (Impact/Assets/Scenes) contains `StandaloneGameplayContext` (Assets/Scripts/Runtime/StandaloneGameplayContext.cs, scene line 163). Its `Start`/`Init` (13-49) validates `InitialWorldSetup`, pushes a clone into `ServiceProvider.Instance.AuthoritativeConfiguration.InitialSessionSetup` (51-56), and instantiates `gameplayBootstrapRunner` into its scene (47).
- The runner prefab is presumably `Impact/Assets/Content/Core/gameWorldStateRunner.prefab` (GameWorldStateRunner script guid 99c8e22b..., line 44; not verified as the serialized reference). Serialized: `worldType: 0` (Local), `loadType: 0` (EntityScene), `loadFlags: 3` (Client|Server) (lines 47-62).
- `GameWorldStateRunner` (athena.shared/Runtime/GameWorldStateRunner.cs): `Start` (35-42) -> `Execute` (44-77). Only `WorldType.Local` is implemented (49-55: `gameWorldAdmin.CreateLocalWorld()`, `ConfigureLocalAuthoritativeWorld` builds the session via `BuildGameSession`, `ConfigureWorldShared` creates `ObjectSceneLoaderSingleton`). Client/Server enum values (14-17) have no branch; `createdGameWorld` would NRE on them (60).
- Then it creates a request entity with `GameAssetLoad.CreateForEntityScene(..., loadFlags,...)` plus `CriticalGameAssetLoad` (63-76), consumed by `GameAssetLoadSystem` in the Local world (WorldFlags.Game, so both Client and Server flags load locally).

Connection / listen flow: none exists. No sockets, transport, endpoints, or connection systems in Assets/ or non-vendored Packages/.

## Inventory
Legend: ONLY = multiplayer-only (candidate for deletion); SHARED = needs edit, not deletion.

### (a) UPM packages
- `Impact/Packages/manifest.json:12` `com.unity.multiplayer.center` 1.0.1 - ONLY (editor onboarding tool); also `Impact/Packages/packages-lock.json:246` entry (generated; may list dependents, not checked). No package depends on it in local packages (grep of Packages found none).
- No `com.unity.netcode*`, `com.unity.transport`, `com.unity.multiplayer.playmode` etc. in manifest.json.
- Local packages (athena.*, com.ai.shared, com.projectdawn.navigation): none used only for multiplayer.

### (b) asmdef references
- none: no asmdef in non-vendored packages/Assets references Unity.NetCode or Unity.Transport (grep for netcode|transport|multiplayer over Packages, excluding entities, returned only the items below).

### (c) C# systems / components / flags
- `athena.shared/Runtime/Components/GameAssetLoadFlags.cs:6-13` enum Client, Server, Synchronize, SetActiveScene - SHARED (SetActiveScene is not multiplayer). Used in GameAssetLoad.cs (43,55,72-163), GameAssetLoadSystem.cs, GameWorldStateRunner.cs:28,107, crate authoring, tests.
- `athena.shared/Runtime/Systems/Crates/GameAssetLoadSystem.cs`: `ShouldLoadRemotely` 588-597 (true only for WorldFlags.GameServer with Client|Synchronize) - ONLY; `CanLoadLocally` 599-602 and `GetWorldLoadFlags` 604-612 (Game -> Client|Server, GameClient -> Client, GameServer -> Server) - SHARED; remote counter increments 236-268 and decrements 405-438 (RemoteLoadCount, RemoteSectionLoadCount, Critical/NonCritical sync version bumps 206-207, 373-389, 615-640) - ONLY logic inside a SHARED system; commented netcode note at 650 (`// because of NetCode, pre spawned ghosts are in section 0`).
- `athena.shared/Runtime/Components/GameAssetLoadSingleton.cs:17-18` RemoteLoadCount, RemoteSectionLoadCount; `:37-38` CriticalSyncVersion, NonCriticalSyncVersion - fields ONLY, struct SHARED.
- `athena.shared/Runtime/Components/GameCrateSingleton.cs:15-16` Critical/NonCriticalSyncVersion; `Systems/Crates/GameCrateLoadSystem.cs:176,186` increments - ONLY fields inside SHARED types.
- `athena.shared/Runtime/Systems/Player/PlayerSystem.cs:73-74` `isAuthoritative = Flags is Game or GameServer` - SHARED (branch simplifies under single-player).
- `athena.shared/Runtime/Systems/Player/PlayerCharacterSystem.cs:73` `Flags is Game or GameServer` - SHARED.
- `athena.shared/Runtime/Systems/Player/PlayerCommandSystem.cs:52` `Flags is Game or GameClient` - SHARED.
- `athena.shared/Runtime/Systems/Hybrid/HybridGameObjectSystemBase.cs:62-65` disables on WorldFlags.GameServer - SHARED.
- `athena.shared/Runtime/Components/Authoring/Crates/BaseGameCrate.cs:17-21` `LoadFlags` enum (Client, Server, DoNotLoad...), `:147-158` ConvertToLoadFlags, `:161-184` ShouldInclude / CheckForInvalidLoadFlags (throws if Synchronize) - SHARED.
- `athena.shared/Runtime/Components/Authoring/Crates/LevelCrate.cs:51,58` Client|SetActiveScene, Client|Server; `CharacterCrate.cs:99` Client|Server; `CharacterSkinCrate.cs:39` Client; `GameCrate.cs:73-109` ConvertToLoadFlags - SHARED.
- `athena.shared/Runtime/GameWorldStateRunner.cs:12-17` `enum WorldType { Local, Client, Server }` and serialized `worldType` (21), `loadFlags` (28), unused `LoadGameplayBootstrap` (103-110) - SHARED (Client/Server enum values ONLY).
- `athena.shared/Runtime/Simulation/GameAuthoritativeConfiguration.cs` and `ServiceProvider.cs:30,45,71`, `AuthoritativeCharacterSkinLoadSystem.cs`, `GameWorldStateRunner.ConfigureLocalAuthoritativeWorld` - "Authoritative" naming only; SHARED, not netcode-specific (naming may be reworded by the human, not required).
- `athena.charactercontroller/Runtime/ThirdPerson/ThirdPersonPlayerSystems.cs:121-122` comment only ("netcode prediction context") - SHARED, comment only.
- `athena.shared/Runtime/Worlds/GameWorldAdmin.cs` (LocalGameWorld only) - SHARED, single-world already.
- No RPC, ghost, GhostField, GhostOwner, ICommandData, NetworkStream*, `[WorldSystemFilter(ClientSimulation|ServerSimulation)]` occurrences anywhere in non-vendored code.

### (d) Enum values / config fields distinguishing client/server/local
- `WorldType.Client`, `WorldType.Server` (GameWorldStateRunner.cs:15-16) - ONLY values; `WorldType.Local` SHARED.
- `GameAssetLoadFlags.Client`, `.Server`, `.Synchronize` (GameAssetLoadFlags.cs:9-11) - Synchronize ONLY; Client/Server are used today as content-load filters in the single Local world (Client|Server both load).
- `BaseGameCrate.LoadFlags.Client/Server` (BaseGameCrate.cs:20-21) - serialized in crate assets, SHARED.
- `WorldFlags.GameClient / GameServer` branches (files above) - engine enum, code branches ONLY.
- `ProjectSettings/MultiplayerManager.asset:4-6` `m_EnableMultiplayerRoles: 0` - ONLY (editor setting, disabled).
- `RunnableContext` (MainBootstrap.cs:14-19: Application, Gameplay, Validation) - not multiplayer.

### (e) Scenes / prefabs / assets / subscenes
- `Impact/Assets/Content/Core/gameWorldStateRunner.prefab:47-62` worldType 0 Local, loadFlags 3 - SHARED (edit if enum/flag shape changes).
- `Impact/Assets/Scenes/MainBootstrap.unity`, `StandaloneGameplay.unity` - no ghost or netcode components (netcode/ghost grep returned only "Listen" from AudioListener false positives across scenes). SHARED.
- Ghost authoring, GhostAuthoringComponent, NetworkStream in scenes/prefabs/subscenes: none found. Crate assets carrying serialized `Flags` values with Client/Server were not enumerated (see risks).

### (f) Tests touching multiplayer
- `Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs`: 167 (Client flag), 214 (`new World("Crate Server EditMode Test World", WorldFlags.GameServer)`), 228 (Client|Synchronize), 242/253 (RemoteLoadCount asserts), 308-341 (Client/Server flag asserts, RemoteLoadCount = 1) - the server/synchronize test(s) are ONLY; rest SHARED.
- `Impact/Assets/Tests/EditMode/Crates/LevelCrateEditModeTests.cs:156,193` GameAssetLoadFlags.Client - SHARED.
- `Impact/Assets/Tests/Crates/TEST_PLAN.md:34` "server-only and synchronized-server requests" - doc of the above.
- Other tests use `WorldFlags.Game` only (LevelCratePlayModeTestHarness.cs:25, LevelCrateTestContext.cs:16, CrateSystemEditModeTests.cs:21, SessionStartDiagnosticSystemEditModeTests.cs:20, ActiveSceneDiagnosticSystemEditModeTests.cs:24) - SHARED, unaffected.
- `Impact/Assets/Tests/PlayMode/StartupReproPlayModeTests.cs` references MainBootstrap (not multiplayer).

### (g) Docs
- `Impact/Packages/athena.shared/CRATE_ASSET_LOADING_FLOW.md` lines 212,235,262-273 (WorldFlags -> load flags, remote sync only on GameServer), 388 - edit.
- `Impact/Packages/athena.shared/PLAYER_SESSION_CHARACTER_FLOW.md:322` ("multiplayer ownership logic later") - edit/remove line.
- `Impact/CHARACTER_ANIMATION_SETUP.md:425-426` "Does this work in multiplayer?" Q/A - edit/remove.
- `Impact/Assets/Tests/Crates/TEST_PLAN.md:34` - edit.
- `Impact/CLAUDE.md:102` lists "multiplayer" among Unity agent-plugin skill areas - generic, not game multiplayer; no edit needed.
- `Impact/ARCHITECTURE_REVIEW.md:76,162`, `athena.shared/PACKAGE_DOCUMENTATION.md:69` mention "authoritative" only (not netcode). No mention of netcode/multiplayer in AGENTS.md or PACKAGE_ARCHITECTURE.md found in grep.
- `athena.core/PACKAGE_DOCUMENTATION.md` is locally modified (git status) - no multiplayer text found by grep.

## Blast radius
- Backend lane (Impact/Packages/athena.shared, Impact/Assets/Scripts, prefab): GameAssetLoadSystem.cs, GameAssetLoadFlags.cs, GameAssetLoad.cs, GameAssetLoadSingleton.cs, GameCrateSingleton.cs, GameCrateLoadSystem.cs, BaseGameCrate.cs, LevelCrate.cs, CharacterCrate.cs, CharacterSkinCrate.cs, GameCrate.cs, GameWorldStateRunner.cs, PlayerSystem.cs, PlayerCharacterSystem.cs, PlayerCommandSystem.cs, HybridGameObjectSystemBase.cs, ThirdPersonPlayerSystems.cs (comment), gameWorldStateRunner.prefab; manifest.json/packages-lock.json (multiplayer.center); ProjectSettings/MultiplayerManager.asset. MainBootstrap.cs, WorldBootstrap.cs, StandaloneGameplayContext.cs, GameWorldAdmin.cs need no multiplayer edit.
- Test lane: CrateSystemEditModeTests.cs (server/synchronize tests, GameServer world), LevelCrateEditModeTests.cs, TEST_PLAN.md; gate is Tools/Run-UnityTests.ps1 EditMode -CoreOnly (and PlayMode).
- Docs lane: CRATE_ASSET_LOADING_FLOW.md, PLAYER_SESSION_CHARACTER_FLOW.md, CHARACTER_ANIMATION_SETUP.md, TEST_PLAN.md.
- Design trigger: yes. Shared shapes read across files/packages: `GameAssetLoadFlags` (enum, includes Synchronize), `BaseGameCrate.LoadFlags` (serialized in assets), `GameAssetLoadSingleton.RequestedAsset` remote fields and `GameCrateSingleton` sync-version fields (only athena.shared and tests read them; no other package found reading them), `WorldType` enum (serialized in prefab).

## Sources of truth
- `Impact/Packages/athena.shared/CRATE_ASSET_LOADING_FLOW.md` governs load flags/world flags; matches code (GameAssetLoadSystem 588-612), looks current.
- `Impact/ARCHITECTURE_REVIEW.md` (CLAUDE.md names it the up-to-date state) - mentions the StandaloneGameplayContext flow at line 76; no multiplayer claims.
- `Impact/Packages/athena.shared/PLAYER_SESSION_CHARACTER_FLOW.md` describes ConfigureLocalAuthoritativeWorld (line 40); matches GameWorldStateRunner.
- `Impact/Tools/TESTING.md` and `Impact/CLAUDE.md` for test gates; `AGENTS.md` for build commands.
