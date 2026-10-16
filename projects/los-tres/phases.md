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
| build | 1..n | backend, frontend, test, docs | anything that edits repo code, tests or `docs/**` — and only once the stack it needs is recorded | — |
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
