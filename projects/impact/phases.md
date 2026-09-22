<!-- Profile extension: ORCHESTRATOR only, read at intake.
     `check_report.py` reads the `verify` rows here; see `## Phases` below. -->

# Project phases: `impact`

The phase→lane binding for this project. Read this at intake, alongside
`project.md`. No specialist lane needs it.

## Contents

- **Phases** — the binding table: which lane fills each phase, in what order,
  and the clause that decides whether it fires. Copied into the run ledger.
- **When the brief is the specification** — why `story` is the exception
  here, not the rule.
- **Why `design` fires more often than it looks like it should** — the
  package/contract seam this repo crosses on an ordinary feature.
- **What the gates run** — the command each `verify` row owes.
- **The short run** — what most work in this repo actually looks like.

## Phases

`protocol/orchestrator.md` § 2 defines the phases and § 3 the loop that walks
them. This table is the binding: which lane fills each phase **here**, in
what order, and the clause that decides whether it fires at all. The
orchestrator copies it into the run ledger at intake and records a verdict
beside every row.

| Phase | # | Lane | Fires when | Human stop |
|---|---|---|---|---|
| ground-truth | 1 | recon | the request names an existing system/behaviour, or rests on an unverified claim about current behaviour | — |
| framing | 1 | product | the request is a new gameplay system or feature surface, or changes what an existing one is *for* rather than how well it does it | **yes** — the brief is relayed and the verdict is the human's |
| specification | 1 | story | framing produced scope no approved brief covers, **and** the slice crosses more than one lane's contract | **yes** — the one hard stop |
| design | 1 | design | the change crosses a package-boundary contract — a shared singleton or component shape, the crate/content-loading pipeline, a new cross-package `.asmdef` reference | — |
| build | 1..n | backend, test, docs | anything that edits `Impact/Packages/**`, `Impact/Assets/**`, `Impact/Tools/**`, or `Impact/*.md` docs | — |
| verify | 1 | integration | any build lane was dispatched | — |
| verify | 2 | review | the run carries a story whose acceptance criteria someone must accept | — |
| close | 1 | docs | always — `Impact/*.md` against what shipped, and `pack-corrections.md` against `capabilities/` **when a lane emitted one** | — |

`quant-audit` has no row. `project.md` § "Why `frontend` and `quant` are not
bound" is the reason, and it applies to every run — do not add the row for a
slice that happens to touch numeric gameplay tuning (damage curves, drop
rates) without first reading that section; a game project's number tuning is
not the mathematics this gate exists to check.

### When the brief is the specification

The `story` row's trigger is narrow, the same shape as `datoro`, and for the
same reason: there is no PRD or epic tree here, so a story restating an
already-approved brief is a dispatch and a second human stop spent on a
decision already made.

Record the row as `not triggered (the delivery brief in <nn> is the
specification)`, and `review` does not fire either — its clause asks for a
story to accept, and there is none.

**What still fires it:** a slice spanning more than one lane's contract with
no existing brief that already covers the shape — most often a change to a
shared singleton or the crate/content pipeline that both `athena.shared` and
a dependent package (`athena.charactercontroller`, `athena.gameplay`) rely
on, since "what breaks downstream" is a question a one-line brief has not
answered.

### Why `design` fires more often than it looks like it should

Unlike a project with a frontend/backend HTTP seam, an ordinary Impact change
usually stays inside one package and correctly skips `design`. What crosses
the seam here is the **package dependency chain** and the **ECS singleton
surface** `ARCHITECTURE_REVIEW.md` describes as the project's central risk:
the crate/content-loading pipeline, and the player/character/skin flow built
on it. Treat "does this change a component or singleton shape another
package already reads" as the operative test for `design`, not "does this
feel small". A one-line change to a widely-read singleton still needs the
shape settled once, by one lane, rather than guessed at twice by
`athena.shared` and `athena.charactercontroller` separately.

A change confined to one system inside one package, with no new or changed
public component/singleton shape, correctly skips `design`.

### What the gates run

**`integration` runs `dotnet build Impact.sln` and
`Tools/Run-UnityTests.ps1 -Platform EditMode -CoreOnly` at minimum**, plus
`-Platform PlayMode` when the change reaches runtime/session/player flow, and
drops `-CoreOnly` for the fuller suite when the order's `verification` field
says so or the change touches the crate/content pipeline directly.
`architecture.md` carries the escalation rule and diagnostic commands to
localise a failure.

**`review`** verifies the story's acceptance criteria one by one, the same
shape as every other project — no repo-specific variation here.

### The short run

Most work in this repo is a short run: a one-system bug fix, a new component,
a single test added for existing behaviour. `framing`, `specification` and
`design` all fail their clauses, and the run is `build → verify(integration)
→ close`. Three dispatches, each false clause written into the ledger with
its reason.

**What makes them true, no matter how small it looks:** any new gameplay
system or feature surface — `framing` fires, verdict is the producer's. Any
change to a component/singleton shape another package already depends on —
`design` fires, always. Any slice that would otherwise ship with no approved
brief and crosses a lane boundary — `specification` fires and the human is
stopped.
