REPORT 2026-09-09-risk-annualized-volatility/10
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   mcp__project__check_gates (dead-code + tsc + goldens + commit-gate) plus a field-by-field read of schemas/diagnostics.py against types.ts and both diagnostics-engine construction paths
  result:    PASS
  detail:    check_gates: ruff/vulture/knip clean, tsc 0 errors, goldens not drifted. Contract structurally identical across the seam. Full run_all_tests.py was green at T-44.1.3 (08). Anchor: independent check_gates run + direct both-sides seam read.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-44.1.4 docs close-out is still open before the human commits: methodology amendment (~line 1012), risk-fields.md new section, diagnostics-fields.md cross-ref, current-product-state.md inventory — per 06's five contract_notes and 07's three copy pins. Not a gate blocker; 05 § 6 defers doc prose to this lane.
  - The card copy strings ("N of 60", "fewer than {min} paired trading days", "Dashboard shows an unfloored estimate") are pinned by substring match in AnnualizedVolatilityCard.test.tsx and must move with risk-fields.md at docs close-out (08 risk).
  - 06's "three shapes (DiagnosticsEngineResponse, ImportedDiagnosticsSource, the snapshot-request variant)" is loose. `DiagnosticsResult` is the one Pydantic response model; TS has one mirror (`ImportedDiagnosticsSource`) plus its alias `DiagnosticsEngineResponse`, both carrying `risk_tab_volatility`. No unmirrored shape; no "snapshot-request variant" type exists.

risks:
  - AnnualizedVolatilityCard.tsx:38 `formatPct` null branch is unreachable — called only in the `trust === 'synthetic'` block where the backend guarantees non-null. knip does not flag it; the dead-code gate stays green and the commit is not blocked. Left as-is per 09. SHOULD_FIX at most.
  - `diagnosticsAnalysis` is null in App state until the Dashboard diagnostics fetch resolves, and stays null if `analyzeExposureSnapshot` threw; the card then shows LoadingState with no error branch. Pre-existing scout risk, not introduced here.
  - The two backend integration tests in test_risk_tab_annualized_volatility.py depend on the conftest `_mock_price_rows` trading-day cadence for the N>=60 / 2<=N<60 bounds; they assert ranges not exact counts (08 risk).

## Orchestrator brief

- Verdict: PASS. The four engineering lanes integrate cleanly; no change requests, no cr/ files.
- Contract identical across the seam: `RiskTabAnnualizedVolatility` (schemas/diagnostics.py:104) vs `RiskTabAnnualizedVolatility` (types.ts:1148) — same four fields, same nullability, `trust` literal `synthetic|withheld|unavailable` on both, `minimum_observations` required (no default) on both. `annualized_volatility_pct` non-null iff `trust==="synthetic"` holds structurally on both sides.
- 3-vs-2 shape discrepancy resolved: one Pydantic model, one TS mirror + one alias, both carry `risk_tab_volatility`. `ImportedExposureSource` is not a `DiagnosticsResult` mirror (no volatility_summary / drawdown_summary / provenance) and correctly does not carry the field. 07's "two shapes" is right; 06's "three" was loose wording echoing 05's speculative risk bullet.
- Wiring intact: existing App state `diagnosticsAnalysis` threaded App.tsx:912 → RiskPanel prop (RiskPanel.tsx:30) → `<AnnualizedVolatilityCard volatility={diagnosticsAnalysis?.risk_tab_volatility ?? null}>` (RiskPanel.tsx:108), mounted in `.risk-shell-stack` after VarDistributionCard, no new fetch/adapter/route. Existing three cards untouched.
- `build_unavailable_diagnostics_result` refactor (06 risk:3) is behaviour-preserving: the previously-inline `PortfolioRiskSummary(...)` is lifted to a local `risk_summary` (diagnostics_engine.py:484) referenced by both `risk_summary=` and `risk_tab_volatility=_build_risk_tab_annualized_volatility(risk_summary)`; `observations=0` still yields `trust="unavailable"`. No other field on that path changed.
- Gates green (check_gates): dead-code clean, tsc 0 errors, no golden drift. `formatPct` unreachable null branch is not knip-caught and does not block commit — left as-is per 09.
- TrustBadge not extended (07 risk:1): clean. `badge` is `undefined` for withheld/unavailable, CardShell renders no badge, union unchanged, no `withheld` case references a badge component anywhere.
- Open before commit: T-44.1.4 docs close-out (methodology amendment + 3 contract-doc targets + current-product-state) — all captured as contract notes, none dropped; process-deferred, not a gate failure.
- No sections below beyond this brief; all findings are in the report block.
