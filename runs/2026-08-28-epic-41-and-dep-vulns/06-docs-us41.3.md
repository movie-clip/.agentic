REPORT 2026-08-28-epic-41-and-dep-vulns/06
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/correlation-fields.md — AC2: the `**Backend schema:**` line for `RollingRiskPoint` (L84) now cites `services/quant-engine/app/schemas/reconciliation.py` — `RollingRiskPoint` (class at reconciliation.py:122), keeping `analytics/risk.py` — `build_rolling_risk_series` as a parenthetical "series assembled by" reference
  - CLAUDE.md — AC5: added a dedicated "Where to find what" doc-map row for `docs/contracts/currency-risk-fields.md`, directly after the `risk-fields.md` row and in the same form (Currency Risk Contribution contract, Epic 26)
  - docs/product/current-product-state.md — AC3: corrected one non-methodology factual staleness in the Backend section — "~16 service files" → "~25 service files" (the `app/services/` directory holds 25 non-`__init__` modules today)
  - docs/product/epic-roadmap.md — AC4: swapped the Epic 23 and Epic 24 `---`-delimited section blocks so per-epic sections run strictly descending (… 26, 25, 24, 23, 22 …); pure block move, no heading/PRD-link/goal/story-snapshot/slice-log content reworded or dropped
  - docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md — ticked AC1-AC6 and tickets T-41.3.1/T-41.3.2/T-41.3.3; appended a dated `## Notes / decisions` sub-block recording the AC1 confirmation, the AC2 factor-drift N/A, the AC3 audit outcome (one edit, no methodology staleness), the AC4 block move, and the AC6 already-closed table

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs lane has no Bash; the orchestrator runs `python scripts/run_all_tests.py` after orders 06 + 07 land

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - quant referral: the terminal reconciliation adjustment is stated as "−$58.11" (financial-methodology.md:2425) and "−$19.98" (financial-methodology.md:581 / 587 / 2427) while story US-34.3 states "−$53.13" — the −$53.13 is unreconciled with either figure; scout § F flagged this 2026-08-27 and it is still live. Methodology-doc figure reconciliation, out of scope for this docs order (non_goals bar editing financial-methodology.md)
  - AC4's mechanical guard is T-41.3.4 (separate test-engineer order): epic-roadmap.md now carries 33 `## Completed Epic: Epic <N> —` headings in strict descending order (Epic 40 → Epic 8); the guard should assert strictly-descending epic numbers plus a non-vacuous-scan check
  - AC3 body re-audit of current-product-state.md surfaced no methodology or trust-semantics staleness — no quant-audit is needed for this story on AC3 grounds; the mid-run quant-referral branch DESIGN flagged did not fire
  - prd/README.md and stories/README.md required no edits — every scout § B-G residue item (stale epic labels, missing Epic 30 heading, build-story prose, "Epic 5 Active" index, Epic 40 "PRD: none" pointers, non-monotonic order) was already closed by US-41.2 or the 2026-08-27 docs passes; see the story's dated `## Notes / decisions` table

risks:
  - AC1's confirmation note was written into the story file's `## Notes / decisions` per this order's DoD wording; DESIGN § Item 1 had instead suggested `correlation-fields.md`'s own `## Notes / decisions`. Followed the order. correlation-fields.md has no `## Notes / decisions` section, so the story file was also the practical home; no table edit was needed either way since the columns already match types.ts
  - The AC3 "~16 → ~25 service files" edit sits on the line between "shipped-feature description with no trust claim" (correctable in place per AC3) and an architecture-inventory count; treated as non-methodology factual staleness and corrected. A reviewer who reads it as out-of-remit can revert that one line without affecting any other AC
  - Story `Status:` left as `Next phase` — not flipped to `Done`. AC7 (full suite) is unverified and the integration/review gates have not run; the order did not instruct a status change
