REPORT 2026-08-27-next-epic-or-story/06
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md — new Backlog story draft: rewrite system-architecture.md's seam/route/data-flow inventory to the 15 shipped routers + ship a pytest guard against re-drift

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only story-drafting order; no verification command named. The story's own AC13 names `python scripts/run_all_tests.py` as the human's close-out check, not this lane's.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - story drafted at docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md — Epic: Unassigned, Status: Backlog, mirrors US-41.1's header/section shape
  - tickets: T-41.2.1 tech-lead scoping/design pass (replacement structure + confirm Data Flow bounds + decide guard file & key), T-41.2.2 docs rewrite of system-architecture.md, T-41.2.3 add/extend the pytest route-inventory guard
  - BLOCKS TICKETING — epic placement is the owner's open decision: open "Epic 41 — Documentation & Roadmap Accuracy Reconciliation" (producer's recommendation, sibling to Epic 32/36) or run standalone under the hygiene precedent
  - BLOCKS TICKETING — provisional number: US-41.2 is a placeholder; US-41.1 (inline-withheld-return-annotation) already holds .1 as its own placeholder and reserves US-41.1 under any new Epic 41, so this story's number may shift. Docs lane writes the renamed file + reports the git rm when an epic is assigned
  - open for tech-lead DESIGN — whether the guard extends services/quant-engine/app/tests/test_route_inventory.py or a sibling file, and whether the rewritten inventory is keyed on route paths or route module names
  - open, resolved inside T-41.2.1 — the exact line-by-line bounds of the "Data Flow" rewrite (recon did not read system-architecture.md lines ~267-345 line by line)

risks:
  - This is a draft for human review, not an approved story: epic placement and the provisional number are unresolved and block ticketing, and no gate has accepted it.
  - 03-delivery-brief.md left epic placement open, so I drafted on the assumption the story may proceed as a Backlog story regardless of the answer. If the owner wants it held pending an epic (as US-41.1 was held on 2026-08-26), ticketing waits on that call.
  - 02-scout.md § A flagged system-architecture.md lines ~267-345 ("Data Flow") as removed-product but did not read them line by line. AC6 is written broadly ("no subsection describing a removed surface") and T-41.2.1 is tasked to confirm the exact bounds; if part of that range is still accurate, AC6's wording will need narrowing at design time.
  - AC8-AC10 assert the market-data / trust-semantics / accepted-tradeoff sections are byte-identical before and after. If the rewrite legitimately needs a cross-reference update landing inside one of those sections, that AC is too strict and the tech lead should flag it.
  - The guard is analogised to test_route_inventory.py, but that test keys on module filenames in current-product-state.md whereas system-architecture.md lists route paths; a path-keyed guard is more brittle. Left to T-41.2.1, not resolved here.

## Orchestrator brief

- Decision: drafted ONE Backlog story, `US-41.2-system-architecture-doc-accuracy-and-route-guard.md`, mirroring US-41.1's header and section shape (Epic: Unassigned / PRD: none / Status: Backlog).
- Decision: 3 tickets, ordered — T-41.2.1 tech-lead scoping/design pass, then T-41.2.2 docs rewrite, then T-41.2.3 the pytest guard. No commit ticket, no self-gate ticket.
- Decision: 13 ACs — AC1-AC7 rewrite the stale seam/service/data-flow/truth-class/API-boundary content to the 15 shipped routers; AC8-AC10 pin the three already-current sections untouched; AC11-AC12 the re-drift guard + its non-vacuous check; AC13 full suite green.
- Decision: no schema/contract/methodology touch — contract_notes and pack_corrections are none.
- Lane split: none set (single story). Unit 1 docs-lane reconciliation from the brief is explicitly out of scope and noted as such.
- Blocks dispatch: two owner decisions — epic placement, and the US-41.2/US-41.1 provisional-number collision. Both reproduced unresolved in the story's `## Open decisions`. Two further items (guard file/key, Data Flow bounds) are the tech lead's at DESIGN, not human blockers.
- Sections below: "Story file" (what was written, where) · "Ticket list" · "Open decisions carried" · "Assumptions made".

## Story file

`docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md`
— full text lives there, not duplicated here. Header block matches US-41.1:
`Epic: Unassigned — Backlog`, `PRD: none`, `Status: Backlog`,
`Last updated: 2026-08-27`. Sections: Story · Context (with Grounding + "must
read" list) · Acceptance criteria (AC1-AC13) · Test plan · Tickets · Out of
scope · Notes / decisions · Open decisions · a closing draft-for-review note.

The story statement: an agent directed by `CLAUDE.md` and `project.md`
§ "Sources of truth" to trust `docs/architecture/system-architecture.md` for
"what the backend seams are" reads a route/seam/data-flow inventory matching
`services/quant-engine/app/api/routes/`, and a mechanical test fails if it
drifts again.

## Ticket list

1. **T-41.2.1** — Design / scoping pass (tech lead). Read registered routers,
   the service layer, and the doc in full. Produce the replacement structure for
   the stale sections; confirm line-by-line the "Data Flow" rewrite bounds
   (~267-345, unread by recon); decide the guard's file placement and whether it
   keys on route paths or module names. Traces AC1-AC7, AC11.
2. **T-41.2.2** — Docs: rewrite `system-architecture.md` per T-41.2.1 — seams
   inventory, implementation-reality service list, engine-purpose line,
   truth-class list, Data Flow section, API Boundary removed-surface references —
   to the 15 shipped routers and real services. Market-data / trust-semantics /
   accepted-tradeoff sections left untouched. Traces AC1-AC10.
3. **T-41.2.3** — Tests: add or extend the pytest guard resolving the doc's
   route inventory against `app/api/`, with offending-entry naming and a
   non-vacuous-scan check, per T-41.2.1's decisions. Traces AC11, AC12.

Contracts (the design pass) before consumers (rewrite, then guard). Tests are
their own ticket. No ticket instructs a commit or a self-run gate.

## Open decisions carried

All reproduced from `03-delivery-brief.md`, unresolved:

- **Epic placement (owner).** Open Epic 41 — Documentation & Roadmap Accuracy
  Reconciliation, or run standalone. Producer recommends opening it. Blocks
  ticketing.
- **Provisional number (owner).** `US-41.2` is a placeholder; `US-41.1` holds
  `.1` as its own placeholder and reserves `US-41.1` under any Epic 41. The
  docs lane writes the renamed file + reports the `git rm` when an epic is
  assigned. Blocks ticketing.
- **Guard test file & key (tech lead, DESIGN).** Extend `test_route_inventory.py`
  or add a sibling; key on route paths or module names.
- **"Data Flow" rewrite bounds (T-41.2.1).** Recon did not read lines ~267-345
  line by line; the scoping pass confirms exactly what is rewritten.

## Assumptions made

- The brief left epic placement open, so the story is drafted to proceed as a
  Backlog story regardless of the answer — matching how US-41.1 sits today.
- AC6 ("Data Flow describes the shipped flow only") is written broadly because
  the exact stale bounds are unconfirmed; T-41.2.1 is tasked to pin them and the
  AC wording may need to narrow at design time.
- AC8-AC10 assume the three already-current sections can be left byte-identical.
  If the rewrite needs a cross-reference update inside one of them, that
  assumption breaks and the tech lead should flag it.
