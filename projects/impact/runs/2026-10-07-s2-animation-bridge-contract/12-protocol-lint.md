REPORT 2026-10-07-s2-animation-bridge-contract/12
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core; edited sections of testing.md and backend.md read against authoring.md rules 1-9, project.md, AGENTS.md, Run-UnityTests.ps1
  result:    PASS
  detail:    plugin validate passed; 1 BLOCKING (rule 9), 3 SHOULD_FIX (rule 8); anchor: authoring.md rule text, Run-UnityTests.ps1:71-79, test/backend tools lines, project.md:187-188, AGENTS.md:48-75; 7 UNVERIFIED premises

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F-1 (authoring.md § Two instructions may not disagree) testing.md:39 vs project.md:187-188 and testing.md:77-80; see § Finding F-1
  - Fix for F-1, docs lane, testing.md:34-41 only: scope the no-pipe sentence to PowerShell, and state that Run-UnityTests.ps1 wins over AGENTS.md's raw Unity.exe lines for test runs
  - SHOULD_FIX SF-2 (authoring.md § Writing for the reader, one fact per bullet) testing.md:34-41 carries five facts; split off the TestResults-*.xml-tracked fact as its own bullet; see § Should-fix findings
  - SHOULD_FIX SF-3 (authoring.md § Writing for the reader, cut history) testing.md:37-39 "on every run in the S2 run" is provenance; drop it, keep the mechanism and the instruction
  - SHOULD_FIX SF-4 (authoring.md § Writing for the reader, one fact per bullet) testing.md:42-45 carries two facts; split the compile-error presentation (exit 1, ~12 s, grep error CS) into its own bullet
  - Carried SF-1 now sits at testing.md:91-94 (line shift); the new TimeData bullet at 102-104 relies on Unity.Entities, which that table omits. The SF-1 fix should list Unity.Entities explicitly

skill_calls:
  - none

risks:
  - The Git Bash backslash fact (backend.md:152-155) applies to test-engineer too, whose shell is the same Bash; testing.md:61-74 still shows .\Tools\ forms. Unedited section, so not in the verdict
  - backend.md:113 gives the script call with no shell prefix, so the forward-slash rule sits only in Definition of done; findable because that section is always-read, so not a finding
  - testing.md:46-48 qualifies testing.md:24-25 rather than contradicting it; both still say run dotnet build first, so no rule 9 finding. They are 20 lines apart
  - UNVERIFIED: this project's NUnit has no Is.AnyOf, and Does.Contain on an array works as written (testing.md:42-43)
  - UNVERIFIED: a compile error shows as "Scripts have compiler errors", exit 1, after about 12 s (testing.md:44-45)
  - UNVERIFIED: dotnet build Impact.sln cannot see new test files until a Unity run regenerates the csproj (testing.md:46-48)
  - UNVERIFIED: TimeData is in namespace Unity.Core in the Unity.Entities assembly, and World.SetTime(new TimeData(elapsed, dt)) is the API (testing.md:102-104)
  - UNVERIFIED: TestResults-*.xml are tracked in git (testing.md:39-41); repo git index not in scope
  - UNVERIFIED: from Git Bash, .\Tools\... loses its backslashes and fails with exit 127 or 1 (backend.md:152-155)
  - UNVERIFIED: an unpiped Unity.exe call returns early under PowerShell; the script's own comment (Run-UnityTests.ps1:71-72) says so, not tested here
  - Confirmed: Run-UnityTests.ps1:73 pipes through Out-Default, :79 exits with $LASTEXITCODE, so the cited range 71-79 is right; -UnityPath default (line 11) matches 6000.4.0f1

## Orchestrator brief
- Verdict FAIL on one BLOCKING rule 9 finding, see § Finding F-1. Route a change request to `docs`, scope testing.md:34-41.
- Frontmatter parses (`claude plugin validate` passed).
- Rule 5/6: both Index blocks are unchanged and still name every section; the new bullets sit in always-read sections (Gotchas, Definition of done) except TimeData, which sits in a conditional section whose condition is evaluable.
- Rule 7: every new command (powershell, dotnet, grep) runs under the owning lanes' `tools:` lines, which both include Bash.
- Rule 1: no message shape or role rule entered either pack.
- Three SHOULD_FIX (rule 8), see § Should-fix findings; they become `Open` rows.
- Prior SF-1 is carried, now at testing.md:91-94; the TimeData bullet adds weight to it.

## Finding F-1

**Rule:** `authoring.md` § "Two instructions may not disagree" — BLOCKING.

**Where:** `projects/impact/capabilities/testing.md:39`, "Do not call `Unity.exe` directly without a pipe."

**What it disagrees with,** all read by `test-engineer` together:

| Location | Instruction |
|---|---|
| `project.md:187-188` (Mechanical gates, always-read) | "Every lane runs the plain `dotnet`/`Unity.exe`/PowerShell commands named in `AGENTS.md` ..." |
| `AGENTS.md:48`, `:70-75` (in every lane's context, per `project.md:8-10`) | raw `Unity.exe -batchmode ... -logFile -` commands, no pipe |
| `testing.md:77-80` (same pack) | presents AGENTS.md's raw `-testFilter` batchmode call as the same mechanism the script wraps |

A test lane that needs one fixture, or the batchmode compile check guardrail 3 names (`project.md:61`, which points at `AGENTS.md` § Build/Compile Commands), is told by the profile to run AGENTS.md's unpiped `Unity.exe` line, and by its pack not to. Nothing says which one wins.

The sentence is also broader than its own premise. The reason it gives, at testing.md:36-37, is PowerShell's handling of a GUI program. The lanes' shell is Git Bash, which the sentence does not mention.

**What would satisfy it:** reword testing.md:39 so it says which case it covers and which instruction wins. For example: "From PowerShell, never call `Unity.exe` without `| Out-Default`. For test runs, use `Run-UnityTests.ps1` rather than AGENTS.md's raw `Unity.exe` lines; this pack wins over them." Either half on its own removes the disagreement. The edit stays inside `testing.md`. `project.md` does not have to change if the pack states that it wins.

## Should-fix findings

| ID | Rule | Location | Finding | Satisfied by |
|---|---|---|---|---|
| SF-2 | § Writing for the reader — one fact per bullet | testing.md:34-41 | five facts: waits/returns exit code, the mechanism, the S2 observation, the no-pipe instruction, TestResults tracked in git | move "TestResults-*.xml are tracked and show modified after every run" to its own bullet |
| SF-3 | § Writing for the reader — cut history | testing.md:37-39 | "Run in the foreground it exited after Unity ended on every run in the S2 run" is how the fact was found | delete the sentence; the script line reference already proves it |
| SF-4 | § Writing for the reader — one fact per bullet | testing.md:42-45 | the Is.AnyOf fact and how a compile error presents in the log | split into two bullets |
