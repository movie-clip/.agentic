REPORT 2026-08-21-epic38-followups-and-etf/05
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-38.1-etf-lookthrough-sector-classification.md — Open decisions #1-#3 folded in as resolved; section removed

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only revision order; no code/test/build command applies

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs/product/stories/US-38.1-etf-lookthrough-sector-classification.md now carries 9 ACs (was 7) and 4 tickets (unchanged count, T-38.1.2 now unconditional)
  - AC8 states the resolved suppression-threshold exemption (Unclassified always itemized, exempt from MIN_SECTOR_WEIGHT); traced to T-38.1.1
  - AC9 states the resolved companion-curation requirement (8 tickers classify via curated sector, not Unclassified); traced to T-38.1.2
  - T-38.1.2 (companion registry curation) is now unconditional scope, no longer gated on a design-pass decision
  - "## Open decisions" section removed entirely — all three items (epic title, suppression exemption, companion curation) are resolved and folded into Context / ACs / Tickets / Notes
  - Filing note updated: epic title is confirmed verbatim; epic number and roadmap entry remain pending human/docs-engineer close-out action, unchanged from before
  - story Status remains Backlog; no other section (roadmap, story index, PRD) touched

risks:
  - I did not re-verify the eight companion-ticker curation values (sector/category strings) against FMP or existing registry conventions — that remains T-38.1.2's implementation work, not something this revision could or should decide
  - the story's test-plan additions (suppression-exemption regression, companion-curation coverage) name behaviours and files per the pack's test-plan convention, not function names or counts, consistent with US-37.1's sibling story
  - this report is a draft revision for human review, same as the original 04-stories.md draft — not an approval

## Orchestrator brief

- US-38.1's three open decisions are now resolved and folded in: epic title (confirmed verbatim, no wording change), suppression-threshold exemption (Unclassified exempt from MIN_SECTOR_WEIGHT — new AC8), companion registry curation (ships inside this story, not fast-follow — new AC9, T-38.1.2 now unconditional)
- "## Open decisions" section deleted from the story; resolutions recorded in Context (new paragraphs) and Notes / decisions (three "— resolved" bullets)
- story is now 9 ACs / 4 tickets, ready for tech-lead DESIGN or backend-engineer dispatch once epic placement (number, roadmap entry) is confirmed by docs-engineer at close-out
- no contract, schema, or roadmap file touched — this was a story-file-only revision
- US-38.2 untouched, per non_goals
