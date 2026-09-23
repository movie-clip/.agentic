REPORT 2026-09-23-fix-cr1-cr2/03
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   dotnet build Impact.sln && powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly
  result:    PASS
  detail:    dotnet build: 0 Error(s), 17 pre-existing dependency-conflict warnings (unchanged from prior run, none from this diff). Independently re-ran a plain -CoreOnly EditMode pass myself (not trusting 02-test.md's own numbers, per this order's DoD): TestResults-EditMode.xml shows testcasecount="35" total="35" passed="35" failed="0" skipped="0" result="Passed", exit code 0 — matches 02-test.md's claimed 35/35 exactly.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-2 confirmed satisfied: SessionStartDiagnosticSystem.cs:17 now ends OnCreate with `state.Enabled = false;`, matching GameSessionSystem.cs:25's precedent exactly (same one-shot, no-OnUpdate ISystem shape). Test file (SessionStartDiagnosticSystemEditModeTests.cs) asserts only on log count, never on state.Enabled, as CR-2 predicted — no test changes were needed and none were made.
  - CR-1 confirmed satisfied: Run-UnityTests.ps1:35-38 now sets $effectiveCategory = "Core" and emits it as a standalone `-testCategory "Core"` argument (lines 54-57), independent of `-testFilter`, which now only carries the caller's own `-Filter` value (line 33, 49-52). A plain `-CoreOnly` run selects the true 35-test Core-tagged suite, not the 1-test name-substring match CR-1 found.
  - 02-test.md's pack_correction verified accurate against the current file: testing.md:36-40 does still read the pre-fix text ("-CoreOnly today runs -testFilter \"Core\" ... Do not rely on it to run every [Category(\"Core\")] test") and the script behavior it describes is now stale, since the fix above. Safe to apply at close per the docs lane's pack-corrections.md loop.

risks:
  - none
