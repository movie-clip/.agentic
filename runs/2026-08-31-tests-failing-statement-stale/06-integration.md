REPORT 2026-08-31-tests-failing-statement-stale/06
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py  (repo root)
  result:    PASS
  detail:    exit 0. Backend 979 passed (pytest -n auto); frontend 359 passed / 40 files; tsc --noEmit clean; dead-code strict (ruff+vulture+knip) clean. .claude/.last-test-pass rewritten 2026-08-31 18:07:46, fresher than every changed file. dashboardGoldens.ts regen produced no new drift (Aug-28-consistent).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - HUMAN before commit: `git checkout -- services/quant-engine/app/scripts/golden_market_data.json` drops the unstaged 48-line delta and keeps the staged refresh_statement.py capture — see § Golden float-noise delta.
  - probe_engine files in the staged set (server.py, probing.py, tools/testing.py, test_mcp_tools.py) are from CLOSED run 2026-08-31-probe-engine-hardening — present, not reviewed here, per order.
  - docs lane (07/08 close-out) still owes the testing-architecture.md option-(ii) amendment — not in the tree yet, expected.

risks:
  - Unstaged golden_market_data.json 48-line delta is float32 round-trip noise (24 ACOMO.AS adjClose values only, ~8th significant digit); benign and suite-green, but spurious churn if not discarded before commit — see § Golden float-noise delta.
  - Widening (b) de-dilution tripwire margin is thin: observed 2.32% against the new rel=0.03 band. Per quant-audit 05, a further drift needs a 2nd-order term, not a 3rd widening.
  - Frozen golden's European listings (DEFS.L / SXRV.DE / SEMI.L) end 2026-08-27, one day before the 08-28 marks — the source of widening (a). A future refresh where the gap widens should refresh the golden's Euro series, not the tolerance.
  - quant-audit 05 checked replay-derived pins for consistency + magnitude plausibility only, not day-by-day recompute (frozen replay engine not run); statement_truths.py pins WERE independently CSV-recomputed. Carry to close-out.
  - Combined-commit traceability: probe_engine hardening + statement refresh staged for one commit; producer flagged, human already chose one-commit. Re-surfaces at close-out — not reopened here.
  - test_ledger_replay_audit.py l.244 SEMI pin reframed from "broker stated MV 2929.20" to "golden SEMI.L quote values 200u at ~2892" (value 2929.20 -> 2892.00, tolerance abs=1.0 kept); sound because the golden Euro series ends 08-27. Observation, not a finding — see § DoD walk item 1.

## Orchestrator brief

- VERDICT: PASS. The re-pin work (unstaged: statement_truths.py + 3 test files) integrates coherently, is faithful to 03's contract and the CSV, and the full suite is green (backend 979 / frontend 359 / tsc / dead-code).
- No change requests. No BLOCKING, no SHOULD_FIX change request. Five carries to the human, all in `risks` above (golden-noise discard, thin widening-(b) margin, Euro-golden 1-day lag, replay-pin audit depth, combined-commit traceability).
- statement_truths.py: exactly the 14 constants from 03's Fix-contract table + docstring l.4/l.30; nothing on the "Explicitly UNCHANGED" list moved. Values match quant-audit 05's independent CSV recompute (HHI 0.135814, base weights, raw mixed sum 62843.22).
- Tolerance changes: exactly 2, both in test_ledger_replay_audit.py (F-4 raw-ratio abs=0.01->rel=0.02; de-dilution rel=0.02->rel=0.03), both with inline justification, both cleared by 05. Every other approx() keeps its tolerance keyword — grep-confirmed across all 3 files.
- l.918/936 line-drift call (04 § risks): CONFIRMED. test_implied_opening_cash_uses_converted_flows uses the ib2026_snapshot fixture — a real IB2026 pin, not synthetic. Synthetic _snapshot blocks in test_portfolio_state.py untouched.
- Scope: clean. No app/schemas/, analytics/, importers/, app/instruments/, frontend src, or docs/contracts/. probe_engine files in the staged set are prior-closed-run, noted not reviewed.
- ACTION REQUIRED of the human before commit: `git checkout -- services/quant-engine/app/scripts/golden_market_data.json` (drop the unstaged float-noise delta; keeps the staged refresh capture).
- Sections below: Golden float-noise delta (the 48-line analysis + discard instruction) · DoD walk (each definition_of_done item and its finding).
- Blocks close-out: nothing. On PASS -> 07 review, 08 docs close-out.

## Golden float-noise delta

`git diff services/quant-engine/app/scripts/golden_market_data.json` (UNSTAGED, on
top of the staged refresh_statement.py capture): 48 changed lines = 24 records,
**all `symbol: "ACOMO.AS"`, all `adjClose` only**. Samples:

| date | staged adjClose | unstaged adjClose | rel delta |
|---|---|---|---|
| 2026-01-23 | 24.02131462097168 | 24.021312713623047 | ~8e-8 |
| 2026-01-26 | 24.068601608276367 | 24.068599700927734 | ~8e-8 |
| 2026-01-29 | 23.64302635192871 | 23.643024444580078 | ~8e-8 |
| 2026-02-18 | 25.487180709838867 | 25.4871826171875 | ~8e-8 |

