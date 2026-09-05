REPORT 2026-08-31-tests-failing-statement-stale/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   independent recompute from docs/IB2026.csv (Open Positions l.226-249, NAV l.14-32, TWR l.20, SBIO trade l.438) + Python recomputation of base weights / HHI / raw mixed sum
  result:    PASS
  detail:    anchor: raw broker CSV + independent numpy-free Python recompute (NOT statement_truths.py, NOT financial-methodology.md). 7/7 anchors CONFIRMED; 2/2 tolerance widenings ACCEPTABLE; all 5 large replay moves explained by window +13 trading days + full re-mark + one SBIO buy + statement TWR 4.77->5.51%.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test lane: scout's stale HHI estimate 0.138194 was correctly discarded; re-pinned IB_POSITION_HHI_BASE 0.135814 is confirmed against raw CSV — no action.
  - reconciliation_adjustment is cross-file consistent at -5.95 (test_ledger_replay_audit.py l.175/l.694, test_portfolio_state.py l.965, test_analytics.py l.8552); anchor.residual consistent at -1.15 across the same three files.

risks:
  - Widening (b) de-dilution tripwire rel=0.02->0.03: observed ratio 1.076 vs predicted 1.052 is 2.32% off — barely over the old band. ACCEPTABLE now, but the 1/(1-w) heuristic is first-order; if it drifts again at the next refresh, add a second-order term rather than widening a third time. See § Widening (b).
  - Replay-derived pins (terminal MV, per-symbol MV, mwr, investment_gain, vols) were checked for consistency with the CSV-anchored statement truths and for direction/magnitude plausibility, NOT recomputed day-by-day — the frozen replay engine was not run in this audit. The statement-truth pins in statement_truths.py WERE independently recomputed from the CSV.
  - Frozen golden's European listings (DEFS.L / SXRV.DE / SEMI.L) end 2026-08-27, one trading day before the statement's 2026-08-28 marks; this one-day lag is the source of the F-4 raw-ratio divergence that drove widening (a). Benign here; a future refresh where the gap widens should refresh the golden's Euro series, not the tolerance. See § Widening (a).

## Orchestrator brief

- VERDICT: PASS. All 7 quant-audit anchors recomputed from raw docs/IB2026.csv are CONFIRMED. Both tolerance widenings are ACCEPTABLE with financial reasoning. All large replay moves flagged by 04b are consistent with the Aug-11->Aug-28 statement delta.
- Anchor used: raw broker CSV (Open Positions / NAV / TWR / trades sections) plus an independent Python recompute of base weights, HHI and the raw mixed-currency sum. NOT statement_truths.py (the artifact under test), NOT the methodology doc.
- No finding. No CRITICAL, no MATERIAL, no MINOR. Nothing routed to the test lane or escalated to the human.
- Guardrails 2-4: the refresh changed no methodology, no schema, no trust-state logic, no return basis, no truth-class boundary. It is a fixture/pin refresh and it stayed one. Reconciliation actually tightened (anchor residual 46.69 -> -1.15; adjustment -19.98 -> -5.95).
- Sections below, by name: Anchor-by-anchor · Tolerance widening (a) — F-4 raw-ratio · Tolerance widening (b) — de-dilution tripwire · Large replay moves (04b) · Trust honesty (guardrails 2-4) · What was NOT independently verified.
- Blocks dispatch: nothing.

## Anchor-by-anchor

All values recomputed from `docs/IB2026.csv` (working tree = Aug-28 export).

### 1. stock_total 65746.67 — CONFIRMED

Open Positions per-currency USD-restated totals (CSV l.229/l.232/l.248):
EUR-restated 13780.99008 + GBP-restated 3905.6596 + USD 48060.02 = **65746.66968**.
= `IB_TOTALS_2DP["stock_total"]` @2dp 65746.67, and = CSV NAV "Stock" Current Total (l.16) exactly.

Σ over 18 positions of `market_value x IB_IMPLIED_FX_4DP[currency]`:
- USD (15 lines) sum = 48060.02 (matches CSV USD subtotal l.248).
- EUR: 11897.6 (DEFS 3074 + SXRV 8823.6) x 1.1583 = 13780.99008.
- GBP: 2885.6 (SEMI) x 1.3535 = 3905.6596.
Total = 65746.66968. Matches. The 4dp-rounded FX rates reproduce the restated totals exactly here.

### 2. IB_TWR_PCT 5.506619 — CONFIRMED

CSV l.20 "Time Weighted Rate of Return" = `5.506619351%`. Truncated/rounded @6dp = 5.506619. Importer passes it through untransformed. Old pin 4.765666 was the Aug-11 value.

### 3. NAV bridge — CONFIRMED (both directions)

Additive (CSV "Change in NAV" l.21-32): starting 52381.120971276
+ MTM 3677.845599 + Deposits 9963 + Dividends 125.72 - Withholding 17.93
- Div-accruals 20.74 + Interest 1.64 - Other Fees 1.05 - Commissions 216.8612606
- Other FX 0.01 = 65892.7353097 vs stated Ending 65892.735311283 (delta 1.7e-6, MTM-component rounding).

