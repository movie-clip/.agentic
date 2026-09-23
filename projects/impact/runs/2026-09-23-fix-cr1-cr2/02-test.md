REPORT 2026-09-23-fix-cr1-cr2/02
status:      DONE
verdict:     NONE

changed:
  - Impact\Tools\Run-UnityTests.ps1 — `-CoreOnly` now passes `-testCategory "Core"` (a real NUnit category filter) instead of folding "Core" into `-testFilter`; `-Filter` still maps to `-testFilter` unchanged and both can be combined.

verification:
  command:   powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly
  result:    PASS
  detail:    TestResults-EditMode.xml: testcasecount="35" total="35" passed="35" failed="0" inconclusive="0" skipped="0" result="Passed" — full EditMode Core suite now selected, matching CR-1's expected 35/35 (was 1/35 before the fix). dotnet build Impact.sln also ran clean (0 errors, 17 pre-existing warnings unrelated to this change).

contract_notes:
  - none

pack_corrections:
  - projects/impact/capabilities/testing.md:36-40 — stale: says `-CoreOnly` runs `-testFilter "Core"` (fixed by CR-1). Replacement: "`-CoreOnly` now passes `-testCategory \"Core\"`, a true NUnit category match, and selects the full 35-test Core suite; `-Filter` is unaffected."

handoff:
  - Impact\Tools\TESTING.md (docs lane owns Impact/*.md) may also reference the old `-CoreOnly`/`-testFilter` behaviour from CR-1's diagnostic run — worth a check when docs next touches that file, out of this lane's scope.

risks:
  - none
