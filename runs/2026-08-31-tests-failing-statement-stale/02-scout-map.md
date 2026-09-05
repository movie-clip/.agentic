# Orchestrator brief

Scope: map every stale pin for the Aug-11 -> Aug-28 `docs/IB2026.csv` refresh so DESIGN can spec pin updates without re-exploring. Read-only; nothing edited.

Key findings:
- **Holdings are byte-identical between the two exports.** All 18 positions, same quantities, same currency split. The Aug-28 export differs only by (a) all positions re-marked to Aug-28 closing prices, (b) recomputed period totals/TWR, (c) exactly ONE extra trade: `SBIO` BUY 5u on 2026-08-13 (commission -1.70).
- **No new symbols. No newly-absent symbols. No instrument-registry work.** `test_registry_isin_integrity.py` is not in the failure set -> registry coverage intact.
- **`statement_truths.py` pins that change:** `IB_STATEMENT_PERIOD`, `IB_LEDGER_COUNTS["BUY"]` (92->93), 5 of 10 `IB_TOTALS_2DP` keys, `IB_TWR_PCT`, `IB_IMPLIED_FX_4DP`, `IB_PINNED_POSITIONS` (DEFS/SEMI/VUAA marks), `IB_RAW_MIXED_CURRENCY_SUM`, `IB_BASE_WEIGHTS_PCT`, `IB_POSITION_HHI_BASE`. **Unchanged:** account id, base ccy, position count (18), currency split, instrument count (70), replay universe (68), pinned instruments (AAPL/CIBR), sector examples, absent symbols, stub-benchmark overweights, DIVIDEND/WITHHOLDING/INTEREST/FEE/DEPOSIT counts.
- **Real DESIGN finding (class c):** `test_ledger_replay_audit.py` and `test_portfolio_state.py` carry ~30+ *inline* statement/replay-derived numeric pins (terminal MV, TWR days, peak date, `len(states)`, cash-anchor residuals, reconciliation adjustment) that fail on this refresh and are **not** in `statement_truths.py`. `docs/architecture/testing-architecture.md` section "Statement refresh workflow" step 3 asserts structural tests "must not fail on a refresh" - these do, and their `US-33.4: X pre-refresh; Y after` comments prove they are hand-regenerated every refresh. The freshness gate cannot see them.
- Golden files (`dashboardGoldens.ts`, `golden_market_data.json`) staged in the working tree **are** consistent with Aug-28 - the user's `refresh_statement.py` run took.

Sections below: `## statement_truths.py - pin-by-pin`, `## Regeneration recipes`, `## 41 failing tests - classification`, `## Docstring / comment drift`, `## Freshness gate`.

---

REPORT 2026-08-31-tests-failing-statement-stale/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE (read-only scout; no Bash granted)
  result:    NOT_RUN
  detail:    Values derived by reading docs/IB2026.csv (working tree = Aug-28) and app/importers/interactive_brokers_csv.py; Aug-11 side read from the still-stale pins in app/tests/statement_truths.py. Counts marked REGEN must be produced by importing the CSV.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Where it lives - the single pin module is `services/quant-engine/app/tests/statement_truths.py` (module-level constants + `diff_statement_truths`). Fixture path `STATEMENT_2026_CSV_PATH` resolves to `docs/IB2026.csv` directly (`app/tests/_statement_fixtures.py:19`) - there is no separate CSV fixture to copy.
  - Importer contract that produces every pinned value: `app/importers/interactive_brokers_csv.py` - `import_statement(path)` -> `ImportedPortfolioSnapshot`. `_normalize_period` (l.156) -> `"2026-01-01 - 2026-08-28"`; `_parse_instruments` (l.428) does NOT dedupe (70 raw Data rows incl. duplicate DEFS LSE+SBF -> count stays 70); `_parse_trades` (l.300) BUY if qty>0 else SELL, Stocks+Order only, Forex/Corporate-Actions ignored; `_implied_fx_rates` (l.233) = base-restated / local Open-Positions Total.
  - CHANGED pins with Aug-11 -> Aug-28 values and the exact accessor: see section "statement_truths.py - pin-by-pin".
  - REGEN-only pins (`IB_RAW_MIXED_CURRENCY_SUM`, `IB_BASE_WEIGHTS_PCT`, `IB_POSITION_HHI_BASE`, and confirmation of `IB_LEDGER_COUNTS["BUY"]`): see section "Regeneration recipes" - the test lane runs the snippet, reads the value, writes it. Scout hand-estimates given but not authoritative.
  - New symbols vs Aug-11: NONE. Newly-absent symbols vs Aug-11: NONE. Only `SBIO` gains a trade (BUY 2026-08-13); `SBIO` already has full coverage (`app/core/symbols.py:69` resolution rule, `golden_market_data.json` series, `app/instruments/etf_sector_resolution.py`). No `app/instruments/registry.py` edit needed.
  - Blast radius by lane - test lane only. `statement_truths.py` (pin values + module docstring). `test_ledger_replay_audit.py` + `test_portfolio_state.py` inline numeric pins (regenerate against the new frozen golden - see section "41 failing tests"). `test_analytics.py` needs no numeric change beyond the shared `IB_STATEMENT_PERIOD` pin. No schema, no analytics/, no frontend, no `docs/contracts/**` - this is a fixture refresh, not a methodology change.
  - Docs: `docs/architecture/testing-architecture.md` section "Statement refresh workflow" step 3 is contradicted by the two replay test files (see section "Docstring / comment drift") - DESIGN decides whether to re-home those pins or amend the doc.

