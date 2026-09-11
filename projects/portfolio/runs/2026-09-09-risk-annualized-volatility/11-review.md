REPORT 2026-09-09-risk-annualized-volatility/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py (+ isolated pytest -n auto -q for the backend count)
  result:    PASS
  detail:    Exit 0. Backend pytest 1001 passed / 50 warnings; frontend vitest 369 passed / 41 files; tsc --noEmit clean; dead-code gate (ruff/vulture/knip) clean; dashboard goldens regenerated with no drift. Counts match 08 exactly.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Acceptance PASS. All 12 ACs satisfied by the implementation as built. Every AC->test mapping in 08 was opened and confirmed to assert the AC requirement, not merely to exist. See section AC-by-AC.
  - Routed item 1 (TrustBadge not extended to `withheld`): acceptable. No AC needs a visible badge in the withheld state; AC7/AC8/AC10 met by distinct EmptyState title+detail copy, which plan 05 section 1.5 sanctions.
  - Routed item 2 (LoadingState shown indefinitely if the Dashboard diagnostics fetch threw): acceptable. No AC covers a frontend transport failure; AC9's "no history context" is the server-side unavailable path and is covered.
  - Docs close-out (T-44.1.4) still owes the four doc targets from 05 section 7 / 06 contract_notes. Not gated here; flagged so it is not lost. See section Notes.

risks:
  - Withheld-state copy strings are pinned by substring in AnnualizedVolatilityCard.test.tsx and must move in lockstep with risk-fields.md at docs close-out.
  - Cross-surface coverage uses two run_diagnostics_engine calls on different windows plus one divergent frontend fixture; it still proves equality at N>=60 and divergence at 2<=N<60.
  - Backend integration bounds depend on the conftest _mock_price_rows trading-day cadence; they assert ranges not exact counts, but a cadence change could break them (carried from 08).
  - AC12 methodology pointer renders only in the published state; withheld/unavailable name the 60-day floor in prose but carry no methodology link. Judged sufficient per plan 05 section 1.5.

---

## Orchestrator brief

Acceptance gate verdict: PASS. Nothing to route back to a lane. Suite green with
counts matching 08 (backend 1001, frontend 369).

Sections below:
- AC-by-AC — each of AC1–AC12 categorised SATISFIED with file/test evidence.
- Human ruling — confirms zero-variance-at-floor publishes 0.00% with no withheld branch.
- Trust rendering spot-check — the four card states read directly from source.
- Test plan delivery — every named case maps to a real passing test.
- Notes — outstanding docs close-out targets (T-44.1.4), not acceptance-gated.

## AC-by-AC

