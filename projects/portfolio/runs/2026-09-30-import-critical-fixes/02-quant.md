REPORT 2026-09-30-import-critical-fixes/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   cd services/quant-engine && python <run_dir>/scratch/{f1_dashboard_expected,f1_pypdf_lines,f2_f3_f4_probe,f3_dashboard_idempotence,f4_request_path}.py (network off, enrichment stubbed, frozen prices)
  result:    PASS
  detail:    5 scripts ran. F1: engine reproduces golden -1.20% (A); true dates+single fee give TWR 3.81% vs my own path 3.8064%. F3 re-add Dashboard identical: True. anchors: raw PDF lines + own arithmetic; rest engine-consistency.

contract_notes:
  - schemas/imports.py ImportedPosition.cost_basis and unrealized_pnl must become float | None; desktop types.ts:37-39 already declares them nullable; no imports contract doc exists (register row "import boundary has no field contract").
  - schemas/reconciliation.py PortfolioOverview.total_cost_basis, total_unrealized_pnl (L29-30) and top_positions[].unrealized_pnl must become nullable; types.ts:56-57,61 must change from number to number | null in the same pass.
  - schemas/reconciliation.py:81 EnrichedPosition.unrealized_pnl is non-nullable; build_enriched_positions has no production caller, so either make it nullable or remove it (dead-code gate).
  - docs/contracts/import-admission-fields.md needs a combined-snapshot section (per-constituent evidence plus the roll-up rule), and the add-statement combine response must carry a combined admission. see § F2
  - apps/desktop/src/test/dashboardGoldens.ts (FF block) and app/scripts/golden_market_data.json must be regenerated after F1: the replay now requests (2026-03-31, 2026-04-11), which the frozen capture does not hold. see § F1

pack_corrections:
  - capabilities/quant.md § The analytics modules — `ls app/analytics/` shows factor_model.py, which the table omits; add a row "factor_model.py | rolling factor regression (residuals feed risk.py residual_vol)".

