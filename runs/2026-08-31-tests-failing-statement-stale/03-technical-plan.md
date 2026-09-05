REPORT 2026-08-31-tests-failing-statement-stale/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    DESIGN pass, read-only order; no verification command specified. All pin values are cited from 02-scout-map.md's table + recipes, not re-derived here.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - test lane: re-pin the 14 changed constants in services/quant-engine/app/tests/statement_truths.py from 02's recipe output — see § Fix contract: statement_truths.py
  - test lane: do NOT transcribe BUY 92->93, IB_RAW_MIXED_CURRENCY_SUM, IB_BASE_WEIGHTS_PCT, IB_POSITION_HHI_BASE from 02 — regenerate by importing the CSV — see § Regeneration procedure
  - test lane: correct statement_truths.py docstring line 4 (2026-06-30 -> 2026-08-28) and line 30 (2026-08-11 -> 2026-08-28); leave lines 48-51 AMZN note as-is — see § Fix contract: statement_truths.py
  - test lane: regenerate the ~15 inline replay pins in test_ledger_replay_audit.py from observed pytest failure values and append a "2026-08-28:" continuation to each US-33.4 history comment — see § Fix contract: replay-audit test files
  - test lane: regenerate the ~8 inline pins in test_portfolio_state.py the same way; IB_POSITION_COUNT / IB_REPLAY_UNIVERSE_SIZE asserts (l.142-143) stay unchanged — see § Fix contract: replay-audit test files
  - DESIGN JUDGMENT RESOLVED: leave the replay pins inline, amend the workflow doc (option ii) — see § Design judgment: re-home vs amend
  - docs lane (close-out): amend docs/architecture/testing-architecture.md "Statement refresh workflow" step 3 sentence + closing paragraph to acknowledge the replay-pin class — see § Design judgment: re-home vs amend
  - quant-audit: independently recompute the 7 consistency anchors against the raw docs/IB2026.csv lines, NOT against statement_truths.py — see § Quant-audit anchor
  - scope confirmed from 02: no app/instruments/registry.py, no schema, no analytics/, no frontend, no docs/contracts/, no docs/product/ — test lane + docs lane only — see § Scope confirmation
  - swap-simulation meta-test (test_statement_refresh.py) needs NO code change; its blindness to class-(c) replay pins is a pre-existing gap, producer follow-up — see § Swap-simulation meta-test
  - lane order: test -> quant-audit -> integration -> review -> docs close-out -> human one-commit — see § Lane split and order
  - engine-dependent pins (IB_INSTRUMENT_COUNT, IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK, IB_ABSENT_SYMBOLS): named tell-line per pin if still red after the pin pass — see § Engine-dependent pins: the tell

risks:
  - class-(c) regeneration assumes the replay tests assert-false rather than error; a shifted date-indexed pin (peak.date, withheld-date lists, len(states)==148) could raise a KeyError/IndexError instead — then the test lane fixes the lookup, not just the literal — see § Risks
  - IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK and IB_INSTRUMENT_COUNT depend on engine behaviour 02 did not execute; if either moves it is beyond a pin refresh and must be escalated, not absorbed
  - option (ii) leaves the swap-simulation meta-test blind to the replay pins; the real fix is a diff_replay_truths harness, which is a future story for the producer, not this run
  - no FMP key / network needed: the human already ran refresh_statement.py, both golden artifacts are staged and Aug-28-consistent per 02
  - producer's combined-commit traceability concern (probe_engine hardening + statement refresh in one commit) is unresolved and re-surfaces at close-out; not a design matter

## Orchestrator brief

