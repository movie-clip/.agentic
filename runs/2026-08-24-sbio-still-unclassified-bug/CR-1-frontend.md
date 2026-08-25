REPORT 2026-08-24-sbio-still-unclassified-bug/CR-1
status:      DONE
verdict:     NONE

changed:
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.tsx — getBenchmarkTrust now reads only exposure_availability.benchmark_overlap_confidence.
  - apps/desktop/src/features/portfolio/BenchmarkPositioningCard.test.tsx — new file; pins the single-vintage regression from quant-audit Finding 1.
  - apps/desktop/src/features/portfolio/DashboardPanel.test.tsx — one pre-existing test updated to assert via availability.confidence, not run_metadata, to match fixed logic.

verification:
  command:   cd apps/desktop && npx tsc --noEmit ; npx vitest run
  result:    PASS
  detail:    tsc --noEmit: no output (clean). vitest: 38 files, 341 tests, all passed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - Order vs pack conflict on test-writing — see § Test-writing conflict.
  - DashboardPanel.test.tsx test broke as a direct consequence of the fix (asserted old run_metadata path) — updated in same pass, see § Broken-test fix.
  - Confirmed benchmark_symbol fallback at line ~80 (run_metadata.reproducibility.benchmark_symbol) left untouched — display-name only, not trust classification, per order.
  - Confirmed via repo-wide grep that no other function/file reads run_metadata.source_status.benchmark_holdings for trust purposes.

## Orchestrator brief
CR-1 fix landed: getBenchmarkTrust derives the badge entirely from frozen exposure_availability, removing the live run_metadata cross-read that quant-audit Finding 1 found reachable. Two named sections below carry detail beyond the bullet budget: § Test-writing conflict (order vs pack, resolved per protocol — order wins, flagged not blocked) and § Broken-test fix (a pre-existing DashboardPanel test that had to change as a mechanical consequence of the fix). tsc and full vitest both green.

## Test-writing conflict
The order's definition_of_done required writing/extending a test in this frontend-lane order. The frontend capability pack's "Definition of done for this lane" says "No test files touched — that is the test lane; name what needs covering in handoff." Per PROTOCOL.md §"When the order and your capability pack disagree": a pack *convention* (not a numbered guardrail) does not block an order; do what the order says and name the conflict here. This is a pack convention, not one of project.md's five numbered hard guardrails, so I followed the order and wrote/extended the tests as explicitly and unambiguously instructed (not an eager add of my own choosing) — the fix would not be provably correct without a regression test proving it, and the order named the exact scenario to cover.

## Broken-test fix
DashboardPanel.test.tsx's "shows degraded coverage note when benchmark holdings support is degraded" set run_metadata.source_status.benchmark_holdings='degraded' and asserted the degraded badge text — that is exactly the pre-fix (buggy) code path Finding 1 named. After the fix, that field no longer drives the badge, so the test broke as a direct mechanical consequence, not a coincidental collision. I updated it to instead set exposure_availability.benchmark_overlap_confidence='medium' (the frozen field that now drives the badge) and kept the same assertion, renaming the test to describe the new mechanism. This is the minimal edit needed to keep an existing, still-valid assertion ("a degraded coverage note renders under degraded support") true under the corrected logic — not new test surface beyond what the fix required to keep the suite green.
