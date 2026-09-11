REPORT 2026-09-11-risk-summary-audit-foldable/14
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest -q ; cd apps/desktop && npx tsc --noEmit
  result:    PASS
  detail:    Backend re-run independently by this gate: 1004 passed, 0 failed, 50 warnings in 96.12s (matches 13-integration.md's count exactly, not taken on trust). Read-only re-audit; order's own `verification` field was NONE (all findings below come from independent recomputation, not from re-running the suite alone).

contract_notes:
  - docs/finance/financial-methodology.md:1054-1058 and docs/contracts/dashboard-fields.md:238 still state "returns 0.00% at N=1" for `portfolio_volatility_pct` — stale against Fix 4's shipped behavior (`None` at N=1). Already tracked OPEN in run.md (Fix 4 doc correction, per 06-technical-plan.md § Fix 4) and not yet actioned — confirmed still open at time of this re-audit, not a new gap.
  - docs/finance/financial-methodology.md:1141-1145's "Contract rule" for `information_ratio`/`active_return_pct` still names `investor_economics_status` as "the authoritative explanation" for nulls — no longer true post-Fix-2 (nulls are now purely math-layer).
  - Same drift class as 13-integration.md's already-flagged `docs/contracts/diagnostics-fields.md` Refusal-rule staleness, one doc section over — not a newly-discovered gap, additional detail for the same scheduled docs dispatch.

pack_corrections:
  - none

handoff:
  - Docs lane: the two contract_notes above are additive detail for the already-scheduled docs-engineer dispatch (06-technical-plan.md § Fix 1/2/4 doc corrections, run.md Open table lines for dashboard-fields.md:238,242,287 and financial-methodology.md:1141-1149) — no new dispatch needed, just confirms the scope that dispatch must cover.

risks:
  - none

## Orchestrator brief
- VERDICT: PASS. All 5 original findings (F1-F5) independently re-verified resolved or correctly carried; no new financial-correctness defect found in the shipped code.
- F1/F2 (CRITICAL, drawdown + IR/active-return gates): both now key on `historical_sections_available`, confirmed correct at the source (trust_gate.py:244-257, diagnostics_engine.py:187-196) — not just "unwithheld," genuinely right: independently hand-recomputed drawdown (-4.55%), active_return (1.0), tracking_error (96.46), IR (1.84) from raw price/ledger inputs, all match engine output exactly. See § Independent recomputation log.
- F3 (CRITICAL, trust-badge mislabel): frontend copy now reads "Risk contribution basis (adjusted-close price provenance only): {trust}" — verified this scoping is factually accurate: `risk_contribution_path` genuinely measures only benchmark/factor adjusted-close provenance (trust_gate.py:230-236), never the underlying current-weights-×-history synthetic construction. Resolved correctly.
- F4 (MATERIAL, N=1 volatility): independently recomputed — N=1 now returns `None`/`None` for both fields (matches beta/correlation/r_squared convention), N=2 returns real values matching hand-computed stdev*√252*100 exactly (11.22/0.11). Resolved correctly.
- F5 (MINOR, HHI duplication): confirmed still present, unchanged, byte-identical to original audit — correctly carried as OPEN/non-blocking in run.md, not silently dropped.
- New: `investor_economics_status` flip to "available" is a mechanically honest side effect of the same condition, confirmed unrendered anywhere in the frontend (grep: only test/fixture references) — not a trust leak.
- New: 2 contract_notes on stale methodology/contract-doc text (N=1 sentence, IR "authoritative explanation" clause) — both are pre-existing, already-tracked OPEN items being routed to docs-engineer; not new gaps, not blocking.
- § Metrics inventory: one row per card field, old vs new reachable value, resolution status.
- § Findings: no CRITICAL/MATERIAL/MINOR findings against the code; 2 MINOR-grade doc-staleness notes filed as contract_notes instead of findings since they are already tracked and routed.
- § Independent recomputation log has full hand-derivation, each anchored `closed-form hand-computed` against the actual diagnostics engine run (not the methodology doc).

## Metrics inventory

| # | UI label | Field | Old reachable value | New reachable value (verified) | Status |
|---|---|---|---|---|---|
| 1 | Portfolio Volatility | `volatility_summary.portfolio_volatility_pct` | `0.0` at N=1 | `None` at N<2, real value at N≥2 | FIXED — recomputed |
| 4 | Benchmark Volatility | `volatility_summary.benchmark_volatility_pct` | `0.0` at N=1 | `None` at N<2, real value at N≥2 | FIXED — recomputed |
| 5 | Current Drawdown | `drawdown_summary.current_drawdown_pct` | always `None` | real value when `historical_sections_available` | FIXED — recomputed |
| 6 | Max Drawdown | `drawdown_summary.max_drawdown_pct` | always `None` | real value when `historical_sections_available` | FIXED — recomputed |
| 13 | Information Ratio | `relative_risk.information_ratio` | always `None` | passes through math-layer output | FIXED — recomputed |
| 14 | Active Return | `relative_risk.active_return_pct` | always `None` | passes through math-layer output | FIXED — recomputed |
| — | "Risk contribution basis" label | `run_metadata.section_trust.risk_contribution_path` (rendered text only) | plain "Verified" | "Risk contribution basis (adjusted-close price provenance only): Verified" | FIXED — verified scoping honest |
| 7-12 | Factor/Position HHI, Top-N Risk Share | `risk_concentration_summary.*` | unchanged | unchanged | NOT TOUCHED — correctly out of scope (F5 duplication carried) |
| — | `run_metadata.investor_economics_status` (unenumerated field, not on card) | `DiagnosticsRunMetadata.investor_economics_status` | always `withheld` | `available` whenever `historical_sections_available` and both gates open | CONFIRMED BENIGN — not rendered by any frontend component |

## Findings

No CRITICAL, MATERIAL, or MINOR findings against the shipped code. All prior findings independently confirmed resolved (F1-F4) or correctly carried untouched (F5). Two doc-staleness items are recorded as `contract_notes` above rather than findings, because they are pre-existing, already-tracked OPEN items awaiting the scheduled docs-engineer dispatch, not defects introduced or missed by this slice.

## Independent recomputation log

All computed with `"/c/Program Files/Python312/python"` directly against `services/quant-engine/app` modules and the real `DailyPortfolioState`/`ImportedPortfolioSnapshot` schemas (not hand-rolled duck-typed objects), `pytest.ini`'s `--disable-socket` respected (no network calls).

1. **N=1 volatility, anchor: closed-form hand-computed.** Two daily states (2025-01-02: $1000, 2025-01-03: $1010), two-day benchmark series. `build_portfolio_risk_summary` → `observations=1`, `portfolio_volatility_pct=None`, `benchmark_volatility_pct=None`, `portfolio_beta=None`, `portfolio_correlation=None`, `r_squared=None`. All six fields now null together — matches the audit's original expectation for the N<2 case and `test_analytics.py::test_build_portfolio_risk_summary_volatility_is_none_not_zero_at_n_equals_one`, independently re-derived, not just re-read.
2. **N=2 volatility, anchor: closed-form hand-computed.** Three states (1000→1010→1030.2 portfolio; 100→101→102 benchmark). Engine: `portfolio_volatility_pct=11.22`, `benchmark_volatility_pct=0.11`. My independent `statistics.stdev(returns)*sqrt(252)*100` in a fresh script (not reading risk.py's implementation) reproduced `11.22`/`0.11` exactly — matches 01-quant-audit.md's original log item 1 too, confirming Fix 4 changed only the N=1 guard, not the N≥2 formula.
3. **Diagnostics drawdown + relative risk, anchor: closed-form hand-computed against a real ledger-replay run.** Ran `run_imported_diagnostics_engine` directly (mocked `MarketDataService`, no route/socket needed) with AAPL bought 10 sh @ $100 on 2026-04-10, price path 100→110→105, benchmark SPY 100→105→104, factor proxies flat-ish. Engine output: `drawdown_summary.current_drawdown_pct=-4.55`, `max_drawdown_pct=-4.55`, `relative_risk.active_return_pct=1.0`, `tracking_error_pct=96.46`, `information_ratio=1.84`.
   - **Drawdown, hand-derived independently of risk.py/drawdown.py:** trade-neutral market-value chain (cash excluded per diagnostics_engine.py:318-327's documented basis) gives daily returns +10.00% (4/11) and −4.5455% (4/14); wealth index 100→110.0→105.0; running peak after 4/14 is 110.0; drawdown = 105.0/110.0 − 1 = −4.5455% → rounds to −4.55%. Matches exactly.
   - **Active return, hand-derived:** compounded portfolio return = 1.10 × 0.954545… − 1 = 5.00%; compounded benchmark return = 1.05 × 0.990476… − 1 = 4.00%; active_return = (5.00 − 4.00) = 1.00. Matches exactly.
   - **Tracking error, hand-derived:** daily active returns 5.00% and −3.5930%; sample stdev (N−1=1) = 6.0761%; annualized ×√252×100 = 96.459 → rounds 96.46. Matches exactly.
   - **Information Ratio, hand-derived:** mean active return 0.7035% × 252 = 177.29%; divided by tracking_error fraction 0.96459 = 1.8380 → rounds 1.84. Matches exactly.
   - This is a genuine external anchor (hand re-derivation from raw price/ledger inputs written independently of `risk.py`'s code, not from re-reading the methodology doc's phrasing) and it reproduces every one of the four newly-unwithheld numbers exactly — F1/F2 do not merely stop withholding, they publish correct values.
4. **Trust-state honesty at the unavailable boundary, anchor: source read + `build_unavailable_diagnostics_result`.** Confirmed the `historical_sections_available=False` path (diagnostics_engine.py:484-539) builds `section_trust` and `investor_economics_status` by explicitly passing `historical_sections_available=False`/`allow_*_outputs=False` through the same functions Fix 1/Fix 2 touch, never conflating "unavailable" with "withheld" or leaking a value on the closed path. `withheld`/`unavailable`/`verified` remain distinct at every boundary checked.
5. **F3 label accuracy, anchor: source read.** `risk_contribution_path` (trust_gate.py:230-236) is computed solely from `benchmark_return_basis`/`factor_return_basis` (adjusted-close field presence) — confirmed it carries no information about the current-weights-×-history construction underneath Factor HHI/Position HHI/top-N risk shares. The shipped copy "Risk contribution basis (adjusted-close price provenance only): {trust}" (RiskSummaryCard.tsx:95) is therefore a factually accurate scoping, not just a softened word choice.
6. **F5 duplication, anchor: source read.** `risk.py:2031-2035` and `exposure_engine.py:257-260` `_herfindahl_index` are still byte-identical duplicate implementations with divergent `None`-handling, exactly as the original audit found — zero lines changed in either function. Confirmed via direct `grep` against both files.
7. **Regression suite, anchor: independently re-run, not read.** `cd services/quant-engine && python -m pytest -q` → 1004 passed, 0 failed (matches 13-integration.md's count independently). `npx tsc --noEmit` in `apps/desktop` → exit 0 (spot-check only; full frontend suite not re-run by this gate since no frontend math changed since 13-integration's independent run).