- DESIGN JUDGMENT RESOLVED: the ~23 inline replay pins stay inline; amend testing-architecture.md instead of re-homing them (option ii). Reason: they are replay-engine-derived regression pins bound to the Epic 31 F-1..F-5 narrative, already hand-regenerated each refresh (US-33.4 pre/post comments are prior art); statement_truths.py is importer-scoped by contract.
- Lane split: test lane (statement_truths.py pins + its own docstring + the 2 replay test files) then quant-audit (gate) then integration (gate) then review (gate) then docs lane (testing-architecture.md only, close-out) then human one-commit.
- Scope confirmed from 02: NO registry, schema, analytics/, frontend, docs/contracts/, docs/product/. Test lane + docs lane only. No new/absent symbols; SBIO's one new BUY is already wired.
- quant-audit gate is REQUIRED: re-pinned TWR (4.77->5.51%), terminal NAV, currency split and implied FX are guardrail-1 financial reference truth; audit checks them against the raw CSV, not the pin module.
- Swap-simulation meta-test needs no code change; note its replay-pin blind spot as a producer follow-up.
- Sections below: Technical plan (contract / reuse / decisions / lanes summary) · Fix contract: statement_truths.py (the 14 changed constants + docstring) · Regeneration procedure (the deterministic recipe + the 4 values not to transcribe) · Fix contract: replay-audit test files (the inline pins in the 2 files) · Design judgment: re-home vs amend (the call, cost of each, prior art) · Quant-audit anchor (7 consistency checks + their CSV sources) · Engine-dependent pins: the tell · Swap-simulation meta-test · Scope confirmation · Lane split and order · Risks.
- Blocks dispatch: nothing.

## Technical plan

This is a fixture/pin refresh, not a methodology change. `docs/IB2026.csv` was
swapped Aug-11 -> Aug-28 export without running the pin-update step of the
documented statement-refresh workflow. Holdings are byte-identical between the
two exports (02); only the marks moved, period totals/TWR recomputed, and one
new trade (`SBIO` BUY 5u 2026-08-13, commission -1.70) was added. 41 backend
tests fail, all downstream of stale pins.

### contract

There is no backend/frontend boundary in this change. The "contract" here is
the set of pinned reference values the test suite asserts the committed IB
statement produces. It has two homes:

1. `services/quant-engine/app/tests/statement_truths.py` — importer-derived
   statement truths, checked by `diff_statement_truths`. Importer-only
   dependency (no replay engine).
2. Inline `pytest.approx` pins in `test_ledger_replay_audit.py` and
   `test_portfolio_state.py` — replay-engine-derived (terminal MV, TWR-day %,
   peak date, `len(states)`, cash-anchor residual, reconciliation adjustment,
   per-symbol replayed value, HHI/vol ratios). Depend on the frozen golden +
   the replay engine.

Both must end Aug-28-consistent. Neither changes a Pydantic schema, a
`types.ts`, or a `docs/contracts/*` field — confirmed against 02's blast-radius
analysis.

### reuse

- `diff_statement_truths(snapshot)` (statement_truths.py:124) — the arbiter.
  `test_importer_csv.py::test_statement_matches_truths_module` prints exactly
  which pins moved. The pin pass is done when this returns `[]`.
- 02 § "Regeneration recipes" — the deterministic, network-free snippet
  (`import_statement(STATEMENT_2026_CSV_PATH)` + `replay_symbol_universe` +
  the base-weight/HHI formulas). Run it; read the printed values; write them.
- The `replay_context` / frozen-`FrozenMarketData` fixture already in both
  replay test files — the inline pins regenerate by re-running those modules
  against the staged Aug-28 golden; the failure messages carry the new values.
- The existing `US-33.4: <pre> pre-refresh; <post> after` inline comments —
  the established format for recording a pin's movement across a refresh;
  extend it, do not strip it.

### decisions

1. **Replay pins stay inline; the doc is amended (option ii).** Full reasoning,
   cost of each option, and prior art in § "Design judgment: re-home vs amend".
2. **`statement_truths.py` docstring lines 4 and 30 are the test lane's**, not
   the docs lane's — the file lives under `app/tests/`. Docs lane touches only
   `docs/architecture/testing-architecture.md`.
3. **No `docs/product/` work.** Producer resolved: no story. An Epic 28
   slice-log line is the producer's optional call at close-out, explicitly out
   of this plan.
4. **Swap-simulation meta-test: no code change this run.** It goes green when
   the `statement_truths.py` totals/TWR/fx pins are corrected. Its structural
   blindness to the replay pins is pre-existing — recorded as a follow-up, not
   fixed here.
5. **Engine-dependent pins are pin-refresh candidates only if they move for a
   data reason.** If `IB_INSTRUMENT_COUNT` or `IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK`
   shifts, that is an importer/exposure-engine behaviour change — escalate,
   do not re-pin silently. § "Engine-dependent pins: the tell".

