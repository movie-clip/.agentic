REPORT 2026-09-24-remove-multiplayer/06
status:      PARTIAL
verdict:     NONE

changed:
  - Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs — deleted `GameAssetLoadSystem_TracksAndReleasesRemoteOnlyRequests` whole (tested remote-load behavior that no longer exists, including the `new World(..., WorldFlags.GameServer)` construction)
  - Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs — `GameAssetLoadFlags.Client` -> `GameAssetLoadFlags.None` in `GameCrateLoadSystem_MarksCrateLoadedWhenLinkedAssetRequestsFinish` (arbitrary flag, not testing removed semantics)
  - Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs — `GameAssetLoadFlags.Client`/`.Server` -> `GameAssetLoadFlags.SetActiveScene` at both round-trip assertion sites, so the round-trip is still exercised against a flag that still exists
  - Round-trip sites: `GameAssetLoad_CreateForEntityPrefab_PreservesPriorityAndOrder`, `GameAssetLoad_CreateForEntityScene_PreservesPriorityAndSections` — see previous bullet
  - Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs — dropped the `RemoteLoadCount = 1,` initializer line in `GameAssetLoadSingleton_CreateAndDispose_ManagesRequestedAssetMap`
  - Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs — renamed test method `AuthoritativeCharacterSkinLoadSystem_StartSwitchSkinProcess_AddsPendingRequestForNonDefaultSkin` -> `CharacterSkinLoadSystem_StartSwitchSkinProcess_AddsPendingRequestForNonDefaultSkin`, mechanical rename only
  - Same test's call site: `AuthoritativeCharacterSkinLoadSystem.StartSwitchSkinProcess` -> `CharacterSkinLoadSystem.StartSwitchSkinProcess` — see previous bullet
  - Impact/Assets/Tests/EditMode/Crates/CrateSystemEditModeTests.cs — renamed `AuthoritativeCharacterSkinLoadSystem_StartSwitchSkinProcess_RemovesPendingRequestForDefaultSkin` -> `CharacterSkinLoadSystem_StartSwitchSkinProcess_RemovesPendingRequestForDefaultSkin` and its call site, same rename
  - Impact/Assets/Tests/EditMode/Crates/LevelCrateEditModeTests.cs — `GameAssetLoadFlags.Client` -> `GameAssetLoadFlags.None` at both linked-asset-load test-setup sites (`LevelCrate_WithLinkedChildCrate_...`, `LevelCrate_WithLinkedAssetRequest_...`), arbitrary flag, not testing removed semantics

verification:
  command:   cd C:\projects\impact\Impact && dotnet build Impact.sln && powershell -ExecutionPolicy Bypass -File .\Tools\Run-UnityTests.ps1 -Platform EditMode -CoreOnly
  result:    FAIL
  detail:    `dotnet build Impact.sln` is clean — 0 Error(s), 17 warnings (all pre-existing MSB3277 reference-conflict noise unrelated to this change). `Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly` then aborted with "It looks like another Unity instance is running with this project open" — confirmed via Editor.log that the open Editor instance has this exact project (`C:\projects\impact\Impact`) open, matching testing.md's documented gotcha. I did not close the running Editor (three live Unity.exe processes) since killing a session I don't own risks unsaved user work; this is an environmental blocker, not a defect from this edit — every stale-symbol grep across the whole Assets/Tests tree returns zero hits after these changes.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The EditMode suite still needs an actual run to confirm PASS: close the open Unity Editor instance (or run these two files' tests from that Editor's own Test Runner window) then re-run `Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly`, or `dotnet build Impact.sln` clean plus the exhaustive stale-symbol grep (see verification.detail) are the only evidence available right now
  - The two `git mv` renames backend-b already flagged (`GameAuthoritativeConfiguration.cs` -> `GameSessionConfiguration.cs`, `AuthoritativeCharacterSkinLoadSystem.cs` -> `CharacterSkinLoadSystem.cs`) are still outstanding — no lane in this run has a rename tool

skill_calls:
  - none

risks:
  - No failing/flaky test surfaced, so `mattpocock-skills:diagnosing-bugs` was not triggered, and no fake-vs-real-World or test/production-coupling judgment was needed, so `mattpocock-skills:tdd` was not triggered — every edit was a mechanical delete/rename/flag-substitution per the order's own line-level spec
  - `Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly` could not complete: the Unity Editor was already open on this exact project (testing.md § Gotchas names this exact failure mode)
  - I chose not to kill the running Editor process since I cannot tell whether it holds unsaved user work, and no lane instruction authorizes that — this leaves the test-pass half of `verification` unproven by a live run
  - Compensating evidence short of a live run: `dotnet build Impact.sln` is 0 Error(s)
  - Further compensating evidence: a repo-wide grep across `Impact/Assets/Tests` for every deleted/renamed symbol returns zero hits, including in the untouched `LevelCrateTestContext.cs` shared fixture
  - Symbols grepped: `GameAssetLoadFlags.Client/.Server/.Synchronize`, `RemoteLoadCount`, `RemoteSectionLoadCount`, `WorldFlags.GameServer`, `AuthoritativeCharacterSkinLoadSystem`, `CriticalSyncVersion`, `NonCriticalSyncVersion` — see previous bullet
