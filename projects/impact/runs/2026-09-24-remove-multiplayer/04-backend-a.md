REPORT 2026-09-24-remove-multiplayer/04
status:      PARTIAL
verdict:     NONE

changed:
  - Impact/Packages/manifest.json — removed `com.unity.multiplayer.center: 1.0.1` dependency line (D-3); packages-lock.json left untouched for Unity to regenerate
  - Impact/Packages/athena.shared/Runtime/GameWorldStateRunner.cs — shrank `WorldType` enum to `{ Local }`, removed `Client`/`Server` members; `Local` stays value 0
  - Impact/Packages/athena.shared/Runtime/GameWorldStateRunner.cs — deleted the unused `LoadGameplayBootstrap(World)` method (zero call sites in the repo, confirmed by grep before removal)
  - Impact/Packages/athena.shared/Runtime/Systems/Player/PlayerSystem.cs:73 — collapsed `state.WorldUnmanaged.Flags is WorldFlags.Game or WorldFlags.GameServer` to `state.WorldUnmanaged.Flags == WorldFlags.Game`
  - Impact/Packages/athena.shared/Runtime/Systems/Player/PlayerCharacterSystem.cs:73 — collapsed `state.WorldUnmanaged.Flags is WorldFlags.Game or WorldFlags.GameServer` to `state.WorldUnmanaged.Flags == WorldFlags.Game`
  - Impact/Packages/athena.shared/Runtime/Systems/Player/PlayerCommandSystem.cs:52 — collapsed `state.WorldUnmanaged.Flags is WorldFlags.Game or WorldFlags.GameClient` to `state.WorldUnmanaged.Flags == WorldFlags.Game`
  - Impact/Packages/athena.shared/Runtime/Systems/Hybrid/HybridGameObjectSystemBase.cs:62-65 — deleted the `if (World.Flags is WorldFlags.GameServer) { Enabled = false; }` block outright; a GameServer world is never created, so the guard was unreachable dead code rather than a branch with a Game-path equivalent to keep
  - Impact/Packages/athena.charactercontroller/Runtime/ThirdPerson/ThirdPersonPlayerSystems.cs:121-122 — dropped the stale netcode-prediction comment above `OrbitCamera orbitCamera = ...`, replaced with a one-line non-netcode comment describing why rotation is calculated rather than read from transform

verification:
  command:   cd C:\projects\impact\Impact && dotnet build Impact.sln
  result:    PASS
  detail:    Build succeeded — 0 Error(s), 17 Warning(s) (all pre-existing MSB3277 System.Threading.Tasks.Extensions version-conflict warnings across multiple .csproj files, unrelated to this change; none reference the files this order touched)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Delete incomplete — no lane has a delete tool: run `git rm Impact/ProjectSettings/MultiplayerManager.asset` to complete D-3. The file was left in place, untouched, per PROTOCOL.md § "You cannot delete or rename files"; DoD explicitly names this as the required fallback rather than emptying the file.
  - Backend-B's next dispatch on GameWorldStateRunner.cs should expect the file already has `WorldType` at `{ Local }` and no `LoadGameplayBootstrap` method — its own target-shapes edits (L26 default `loadFlags`, the `GameAuthoritativeConfiguration`/D-4 rename) are unaffected and still apply against the current file content.

skill_calls:
  - none

risks:
  - No first-attempt fix failed and needed `mattpocock-skills:diagnosing-bugs` — this order was a direct, pre-specified deletion/collapse with no diagnosis step, so `skill_calls` is a bare none rather than a recorded non-call.
  - Four of the eight scoped paths don't match the repo: `PlayerSystem.cs`/`PlayerCharacterSystem.cs`/`PlayerCommandSystem.cs` actually live under `Systems/Player/`, not directly under `Systems/`.
  - `ThirdPersonPlayerSystems.cs` actually lives in `athena.charactercontroller/Runtime/ThirdPerson/`, not `athena.shared/Runtime/Systems/` as the scope fence states — a different package, not just a missing subfolder.
  - Each of those four filenames is unique repo-wide (verified by `find` before editing) and its content matched the order's own line numbers and description exactly, so I read this as path-prefix drift in the order's drafting and edited the real files rather than stopping.
  - Flagging the path drift above since a stricter reading of "scope is a fence" could call editing `athena.charactercontroller` out of scope — the fence's own literal path for that file does not exist anywhere in the repo.
  - HybridGameObjectSystemBase.cs's `WorldFlags.GameServer` branch disabled the system on GameServer, unlike the other three sites which gate work to run only on Game — not the same shape as a `Game`-vs-`GameClient/GameServer` check to collapse.
  - I deleted that whole guard rather than converting it to a `WorldFlags.Game` check, since converting it would invert its meaning (disabling the system on the one world type that now always exists) — the only reading of "collapse to the Game path" that doesn't change behavior there.