### lanes

`test` -> `quant-audit` -> `integration` -> `review` -> `docs` (close-out) ->
human commit. Detail and each lane's boundary in § "Lane split and order".

### risks

See the `risks:` block above and § "Risks" below.

---

## Fix contract: statement_truths.py

Owner: **test lane**. All values from 02's pin-by-pin table. The `check`
helper rounds totals to 2dp, TWR to 6dp, fx to 4dp, pinned-position fields to
6dp — write values at least that precise.

**14 constants change:**

| Constant | line | Aug-11 (current) | Aug-28 (required) | How the test lane obtains it |
|---|---|---|---|---|
| `IB_STATEMENT_PERIOD` | 32 | `"2026-01-01 - 2026-08-11"` | `"2026-01-01 - 2026-08-28"` | `S.statement.statement_period` |
| `IB_LEDGER_COUNTS["BUY"]` | 62 | `92` | `93` | `Counter(e.entry_type ...)` — **regenerate, do not transcribe** |
| `IB_TOTALS_2DP["ending_nav"]` | 75 | `65429.98` | `65892.74` | `S.statement_totals.ending_nav` @2dp |
| `IB_TOTALS_2DP["cash_total"]` | 76 | `507.00` | `146.07` | `.cash_total` @2dp |
| `IB_TOTALS_2DP["stock_total"]` | 77 | `64922.99` | `65746.67` | `.stock_total` @2dp |
| `IB_TOTALS_2DP["commissions_total"]` | 82 | `215.16` | `216.86` | `.commissions_total` @2dp |
| `IB_TWR_PCT` | 85 | `4.765666` | `5.506619` | `.time_weighted_return_pct` @6dp |
| `IB_IMPLIED_FX_4DP` | 88 | `{"EURUSD":1.1543,"GBPUSD":1.3508}` | `{"EURUSD":1.1583,"GBPUSD":1.3535}` | `.fx_rates` @4dp |
| `IB_PINNED_POSITIONS["DEFS"]` | 46 | `close_price 6.496, market_value 3248.0, unrealized_pnl 451.524985` | `close_price 6.148, market_value 3074.0, unrealized_pnl 277.524985` | `{p.symbol:p for p in S.positions}["DEFS"]` — `quantity 500`, `cost_basis 2796.475015` UNCHANGED |
| `IB_PINNED_POSITIONS["SEMI"]` | 47 | `market_value 2929.2, unrealized_pnl 166.2` | `market_value 2885.6, unrealized_pnl 122.6` | ditto |
| `IB_PINNED_POSITIONS["VUAA"]` | 51 | `market_value 11964.8` | `market_value 12004.8` | ditto — `quantity 80`, `cost_basis 10081.463136` UNCHANGED |
| `IB_RAW_MIXED_CURRENCY_SUM` | 100 | `62031.85` | REGEN (02 est. `62843.22`) | `round(sum(p.market_value for p in S.positions), 2)` — **regenerate, do not transcribe** |
| `IB_BASE_WEIGHTS_PCT` | 102 | `{"SEMI":6.09,"SXRV":15.70,"VDST":24.70,"VUAA":18.43}` | REGEN (02 est. `{"SEMI":5.94,"SXRV":15.55,"VDST":24.44,"VUAA":18.26}`) | recipe base-weight formula — **regenerate, do not transcribe** |
| `IB_POSITION_HHI_BASE` | 104 | `0.138194` | REGEN @6dp | recipe HHI formula — **regenerate, do not transcribe** |

**Explicitly UNCHANGED** (the pin pass must leave these and `diff_statement_truths`
must return `[]` after the edit): `IB_ACCOUNT_ID`, `IB_BASE_CURRENCY`,
`IB_POSITION_COUNT` (18), `IB_POSITIONS_BY_CURRENCY` (`{USD:15,EUR:2,GBP:1}`),
`IB_INSTRUMENT_COUNT` (70), `IB_REPLAY_UNIVERSE_SIZE` (68), `IB_PINNED_INSTRUMENTS`
(AAPL/CIBR), `IB_TOTALS_2DP` keys `starting_nav` / `dividends_total` /
`withholding_tax_total` / `interest_total` / `other_fees_total` / `deposits_total`,
`IB_LEDGER_COUNTS` keys `SELL` (77) / `DIVIDEND` (25) / `WITHHOLDING_TAX` (28) /
`INTEREST` (1) / `FEE` (5) / `DEPOSIT` (1), `IB_SECTOR_EXAMPLES`,
`IB_ABSENT_SYMBOLS`, `IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK`.

