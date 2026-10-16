# Capability pack: `testing` (Impact)

Owns `Impact/Tools/**` and the project's two test assemblies,
`Impact/Assets/Tests/EditMode` and `Impact/Assets/Tests/PlayMode`, including
their `.asmdef` files.

## Index

**Always read:** **Gotchas** · **Running the suite** · **Definition of done
for this lane**

| Section | Read it when |
|---|---|
| Single fixture / single test | your order only needs to prove one behaviour, not the whole suite |
| EditMode vs PlayMode | you are adding a new test and choosing which platform |
| Which packages a test can see | your new test exercises a package, or fails to compile against one |
| Technique skills (mattpocock-skills) | you are making the `tdd` call Definition of done requires, or a failing or flaky test resists your first diagnosis |

## Gotchas

- **Unity batchmode fails if the project is already open in the Editor** —
  close it first, or run the same test from the open Editor's Test Runner
  instead of treating it as a test bug.
- **Compile before running tests.** `dotnet build Impact.sln` first; a stale
  compile produces confusing failures that look like test bugs.
- **Always write results to a file**, never rely on console output alone —
  a human or a later gate needs to inspect failures after the process exits.
- **`Run-UnityTests.ps1`'s `-UnityPath` default has drifted from the actual
  Editor version before** (it pointed at `6000.1.8f1` while the project was
  on `6000.4.0f1`).
- Check the script's `-UnityPath` default against
  `Impact/ProjectSettings/ProjectVersion.txt` before assuming a wrong-Editor
  run is a test bug.
- **`Run-UnityTests.ps1` waits for Unity and returns its exit code.** The
  script pipes `Unity.exe` through `Out-Default` (`Run-UnityTests.ps1:71-79`),
  because Unity.exe is a GUI program and PowerShell only waits for it, and
  only sets `$LASTEXITCODE`, when its output is piped.
- **In PowerShell, do not call `Unity.exe` without a pipe.** It returns at
  once and `$LASTEXITCODE` is not set.
- **For test runs, `Run-UnityTests.ps1` wins over the raw `Unity.exe`
  `-runTests` lines in `AGENTS.md`.** Use the script; a raw call needs the
  same pipe.
- **The `TestResults-*.xml` files are tracked in git** and show as modified
  after every run.
- **The NUnit in this project has no `Is.AnyOf`.** Use
  `Assert.That(new[] { a, b }, Does.Contain(x))`.
- **A test compile error shows as "Scripts have compiler errors"**, exit 1
  after about 12 s. Grep the log for `error CS`.
- **`dotnet build Impact.sln` cannot see new test files until a Unity run has
  regenerated the csproj**, so the first Unity batchmode run is the real
  compile for new test files.

## Running the suite

Run these from `Impact\` (one level below the repo root) — the `.\Tools\`
paths are relative to that directory, not the git root.

`-CoreOnly` passes `-testCategory "Core"`. Both test assemblies declare
`[assembly: Category("Core")]`, so `-CoreOnly` runs every project test.
Dropping it adds nothing: the manifest has no `testables`, so no package tests
run either way. Don't quote a test count from a doc; read `total=` in the
results XML.

```powershell
powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly
powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform PlayMode -CoreOnly
```

Full detail and the current `Core`-tagged fixture list: `Tools/TESTING.md`.

## Single fixture / single test

Via `-Filter` (fully qualified name):

```powershell
powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -Filter "Impact.EditModeTests.Crates.CrateSystemEditModeTests"
powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform PlayMode -Filter "Impact.PlayModeTests.Crates.CrateBootstrapPlayModeTests.MainBootstrap_RepeatedPlayerCrateCycles_ReturnToBaselineBookkeeping"
```

Prefer this over the full suite when an order only needs to prove one
behaviour — it is the same filter mechanism `AGENTS.md` § Single-Test
Guidance documents for raw Unity batchmode `-testFilter`, wrapped by the
script.

## EditMode vs PlayMode

Choose `EditMode` unless the test depends on scene playback, GameObjects in
play mode, or runtime integration behaviour — `PlayMode` is for exactly that
case (`AGENTS.md` § Single-Test Guidance). Most new coverage in this repo is
`EditMode`; reach for `PlayMode` deliberately, not by default.

## Which packages a test can see

| Assembly | References (Athena) |
|---|---|
| `Impact.EditModeTests` | sceneslice (Runtime, Editor), shared (Runtime, Components), contentmanagement, core, Unity.Transforms |
| `Impact.PlayModeTests` | shared (Runtime, Components), contentmanagement, Unity.Transforms |

- No test assembly references `athena.charactercontroller`, `athena.gameplay`
  or `athena.ai`. Today only the compile covers them.
- A test for one of those packages needs a new reference in the test
  `.asmdef`. Adding it is yours, but say so in `changed`.
- Test code follows the same direction rule as runtime code (`project.md`
  guardrail 2).
- `TimeData` is in namespace `Unity.Core` inside the `Unity.Entities`
  assembly, so no extra reference is needed. Use
  `World.SetTime(new TimeData(elapsed, dt))` before `SystemHandle.Update`.

## Technique skills (mattpocock-skills)

Impact's `.claude/settings.json` enables this plugin. Constraints for the
`mattpocock-skills:tdd` call Definition of done requires:

- You still never touch non-test code to turn a test green (Scope discipline
  in your role file).
- The seams for a new test are the ones your order's `inputs` name. Don't
  pause to ask which seam; that was decided upstream.
- Red before green costs a Unity boot each way. Prove red once with `-Filter`
  on the new test, then green. Don't loop per assertion.
- A seam that needs a running World or a scene is `PlayMode`. Everything else
  stays `EditMode` (§ EditMode vs PlayMode).

A failing or flaky test resists your first diagnosis: call the Skill tool
with `mattpocock-skills:diagnosing-bugs`. Adapted to this lane:

- Your feedback loop is `-Filter` on the failing test. Each run is a cold
  batchmode boot, so batch probes per run.
- Tag every probe `Debug.Log("[DEBUG-xxxx] ...")`, and grep the tag to remove
  them all before you report.
- If the defect is in the test itself, fix it — that's your job.
- If the defect is in production code, stop at diagnosis: report it as a
  finding per Scope discipline, and do not patch non-test code.
- The skill's "ask the user" moments become a `risks` entry instead.
- Name any scratch file in `handoff` with its `git rm <path>` command — you
  have no delete tool.
- No commit. Your report is the protocol's report block, not a commit message.
- Record each call in `skill_calls:` (`PROTOCOL.md` § 7).

## Definition of done for this lane

- The order's `verification` command was actually run, and its result
  (`PASS`/`FAIL`, with counts) is in the report — not assumed from a compile
  succeeding.
- Test results were written to a file (`TestResults-*.xml`), not read off the
  console only.
- A new test's platform choice (`EditMode`/`PlayMode`) matches the rule
  above, and is stated in `changed` if it might look surprising.
- If you chose between a fake and a real ECS World/system, or accepted
  test/production coupling, you called `mattpocock-skills:tdd` first.
- That call is recorded in `skill_calls:`, not only noted in `risks`
  afterward.
