REPORT 2026-09-11-risk-summary-audit-foldable/15
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd apps/desktop && npx vitest run
  result:    PASS
  detail:    42 test files passed (42), 380 tests passed (380), 0 failed. Re-ran myself against the current working tree, not taken on 12-test.md's or 13-integration.md's word. mcp__project__check_gates confirms deadcode clean (ruff/vulture/knip), tsc clean, goldens not drifted.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - RiskSummaryCard.tsx is still absent from designSystem.audit.test.ts's ALL_CARD_FILES list (:44-81) — pre-existing, not introduced by this story; see § Test plan fidelity.
  - The audit "still passes against the modified card" claim is true only because the card sits outside the audit's scope, not because a check ran and cleared it.
  - docs/product/stories/US-45.1-dashboard-risk-summary-foldable.md:3 still reads "Status: Backlog" though the story is fully implemented, tested and gate-passed — a docs-lane close-out item, not a reviewer-blocking defect.

## Orchestrator brief
VERDICT: PASS. § Acceptance criteria (US-45.1) — all 8 ACs re-verified SATISFIED
against the current working tree; the two tests stale in 11-review.md
(RiskSummaryCard.test.tsx:88, DashboardPanel.test.tsx:437) now assert the
reconciled copy "Risk contribution basis (adjusted-close price provenance
only): {trust}". § Test plan fidelity — all named test files/counts present,
independently re-run (42/42 files, 380/380 tests). § Trust-state spot checks —
no masked regression in trust-state rendering; nullable-as-dash and
verified/degraded/unavailable vocabulary unchanged by this story. §
Verification detail — `npx vitest run` re-run by this gate itself, green,
plus check_gates confirms deadcode/typecheck/goldens all clean. No BLOCKING
or SHOULD_FIX findings; the two `risks` bullets are pre-existing, non-blocking
observations (audit-list coverage gap, stale story status field) carried
forward for visibility. Nothing to dispatch back to any lane.

## Acceptance criteria (US-45.1)

- **AC1 (default expanded):** SATISFIED. `RiskSummaryCard.tsx:42` — `useState(true)`. Test: `RiskSummaryCard.test.tsx:23-32` — passes.
- **AC2 (single toggle control):** SATISFIED. One `<button>` at `RiskSummaryCard.tsx:76-93`, `onClick={() => setExpanded(!expanded)}`. Test: `RiskSummaryCard.test.tsx:39` asserts exactly one matching button; toggle-then-re-expand at lines 68-78 — passes.
- **AC3 (collapsed hides detail):** SATISFIED. `{expanded && (...)}` at `RiskSummaryCard.tsx:97-160` wraps all 12 stat rows including the conditional `showRelativeRisk` pair. Tests: `RiskSummaryCard.test.tsx:34-55` and `:57-66` — both pass.
- **AC4 (collapsed compact header):** SATISFIED. Header (`panel-label` + toggle, `RiskSummaryCard.tsx:74-93`) and the trust-label `<p>` (`:95`) sit outside the `{expanded && ...}` block, so both always render. Test `RiskSummaryCard.test.tsx:80-92` now asserts the current copy "Risk contribution basis (adjusted-close price provenance only): Verified" (reconciled by 12-test.md) — passes; re-run confirmed.
- **AC5 (aria-expanded legible to AT):** SATISFIED. `aria-expanded={expanded}` and `aria-controls={detailId}` at `RiskSummaryCard.tsx:78-79`, matching `DrawdownAnalyticsCard.tsx`'s convention. Tests: `RiskSummaryCard.test.tsx:94-116` — both pass.
- **AC6 (scoped to this card):** SATISFIED. `DashboardPanel.test.tsx:515-539` ("collapsing the Risk Summary card leaves sibling Dashboard cards unchanged") renders the full Dashboard, collapses Risk Summary, re-asserts Performance & Benchmark, Sector Composition, Benchmark Positioning cards' content unchanged — passes.
- **AC7 (no change to values/trust rendering):** SATISFIED. `git diff HEAD -- RiskSummaryCard.tsx` confirms the toggle change touches only the fold state and wrapping `<div>`, never a formatter, a value, or `sectionTrustLabel` (`:23-32`). The concurrent Fix 3 sentence-copy edit (10-frontend.md, out of this story's scope) coexists cleanly — it changed only surrounding prose text, not the value/trust logic — and is independently gated PASS by 13-integration.md. Regression pin: `RiskSummaryCard.test.tsx:140-152` — passes.
- **AC8 (unavailable state unaffected):** SATISFIED. Early-return branch (`RiskSummaryCard.tsx:51-61`) untouched by the diff. Tests: `RiskSummaryCard.test.tsx:118-138` (null diagnostics and partial sub-sections, both assert `queryByRole('button')` is null) — both pass.

## Test plan fidelity

- Colocated `RiskSummaryCard.test.tsx` (new, 10 `it` blocks) covers every behaviour the test plan names: default-expanded, toggle collapse/re-expand, conditional relative-risk rows, collapsed header + trust-label content, `aria-expanded`/`aria-controls` transitions, both unavailable-state variants, and the AC7 value/trust regression pin.
- `DashboardPanel.test.tsx` gained exactly the one test the plan names (`:515-539`), covering AC6.
- `designSystem.audit.test.ts` was not modified by this story and its own suite runs clean — but `RiskSummaryCard.tsx` is not, and was never, in its `ALL_CARD_FILES` list (:44-81), so "still passes" is true by non-coverage, not by a check that ran and cleared it (pre-existing gap, not introduced here).
- Actual re-run count: `npx vitest run` → 42 files passed (42), 380 tests passed (380), 0 failed — matches 12-test.md's and 13-integration.md's reported counts; independently confirmed, not taken on their word.

## Trust-state spot checks

- Trust label vocabulary (`verified`/`degraded`/`unavailable`) and its mapping (`sectionTrustLabel`, `RiskSummaryCard.tsx:23-32`) are untouched by this story's diff.
- Nullable metrics still render `n/a` via `formatPct`/`formatRatio` (`RiskSummaryCard.tsx:6-12`), never `0` or `""` — confirmed by `RiskSummaryCard.test.tsx:140-152`'s AC7 regression pin, which passes.
- The surrounding trust-label sentence ("Risk contribution basis (adjusted-close price provenance only): {trust}", `RiskSummaryCard.tsx:95`) reflects the reconciled copy from the concurrent Fix 3 slice; `RiskSummaryCard.test.tsx:89` and `DashboardPanel.test.tsx:437,443,449` all assert this exact text across all three trust states (Verified/Degraded/Unavailable) — no stale assertions remain, no masked regression in trust-state rendering.
- No new market-data caller introduced by this story; no schema field introduced or removed — presentation-only change, as the story's own § Notes states.

## Verification detail

`cd apps/desktop && npx vitest run` against the current working tree: 42 test files passed (42), 380 tests passed (380), 0 failed, ~5.8s. Both previously-stale assertions (`RiskSummaryCard.test.tsx:88-90`, `DashboardPanel.test.tsx:436-450`) now match the current rendered copy exactly — confirmed by reading both files directly, not just re-running the suite. `mcp__project__check_gates` confirms deadcode clean (ruff/vulture/knip), `tsc --noEmit` clean, goldens not drifted, commit-gate marker present. No mechanical gate is red.
