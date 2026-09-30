REPORT 2026-09-29-statement-import-audit/02
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests -k "import or statement" -q ; python scratch/ib_csv_rederive.py, ib_csv_compare.py, ib_qty_conservation.py, combine_probe.py, pdf_importers_run.py, ff_true_path.py, overlay_probe.ts (vite-node)
  result:    PASS
  detail:    pytest: 161 passed, 860 deselected, 6 warnings. anchor: raw statement (own csv parse of IB2026.csv + its MTM qty + Cash Report roll-forward; pdftotext of FF/ESPP); statement_truths.py not used. IB CSV direct fields: 0 mismatches.

contract_notes:
  - ImportedPosition.cost_basis and unrealized_pnl are non-nullable floats (schemas/imports.py), which forces the Freedom24 importer to fabricate them (F4); a fix needs Optional fields mirrored in desktop types.ts:37-39 and a new imports contract doc.
  - PortfolioOverview.realized_cash_flow (schemas/reconciliation.py:36, types.ts:66) has no methodology section and no contract doc, so it is an untraceable number (guardrail 2), and it is wrong on IB2026 (F5).

pack_corrections:
  - none

handoff:
  - BLOCKING F1 (CRITICAL): Freedom24 trades/fees are dated 2025-12-01, outside the period and 4 months before the true 2026-04-07; the Dashboard shows FF TWR -1.20% vs statement NAV +5.89%. Owner: backend (importers/freedom24.py). see § Findings
  - BLOCKING F2 (CRITICAL): after "add statement" the Exposure admission card shows only the added statement's admission (ESPP verified over IB degraded). Owner: frontend (App.tsx:804). see § Findings
  - BLOCKING F3 (CRITICAL): desktop overlay sums same-account statements; re-adding IB2026 doubles Exposure MV 62,843.22 -> 125,686.44 and VUAA 80 -> 160. Owner: frontend (portfolioSnapshot.ts:92-165). see § Findings
  - BLOCKING F4 (CRITICAL): Freedom24 cost_basis is fabricated as market value (3,018.96) with unrealized_pnl 0.0 in broker-truth ImportedPosition; the statement states no cost basis. Owner: backend + schema. see § Findings
  - SHOULD_FIX F5-F12 (MATERIAL): Forex rows dropped, LQQ split unparsed, FF fee double count, FF totals mislabelled, reconciliation unwired, combine flow totals/TWR double count, None->0 cash merge, starting_nav fallback. see § Findings
  - SHOULD_FIX F13-F20 (MINOR): admission multi-currency ceiling, description false positives, tax abs, stale doc numbers, ESPP inferences, PDF EUR regex, DEFS cross-listing, reconciliation deposit definition. see § Findings
  - F10 and F12 are methodology-doc findings (Multi-Statement Snapshot Merge rules) and go to the human, not to an engineer. see § Findings
  - Per-suspicion verdicts for S-01..S-36 and D-01..D-07 are in § Recon verdicts; the IB CSV field-by-field comparison is in § IB2026.csv re-derivation.

skill_calls:
  - none

risks:
  - F2 and F3 were proven by executing the production overlay function on real importer output (vite-node) and by reading the App.tsx node-save and exposure paths; no UI click-through was performed.
  - Implied FX (EURUSD 1.1583, GBPUSD 1.3535) has no external anchor: network is off and no second FX source exists offline. Base-converted MV matching NAV Stock is partly true by construction of the rate.
  - FF dashboard TWR -1.20% is read from the committed golden (dashboardGoldens.ts), not re-run; my own path uses frozen prices and reproduces the statement's opening balance 2,900.12 exactly.
  - pdftotext layout for FF2026 interleaves label/value columns; FF broker-truth values were read by hand and cross-checked by the statement's own cash-flow identity (911.23 - 861.08 - 6.76 + 8.65 = 52.04).
  - The IBKR PDF parser was spot-run on the four legacy PDFs, not re-derived; S-15 is UNVERIFIABLE with the available fixtures.
  - The runtime note forbidding report files conflicts with this order's report_to; I followed the order and PROTOCOL.md § 3.

