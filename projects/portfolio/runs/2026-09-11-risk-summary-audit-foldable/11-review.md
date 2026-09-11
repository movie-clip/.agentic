REPORT 2026-09-11-risk-summary-audit-foldable/11
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd apps/desktop && npx vitest run
  result:    FAIL
  detail:    2 of 380 tests fail (42 files, 40 pass/2 fail) — RiskSummaryCard.test.tsx:88 (AC4 test) and DashboardPanel.test.tsx:436 (pre-existing trust-label test) both assert stale copy; see § Verification detail

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - RiskSummaryCard.test.tsx:88 and DashboardPanel.test.tsx:436-444 assert the pre-10-frontend.md copy "Risk contribution basis: Verified" — both need the "(adjusted-close price provenance only)" text before `npx vitest run` is green again.
  - Per 10-frontend.md's own handoff ("Test lane: add/update a Vitest assertion…"), this reconciliation belongs to the trust-gate slice's test step, not a T-45.1.1/T-45.1.2 defect — re-request this review once the suite is green.

risks:
  - 07-test.md ("380 tests passed") and 08-integration.md (PASS) were both accurate when each ran; 10-frontend.md's copy edit landed afterward in the same uncommitted working tree and silently invalidated both without re-triggering either gate.
  - RiskSummaryCard.tsx is not in designSystem.audit.test.ts's ALL_CARD_FILES list (pre-existing, not introduced by this story) — the story's AC/test-plan claim that the audit "still passes against the modified card" is true only because the card is outside the audit's scope, not because it was checked.

