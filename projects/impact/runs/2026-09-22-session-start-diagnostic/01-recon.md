REPORT 2026-09-22-session-start-diagnostic/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - see § Findings below — this is the full body the brief indexes

risks:
  - The order's DoD item about "which one is where ordinary gameplay systems ... run during a real play session" is answered from GameWorldStateRunner.cs's own calls (it invokes GameWorldAdmin.CreateLocalWorld, not WorldBootstrap.CreateApplicationWorld, for session/asset-load setup) rather than from tracing a concrete athena.charactercontroller system's `[UpdateInGroup]` — no such system was opened, per the non-goal against re-deriving Unity internals and to stay inside the named scope. If the orchestrator needs a specific gameplay system's world placement confirmed by name, that is a follow-up grep, not inferred here.
  - Two worlds exist per session (Application World, created once by WorldBootstrap.Initialize/ICustomBootstrap; Local World, created by GameWorldAdmin.CreateLocalWorld inside GameWorldStateRunner.Execute). "World initialization" in the order's goal is ambiguous between the two — see § Findings 2-3 for exactly how they differ, since which one is meant changes both where a diagnostic system would need `[UpdateInGroup]`/`[WorldSystemFilter]` placement and which asmdef reference it needs.

## Orchestrator brief

- `athena.core`'s asmdef has zero `athena.*` dependencies and zero `ISystem`/`SystemBase` usage anywhere in the package today (§ Findings 1). A new system placed there is a green-field addition, not an extension of a pattern.
- The two worlds behave very differently: Application World is an *allow-listed* subset (only `Unity.Entities`/`Unity.Entities.Hybrid`/`Unity.Scenes` assemblies, plus `TransformSystemGroup`); Local World runs the Unity-default full system set via `WorldSystemFilterFlags.Default`, with no assembly filter (§ Findings 2). Gameplay code (crate loading, session setup, `ServiceProvider`) runs in the **Local World**, created per-session by `GameWorldAdmin.CreateLocalWorld` (§ Findings 3).
- A system compiled in `athena.core` would **not** run in Application World (its assembly is not on the allow-list) unless `athena.core`'s assembly is explicitly added to `WorldBootstrap.ApplicationWorldAllowedSystemAssemblies`; it **would** run in Local World automatically, since Local World applies no assembly filter at all — see § Findings 2 for the exact mechanism.
- `Impact.EditModeTests.asmdef` does **not** reference `Athena.Core.Runtime` today (§ Findings 4).
- `LevelCrateTestContext.cs` (§ Findings 5) is the closest existing precedent for a test that creates a `World`, calls `World.CreateSystem<T>()`, and drives `SystemHandle.Update(World.Unmanaged)` an explicit, countable number of times — usable as the shape for an "ran exactly once" proof.
- No existing "Session started"/`SessionStart`-style one-time log message exists anywhere in the repo (§ Findings 6, grep returned zero matches).
- Unity Editor version: `6000.4.0f1` (§ Findings 7).
- Sections below: **Findings 1–7** (one per DoD item, in order), **Sources consulted**.

## Findings

### 1. `athena.core` asmdef — dependencies and existing `ISystem` usage

`Impact\Packages\athena.core\Runtime\Athena.Core.Runtime.asmdef:4-8` declares
`"references": ["Unity.Mathematics", "Unity.Entities", "Unity.Collections"]` —
no `athena.*` package is referenced. This matches the guardrail-2 dependency
chain (`athena.core` is the root, no deps) stated in
`project.md` § "Hard guardrails" and `PACKAGE_ARCHITECTURE.md`.

A grep for `ISystem|SystemBase|struct.*System` across
`Impact\Packages\athena.core\**` returned **no matches**. The package's `.cs`
files are: `Editor\Dummy.cs`, `Runtime\CollectionsInternals\AssemblyInfo.cs`,
`Runtime\Utils\NativeHashMapExtensions.cs`,
`Runtime\Utils\UpdateInGroupConditional.cs`,
`Runtime\Utils\HashRetrieverUtility.cs` — all utility/helper code, none of it
an ECS system. `UpdateInGroupConditional.cs` is a helper *used by*
`WorldBootstrap.CreateApplicationWorld` (`UpdateInGroupConditionalUtility.UpdateConditionalSystemLocations`,
`WorldBootstrap.cs:93`), not a system itself.