## Orchestrator brief
- Verdict FAIL: 4 CRITICAL (F1-F4), 8 MATERIAL (F5-F12), 8 MINOR (F13-F20).
- IBKR CSV direct broker truth is exact: all 18 positions x 5 fields, cash (3 currencies), 11 totals, FX, and all ledger counts and sums match the raw CSV with 0 mismatches.
- The IBKR CSV ledger is incomplete: 89 Forex trades and the LQQ split are dropped (F5, F6). Downstream withholding keeps the LQQ number honest; per-currency cash is not honest.
- The Freedom24 importer is the weakest parser: fabricated dates (F1), fabricated cost basis (F4), fee double count (F7), and wrong totals (F8).
- The desktop add-statement path is wrong twice: it sums same-account holdings (F3) and shows a trust label taken from one statement only (F2).
- A multi-currency statement can never reach admission `verified` (F13). This is conservative, not dishonest; changing it needs the owner.
- build_reconciliation_summary has no production caller, and it has no commissions check (F9).
- Route: F1/F4/F7/F8 to backend (freedom24.py + schema); F2/F3 to frontend; F5/F6/F9/F11 to backend; F10/F12 to human (methodology doc).
- § Findings: 20 FINDING blocks with numbers.
- § IB2026.csv re-derivation: field-by-field comparison table and ledger roll-forward.
- § Freedom24 and ESPP re-derivation: statement vs importer values.
- § Recon verdicts: one verdict line per S-xx / D-xx.
- Nothing blocks dispatch.

## IB2026.csv re-derivation

Anchor: the raw CSV, parsed by my own reader (`scratch/ib_csv_rederive.py`: stdlib csv, per-section header tracking, Decimal arithmetic). It does not import app.importers or statement_truths.py. It is compared against the production importer's runtime output (`scratch/ib_csv_compare.py`, snapshot dumped to `scratch/importer_snapshot.json`). Two further external anchors come from inside the statement itself: the Mark-to-Market Prior/Current Quantity columns (quantity conservation) and the Cash Report starting/ending cash (cash roll-forward).

| Quantity | Raw statement | Importer | Delta |
|---|---|---|---|
| positions | 18 (USD 15, EUR 2, GBP 1) | 18 (same split) | 0 |
| per-position qty, cost_basis, close, value, unrealized (90 values) | row values | identical | 0 (tol 1e-6) |
| per-row qty x close = value; value - cost = uPnL | 18/18 consistent | n/a | 0 |
| starting_nav / ending_nav | 52,381.120971 / 65,892.735311 | same | 0 |
| cash_total / stock_total | 146.065631 / 65,746.66968 | same | 0 |
| dividends / WHT / interest / other fees / commissions / deposits (abs) | 125.72 / 17.93 / 1.64 / 1.05 / 216.8612606 / 9,963 | same | 0 |
| TWR | 5.506619351% | 5.506619351 | 0 |
| EURUSD / GBPUSD (value-implied) | 1.1583000000 / 1.3535000000 | 1.1583 / 1.3535 | 0; cost-basis-implied rates identical |
| MV in base | 65,746.669680 = NAV Stock | overview uses same rates | 0.00000 |
| raw mixed-currency sum | 62,843.22 | n/a | the doc's 58,588.76 / 61,238.53 are stale (F16) |
| cash EUR / GBP / USD (start, end, settled) | 0,0,0 / 0,0,0 / 4,672.035671, 146.065631, 146.065631 | same | 0 |
| ledger BUY / SELL | 93 / 77 (Stocks Order rows) | 93 / 77 | 0 |
| DIVIDEND / WHT / INTEREST / FEE / DEPOSIT counts | 25 / 28 / 1 / 5 / 1 | same | 0 |
| dividend / WHT / interest / fee / deposit signed sums | 125.72 / -17.93 / 1.64 / -1.05 / 9,963 | same (net_amount) | 0 |
| WHT `tax` field sum | signed -17.93 (2 positive reversals) | 24.45 | +6.52 (F15) |
| Forex Order rows | 89, commissions -26.00 USD | 0 | dropped (F5) |
| Corporate Actions | 1 row: LQQ split 200:1, qty 199 | 0 | dropped (F6) |
| instruments | 70 (DEFS listed twice: LSE USD, SBF EUR) | 70, 0 with currency | F19 |

