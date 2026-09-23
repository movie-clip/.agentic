REPORT 2026-09-23-active-scene-diagnostic/02
status:      PARTIAL
verdict:     NONE

changed:
  - Impact/Assets/Tests/EditMode/Core/ActiveSceneDiagnosticSystemEditModeTests.cs — new EditMode test proving `ActiveSceneDiagnosticSystem` logs its active-scene message exactly once from `OnCreate`, and not again after a manual `Update`
  - the new test mirrors `SessionStartDiagnosticSystemEditModeTests`'s proof shape exactly — own `World`, `LogAssert.Expect`, an `Application.logMessageReceived` counter, `world.Dispose()` in teardown

verification:
  command:   unity pipeline list (fast path, tried first); dotnet build Impact.sln; powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -Filter "Impact.EditModeTests.Core.ActiveSceneDiagnosticSystemEditModeTests" (run from Impact/)
  result:    FAIL
  detail:    unity-cli fast path tried first per the order: `unity pipeline list` showed Impact/PID 19804/Pipeline:true but `Server Reachable: false` with no `Server Port`, same as both prior dispatches this run — confirmed unusable, not retried further. `dotnet build Impact.sln` (clean first) passed: 0 Error(s), 17 Warning(s), same pre-existing MSB3277 vendored-assembly-conflict set the backend report logged, none referencing the new test file. The batchmode fallback then aborted before running any test: "Aborting batchmode due to fatal error: It looks like another Unity instance is running with this project open" — `tasklist` confirms Unity.exe PID 19804 (the same open Editor the fast path found) is live. `Tools/TESTING.md`/the testing pack's own Gotchas section names this exact failure mode ("Unity batchmode fails if the project is already open in the Editor — close it first"); closing/killing a running Editor the human has open is outside this lane's authority to decide unilaterally, so verification could not complete either path this dispatch.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `ActiveSceneDiagnosticSystemEditModeTests.cs` has no Unity `.meta` yet, same as the backend's production file — created outside the Editor, so Unity will auto-generate it on the next asset-database refresh/domain reload; no GUID was hand-fabricated
  - `Impact.EditModeTests.asmdef` needed no change — it already references `Athena.Core.Runtime` (added for the backend's system) and every other reference (`UnityEngine.TestRunner`, `NUnit`, `Unity.Entities`) the new test uses was already present from the `SessionStartDiagnosticSystemEditModeTests` precedent
  - to actually run verification: either close the open Unity Editor (PID 19804) so batchmode can claim the project lock, or get the Pipeline server reachable (`Server Port` bound) so `unity command eval`/Test Runner can be driven through the open Editor instead — either unblocks the same filter command already in this report

risks:
  - test file is unexecuted this dispatch — code review only, not a PASS
  - the test's regex is built from the live `SceneManager.GetActiveScene().name` at run time (via `Regex.Escape`), not a hardcoded scene name, to hold across whatever EditMode's actual active scene is
  - both the unity-cli fast path and the batchmode fallback are unavailable simultaneously in this run's environment (Editor open + unreachable Pipeline server) — third consecutive dispatch to hit this (01-backend, 02-test), worth escalating to the human