### 2. Application World vs. Local World — what each actually schedules

Both are built in `Impact\Packages\athena.shared\Runtime\Worlds\WorldBootstrap.cs`:

- **Application World** (`CreateApplicationWorld`, `WorldBootstrap.cs:76-95`):
  starts from `DefaultWorldInitialization.GetAllSystems(WorldSystemFilterFlags.Default)`
  (all systems Unity would normally put in a default world), then
  **intersects** that set with `ApplicationWorldAllowedSystemAssemblies`
  (`WorldBootstrap.cs:18-23`: only `Unity.Entities`, `Unity.Entities.Hybrid`,
  `Unity.Scenes`), unions in `ApplicationWorldAdditionalSystems`
  (`TransformSystemGroup` only, line 27-30), then strips anything under
  `ApplicationWorldDeniedSystemGroups` (`FixedStepSimulationSystemGroup`,
  `VariableRateSimulationSystemGroup`, `PresentationSystemGroup`, lines
  32-37). It is instantiated once, on `ICustomBootstrap.Initialize`
  (`WorldBootstrap.cs:41-50`), and is `World.DefaultGameObjectInjectionWorld`
  at that point.
- **Local World** (`CreateLocalWorld`, `WorldBootstrap.cs:52-64`): also starts
  from `DefaultWorldInitialization.GetAllSystems(WorldSystemFilterFlags.Default)`,
  but adds **all** of those systems with **no assembly filter and no
  additional-systems/denied-groups narrowing** — every default-tagged system
  from every assembly (including any `athena.*` package's systems) is added
  via `DefaultWorldInitialization.AddSystemsToRootLevelSystemGroups(world, systems)`.

So Application World is a curated subset (engine-only, plus explicit
opt-ins); Local World is the Unity-standard everything-by-default set. A
system's package assembly membership only matters for Application World.

### 3. Which world runs ordinary gameplay systems in a real session

`Impact\Packages\athena.shared\Runtime\GameWorldStateRunner.cs` is the
`MonoBehaviour` that drives session start (`Start()` → `Execute()`,
lines 35-42, 44-77). For `WorldType.Local` (the only branch implemented —
`Client`/`Server` exist in the enum but are not handled), it calls
`gameWorldAdmin.CreateLocalWorld()` (`GameWorldStateRunner.cs:51`), which
resolves to `GameWorldAdmin.CreateLocalWorld` →
`WorldBootstrap.CreateLocalWorld("Local World")`
(`GameWorldAdmin.cs:33-37`, `WorldBootstrap.cs:52-64`). Session setup itself —
`ConfigureLocalAuthoritativeWorld` (crate/level session build,
`GameWorldStateRunner.cs:79-91`) and `ConfigureWorldShared`
(`ObjectSceneLoaderSingleton` creation, lines 93-100) — is applied to *that*
Local World, not to `WorldBootstrap.ApplicationWorld`.
`ServiceProvider.InitServices()` (`ServiceProvider.cs:38-52`) constructs
`gameWorldAdmin = new GameWorldAdmin(WorldBootstrap.ApplicationWorld)`
(line 50) — the Application World is passed in only as the admin's parent
reference (`GameWorldAdmin.cs:28-31`, stored as `GameWorld Id=1`); the actual
per-session gameplay world it hands out is the Local World it creates on
demand. **Conclusion, stated plainly:** ordinary gameplay code (crate
loading, session/level setup, asset-load orchestration) runs in the **Local
World**, created via `GameWorldAdmin.CreateLocalWorld`/
`WorldBootstrap.CreateLocalWorld`, during a real play session — not in the
Application World.

**A new `ISystem` placed in `athena.core` today would execute in the Local
World** (no assembly filter there — § Findings 2) but would **not** execute
in the Application World, because `athena.core`'s assembly is absent from
`ApplicationWorldAllowedSystemAssemblies` (`WorldBootstrap.cs:18-23`) — it
would need to be added there for Application-World execution. Since real
gameplay/session code runs in the Local World (this section), a system in
`athena.core` would run during a real session by virtue of Local World's
unfiltered default-system inclusion, without needing any change to
`WorldBootstrap`.

### 4. `Impact.EditModeTests.asmdef` — does it reference `Athena.Core.Runtime`?

`Impact\Assets\Tests\EditMode\Impact.EditModeTests.asmdef:3-16` references:
`UnityEngine.TestRunner`, `UnityEditor.TestRunner`, `Unity.Collections`,
`Unity.Entities`, `Unity.Mathematics`, `Unity.Scenes`,
`Unity.Entities.Hybrid`, `Athena.SceneSlice.Runtime`,
`Athena.SceneSlice.Editor`, `Athena.Shared.Runtime`, `Athena.Shared.Components`,
`Athena.ContentManagement.Runtime`. **`Athena.Core.Runtime` is not in this
list.** A test that needs to reference a new `athena.core` system directly
would need this asmdef updated first (a `test`-lane, not `backend`-lane,
concern per `project.md` § Lane routing).

### 5. Existing EditMode-test precedent for a World + exactly-once system proof

`Impact\Assets\Tests\EditMode\Crates\LevelCrateTestContext.cs` is the closest
precedent found. It creates its own `World` in its constructor
(`new World("Level Crate Test World", WorldFlags.Game)`, line 16), calls
`World.CreateSystem<GameCrateLoadSystem>()` to get a `SystemHandle`
(line 19), and exposes an explicit `UpdateOneFrame()` method
(lines 84-88) that calls `SystemHandle.Update(World.Unmanaged)` on each
system handle exactly once per invocation, then disposes the `World`
(`Dispose()`, lines 32-38). Its consumer,
`Impact\Assets\Tests\EditMode\Crates\CrateSystemEditModeTests.cs`, is the
paired test file (found in the same grep, not opened in detail — scope
covers the whole `Assets\Tests\EditMode\**` tree so it is available for a
follow-up read if the test lane needs the exact assertion style). No other
EditMode test file under `Assets\Tests\EditMode\**` matched a grep for
`World.DefaultGameObjectInjectionWorld|new World\(|CreateLocalWorld|CreateApplicationWorld`.

### 6. Existing one-time startup log message

A grep across `Impact\Assets` and `Impact\Packages` (repo-wide, via the whole
`Impact` tree) for `Session started|SessionStart|Session Started` returned
**zero matches**. No such diagnostic currently exists anywhere in the repo —
this would be a genuinely new addition, not a duplicate of existing
functionality.

### 7. Unity Editor version

`Impact\ProjectSettings\ProjectVersion.txt:1-2`:
```
m_EditorVersion: 6000.4.0f1
m_EditorVersionWithRevision: 6000.4.0f1 (8cf496087c8f)
```
Exact version string: **`6000.4.0f1`**.

## Sources consulted

- `Impact\Packages\athena.core\Runtime\Athena.Core.Runtime.asmdef`
- `Impact\Packages\athena.core\Runtime\**\*.cs` (all 5 files, via glob)
- `Impact\Packages\athena.shared\Runtime\Worlds\WorldBootstrap.cs`
- `Impact\Packages\athena.shared\Runtime\Worlds\GameWorldAdmin.cs`
- `Impact\Packages\athena.shared\Runtime\GameWorldStateRunner.cs`
- `Impact\Packages\athena.shared\Runtime\ServiceProvider.cs`
- `Impact\Assets\Tests\EditMode\Impact.EditModeTests.asmdef`
- `Impact\Assets\Tests\EditMode\Crates\LevelCrateTestContext.cs`
- `Impact\ProjectSettings\ProjectVersion.txt`
- `<agenticRoot>\projects\impact\capabilities\backend.md` (§ Known weak spots, per `inputs`)
- `<agenticRoot>\projects\impact\capabilities\testing.md` (per `inputs`)
- `<agenticRoot>\projects\impact\project.md`, `<agenticRoot>\PROTOCOL.md` (binding)
- `PACKAGE_ARCHITECTURE.md` and `ARCHITECTURE_REVIEW.md` were **not** opened —
  the order's scope names them, but every DoD item was answerable directly
  from the code files above; naming them here so the orchestrator knows they
  remain unread if a later lane needs their narrative content specifically.