- AC1 on the tab: `AnnualizedVolatilityCard` mounted in `RiskPanel.tsx:108` inside `.risk-shell-stack`; `App.tsx:912` threads `diagnosticsAnalysis`. SATISFIED.
- AC2 consistent presentation: `CardShell` + `TrustBadge` + design tokens; added to `designSystem.audit.test.ts` ALL_CARD_FILES / CARDS_WITH_BADGE. SATISFIED.
- AC3 synthetic trust only: `RiskTabVolatilityTrust = synthetic|withheld|unavailable`; badge `type="synthetic"`; no verified/degraded path. SATISFIED.
- AC4 cross-surface equality: `test_run_diagnostics_engine_publishes_and_equals_dashboard_at_or_above_floor` asserts `rtv.annualized_volatility_pct == volatility_summary.portfolio_volatility_pct`. SATISFIED.
- AC5 same computation reused: `_build_risk_tab_annualized_volatility` copies `risk_summary.portfolio_volatility_pct`, no recompute; `test_published_value_is_byte_identical_to_risk_summary_scalar` asserts `.hex()` equality. SATISFIED.
- AC6 published at/above floor: `test_at_or_above_floor_publishes_synthetic_number` (N in FLOOR, FLOOR+1, 252); frontend synthetic block renders `18.27%`. SATISFIED.
- AC7 withheld below floor, no number: `test_below_floor_is_withheld_and_never_exposes_a_value` (N in 1,2,30,58,59) with a real value on the summary; frontend "renders no number, no zero, no dash and no trust badge". `formatPct` is only reachable in the synthetic branch. SATISFIED.
- AC8 withheld names its reason: frontend asserts "12 of 60 paired", "fewer than 60 paired trading days", "Dashboard shows an unfloored estimate". SATISFIED.
- AC9 unavailable when no series: `test_zero_observations_is_unavailable_with_null_value`, `test_build_unavailable_diagnostics_result_marks_risk_tab_volatility_unavailable`; frontend unavailable block. SATISFIED.
- AC10 withheld not collapsed: `test_withheld_serializes_distinct_from_unavailable` asserts distinct `trust` in `model_dump()` and `"unavailable" not in withheld.model_dump_json()`; frontend "withheld vs unavailable are visibly distinct". SATISFIED.
- AC11 never a fabricated zero: `test_n_equals_one_never_publishes_a_zero_on_this_field` (value 0.0, N=1 -> withheld/None); frontend "renders no number, no zero" and "keeps a genuinely computed zero as 0.00%". SATISFIED.
- AC12 methodology reachable: synthetic-state helper text contains "Annualized realized volatility", "60" and the observation count; badge tooltip carries the formula. SATISFIED (published state only — see risks).

## Human ruling

Zero-variance at N >= 60 -> publish 0.00%, no withheld branch:
- `_build_risk_tab_annualized_volatility` has no `vol == 0` branch — only observation-count checks. Confirmed by direct read of `diagnostics_engine.py:455-474`.
- `test_zero_variance_series_at_floor_publishes_0_pct_not_withheld`: N=FLOOR, value 0.0 -> `trust=="synthetic"`, `annualized_volatility_pct == 0.0`.
- Below the floor no number ever appears: `test_n_equals_one_never_publishes_a_zero_on_this_field` and the parametrized withheld test.
- Frontend "keeps a genuinely computed zero as 0.00% (never withheld)": synthetic + value 0 renders "0.00%" with the Synthetic badge.

## Trust rendering spot-check

Read from AnnualizedVolatilityCard.tsx, not the tests:
- withheld (N 1..59): `EmptyState` title "Annualized volatility withheld", detail "{N} of {min} paired ... available. An annualized volatility projected from fewer than {min} paired trading days is not published here. The Dashboard shows an unfloored estimate...". No number, no 0, no 0.00%, no dash. Distinct title+detail from unavailable.
- unavailable (N 0): `EmptyState` title "Annualized volatility unavailable", detail "No paired portfolio and benchmark return history is available for this portfolio yet." No number.
- synthetic (N >= 60): stat row `formatPct` + `TrustBadge type="synthetic"` with formula tooltip + helper line naming the methodology section and the 60-observation floor.
- null prop: `LoadingState` "Computing annualized volatility…".

## Test plan delivery

Every backend and frontend case named in the story Test plan maps to a real passing test (backend `test_risk_tab_annualized_volatility.py` 18 tests; frontend `AnnualizedVolatilityCard.test.tsx` 10, `RiskPanel.test.tsx` four-cards case). Dashboard-unchanged regression: `test_run_diagnostics_engine_withholds_risk_tab_while_dashboard_stays_unfloored_below_floor` asserts `volatility_summary.portfolio_volatility_pct is not None` at 2<=N<60; goldens regenerate clean. `designSystem.audit.test.ts` updated for the new card.

## Notes

Docs close-out targets outstanding (owned by `docs` lane, T-44.1.4): financial-methodology.md "Annualized realized volatility" amendment; risk-fields.md new `risk_tab_volatility` section; diagnostics-fields.md cross-reference; current-product-state.md inventory add. Not acceptance-gated by this story's ACs but required to close the slice.
