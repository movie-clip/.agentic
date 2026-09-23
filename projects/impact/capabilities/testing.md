# Capability pack: `testing` (Impact)

Owns `Impact/Tools/**` and the project's EditMode/PlayMode test assemblies.

## Index

**Always read:** **Gotchas** · **Running the suite** · **Definition of done
for this lane**

| Section | Read it when |
|---|---|
| Single fixture / single test | your order only needs to prove one behaviour, not the whole suite |
| EditMode vs PlayMode | you are adding a new test and choosing which platform |

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

## Running the suite

Run these from `Impact\` (one level below the repo root) — the `.\Tools\`
paths are relative to that directory, not the git root.

`-CoreOnly` now passes `-testCategory "Core"`, a true NUnit category match,
and selects the full 35-test Core suite; `-Filter` is unaffected.

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

## Definition of done for this lane

- The order's `verification` command was actually run, and its result
  (`PASS`/`FAIL`, with counts) is in the report — not assumed from a compile
  succeeding.
- Test results were written to a file (`TestResults-*.xml`), not read off the
  console only.
- A new test's platform choice (`EditMode`/`PlayMode`) matches the rule
  above, and is stated in `changed` if it might look surprising.
