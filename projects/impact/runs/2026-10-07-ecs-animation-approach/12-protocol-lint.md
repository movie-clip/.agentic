REPORT 2026-10-07-ecs-animation-approach/12
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core; testing.md read end to end against protocol/authoring.md rules 1-9; both test .asmdef files read
  result:    PASS
  detail:    plugin validate passed; 0 BLOCKING, 1 SHOULD_FIX (rule 8); anchor: authoring.md rule text plus the two test .asmdef files and test-engineer.md tools line; Athena refs in both rows match; 7 UNVERIFIED premises

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SHOULD_FIX (authoring.md § Writing for the reader, tables) testing.md:76-79 — header says "References (Athena)" but rows now list Unity.Transforms and omit five other Unity refs; see § Finding SF-1
  - Fix for SF-1: keep the "References (Athena)" column Athena-only and add one bullet listing each assembly's Unity refs, or add a "References (Unity)" column listing all of them

skill_calls:
  - none

risks:
  - UNVERIFIED: Run-UnityTests.ps1 accepts -Platform, -CoreOnly and -Filter, and -CoreOnly passes -testCategory "Core" (testing.md:40-59); script not opened, outside scope
  - UNVERIFIED: Impact/Tools/TESTING.md exists and carries the Core-tagged fixture list (testing.md:51)
  - UNVERIFIED: both test assemblies declare [assembly: Category("Core")] and the manifest has no testables (testing.md:40-43)
  - UNVERIFIED: the -Filter example fixtures CrateSystemEditModeTests and CrateBootstrapPlayModeTests still exist under those names (testing.md:58-59)
  - UNVERIFIED: Run-UnityTests.ps1 -UnityPath default currently matches ProjectVersion.txt 6000.4.0f1 (testing.md:28-33)
  - UNVERIFIED: mattpocock-skills enablement location; testing.md:90 says "Impact's .claude/settings.json", project.md:148 says repo-root .claude/settings.json
  - UNVERIFIED: no test assembly references charactercontroller, gameplay or ai (testing.md:81) — confirmed for the two test asmdefs only, other *Tests* asmdefs not searched
  - 06-test.md handoff reports Run-UnityTests.ps1 returns before Unity.exe exits; this hazard is absent from testing.md Gotchas and was never filed as a pack correction
  - test-engineer.md tools line declares mcp__project__* tools; project.md:185 says Impact has no tool server. testing.md names none, so not a pack finding; noted only

## Orchestrator brief
- Verdict PASS: no blocking finding against testing.md; frontmatter parses.
- Index (lines 9-17) still names every section by its heading; conditions evaluable; hazards (Gotchas) are always-read.
- Rule 7: every command (dotnet, powershell, grep, Skill tool) is runnable under test-engineer's tools line (Read, Write, Edit, Glob, Grep, Bash, Skill, mcp__project__*).
- Rule 9: no instruction in testing.md contradicts project.md guardrails or Mechanical gates.
- Corrected rows: Athena references in both rows match the asmdefs exactly; Unity.Transforms is present in both asmdefs.
- One SHOULD_FIX, see § Finding SF-1; route to Open, not a change request.

## Finding SF-1

Rule: `authoring.md` § "Writing for the reader you actually have" — tables "make an omission visible as an empty cell". Severity SHOULD_FIX (rule 8; never FAIL alone).

File: `projects/impact/capabilities/testing.md:76-79`.

The header reads `References (Athena)`. After the close-out edit both rows also list `Unity.Transforms`, a non-Athena assembly, while the asmdefs reference further Unity assemblies the table omits:

| Assembly | Unity refs in asmdef, not in table |
|---|---|
| `Impact.EditModeTests` | Unity.Collections, Unity.Entities, Unity.Mathematics, Unity.Scenes, Unity.Entities.Hybrid |
| `Impact.PlayModeTests` | Unity.Mathematics, Unity.Entities, Unity.Collections |

A test lane reading the mixed column cannot tell whether the list is Athena-only or complete, and could read `Unity.Entities` as unavailable. The Athena entries are all correct.

Satisfied by either: (a) keep the column Athena-only and add one bullet naming the Unity references per assembly, or (b) add a `References (Unity)` column carrying the full Unity list from each asmdef.