No `date`, `symbol`, `price`, or `volume` field changed on any record — `price`
and `volume` are byte-identical in every hunk. Every delta sits in the 7th-8th
significant digit, the signature of a float32 <-> Python-float repr round-trip.
ACOMO.AS is not an IB2026 holding (market-overlap universe symbol), so this is
untouched by the statement refresh.

**Conclusion: float32 rounding noise, NOT a real market-data change.** It does
not affect the suite (golden_market_data.json is a frozen input; only
`refresh_statement.py` regenerates it, and it is stable across two full-suite
runs). It is not this run's product — the staged version is the user's
`refresh_statement.py` capture.

**Discard before commit — the human, not this run** (read-only order):
`git checkout -- services/quant-engine/app/scripts/golden_market_data.json`
resets the working tree to the staged capture, dropping only the noise delta.

## DoD walk

1. **Re-pin diff faithful to 03 + CSV.** PASS. statement_truths.py diff = the 14
   constants in 03's Fix-contract table (IB_STATEMENT_PERIOD; DEFS/SEMI/VUAA
   pinned positions; BUY 92->93; ending_nav/cash_total/stock_total/commissions_total;
   TWR 4.765666->5.506619; implied FX; raw mixed sum 62031.85->62843.22; base
   weights; HHI 0.138194->0.135814) + docstring l.4 (2026-06-30->2026-08-28) and
   l.30 (2026-08-11->2026-08-28). "Explicitly UNCHANGED" list (IB_ACCOUNT_ID,
   IB_POSITION_COUNT, IB_INSTRUMENT_COUNT 70, IB_REPLAY_UNIVERSE_SIZE 68,
   IB_ABSENT_SYMBOLS, IB_TOP_OVERWEIGHTS_VS_STUB_BENCHMARK, unchanged totals keys,
   unchanged ledger keys) — none appear in the diff. Values match 05's CSV recompute.
   Inline replay pins across test_ledger_replay_audit.py / test_portfolio_state.py /
   test_analytics.py each carry a `# 2026-08-28 statement refresh: <old> -> <new>`
   line above the assertion (a fresh line rather than an appended continuation to
   the US-33.4 comment as 03's prose worded it — consistent across all files, prior
   US-33.4 comments preserved; cosmetic, not a finding). Synthetic `_snapshot`
   fixtures in test_portfolio_state.py: untouched — diff only hits ib2026 /
   ib2026_snapshot-based tests (l.702-712, l.776, l.922, l.941, l.965).

2. **l.918/936 line-drift call.** CONFIRMED 04 was right.
   `test_implied_opening_cash_uses_converted_flows(self, ib2026_snapshot)`
   (test_portfolio_state.py l.911) takes the `ib2026_snapshot` fixture — a real
   IB2026 statement pin, not a synthetic `_snapshot`. The adjacent synthetic test
   `test_cash_anchor_falls_back_to_the_derived_identity` (l.~885-909, builds
   `position("AAA", ...)`) is untouched. raw_mixed -1_549.28->-1_910.21 and
   implied 4_625.35->4_673.19 are correct re-pins; tolerances (abs=1.0 / abs=2.0)
   unchanged.

3. **The 2 tolerance widenings are the only tolerance changes.** CONFIRMED by
   grep over `git diff app/tests/` for `abs=` / `rel=` / `approx(`. Every other
   `approx()` assertion keeps its tolerance keyword identical old-vs-new (abs=2.0,
   abs=1.0, abs=0.1, abs=0.05, abs=0.02, abs=1e-3, abs=1e-4, abs=1e-5, abs=0.01,
   abs=0.005) and moves only the pinned value. The two exceptions:
   test_ledger_replay_audit.py F-4 raw-ratio `abs=0.01 -> rel=0.02` (3 assertions,
   one logical widening) and de-dilution tripwire `rel=0.02 -> rel=0.03` — each
   carries an inline justification comment, and quant-audit 05 cleared both as
   ACCEPTABLE with financial reasoning. No other test was loosened rather than
   re-pinned.

4. **Unstaged golden delta.** See § Golden float-noise delta. Float32 noise, not
   real; discard via `git checkout` before commit; the human does it.

5. **Full suite re-run.** PASS — `python scripts/run_all_tests.py` exit 0,
   backend 979 / frontend 359 / tsc / dead-code all green, `.claude/.last-test-pass`
   fresh at 18:07:46.

6. **Scope confirmation.** No `app/schemas/`, no `app/analytics/`, no importer,
   no `app/instruments/`, no frontend `src/` (only `src/test/dashboardGoldens.ts`,
   staged, the user's real Aug-28 refresh — stays per 03 § Lane split), no
   `docs/contracts/`, no `docs/finance/`, no `docs/product/`. probe_engine files
   (server.py, probing.py, tools/testing.py, test_mcp_tools.py) in the staged set
   are prior CLOSED run 2026-08-31-probe-engine-hardening — noted, not reviewed.
