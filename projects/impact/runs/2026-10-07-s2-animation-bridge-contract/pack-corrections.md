# Pack corrections — 2026-10-07-s2-animation-bridge-contract
state: APPLIED

## Outcome (docs lane, order 11)
1. 03-test TimeData — APPLIED to testing.md § Which packages a test can see. Premise confirmed: the test fixtures use `using Unity.Core` and `World.SetTime(new TimeData(...))` with no extra reference.
2. 03-test Run-UnityTests.ps1 / TestResults tracked — APPLIED to testing.md § Gotchas, reconciled against the code. The script pipes Unity.exe through `Out-Default` and exits with `$LASTEXITCODE` (Run-UnityTests.ps1:71-79), so the carried "returns early" gap is fixed in the script, not a live gotcha. The pack held no earlier gap bullet, so nothing contradictory was stacked. Wording adds the line reference and "do not call Unity.exe without a pipe".
3. 04-backend Git Bash forward slashes — APPLIED to backend.md § Definition of done for this lane as a new last bullet (shell-syntax fact, taken as given; not re-run).
4. 05-test Is.AnyOf — APPLIED to testing.md § Gotchas. Not independently verifiable (no nunit.framework.dll or docs in PackageCache to grep); the evidence is the test lane's compile error and the absence of `AnyOf` in the tests now.
5. 05-test dotnet build and new test files — APPLIED to testing.md § Gotchas as a sibling of "Compile before running tests", which it qualifies rather than contradicts.

## from 03-test.md
- capabilities/testing.md § Which packages a test can see — the table lists no Unity.Core/TimeData source; add: "TimeData is in namespace Unity.Core inside the Unity.Entities assembly, no extra reference; use World.SetTime(new TimeData(elapsed, dt)) before SystemHandle.Update"
- capabilities/testing.md § Gotchas — add: "Run-UnityTests.ps1 run in the foreground did exit after Unity.exe ended on every run here (exit code = Unity's); the prior-run gap did not reproduce when output is piped. TestResults-*.xml are tracked in git and show as modified after every run"

## from 04-backend.md
- capabilities/backend.md § Definition of done for this lane — add: "From Git Bash, run the test script as powershell -ExecutionPolicy Bypass -File ./Tools/Run-UnityTests.ps1 ... with forward slashes. .\Tools\... loses its backslashes there and the script is not found (exit 127 or 1)"

## from 05-test.md
- capabilities/testing.md § Gotchas — add: "The NUnit in this project has no Is.AnyOf. Use Assert.That(new[] { a, b }, Does.Contain(x)). A compile error shows as 'Scripts have compiler errors', exit 1 after about 12 s; grep the log for 'error CS'"
- capabilities/testing.md § Gotchas — add: "dotnet build Impact.sln cannot see new test files until a Unity run has regenerated the csproj, so the first Unity batchmode run is the real compile for new test files"
