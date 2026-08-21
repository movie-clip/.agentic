REPORT 2026-08-21-dynamic-sector-classification/03
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-24.12-dynamic-equity-sector-classification.md — new Backlog story draft (F-A only), for human review

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field is NONE (drafting only); no Bash/shell tool was available this session to run check_report.py's self-check — see risks

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Story path: docs/product/stories/US-24.12-dynamic-equity-sector-classification.md — Status: Backlog, not yet ticketed
  - Ticket list (4, ordered): T-24.12.1 equity resolution logic (backend) — AC1-AC8; T-24.12.2 aggregation follow-through + caching (backend) — AC9; T-24.12.3 docs (methodology + exposure-fields.md); T-24.12.4 tests (test-engineer)
  - Open decision (blocking ticketing) 1/4: naming of the classification-provenance field/enum — schema owner's call, candidate name flagged non-binding
  - Open decision (blocking ticketing) 2/4: exact nullability wiring of `sector` through analytics/overview.py's sector-aggregation dict-keyed-by-string code
  - Open decision (blocking ticketing) 3/4: whether the ISIN-mismatch case needs its own exposed withheld-adjacent state or collapses into unavailable
  - Open decision (blocking ticketing) 4/4: caching/persistence shape — widened TTL vs a persisted classification record, research brief calls this a "should" not a hard block
  - Filing note, not a blocking decision but flagged for confirmation: this draft numbers the story US-24.12 (reopening the closed Epic 24) because F-A directly closes that epic's own tagged tech-debt row; the human may reassign the epic number without touching anything else in the draft
  - Judgment call, not a blocking decision: no frontend ticket included — ExposurePanel.tsx already renders top_sectors generically off whatever bucket labels the engine returns; flagged explicitly in the story's Notes section for the design pass to override if it disagrees
  - A second backend call site (analytics/overview.py:50) must change alongside registry.py or the "no more Other" fix will not reach the UI — its own get_sector() fallback silently re-coerces a None sector back to "Other"; documented in the story's Context and folded into T-24.12.2

risks:
  - This session had no Bash/shell tool available, so check_report.py could not actually be run against this artifact — self-check per lane instructions was attempted but not executed; the orchestrator's own run of it is the first real check
  - This is a draft for human review, not an approved story — status is Backlog and nothing here has been ticketed or dispatched
  - Epic-number assignment (24, reopening a closed epic) is this draft's own judgment call per the "Filing note" in the story file, not a re-litigation of the human's already-made "no new epic" decision — confirm before ticketing
  - The no-frontend-ticket call is a judgment based on reading ExposurePanel.tsx's current generic rendering; if the design pass wants a distinct visual treatment for the new unclassified state (a possibility the research brief raises but does not require), a frontend ticket needs adding at that point
  - I did not independently re-verify the research brief's live-FMP findings (INTU/PANW/VICI/SPCX classifications, the 5-of-11 taxonomy divergence, the DFNS collision reproduction) — carried forward as reported, per this lane's scope (drafting, not auditing)
  - The research brief's own risks (SPCX data-quality anomaly, ETF-side FMP sector unreliability, the hardcoded `cached: True` flag) are carried into the story's Out of scope section rather than resolved — they are the research brief's open observations, not mine to settle

## Orchestrator brief

- Decision: single Backlog story drafted, F-A (equity branch) only — F-B and the audit-first shape stay out, per the work order's binding scope.
- Decision: filed as US-24.12 (reopening the closed Epic 24) — a judgment call grounded in the tech-debt register's own `epic-24` tag on this code path, not the human's decision restated. Confirm at ticketing.
- Decision: no frontend ticket — Exposure tab's sector rendering is already generic/data-driven; flagged in the story for the design pass to override.
- 4 open decisions carried forward from the research brief, all blocking ticketing — see `handoff` bullets and the story's own `## Open decisions` section (top of file).
- Story lives at `docs/product/stories/US-24.12-dynamic-equity-sector-classification.md` — the canonical artifact; this report does not duplicate its body.
- Next lane: `tech-lead` DESIGN, once the human approves the draft and pulls it into the next phase (settles the 4 open decisions as part of the contract).
- Nothing here blocks re-reading — the story is a draft, not an approval; say so plainly to the human.
