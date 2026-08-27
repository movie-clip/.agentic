REPORT 2026-08-26-missing-chart-data-0414/05
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-41.1-inline-withheld-return-annotation.md — new draft story, status Backlog, no epic assigned

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read/write story-drafting order, no verification command named; I have no Bash and cannot self-run check_report.py

contract_notes:
  - PerformancePoint.withheld_reason: str | None is a new field named in the story (per 03-quant-research.md § Field proposal, carried forward as a cited constraint, not a schema I am defining) — the tech-lead DESIGN pass owns the actual schema/type/contract-doc edit, per T-41.1.1

pack_corrections:
  - none

handoff:
  - story path: docs/product/stories/US-41.1-inline-withheld-return-annotation.md
  - tickets: T-41.1.1 (backend field + shared classifier extraction), T-41.1.2 (frontend chart annotation, design-pass-dependent), T-41.1.3 (tests), T-41.1.4 (methodology-doc two-granularity note, NOT the separate self-contradiction fix already dispatched as 04-docs.md)
  - open decision (reproduced from 03-quant-research.md § Open questions, unresolved): whether to delete replay_disclosures()'s now-dead reconciliation_adjustment branch as part of the classifier extraction — tech-lead DESIGN call
  - open item (mine, not a producer/quant open decision): the story's epic numbering (US-41.1) is a placeholder — no epic exists yet per the human's "Backlog, no new epic" decision, and this project has no orphan-story-without-an-epic precedent; a future pass must confirm or renumber when an epic is actually opened
  - the story cites 03-quant-research.md's field proposal (PerformancePoint.withheld_reason) as a carried-forward research constraint per the work order's DoD, not as a schema I am authoring — the exact type/nullability contract is explicitly left to the tech-lead design pass (AC4)

risks:
  - I assumed the work order's "no epic assigned yet" instruction means I should still pick a placeholder US-<epic>.<n> filename (US-41.1, next unused epic number) rather than leave the file unnumbered, since docs/product/stories/README.md's convention (every story lives under some epic, even Backlog-status ones like Epic 28) has no orphan-story precedent to fall back on — flagged explicitly in the story's own § Open decisions so it is not silently treated as a real epic assignment
  - dashboard-fields.md line 312 ("withheld because the state carried a material reconciliation_adjustment") carries the same stale pre-US-34.8 framing 03-quant-research.md flagged at financial-methodology.md:2436-2443 and dashboard_history_engine.py:504-505 — I did not touch it (out of my lane's scope, docs/product/stories/ only) but it is a second instance of the same drift the already-dispatched docs run may not have found; naming it here so it can be routed
  - this report is a draft for human review, not an approved story — status Backlog, and the human has not yet seen or approved the ACs, tickets, or the two open decisions carried forward

## Orchestrator brief
- Decision: story title/outcome, status (Backlog), and AC1/AC2 framing follow the work order's DoD verbatim — narrowed "withheld_return_dates" framing, not "every null point."
- Decision: field named in AC4 (PerformancePoint.withheld_reason) is cited as a research-brief constraint, not an authored schema — tech lead settles the actual contract.
- Decision: numbered US-41.1 as a placeholder (no epic exists) — flagged as an open item, not a resolved epic assignment.
- Both design questions from 03-quant-research.md § Open questions reproduced as OPEN in the story, not resolved.
- Out-of-scope surfaces (IndexedReturnChart, Risk-tab charts, MonthlyReturnsGrid) and the separate doc-defect fix (04-docs.md) named explicitly so no duplication.
- Story file: docs/product/stories/US-41.1-inline-withheld-return-annotation.md — the only artifact besides this report.
- Blocks dispatch: human must approve the draft story (ACs, tickets, epic-placeholder numbering) before any build lane starts.