**Docstring corrections (same file, test lane):**

- Line 4: `period 2026-01-01 - 2026-06-30` -> `period 2026-01-01 - 2026-08-28`
  (currently TWO refreshes stale — it was never bumped at the Aug-11 refresh).
- Line 30: section comment `(period 2026-01-01 - 2026-08-11)` ->
  `(period 2026-01-01 - 2026-08-28)`.
- Lines 48-51 (`# USD pin was AMZN until the 2026-08-11 refresh ...`): leave
  as-is. It documents why VUAA is the USD pin and is still literally true; it
  is not a current-period claim.

## Regeneration procedure

Owner: **test lane**. Deterministic, no network — the Aug-28 CSV and both
golden artifacts are already in the working tree. Run 02 § "Regeneration
recipes" verbatim from `services/quant-engine`:

```python
from collections import Counter
from app.importers.interactive_brokers_csv import import_statement
from app.tests._statement_fixtures import STATEMENT_2026_CSV_PATH
from app.engine.portfolio_state import replay_symbol_universe

S = import_statement(STATEMENT_2026_CSV_PATH)
print(S.statement.statement_period)
print({k: getattr(S.statement_totals, k) for k in
       ("starting_nav","ending_nav","cash_total","stock_total","dividends_total",
        "withholding_tax_total","interest_total","other_fees_total",
        "commissions_total","deposits_total")})
print(S.statement_totals.time_weighted_return_pct, S.statement_totals.fx_rates)
print(Counter(e.entry_type for e in S.ledger_entries))
print(len(S.instruments), len(replay_symbol_universe(S)))
print(round(sum(p.market_value for p in S.positions), 2))     # IB_RAW_MIXED_CURRENCY_SUM
fx = S.statement_totals.fx_rates
base = {p.symbol: p.market_value * fx.get(f"{p.currency}USD", 1.0) for p in S.positions}
den = sum(base.values())
print({s: round(base[s]/den*100, 2) for s in ("SEMI","SXRV","VDST","VUAA")})  # IB_BASE_WEIGHTS_PCT
print(round(sum((v/den)**2 for v in base.values()), 6))       # IB_POSITION_HHI_BASE
```

**Values the test lane must NOT copy from 02** (02 marks them scout
hand-derivations from an 888-line CSV): `IB_LEDGER_COUNTS["BUY"]` `92->93`,
`IB_RAW_MIXED_CURRENCY_SUM`, `IB_BASE_WEIGHTS_PCT`, `IB_POSITION_HHI_BASE`.
Take these from the snippet output only.

Before writing the weight/HHI values, confirm `den` equals both
`total_base_market_value(S)` (`app.analytics.currency`) and the corrected
`IB_TOTALS_2DP["stock_total"]`, and that the raw-sum helper actually used by
`test_currency_conversion.py` matches the `round(sum(...))` above. If they
disagree, stop — that is a real finding, not a pin update.

## Fix contract: replay-audit test files

Owner: **test lane**. These are the class-(c) pins from 02 — inline
`pytest.approx` literals that shift because the Aug-28 window adds ~12 trading
days and re-marks every position. Regeneration is deterministic: run each
module against the staged Aug-28 golden; the assertion-failure messages carry
the observed values; transcribe the observed value into the literal AND append
a `2026-08-28: <value>` continuation to the adjacent `US-33.4:` history
comment. No hand-derivation, no golden regen.

