REPORT 2026-10-16-github-tracker-lint/02
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    parser PASS; 01 F3 F4 F5 S1 resolved; 2 BLOCKING (rule 9 x2), round 2 of F1 and F2; anchor: authoring.md + orchestrator.md § 1 § 5 § 7, producer.md, tech-lead.md, check_report.py, ledger.py; 2 UNVERIFIED premises

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F6 (rule 9; round 2 of F2): phases.md "Where the run records them" logs issue and PR numbers in decisions.md, which orchestrator.md § 5 reserves for human rulings in their words. see § Findings
  - BLOCKING F7 (rule 9; round 2 of F1): phases.md orders writes outside the set orchestrator.md § 7 lets a project grant, including the issue-body edit, PR comment, labels, sub-issue links and branch creation. see § Findings
  - Lineage for the Rounds table: F6 is caused by the F2 fix and F7 by the F1 fix. Both are now at round 2 of 2, so another failure on either goes to the human (gates.md § 4).

skill_calls:
  - none

risks:
  - UNVERIFIED by this lane: the GitHub MCP tool coverage (issue_read, issue_write, sub_issue_write, projects_write, update_pull_request); the 02 order says the orchestrator verified it.
  - UNVERIFIED by this lane: Project 3 under `movie-clip`, its five Status values, and the public repo and board; the 02 order says the orchestrator verified them.
  - check_report.py `_stop_lanes` counts a stop only when the cell contains "yes"; the new build cell has no "yes", so close-out never demands a ruling for the conditional build stop.
  - Out of lint scope, not re-judged: README.md:162 and ARCHITECTURE.md:~376 were reworded by the orchestrator.

## Orchestrator brief

Verdict FAIL. Two BLOCKING findings, both caused by round-1 fixes, so each
continues its parent's count (round 2 of 2).
- § Findings: F6 (decisions.md repurposed) and F7 (§ 7's grant is narrower
  than phases.md's writes). Each gives the file:line, why it matters and what
  would satisfy it.
- § Resolved from 01: the status of each round-1 finding.

## Findings

### F6 — decisions.md used as a tracker log (rule 9; round 2 of F2)

- Rule: authoring.md § "Two instructions may not disagree". Both texts below
  are read by the orchestrator.
- `orchestrator.md` § 5 ("The human's ruling is a path too") says decisions.md
  holds "One entry per decision the human actually resolved, the ruling in
  **their words**, and the artifact and section that raised it". The shape
  given there has `open decision:`, `raised by:`, `ruling:` and `by:`.
- phases.md, Shape table row "Where the run records them", says "`decisions.md`:
  one entry naming the issue when it is set, one naming the pull request when
  it is opened". The intake, framing, no-issue-build and build-returned rows
  all say "record it".
- An issue read at intake and a pull request the orchestrator opens are not
  human rulings. Neither has a `ruling:` or `by:`.
- Why it matters:
  - The orchestrator gets two contradictory instructions for the same file.
  - `check_report.py` `check_decisions` passes as soon as decisions.md is
    non-empty. A PR entry therefore satisfies the check for a framing or
    specification stop whose ruling was never written down. That disables the
    one mechanical check on the hard stop.
- What would satisfy it, either of:
  - (a) `orchestrator.md` § 7's list of run-dir files names a `tracker.md`,
    written only where phases.md grants tracker writes. phases.md records the
    issue and the PR there.
  - (b) An optional, project-agnostic `tracker:` header field in
    `orchestrator.md` § 1, added to `HEADER_ORDER` and `SETTABLE` in
    `scripts/ledger.py`.
  The Ready-or-go ruling at build is a genuine human ruling and stays in
  decisions.md.

### F7 — the grant is broader than the section that allows it (rule 9; round 2 of F1)

- Rule: authoring.md § "Two instructions may not disagree": "An exception may
  not be broader than the section that grants it."
- `orchestrator.md` § 7 says a project "may grant you a named set: commit and
  push to the run's branch, open and update its pull request, and create or
  move issues on its tracker. You make only the writes it names".
- phases.md also orders writes outside that set:
  - "put the story file's path in the story issue's body" (specification
    approved row) edits an existing issue.
  - "comment the gate verdicts on it" (every verify gate PASS row) comments on
    a pull request.
  - "label them, link sub-issues" (framing approved row).
  - "Create the branch" (build is about to fire row).
- Why it matters: the orchestrator reads § 7 as the outer limit. It then either
  skips these steps or treats the phases.md grant as wider than the protocol
  allows, and nothing records which.
- What would satisfy it: widen § 7's list to "create the run's branch, commit
  and push to it; open, update and comment on its pull request; create, edit,
  label, link, comment on and move issues on its tracker". Alternatively, make
  the list illustrative and say the phases.md list, minus the excluded writes,
  is the bound.

## Resolved from 01

| 01 finding | Status | Evidence |
|---|---|---|
| F1 boundary split from its exception | resolved, with the remainder raised as F7 | orchestrator.md § 7 now holds the grant; SKILL.md:22-23 and :229-230 cite § 7 rather than restating it |
| F2 ledger header extended | resolved, with the remainder raised as F6 | the ledger-header row is gone from phases.md |
| F3 undeclared build stop | resolved | the build row's Human stop cell now names the condition (see the risks bullet about the parser) |
| F4 story branch | resolved | project.md:147 reads "to the run's branch" |
| F5 no lane runs git | resolved | phases.md reads "no lane writes to git or GitHub. Read-only git by a lane that has `Bash` is unchanged." |
| S1 long bullet | resolved | the hard limits are one per bullet |
