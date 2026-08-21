REPORT 2026-08-21-dynamic-sector-classification/04
status:      PARTIAL
verdict:     NONE

changed:
  - docs/product/stories/US-37.1-dynamic-equity-sector-classification.md — renumbered story (was US-24.12), Epic 37, tickets T-37.1.1-4, Filing note resolved
  - docs/product/prd/epic-37-dynamic-equity-sector-classification.md — new single-story-epic PRD stub, US-37.1 the only story
  - docs/product/stories/US-24.12-dynamic-equity-sector-classification.md — old path not deleted (no delete tool this session), converted to a tombstone pointing at US-37.1

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE (drafting/renumbering only); no Bash/shell tool was available this session, so check_report.py's self-check could not actually be run against this artifact — same gap as report 03

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Renamed story path: docs/product/stories/US-37.1-dynamic-equity-sector-classification.md — Status: Backlog, still not ticketed
  - New PRD stub: docs/product/prd/epic-37-dynamic-equity-sector-classification.md — single-story epic, Status: Backlog
  - Ticket list (4, ordered, renumbered): T-37.1.1 equity resolution logic (backend) — AC1-AC8; T-37.1.2 aggregation follow-through + caching (backend) — AC9; T-37.1.3 docs (methodology + exposure-fields.md); T-37.1.4 tests (test-engineer)
  - The 4 open decisions from the original draft are unchanged in substance and still block ticketing — see US-37.1's `## Open decisions` (provenance-field naming, `sector` nullability wiring, ISIN-mismatch state shape, caching/persistence shape)
  - Old path docs/product/stories/US-24.12-dynamic-equity-sector-classification.md still exists on disk, converted to a tombstone (superseded notice + pointer to US-37.1)
  - A lane with file-delete access, or the human directly, should delete the old US-24.12 file; it must not be read as an independent draft
  - No content beyond epic/PRD/ticket-ID plumbing changed: story statement, context, all 10 ACs, test plan, out-of-scope list stayed byte-identical to the approved draft
  - One Notes/decisions bullet was reworded (previously said "this draft chose 24, confirm or reassign at ticketing") so the file no longer contradicts its own new epic number
  - That reword only records the placement resolution — the ISIN-comparison rationale, naming caution, and methodology-doc-gap bullets around it are untouched
  - Next lane: tech-lead DESIGN, once the human approves the renumbered draft and pulls it into the next phase

risks:
  - This session had no Bash/shell/file-delete tool, so the scoped "rename" could not be a true filesystem rename — the old US-24.12 file still exists physically, converted to a tombstone rather than removed
  - That is a real gap against the work order's definition_of_done ("story file renamed/renumbered"), not a silent shortcut — flagging explicitly, not glossing over it
  - check_report.py could not be run against this artifact for the same reason (no shell tool) — the orchestrator's own run of it is the first real mechanical check
  - Judgment call: I reworded one Notes/decisions bullet beyond the work order's literal "remove the Filing note callout at the top" instruction — see handoff for what and why
  - Reasoning for that call: leaving it verbatim would have the file say "this draft chose 24" while everything else now reads 37; treated as epic-placement provenance, the same category as the Filing note, not story substance
  - Flagging that judgment call for human review in case a stricter reading (touch nothing outside the header) was intended instead
  - This is a draft for human review, not an approved story — status is Backlog on both the story and the new PRD, nothing here is ticketed or dispatched
  - Did not re-verify any of the underlying research/financial claims in this pass — pure renumbering, per the work order's scope

## Orchestrator brief

- Decision: story renumbered US-24.12 -> US-37.1, new dedicated single-story Epic 37 created, per the human's explicit placement decision (no Epic-24 reopening).
- Decision: all substantive content (statement, context, 10 ACs, test plan, out-of-scope, 4 open decisions) preserved byte-identical; only epic header, PRD link, ticket IDs (T-37.1.1-4), and the Filing-note/epic-placement bullets changed.
- Gap: no Bash tool available this session — old US-24.12 file could not be deleted, only converted to a tombstone. Needs a real delete before close-out (see risks).
- New files: `docs/product/stories/US-37.1-dynamic-equity-sector-classification.md` (the story), `docs/product/prd/epic-37-dynamic-equity-sector-classification.md` (single-story PRD stub).
- Roadmap, story index (`docs/product/stories/README.md`), and epic-24 PRD untouched, per non_goals.
- 4 open decisions still block ticketing — unchanged from the 03 draft, see handoff.
- Next: human review/approval of the renumbered draft, then tech-lead DESIGN; separately, someone with delete access should remove the old US-24.12 file.