risks:
  - `IB_LEDGER_COUNTS["BUY"]` 92->93 and `IB_BASE_WEIGHTS_PCT` / `IB_POSITION_HHI_BASE` / `IB_RAW_MIXED_CURRENCY_SUM` are scout hand-derivations from an 888-line CSV. They are internally consistent (the SBIO 08-13 buy explains both the +1 BUY and the +1.70 commission delta) but the test lane MUST regenerate by importing the CSV, not transcribe these.
  - `IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK` (`["MSFT","AAPL"]`) and `IB_INSTRUMENT_COUNT` (70) are judged UNCHANGED from the data but depend on engine behaviour scout did not execute (exposure-overlap ordering; whether any instrument row fails `_parse_instruments`). If `test_exposure_engine.py:558` or `test_importer_csv.py:195` still fail after the pin pass, they are the tell.
  - Could not run `pytest -q` for the exact 41-test list; classification is derived from reading the assertions in the seven named files against the new CSV, not from a run log. Cluster boundaries match `run.md` section Diagnosis.
  - `len(states) == 148` (`test_ledger_replay_audit.py:623`, `test_portfolio_state`): the Aug-28 window adds ~12 trading days, so this and every date-indexed pin (`peak.date == "2026-08-10"`, withheld-date lists) shift - not just the money figures.

---

## statement_truths.py - pin-by-pin

Snapshot handle below: `S = import_statement(STATEMENT_2026_CSV_PATH)` from `app.importers.interactive_brokers_csv`.