Cash roll-forward per currency (start + ledger net = end):

| ccy | start | stock trades net | cash flows | end without Forex (= importer ledger) | end with Forex (my parse) | statement end |
|---|---|---|---|---|---|---|
| USD | 4,672.035671 | +932.006189 | +10,071.38 | 15,675.421860 | 146.065631 | 146.065631 |
| EUR | 0 | -9,979.747652 | 0 | -9,979.747652 | 0.000000 | 0 |
| GBP | 0 | -2,933.848800 | 0 | -2,933.848800 | 0.000000 | 0 |

With the 89 Forex rows included, my parse closes all three currencies to the cent. The importer's ledger misses by exactly the Forex cash effect. Commissions: ledger trade fees = 137.5676 USD + 25.7577 EUR + 17.4488 GBP = 190.86 at IBKR's own trade-date USD equivalents (191.02 at the static rate), against 216.86 in the statement. The gap is the $26.00 Forex commission.

Quantity conservation (Mark-to-Market prior qty + Σbuy − Σsell = current qty, cross-listings summed): 69 symbols, 1 violation. It is LQQ, with gap −199.0, exactly the unparsed corporate-action quantity.

Admission on IB2026.csv (runtime): decision `degraded`. The cash, positions and NAV checks are `unavailable` ("not in one currency"), description is `warn` (ASML, NICE, UBER, VALE, VUAA), and ISIN and symbol identity `pass`. Running build_reconciliation_summary manually gives 7/7 pass.

## Freedom24 and ESPP re-derivation

Text extracted with `pdftotext -layout` (poppler, mingw64). Importers run offline with sockets blocked and FMP enrichment stubbed (`scratch/pdf_importers_run.py`).

Freedom24 (FF2026.pdf, period 2025-12-31 to 2026-04-11):

| Field | Statement | Importer | Verdict |
|---|---|---|---|
| starting / ending NAV | 2,900.12 / 3,071.00 | same | ok |
| cash start / end | 911.23 / 52.04 | same | ok |
| stock_total | 3,018.96 | same | ok |
| position | VTI 9 @ 335.44 = 3,018.96 | same | ok |
| VTI cost basis | not stated | 3,018.96, uPnL 0.00 | fabricated (F4) |
| trade dates | 2026-04-07 (all 3) | 2025-12-01 | fabricated, outside period (F1) |
| trades | SCHD S28 @30.632 857.70 fee 2.56; VTI B6 @322.426 1,934.56 fee 2.12; VWO S4 @53.946 215.78 fee 2.08 | qty/price/amount/fee same | ok |
| commission | 6.76 total, separate from the -861.08 trade flow | per-trade fee in net_amount AND a FEE -6.76 row | double count (F7) |
| dividends | 7.19 + 2.99 = 10.18 gross; taxes -1.53 | ledger same; dividends_total 8.65 (net) | F8 |
| deposits | none | deposits_total 8.65 | wrong (F8) |
| withholding_tax_total | 1.53 | None | missed (F8) |
| ledger cash roll-forward | 52.04 | 911.23 − 867.84 + 8.65 − 6.76 = 45.28 | −6.76 (F7) |
| admission | n/a | degraded (the EUR 0.00 cash row blocks the cash check) | conservative |

Independent value path (`scratch/ff_true_path.py`, frozen prices from golden_market_data.json). With the true holdings, 2025-12-31 is valued at 2,900.12, exactly the statement's opening balance. The path runs to 3,067.49 on 2026-04-10 (+5.77%), and the statement NAV return with no external flows is +5.89%. With the importer's dates the path starts 2025-12-01 and returns +0.40%. The committed golden shows Dashboard TWR −1.20% and start date 2025-12-01.

ESPP (ESPP2026.pdf, 2025):

