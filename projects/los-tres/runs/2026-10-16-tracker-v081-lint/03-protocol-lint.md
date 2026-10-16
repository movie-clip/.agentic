REPORT 2026-10-16-tracker-v081-lint/03
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    parser PASS; F-2, F-3, F-4 fixed, F-1 fixed at its named lines but its situation still conflicts (F-5, round 2); 5 scoped files, rules 1-9; 1 BLOCKING, 0 SHOULD_FIX; anchor: authoring.md, and for § Wiring a tracker the agent tools: lines, los-tres .mcp.json/settings.json/CLAUDE.md; 3 UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 (Two instructions may not disagree), continues F-1 via CR-1, round 2 of 2: SKILL.md:216 and :252-253 still direct PR actions in a tracked run where build never fired, against orchestrator.md:770-772. see § F-5
  - F-1 at its named lines: fixed. SKILL.md:215 and :236 are scoped to build fired; orchestrator.md:770-772 holds the rule; SKILL.md:218 cites it. see § Round-1 findings
  - F-2 fixed: project.md:147 is the pointer "Git and GitHub: CLAUDE.md § Git and tickets." with no rule text. see § Round-1 findings
  - F-3 fixed: authoring.md:406-407 is a pointer to orchestrator.md § 8; no stray text, the paragraph is only unwrapped at 406. see § Round-1 findings
  - F-4 fixed: "The human merges" is gone from SKILL.md:218-219; only the board-automation sentence remains. see § Round-1 findings

skill_calls:
  - none

risks:
  - Out of scope (§ 7): orchestrator.md:744-746 restates § 8:760-762 in the same file ("By default you make none, and the human commits"); two homes for one rule inside one file.
  - Still true, out of scope (repo file): los-tres/.claude/settings.json denies only `gh pr merge`, not `gh`; orchestrator.md:775-776 says the deny list removes the host's CLI.
  - Still true, out of scope (repo file): settings.json push denies match only `git push origin main` / `HEAD:main`; a bare `git push` with main as upstream is not denied.
  - UNVERIFIED: movie-clip/los-tres protects `main` (PRs only, no force-push, no deletion, no bypass), per authoring.md:418-420; not opened.
  - UNVERIFIED: Project 3 has status options Backlog, Ready, In progress, In review, Done and the repo has labels type:epic/story/ticket, per phases.md:78-79; not opened.
  - UNVERIFIED: Project 3's built-in automation moves a merged issue to Done, as SKILL.md:219 asserts; not opened.

## Orchestrator brief

Verdict FAIL on 1 BLOCKING finding; parser clean. F-2, F-3, F-4 are fixed.
F-1 is fixed at the lines it named, but the same situation (tracked run,
`build` never fired, `close` edits the repo) still has two unscoped SKILL.md
instructions that disagree with the new § 8 paragraph. Per gates.md § 4 this
continues F-1's count: Rounds row `caused by CR-1`, round 2 of 2. Owning lane:
whichever lane holds the network-file authoring order; fix is SKILL.md only.

- § F-5 — SKILL.md:216 and :252-253 vs orchestrator.md:770-772.
- § Round-1 findings — F-1..F-4, each with file:line.
- § Anchor — what each scoped file was checked against.

## F-5

- **Rule:** authoring.md § "Two instructions may not disagree".
- **Lineage:** the situation F-1 named; CR-1 scoped SKILL.md:215 and :236 as
  F-1 asked, and these two lines are what is left. gates.md § 4: a finding a
  previous round's fix leaves standing continues the count.
- **Situation:** a tracked run in which `build` does not fire and `close`
  edits the repo — phases.md:51-52 (`framing → close`, pure scope) and
  phases.md:43-49 (the stack run, `docs` writes `docs/decisions/` at close).
- **Instruction A:** orchestrator.md:770-772 — no branch, "no commit and no
  push, and whatever the `close` lane edited stays uncommitted for the human;
  the close-out report says so."
