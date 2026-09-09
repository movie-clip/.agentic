REPORT 2026-09-07-new-epic-perf-benchmark-trust/07
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-44.1-monthly-returns-honour-withholding-gate.md — draft banner replaced with a 2026-09-08 human-approval note; kept the `## Open decisions` pointer; Last updated already 2026-09-08, unchanged; Status Backlog unchanged.
  - docs/product/stories/US-44.2-withheld-days-warning-direction.md — draft banner replaced with the approval note; Last updated 2026-09-07 → 2026-09-08; Status Backlog unchanged.
  - docs/product/stories/US-44.3-benchmark-outage-preserves-portfolio-performance.md — draft banner replaced with the approval note, keeping the design-pass fact ("implementation tickets additionally wait on the T-44.3.1 DESIGN pass"); Last updated 2026-09-07 → 2026-09-08; Status Backlog unchanged.
  - docs/product/stories/US-44.4-selectable-comparison-benchmark.md — draft banner replaced with the approval note; Last updated already 2026-09-08, unchanged; Status Backlog unchanged.

verification:
  command:   NONE (order verification field was NONE; read-only-adjacent status edit)
  result:    NOT_RUN
  detail:    Order named no verification command. No story statement, Context, AC, ticket, Out-of-scope or Notes text was altered — only the top-of-file banner and the Last updated date.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The four Epic 44 story files now record human approval dated 2026-09-08 (Epic 44 and all four stories); they are no longer unapproved drafts.
  - All four keep Status: Backlog — approved, not started. Each story's implementation is a separate per-story run, not dispatchable from this run.
  - US-44.3 implementation tickets (T-44.3.2, T-44.3.3, T-44.3.4, T-44.3.5) still gate on the T-44.3.1 tech-lead DESIGN pass; that fact is preserved in the file's banner and its `## Open decisions` block.
  - US-44.4 implementation run opens with a quant-analyst RESEARCH dispatch (T-44.4.0) before T-44.4.2; unchanged by this edit, still recorded in the file.
  - `## Open decisions` blocks in all four files are untouched: they continue to record which items are resolved vs ratified-by-human-at-close-out.

risks:
  - This is a draft for human review. The edit asserts a human approval dated 2026-09-08 on the strength of the work order's goal line alone; the four story files carry no independent approval record and I did not see a signed approval artifact. If the approval or its date is wrong, revert the banner and Last updated changes.
  - The `**Epic:**` and `**PRD:**` lines in every file still read "proposed" / "to be created (by the docs lane after human approval)". The order scoped edits to the approval banner and status line only, so I left them; a docs-lane pass may want to reconcile that wording now that approval has happened.
  - US-44.1 and US-44.4 already carried Last updated 2026-09-08, so their dates were left as-is per the order ("in any file where it is not already that date").

## Orchestrator brief

- Decision: applied the human-approval banner (dated 2026-09-08, Epic 44 + all four stories) to US-44.1 through US-44.4, replacing the "draft / not approved" blockquote in each.
- Decision: Status left at Backlog in every file; no AC, ticket, scope, Notes or Open-decisions text changed.
- Decision: US-44.3 keeps its design-pass gate note (T-44.3.1) in the new banner; US-44.1 keeps its `## Open decisions` pointer.
- Decision: Last updated set to 2026-09-08 in US-44.2 and US-44.3; already that date in US-44.1 and US-44.4.
- No lane split — single mechanical status edit across four files.
- Sections below: none beyond this brief and the report block; the four `changed` bullets are the whole change.
- Blocks dispatch: none. This report is a draft for human review — it records an approval it was told about, it does not verify one. If the approval date is wrong, revert per `risks`.
- Not in scope / not touched: roadmap, PRD, story index, READMEs (docs lane owns those).