| Field | Statement | Importer | Verdict |
|---|---|---|---|
| MSFT qty / price / MV / cost / uPnL | 7.012 / 483.62 / 3,391.24 / 3,139.15 / 252.09 | same | ok |
| core cash (FYIXX) | 10.44 | ending_cash 10.44, starting None | ok (beginning "-") |
| ending NAV | 3,401.68 | same | ok |
| dividends | 12.27 total (MSFT 12.20 + FYIXX 0.07) | one DIVIDEND 12.27 on MSFT | F17 |
| taxes withheld | 1.83 | WHT 1.83; also other_fees_total 1.83 | F17 |
| purchase | 7.012 @ 447.67 on 2025-06-30 | BUY −3,139.06 + synthesised DEPOSIT 3,139.06 | inferred flow (F17) |
| deposits_total | not stated | 3,139.15 (= cost basis) | Δ0.09 vs DEPOSIT (F17) |
| cash roll-forward | 10.44 | 0 + 3,139.06 − 3,139.06 − 1.83 + 12.27 = 10.44 | ok |
| admission | n/a | admitted / verified; all three numeric checks Δ0.00 | supported |

## Findings

```
FINDING 1
severity:   CRITICAL
where:      services/quant-engine/app/importers/freedom24.py:46-51 (_statement_grouped_date), used by trades :236-280 and commissions :348-378
claim:      trades and the period FEE are "grouped" to day GROUPED_ENTRY_DAY of the statement-start month
actual:     FF2026 period starts 2025-12-31, so every trade and the fee is dated 2025-12-01, which is before the statement period. The PDF states 2026-04-07 for all three trades. The replay window then starts 2025-12-01 (dashboard_history_engine.py:549-554) and the committed golden shows TWR −1.20%. The statement's own NAV return (no external flows) is +5.89%, and my true-date path is +5.77% to 04-10.
impact:     Dashboard performance/TWR/MWR for any Freedom24 import is computed on holdings the account did not have (9 VTI from Dec 1 instead of 28 SCHD + 3 VTI + 4 VWO until Apr 7) and shows a ~7 pp wrong return
expected:   per-trade trade_date parsed from the Transactions rows; if unparseable, drop the record (resilience rule), never synthesise a date
```

```
FINDING 2
severity:   CRITICAL
where:      apps/desktop/src/app/App.tsx:804 -> app/portfolioWorkspaceStorage.ts:325 -> App.tsx:312-314 -> ExposurePanel.tsx:209 ImportAdmissionReviewCard
claim:      the Exposure tab's Import Admission Review describes the snapshot being shown
actual:     on add_snapshot the new node persists nextAnalysis.admission_summary, which covers only the added file. No admission is computed for the combined snapshot. Runtime: IB2026.csv = degraded (3 checks unavailable, 1 warn) and ESPP2026.pdf = admitted/verified. So IB + add ESPP shows "admitted / verified" over a portfolio that is 95% IB holdings.
impact:     the user sees a verified trust label on a combined portfolio whose dominant statement failed to reach verified. The label overstates its basis.
expected:   admission computed on the combined snapshot, or the weakest of the constituent admissions, never the last file's alone
```

```
FINDING 3
severity:   CRITICAL
where:      apps/desktop/src/features/portfolio/portfolioSnapshot.ts:92-165 overlayImportedSnapshot; consumed by App.tsx:776/800 (node.portfolioSnapshot) -> runExposureEngine(snapshot) App.tsx:572 (added nodes carry no importedExposureOverride)
claim:      methodology § Multi-Statement Snapshot Merge: same account_id -> latest-wins REPLACE; different accounts -> SUM
actual:     the desktop overlay sums by symbol regardless of account or period. Executed on the real importer output: IB2026 + IB2026 gives raw MV 62,843.22 -> 125,686.44, VUAA qty 80 -> 160, USD cash 146.07 -> 292.13. It also sums across currencies without conversion and overwrites baseCurrency with no check. The backend combine of the same pair keeps VUAA at 80.
impact:     adding an updated statement from the same broker account (the normal IB YTD refresh) doubles every held position and total on the Exposure tab. The Dashboard (backend combine) disagrees with it.
expected:   the overlay follows the backend merge rule (replace same account, sum distinct accounts, convert or refuse cross-currency), or the Exposure view is driven by the backend-combined snapshot
```

