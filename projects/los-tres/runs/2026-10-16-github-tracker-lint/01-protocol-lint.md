REPORT 2026-10-16-github-tracker-lint/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    parser PASS; 5 BLOCKING (rule 1 x1, rule 9 x4, one also rule 2), 1 SHOULD_FIX (rule 8); anchor: authoring.md + orchestrator.md, producer.md, tech-lead.md, story-author.md, gates.md, check_report.py, ledger.py; 3 UNVERIFIED premises

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1 (rule 9, rule 2): SKILL.md:228 grants commit only, apart from the run-dir boundary it excepts (SKILL.md:22, orchestrator.md § 7); phases.md:91-98 also orders branch, push, PR and issue writes. see § Findings
  - BLOCKING F2 (rule 1): phases.md:85 adds `issue:` and `pr:` to the ledger header, a shape owned by orchestrator.md § 1; ledger.py SETTABLE rejects both on --set. see § Findings
  - BLOCKING F3 (rule 9): phases.md:94 makes build wait for Ready or a human go, but the build row at phases.md:33 says Human stop "—", the column check_report.py reads. see § Findings
  - BLOCKING F4 (rule 9): project.md:147 limits commits to "a story branch"; phases.md:83 makes a branch for every run that builds, including plain-issue runs with no story. see § Findings
  - BLOCKING F5 (rule 9): phases.md:75-76 says no lane runs `git`; producer.md:50-57 tells producer to run `git log` and tech-lead.md:14 to read git state. see § Findings
  - SHOULD_FIX S1 (rule 8): the bullet at phases.md:102-104 carries four prohibitions plus an enforcement note in one bullet over 200 characters; split it, one limit per bullet.

skill_calls:
  - none

risks:
  - UNVERIFIED: the GitHub MCP tool names and toolsets (`issue_read`, sub-issue linking, Project status, draft-to-ready) exist under X-MCP-Toolsets issues,projects,pull_requests; not opened.
  - UNVERIFIED: GitHub Project 3 exists, is owned by user `movie-clip`, and has the five Status values phases.md:82 names.
  - UNVERIFIED: phases.md:107 says the repo and the board are public; not confirmed.
  - Design gap, not an authoring rule: a run with `issue: none` that skips framing has no issue for the Ready check, the `<issue>-<slug>` branch name, or `Closes #`.
  - Outside scope: SKILL.md:226 still reports "the exact command to run before committing", which no longer fits once phases.md lets the orchestrator commit.
  - Outside scope: README.md:162 and ARCHITECTURE.md:376 still say "No agent commits" with no opt-in exception.
  - Outside scope: story-author.md:114 says "the human commits"; now false for los-tres, but the action it governs (no ticket orders a commit) is unchanged.

## Orchestrator brief

Verdict FAIL. Five BLOCKING findings, one SHOULD_FIX. Every fix is a wording
change, and none needs a code change.
- § Findings: F1-F5 and S1, each with the rule, file:line and what would
  satisfy it. F1's fix touches `protocol/orchestrator.md` § 7, which is outside
  this order's three files. F2's fix may touch `scripts/ledger.py`.
- § Checked, not contradictions: story-author.md, tech-lead.md, gates.md,
  PROTOCOL.md, layer placement, Contents, tool grants.

## Findings

### F1 — the orchestrator's exception is split from its rule, and covers less than phases.md orders (rule 9; rule 2)

- Rule: authoring.md § "Two instructions may not disagree": "A rule and its
  exception are one fact". Also § "One rule, one home": "A skill is not a fifth
  place to put a rule".
- The rule: `orchestrator.md` § 7 says "What the main session writes. Only the
  run dir … Every other edit to the bound repo or the network is a work order."
  `SKILL.md:22-23` repeats it: "In the main session you write only the run
  dir."
- The exception: it sits only at `SKILL.md:228-229`, 200 lines away, and it
  covers **commit** only: "You never commit, unless the project's `phases.md`
  grants it and names the branch".
- What phases.md orders: `phases.md:94-98` has the orchestrator create a
  branch, push, open a pull request, mark it ready, comment on it, create and
  label issues, and move board status. The skill's grant covers none of these.
  The boundary in § 7 and at SKILL.md:22 forbids every one of them, because
  each is a write outside the run dir.
- Why it matters: the orchestrator reads all three files. It either refuses the
  procedure or ignores the boundary, and nothing records which it chose.
- Rule 2: "a project may grant the orchestrator git and tracker writes" stays
  true whatever order the run happens in, so by the skill test it is a rule.
  Its home is `orchestrator.md` § 7, not a step in the skill.
- What would satisfy it:
  1. Add one sentence to `orchestrator.md` § 7: git and tracker writes
     (commit, branch, push, pull request, issue, comment, board) are outside
     the run dir too. Make none of them unless the project's `phases.md` grants
     them and names the branch. Never merge.
  2. Change `SKILL.md:228` to cite § 7 instead of restating the rule, e.g.
     "Commits and tracker writes: `orchestrator.md` § 7."
  3. At `SKILL.md:22`, either point at that exception or leave the line
     unchanged, since it already cites § 7.
  `orchestrator.md` is outside this order's file list, so the producer must
  widen scope.

### F2 — a capability file extends a protocol shape (rule 1)

- Rule: authoring.md § "The four-layer split". The Capability layer "must not
  contain … message shapes".
