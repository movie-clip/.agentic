REPORT 2026-09-23-active-scene-diagnostic/01
status:      DONE
verdict:     NONE

changed:
  - Impact/Packages/athena.core/Runtime/Systems/ActiveSceneDiagnosticSystem.cs — new one-shot `ISystem` logging `[Impact] Active scene — <sceneName>` in `OnCreate` via `Debug.Log`, then `state.Enabled = false;`

verification:
  command:   dotnet build Impact.sln (run from C:\projects\impact\Impact)
  result:    PASS
  detail:    Build succeeded. 0 Error(s), 17 Warning(s) — all 17 are pre-existing MSB3277 assembly-conflict warnings from vendored packages, none reference the new file. Active scene name read via UnityEngine.SceneManagement.SceneManager.GetActiveScene().name; required no new .asmdef reference — Athena.Core.Runtime.asmdef has noEngineReferences:false, so UnityEngine.SceneManagement (part of UnityEngine.CoreModule) is already available the same way Debug/Application are in the precedent, with no explicit reference for either.

contract_notes:
  - no new .asmdef reference was needed for UnityEngine.SceneManagement — Athena.Core.Runtime.asmdef's noEngineReferences:false already grants the full UnityEngine core module set, so this does not re-trigger design per phases.md
  - athena.core remains the correct package for this second diagnostic: it has zero athena.* dependencies (PACKAGE_ARCHITECTURE.md), so the system stays visible regardless of which higher package loads, and is picked up by the unfiltered Local/Game World the same way SessionStartDiagnosticSystem is — placing it deeper in the chain would make it conditional on that package being present

pack_corrections:
  - none

handoff:
  - the new file has no Unity .meta yet — created outside the Editor, so Unity will auto-generate ActiveSceneDiagnosticSystem.cs.meta on its next asset-database refresh/domain reload; no GUID was hand-fabricated
  - test lane: this system has no dedicated test coverage; a scene-name-in-log check would be the natural fixture to add
  - unity-cli path was unreachable this run too — unity pipeline list showed Impact (PID 19804), Pipeline:true, but Server Reachable:false with no Server Port, same failure mode as the 2026-09-22 run

risks:
  - none