Cross-check: ending 65892.735311283 = cash_total 146.065631283 + stock_total 65746.66968 **exactly** (Dividend Accruals now 0). `ending_nav` @2dp 65892.74, `cash_total` @2dp 146.07 — both match the re-pinned constants.

### 4. Implied FX — CONFIRMED

- EURUSD: CSV EUR-restated Open-Positions value total 13780.99008 / EUR local total 11897.6 = 1.15830706 -> @4dp **1.1583**.
- GBPUSD: 3905.6596 / 2885.6 = 1.35350069 -> @4dp **1.3535**.
Old pins (1.1543 / 1.3508) were Aug-11.

### 5. Commission / BUY delta — CONFIRMED

`commissions_total` 216.86 - 215.16 = **1.70**. The only trade in the CSV dated after 2026-08-11 is CSV l.438: `Trades,Data,Order,Stocks,USD,SBIO,"2026-08-13, 05:45:35",5,...,-1.7,...` — Comm/Fee -1.70, quantity +5 (>0 => BUY). Explains both `commissions_total` +1.70 and `IB_LEDGER_COUNTS["BUY"]` 92 -> 93. `SELL` stays 77.

### 6. HHI / base weights — CONFIRMED

Independent Python recompute, `base_value_i = market_value_i x fx[currency_i]`, `den = Σ base_value = 65746.66968` (= stock_total):

| symbol | base_value | base_weight_i / stock_total x100 | re-pinned |
|---|---|---|---|
| SEMI | 3905.6596 | 5.94 | 5.94 |
| SXRV | 10220.37588 | 15.55 | 15.55 |
| VDST | 16069.86 | 24.44 | 24.44 |
| VUAA | 12004.8 | 18.26 | 18.26 |

`HHI = Σ (base_value_i / den)^2` over all 18 = **0.135814** @6dp. Matches re-pinned `IB_POSITION_HHI_BASE`. Identical under 4dp-rounded and full-precision FX.
`IB_RAW_MIXED_CURRENCY_SUM` (no FX applied) = Σ raw market_value = **62843.22** — matches; and it is NOT equal to the converted 65746.67, so the arbiter counter-example still holds.

### 7. Trust honesty — CONFIRMED

See § Trust honesty below.

## Tolerance widening (a) — F-4 raw-ratio

F-4 raw-ratio: abs=0.01 -> rel=0.02.

`test_f4_resolved_by_fund_currency_conversion` (test_ledger_replay_audit.py ~l.277-288).

`raw_ratio(sym)` = latest frozen-golden close / statement `close_price`. Observed
(golden terminal rows are 2026-08-27 for the Euro listings):

| sym | golden close (08-27) | statement mark (08-28) | raw_ratio | target | old abs=0.01 | new rel=0.02 |
|---|---|---|---|---|---|---|
| DEFS | 7.248 (DEFS.L, USD) | 6.148 | 1.17892 | EURUSD 1.1583 | FAIL (0.0206) | pass (1.78%) |
| SXRV | 1455.20 (SXRV.DE, EUR) | 1470.6 | 0.98953 | 1.0 | ~FAIL (0.0105) | pass (1.05%) |
| SEMI | 14.46 (SEMI.L, GBP) | 14.428 | 1.00222 | 1.0 | pass | pass |

**Verdict: ACCEPTABLE.** The assertion's job is currency-basis discrimination — proving DEFS.L quotes in USD (ratio ~1.16) while SXRV.DE / SEMI.L quote locally (ratio ~1.0). That signal is ~16 percentage points; a 2% band leaves the USD band [1.135, 1.182] and the local band [0.98, 1.02] non-overlapping with a ~0.14 gap (7x the tolerance). A genuine currency-basis regression (DEFS collapsing to ~1.0, or SXRV jumping to ~1.16) still trips the assertion. The observed ~1.8% for DEFS is one trading day of close-vs-mark movement because the frozen golden's European-listing series ends 2026-08-27 while the statement marks are 2026-08-28 — per-line price noise, not a currency error. Not masking drift.

## Tolerance widening (b) — de-dilution tripwire

De-dilution tripwire: rel=0.02 -> rel=0.03.

`test_us249_de_dilution_is_explained_by_the_cash_weight` (test_ledger_replay_audit.py ~l.447).

Assertion: `neutral_vol / twr_vol ≈ 1 / (1 - median_cash_weight)`.
Aug-28 values: median_weight 0.0490 -> prediction 1/(1-0.0490) = 1.05152.
twr_vol 0.1343, neutral_vol 0.1445 -> observed ratio 1.07595. Relative gap 2.32% (was inside the 2% band on Aug-11).

**Verdict: ACCEPTABLE, with a caveat.** `1/(1-w)` is a first-order approximation that is exact only if the cash weight is constant across the window; the residual error is driven by the dispersion of the daily cash weight and its correlation with the invested return path. The Aug-28 window adds 13 trading days and re-estimates both volatilities from a different path, so a heuristic tripwire landing 2.3% off its first-order prediction is within expected noise. The real-regression signal is preserved: if the cash-weight explanation broke, the ratio would sit near 1.0 — ~5% off the prediction — and trip even the 3% band. Caveat carried to `risks`: this is now close to its band and should get a second-order correction, not a third widening, if it drifts again.

