<!-- Profile extension: ORCHESTRATOR only, read at intake.
     `check_report.py` reads the `verify` rows here; see `## Phases` below. -->

# Project phases: `datoro`

The phase→lane binding for this project. Read this at intake, alongside
`project.md`. No specialist lane needs it.

## Contents

- **Phases** — the binding table: which lane fills each phase, in what order,
  and the clause that decides whether it fires. Copied into the run ledger.
- **When the brief is the specification** — why `story` is the exception here,
  not the rule.
- **Why `design` fires more often than it looks like it should** — the
  frontend/backend seam this repo crosses on an ordinary feature.
- **What the gates run** — the command each `verify` row owes.
- **The short run** — what most work in this repo actually looks like.

## Phases

`protocol/orchestrator.md` § 2 defines the phases and § 3 the loop that walks
them. This table is the binding: which lane fills each phase **here**, in what
order, and the clause that decides whether it fires at all. The orchestrator
copies it into the run ledger at intake and records a verdict beside every row.

| Phase | # | Lane | Fires when | Human stop |
|---|---|---|---|---|
| ground-truth | 1 | recon | the request names an existing route/component/service, or rests on an unverified claim about current behaviour | — |
| framing | 1 | product | the request is a new user-facing surface, or changes what an existing one is *for* rather than how well it does it | **yes** — the brief is relayed and the verdict is the human's |
| specification | 1 | story | framing produced scope no approved brief covers, **and** the slice crosses more than one lane's contract or touches a route/Prisma model already relied on by shipped frontend code | **yes** — the one hard stop |
| design | 1 | design | the change crosses the frontend/backend contract (a new or changed API response shape, a Prisma schema change), or more than one build lane touches it | — |
| build | 1..n | backend, frontend, test, docs | anything that edits `server/**`, `src/**`, `prisma/**`, `tests/**` or `docs/**` | — |
| verify | 1 | integration | any build lane was dispatched | — |
| verify | 2 | review | the run carries a story whose acceptance criteria someone must accept | — |
| close | 1 | docs | always — `docs/**` against what shipped, and `pack-corrections.md` against `capabilities/` **when a lane emitted one** | — |

`quant-audit` has no row. `project.md` § "Why `quant` is not bound" is the
reason, and it applies to every run, not a case-by-case judgment — do not add
the row for a slice that happens to touch `src/services/dcf/**` or
`src/services/health/**` without first reading that section.

### When the brief is the specification

The `story` row's trigger is narrow, the same way it is in `tradingview`, and
for the analogous reason: there is no PRD or epic tree here, so a story that
merely restates an already-approved brief is a dispatch and a second human stop
spent on a decision already made.

Record the row as `not triggered (the delivery brief in <nn> is the
specification)`, and `review` does not fire either — its clause asks for a
story to accept, and there is none.

**What still fires it:** a slice spanning more than one lane's contract with no
existing brief that already covers the shape, and any change to a route
response or a Prisma model that shipped frontend code already depends on —
because "what breaks for an existing watchlist / subscription / session" is a
question a one-line brief has not answered.

### Why `design` fires more often than it looks like it should

Unlike `tradingview`, where a script is its own whole artifact, an ordinary
datoro feature usually touches both `server/routes/**` (or a service) and
`src/**` — the batch ticker endpoint pattern `AGENTS.md` describes is exactly
this seam. Treat "does this change what an API response looks like, or add a
field a component now depends on" as the operative test for `design`, not
"does this feel small". A small change that adds a field to a shared response
still needs the contract settled once, by one lane, rather than guessed at
twice.

A change confined to one file on one side of the seam — a Vue component with
no new prop touching the outside, a backend service with no changed
response shape — correctly skips `design`.

### What the gates run

**`integration` runs `npm run validate:quick` at minimum** (`lint:check` +
`test`), and the full `npm run validate` when the order's `verification` field
says so or the slice touched `server/**` and `src/**` both. `architecture.md`
carries the exact escalation rule and the diagnostic commands to localise a
failure.

**`review`** verifies the story's acceptance criteria one by one, the same
shape as every other project — no repo-specific variation here.

### The short run

Most work in this repo is a short run: a one-file bug fix, a copy change, a
single new component with no new API surface. `framing`, `specification` and
`design` all fail their clauses, and the run is `build → verify(integration) →
close`. Three dispatches, and each false clause written into the ledger with
its reason.

**What makes them true, no matter how small it looks:** any new user-facing
surface — `framing` fires, verdict is the producer's. Any change to a shared
API response shape or a Prisma model — `design` fires, always. Any slice that
would otherwise ship with no approved brief and crosses a lane boundary —
`specification` fires and the human is stopped.
