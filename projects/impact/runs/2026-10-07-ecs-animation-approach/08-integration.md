REPORT 2026-10-07-ecs-animation-approach/08
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd Impact; dotnet build Impact.sln (also --no-incremental); Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly
  result:    PASS
  detail:    dotnet build 0 errors (36 warnings, all MSB3277 reference conflicts). EditMode total=45 passed=45 failed=0. PlayMode total=8 passed=8 failed=0. Run by me from XML in the scratchpad. Anchor: red-run assertion text in 06, not the plan alone.

contract_notes:
  - CharacterAnimationBridgeInitialized is now a managed cleanup class with LinkedInstance. Grep shows only the bridge, the cleanup system and tests (typeof only) touch it. No client type lags
  - HybridGameObjectSystemBase generic spawner now skips HybridGameObjectManualCreation. Only CharacterAuthoring adds that tag in the repo, so no other entity changes behaviour
  - Docs lag for the close lane: athena.shared PACKAGE_DOCUMENTATION.md:97 and CHARACTER_ANIMATION_SETUP.md ("runs once", marker semantics). Not requested as changes here

pack_corrections:
  - none

handoff:
  - Slice may proceed to docs lane 09. No BLOCKING finding, no re-run of this gate needed
  - Open SHOULD_FIX for the ledger Open table: C:\projects\investments\.agentic\projects\impact\runs\2026-10-07-ecs-animation-approach\cr\CR-1.md (per-frame Animator-less LogWarning, backend, bridge file only)
  - Uncommitted ProjectSettings/ProjectSettings.asset churn is line-ending noise only (git diff --ignore-space-at-eol is empty). Not lane work. The human may discard it before committing
  - Missing tests, not blocking, for a later test order: bridge pass-2 skip when Spawned.Instance is null for a frame, and the not-ready skin fallback now spawning the baked default

skill_calls:
  - mattpocock-skills:codebase-design — called, before writing the reuse and consistency judgments. Applied: the bridge module still owns link lifetime (locality holds across three edited files), tests cross the Animator-parameter seam, no new seam opened

risks:
  - Test gate did not exercise the Animator-less path (0 warning lines in either run log), so CR-1 rests on code reading, not execution
  - Pass-2 cost per frame (one reference compare per linked character, plan estimate about 15 microseconds at 150 characters) is still unmeasured. S2 should treat it as an input
  - Generated csproj files were not edited by lanes. dotnet build only saw new files after Unity regenerated them. My --no-incremental build ran after the Unity runs and covers them
  - E3 proves the generic spawner skips ManualCreation in a minimal world only. Whether the full flow ever hit D5 stays unproven, as 05 said

## Orchestrator brief
- Verdict: PASS. Engineering is coherent with 05; no BLOCKING finding.
- Gates run by me: dotnet build 0 errors; EditMode 45/45; PlayMode 8/8 (Unity closed, results read from XML).
- Diff matches 05 § Contract and § Backend plan: marker class, two-pass bridge, cleanup system, RefRO plus local copy in spawn, item 5 guard applied (E3 was red).
- Untouched as required: CharacterSkinChangeSystem, CharacterAnimatorSync, bakers, the despawn path; only asmdef edge added is Unity.Transforms in the two test asmdefs.
- Guardrails 1, 2, 5 respected; no IAspect; no edits under Library or generated csproj.
- Tests are real red-to-green evidence: 06 records assertion-text failures for all 10 new tests, now green, 42 old tests stay green.
- Ruling on 07 risk 1: SHOULD_FIX, not BLOCKING. Written as cr/CR-1.md for backend; goes to the ledger Open table.
- ProjectSettings.asset churn is line-ending noise, noted only.
- Sections: Ruling on 07 risks item 1 · Diff checked against plan · Test evidence.

## Ruling on 07 risks item 1

The Animator-less LogWarning fires every frame per affected character, in pass 1 and in pass 2. Ruling: SHOULD_FIX.

- Why not acceptable: before S1 the case was silent. Now it logs 60 times a second per character, with a string allocation each time, and buries real diagnostics.
- Why not BLOCKING: no current prefab hits it (0 warning lines in either gate log), the tests are unaffected, and 05 asked for "one LogWarning" without saying once-only. The ambiguity is in the plan, not the engineer's reading.
- Fix scope: one private field in CharacterAnimationBridgeSystem.cs to warn once per instance. See cr/CR-1.md.

## Diff checked against plan

- CharacterAnimationState.cs: marker class with GameObject LinkedInstance plus using UnityEngine, nothing else changed. Matches § Contract.
- CharacterAnimationBridgeSystem.cs: still SystemBase in PostEntityLifecycleGroup after SpawnHybridCharacterSkinSystem. Pass 1 uses ECB add, pass 2 mutates the class in place, TryLink looks for a sync with GetComponentInChildren before adding one (I1, I2, I3).
- CharacterAnimationBridgeCleanupSystem.cs: ISystem, UpdateAfter bridge, cached query WithNone CharacterEntity, RequireForUpdate, whole-query RemoveComponent (I4). Same shape as CharacterSkinCleanupSystem. No BurstCompile, as decided.
- SpawnHybridCharacterSkinSystem.cs: RefRO, local copy for the override, spawn helper takes `in`. The baked Prefab is never written (I5).
- HybridGameObjectSystemBase.cs: WithNone ManualCreation on the spawn query and HandleSpawns only. Despawn query and path untouched.
- Test asmdefs: Unity.Transforms added to both, an engine package, so no guardrail 2 edge. No production asmdef edited.
- Reuse: tests reuse LevelCrateTestContext, and the lookup builder is extracted to TestSupport/CharacterCrateLookupTestFactory (both old tests stay green). No reimplementation found.
- Contract alignment: no client or cross-package type exists for these components, so there is no wire-shape mismatch to check.
- Skill-call fidelity: 06 and 07 skill_calls agree with their own risks. 07 names no tradeoff that contradicts "diagnosing-bugs not called".

## Test evidence

- 06 § Red run shows every new test failing by assertion on unmodified code, not by compile or setup error. Examples: shell exists (E1), Expected 1 was 0 and Expected 1 sync was 2 (E2, E2b), DefaultVisual vs SkinVisual (E4), CurrentGait Expected 3 was 0 (P1, P2), entity count Expected 6 was 26 (P5).
- Green on fixed code in my run: E1, E2, E2b, E3, E4, the control test, P1 to P5.
- Assertions are observable behaviour (Animator parameters, instance names, entity existence, ref counts). The marker is referenced by typeof only. Nothing would still pass if the requirement changed.
- P5 asserts count, marker, instances and RefCount together, so after the fix all four are exercised.
