REPORT 2026-08-24-etf-sector-classification-research/05
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-39.1-direct-held-etf-sector-classification.md — Open decisions #1-#2 folded in as resolved; section removed

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only revision order; no code/test/build command applies

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs/product/stories/US-39.1-direct-held-etf-sector-classification.md still carries 12 ACs and 6 tickets (T-39.1.1-6), unchanged counts, per the order's instruction that no ticket is needed for category
  - AC6 now states the concrete `DOMINANCE_THRESHOLD = 55%` behavior, no longer citing "Open decision #1"
  - Context now carries a resolved evidence table framed as "55% chosen: captures GRID (58.4%) and QQQ (60.3%) with margin, cleanly excludes ICLN (41.4%) and SPY (37.4%)"
  - Context now carries an explicit "`category` is out of scope, unaffected — resolved" paragraph; Out of scope and Notes / decisions sections updated to match (category's existing keyword derivation is unaffected, not deferred/TBD)
  - Test plan's dominance-threshold pass/fail cases and T-39.1.4's ticket description now reference the concrete 55% value, not "the finalized threshold"
  - "## Open decisions" section removed entirely — both items resolved and folded into Context / AC6 / Test plan / Tickets / Out of scope / Notes
  - story Status remains Backlog; no other section (roadmap, story index, PRD, epic PRD) touched; Filing note (epic placement, a separate still-open item) left untouched per non_goals

risks:
  - the "New work this story requires" intro paragraph in Context still cites the research brief's own section title "§ Open item: category" as a source citation (historical pointer to where the brief discussed it) — left as-is since it names the brief's section, not the story's own resolution state; flagging in case a reviewer reads it as residual ambiguity
  - this report is a draft revision for human review, same as the original 04-story.md draft — not an approval
  - I did not re-verify the 55% cutoff arithmetic beyond restating the four data points (58.4%, 60.3%, 41.4%, 37.4%) already present in 03-quant-research.md and the prior story draft — no new evidence was gathered, this was a synthesis-only pass per the order's scope

## Orchestrator brief

- Decision: DOMINANCE_THRESHOLD = 55% (human's resolution) folded into Context, AC6, Test plan, T-39.1.4 — no more "(Open decision #1)" references anywhere in the file
- Decision: `category` field scoped out entirely (human's resolution) — Context, Out of scope, and Notes now state it plainly as unaffected/untouched, not deferred; no new ticket added
- "## Open decisions" section deleted; both resolutions recorded in Context (two new paragraphs) and Notes / decisions (two "— resolved" bullets), mirroring the US-38.1 05-story-revise.md precedent
- AC count unchanged at 12, ticket count unchanged at 6 (T-39.1.1-6) — story is otherwise structurally identical to 04-story.md's draft
- Story is now ready for tech-lead DESIGN or backend-engineer dispatch once epic placement (number, roadmap entry) is confirmed by docs-engineer at close-out — that item is untouched, separate from the two resolved here
- No contract, schema, or roadmap file touched — this was a story-file-only revision
