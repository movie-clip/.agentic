REPORT 2026-08-20-health-review-fold-in/08
status:      DONE
verdict:     NONE

changed:
  - docs/contracts/cache-fields.md — "Last updated" header (line 9) bumped 2026-06-05 → 2026-08-20; prose at the old lines 55-57 rewritten to describe the shipped US-35.2 behavior (namespaces enumerated live from disk via `JsonFileCache.namespaces()`, not hardcoded; a typo'd `--namespace` now rejected with the present namespaces listed, instead of silently reporting "Removed 0 cache file(s).")
  - docs/product/current-product-state.md — "12 route modules" → "15 route modules" (line 96); added `cache.py`, `currency_risk.py`, `provenance.py` rows matching the existing one-line-description style of the other 12
  - docs/product/prd/epic-24-codebase-improvement.md — line 3 status header "Active (started 2026-06-19)" → "Completed", matching the framing of epic-roadmap.md's own "## Completed Epic: Epic 24 — Codebase Improvement" section header (no date invented; the roadmap header carries no completion date to pull, so none was added)
  - docs/architecture/system-architecture.md — added a new paragraph to the "API Boundary" section naming `imports.py`'s filesystem-path acceptance and the absence of server-side auth as a deliberate, accepted tradeoff (not a defect), citing the local-first/single-user design, no-execution guardrail, and CORS restricted to `localhost:5173`/`127.0.0.1:5173` (not wildcard)

verification:
  command:   grep -n "Last updated" docs/contracts/cache-fields.md ; grep -n "route modules" docs/product/current-product-state.md ; grep -n "cache.py\|currency_risk.py\|provenance.py" docs/product/current-product-state.md ; grep -n "Status:" docs/product/prd/epic-24-codebase-improvement.md ; grep -n "imports.py\|unauthenticated\|filesystem-path\|accepted tradeoff" docs/architecture/system-architecture.md
  result:    PASS
  detail: |
    1. `docs/contracts/cache-fields.md:9:**Last updated:** 2026-08-20` — matches today's date, not 2026-06-05.
    2. `docs/product/current-product-state.md:96:15 route modules:` — reads 15, not 12.
    3. `docs/product/current-product-state.md:109: - `cache.py` — market-data cache stats + clear (Epic 20 / US-20.1)`
       `docs/product/current-product-state.md:110: - `currency_risk.py` — currency risk engine (Epic 26)`
       `docs/product/current-product-state.md:111: - `provenance.py` — market-data provenance (FMP vs Yahoo Finance) engine (Epic 18)`
       — all three present.
    4. `docs/product/prd/epic-24-codebase-improvement.md:3:**Status:** Completed` — no longer reads "Active".
    5. `docs/architecture/system-architecture.md:252:**Accepted tradeoff — unauthenticated local file-read (import routes).**`
       `docs/architecture/system-architecture.md:253:`services/quant-engine/app/api/routes/imports.py`'s`
       `docs/architecture/system-architecture.md:258:accepted tradeoff, not an unnoticed defect**: the product is local-first and`
       — new note present.

contract_notes:
  - none. All four edits are prose-only reconciliation against already-shipped behavior; no schema, TS type, or computed value changed (AC7 self-check: only the four in-scope docs files were touched — confirmed no `app/schemas/`, `app/analytics/`, or any `.tsx`/`.ts`/`.py` production file was opened for write in this order).
  - Downstream, unblocked by this order's current-product-state.md fix: T-36.3.2b (test-engineer, `test_route_inventory.py`) can now land green against the corrected "15 route modules" doc rather than red-then-fixed, per the technical plan's sequencing note.

pack_corrections:
  - none. This order made no discoveries contradicting `<agenticRoot>/projects/portfolio/capabilities/docs.md` or `project.md` — both matched the repo state encountered.

handoff:
  - CLAUDE.md's repo-layout route-module list (line 77, `## Repository Layout`) was re-confirmed by direct grep this pass: it already lists all 15 modules (`exposure, dashboard_history, diagnostics, drift, attribution, correlation, stress, drawdown, distribution, provenance, imports, market_data, cache, currency_risk, health`). Per this order's scope, it was not touched. Nothing further needed there.
  - `docs/product/review-2026-08-20-findings.md` was not touched, per non_goals — its retirement (T-36.3.5) remains gated on the Epic 36 PRD existing, which does not exist yet.
  - The epic-24 PRD status line now reads a bare "Completed" with no date, because `epic-roadmap.md`'s own "## Completed Epic: Epic 24 — Codebase Improvement" section header carries no completion date to pull forward — instructed by the work order not to invent one. If the human wants a specific completion date on the PRD header, that is a separate, deliberate addition, not implied by this order's DoD.
  - T-36.3.2b (`test_route_inventory.py`, test-engineer lane) is now unblocked/sequenced-clean against the corrected doc, per the technical plan (`05-technical-plan.md` § US-36.3, "Lane split").

risks:
  - I could not run `python <agenticRoot>/scripts/check_report.py` against this artifact — this session has no Bash/PowerShell tool available (Read/Write/Edit/Glob/Grep only). The orchestrator's own check-report pass should catch anything wrong with this file's shape.
  - The four edits are grounded directly against current repo state (`JsonFileCache.namespaces()` confirmed to exist at `services/quant-engine/app/core/cache.py:116`; `app/api/main.py:11-17` CORS lines confirmed; `imports.py:17-34` confirmed; `epic-roadmap.md`'s Epic 24 header confirmed at line 971) rather than assumed from the technical plan's citations alone — no discrepancy found between the plan's claims and the code.