| Constant (line) | Aug-11 value (current) | Aug-28 value (required) | Accessor |
|---|---|---|---|
| `IB_ACCOUNT_ID` (31) | `"U8516450"` | unchanged | `S.statement.account_id` |
| `IB_STATEMENT_PERIOD` (32) | `"2026-01-01 - 2026-08-11"` | `"2026-01-01 - 2026-08-28"` | `S.statement.statement_period` |
| `IB_BASE_CURRENCY` (33) | `"USD"` | unchanged | `S.statement.base_currency` |
| `IB_POSITION_COUNT` (36) | `18` | `18` (unchanged) | `len(S.positions)` |
| `IB_POSITIONS_BY_CURRENCY` (37) | `{"USD":15,"EUR":2,"GBP":1}` | unchanged | `Counter(p.currency for p in S.positions)` |
| `IB_INSTRUMENT_COUNT` (39) | `70` | `70` (unchanged - 70 Data rows, no dedupe) | `len(S.instruments)` |
| `IB_REPLAY_UNIVERSE_SIZE` (42) | `68` | `68` (unchanged) | `len(replay_symbol_universe(S))` from `app.engine.portfolio_state` |
| `IB_PINNED_POSITIONS["DEFS"]` (46) | `close_price 6.496, market_value 3248.0, unrealized_pnl 451.524985` (qty 500, cost_basis 2796.475015 unchanged) | `close_price 6.148, market_value 3074.0, unrealized_pnl 277.524985` | `{p.symbol:p for p in S.positions}["DEFS"]` (CSV l.226) |
| `IB_PINNED_POSITIONS["SEMI"]` (47) | `market_value 2929.2, unrealized_pnl 166.2` (qty 200) | `market_value 2885.6, unrealized_pnl 122.6` | ditto (CSV l.230) |
| `IB_PINNED_POSITIONS["VUAA"]` (51) | `market_value 11964.8` (qty 80, cost_basis 10081.463136 unchanged) | `market_value 12004.8` | ditto (CSV l.247) |
| `IB_PINNED_INSTRUMENTS` (55-58) | AAPL / CIBR fields as-is | unchanged (CSV l.715 / l.725 identical) | `{i.symbol:i for i in S.instruments}` |
| `IB_LEDGER_COUNTS` (61-69) | `BUY 92, SELL 77, DIVIDEND 25, WITHHOLDING_TAX 28, INTEREST 1, FEE 5, DEPOSIT 1` | `BUY 93`; all six others unchanged | `Counter(e.entry_type for e in S.ledger_entries)` |
| `IB_TOTALS_2DP["starting_nav"]` (74) | `52381.12` | unchanged | `S.statement_totals.starting_nav` |
| `IB_TOTALS_2DP["ending_nav"]` (75) | `65429.98` | `65892.74` | `.ending_nav` (CSV l.32 = 65892.735311283) |
| `IB_TOTALS_2DP["cash_total"]` (76) | `507.00` | `146.07` | `.cash_total` (NAV "Cash" Current Total, CSV l.15) |
| `IB_TOTALS_2DP["stock_total"]` (77) | `64922.99` | `65746.67` | `.stock_total` (CSV l.16 = 65746.66968) |
| `IB_TOTALS_2DP["dividends_total"]` (78) | `125.72` | unchanged | `.dividends_total` |
| `IB_TOTALS_2DP["withholding_tax_total"]` (79) | `17.93` | unchanged | `.withholding_tax_total` |
| `IB_TOTALS_2DP["interest_total"]` (80) | `1.64` | unchanged | `.interest_total` |
| `IB_TOTALS_2DP["other_fees_total"]` (81) | `1.05` | unchanged | `.other_fees_total` |
| `IB_TOTALS_2DP["commissions_total"]` (82) | `215.16` | `216.86` | `.commissions_total` (CSV l.30 = 216.8612606) |
| `IB_TOTALS_2DP["deposits_total"]` (83) | `9963.00` | unchanged | `.deposits_total` |
| `IB_TWR_PCT` (85) | `4.765666` | `5.506619` | `S.statement_totals.time_weighted_return_pct` @ 6dp (CSV l.20 = 5.506619351%) |
| `IB_IMPLIED_FX_4DP` (88) | `{"EURUSD":1.1543,"GBPUSD":1.3508}` | `{"EURUSD":1.1583,"GBPUSD":1.3535}` | `S.statement_totals.fx_rates` @ 4dp (13780.99008/11897.6 ; 3905.6596/2885.6) |
| `IB_RAW_MIXED_CURRENCY_SUM` (100) | `62031.85` | REGEN, scout est. `62843.22` | `round(sum(p.market_value for p in S.positions), 2)` |
| `IB_BASE_WEIGHTS_PCT` (102) | `{"SEMI":6.09,"SXRV":15.70,"VDST":24.70,"VUAA":18.43}` | REGEN, scout est. `{"SEMI":5.94,"SXRV":15.55,"VDST":24.44,"VUAA":18.26}` | see recipe |
| `IB_POSITION_HHI_BASE` (104) | `0.138194` | REGEN (6dp; base denominator now 65746.66968) | see recipe |
| `IB_SECTOR_EXAMPLES` (108-113) | dict | unchanged - DEFS,IDFN,CIBR,SEMI,SXRV,VUAA,VDST all still held | `{p.symbol for p in S.positions}` |
| `IB_ABSENT_SYMBOLS` (116) | `("FICO","DFND","IUIT","IUFS","IUHC","AMZN")` | still valid (none held) - no change required; DESIGN may optionally add newly round-tripped names | ditto |
| `IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK` (121) | `["MSFT","AAPL"]` | likely unchanged (neither held; AAPL now 0-qty) - confirm via `test_exposure_engine.py:558` | exposure-engine overlap |
| `REFRESH_WORKFLOW_DOC` (28) | string | unchanged | - |

## Regeneration recipes

Deterministic, no network. Run from `services/quant-engine`.

