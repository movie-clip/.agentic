# Capability pack: story — project `portfolio`

For the `story-author` lane.

Companion source: `portfolio/.claude/skills/write-story/SKILL.md` — read it for
the drafting craft (how ACs are phrased here, how the test plan reads).

**But do not follow its process.** That skill was written before this network
existed, when it *was* the pipeline. It instructs its user to decide epic
placement, update the roadmap and the story index, and hand off to
`build-story`. In this network those belong to the human, the docs lane, and the
orchestrator. Take the writing conventions; leave the workflow.

This is a live example of the two-sources-of-truth problem: the repo skill and
this pack overlap, and the skill will not be updated when the network changes.
When they conflict, this pack wins.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Files** · **Status values** · **Guardrails as they show up in acceptance criteria** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Read the nearest sibling story first | always, before drafting — it is one file |
| Sizing | you are deciding whether this is one story or several |
| Common failure modes here | before you report — read it as a checklist |

---

## Files

| Path | Your relationship to it |
|---|---|
| `docs/product/stories/_TEMPLATE.md` | the shape to follow |
| `docs/product/stories/US-<epic>.<n>-<slug>.md` | **the one file you create** |
| `docs/product/stories/README.md` | read for numbering. **Do not edit.** |
| `docs/product/epic-roadmap.md` | read for context. **Do not edit.** |
| `docs/product/prd/epic-<n>-<slug>.md` | read the epic's goals and non-goals |
| `docs/finance/financial-methodology.md` | read when the story touches a formula |
| `docs/contracts/<area>-fields.md` | read to see what the contract *is* today |

Numbering: `US-<epic>.<n>-<slug>.md`, tickets `T-<epic>.<story>.<n>`.

## Read the nearest sibling story first

Before drafting, read one or two recent stories from the same area. US-15.1 and
US-15.2 are good models for a full-stack analytics slice: how ACs are phrased,
how the reconciliation invariant is stated as a checkable criterion, how the
"Notes / decisions" section records what was considered and rejected.

Match their register. A story that reads differently from its neighbours makes
the whole product-docs set harder to trust.

## Status values

`Backlog` → `Next phase` → `In progress` → `Done`.

You write `Backlog`, or `Next phase` if the work order says the human has pulled
it into the active phase. **Never `Active`** — that is an epic-level word, not a
story-level one, and using it creates a roadmap contradiction. Never `Done`.

## Guardrails as they show up in acceptance criteria

The five guardrails hold whether or not you write them down. Do not restate them
as ACs. Do write an AC when this story creates a *specific new way* to violate
one — that is the case worth checking:

- A new field that can be missing → an AC stating what the user sees when it is
  (a dash, a badge, a named disclosure — never zero, never a placeholder).
- A new aggregate over values that can be missing → an AC stating that the
  missing share is disclosed rather than apportioned across the others.
- A new number derived from synthetic history → an AC stating the trust level it
  claims, so the reviewer can check it does not overstate its basis.
- A change to a withheld field → this needs the owner's decision, not an AC.
  Report `BLOCKED`.

## Sizing

If the draft runs past roughly a dozen acceptance criteria, or the tickets span
schema *and* a new UI interaction model, say so in `risks` and propose the split
— typically the backend contract as one story and the UI surface as another.

Do not split it yourself: whether to split is a producer decision, and you would
be creating a second story nobody scoped. Flag and let the human choose.

The producer's `invest:` line often names Estimable as the weak criterion. If it
did, that is a signal the story wants a design decision before ticketing, not a
longer AC list.

## Common failure modes here

**Answering the producer's open decision.** The single most damaging one. If the
brief says "your call", the story says "open, blocks ticketing".

**Specifying the schema.** Tempting because the research brief often gives you
enough to do it. That inventory is a *constraint for the tech lead*, cited as
such — not a set of field definitions to promote into ACs.

**Writing roadmap entries.** The skill tells you to. Don't.

**Ticket 5 tells someone to commit.** The repo's older stories sometimes end
with a close-out ticket that self-invokes `verify-story` and commits. Do not
reproduce that pattern — the gates are dispatched by the orchestrator, and the
human commits.

**Predicting test counts.** "+8 backend, +7 frontend" reads precise and invites
the test lane to hit a number instead of covering the behaviour.

## Definition of done for this lane

- [ ] Producer brief read in full; quant research brief read where one exists
- [ ] Nearest sibling stories read for register and structure
- [ ] Every producer open decision reproduced in `## Open decisions`, unresolved
- [ ] ACs state observable behaviour; none specifies a field name, type or function signature
- [ ] Absent and degraded cases have their own ACs
- [ ] Research-brief constraints carried forward and cited, not restated as schema
- [ ] Test plan names files and behaviours; no function names, no counts
- [ ] Tickets ordered, lane-sized, tracing to ACs; **none instructs a commit or a self-gate**
- [ ] Status is `Backlog` or `Next phase`
- [ ] Roadmap, story index and PRD untouched
- [ ] Report says plainly that this is a draft for human review
