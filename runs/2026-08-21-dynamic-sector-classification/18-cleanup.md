REPORT 2026-08-21-dynamic-sector-classification/18
status:      PARTIAL
verdict:     NONE

changed:
  - docs/product/prd/epic-37-dynamic-equity-sector-classification.md — Status header changed "Backlog" → "Completed" (no other content touched)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order specified verification: NONE; confirmed both file states by re-reading them after edit

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - PRD header now reads "Status: Completed (created 2026-08-21)", matching epic-roadmap.md's "Completed Epic: Epic 37" heading and US-37.1's own Status: Done.
  - US-24.12 file was NOT deleted — see risks. If a human confirms it is genuinely disposable, delete with: git rm "docs/product/stories/US-24.12-dynamic-equity-sector-classification.md"

risks:
  - Stop condition triggered on task 1 (US-24.12 delete) — see § US-24.12 tombstone check below.
  - Task 2 (PRD header) has no such ambiguity — re-read after edit, only "Backlog"→"Completed" changed on that one line.

## Orchestrator brief

- Done: PRD status header flipped Backlog → Completed, matching roadmap and story. No other content touched.
- Refused: US-24.12 file not deleted. The order's own stop condition ("if it contains anything beyond a superseded-notice, stop and report") fired — see § US-24.12 tombstone check.
- The file is lines 1-10 redirect banner + lines 12-344 the full original story body, substantively identical to US-37.1 (only epic number, status, filing note, checkboxes differ).
- No other repo file references US-24.12, so leaving it is inert but confusing to a direct reader.
- Human decision needed: delete as-is (banner already disclaims it) vs. have docs-engineer trim it to a bare notice first, then delete.

## US-24.12 tombstone check

Read the full file before deleting, per the order's own instruction: "confirm
it is in fact just a tombstone/redirect notice, not real content, before
deleting — if it contains anything beyond a superseded-notice, stop and report
instead of deleting."

Lines 1-10 of `US-24.12-dynamic-equity-sector-classification.md` are a
superseded/redirect banner. Lines 12-344 are the complete original story body:
Open decisions, Story, Context, AC1-AC10, Test plan, Tickets T-24.12.1
through T-24.12.4, Out of scope, Notes/decisions. That is not a bare tombstone
stub — it is a full duplicate draft.

Diffed against `US-37.1-dynamic-equity-sector-classification.md`: the two are
line-for-line identical in substance except epic number/PRD link (24 → 37),
Status (Backlog → Done), the "Filing note" paragraph (open question →
resolved), every AC/ticket checkbox (unchecked → checked), and the final
"Notes/decisions" bullet (open epic-placement question → resolved note).
Nothing in US-24.12 is missing from US-37.1.

`grep -r "US-24.12"` across the repo returns only the file itself — no other
doc, story, or PRD references it, so leaving it in place breaks no links, but
a reader who opens it directly (rather than following the banner) sees a full
duplicate set of ACs and tickets, not obviously distinguishable from a second
live draft except by reading the banner first.

Two ways to close this out, both requiring a human decision the order did not
delegate to this lane:
1. Confirm "delete it as-is, the banner already disclaims it" — then any lane
   with delete access runs `git rm "docs/product/stories/US-24.12-dynamic-equity-sector-classification.md"`.
2. Ask docs-engineer to first trim the file to just the superseded-notice (an
   in-scope docs edit, not a delete), removing the duplicate body, then delete.
