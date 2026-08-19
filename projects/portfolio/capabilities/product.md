# Capability pack: product — project `portfolio`

For the `producer` lane. How this project's roadmap, epics and stories actually
work.

---

## Where the plan lives

| Doc | Role |
|---|---|
| `docs/product/epic-roadmap.md` | **the authority.** Living execution snapshot: active epic, story snapshot table, slice log, open items. Every pointer elsewhere goes stale; this does not. |
| `docs/product/prd/epic-<n>-<slug>.md` | one PRD per epic: problem, goals, non-goals, findings |
| `docs/product/stories/US-<epic>.<n>-<slug>.md` | one file per story |
| `docs/product/stories/README.md` | story index, grouped by epic, with scope summaries |
| `docs/product/current-product-state.md` | canonical shipped-state inventory |
| `docs/tech-debt-register.md` | deferred improvements, not stories |

Read the roadmap **first**, every time. It states which epic is active and lists
open items that were deliberately left open.

## Story lifecycle

| Status | Meaning |
|---|---|
| **Backlog** | Defined: statement + ACs + rough test plan. Not ticketed. |
| **Next phase** | Pulled into the active phase, broken into ordered tickets. |
| **In progress** | Being delivered. |
| **Done** | Every AC met, full test plan passing, docs updated. |

Naming: `US-<epic>.<n>-<slug>.md`. Tickets: `T-<epic>.<story>.<n>`.

Only a **ticketed** story can be dispatched. A Backlog story needs a ticketing
pass first.

## The house pattern: findings-first epics

This is the most important convention in the project, and it is unusual enough
that you must apply it deliberately rather than defaulting to a normal feature
epic.

**When an epic addresses something suspected wrong with shipped behaviour, its
first story is an audit.** `US-<epic>.1` is audit-only: it investigates, records
findings as `F-1`, `F-2`, … in the PRD, and ships no behaviour change. Each
subsequent story closes one or more findings and names them in its scope line.

Epics 33 and 34 both work this way. It exists because scoping a fix before the
cause is named produces stories that get rewritten mid-flight — and in a system
whose whole premise is that every number is traceable, "we think it's wrong"
is not a scope.

Two things follow that matter for your briefs:

**The audit records what is correct too.** Each audit story carries an
"examined-and-correct" list. That is what makes the finding list trustworthy
rather than just a list of the first three things someone noticed.

**Findings may be closed as "will not fix", with the reason recorded.** Epic 34
left F-1a, part of F-10, and F-12 open deliberately — structurally unreachable,
or bounded and immaterial. When a request touches one of these, surface the
recorded reason and ask whether it has changed. Do not quietly reopen a decision
someone already made with more context than you have.

## Epics get created mid-flight

Epic 35 was created from a hazard hit during US-34.9's work. This is normal and
healthy here: implementation surfaces real problems, and the honest response is
a new epic rather than scope-creeping the current story.

So when an implementation lane reports a finding outside its scope, that is a
producer input, not noise. Brief it: new epic, new story in an existing epic, or
debt-register entry.

Note also that epic creation **corrects the framing**, it does not just copy the
complaint. Epic 35's own description records that the original framing was
partly wrong and states the corrected version. A brief that simply restates the
reporter's words has skipped the producer's actual work.

## What is a story here, and what is not

**A story is a vertical slice of user value.** Read a few existing story
statements before writing a brief — they are phrased as what the researcher can
now see or trust, not as what the code now does.

Not stories:

- **Refactors and cleanups** → `docs/tech-debt-register.md`.
- **Pure technical enablement** with no user-visible change. If it is genuinely
  needed, it is a ticket inside a story that delivers something.
- **A bug with no diagnosis** → route to investigation. In this project that
  usually means an audit story, not a fix story.

## Guardrails you must respect when briefing

The product's five guardrails are in the project profile. Two shape scope
decisions specifically:

- **No execution.** The system never places trades or moves money. A request in
  that direction is declined, not deferred.
- **Trust semantics over fabrication.** A request to "just show a number" where
  the system currently withholds is a request to weaken a guardrail. It may
  still be legitimate — US-34.2 published a replay-derived TWR under a *new,
  explicitly labelled* trust rung rather than pretending it was verified. But
  the brief must name it as a trust-model change, because that is what it is,
  and it needs the owner's decision.

## Sequencing conventions

- **Recommended order is stated explicitly** at the end of each epic's story
  index. Follow the existing convention: state the order and the reason.
- **Risk-first.** Put the story that could invalidate the others first.
  US-34.2 was first in its epic and immediately surfaced three hidden defects
  that reshaped the rest.
- **A story that surfaces a finding may spawn its own successor.** Expect this
  and say so in the brief rather than presenting a plan as fixed.

## Definition of done for this lane

- [ ] Roadmap, active PRD, story index and shipped-state inventory all actually read
- [ ] Checked whether the request is already shipped, already storied, or deliberately open
- [ ] Verdict stated plainly, including "already covered" or "decline" when true
- [ ] Proposed stories are vertical slices with a one-sentence user-visible outcome
- [ ] Audit-first applied where the cause is not yet named
- [ ] Dependencies named with the reason for each edge
- [ ] Any prior recorded decision the brief would reverse is surfaced, not overridden
- [ ] Open decisions for the human listed explicitly
- [ ] No story files written, no implementation specified
