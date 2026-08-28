REPORT 2026-08-27-next-epic-or-story/04
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/README.md — 6 stale epic labels 35/34/32/28/26/24 → "(complete)"; 22/21/20/19 "(completed)" → "(complete)"; Epic 26 section moved above Epic 25 (monotonic descending); new "### Epic 30 — Exposure Improvements (complete)" section created and the 8 US-30.x rows moved into it out of Epic 28; new "### Unassigned / Backlog (no epic)" section indexing US-41.1; Epic 40 "PRD: none" → link to epic-40 PRD; lifecycle-table + footer "build-story" guidance → orchestrate-feature / write-story
  - docs/product/prd/README.md — § Index rewritten: drops the stale Epic 5 "Active" row and the non-existent epic-5/epic-3 PRD references, points at epic-roadmap.md as the authoritative epic index, records the retrospective-PRD / cancelled-Epic-3 / superseded-Epic-5 conventions; rule 5 "build-story" → orchestrate-feature / write-story
  - docs/product/current-product-state.md — header line only: "Updated: 2026-08-19 (after Epic 34 …)" → "Updated: 2026-08-27 (body current through Epic 40 … plus Epics 35–39 and the 2026-08-26 chart-data audit; see epic-roadmap.md …)"; body untouched
  - docs/product/epic-roadmap.md — Epic 40 "**PRD:** none" paragraph → link to epic-40-snapshot-trust-and-fidelity-follow-through.md (Status: Completed, retrospective); "## Epic 33 — … (complete)" → "## Completed Epic: Epic 33 — …"; "## Completed Epic: Epic 8 — Reset to Portfolio Analysis Core" → "… Reset to Analysis Core" (matches PRD filename)
  - docs/product/stories/US-34.3-anchor-opening-cash-on-statement.md — two stale "−$53.13" strings (test-pin line and the F-5 "still cost a day" line) → "−$58.11", matching the story's own AC7/AC8 and its "Measured: −$58.11" line; the deliberate "first estimate of −$53.13 omitted day-one trade cash" narrative left intact
  - docs/product/stories/US-40.1-snapshot-trust-signal-completeness.md — **PRD:** header "none — docs-engineer close-out did not create one" → link to the retrospective epic-40 PRD
  - docs/product/stories/US-40.2-add-snapshot-preserves-imported-history.md — **PRD:** header "none — docs-engineer close-out did not create one" → link to the retrospective epic-40 PRD
  - docs/product/stories/US-41.1-inline-withheld-return-annotation.md — index-placement header note only: records that the file is now indexed under the "Unassigned / Backlog (no epic)" section of stories/README.md, keeps its US-41.1 number and "Epic: Unassigned" / "Status: Backlog" header, and that no renumber applies (owner decided against a new epic)
  - .agentic/projects/portfolio/project.md — pack correction applied: the two stale sentences in § "`build-story` is superseded and must not run" (claiming the skill description "still triggers on build US-X.Y" and "two architectures compete … coin flip") replaced with the verbatim wording from pack-corrections.md

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs lane has no Bash; per the order the orchestrator runs python scripts/run_all_tests.py after this order and 05 land

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - order 06 owns docs/architecture/system-architecture.md; its story file docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md exists on disk but is not yet indexed in docs/product/stories/README.md — order 06 (or its close-out) should add its row, e.g. under a new "### Epic 41" section or the Unassigned/Backlog section depending on the final numbering call
  - epic-roadmap.md has its own non-monotonic per-epic section ordering (Epic 23 section precedes Epic 24) — noticed, not in this order's scope, left for a future roadmap pass
  - the roadmap snapshot header still reads "Updated: 2026-08-25"; not in this order's permitted roadmap edits, but it now predates the Epic 40 PRD link added to that same file's Epic 40 section — a one-line date bump for a future order

risks:
  - the pack-correction replacement wording was applied verbatim per protocol/packs.md ("apply the replacement wording as given, do not rewrite the surrounding paragraph"); it states residual build-story prose "survives only in docs/product/stories/README.md and docs/product/prd/README.md" — this same order removed that prose, so the clause reads as stale on landing. Flagged rather than paraphrased.
  - current-product-state.md body was not re-audited against shipped code (order restricted me to the header line); the new header's "body current through Epic 40" claim rests on 02-scout.md § E and 03-delivery-brief.md § Stories spot-checks, not my own verification
  - US-41.1's placeholder-number question: I indexed it under "Unassigned / Backlog (no epic)" and updated its header note per the order; a sibling file US-41.2 now exists (order 06), so if the owner later opens Epic 41 the US-41.1 number may still need reconciling against that story — recorded in the header note, not resolved here