```
FINDING 4
severity:   CRITICAL
where:      services/quant-engine/app/importers/freedom24.py:177-192; schemas/imports.py ImportedPosition (cost_basis, unrealized_pnl non-optional)
claim:      ImportedPosition is broker truth; methodology L59-65 "never fabricated or zero-filled"
actual:     FF2026 states no cost basis for VTI. The importer emits cost_basis 3,018.96 (= ending qty x close) and unrealized_pnl 0.00. This flows into overview.total_cost_basis, total_unrealized_pnl and top_positions[].unrealized_pnl, is published in the bootstrap response, and is persisted in importedExposureOverride. It is also used by ledger.py:244 to estimate opening-lot cost.
impact:     any consumer reads a zero unrealized P&L as broker truth for a position whose P&L is unknown. No current tsx renders it, but the number is already persisted.
expected:   cost_basis and unrealized_pnl null (schema made Optional), surfaced as unavailable
```

```
FINDING 5
severity:   MATERIAL
where:      services/quant-engine/app/importers/interactive_brokers_csv.py:300-306 (_parse_trades keeps only Asset Category == Stocks)
claim:      the imported ledger represents the statement's cash activity; methodology says gaps surface via reconciliation
actual:     89 Forex Order rows are dropped. The per-currency ledger roll-forward misses by USD +15,529.36, EUR −9,979.75 and GBP −2,933.85. With the Forex rows, my parse closes all three to 0.00. $26.00 of Forex commissions is absent (ledger 190.86 vs statement 216.86). overview.realized_cash_flow publishes USD +11,003.39 / EUR −9,979.75 / GBP −2,933.85 against broker net USD −4,525.97 / EUR 0 / GBP 0. In base currency the replay gap is about $26 (static-rate net +1.15), absorbed by the terminal reconciliation.
impact:     per-currency cash history and realized_cash_flow are wrong. Commission totals from the ledger understate cost by 12%. Not rendered today.
expected:   Forex conversions imported as ledger entries (a CONVERSION type, or paired cash legs plus commission) so each currency's cash closes to the Cash Report
```

```
FINDING 6
severity:   MATERIAL
where:      interactive_brokers_csv.py (no Corporate Actions parser); IB2026.csv:585
claim:      ledger quantities are complete broker truth
actual:     quantity conservation against the statement's own Mark-to-Market prior/current qty holds for 68/69 symbols. LQQ misses by −199.0, exactly the unparsed "Split 200 for 1" quantity. Downstream, engine/portfolio_state.py withholds LQQ because its price ratio of 218 is ≥ 5.0, which is honest. A split with a ratio below 5 (2:1, 3:1, 4:1) would evade the heuristic and publish a phantom opening position.
impact:     today LQQ is withheld, not wrong. Any future low-ratio split produces a fabricated opening quantity valued on the Dashboard.
expected:   parse Corporate Actions into the ledger (split quantity adjustment) so conservation holds by construction; keep the heuristic as a backstop
```

```
FINDING 7
severity:   MATERIAL
where:      freedom24.py:253-256 (net_amount = gross − fee) and :348-378 (separate period FEE row)
claim:      one commission charge per trade
actual:     the 6.76 of commissions is charged twice. The ledger cash roll-forward gives 911.23 − 867.84 + 8.65 − 6.76 = 45.28 against the statement's 52.04 (Δ −6.76, 0.22% of NAV).
impact:     replay cash and Dashboard value/return for Freedom24 imports are understated by the double-counted fees
expected:   either per-trade fees or the period FEE row, not both
```

```
FINDING 8
severity:   MATERIAL
where:      freedom24.py:112-139 (_parse_statement_totals)
claim:      statement_totals carry the statement's own totals
actual:     deposits_total = 8.65 while the account had no deposits (8.65 is the net dividends/taxes cash-movement total). dividends_total = 8.65 is net, while the ledger and the IBKR convention use gross (10.18). withholding_tax_total = None while the statement shows 1.53. other_fees_total = commissions_total = 6.76, so the same charge is stored in two fields.
impact:     merged totals (statement_importer.py:190-243) and any reconciliation compare against wrong targets. Not rendered today.
expected:   deposits_total 0 (from the Cash Flow table), dividends 10.18 gross, withholding 1.53, other_fees None
```

