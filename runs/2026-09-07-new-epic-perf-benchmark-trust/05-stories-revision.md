REPORT 2026-09-07-new-epic-perf-benchmark-trust/05
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-44.1-monthly-returns-honour-withholding-gate.md — folded the per-month "partial month" disclosure marker into the story (Open decision 2 marked RESOLVED); revised AC7, added AC8-AC10, renumbered old AC8 to AC11 (8 ACs → 11); extended T-44.1.1 (schema hook), T-44.1.2 (marker render), T-44.1.3 (partial/full/absent tests), T-44.1.4 (contract-doc wording); removed the US-44.5 out-of-scope bullet; Notes + "Last updated" 2026-09-08.
  - docs/product/stories/US-44.4-selectable-comparison-benchmark.md — recorded that the implementation run opens with a focused quant-analyst RESEARCH pass on a non-verified benchmark's return basis; added T-44.4.0 as the first ticket (5 tickets → 6) with T-44.4.2 depending on it; settled the "may need a RESEARCH pass" wording in Open decisions and Notes; "Last updated" 2026-09-08.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification field was NONE — edit-only revision of two already-approved story drafts to apply two 2026-09-08 human decisions. No command to run. Both stories remain Status: Backlog.

contract_notes:
  - US-44.1 now introduces a per-month partial-month marker on the monthly-returns contract (services/quant-engine/app/schemas/dashboard_history.py), mirrored to desktop types.ts and docs/contracts/dashboard-fields.md — the schema hook now fires for US-44.1, where the prior draft was written to avoid it. Field name/type/nullability are left to the US-44.1 DESIGN pass.

pack_corrections:
  - none

handoff:
  - US-44.1 revised in place: docs/product/stories/US-44.1-monthly-returns-honour-withholding-gate.md — 11 acceptance criteria (was 8), 4 tickets T-44.1.1..T-44.1.4 (count unchanged, T-44.1.1 and T-44.1.4 scope extended for the schema hook).
  - US-44.4 revised in place: docs/product/stories/US-44.4-selectable-comparison-benchmark.md — 8 acceptance criteria (unchanged), 6 tickets T-44.4.0..T-44.4.5 (was 5; T-44.4.0 quant RESEARCH added as the first ticket).
  - US-44.1 Open decision 2 (per-month disclosure marker) is now RESOLVED per the human decision of 2026-09-08 — folded in, no successor story, no US-44.5.
  - US-44.1 Open decision 5 (methodology wording: exclude-the-day vs withhold-the-month) still stands; it is ratified by the human at close-out and does not hard-block ticketing — the ACs are written to the settled quant reading (02-quant-research.md § P1).
  - US-44.4 carries no blocking open decision. T-44.4.0 (quant-analyst RESEARCH on a non-verified benchmark's return basis) must be dispatched by the orchestrator at the start of the US-44.4 implementation run and gates T-44.4.2.
  - Both stories remain Status: Backlog and are drafts for human review — approval is the human's, not this lane's; the run.md signoff line already records the 2026-09-08 approval of all four Epic 44 stories.

risks:
  - Assumed the partial-month marker is a new element of the monthly-returns contract (schema hook), per the DoD. If the US-44.1 DESIGN pass finds the existing run-level withheld_return_dates is enough to drive the grid marker frontend-only, T-44.1.1's schema-hook clause and the AC11-adjacent contract note become moot.
  - AC10 says a clean full month renders "byte-identical to today" (DoD wording carried verbatim). If the DESIGN pass restructures the grid cell markup to host the partial marker, a reviewer should read AC10 as "the full-month cell is visually and semantically unchanged" rather than a literal byte diff.
  - US-44.1 ticket numbering was kept at T-44.1.1..T-44.1.4 (DoD's mapping) rather than inserting a dedicated schema/contract ticket; T-44.1.1 now spans the analytics gate and the schema+TS+contract-doc change, which the DESIGN pass may choose to split across the backend and a contract lane.
  - T-44.4.0 is a quant RESEARCH dispatch listed inside a story's ticket list. It instructs no commit and no self-gate, but it is a planning-lane pass rather than an implementation lane — flagged in case the orchestrator prefers to track it on the run ledger instead of the story.

## Orchestrator brief

Edit-only revision applying the two 2026-09-08 human decisions to two approved Epic 44
story drafts. Verdict NONE (story lane does not gate). Both stories stay Status: Backlog,
drafts for human review.

Decisions applied:
- US-44.1: the per-month "partial month" disclosure marker is FOLDED IN (Open decision 2
  RESOLVED). US-44.1 is now a schema-hook story. No US-44.5. AC count 8 → 11; tickets
  unchanged at 4 (T-44.1.1 + T-44.1.4 scope extended).
- US-44.4: the implementation run now BEGINS with a focused quant-analyst RESEARCH pass on
  a non-verified benchmark's return basis, added as T-44.4.0; T-44.4.2 depends on it. AC
  count unchanged at 8; tickets 5 → 6.

No lane split set. Nothing blocks dispatch: US-44.1 Open decision 5 is close-out
ratification only; US-44.4 has no blocking decision.

Sections below: "Report block" (changed / contract_notes / handoff / risks as above);
this brief. The full revised stories are the two files under docs/product/stories/, not
reproduced here — they travel to the per-story implementation runs as inputs.

REPORT HEAD 2026-09-07-new-epic-perf-benchmark-trust/05
artifact:    C:\projects\investments\.agentic\runs\2026-09-07-new-epic-perf-benchmark-trust\05-stories-revision.md
status:      DONE
verdict:     NONE
verification: NOT_RUN
detail:      Order verification field was NONE — edit-only revision of two already-approved story drafts to apply two 2026-09-08 human decisions. No command to run. Both stories remain Status: Backlog.
changed:     2
contract_notes: 1
pack_corrections: 0
handoff:     6
risks:       4
headline:    Applied the two 2026-09-08 decisions — US-44.1 folds in the partial-month marker (8→11 ACs, schema hook now fires); US-44.4 opens with quant RESEARCH (T-44.4.0 added). Both stay Backlog drafts for human review.
