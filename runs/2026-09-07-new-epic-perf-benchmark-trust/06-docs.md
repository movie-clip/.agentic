REPORT 2026-09-07-new-epic-perf-benchmark-trust/06
status:      DONE
verdict:     NONE

changed:
  - docs/product/epic-roadmap.md — CREATED. Fresh minimal skeleton; header records the ce9c97d removal and the 2026-09-07 human decision (fresh skeleton, Epics 1–43 stay in git). One epic entry: Epic 44 "Performance & Benchmark Trust", Status Planned/Backlog, four stories US-44.1..US-44.4 (one line each, linked), sequence US-44.1 → [US-44.2 parallel] → US-44.3 → US-44.4, empty slice log.
  - docs/product/prd/epic-44-performance-benchmark-trust.md — CREATED. House PRD format (Epic 34 / Epic 43 reference): problem, goal, findings F-1..F-4 (one per reported point, each with 01-recon file:line evidence and the guardrail it implicates), story breakdown table (outcome / lanes / quant-gated? / sequencing), epic sequence, "Not in scope", "Open decisions still pending", Status: Planned. No slice log, no delivered claims.
  - docs/product/prd/README.md — CREATED. Minimal index; one row: Epic 44 → its PRD, Status Planned. Notes the 2026-09-08 rebuild.
  - docs/product/stories/README.md — CREATED. Minimal index; four US-44.x stories each Status Backlog, linked; numbering note (US-<epic>.<n>-<slug>.md, tickets T-<epic>.<story>.<n>) and that no _TEMPLATE.md exists — house format follows the two most recent sibling stories.
  - .agentic/projects/portfolio/capabilities/product.md — pack-correction applied ("Where the plan lives" table + the roadmap-navigation subsection): rows for epic-roadmap.md / prd / stories updated to the rebuilt fresh skeleton; "Navigating the roadmap without reading 1,700 lines" replaced with "The roadmap is short now".
  - .agentic/projects/portfolio/capabilities/story.md — pack-correction applied (§ Files): _TEMPLATE.md row replaced with "the two most recent sibling US-*.md stories"; epic-roadmap.md row annotated as a fresh minimal skeleton since ce9c97d. README.md and epic-roadmap.md rows kept (both exist again).

verification:
  command:   NONE (work order verification field was NONE)
  result:    NOT_RUN
  detail:    Read-only of no command. Four planning docs created under docs/product/, two capability packs corrected; nothing to execute. No tests touched.

contract_notes:
  - docs/contracts/dashboard-fields.md:98-101 (source_status.monthly_returns) needs a line noting a published monthly figure may exclude a withheld/reconciled day — recorded in PRD finding F-1; belongs to US-44.1 close-out (T-44.1.4), not this order.
  - docs/contracts/dashboard-fields.md:105 documents a benchmark_history:"unavailable"-within-a-valid-run state the code cannot currently reach — recorded in PRD finding F-3; belongs to US-44.3 close-out (T-44.3.5), not this order.

pack_corrections:
  - none

handoff:
  - project.md is named in pack-corrections.md entry 1 (§ "Sources of truth", Layout) but is out of scope for this order. Needed change is now minor and non-blocking: epic-roadmap.md / prd/ / stories/ exist again, so line "| Which epic is current? | docs/product/epic-roadmap.md — the authority; PRD pointers in CLAUDE.md go stale |" is accurate; optional refinement is to append "(rebuilt 2026-09-08 as a fresh minimal skeleton; Epics 1–43 history is in git, not the file)". Layout block lines 88-96 are accurate as-is.
  - CLAUDE.md conflicts with the rebuilt surface and is out of scope here (non_goals forbid editing it): it states "Historical implementation tickets and roadmaps are preserved in Git history, not maintained as active documentation" and its "Canonical documentation" table omits epic-roadmap.md and prd/README.md. Needs a follow-up edit to reflect the 2026-09-07 human decision to keep a minimal active roadmap.
  - The four US-44.x story files still carry the "This is a draft for human review. It has not been approved" banner and Status: Backlog, though this order treats Epic 44 and its stories as approved. A story-status pass (or the human) should clear the banner; not touched here per scope.
  - No docs/tech-debt-register.md entry was created for P1-P4 — they are storied under Epic 44, which is the correct home; the register is not in scope for this order.

risks:
  - epic-roadmap.md is now an active planning doc, which contradicts the current CLAUDE.md statement that roadmaps are "not maintained as active documentation". Built to the work order's explicit DoD and the cited 2026-09-07 human decision; the CLAUDE.md conflict is flagged in handoff. Not REFUSED — no numbered project guardrail is broken.
  - PRD findings F-1..F-4 carry no severity labels. The Epic 34 house format tags severities; 01-recon / 02-quant-research / 03-delivery-brief did not assign any to P1-P4, so none were invented.
  - The roadmap header and the product.md pack text suggest `git show ce9c97d^:docs/product/epic-roadmap.md` for the pre-cleanup record; the command is standard git syntax, not executed from this shell-less lane.