```python
from collections import Counter
from app.importers.interactive_brokers_csv import import_statement
from app.tests._statement_fixtures import STATEMENT_2026_CSV_PATH
from app.engine.portfolio_state import replay_symbol_universe
from app.analytics.currency import total_base_market_value

S = import_statement(STATEMENT_2026_CSV_PATH)

# period / totals / twr / fx
print(S.statement.statement_period)
print({k: getattr(S.statement_totals, k) for k in
       ("starting_nav","ending_nav","cash_total","stock_total","dividends_total",
        "withholding_tax_total","interest_total","other_fees_total",
        "commissions_total","deposits_total")})
print(S.statement_totals.time_weighted_return_pct, S.statement_totals.fx_rates)

# counts
print(Counter(e.entry_type for e in S.ledger_entries))     # -> IB_LEDGER_COUNTS
print(len(S.instruments), len(replay_symbol_universe(S)))   # -> 70, 68

# IB_RAW_MIXED_CURRENCY_SUM  (see test_currency_conversion.py for the exact helper it uses)
print(round(sum(p.market_value for p in S.positions), 2))

# IB_BASE_WEIGHTS_PCT / IB_POSITION_HHI_BASE
# base value per symbol = market_value * fx_rates[f"{currency}USD"]  (USD -> x1.0)
fx = S.statement_totals.fx_rates
base = {p.symbol: p.market_value * fx.get(f"{p.currency}USD", 1.0) for p in S.positions}
den = sum(base.values())                                     # == total_base_market_value(S) == stock_total
print({s: round(base[s]/den*100, 2) for s in ("SEMI","SXRV","VDST","VUAA")})
print(round(sum((v/den)**2 for v in base.values()), 6))      # -> IB_POSITION_HHI_BASE
```
(Confirm `total_base_market_value(S)` and the `test_currency_conversion.py` raw-sum helper match the two hand formulas above before writing the values.)

## 41 failing tests - classification

`run.md` clusters: test_analytics, test_ledger_replay_audit, test_importer_csv, test_portfolio_state, test_statement_refresh, test_exposure_engine, test_currency_conversion.

**(a) reads a `statement_truths.py` pin directly - fixed by the pin pass alone:**
- `test_importer_csv.py` - `preview.period == EXPECTED_PERIOD` (l.55), `statement.statement_period == EXPECTED_PERIOD` (l.72, l.116, l.368), `diff_statement_truths(snapshot) == []` (l.106), `IB_PINNED_POSITIONS` field approx (l.131), `counts == EXPECTED_LEDGER_COUNTS` (l.146). Lines 195 (instrument count), 112/114 (position count/split), 202 (pinned instruments), 391 (self-contained literal fixture) should already pass.
- `test_statement_refresh.py` - both tests. `test_committed_statement_yields_zero_truths_diffs` (l.137) is the direct gate. `test_swap_simulation_fails_only_the_documented_pin_surface` (l.87) fails on its `assert "totals." not in labels` / `assert "fx_rates" not in labels` (l.111-112) because the stale committed pins already diff on totals/twr/fx.
- `test_currency_conversion.py` - `IB_TOTALS_2DP["stock_total"]` (l.85), `IB_RAW_MIXED_CURRENCY_SUM` (l.92), `IB_BASE_WEIGHTS_PCT` (l.105), `IB_POSITION_HHI_BASE` (l.122). The snapshot-derived half of l.82 (`total_base_market_value == statement.stock_total`) already passes.
- `test_exposure_engine.py` - `portfolio_market_value / total_base_market_value == IB_TOTALS_2DP["stock_total"]` (l.645, l.753). `IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK` (l.558) - verify; probably passes. Docstring at l.741-743 ("16 USD holdings, 3 EUR ... $61,238.53") is stale but not asserted.
- `test_analytics.py` - `snapshot.statement.statement_period == IB_STATEMENT_PERIOD` (l.7430). The IB_ABSENT/IB_SECTOR test (l.604-621) still passes; the IB2025+IB2026.pdf window tests (l.728-777) use frozen PDFs and are unaffected.

**(b) derives an expectation from the snapshot, fails for another reason:** none found. Every purely snapshot-derived assertion (position count, currency split, instrument count, replay-universe size, `end_value == daily_states[-1]`, `total_base_market_value == stock_total`) still holds because holdings and the importer/engine are unchanged.