## Large replay moves (04b)

All consistent with: window Aug-11 -> Aug-28 (+13 trading days, 148 -> 161 replay states), every position re-marked to the Aug-28 close, one SBIO BUY 2026-08-13, and the statement's own period TWR moving 4.765666% -> 5.506619% (+0.74pp).

| move | Aug-11 | Aug-28 | assessment |
|---|---|---|---|
| `twr["3M"]` | 1.56 | -0.79 (sign flip) | EXPECTED. A trailing-3-month window slid 17 calendar days drops late-May and adds a flat-to-down late-August (peak 2026-08-17 then a ~0.3% pullback into month-end). Sign flips in short trailing-window returns are normal, not anomalies. |
| `twr["All"]` | 0.43 | 1.11 (+0.68pp) | CONSISTENT. Same direction and same order of magnitude as the statement period-TWR delta (+0.74pp). |
| `money_weighted_return_pct` | 2.76 | 3.49 (+0.73pp) | CONSISTENT. Tracks the statement TWR delta (+0.74pp) almost exactly; stock_total rose +823.68 against only a $359 new buy. |
| `investment_gain` | 1645.99 | 2091.78 (+445.79) | CONSISTENT. NAV rose +462.76 (65429.98 -> 65892.74) over the extra window net of the one contribution; ~+$480 is what +0.74pp TWR on a ~$65k book implies. |
| `reconciliation_adjustment` | -19.98 | -5.95 | CONSISTENT / an improvement. Residual between replayed terminal value and the statement level; both are <0.03% of NAV. Re-marking pulls the replay terminal (65753.77) to within 0.011% of stock_total (65746.67), shrinking the residual. Moving toward zero is not a defect. |

Cross-file consistency (order asked to check): `reconciliation_adjustment` = -5.95 in all three touched files (test_ledger_replay_audit.py l.175 & l.694, test_portfolio_state.py l.965, test_analytics.py l.8552). `anchor.residual` = -1.15 in the same three (l.134 / l.773 / l.8509). No divergence — 04b's flagged concern is resolved.

Spot-checks of replay per-symbol values against the CSV anchor:
- `by_symbol["SEMI"]` 3914.32 = golden SEMI.L 14.46 x 200 x GBPUSD 1.3535. Ties out.
- `by_symbol["SXRV"]` 10113.35 = golden SXRV.DE 1455.20 x 6 x EURUSD 1.1583. Ties out.
- `states[-1].total_market_value` 65753.77 ≈ stock_total 65746.67 within the unchanged rel=0.001 cross-check.

## Trust honesty (guardrails 2-4)

`git diff` for the statement-refresh work touches only: `golden_market_data.json`
(golden artifact, regenerated by the human's `refresh_statement.py` run),
`statement_truths.py`, `test_analytics.py`, `test_ledger_replay_audit.py`,
`test_portfolio_state.py`. All four code files are under `app/tests/`.

- No `docs/finance/financial-methodology.md` change — no formula moved.
- No `app/schemas/**` change — the schema hook did not fire; no field added, removed or retyped.
- No `app/analytics/**`, no `app/domain/**`, no `reconciliation.py`, no `performance.py` — no return basis, weighting or aggregation changed.
- No trust-state logic change. `anchor.trust == "verified"` assertions are unchanged; the residual got *smaller* (46.69 -> -1.15; |−1.15| / 4672.04 = 0.000246, far inside `REPLAY_OPENING_CASH_RESIDUAL_SHARE`). The rung is still earned by a wide margin — nothing was relabelled to stay publishable.
- `withheld` / `unavailable` distinction intact: the withheld-date set
  ["2026-04-14","2026-04-17","2026-06-12","2026-07-17"] is unchanged (all pre-08-11),
  `return_is_publishable` assertions unchanged.
- No truth class mixed: every changed pin is statement-truth or replay-derived fixture data.

It is a fixture/pin refresh and it stayed one.

## What was NOT independently verified

- The replay engine was not run in this audit. Replay-derived pins (terminal MV, per-symbol MV, mwr, investment_gain, twr_vol / neutral_vol, len(states)=161, peak.date=2026-08-17) were checked for internal consistency with the CSV-anchored statement truths and for direction/magnitude plausibility, not recomputed day-by-day. The statement-truth constants in `statement_truths.py` WERE independently recomputed from the raw CSV (§ Anchor-by-anchor).
- `len(published)` = 157 = 161 - 4 withheld is the test lane's only hand-derived figure; arithmetic checks out and the suite is green (04b).
- Engine-dependent pins (IB_INSTRUMENT_COUNT 70, IB_REPLAY_UNIVERSE_SIZE 68, IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK, IB_ABSENT_SYMBOLS) did not move per 04/04b — no escalation, consistent with byte-identical holdings.
