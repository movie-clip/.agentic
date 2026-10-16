REPORT 2026-10-16-tracker-v081-lint/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    parser PASS; 5 scoped files judged, rules 1-9; 4 BLOCKING, 0 SHOULD_FIX; anchor: authoring.md, and for its own § Wiring a tracker the agent tools: lines, los-tres .mcp.json/settings.json/CLAUDE.md, orchestrator.md § 8; 3 UNVERIFIED premises

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 (Two instructions may not disagree): SKILL.md:215 and :236 order a commit/push after the close lane edits the repo; SKILL.md:218 says a run that never reaches build touches no branch. see § F-1
  - BLOCKING rule 2 (One rule, one home; Wiring a tracker, lint check 4): projects/los-tres/project.md:147-149 restates the orchestrator.md § 8 limits (no lane writes git, only a human merges) in profile text. see § F-2
  - BLOCKING rule 2 (One rule, one home): protocol/authoring.md:406-407 restates the no-tracker default that protocol/orchestrator.md:760-762 owns; the same rule now lives in two protocol files. see § F-3
  - BLOCKING rule 2 (One rule, one home, skill clause): SKILL.md:218 "The human merges" restates orchestrator.md:783, two lines after SKILL.md:205-206 cites § 8 for the limits. see § F-4

skill_calls:
  - none