```
FINDING 9
severity:   MATERIAL
where:      docs/finance/financial-methodology.md:59-65 vs analytics/reconciliation.py:59 (only a re-export at analytics/portfolio_imports.py:4,13; not in vulture_allowlist.py)
claim:      "the resulting totals gap surfaces through the statement reconciliation"
actual:     build_reconciliation_summary has no production caller, so no user sees its result. It has no commissions check, so it passes 7/7 on IB2026 despite F5's $26 gap. Run manually it fails on the legacy 2022 PDF (ending_usd_cash Δ −10,533.56) and the 2023 PDF (deposits Δ 5,291.50), and nobody sees either failure. The importers record no per-record skip count.
impact:     the stated safety net for fail-safe record skipping does not exist, so a partial snapshot looks complete
expected:   reconciliation wired into bootstrap/admission output with a commissions check, or the methodology claim removed
```

```
FINDING 10
severity:   MATERIAL
where:      statement_importer.py:190-243 _merge_statement_totals; methodology § Multi-Statement Snapshot Merge (L2328-2412)
claim:      doc: flow totals are "plain sums across all input statements" and TWR "geometric compounding of EVERY input statement"
actual:     combine(IB2026, IB2026) keeps positions correct (VUAA 80) and dedupes the ledger (230 entries), but gives dividends 251.44, deposits 19,926, commissions 433.72 and TWR 11.3165% (= 1.055066² − 1) against 5.5066%. IB YTD exports all start Jan 1, so any two refreshes overlap.
impact:     combined statement_totals double count every overlapping period. Not rendered today, but it is the snapshot's broker-truth block.
expected:   methodology change (human): a non-overlap precondition, or totals rebuilt from the deduped ledger; overlapping TWR null
```

```
FINDING 11
severity:   MATERIAL
where:      statement_importer.py:306-308 (None -> 0.0 in merged cash); domain/ledger.py:305 classify_opening_state
claim:      a missing value stays missing; broker_proven means the starting cash is stated
actual:     IB2026 + ESPP2026 gives merged USD starting_cash 4,672.04, with ESPP's None summed as 0.0. The opening state becomes broker_proven, while ESPP alone classifies as trade_window_covered.
impact:     the opening-state trust class is upgraded by a fabricated zero. It is correct here only by coincidence, because ESPP's beginning value was "-".
expected:   the merged field is None if any input is None, and the opening state is the weakest constituent's
```

```
FINDING 12
severity:   MATERIAL
where:      methodology § Multi-Statement Snapshot Merge ("falls back to the first positive starting_nav found across statements")
claim:      combined starting_nav is the earliest statement's opening NAV
actual:     IB2026 + ESPP2026 gives starting_nav 52,381.12 (IB, as of 2026-01-01) for a combined window starting 2025-06-30 (ESPP), while ending_nav sums IB at 2026-08-28 and ESPP at 2025-12-31. The cash anchor (starting_nav − opening_positions_value) then mixes as-of dates.
impact:     the cash anchor for a cross-account, cross-period combine rests on a NAV from the wrong date
expected:   methodology decision (human): the fallback applies only when as-of dates coincide; otherwise starting_nav is null/disclosed
```

```
FINDING 13
severity:   MINOR
where:      services/import_admission.py:75-79, 236, 257, 330, 351 (single-currency comparability gate)
claim:      the admission decision reflects whether the statement reconciles
actual:     IB2026 is `degraded` because the cash, positions and NAV checks are `unavailable`. Converted with the statement's own rates, positions give Δ 0.00, NAV 65,746.67 + 146.07 = 65,892.74 gives Δ 0.00, and cash (EUR/GBP 0) gives Δ 0.00. Even FF2026 (all-USD positions) is degraded, only because of an EUR 0.00 cash row. So no multi-currency statement can reach `verified`.
impact:     the trust label understates the basis. This is conservative, not dishonest.
expected:   owner decision; any unlock is a trust-model change (a new labelled rung), not a fix
```