## Orchestrator brief
US-45.1's own diff (T-45.1.1 fold/expand toggle, T-45.1.2 tests) is complete and
correct: AC1-AC6, AC8 verified SATISFIED with passing tests. AC7 is satisfied by
this story's own diff in isolation, but the actual working tree right now also
carries an unrelated, concurrent slice's edit (10-frontend.md, explicitly out of
this order's scope) to the same trust-label sentence in RiskSummaryCard.tsx,
which breaks 2 tests (1 from this story's own T-45.1.2 suite, 1 pre-existing).
`npx vitest run` — the order's own verification command — fails as a result.
Verdict is FAIL on that basis alone; § Acceptance criteria, § Test plan fidelity,
§ Trust-state spot checks (AC7), § Verification detail below give the full
evidence trail. No fix needed in T-45.1.1 or T-45.1.2 — see handoff.

## Acceptance criteria (US-45.1)

- **AC1 (default expanded):** SATISFIED. `RiskSummaryCard.tsx:42` —
  `useState(true)`. Test: `RiskSummaryCard.test.tsx:23-32` — passes.
- **AC2 (single toggle control):** SATISFIED. One `<button>` at
  `RiskSummaryCard.tsx:76-93`, `onClick={() => setExpanded(!expanded)}`. Test:
  `RiskSummaryCard.test.tsx:39` asserts exactly one button matching
  `/Risk Summary/i`; toggle-then-re-expand at lines 68-78 — passes.
- **AC3 (collapsed hides detail):** SATISFIED. `{expanded && (...)}` at
  `RiskSummaryCard.tsx:97-160` wraps all 12 stat rows including the conditional
  `showRelativeRisk` pair. Tests: `RiskSummaryCard.test.tsx:34-55` (all 12 rows
  queried absent) and `:57-66` (conditional rows) — both pass.
- **AC4 (collapsed compact header):** SATISFIED in this story's own diff — the
  header (`panel-label` + toggle) and the trust-label `<p>` sit outside the
  `{expanded && ...}` block (`RiskSummaryCard.tsx:73-95`), so both always
  render. The dedicated test (`RiskSummaryCard.test.tsx:80-90`) currently FAILS
  — not because the header/trust-label stopped rendering, but because its exact
  text assertion is stale against an unrelated concurrent edit; see §
  Verification detail.
- **AC5 (aria-expanded legible to AT):** SATISFIED. `aria-expanded={expanded}`
  and `aria-controls={detailId}` at `RiskSummaryCard.tsx:78-79`, matching
  `DrawdownAnalyticsCard.tsx:494-496`'s convention. Tests:
  `RiskSummaryCard.test.tsx:92-114` — both pass.
- **AC6 (scoped to this card):** SATISFIED. `DashboardPanel.test.tsx:509-539`
  renders the full Dashboard, collapses Risk Summary, and re-asserts
  Performance & Benchmark, Sector Composition, and Benchmark Positioning cards'
  content is unchanged — passes.
- **AC7 (no change to values/trust rendering):** SATISFIED by this story's own
  diff — `git diff HEAD -- RiskSummaryCard.tsx` shows the toggle change touches
  only the fold state and wrapping `<div>`, never a formatter, a value, or
  `sectionTrustLabel`. Caveat: the merged working-tree state also carries an
  unrelated concurrent edit to the trust-label sentence (out of this order's
  scope per non_goals) that does currently alter what the trust indicator's
  surrounding text reads — see § Verification detail and § Trust-state spot
  checks.
- **AC8 (unavailable state unaffected):** SATISFIED. The early-return branch
  (`RiskSummaryCard.tsx:51-61`) is untouched by the diff — no button, no
  `expanded` reference. Tests: `RiskSummaryCard.test.tsx:116-136` (null
  diagnostics and partial sub-sections, both assert `queryByRole('button')` is
  null) — both pass.

## Test plan fidelity

- Colocated `RiskSummaryCard.test.tsx` (new, 10 `it` blocks) covers every
  behaviour the story's test plan names: default-expanded, toggle
  collapse/re-expand, conditional relative-risk rows, collapsed header +
  trust-label content, `aria-expanded`/`aria-controls` transitions, both
  unavailable-state variants, and an AC7 value/trust regression pin.
- `DashboardPanel.test.tsx` gained exactly the one test the plan names
  (`:509-539`), covering AC6's sibling-card-unaffected requirement.
- `designSystem.audit.test.ts` was not modified and its own suite run clean
  (not among the 2 failures) — but see the risks bullet: `RiskSummaryCard.tsx`
  was already outside `ALL_CARD_FILES` before this story, so "still passes" is
  true by non-coverage, not by a check that ran and cleared.
- Actual count of failing vs. passing: `npx vitest run` → 42 files (40 pass, 2
  fail), 380 tests (378 pass, 2 fail). This contradicts 07-test.md's claimed
  "42 test files passed, 380 tests passed" and 08-integration.md's PASS —
  both were true at the time each ran (see § Verification detail).

## Trust-state spot checks (AC7)

- Trust label vocabulary (`verified`/`degraded`/`unavailable`) and its mapping
  (`sectionTrustLabel`, `RiskSummaryCard.tsx:23-32`) are untouched by this
  story's diff — the classification logic itself did not change.
- Nullable metrics still render `n/a` via `formatPct`/`formatRatio`
  (`RiskSummaryCard.tsx:6-12`), never `0` or `""` — unchanged by this story;
  confirmed by `RiskSummaryCard.test.tsx:138-150`'s AC7 regression pin, which
  passes.
- The surrounding trust-label sentence text ("Risk contribution basis…") did
  change in the current working tree, from a source outside this order's
  scope (10-frontend.md) — flagged, not evaluated, per non_goals.

## Verification detail

`cd apps/desktop && npx vitest run` against the current working tree fails 2
tests:

1. `RiskSummaryCard.test.tsx:88` — `AC4: collapsed state still renders the
   title and trust label, no stat rows` — asserts
   `screen.getByText('Risk contribution basis: Verified')`.
2. `DashboardPanel.test.tsx:436` (pre-existing, US-25.3) —
   `trust label follows section_trust.risk_contribution_path across its three
   states` — asserts the same pre-edit copy at lines 436, 440, 444.

Both fail because `RiskSummaryCard.tsx:95` currently reads `Risk contribution
basis (adjusted-close price provenance only): {trust}` — confirmed via `git
diff HEAD` to be an edit from 10-frontend.md (the concurrent, explicitly
out-of-scope trust-gate fixes slice), landed in the same uncommitted working
tree after 07-test.md's tests were written and after 08-integration.md's PASS.
10-frontend.md's own handoff already names the needed test update
("Test lane: add/update a Vitest assertion…") — it has not happened yet.
`mcp__project__check_gates` confirms deadcode and typecheck are clean and
goldens are not drifted; the only red is these 2 vitest tests.
