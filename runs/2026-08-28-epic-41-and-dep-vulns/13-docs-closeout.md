REPORT 2026-08-28-epic-41-and-dep-vulns/13
status:      DONE
verdict:     NONE

changed:
  - docs/product/prd/epic-41-documentation-and-roadmap-accuracy-reconciliation.md — NEW. Structure mirrors epic-36's PRD. Charter line per the owner decision. `2026-08-27` `02-scout.md` § A–I folded into "### Findings and disposition" as F-1..F-15 (each marked: closed by US-41.2 / closed by US-41.3 / closed by this close-out / examined-and-correct / still-open) plus an "### Examined and correct (scout § I)" list. Stories: US-41.1 Backlog (carried Dashboard-trust), US-41.2 Done, US-41.3 Done. Status: Active.
  - docs/product/prd/epic-42-dependency-vulnerability-remediation.md — NEW. Structure mirrors epic-36's PRD. `dependency-advisory-assessment-2026-08.md` F-1..F-6 folded into "### Findings and disposition" (id / source / disposition per 10-docs § handoff). Three-bucket remediation grouping recorded as the forward plan: one backend golden-safe bump story (F-2/F-3/F-4/F-5), one lockfile-only @babel/core story (F-6), F-1 starlette blocked behind a FastAPI-bump story. Broader apps/desktop advisories (vite/esbuild/postcss/nanoid/@vitest/mocker/vite-node) recorded as in-scope-but-unassessed, needs its own story. Stories: US-42.1 Done. Status: Active. Sibling to Epic 21 / Epic 36.
  - docs/product/epic-roadmap.md — snapshot header date → 2026-08-28; "Every epic is complete" and "No epic is active" → "Epic 41 and Epic 42 are active"; the dependency-findings open-items bullet now points at Epic 42; the "Between-epic work shipped 2026-08-27 (no epic)" narrative paragraph replaced by a pointer to the new epic sections. Added "## Epic 42 —" and "## Epic 41 —" sections at the TOP of the epic list (descending 42 → 41 → 40), each with a PRD link, story snapshot, and "### Slice log" rows for US-42.1 (2026-08-28), US-41.2 (2026-08-27) and US-41.3 (2026-08-28) in the file's slice-log format.
  - docs/product/stories/README.md — removed the now-empty "### Unassigned / Backlog (no epic)" group; added "### Epic 42 — Dependency Vulnerability Remediation (active)" (US-42.1 Done) and "### Epic 41 — Documentation & Roadmap Accuracy Reconciliation (active)" (US-41.1 Backlog, US-41.2 Done, US-41.3 Done) groups above Epic 40.
  - docs/product/stories/US-41.1-inline-withheld-return-annotation.md — **Epic:** header field flipped from "Unassigned — Backlog, no epic yet …" to "41 — Documentation & Roadmap Accuracy Reconciliation". Nothing else changed.
  - docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md — **Epic:** header field flipped from "Unassigned — Backlog, no epic yet …" to "41 — Documentation & Roadmap Accuracy Reconciliation". Nothing else changed.
  - docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md — CR-2: **Status:** "Next phase" → "Done"; "Draft for human review" banner removed; dated "## Close-out — 2026-08-28" block appended (gates: integration PASS `11-integration.md`, acceptance PASS `12-review.md`, full suite green backend 949 / frontend 359); AC7 and the T-41.3.4 checkbox ticked (guard shipped and green); PRD header line updated from "docs lane writes this PRD at close-out" to the written path.
  - docs/product/stories/US-42.1-assess-outstanding-dependency-advisories.md — CR-1: "Draft for human review / not owner-approved" banner removed; the "## Open decisions" section's 3 items each marked RESOLVED with disposition (quant sign-off: not required per DESIGN owner decision 2026-08-28 / bucket (b) empty; Epic 42 PRD: written; remediation stories: scoped by the three-bucket grouping); PRD header line updated to the written path.
  - docs/product/current-product-state.md — header date bumped 2026-08-27 → 2026-08-28; parenthetical extended to note the 2026-08-28 US-41.3 body re-audit and that Epic 41 / Epic 42 add no user-visible surface (no body entry, per the doc's feature-only convention).

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs lane has no Bash and the order's verification field is NONE. The orchestrator runs `python scripts/run_all_tests.py` after this order; `test_roadmap_epic_ordering.py` covers the epic-section insert (headings now run strictly descending 42 → 41 → 40 → … → 8).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Epic 42 remediation stories are not authored — the three-bucket grouping in the PRD is the forward plan only; the remediation run is a separate deferred dispatch (one backend golden-safe bump story F-2/F-3/F-4/F-5; one lockfile-only apps/desktop story F-6; a FastAPI-bump story before F-1 starlette).
  - The broader apps/desktop advisories (vite, esbuild, postcss, nanoid, @vitest/mocker, vite-node) flagged by run lanes 09/10 are in Epic 42 scope but unassessed — they need their own US-42.x assessment story before any bump; a bare `npm audit fix` must not be used for F-6.
  - F-10 still open: `financial-methodology.md` states the terminal reconciliation adjustment as −$58.11 / −$19.98 while story US-34.3 says −$53.13 — a standalone quant-lane referral carried from run 2026-08-27 `02-scout.md` § F, out of Epic 41 scope (editing `financial-methodology.md` was barred this run).
  - US-41.1 stays Backlog under Epic 41 — a Dashboard-trust chart-annotation feature, not doc work; it needs its own build run.

risks:
  - The order limited US-41.1 / US-41.2 edits to the **Epic:** header field only, so both files keep now-stale in-body narrative ("Backlog, no epic yet", "shipped as a standalone Backlog story (no epic opened)") in their Open-decisions / close-out prose. Left as instructed; a later docs pass could reconcile that prose to the Epic 41 placement.
  - `current-product-state.md`'s body is feature-only by convention (US-41.2 was likewise recorded only in the header parenthetical, never the body). US-41.3 and US-42.1 are agent/infra-facing with no user-visible surface, so neither got a body entry — the header parenthetical carries the note. Flagged per the order's instruction to say so if the convention is feature-only.
  - The Epic 41 PRD is written with Status: Active rather than at a completed-epic close-out, because the order specifies writing it now and the epic still carries an open Backlog story (US-41.1). All findings and dispositions are transcribed from `02-scout.md` § A–I and the gate reports; none re-judged.
  - After inserting `## Epic 42` and `## Epic 41` headings above `## Completed Epic: Epic 40`, the roadmap's per-epic heading run is 42 > 41 > 40 > … > 8 (strictly descending, verified by grep). `test_roadmap_epic_ordering.py` should stay green but this lane cannot run it — the orchestrator's suite run is the confirmation.