```
FINDING 14
severity:   MINOR
where:      services/instrument_identity.py:88-100 (description token check), surfaced by import_admission.py:392-417
claim:      flags registry-known holdings whose description is identity-disjoint
actual:     5 flags on IB2026 (ASML, NICE, UBER, VALE, VUAA). 4 of them are not held, and all 5 ISINs match. The cause: the symbol is removed from the description tokens but not from the registry-name tokens ("UBER TECHNOLOGIES" vs "Uber"), and IBKR abbreviations ("VANG S&P500 USDA") do not match.
impact:     the card tells the user "Instrument identity may be mislabeled" for correct instruments and degrades admission
expected:   iterate positions, not instruments; skip when the ISIN matches; subtract the symbol from both sides
```

```
FINDING 15
severity:   MINOR
where:      interactive_brokers_csv.py:369 (tax=abs(amount)); ib.py:408; csv:315 fee=abs
claim:      tax carries the withheld amount
actual:     sum(tax) = 24.45 against the statement's −17.93, because the positive reversals 0.66 and 2.60 are counted as tax. No consumer reads `tax` today (only the dedupe key).
impact:     latent. The first consumer of `tax` will overstate withholding by 36%.
expected:   tax = −amount (signed)
```

```
FINDING 16
severity:   MINOR
where:      financial-methodology.md:356-359 and :1760-1762; analytics/overview.py:37-38 comment ("4.33%")
claim:      "On the committed IB2026 statement the raw sum is $58,588.76 ... converted $61,238.53"; stock_total $64,922.99
actual:     the committed statement gives raw 62,843.22, converted 65,746.67 = stock_total, understatement 4.42%
impact:     the doc cites numbers a reader cannot reproduce from the committed fixture
expected:   refresh the figures, or label them as the 2026-08-11 statement
```

```
FINDING 17
severity:   MINOR
where:      importers/espp.py:87-93, 140-211
claim:      ESPP totals and ledger are statement-stated
actual:     deposits_total 3,139.15 (the cost-basis line) vs the synthesised DEPOSIT 3,139.06 (447.67 x 7.012), Δ 0.09. other_fees_total and withholding_tax_total are both 1.83 (the same charge). The 0.07 FYIXX dividend is attributed to MSFT. The DEPOSIT is an inference, labelled with the statement's section name.
impact:     small cent-level inconsistencies. The inferred payroll flow is presented as stated.
expected:   one field per charge; mark inferred entries as inferred
```

```
FINDING 18
severity:   MINOR
where:      importers/interactive_brokers.py:174; analytics/reconciliation.py:26-30
claim:      the PDF path extracts the statement's EUR rate
actual:     the regex requires the literal prior-year rate "1.0353", so it only works on the 2025 PDF (EURUSD 1.1746). The 2022-2024 PDFs have no EUR rate (2023 has an EUR −5,000 withdrawal). Reconciliation then uses EUR at 1.0, a fabricated rate (documented at methodology L128-130).
impact:     any other IBKR PDF with EUR holdings reconciles at 1:1
expected:   a rate-agnostic regex; no 1.0 fallback
```

```
FINDING 19
severity:   MINOR
where:      interactive_brokers_csv.py:263-337, 428-444 (symbol-only identity)
claim:      symbol identifies the instrument
actual:     DEFS is two instruments: conid 792056066 (LSE, USD) and 785370514 (SBF, EUR), same ISIN LU3038520774. Trades in both land under "DEFS", and instruments carry two DEFS rows. Symbol-keyed dicts downstream keep one.
impact:     latent. Price history and trade anchors for cross-listed symbols mix listings.
expected:   carry currency/listing (or conid) as part of the key where the statement distinguishes them
```

```
FINDING 20
severity:   MINOR
where:      analytics/reconciliation.py:83,96 (deposits check)
claim:      compares statement deposits with parsed deposit entries
actual:     deposits_total is abs(net Deposits & Withdrawals), but deposits_actual sums DEPOSIT rows only. The 2023 PDF fails by 5,291.50, exactly its EUR withdrawal in USD, although the importer is correct.
impact:     if F9 wires reconciliation, it will false-fail every period with a withdrawal
expected:   compare the net of DEPOSIT and WITHDRAWAL (FX-converted)
```

