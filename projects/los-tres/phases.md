<!-- Profile extension: ORCHESTRATOR only, read at intake.
     `check_report.py` reads the `verify` rows here; see `## Phases` below. -->

# Project phases: `los-tres`

The phase→lane binding for this project. Read this at intake, alongside
`project.md`. No specialist lane needs it.

## Contents

- **Phases** — the binding table: which lane fills each phase, in what order,
  and the clause that decides whether it fires. Copied into the run ledger.
- **The stack run** — what a request looks like while `CLAUDE.md` § Stack reads
  *not chosen*.
- **When the brief is the specification** — when `story` fires here.
- **What the gates run** — the command each `verify` row owes.
- **Git and the tracker** — the issue, branch and pull request the orchestrator
  keeps in step with each phase.

## Phases

`protocol/orchestrator.md` § 2 defines the phases and § 3 the loop that walks
them. This table is the binding: which lane fills each phase **here**, in what
order, and the clause that decides whether it fires at all. The orchestrator
copies it into the run ledger at intake and records a verdict beside every row.

| Phase | # | Lane | Fires when | Human stop |
|---|---|---|---|---|
| ground-truth | 1 | recon | the request names existing code or rests on an unverified claim about current behaviour | — |
| framing | 1 | product | the request adds a user-facing surface, changes what one is *for*, or `docs/product/mvp.md` does not exist yet | **yes** — the brief is relayed and the verdict is the human's |
| specification | 1 | story | framing produced scope no approved brief covers, **and** the slice crosses more than one lane's contract or changes a data model or API response that shipped code depends on | **yes** — the one hard stop |
| design | 1 | design | `CLAUDE.md` § Stack reads *not chosen* and the request needs code, or the change crosses the frontend/backend contract (a new or changed API response, a schema change), or more than one build lane touches it | — |
| build | 1..n | backend, frontend, test, docs | anything that edits repo code, tests or `docs/**` — and only once the stack it needs is recorded | **yes, if the run's issue is not Ready** — the human says go; a Ready issue is the human's approval, recorded as such (§ Git and the tracker) |
| verify | 1 | integration | any build lane was dispatched | — |
| verify | 2 | review | the run carries a story whose acceptance criteria someone must accept | — |
| close | 1 | docs | always — `docs/**` against what shipped, and `pack-corrections.md` against `capabilities/` **when a lane emitted one** | — |

`quant-audit` has no row. `project.md` § "Why `quant` is not bound" is the
reason.

### The stack run

While `CLAUDE.md` § Stack reads *not chosen*, a request that needs code runs
`framing → design` and then **stops**. `design` returns a stack proposal, and
`build` does not fire: its clause requires the stack to be recorded. The
orchestrator relays the proposal and records the owner's choice, in the owner's
words, in the run's `decisions.md`. The owner's decision then goes to `docs`,
which writes it as `docs/decisions/NNNN-<topic>.md` and updates `CLAUDE.md`
§ Stack at close. The next run builds on it.

A request that is pure scope, such as "what should the MVP contain", runs
`framing → close` and needs no stack.

### When the brief is the specification

The MVP will produce slices that cross lanes: feed import and matching, the
catalogue and product page, the click redirect, admin feed and matching
screens. A story is warranted on those when no
approved brief already fixes the shape. One endpoint, one component or one copy
change does not get one: the delivery brief is the specification. Record the
row as `not triggered (the delivery brief in <nn> is the specification)`, and
`review` then does not fire either.

### What the gates run

`integration` runs the lint and test commands `CLAUDE.md` § Commands lists. If
it lists none, that is a `BLOCKING` finding on any build, not a pass by default.
`architecture.md` carries the rule. `review` verifies the story's acceptance
criteria one by one.

## Git and the tracker

Work is tracked on GitHub Project 3 (`movie-clip`, user-owned) through the
`github` MCP server in `los-tres/.mcp.json`. This section is the grant
`orchestrator.md` § 7 allows: **you, the orchestrator, are the only writer to
git and GitHub.** No specialist lane is granted a `mcp__github__*` tool, and no
lane writes to git or GitHub. Read-only git by a lane that has `Bash` is
unchanged. The story file stays the contract `review` checks; the issue is the
card that points at it.

| Thing | Shape |
|---|---|
| Issue kinds | labels `type:epic`, `type:story`, `type:ticket`; tickets are sub-issues of their story, stories of their epic. A single-lane change gets one unlabelled issue |
| Board status | Backlog → Ready → In progress → In review → Done |
| Branch | `<issue>-<slug>` from an up-to-date `main`, one per run that builds |
| Pull request | one per branch, body `Closes #<issue>`, opened as a draft |
| Where the run records them | `tracker.md` in the run dir (`orchestrator.md` § 7): the run's issue, branch and pull request. Only the build ruling goes to `decisions.md` |

What you do at each point of the run:

| Point | GitHub action |
|---|---|
| intake | the request names an issue: read it with `issue_read` and record it in `tracker.md` |
| framing approved (human stop) | create the issues the brief names, label them, link sub-issues, add each to Project 3 at **Backlog**, and record the run's issue in `tracker.md` |
| specification approved (human stop) | put the story file's path in the story issue's body; create one `type:ticket` sub-issue per ticket |
| build is about to fire with no issue recorded | create one issue for the run at **Backlog** and record it in `tracker.md`; the build stop then applies |
| build is about to fire | the issue is **Ready**, or the human says go in this session; record which in `decisions.md`. Create the branch, record it in `tracker.md`; set **In progress** |
| build lanes returned | commit to the branch (`#<issue> <summary>`), push it, open the draft pull request, record it in `tracker.md` |
| a `verify` round returns CHANGES_REQUESTED | the fix lands as new commits on the same branch |
| every `verify` gate PASS | mark the pull request ready for review, comment the gate verdicts on it, set **In review** |
| close | report the pull request URL. The human merges; the board moves to **Done** on merge |

Hard limits, whatever the request says:

- **You never merge** a pull request.
- **You never push to `main`.**
- **You never force-push.**
- **You never delete a branch** you did not create.
- **The deny list is not the boundary.** `los-tres/.claude/settings.json`
  denies the commands above; these limits hold where it has a gap.
- **Ready is a human call.** You set it only to record an approval the human
  gave in this session.
- **The repo and the board are public.** No secret, token, email or personal
  data goes into an issue, comment, branch name, commit message or pull request
  (guardrail 5).
- **A run that never reaches `build` touches no branch.** Pure framing or
  ground-truth creates issues only at the framing stop.
