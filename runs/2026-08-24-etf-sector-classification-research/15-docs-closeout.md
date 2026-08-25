REPORT 2026-08-24-etf-sector-classification-research/15
status:      PARTIAL
verdict:     NONE

changed:
  - docs/product/prd/epic-39-direct-held-etf-sector-classification.md — new file, PRD for Epic 39 (Status/Created/Closed/Seeded-by header, Problem, Goal, Non-goals, Story snapshot, Slice log, Notes on T-39.1.7 + two carries)
  - docs/product/epic-roadmap.md — top-of-file "Most recently shipped" now names Epic 39; new "## Completed Epic: Epic 39" section inserted before Epic 38's, most-recent-first
  - docs/product/stories/README.md — new Epic 39 index section added above Epic 38's, with a US-39.1 row (Status: Done)
  - docs/product/stories/US-39.1-direct-held-etf-sector-classification.md — Status Backlog to Done; PRD line filled in; filing note updated; AC1-AC12 checkboxes ticked; T-39.1.1-6 ticked; T-39.1.7 added (unplanned, ticked, with a one-line reason)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (docs lane, no Bash tool granted per PROTOCOL.md §7)

contract_notes:
  - none — the one prior contract note (exposure-fields.md's enumeration prose needing the new literal) was already landed by 09-docs.md (T-39.1.5), confirmed by direct read

pack_corrections:
  - none

handoff:
  - docs/product/current-product-state.md needed no edit — 09-docs.md's T-39.1.5 pass already extended the Exposure-tab paragraph with the direct-held-ETF-branch mechanism (confirmed by grep, line 88); the order's conditional scope item did not apply
  - epic-roadmap.md's "Open items" list has no existing bullet naming tech-debt-register.md:186 (confirmed by direct read of lines 15-53, and by 02-delivery-brief.md's own earlier finding that no such bullet exists) — nothing to narrow there; no edit made
  - the two non-blocking review-gate carries (golden fixture no longer exercises SBIO's positive path end-to-end; RecordingMarketData's misleading docstring) are recorded in the PRD's Notes section only, not filed as new tech-debt-register.md rows, per this order's non_goals

risks:
  - capabilities/docs.md's "Never: create a PRD file. That belongs to story authoring" pack convention directly conflicts with this order's DoD, which explicitly required creating docs/product/prd/epic-39-...md — per PROTOCOL.md's "pack convention does not block the order" rule, I followed the order (status: PARTIAL reflects this) rather than silently complying; a human should confirm this repo's actual PRD-authorship convention, since two prior epics (37, 38) already show docs-engineer creating close-out PRDs in practice, suggesting the pack line itself may be stale
  - none of this pass's edits were re-verified by any command (no Bash granted); all factual content (test counts, AC/ticket dispositions, T-39.1.7 detail) is drawn directly from 07-14's own reports, cross-checked against each other where they overlapped (e.g. 13-integration.md's correction of 08-backend.md's cache-key-typo claim, which I did not repeat)