- `phases.md:85`: `| Ledger header | issue: #<n> | none and pr: #<n> | none,
  beside story: |`.
- The ledger header is defined in `orchestrator.md` § 1. `scripts/ledger.py:61`
  (`HEADER_ORDER`) and `:68` (`SETTABLE`) do not contain these fields.
  `orchestrator.md` § "One call for the fields that move on every head" tells
  the orchestrator to move header fields with `ledger.py --set`, and that
  command raises "is not a settable header field" for `issue` and `pr`.
- What would satisfy it, either of:
  - Drop the row. Record the issue and the pull request somewhere the protocol
    already gives free text: a `decisions.md` entry, or `next:`/Artifacts
    prose.
  - Add one optional, project-agnostic header field (e.g. `tracker:`) to
    `orchestrator.md` § 1, and to `HEADER_ORDER` and `SETTABLE` in
    `ledger.py`. phases.md then only says what goes in it.

### F3 — a human stop at build that the Phases table does not declare (rule 9)

- Rule: authoring.md § "Two instructions may not disagree".
- `phases.md:33`: the build row's Human stop column reads `—`.
- `phases.md:94`: build fires only when "the issue must be **Ready**, or the
  human says go in this session — record which in `decisions.md`". In practice
  that is a conditional human stop.
- Why it matters: `orchestrator.md` § 3 step 4 stops only for "a human stop"
  the phase carries. `check_report.py:778` and `:947` take the stop set from
  the table's last column. The loop and the close-out sweep both read "no
  stop", and the Git section says stop.
- What would satisfy it: write the condition into the build row's Human stop
  cell, e.g. "**yes**, unless the issue is already Ready". Point phases.md:94
  at that cell instead of stating the stop itself.

### F4 — "story branch" versus a branch per run that builds (rule 9)

- Rule: authoring.md § "Two instructions may not disagree".
- `project.md:147-148`: "Only the orchestrator commits, to a story branch".
- `phases.md:83`: the branch is "`<issue>-<slug>` … one per run that builds".
  `phases.md:92` creates "one plain issue for a single-lane change". phases.md
  § "When the brief is the specification" says most single-lane runs have no
  story.
- Why it matters: on a run with no story, the orchestrator reads two answers to
  "may I commit here".
- What would satisfy it: in project.md, replace "to a story branch" with "to
  the run's branch".

### F5 — "no lane runs git" versus lanes told to run it (rule 9)

- Rule: authoring.md § "Two instructions may not disagree". Also: "An exception
  may not be broader than the section that grants it."
- `phases.md:75-76`: "no lane runs `git` or `gh`".
- `producer.md:50-57`: "**Use git for it.** You have `Bash` … `git log
  --oneline -S…`".
- `tech-lead.md:14`: "and read git state". tech-lead's tools are `Read, Write,
  Glob, Grep, Bash, Skill, mcp__project__run_tests, mcp__project__check_gates`.
- Why it matters: the orchestrator writes work orders from phases.md. If it
  puts "no git" in a producer's `non_goals`, that lane gets two instructions
  pointing opposite ways. The owner's intent concerns git and GitHub *writes*.
- What would satisfy it: reword phases.md:75-76 to "no lane writes to git or
  GitHub: no commit, branch, push, issue or pull request. Read-only `git log`
  or `git diff` by a lane with `Bash` is unchanged."

### S1 — one bullet, five facts (rule 8, SHOULD_FIX)

- `phases.md:102-104` carries four facts in one bullet: never merge, never push
  to main, never force-push, never delete a branch you did not create. It adds
  the deny-list note on top and runs over 200 characters.
- What would satisfy it: split it into one bullet per limit, with the deny-list
  sentence as its own line.

## Checked, not contradictions

| File:line | Text | Why it holds, given that the grant is to the orchestrator only |
|---|---|---|
| story-author.md:112-115 | "No ticket instructs anyone to commit … the human commits" | The action is unchanged: tickets go to lanes, and lanes still never commit. The clause "the human commits" is now inaccurate for los-tres (risks), but it directs nothing. |
| tech-lead.md:159 | "Commits. Never." | tech-lead is a lane. project.md:147 still says no lane commits. |
| gates.md § 3 | no bypassing a hook; a blocked commit means fixing the work | This now also binds the orchestrator's commits. It agrees with the edit. |
| PROTOCOL.md:186-199, orchestrator.md:740 | `git rm` / `git mv` are the human's | Deletes and renames are not covered by the grant, and phases.md does not claim them. |
| project.md:127-131 | No project tool server; `github` is orchestrator-only | Accurate. Every agent file has an explicit `tools:` allowlist with no `mcp__github__*`, and the parser passed, so no lane falls back to the parent roster. |
| phases.md placement | the GitHub procedure | Correct layer. It is project-specific (Project 3, labels, branch pattern) and has one reader, the orchestrator. It belongs in phases.md, not project.md and not the skill. |
| phases.md:17-18 | Contents bullet | Matches the heading `## Git and the tracker`. phases.md is read in full, so `## Contents` is the right form. |
| SKILL.md:228 | "phases.md grants it and names the branch" | Rule 1 holds: it names no lane, project or branch, and cites the profile. The defect is F1. |
| los-tres/.claude/settings.json | deny list | Opened. It denies merge via MCP and `gh`, pushes to `main`, and `--force`/`-f`, matching phases.md:102-104's "denies the commands". |
