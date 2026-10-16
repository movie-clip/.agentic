REPORT 2026-10-07-ecs-animation-approach/10
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd Impact; dotnet build Impact.sln (also --no-incremental); Run-UnityTests.ps1 -Platform EditMode -CoreOnly; Run-UnityTests.ps1 -Platform PlayMode -CoreOnly
  result:    PASS
  detail:    dotnet build 0 errors (17 warnings incremental, 36 with --no-incremental, all MSB3277). EditMode total=45 passed=45 failed=0. PlayMode total=8 passed=8 failed=0. Read from fresh result XML (12:46:53 and 12:47:23). 0 "has no Animator" lines in either. Anchor: CR-1 text and the HEAD bridge source, not 09's own report.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CR-1 is satisfied. Close it in the ledger Open table; no CR-2 written and no re-run of this gate needed
  - Run-UnityTests.ps1 returns before Unity.exe exits (GUI exe, no wait), so its exit code and tail output are not a result. Poll for Unity.exe to exit, then read the XML mtime and totals. A second launch while one is running collides on the project lock

skill_calls:
  - mattpocock-skills:codebase-design — called, before the consistency judgment in § CR-1 judgement. Applied: the bridge module keeps sole ownership of link and warn state, interface unchanged, no new seam

risks:
  - The warn-once path itself is not exercised by any test (both gate logs show 0 warnings). CR-1 rests on code reading plus the unchanged green suite, as 09 disclosed. CR-1 required no new test
  - The Dictionary<Entity, GameObject> field has no precedent elsewhere in athena.shared, athena.gameplay or athena.charactercontroller (grep). Accepted: CR-1 named this shape and the state is private to one SystemBase

## Orchestrator brief
- Verdict: PASS. CR-1 satisfied, S1 not regressed. No CR-2.
- Gates run by me: dotnet build 0 errors; EditMode 45/45; PlayMode 8/8, from fresh XML.
- Scope: the bridge system is the only non-meta file under Assets/Tests and Packages newer than 08. Marker, state, other systems and asmdefs untouched.
- Ruling on 09 risks item 1 (warned instance not re-probed): acceptable. See § Ruling on 09 risks item 1.
- Sections: CR-1 judgement · Ruling on 09 risks item 1.

## CR-1 judgement

Read against CR-1 "What satisfies it", file `CharacterAnimationBridgeSystem.cs` as it stands.

- Once per instance. TryLink writes `warnedInstances[entity] = instance` immediately before the single LogWarning. Pass 1 and pass 2 both `continue` on `IsAlreadyWarned(entity, Instance)` before calling TryLink again. A swapped-in instance differs by reference, so it is probed and warns once more, or links normally.
- Link ownership stays in this system. The warned map is a private field of the bridge. CharacterSkinChangeSystem, the marker class and CharacterAnimationState are not touched (mtimes 12:25, before 08 at 12:32).
- Pass 1 and pass 2 link behaviour unchanged. The pass-2 order `Instance == null`, then `marker.LinkedInstance == Instance`, then `IsAlreadyWarned` keeps the linked steady state at one reference compare per character. The dictionary is not consulted for linked characters.
- No unbounded growth. One entry per entity, overwritten on a new warned instance. `TrimWarnedInstances` drops entries whose entity no longer exists (`EntityManager.Exists` checks version, so reused indices are covered), has lost `CharacterEntity` (the cleanup shell), or whose GameObject is destroyed.
- No retention of destroyed GameObjects. A destroyed instance compares equal to null under Unity's operator, so it is removed in the trim at the end of the same OnUpdate it is first seen. At most one frame of managed-wrapper retention, no native memory. A live warned instance is held only while its character uses it. `OnDestroy` clears both collections.
- No per-frame allocation on the warned path. The path is one `Dictionary<Entity,GameObject>.TryGetValue` (Entity is IEquatable, no boxing) plus the trim loop. The trim uses the struct enumerator over the dictionary and a reused List, and is skipped when the map is empty. The interpolated warning string is built once per instance. The Temp `EntityCommandBuffer` was already there at HEAD.
- Touched only that file. Files under Assets/Tests and Packages newer than 08-integration.md: the bridge system only (`find -newer`, `.meta` excluded). The list of modified and untracked paths in `git status` is the same set 08 reviewed.
- Guardrails: no asmdef, Library, generated csproj or IAspect change. TryLink going from private static to private instance has no external callers.

## Ruling on 09 risks item 1

Acceptable. An instance already warned about is not probed again, so an Animator added to it later at runtime is not linked.

- CR-1 prescribed exactly this ("remember the last instance already warned about"). Re-probing is what produced the per-frame cost, so the two cannot both hold.
- The case is not reachable in this repo. The only `AddComponent<Animator>` calls are in test support, at construction time, before the bridge sees the instance. No production code adds an Animator after spawn.
- The relink trigger the plan defines is "presentation instance changed" (05 I1 to I5), not "components on the instance changed". A swap to any new instance, including one that gains an Animator, is still probed and linked. That contract is intact.
- HEAD did re-probe an Animator-less instance every frame, silently, so a late Animator would have linked at HEAD. That is a real difference, but it was incidental to the old behaviour and is the cost of the fix CR-1 asked for. A prefab that needs its Animator ready at spawn time is already the setup the Viking skins have.