handoff:
  - F1 backend (importers/freedom24.py): trade_date = date part of each Transactions record's "Trade date" (pypdf record offset +9), not settlement (+10). Unparseable date: skip the record. Delete _statement_grouped_date, GROUPED_ENTRY_DAY and the date(2026,1,1) fallback. see § F1
  - F1 expected FF2026 Dashboard (frozen prices, F1 plus a single fee charge): window 2026-03-31..2026-04-10, 8 states; every range start 2,955.01, end 3,071.00, TWR 3.81%, MWR 3.81%, bench 4.48%, excess -0.67pp, gain 112.48, trust degraded. see § F1
  - F1 alone (period FEE row re-dated, still double-charged per F7) gives TWR 3.58%, excess -0.90pp, recon adj +10.27. That is a known-wrong number, so an AC must not pin it. Bundling F7 is the orchestrator's call. see § F1
  - F1 test lane: test_importer.py:288 pins the fabricated {"2025-12-01", ...}; it must become {"2026-03-31", "2026-04-01", "2026-04-07"}. The frozen capture needs a live re-capture (FMP key); FF rows shrink 90 to 9 per symbol, which may trip the capture guard (--allow-smaller-capture). see § F1
  - F2 (engine + frontend): recommended rule is combined trust = weakest of {each input statement's own admission, admission recomputed on the combined snapshot}. The doc does not settle this, so it is an open decision for the human. see § F2
  - F2 expected: IB2026 + ESPP2026 must show degraded/degraded (today admitted/verified). FF2026 + ESPP2026 must show degraded/degraded (today admitted/verified). IB2026 + IB2026 shows degraded. see § F2
  - F3 frontend: Exposure for a combined portfolio must come from the backend combine_imported_snapshots output. The desktop PortfolioSnapshot has no account_id, so overlayImportedSnapshot cannot apply same-account replace and is a second merge formula. see § F3
  - F3 expected, IB2026 re-added: Exposure input identical to IB2026 alone: 18 positions, 0 quantity diffs, raw MV 62,843.22 (base 65,746.67), VUAA 80 / 12,004.80, cash USD 146.07, EUR 0, GBP 0. Today it shows 125,686.44, VUAA 160, USD 292.13. see § F3
  - F3: when the backend combine is refused (HTTP 400: base-currency mismatch or missing account_id), no combined portfolio may be saved on any surface. Today App.tsx:791-800 still saves the summed overlay. see § F3
  - F4 backend: null cost_basis/unrealized_pnl (trust unavailable) when the statement states none. Two fabrication sites: freedom24.py:177-192, and portfolio_snapshot_builder.py:39,42 (every request-path engine, including Exposure for added nodes). see § F4
  - F4 aggregates: total_cost_basis and total_unrealized_pnl are null if any position's value is null (FF 3,018.96 / 0.00 -> null/null; IB+FF 65,274.10 / 3,491.53 -> null/null; IB alone 62,255.14 / 3,491.53 unchanged). Per-position top_positions uPnL is null for VTI. see § F4
  - F4 merge: statement_importer.py:279-281 must sum cost_basis/unrealized_pnl only when both are non-null, else null. ledger.py:244 must not estimate an opening-lot unit cost from a null basis. see § F4
  - New finding N1 (outside F1-F4, not ruled): Dashboard monthly returns divide by the reconciled terminal value, so the accounting adjustment enters performance, contrary to § Terminal-value input rule. Route to a quant-audit order or the register. see § New findings outside F1-F4
  - Open decision D-F1 for the human: the replay window starts at the first ledger date, so a fixed FF2026 covers 8 of the statement's ~70 trading days. Anchoring at the statement-period start (+5.77% on frozen prices) is a methodology change. see § F1
  - Proposed methodology-doc edits E1-E4 (not applied) go to docs-engineer once the human rules on D-F1/D-F2. see § Proposed methodology edits

skill_calls:
  - quant-research — not called; this lane has no Skill tool. Its SKILL.md § Step 2 was read as reference for the seven-section brief template.

risks:
  - The F1 expected values come from frozen prices sliced to the new window (same captured rows, filtered by date). A live re-capture could move them slightly if FMP re-adjusts closes; the -0.67pp excess and 3.81% TWR should be re-read from the regenerated golden.
  - F2's rule is not in the methodology doc. The recommendation (weakest-of-all) is mine and needs the owner's ruling before it ships under the doc's authority. On all 5 fixture pairs both candidate rules give the same label, so only a synthetic offsetting-delta fixture can tell them apart.
  - D-F1: shipping F1 without a window decision shrinks the FF Dashboard from Dec-Apr (fabricated) to 8 days in April (honest). All range tabs then show identical values; window_start_date = 2026-03-31 discloses this, but users may read it as a regression.
  - Workspaces persisted before the F4 fix still carry the fabricated 3,018.96 / 0.00 in importedExposureOverride (persisted-import class). The fix must state whether those values are recomputed on load or disclosed as stale; I did not rule on it.
  - interactive_brokers_csv.py:275-289 drops the whole position when the Cost Basis cell is malformed. Once cost_basis is Optional, dropping broker-truth market value for a missing optional field is worse than nulling it. This is adjacent to F4, not required by it.
  - The F3 "today" numbers (125,686.44 / VUAA 160 / USD 292.13) are reused from the prior audit's overlay_probe.ts run, not re-executed here.
  - Brief sections 2.2 (academic grounding) and 2.6 (visualization) are condensed: this brief corrects existing fields and has no new metric or chart.
  - The runtime note forbidding report files conflicts with this order's report_to; I followed the order and PROTOCOL.md § 3.

## Orchestrator brief
- Decision F1: dates come from the statement's own per-record "Trade date"; no importer synthesizes a date. Expected FF2026 Dashboard after the fix: TWR 3.81%, window 2026-03-31..04-10, trust degraded.
- Decision F1/F7 interaction: the period FEE row has no date of its own. F1 alone gives 3.58% (still double-charged), so the AC should pin 3.81%, which needs F7's single-charge fix in the same slice.
- Open decision D-F1 (human): replay window from the first ledger date (the current doc: 8 trading days) vs the statement-period start (a methodology change, +5.77% frozen).
- F2 is not settled by the doc: open decision D-F2 (human). Recommended: combined trust = weakest of constituents and combined recompute. Expected IB+ESPP and FF+ESPP: degraded (today verified).
- Decision F3: the backend merge is the only merge. Exposure must consume combine_imported_snapshots. IB2026 re-add must equal IB2026 alone (MV 62,843.22, VUAA 80); the backend Dashboard is already idempotent.
- Decision F4: null + unavailable, never derived. Two fabrication sites (freedom24.py, portfolio_snapshot_builder.py). Aggregates are null if any input is null (merge-TWR precedent). No Dashboard or Risk number consumes cost basis.
- Lane split: backend (F1, F4 importer/builder/merge/schema), frontend (F2 display, F3 Exposure source, F4 types), test (goldens + recapture + test_importer.py:288), docs (E1-E4 after rulings).
- New finding N1 (monthly returns include the reconciliation adjustment) is outside F1-F4: route separately.
- § F1: date source, feasibility, expected numbers A/B/C, golden impact. § F2: rule options, numbers. § F3: rule, expected values, structure.
- § F4: representation, consumer list. § Proposed methodology edits: E1-E4 text. § Computed-metrics inventory. § New findings outside F1-F4. § Verification outputs.
- Blocks dispatch: F2's rule and D-F1 need human rulings before their ACs can be final. F3, F4 and the F1 date parse can be dispatched now.

## F1 — Freedom24 trade and fee dates

**Problem framing.** The researcher reads the FF2026 Dashboard to learn what the account returned. Today it shows -1.20% (3M) on a replay in which 9 VTI were held from 2025-12-01, although the account held 28 SCHD + 3 VTI + 4 VWO until 2026-04-07. The number is wrong by about 5 pp and has no warning attached.

**Concept.** Trade-date accounting: a transaction is recognised on the date the trade executes, not the settlement date. This matches the IBKR CSV importer (`Date/Time`, interactive_brokers_csv.py:316) and GIPS, which require trade-date accounting (GIPS 2010 provision 1.A.6). The replay values holdings from each ledger entry's date, so a ledger date is a valuation input, not metadata.

**Date source (feasibility checked with the production extractor, `scratch/f1_pypdf_lines.py`).** Each Transactions record is 12 pypdf lines. The importer already reads offsets +3..+8. Offset +9 is the trade timestamp, +10 is settlement, +11 is the order ID:

| Ticker | +9 Trade date | +10 Settlement | +11 Order ID | Commissions page: order / date / fee |
|---|---|---|---|---|
| SCHD.US Sell 28 | 2026-04-07 16:35:44 | 2026-04-08 | 638027902/… | 638027902 / 2026-04-07 / 2.56 |
| VTI.US Buy 6 | 2026-04-07 17:17:58 | 2026-04-08 | 638042122/… | 638042122 / 2026-04-07 / 2.12 |
| VWO.US Sell 4 | 2026-04-07 16:30:05 | 2026-04-08 | 638024717/… | 638024717 / 2026-04-07 / 2.08 |

The order IDs link each commission to its trade, and the pairs agree. The Cash deposits/withdrawals section already carries true dates (2026-03-31, 2026-04-01) and is correct today.

**Rule.**
```text
trade_date(record) = date part (YYYY-MM-DD) of the Transactions "Trade date" cell
  - never the settlement date
  - unparseable / absent  -> the record is skipped (Importer resilience rule); never a date
    synthesised from statement_period, the period start, or a constant
period totals ("Total commissions for the period") carry no per-record date and are not
  dated ledger entries. The per-trade commission is already on each trade row (net_amount = gross - fee).
```
Remove `_statement_grouped_date`, `GROUPED_ENTRY_DAY`, and the `date(2026, 1, 1)` branch.

**Expected values** (`scratch/f1_dashboard_expected.py`; production `run_imported_dashboard_history`, frozen prices):

| Scenario | Window (states) | Range start value | End value | TWR | MWR | Bench | Excess | Gain | Recon adj | Cash-anchor residual |
|---|---|---|---|---|---|---|---|---|---|---|
| A today (3M) | 2025-12-01..04-10 (90) | 3,097.89 | 3,071.00 | **-1.20%** (= golden) | -1.20% | -1.19% | -0.01 | -37.16 | +10.27 | -6.76 |
| B F1 only | 2026-03-31..04-10 (8) | 2,955.01 | 3,071.00 | 3.58% | 3.58% | 4.48% | -0.90 | 105.72 | +10.27 | -6.76 |
| **C F1 + single fee** | 2026-03-31..04-10 (8) | **2,955.01** | **3,071.00** | **3.81%** | **3.81%** | **4.48%** | **-0.67** | **112.48** | **+3.51** | **0.00** |
| Independent path, same window | 03-31..04-10 | 2,955.01 | 3,067.49 (market) | 3.8064% | — | 4.4768% | — | 112.48 | — | — |

- In C every range (1M/3M/YTD/1Y/All) is identical, because the window is shorter than 1M. `portfolio_return_trust = degraded` (basis `replay_derived`), benchmark basis `verified_total_return`, net contributions 0.00, drawdown withheld (n/a, unchanged).
- C's terminal adjustment +3.51 = 9 × (335.44 statement − 335.05 frozen close) exactly, so C reconciles fully. B's extra 6.76 is F7's double charge.
- C's first state: 911.23 cash + 6.11 (3/31 dividend net) + MV 2,037.67 = 2,955.01, which matches my path to the cent.
- Monthly grid: only 2026-04 exists, so `monthly_returns_reliable = false` (fewer than 2 months) and the grid is hidden. The emitted value is 3.9252%, not 3.81% (see N1).
- Statement-period facts for D-F1: the statement's own NAV return 2025-12-31 → 2026-04-11 = 3,071.00 / 2,900.12 − 1 = **+5.8922%**. My path on frozen closes 2025-12-31 → 04-10 = **+5.7711%** (SPY −0.0899%). Cash identity 911.23 − 861.08 − 6.76 + 8.65 = 52.04 = statement.

**D-F1 (open, human).** `_derive_imported_history_window` (dashboard_history_engine.py:549-554) starts the replay at the earliest ledger/position date. The methodology documents this for IB2026 ("positions valued 2026-01-08 — the first trade date", § FX Conversion Fallback Disclosure). For FF2026 that cuts the view to 8 of ~70 trading days, although the statement proves the opening holdings (Securities "Beginning balance": SCHD 28, VTI 3, VWO 4) and cash (911.23) at 2025-12-31. Anchoring the replay at the statement-period start when opening holdings are statement-stated would publish the whole period (≈ +5.77%). That is a methodology change, and it must not be approximated by any synthetic ledger date. Drift already anchors "Since Import" at the period start (§ Indexed Return Series), which is precedent the owner may weigh.

**Golden and test impact.** The replay will request (2026-03-31, 2026-04-11). The frozen capture holds only (2025-12-01, 2026-04-11) for VTI/SCHD/VWO/SPY, so `FrozenMarketData` raises `FrozenMarketDataMiss` by design. A live re-capture is required (`export_dashboard_goldens --capture`, FMP key). The FF series shrink from 90 to 9 rows per symbol, which may trip `assess_capture_regression`'s row-loss rule. `test_importer.py:288` pins the fabricated date set.

## F2 — Admission label of a combined portfolio

**What the doc says.** Import admission rule (methodology L55-57) and import-admission-fields.md: admission is read-only evidence "for an imported broker snapshot", and "Any exception can only lower the decision". Neither says how a portfolio built from several statements is labelled. **The doc does not settle F2. This is open decision D-F2.**

**Two paths disagree today.** The multi-file initial import runs `import_statements` → `combine_imported_snapshots` → `build_import_admission_summary(combined)` (import_engine.py:16,45), so admission is recomputed on the combined snapshot. The add-statement path persists `nextAnalysis.admission_summary`, which covers only the added file (App.tsx:804). The same two files therefore get different labels depending on the button used.

**Numbers** (`scratch/f2_f3_f4_probe.py`):

| Pair (base + added) | Shown today | Recompute on combined | Weakest constituent | Base-MV share |
|---|---|---|---|---|
| IB2026 + IB2026 | degraded/degraded | degraded | degraded | 100% IB |
| IB2026 + ESPP2026 | **admitted/verified** | degraded | degraded | IB 95.1%, ESPP 4.9% |
| ESPP2026 + IB2026 | degraded/degraded | degraded | degraded | — |
| IB2026 + FF2026 | degraded/degraded | degraded | degraded | IB 95.6% |
| FF2026 + ESPP2026 | **admitted/verified** | degraded | degraded | FF 47.1%, ESPP 52.9% |

Constituents: IB2026 degraded (cash/positions/NAV checks unavailable because the statement is multi-currency; description check warns); FF2026 degraded (cash and NAV checks unavailable because of an EUR 0.00 row; positions check passes with Δ 0.00); ESPP2026 admitted/verified (all Δ 0.00).

**Candidate rules.**
1. *Recompute on the combined snapshot* (what multi-file import does today). Weakness: the numeric checks compare summed statement totals against summed parsed values, so a +x delta in one account and a −x delta in another net to `pass`. The combined label can then exceed a constituent's label, which is an overstatement.
2. *Weakest constituent.* It can never exceed any input. Weakness: it misses defects that exist only in the merged snapshot.
3. **Recommended: the weakest of both**, i.e. `trust = min(trust(s_1), …, trust(s_n), trust(combined))` on the ladder verified > degraded > withheld > unavailable, and `decision` likewise (admitted > degraded > withheld). The summary keeps each constituent's checks, so evidence is not collapsed into one label (the same principle as § Market Data Basis "grouped section_trust so mixed trust does not collapse into one top-line label").

Sub-decision: include all input statements, or only the terminal (latest-per-account) ones? I recommend **all**. A superseded same-account statement still contributes ledger entries, flow totals and `starting_nav` to the combined snapshot. The trust roll-up is engine logic (thin frontend), so it belongs in the combine response. If the combine is refused (HTTP 400), there is no combined portfolio and therefore no combined label (see F3).

**Acceptance observation that would prove the rule false:** a synthetic pair whose positions-check deltas offset (+x / −x). Under rule 3 it must show `degraded` or lower. Rule 1 would show `verified`. The committed fixtures cannot distinguish the rules, because all 5 pairs agree.

## F3 — Re-adding a statement from the same account

**Rule (methodology § Multi-Statement Snapshot Merge, authoritative):** positions and cash come from the terminal snapshot per `account_id`. Same `account_id` → latest-wins REPLACE. Different `account_id` → SUM. A missing `account_id` or mismatched base currency → the combine is refused (ValueError → HTTP 400).

**Expected values, IB2026 re-added onto IB2026** (backend `combine_imported_snapshots`, `scratch/f2_f3_f4_probe.py`):

| Quantity | IB2026 alone | Backend combine (expected on Exposure) | Desktop overlay today (prior audit) |
|---|---|---|---|
| positions | 18 | 18, 0 per-(symbol, ccy) quantity differences | 18 |
| raw MV | 62,843.22 | 62,843.22 | 125,686.44 |
| base MV (statement rates) | 65,746.67 | 65,746.67 | n/a |
| VUAA qty / MV | 80 / 12,004.80 USD | 80 / 12,004.80 | 160 |
| cash USD / EUR / GBP | 146.065631 / 0 / 0 | same | 292.13 / 0 / 0 |

Dashboard (backend path, `scratch/f3_dashboard_idempotence.py`): IB2026 vs IB2026+IB2026 → 161 states, 3M TWR −0.79%, MWR −0.51%, All TWR 1.11%, MWR 3.49%, net contributions 9,963.00. **identical: True.** The backend is already idempotent, so the fix brings Exposure to the same property: `combine(S, S)` yields the positions and cash of `S`.

**Why the overlay cannot be patched in place.** The desktop `PortfolioSnapshot.importedMeta` carries importer, statementPeriod, importedAt and sourceFileNames, but **no account_id**, so the overlay cannot tell "same account" from "another account". It is also a second implementation of the merge formula (guardrail 2). It already diverges twice more: it sums `marketValue` across currencies without conversion and overwrites `baseCurrency` unchecked (portfolioSnapshot.ts:118,150), and `normalizePortfolioSnapshot` dedups by symbol only, summing across currencies (L21-30; latent, since IB2026 has no symbol held in two currencies). The correct behaviour is that every combined surface consumes the backend combined snapshot.

**Refused combine.** App.tsx:789-800 catches the combine failure, sets `combinedHistorySnapshot = null`, and still saves `overlaidSnapshot`. A refusal means the merge cannot be classified, so the Exposure view must not publish a summed portfolio either. The honest outcome is no combined node, plus the existing error disclosure.

**Out of scope, noted:** the combined `statement_totals` for IB+IB double count (TWR 11.3165 vs 5.5066; F10, awaiting human). Exposure does not read them.

## F4 — Cost basis the statement does not state

**Representation.**
```text
ImportedPosition.cost_basis     = stated cost basis, or null when the statement states none
ImportedPosition.unrealized_pnl = stated unrealized P&L, or null when the statement states none
                                  (never market_value − fabricated cost; never 0)
trust: unavailable ("we do not have it"). Not withheld (nothing is held back), not degraded (there
is no value to degrade).
Never derived from: market value, close price, ending quantity × price, or partial trade history.
```
FF2026 shows why partial derivation is also out: 6 of the 9 VTI were bought in-period (6 × 322.426 + 2.12 = 1,936.68), and the cost of the 3 opening shares appears nowhere in the PDF. A "cost basis" of 1,936.68 + ? is a different quantity, not a degraded version of the right one. Realized P/L on the sold lines (SCHD 121.16, VWO 49.86) is stated, but it is not modelled and is not a cost basis for VTI.

Grounding: Importer resilience rule (L59-65, "never fabricated or zero-filled"); broker-truth class; and the null-propagation precedent in § Multi-Statement Snapshot Merge ("If ANY input statement's time_weighted_return_pct is null, the combined value is null … never a partial/silent result").

**Fabrication sites, both must change** (grep for the computation, not the name):
1. `importers/freedom24.py:177-192`: VTI cost_basis 3,018.96 (= 9 × 335.44), unrealized 0.00.
2. `services/portfolio_snapshot_builder.py:39,42`: `cost_basis = market_value`, `unrealized_pnl = 0` for **every** position on the request path. This builder feeds `/engines/exposure/run`, stress, drawdown, distribution, drift and the snapshot bootstrap route. Measured on IB2026 (`scratch/f4_request_path.py`): request-path overview total_cost_basis 62,843.22 and total_unrealized_pnl **0.00**, against the statement path's 62,255.14 / **3,491.53**. Added-statement nodes carry no `importedExposureOverride` (App.tsx:572-573), so their Exposure overview comes from this path. This site is not in the tech-debt register.

**Every downstream consumer, and how it must behave:**

| Consumer | Today on fixtures | Required |
|---|---|---|
| `overview.total_cost_basis` (overview.py:43) | FF 3,018.96; IB 62,255.14; IB+FF 65,274.10 | null if any position's cost_basis is null → FF null, IB+FF null, IB unchanged |
| `overview.total_unrealized_pnl` (overview.py:44) | FF 0.00; IB 3,491.53; IB+FF 3,491.53 (silently IB-only) | null if any is null → FF null, IB+FF null, IB unchanged |
| `overview.top_positions[].unrealized_pnl` (overview.py:56) | VTI 0.00 | per-position null |
| `_merge_terminal_positions` (statement_importer.py:279-281) | sums | sum only when both non-null; else null |
| `reconstruct_position_lots` opening lot (ledger.py:243-244) | FF est. unit cost 335.44 from the fabricated basis | no estimate when cost_basis is null (no production caller today) |
| `EnrichedPosition.unrealized_pnl` (performance.py:62) | copies the value | nullable, or remove (no production caller) |
| desktop `PortfolioOverview` type (types.ts:56-61) | `number` | `number \| null`; render as unavailable, never 0 |
| persisted `importedExposureOverride` | holds 3,018.96 / 0.00 | pre-fix workspaces keep stale values; the story must decide recompute-on-load vs disclose (see risks) |

Not consumers (grep-verified): admission checks, TWR, MWR, the replay, drawdown, VaR, stress, correlation. **F4 changes no Dashboard or Risk number.** A partial-coverage aggregate (sum over stated positions plus a coverage count) would be a new labelled rung needing the owner's approval. It is not the default.

## Proposed methodology edits

Not applied. For docs-engineer after the rulings.

**E1 (F1), under Trust … → Importer resilience rule, Freedom24 bullet, append:**
> Ledger dates are the statement's own per-record dates. Transactions use the "Trade date" column (date part; trade-date accounting, as the IBKR CSV `Date/Time`), never the settlement date. Cash deposits/withdrawals use their "Date". A record whose date cannot be parsed is skipped under this rule. No importer synthesises a ledger date (from the statement period or any constant), because the replay values holdings from each entry's date: a synthetic date moves positions in time and fabricates performance. Period totals without a per-record date (e.g. "Total commissions for the period") are not dated ledger entries.

**E2 (F2), new paragraph after "Import admission rule" — PROPOSED, pending D-F2:**
> Combined-snapshot admission: the admission of a portfolio combined from several statements is the weakest of (a) each input statement's own admission and (b) the admission recomputed on the combined snapshot, on the ladder verified > degraded > withheld > unavailable (decision: admitted > degraded > withheld). Constituent evidence is kept alongside the roll-up. Recomputation alone is insufficient because offsetting per-account deltas can net to a pass. A combine that is refused has no combined admission. The same rule applies to the multi-file import and the add-statement paths.

**E3 (F3), § Multi-Statement Snapshot Merge, Contract rule, add:**
> This merge is the only implementation of combining statements. Every surface that shows a combined portfolio (Dashboard, Exposure, Risk) consumes the snapshot it produces; no client re-merges holdings. Property: for positions and cash, combine(S, S) = S. A refused combine yields no combined portfolio on any surface.

**E4 (F4), new section "Cost Basis and Unrealized P&L (broker truth)" after Truth Classes:**
> `ImportedPosition.cost_basis` and `unrealized_pnl` are statement-stated values. When the statement states none, both are null (unavailable). They are never derived from market value, close price or partial trade history, and never zero-filled; this applies equally to request-path snapshots, which carry no cost basis. Aggregates (`total_cost_basis`, `total_unrealized_pnl`) are null when any contributing position's value is null. The multi-statement merge sums them only when both inputs are non-null.

**E5 (D-F1), only if the owner rules to extend the window:** a Dashboard replay-window rule anchored at the statement-period start when the statement states opening holdings. I have deliberately not drafted it; it is the owner's call.

## Computed-metrics inventory

| Field | Type | Formula / rule | Truth class | Trust when available | Nullable | FF2026 / IB2026 expected |
|---|---|---|---|---|---|---|
| `ImportedLedgerEntry.trade_date` (Freedom24 BUY/SELL) | date | E1 | broker truth | — | no (record skipped if unparseable) | 2026-04-07 ×3 |
| `range_metrics[*].summary.time_weighted_return_pct` (FF) | float\|null | § Portfolio Return Methodology | broker-truth replay | degraded (`replay_derived`) | yes | 3.81 |
| `…summary.money_weighted_return_pct` (FF) | float\|null | § Modified Dietz, market-derived terminal | replay | degraded | yes | 3.81 |
| `…summary.start_value` / `end_value` (FF) | float\|null | first / reconciled last state | replay | degraded | yes | 2,955.01 / 3,071.00 |
| `…summary.investment_gain` (FF) | float\|null | market-derived terminal − start − flows | replay | degraded | yes | 112.48 |
| `…summary.benchmark_return_pct` / `excess_return_pct` (FF) | float\|null | § US-34.5 | market data / mixed | verified_total_return / degraded | yes | 4.48 / −0.67 |
| `…window_start_date` (FF, non-All) | str\|null | first date of the slice | replay | — | yes | 2026-03-31 |
| `…monthly_returns_reliable` (FF) | bool | ≥2 months | replay | — | no | false |
| `admission_summary.trust_level` (combined) | enum | E2 (pending D-F2) | snapshot evidence | min over inputs | no | IB+ESPP degraded; FF+ESPP degraded |
| `admission_summary.decision` (combined) | enum | E2 | snapshot evidence | min over inputs | no | IB+ESPP degraded |
| Exposure positions / MV / cash (IB re-add) | — | § Multi-Statement Snapshot Merge | broker truth (terminal) | as IB alone | — | 18 / 62,843.22 raw / USD 146.07 |
| `ImportedPosition.cost_basis` | float\|null | E4 | broker truth | stated | **yes** | FF VTI null; IB unchanged |
| `ImportedPosition.unrealized_pnl` | float\|null | E4 | broker truth | stated | **yes** | FF VTI null |
| `PortfolioOverview.total_cost_basis` | float\|null | Σ base-converted, null if any null | snapshot analytics | — | **yes** | FF null; IB 62,255.14 |
| `PortfolioOverview.total_unrealized_pnl` | float\|null | same | snapshot analytics | — | **yes** | FF null; IB 3,491.53 |
| `PortfolioOverview.top_positions[].unrealized_pnl` | float\|null | per position | snapshot analytics | — | **yes** | VTI null |
| `EnrichedPosition.unrealized_pnl` | float\|null | copy | snapshot analytics | — | **yes** | (no production caller) |

## New findings outside F1-F4

Not ruled on, and not part of this order's fixes. Recorded so they are not lost.

```
FINDING N1
severity:   MATERIAL
where:      services/quant-engine/app/services/dashboard_history_engine.py:856 (_compute_contribution_adjusted_monthly_returns)
claim:      methodology § Monthly Returns: monthly returns compound the same daily returns as the TWR chain, and Π(1+m) = period TWR; § Terminal-value input rule: no performance figure contains the reconciliation adjustment
actual:     the daily return uses the reconciled terminal total_portfolio_value. FF (C): April = 3,071.00/2,955.01 − 1 = 3.9252% vs TWR 3.81%. Committed golden 3M: Π monthly = −0.87% vs TWR −1.20%; the 0.34pp gap = the +10.27 adjustment
impact:     the monthly grid publishes an accounting correction as performance and disagrees with the headline TWR on every reconciled run
expected:   the terminal day uses market_derived_terminal_value (the shared helper), so Π monthly = TWR
```

The request-path cost-basis fabrication (`portfolio_snapshot_builder.py:39,42`) is folded into F4 above rather than raised separately, because F4's fix is incomplete without it.

## Verification outputs

All scripts are under `<run_dir>/scratch/` and were run from `services/quant-engine` with sockets blocked and FMP enrichment stubbed.

- `f1_dashboard_expected.py`: scenario A reproduces the committed golden (3M TWR −1.20, start 3,097.89, bench −1.19, monthly 0.12/−0.52/−5.04/4.81). B and C are as tabled in § F1. Independent path: 03-31→04-10 3.8064% (SPY 4.4768%), 12-31→04-10 5.7711% (SPY −0.0899%), statement NAV return 5.8922%, cash identity 52.04.
- `f1_pypdf_lines.py`: Transactions records at lines 13/25/37, trade timestamps at 22/34/46, settlement dates 2026-04-08 at 23/35/47. Commissions orders 638024717/638027902/638042122 are dated 2026-04-07 with fees 2.08/2.56/2.12.
- `f2_f3_f4_probe.py`: admission table (§ F2), IB+IB combine table (§ F3), cost-basis consumer values (§ F4), reconstruct_position_lots(FF) = opening lot 3 @ est. 335.44 plus trade lot 6 @ 322.426.
- `f3_dashboard_idempotence.py`: 161 states; 3M −0.79 / −0.507; All 1.11 / 3.493; net contributions 9,963.0; identical: True.
- `f4_request_path.py`: request-path IB2026 overview 62,843.22 / 62,843.22 / 0.00 against the statement path's 65,746.67 / 62,255.14 / 3,491.53.

Anchors: the F1 dates and fees come from the raw PDF lines (production extractor) cross-checked by order ID. The F1 returns are backed by my own arithmetic path from statement facts and frozen closes, which is independent of app code. Everything else (admission, combine, overview) runs the engine itself on the committed statements, so it is an **engine-consistency check, not independent verification**.