**(c) inline statement/replay-derived numeric pin NOT in `statement_truths.py` - must be regenerated by the test lane against the new frozen golden + Aug-28 window:**
- `test_ledger_replay_audit.py` - `stock_total == approx(64_922.99)` (l.519, l.645), `total_market_value == approx(64_896.27)` (l.517, l.649), `peak.total_market_value == approx(65_377.31)` + `peak.date == "2026-08-10"` (l.641-642), `len(states) == 148` (l.623), `len(ratios) == 61` (l.606), `reconciliation_adjustment == approx(-19.98)` (l.177, l.676), `anchor.residual == approx(46.69)` (l.134), `median_weight == approx(0.0650)` (l.420), `twr_vol / neutral_vol` 0.1381 / 0.1491 (l.429-430), `money_weighted_return_pct == approx(2.76)` + `investment_gain == approx(1_645.99)` (l.682-683), the withheld-date list (l.735-740), and the per-day TWR approximations (l.347-351, l.377-384, l.456-465). These files' own `US-33.4: X pre-refresh; Y after` comments show they are hand-updated every refresh.
- `test_portfolio_state.py` - `day_one.total_market_value == approx(49_050.54)` (l.191), `drift == approx(2_620.74)` (l.233), `by_symbol["SXRV"] == approx(10_192.01)` / `["SEMI"] == approx(3_956.76)` / DEFS (l.702-706), `terminal.total_market_value == approx(64_896.27)` (l.711), `states[0].cash["USD"] == approx(4_677.02)` (l.757), `anchor.residual == approx(46.69)` (l.773), `reconciliation_adjustment == approx(-19.98)` (l.963). The `IB_POSITION_COUNT` / `IB_REPLAY_UNIVERSE_SIZE` asserts (l.142-143) pass unchanged. (Lines 918/936 and the 300-1460 block are synthetic `_snapshot` fixtures, not IB2026 - unaffected.)

## Docstring / comment drift

- `app/tests/statement_truths.py:4` - `"period 2026-01-01 - 2026-06-30"` -> should read `2026-08-28`.
- `app/tests/statement_truths.py:30` - section comment `(period 2026-01-01 - 2026-08-11)` -> `2026-08-28`.
- `app/tests/statement_truths.py:48-51` - `# USD pin was AMZN until the 2026-08-11 refresh` - historical note about the *prior* refresh; still literally true, DESIGN may leave or bump.
- `docs/architecture/testing-architecture.md` "Statement refresh workflow" step 3 + closing paragraph (l.172-187): "Structural tests derive their expectations from the snapshot itself and must not fail on a refresh." Contradicted in practice by ~30 inline pins in `test_ledger_replay_audit.py` / `test_portfolio_state.py`. DESIGN: either re-home those into `statement_truths.py` (or a sibling replay-truths module) or amend the doc to acknowledge a "regenerate the replay-audit numeric pins" step.
- `test_exposure_engine.py:741-743` docstring - `16 USD holdings, 3 EUR, 1 GBP ... $61,238.53` is two refreshes stale (now 15/2/1, ~$65,746.67); not asserted, cosmetic.
- `app/importers/interactive_brokers_csv.py:157` - `_normalize_period` docstring example uses `June 30, 2026`; illustrative only, harmless.

## Freshness gate

No mechanism is needed beyond the pin update.
- `test_statement_refresh.py::test_committed_statement_yields_zero_truths_diffs` IS the truths-diff baseline; it goes green once the pins match.
- The golden re-capture is already gated by the `FrozenMarketData` freshness check + the US-35.3 degrade-guard in `scripts/refresh_statement.py`; the user ran it and both golden artifacts are staged and Aug-28-consistent (`dashboardGoldens.ts` `statementPeriod "2026-01-01 - 2026-08-28"`, `portfolioValue "$65892.74"`, a `2026-08` monthly row; `golden_market_data.json` has 481 `2026-08-2x` price rows and an `SBIO`/`SBIO.L` series).
- There is no committed-statement hash and none is required. The swap-simulation meta-test is the regression pin for the failure surface; DESIGN should note it does NOT cover the class-(c) inline pins above.

## Aug-11 vs Aug-28 delta (evidence trail)

- Period: `January 1, 2026 - August 11, 2026` -> `January 1, 2026 - August 28, 2026` (generated 2026-08-29, CSV l.5-6).
- Positions: identical set, identical quantities (18: 15 USD / 2 EUR / 1 GBP). Only the marks moved (all re-priced to the Aug-28 close).
- Ledger: exactly one new entry - `Trades,Data,Order,Stocks,USD,SBIO,"2026-08-13,...",5,...` (CSV l.438), a BUY, commission -1.70. It is the only trade dated after 2026-08-11.
- That single trade fully explains: `IB_LEDGER_COUNTS["BUY"]` 92->93 and `commissions_total` 215.16 -> 216.86 (delta 1.70). `SELL` stays 77.
- New symbols: none (SBIO first bought 2026-08-05, already in the Aug-11 export and already fully wired: `app/core/symbols.py:69`, `golden_market_data.json`, `app/instruments/etf_sector_resolution.py`).
- Fully-sold-since-Aug-11 symbols: none.