**`test_ledger_replay_audit.py`** (~15 pins, lines per 02):
`stock_total approx 64_922.99` (l.519, l.645), `total_market_value approx
64_896.27` (l.517, l.649), `peak.total_market_value approx 65_377.31` +
`peak.date == "2026-08-10"` (l.641-642), `len(states) == 148` (l.623),
`len(ratios) == 61` (l.606), `reconciliation_adjustment approx -19.98`
(l.177, l.676), `anchor.residual approx 46.69` (l.134), `median_weight approx
0.0650` (l.420), `twr_vol / neutral_vol` `0.1381 / 0.1491` (l.429-430),
`money_weighted_return_pct approx 2.76` + `investment_gain approx 1_645.99`
(l.682-683), the withheld-date list (l.735-740), the per-day TWR
approximations (l.347-351, l.377-384, l.456-465). Date-indexed pins
(`peak.date`, withheld-date lists) shift with the window — update to observed.

**`test_portfolio_state.py`** (~8 pins, lines per 02):
`day_one.total_market_value approx 49_050.54` (l.191), `drift approx 2_620.74`
(l.233), `by_symbol["SXRV"] approx 10_192.01` / `["SEMI"] approx 3_956.76` /
DEFS (l.702-706), `terminal.total_market_value approx 64_896.27` (l.711),
`states[0].cash["USD"] approx 4_677.02` (l.757), `anchor.residual approx
46.69` (l.773), `reconciliation_adjustment approx -19.98` (l.963). The
`IB_POSITION_COUNT` / `IB_REPLAY_UNIVERSE_SIZE` asserts (l.142-143) are
truths-module reads and stay unchanged. Lines 918/936 and the 300-1460 block
are synthetic `_snapshot` fixtures — not IB2026, do not touch.

**Prior art:** both files already carry `US-33.4: <pre> pre-refresh; <post>
after` comments at ~12 sites (grep-confirmed: replay-audit l.126, l.174,
l.238, l.342, l.399, l.461-462, l.488, l.506-508; portfolio_state l.136-137,
l.446, l.698, l.915, l.932-933, l.960). The project has already accepted these
pins as hand-regenerated each refresh — this plan follows that precedent, it
does not invent it.

## Design judgment: re-home vs amend

**RESOLVED: option (ii) — leave the replay pins inline, amend the workflow doc.**

**Option (i): re-home into `statement_truths.py` or a sibling
`replay_truths.py` now.**
- Cost: high. The ~23 pins are heterogeneous (money, percentages, dates,
  counts, ratios), each compared with a per-test `approx` tolerance, and each
  is meaningful only inside its test's F-1..F-5 narrative — the file docstring
  states "the magnitudes only make sense in that order". A constants module
  strips that. It also needs a `diff_replay_truths` that runs the replay
  engine + frozen golden, a heavier dependency than `statement_truths.py`'s
  importer-only surface. Both test files would be rewritten to import ~23
  names. The inline `US-33.4:` history comments would be lost or duplicated.
- Benefit: the swap-simulation meta-test and the workflow's "structural tests
  must not fail" claim become literally true.

**Option (ii): leave inline, amend the doc.**
- Cost: low. One paragraph in `docs/architecture/testing-architecture.md`.
- Benefit: preserves the Epic 31 regression-pin narrative (deliberate, and
  called out in the file docstring). Keeps `statement_truths.py` scoped to
  importer-derived truths — the class distinction US-33.4 itself drew. The
  US-33.4 pre/post comments are prior art that the project already treats
  these as a hand-regenerated refresh step.
- Downside: the swap-simulation meta-test stays blind to these pins; a
  refresher who skips the step gets a multi-file failure with no single
  self-documenting pointer. This is the current status quo and the failures
  still name their tests.

**Why (ii):** the cost asymmetry is large (a doc paragraph vs a multi-file
refactor + a new diff harness, with no story to fund it), and the premise of
(i) is questionable — US-33.4 re-homed values that *structural* tests had no
business pinning; the Epic 31 tests exist *precisely* to pin replay
magnitudes, so pinning them inline is correct by design, not a defect. The
genuinely better end-state (a `diff_replay_truths` harness the meta-test can
assert against) is a future story for the producer, recorded in `risks`.

**Docs lane change (close-out), `docs/architecture/testing-architecture.md`
only:**
- "Statement refresh workflow" step 3, the sentence "Structural tests derive
  their expectations from the snapshot itself and must not fail on a refresh."
  — add a step 3b / named paragraph: a distinct class of **replay-audit
  regression pins** in `test_ledger_replay_audit.py` and
  `test_portfolio_state.py` is replay-engine-derived (not importer-derived),
  carries inline pre/post-refresh history comments, and is hand-regenerated
  against the frozen golden on each refresh.
