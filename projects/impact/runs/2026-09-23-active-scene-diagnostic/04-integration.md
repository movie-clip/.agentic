REPORT 2026-09-23-active-scene-diagnostic/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build Impact.sln (from Impact/); powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly (from Impact/)
  result:    PASS
  detail:    dotnet build: 0 Error(s), 17 Warning(s) — same pre-existing MSB3277 vendored-assembly-conflict set every prior report in this run logged, none referencing the two files in scope. Run-UnityTests.ps1 -CoreOnly (no open Editor blocking this time; confirmed via tasklist first): exit code 0, TestResults-EditMode.xml test-run node testcasecount="36" result="Passed" total="36" passed="36" failed="0" inconclusive="0" skipped="0" — the corrected `-testCategory "Core"` flag from CR-1 selected the full Core suite (35 pre-existing + this dispatch's 1 new fixture), not a name-substring subset. The new fixture's own node: `ActiveSceneDiagnosticSystemEditModeTests` testcasecount="1" result="Passed".

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs lane: PACKAGE_DOCUMENTATION.md (athena.core) documents SessionStartDiagnosticSystem (lines 22, 52) but not the new ActiveSceneDiagnosticSystem — worth adding at the next docs touch; not blocking, docs was not part of this dispatch.

risks:
  - the order's `inputs` path for CR-1 (`../2026-09-22-session-start-diagnostic/cr/CR-1.md`) does not exist — that run directory is gone from disk.
  - verified CR-1's fix instead via `runs/2026-09-23-fix-cr1-cr2/{01-backend,02-test,03-integration}.md`, which confirm `-CoreOnly` now emits a standalone `-testCategory "Core"` argument, independent of `-testFilter`.
  - this dispatch's own 36/36 `-CoreOnly` run (see verification) is consistent with that fix already being live — no discrepancy found.
  - the test's exactly-once proof asserts a log-count field equals 1 right after `world.CreateSystem<T>()`, and again after an explicit `systemHandle.Update()`.
  - that shape is sound because it does not rely solely on `LogAssert.Expect`, which alone would only prove at-least-one occurred, not exactly-one.
  - the new test mirrors `SessionStartDiagnosticSystemEditModeTests`'s already-integration-reviewed proof shape field-for-field, no deviation.

## Orchestrator brief

- Verdict: PASS. No change requests filed — engineering is coherent, no CRs to relay.
- Both mechanical gates re-run independently and confirmed: `dotnet build Impact.sln` clean (0 errors); `Run-UnityTests.ps1 -Platform EditMode -CoreOnly` 36/36 passed, using the corrected `-testCategory "Core"` flag from the prior run's CR-1.
- `ActiveSceneDiagnosticSystem.cs` exactly mirrors `SessionStartDiagnosticSystem.cs`'s one-shot `ISystem` shape (`OnCreate` logs, then `state.Enabled = false;`); `athena.core` is the correct package (zero deps, matches precedent).
- Test's exactly-once proof is sound: explicit log-count assertions before/after a manual `Update()`, not `LogAssert.Expect` alone.
- See § Engineering coherence for the full precedent-by-precedent check (asmdef, category tagging, `.meta` generation, package placement).
- `handoff`: one SHOULD_FIX-flavoured, non-blocking note for the docs lane (PACKAGE_DOCUMENTATION.md doesn't yet list the new system) — not a CR, does not block close.
- `risks`: the order's CR-1 `inputs` path is stale (run dir no longer exists) — verified CR-1's fix via the `2026-09-23-fix-cr1-cr2` run's artifacts instead; no impact on this verdict.

## Engineering coherence

- **Precedent mirror.** `ActiveSceneDiagnosticSystem.cs` (Impact/Packages/athena.core/Runtime/Systems/ActiveSceneDiagnosticSystem.cs:12-19) matches `SessionStartDiagnosticSystem.cs:12-19` exactly in shape: `partial struct : ISystem`, no `OnUpdate`, `Debug.Log` in `OnCreate` followed by `state.Enabled = false;` as the last line — the same one-shot pattern `GameSessionSystem.cs:14-26` (athena.shared) established and CR-2 required for the precedent system in the prior run. No deviation.
- **Package placement.** `athena.core` has zero `athena.*` dependencies (PACKAGE_ARCHITECTURE.md:13,25,47), matching the precedent's placement and the dependency-chain guardrail (`athena.core` → `athena.contentmanagement` → `athena.shared` → …). `UnityEngine.SceneManagement` needs no new `.asmdef` reference — `Athena.Core.Runtime.asmdef`'s `noEngineReferences: false` already grants the full UnityEngine core module set, confirmed by the clean build.
- **Test asmdef.** `Impact.EditModeTests.asmdef` already references `Athena.Core.Runtime` (line 16) from the precedent dispatch; no change was needed or made for this test, confirmed by reading the current file.
- **Category tagging.** The new test needs no per-fixture `[Category("Core")]` — `Impact/Assets/Tests/EditMode/AssemblyInfo.cs:3` applies `[assembly: Category("Core")]` to the whole EditMode assembly, so it was picked up by `-CoreOnly` automatically; the 36-vs-35 count confirms this.
- **`.meta` files.** Both new source files lack a hand-authored `.meta`, as both build reports flagged; confirmed the Editor batchmode run auto-generated `ActiveSceneDiagnosticSystem.cs.meta` and `ActiveSceneDiagnosticSystemEditModeTests.cs.meta` on its own asset-database refresh during this verification — no GUID collision, no fabricated GUID.
- **No stray scope.** `git status` shows no changes outside what the backend/test dispatches already reported; nothing else was touched by this review.