- **Instruction B1:** SKILL.md:216, unscoped row "close: `check_report.py
  <run_dir>/ --require-heads` exits 0 | mark the pull request ready, comment
  every gate verdict on it, set *reviewing*". There is no pull request, and
  the row moves the issue to *reviewing* (`In review`) with nothing to review.
- **Instruction B2:** SKILL.md:252-253, close-out report: "the exact command to
  run before committing, or, where the profile declares a tracker, the pull
  request URL". The profile declares a tracker, so the report gives a PR URL
  that does not exist instead of the commit command the human now needs, and
  never says the edits are uncommitted, which § 8 requires.
- **Consequence:** the orchestrator either opens a PR (§ 8 forbids a branch),
  sets an issue to In review on a run that built nothing, or follows § 8 and
  leaves row 216 and the report line unticked; nothing records which.
- **What would satisfy it:** scope SKILL.md:216 the way :215 and :236 are
  ("close, once `build` has fired: ..."), and reword :252-253 so the PR URL is
  given only where `build` fired in a tracked run, and otherwise the
  uncommitted paths and the commit command, citing `orchestrator.md` § 8.
  No protocol edit needed: § 8 already states the rule.

## Round-1 findings

- **F-1 — fixed at the named lines.** SKILL.md:215 row now reads "once `build`
  has fired"; SKILL.md:236 reads "tracker declared and `build` fired" and cites
  § 8; the rule's single home is orchestrator.md:770-772, matching D-1's
  direction; SKILL.md:218 cites it. Residue: § F-5.
- **F-2 — fixed.** project.md:147 is a pointer with no rule text; lint check 4
  (authoring.md:444-448) now holds for the profile's Mechanical gates.
- **F-3 — fixed.** authoring.md:406-407 reads "A tracker is optional and per
  project. `orchestrator.md` § 8 says what declaring one permits and what
  holds without one." No stray text from the docs lane's retry remains; line
  406 is unwrapped, which renders identically and is not a rule.
  orchestrator.md:760-762 is the protocol home among the two files F-3 named.
- **F-4 — fixed.** SKILL.md:218-219 holds only the citation sentence and the
  board-automation sentence; orchestrator.md:787 remains the only "never merge".

## Anchor

- **authoring.md § Wiring a tracker is part of the subject**, so it was checked
  against network and repo files, not against itself:
  - check 1: los-tres/.mcp.json declares only `github`; phases.md:75 names it.
  - check 2: all 11 `tools:` lines in plugins/agentic-core/agents/ read; none
    holds `mcp__github__*`.
  - check 3: phases.md:33 build human stop reads **yes**.
  - check 4: project.md:147 and phases.md:71-82 restate no § 8 procedure or
    limit. phases.md:82 ("The repo and the board are public.") is a fact the
    § 8 limit applies to, not the limit.
  - repo item 5: los-tres/CLAUDE.md § Git and tickets says only the
    orchestrator commits to the run's branch and only a human merges. Holds.
- **Rule 1:** no repo path in orchestrator.md § 1/§ 8 or SKILL.md; phases.md
  holds the repo-specific block. No finding.
- **Rule 2:** new § 8:770-772 text grepped across PROTOCOL.md, protocol/,
  skills/; its only other mentions are SKILL.md citations. § 7 duplicate is out
  of scope (see `risks`).
- **Rules 3, 4, 7:** no agent file in scope; parser clean; no command in the
  scoped profile files; § 8's `git` under `Bash` is the main session's.
- **Rules 5, 6:** phases.md `## Contents` matches its headings incl. Tracker;
  project.md `## Index` unchanged, Mechanical gates always-read.
- **Rule 8:** nothing found in the fix text.
- **Rule 9, other pairs checked and consistent:** phases.md:79 "a single-lane
  change gets one unlabelled issue" vs SKILL.md:212 "label them" (the skill
  reads labels from the block's mapping, SKILL.md:206); build stop phases.md:33
  vs SKILL.md:129-130, :214; CLAUDE.md § Git and tickets vs § 8.
