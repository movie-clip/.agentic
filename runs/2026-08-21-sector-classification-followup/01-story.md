REPORT 2026-08-21-sector-classification-followup/01
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-37.2-sector-classification-followups.md — new Backlog story, 5 ACs, 4 tickets, filed under existing Epic 37

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE; check_report.py run instead, see below

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Story path: docs/product/stories/US-37.2-sector-classification-followups.md
  - Tickets T-37.2.1 (taxonomy normalization) and T-37.2.2 (cache-flag fix) are both backend-engineer, independent of each other
  - Tickets T-37.2.3 (shared test fixture) and T-37.2.4 (regression tests) are both test-engineer; T-37.2.4 depends on T-37.2.1/.2/.3
  - Open decisions: none — see the story's "Open decisions" section for the explicit statement
  - This is a draft for human review, not an approved story — status is Backlog; the human approves before any lane is dispatched against it

risks:
  - Filed as US-37.2 under existing Epic 37 (no new epic), matching the US-9.6/US-27.9 follow-up-story convention — flagging in case "same pattern as US-37.1 itself" meant something else
  - AC1's normalization is case-insensitive, not just whitespace-stripping; work order left casing to this draft's judgment — grounded in FINDING 2's own reproduced casing variants
  - The same hardcoded `cached: True` bug shape exists in 4 other MarketDataService methods beyond the one named finding (get_company_profile) — left out of scope, no source doc diagnosed those
  - No genuine open decision found blocking ticketing; T-37.2.1/T-37.2.2 look like express-lane candidates (no schema touched) — routing call left to the dispatcher
  - Confirmed by search: no existing test pins the wrong "cached": True value for the profile last_fetch_meta entry, so the cache-flag fix carries low regression risk

## Orchestrator brief

- Decision: filed as US-37.2 under existing Epic 37 (no new epic created) — matches this project's US-9.6/US-27.9 follow-up-story convention.
- Decision: normalization (AC1) covers case as well as whitespace, grounded in FINDING 2's own reproduced variants — see story's Notes / decisions.
- Decision: cache-flag fix scoped to `get_company_profile` only, not the 4 sibling methods with the same bug shape — see story's Out of scope + this report's risks.
- No open decisions block ticketing; story is a **draft for human review**, status Backlog, not approved.
- The full story — statement, 5 ACs, test plan, 4 tickets, out-of-scope, notes/decisions — is in `docs/product/stories/US-37.2-sector-classification-followups.md`, the `inputs` path for whichever lane is dispatched next.
- Two backend tickets (T-37.2.1 taxonomy, T-37.2.2 cache-flag) are independent of each other; two test tickets (T-37.2.3 fixture consolidation, T-37.2.4 regression tests) — T-37.2.4 depends on all three others.
- Possible express-lane candidate (no schema touched, single-lane fixes) — flagged for the dispatcher, not decided here.