- The closing paragraph ("anything else failing on a refresh is a structural
  test wrongly pinning statement truths (fix the test)") — narrow it to
  exclude that named class, or it keeps asserting something false.

## Quant-audit anchor

Gate: **quant-analyst AUDIT**, REQUIRED (guardrail 1 — re-pinned TWR, terminal
NAV, currency split, implied FX are financial reference truth). Recompute
**independently against the raw `docs/IB2026.csv`** (the lines 02 cites), NOT
against `statement_truths.py` (the artifact under test):

1. **`stock_total` internal consistency.** `IB_TOTALS_2DP["stock_total"]`
   (65746.67) == Σ over 18 positions of `market_value × implied_fx[currency]`
   (USD ×1), using `IB_IMPLIED_FX_4DP`. Also == CSV line 16 (65746.66968)
   directly. Source: CSV Open Positions rows incl. EUR line 226 (DEFS), GBP
   line 230 (SEMI), line 247 (VUAA); CSV line 16.
2. **TWR.** `IB_TWR_PCT` (5.506619) == CSV line 20 (5.506619351%) @6dp; the
   importer must pass it through untransformed.
3. **NAV bridge.** `ending_nav` (65892.74) == `starting_nav` (52381.12) + Σ
   NAV changes (deposits 9963.00 + dividends − withholding − fees ± trading
   P&L) per the CSV "Change in NAV" section. Cross-check `ending_nav` ==
   `cash_total` (146.07) + `stock_total` (65746.67). Source: CSV lines 15, 16,
   32.
4. **Implied FX.** `IB_IMPLIED_FX_4DP["EURUSD"]` (1.1583) == EUR
   base-restated Open-Positions total / EUR local Open-Positions total
   (02: 13780.99008 / 11897.6); `GBPUSD` (1.3535) == 3905.6596 / 2885.6.
   Source: CSV Open Positions per-currency subtotal rows.
5. **Commission / BUY delta.** `commissions_total` 216.86 − 215.16 == 1.70 ==
   the single new trade's commission; `IB_LEDGER_COUNTS["BUY"]` +1 from the
   same row. Source: CSV SBIO BUY row (~line 438, 2026-08-13), CSV line 30
   (216.8612606).
6. **HHI / base weights.** `IB_POSITION_HHI_BASE` == Σ(base_weight_i)² with
   base_weight_i = base_value_i / stock_total; every `IB_BASE_WEIGHTS_PCT`
   entry == base_value / stock_total × 100 for its symbol.
7. **Trust honesty (guardrails 2-4).** Confirm the refresh touched no
   methodology, no schema, no trust-state logic — no `withheld`/`unavailable`
   distinction changed, no truth class mixed. It is a fixture refresh; the
   audit confirms it stayed one.

## Engine-dependent pins: the tell

02 judges these unchanged but did not execute the engine. If one is still red
after the pin pass, the named line is the tell — and it is an escalation, not
a re-pin:

- **`IB_INSTRUMENT_COUNT` (70):** tell = `test_importer_csv.py:195` +
  `diff_statement_truths` "instrument count" line. A move means
  `_parse_instruments` behaviour shifted on the new CSV (a row now fails
  parsing, or dedupe changed) — a real importer finding.
- **`IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK` (`["MSFT","AAPL"]`):** tell =
  `test_exposure_engine.py:558`. A move means exposure-overlap ordering
  changed (AAPL is now 0-qty and could drop from the delta list). Re-pin only
  from observed output AND route to quant-audit — overlap ordering is
  exposure-engine output, not a statement truth.
- **`IB_ABSENT_SYMBOLS`:** tell = `diff_statement_truths` "absent-symbol pin
  X: now held" line + `test_analytics.py` l.604-621. 02 confirms holdings are
  byte-identical, so this should not fire; if it does, it is a real
  composition change.

## Swap-simulation meta-test

`test_statement_refresh.py::test_swap_simulation_fails_only_the_documented_pin_surface`
and `::test_committed_statement_yields_zero_truths_diffs` both currently FAIL
only because the committed pins are stale — the swap test's negative
assertions `assert "totals." not in labels` / `assert "fx_rates" not in
labels` (l.111-112) trip on the stale totals/TWR/fx diffs. Both go green the
moment the `statement_truths.py` totals/TWR/fx pins are corrected. **No code
change to this file this run.**

Known gap (do not fix here): the meta-test only inspects the diff of its own
simulated mutation; it does not run the full suite, so it cannot see the
class-(c) replay pins. Under option (ii) the workflow's "only the documented
pin surface" claim therefore has a standing exception. Closing it properly
needs a `diff_replay_truths` harness the meta-test can assert against — a
future story for the producer.

## Scope confirmation

From 02, confirmed:

- **No `app/instruments/registry.py` edit.** No new symbols vs Aug-11, no
  newly-absent symbols. `SBIO` gains one BUY (2026-08-13) and is already fully
  wired (`app/core/symbols.py:69`, `golden_market_data.json` series,
  `app/instruments/etf_sector_resolution.py`). `test_registry_isin_integrity.py`
  is not in the failure set.
- **No schema change** (`app/schemas/**` untouched — the schema hook does not
  fire).
- **No `analytics/` change**, no formula, no weighting, no return basis.
- **No frontend change** (`apps/desktop/src/**`).
- **No `docs/contracts/**` change** — no field added/removed/retyped.
- **No `docs/product/**` change** — producer resolved there is no story; an
  Epic 28 slice-log line is the producer's optional close-out call, out of
  this plan.
- Golden artifacts (`dashboardGoldens.ts`, `golden_market_data.json`) are
  already regenerated, staged, and Aug-28-consistent — no golden work.

## Lane split and order

1. **test lane** — the re-pin. Files: `statement_truths.py` (14 constants +
   docstring l.4, l.30), `test_ledger_replay_audit.py` (~15 inline pins +
   history comments), `test_portfolio_state.py` (~8 inline pins + history
   comments). Method: 02's recipe for statement_truths.py; observed
   pytest-failure values for the replay files. Verification:
   `python scripts/run_all_tests.py` green (or
   `mcp__project__run_tests(scope="full")`). No golden regen.
2. **quant-audit** (gate, REQUIRED) — the 7 anchors in § "Quant-audit anchor",
   recomputed against the raw CSV. Runs before integration: guardrail 1 means
   the maths gate precedes the engineering gate.
3. **integration** (gate, REQUIRED) — tech-lead INTEGRATION: no schema /
   analytics / contract drift; the pin edits are faithful to the recipe and
   the CSV; full suite green; `git diff apps/desktop/src/test/dashboardGoldens.ts`
   is the expected refresh artifact (here it is a *real* refresh, so it
   stays — do not reset it).
4. **review** (gate) — reviewer: no story, so acceptance is against the
   workflow DoD — suite green against the Aug-28 export, and only the
   documented surfaces (the two pin homes + the doc) changed.
5. **docs lane** (close-out) — `docs/architecture/testing-architecture.md`
   only, per § "Design judgment". Not `docs/product/`. The
   `statement_truths.py` docstring is the test lane's (file under
   `app/tests/`).
6. **human** — one commit (probe_engine hardening + statement refresh
   together, per the resolved decision), after a green suite. The producer's
   split-commit concern re-surfaces here as a flag, not a blocker.

## Risks

- Class-(c) regeneration assumes the replay tests assert-false and surface the
  new value in the failure message. If a shifted date-indexed pin instead
  raises (KeyError on `peak.date`, IndexError on a withheld-date slice,
  `len(states)` cascade), the test lane fixes the lookup/logic, not just the
  literal — and flags it, because a structural break is beyond a pin refresh.
- `IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK` / `IB_INSTRUMENT_COUNT` moving is an
  engine-behaviour change — escalate per § "Engine-dependent pins".
- Option (ii) leaves the swap-simulation meta-test blind to the replay pins;
  the `diff_replay_truths` harness that would close it is a producer
  follow-up, not this run.
- No FMP key / network required — the human already ran `refresh_statement.py`;
  both golden artifacts are staged and Aug-28-consistent (02).
- The producer's combined-commit traceability concern (MCP/probe_engine
  hardening landing in the same commit as the statement refresh) is unresolved
  and re-surfaces at close-out. Not a design-pass matter.