risks:
  - Out of scope (repo file): los-tres/.claude/settings.json denies only `gh pr merge`, not `gh`; authoring.md:416-417 requires the host CLI denied and orchestrator.md:771-772 asserts it is.
  - Out of scope (repo file): settings.json push denies match only `git push origin main` / `HEAD:main`; a bare `git push` with main as upstream is not denied. Branch protection is the stated enforcement.
  - UNVERIFIED: movie-clip/los-tres protects `main` (PRs only, no force-push, no deletion, no bypass), per authoring.md:418-420; not opened.
  - UNVERIFIED: Project 3 has status options Backlog, Ready, In progress, In review, Done and the repo has labels type:epic/story/ticket, per authoring.md:421-422; not opened.
  - UNVERIFIED: Project 3's built-in automation moves a merged issue to Done, as SKILL.md:218-219 asserts; not opened.
  - Not judged: SKILL.md:215 "commit its paths" when the close lane applies pack-corrections to <agenticRoot>/projects/los-tres/capabilities/**, a separate git repo the run's branch cannot hold.
  - Out of scope (§ 7): orchestrator.md:738-740 lists run-dir files without tracker.md; judged no conflict, since "only the run dir" governs and § 1:30-31 and § 8 name it.
  - Noted, no rule cited: SKILL.md:15-17 lists orchestrator.md §§ 1-7 and omits § 8; harmless because the same line orders a full read.

## Orchestrator brief

Verdict FAIL on 4 BLOCKING findings; parser clean. Owning lane for every
finding: whichever lane holds the network-file authoring order (the files are
under <agenticRoot>). Fix lane-independent; all four can go in one order.

- § F-1 — SKILL.md Tracker table vs its own trailer: commit after close vs
  no branch without build. The one finding that changes what the orchestrator does.
- § F-2 — project.md Mechanical gates bullet restates § 8 limits.
- § F-3 — authoring.md § Wiring a tracker opening restates § 8 opening.
- § F-4 — SKILL.md "The human merges" restates a § 8 limit.
- § Anchor — what each scoped file was checked against, and what passed.

## F-1

- **Rule:** authoring.md § "Two instructions may not disagree".
- **Where:** plugins/agentic-core/skills/orchestrate-feature/SKILL.md:215
  (row: "a lane that edited the repo returns (build, a `verify` fix, `close`) |
  commit its paths to the branch ... and push"), SKILL.md:236 (close checklist:
  "tracker declared: every repo edit committed and pushed, pull request ready"),
  against SKILL.md:218 ("A run that never reaches `build` touches no branch").
- **The situation:** a run in which `build` does not fire but the `close` lane
  edits the repo. projects/los-tres/phases.md:36 fires `close`/docs "always";
  phases.md:43-52 (§ The stack run) has docs write `docs/decisions/NNNN-*.md`
  and update `CLAUDE.md` § Stack at close with build not fired, and a pure-scope
  run (`framing → close`) edits `docs/**` the same way.
- **Consequence:** the branch is created only at the build go (SKILL.md:214),
  so in that run there is no branch to commit to. Row 215 and checklist 236 say
  commit, push and have a ready PR; line 218 says touch no branch. The
  orchestrator picks one and nothing records which: it either creates an
  unapproved branch (no build stop was given) or closes with checklist 236
  unticked. § 8 does not settle it — "no block means the human commits" covers
  only untracked projects.
- **What would satisfy it:** state which wins for a tracked run that edits the
  repo without reaching build — e.g. "the close lane's edits are left
  uncommitted for the human, and the close-out report says so", with row 215
  and checklist 236 scoped to "a run whose build fired". Because it holds in any
  run order, the rule itself belongs in orchestrator.md § 8, with SKILL.md
  citing it (authoring.md § "One rule, one home", skill paragraph); line 218 is
  currently that rule's only home.

## F-2

- **Rule:** authoring.md § "One rule, one home", applied by § "Wiring a
  tracker" lint check 4: "no profile text restates the procedure or the limits
  in `orchestrator.md` § 8" (authoring.md:448-449).
- **Where:** projects/los-tres/project.md:147-149: "No lane commits or writes to
  GitHub. Only the orchestrator commits, to the run's branch, and pushes it
  (`protocol/orchestrator.md` § 8). Only a human merges."
- **Duplicates:** orchestrator.md:767-768 ("You are the only writer: no lane is
  granted the server's tools or makes a git write") and :783 ("You never merge a
  pull request"). The lane-facing copy that authoring.md:424-426 requires already
  exists in los-tres/CLAUDE.md § Git and tickets, which project.md:6-13 says is
  in every lane's context and which this file is meant not to repeat.
- **Consequence:** three statements of one limit, in three files edited by
  three different hands; the profile copy is the one a § 8 edit will not touch.
- **What would satisfy it:** delete the bullet, or reduce it to a pointer with
  no rule text, e.g. "Git and GitHub: `CLAUDE.md` § Git and tickets." Either
  makes check 4 true of the profile. The alternative — narrowing check 4 to the
  `## Tracker` block — is an authoring.md edit and must then say why lane-facing
  profile text is exempt.

## F-3

- **Rule:** authoring.md § "One rule, one home": "no rule appears in two of
  them"; the dispatcher's rules go in `orchestrator.md`.
- **Where:** protocol/authoring.md:406-407: "Without one, a project runs exactly
  as before: no git or tracker write by any agent, and the human commits."
- **Duplicates:** protocol/orchestrator.md:760-762: "No block means no tracker:
  you make no git or tracker write, and the human commits." The rule governs
  what the orchestrator may do, so its home is orchestrator.md.
- **Consequence:** the two copies already differ in subject ("any agent" vs
  "you"); the next edit to either makes them disagree, and a reader of
  authoring.md cannot tell which is current.
- **What would satisfy it:** replace authoring.md:406-408 with a pointer only,
  e.g. "A tracker is optional and per project; `orchestrator.md` § 8 says what
  declaring one permits and what holds without one." This also drops "as
  before", which is change history (§ "Writing for the reader you actually
  have").

## F-4

- **Rule:** authoring.md § "One rule, one home", skill paragraph: a statement
  true in any run order is a rule, belongs in the protocol, and the step cites it.
- **Where:** SKILL.md:218 "The human merges"; the section opens at
  SKILL.md:205-206 by citing § 8 for "the tools and limits".
- **Duplicates:** orchestrator.md:783 ("You never merge a pull request").
- **What would satisfy it:** drop "The human merges" from SKILL.md:218; keep
  the sentence about board automation if it is wanted (see the UNVERIFIED
  bullet in `risks`). Resolving F-1 by moving line 218's first sentence into § 8
  leaves this paragraph needing only the automation note.

## Anchor

- **authoring.md § Wiring a tracker is part of the subject**, so it was checked
  against the network and repo files, not against itself (protocol-linter
  § "When the file you judge is the file you judge by"):
  - lint check 1 — `server` is a `.mcp.json` key: los-tres/.mcp.json declares
    only `github`; phases.md:75 names `github`. Holds.
  - lint check 2 — no `tools:` line holds `mcp__github__*`: all 11 files in
    plugins/agentic-core/agents/ read; none does. Holds.
  - lint check 3 — build human stop reads yes: phases.md:33. Holds.
  - lint check 4 — no profile restatement of § 8: violated by project.md:147-149
    (F-2), which is part of the same edit set.
  - repo-side items: 1 holds (token from `${GITHUB_PERSONAL_ACCESS_TOKEN}`);
    2 partly (see `risks`); 3 and 4 UNVERIFIED; 5 holds (CLAUDE.md § Git and
    tickets says the orchestrator commits to the run's branch and only a human
    merges).
  - the template block (authoring.md:433-443) has the six keys phases.md:73-80
    uses, in the same order.
- **Rule 1 (layers):** orchestrator.md § 1/§ 8 name no repo, host CLI only by
  role; SKILL.md Tracker table reads statuses and labels by role (*new*,
  *building*, *reviewing*) from the block. No finding.
- **Rules 3, 4, 7:** no agent file in scope; parser clean. The commands § 8
  gives the orchestrator (`git` under `Bash`, `mcp__github__*`) are the main
  session's, not a lane's. No finding.
- **Rules 5, 6:** phases.md `## Contents` matches its five headings, Tracker
  included; authoring.md `## Contents` lists § Wiring a tracker; project.md
  `## Index` unchanged and its always-read set still covers Mechanical gates.
  No finding.
- **Rule 9, other pairs checked and found consistent:** build stop (phases.md:33
  vs SKILL.md:129-130, :214 vs § 8); intake server check (SKILL.md:44, :71-73 vs
  orchestrator.md:776-779); human-only statuses (phases.md:78 vs § 8:788 vs
  SKILL.md never setting Ready/Done); tracker.md location (§ 1:30-31 vs
  § 8:794-806 vs SKILL.md:207); close order (SKILL.md:216 vs :235-237; the
  sweep does not require CLOSED); CLAUDE.md § Git and tickets vs block.