## Recon verdicts

- S-01 CONFIRMED MATERIAL: F5 (Forex) and F6 (LQQ split).
- S-02 CONFIRMED MATERIAL: F9. No skip counter exists in any importer (code read).
- S-03 CONFIRMED MINOR (code read, statement_importer.py:31-35): an IBKR PDF parse error is reported with the Freedom24/ESPP message. Not exercised.
- S-04 CONFIRMED MINOR: imports.py:89 defaults to `.pdf`.
- S-05 CONFIRMED MINOR: documented abs convention. The sign is lost on net-withdrawal periods, and this feeds F20.
- S-06 CONFIRMED MINOR: F15 (24.45 vs 17.93).
- S-07 CONFIRMED MINOR (code read): unreachable on the fixture, which has 0 zero-quantity trades.
- S-08 CONFIRMED MINOR (code read): the fixture carries Base Currency USD.
- S-09 CONFIRMED MINOR: EUR/GBP cash is 0 on IB2026, so the impact is nil. It is disclosed per currency.py.
- S-10 CONFIRMED MINOR: 0 of 70 IBKR instruments carry a currency.
- S-11 CONFIRMED MINOR (code read): ib.py:99, 571. The CSV path raises instead.
- S-12 CONFIRMED MINOR: F18.
- S-13 CONFIRMED MATERIAL: F11 (runtime IB+ESPP).
- S-14 CONFIRMED MINOR: identical branches, no numeric effect.
- S-15 UNVERIFIABLE: no fixture has a hyphenated or lowercase PDF symbol or a failing multi-line trade.
- S-16 CONFIRMED MATERIAL for totals and TWR (F10). REFUTED for within-statement dedupe: 0 key collisions among IB2026's 230 entries.
- S-17 CONFIRMED CRITICAL: F4.
- S-18 CONFIRMED MINOR: USD hard-codes are correct for FF2026. Totals defects are in F8.
- S-19 CONFIRMED CRITICAL: F1. Worse than stated, because the date precedes the period.
- S-20 CONFIRMED MATERIAL: F7 (−6.76).
- S-21 CONFIRMED MINOR (code read): latent layout-shift emptiness.
- S-22 CONFIRMED MINOR (code read, imports.py:89-93): the upload path stores temp names as source_path.
- S-23 CONFIRMED MINOR (code read): Freedom24 output depends on FMP reachability (I stubbed enrichment).
- S-24 CONFIRMED MINOR: F13. A multi-currency statement cannot reach `verified`.
- S-25 CONFIRMED MINOR (code read): latent, because no IB2026 entry has a None net_amount.
- S-26 CONFIRMED MINOR (code read): registry defaults, outside the import core.
- S-27 CONFIRMED MINOR for this audit: the generic request path, not statement import.
- S-28 CONFIRMED MINOR (code read): latent, because no fixture has a None ending_cash.
- S-29 REFUTED: the risk_summary stub carries honest nulls.
- S-30 CONFIRMED MINOR (code read): latent null -> 0 in the desktop cash projection.
- S-31 CONFIRMED CRITICAL: F3.
- S-32 CONFIRMED MINOR (code read).
- S-33 CONFIRMED CRITICAL: F2.
- S-34 CONFIRMED MINOR: derived exposure persisted with the import (truth-class hygiene, no number changes).
- S-35 CONFIRMED MINOR: "-1.83" -> "01.83" = 1.83, masked by abs(). Latent for the signed change_match.
- S-36 CONFIRMED MINOR: F17.
- D-01 CONFIRMED MINOR: random UUIDs and put(), not content-addressed.
- D-02 CONFIRMED MINOR: same as S-34.
- D-03 CONFIRMED MATERIAL: F9.
- D-04 REFUTED as a disagreement: each consumer matches its own doc section (L128-130 vs L1744). The EUR 1.0 fallback is in F18.
- D-05 CONFIRMED MINOR: docs/IB2026.pdf is absent (ls).
- D-06 CONFIRMED MINOR: Freedom24/ESPP are routed but not listed as shipped scope.
- D-07 CONFIRMED: aggregate of F4, F11, S-25, S-28, S-30.
