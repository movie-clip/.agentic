REPORT 2026-08-31-tests-failing-statement-stale/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail:    exit 0. Backend 979 passed (pytest -n auto, 49 warnings); frontend 359 passed / 40 files; tsc --noEmit clean; dead-code strict (ruff+vulture+knip) clean. Matches 04b and 06.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs lane (08): testing-architecture.md § "Statement refresh workflow" step 3 / closing paragraph amendment (option ii) is not in the tree yet — expected, docs close-out owns it, not a gate failure.
  - human before commit: `git checkout -- services/quant-engine/app/scripts/golden_market_data.json` drops the unstaged float32-noise delta (24 ACOMO.AS adjClose values, 8th sig digit) — per 06.

risks:
  - Widening (b) de-dilution tripwire now sits at 2.32% against its new rel=0.03 band — a further drift at the next refresh needs a second-order term, not a third widening (carried from 05/06).
  - 05 checked replay-derived pins (terminal MV, per-symbol MV, mwr, gain, vols, len(states)=161, peak.date) for consistency and magnitude plausibility only, not day-by-day recompute — the frozen replay engine was not run. statement_truths.py pins WERE independently CSV-recomputed.
  - Combined-commit traceability: probe_engine hardening (prior CLOSED run) is staged alongside this refresh for one commit — producer flagged, human chose one-commit. Re-surfaces at close-out, not reopened here.
  - Frozen golden's Euro listings (DEFS.L/SXRV.DE/SEMI.L) end 2026-08-27, one day before the 08-28 marks — source of widening (a); a future refresh where the gap widens should re-capture the Euro series, not the tolerance.

## Orchestrator brief

- VERDICT: PASS. No story; acceptance judged against testing-architecture.md
  § "Statement refresh workflow" as the DoD surrogate, per 03 § Lane split.
- All six definition_of_done items met: original request satisfied (41 failures
  root-caused + resolved), workflow steps 3-5 done, trust-state honesty intact,
  change surface bounded, own suite green, both tolerance widenings gated.
- Own verification: `python scripts/run_all_tests.py` exit 0 — backend 979,
  frontend 359, tsc clean, dead-code clean. Matches 04b and 06.
- No blocking findings. No CHANGES_REQUESTED (not a tech-lead gate). Four
  observations in `risks`, two carries in `handoff` — none hold the run.
- Known-expected gaps, NOT failed per the order's non_goals: testing-
  architecture.md amendment not yet in tree (docs lane 08); unstaged golden
  float-noise delta (human `git checkout`).
- Sections below: DoD walk (item-by-item, with the failure-cluster table and
  the falsifiability check).
- Blocks close-out: nothing. On PASS → 08 docs close-out.

## DoD walk

### 1. Original request: "check why tests are failing, and fix it" — SATISFIED

run.md § Diagnosis: `run_all_tests.py` EXIT 1, 41 failed / 938 passed backend;
root cause = `docs/IB2026.csv` swapped Aug-11 → Aug-28 export without running the
pin-update step of the documented statement-refresh workflow, leaving
`statement_truths.py` and ~34 inline replay pins on stale Aug-11 values.

Failure clusters from run.md § Diagnosis, each now addressed:

| cluster | how resolved | evidence |
|---|---|---|
| test_importer_csv | statement_truths.py 14 constants + docstring re-pinned; `diff_statement_truths()` returns `[]` | 04, suite green |
| test_statement_refresh | swap-simulation + zero-diff meta-tests go green once totals/TWR/fx pins corrected (no code change) | 03 § Swap-simulation, suite green |
| test_exposure_engine | reads truths module (IB_TOP_OVERWEIGHTS unchanged — no engine move) | 04 handoff, suite green |
| test_currency_conversion | reads IB_RAW_MIXED_CURRENCY_SUM / IB_BASE_WEIGHTS_PCT / IB_POSITION_HHI_BASE from truths module | 04, 05 anchor 6 |
| test_ledger_replay_audit | ~17 inline replay pins refreshed to observed Aug-28 values + history comments | 04 diff |
| test_portfolio_state | 8 inline replay pins refreshed (incl. l.918/936 real IB2026 pins, line-drift corrected) | 04, 06 DoD walk item 2 |
| test_analytics | 9-test / 16-assertion class-(c) cluster (l.8493-8958) refreshed — scope gap found by 04, closed by 04b | 04b diff |

Own suite run: `python scripts/run_all_tests.py` EXIT 0, backend 979 passed,
frontend 359 passed, tsc clean, dead-code clean. The 41 failures are gone.

### 2. Workflow steps 3-5 (testing-architecture.md § Statement refresh workflow) — SATISFIED

- **Step 3 (update the statement-truth pins in ONE module).** Done in
  `statement_truths.py`: the 14 constants match 03's Fix-contract table exactly
  (IB_STATEMENT_PERIOD; DEFS/SEMI/VUAA pinned positions; BUY 92→93;
  ending_nav/cash_total/stock_total/commissions_total; TWR 4.765666→5.506619;
  implied FX; raw mixed sum 62031.85→62843.22; base weights; HHI
  0.138194→0.135814) + docstring l.4 (2026-06-30→2026-08-28, was two refreshes
  stale) and l.30. Every entry on 03's "Explicitly UNCHANGED" list is absent
  from the diff. Values agree with 05's independent CSV recompute.
- **Replay-pin regeneration** (the class the doc does not yet name — option ii):
  done inline in test_ledger_replay_audit.py, test_portfolio_state.py,
  test_analytics.py, each pin carrying a `# 2026-08-28 statement refresh: <old>
  -> <new>` history line above the assertion, matching the US-33.4 prior-art
  format.
- **Step 4 (registry entries for brand-new holdings).** Correctly established as
  a no-op by 02/03 and re-confirmed here: the Open-Positions symbol set is
  byte-identical between the Aug-11 and Aug-28 exports (`comm` diff empty both
  directions). SBIO is a pre-existing holding (10u) that gained one BUY
  (2026-08-13, 5u, −1.70), already fully wired (app/core/symbols.py,
  golden series, etf_sector_resolution.py). No `app/instruments/registry.py`
  edit; `test_registry_isin_integrity.py` not in the failure set and green.
- **Step 5 (commit together).** The human's step — IB2026.csv,
  golden_market_data.json, dashboardGoldens.ts (staged, the human's
  refresh_statement.py output) plus the four unstaged test files. Not this
  gate's to perform.

### 3. Trust-state honesty — SATISFIED

The refresh did not collapse `withheld` into `unavailable` or relabel any trust
level:

- Withheld-date list is **unchanged**: `["2026-04-14","2026-04-17","2026-06-12",
  "2026-07-17"]` asserted verbatim in test_ledger_replay_audit.py l.758-763 and
  test_portfolio_state.py l.979-982; test_analytics.py still asserts
  `len(metadata.withheld_return_dates) == 4` and `[-1] == "2026-07-17"`.
- The withheld set is still asserted with named causes (unbacked-cash days,
  US-33.2 / US-34.4), not a silent unavailable — `assert "2026-04-17" in gaps
  # US-33.2, an unbacked-cash day` and the `gaps == set(withheld_return_dates)`
  identity are untouched.
- `anchor.trust == "verified"` assertions unchanged; the residual moved
  *toward* zero (46.69 → −1.15), still earned by a wide margin against
  `REPLAY_OPENING_CASH_RESIDUAL_SHARE` — nothing relabelled to stay
  publishable. Confirmed by 05 anchor 7.
- The only `"2026-08-11" → "2026-08-28"` string edits are terminal-date `not in`
  correctness guards, not trust-class changes.

### 4. Only documented surfaces changed — SATISFIED

Unstaged working-tree changes attributable to this run:
`statement_truths.py`, `test_analytics.py`, `test_ledger_replay_audit.py`,
`test_portfolio_state.py` — all under `app/tests/`. No `app/schemas/`, no
`app/analytics/`, no importer, no `app/instruments/`, no `apps/desktop/src/**`
(non-test), no `docs/contracts/`, no `docs/finance/`, no `docs/product/`. The
schema hook did not fire. Confirmed by 05 and 06 and re-checked here against
`git status`.

Out of this run's scope, correctly excluded: the staged `mcp_server/*` +
`test_mcp_tools.py` are the prior CLOSED run 2026-08-31-probe-engine-hardening;
the staged `IB2026.csv` / `golden_market_data.json` / `dashboardGoldens.ts` are
the human's `refresh_statement.py` output (workflow step 2), Aug-28-consistent
per 02/06. The unstaged `golden_market_data.json` 48-line delta is float32
round-trip noise (06 § Golden float-noise delta) — the human discards it before
commit.

### 5. The two tolerance widenings — SATISFIED (gated, justified)

Both in test_ledger_replay_audit.py, both the only loosened tolerances
(grep-confirmed by 06 across all three replay/analytics files — every other
`approx()` keeps its keyword and moves only the value):

- **F-4 raw-ratio** `abs=0.01 → rel=0.02` (l.277-291). Inline 4-line
  justification: frozen golden terminal close vs statement mark diverge up to
  ~1.8% per symbol (DEFS), per-line close-vs-mark noise; the USD-vs-local
  discrimination margin (~0.14, ~7× the band) is untouched. 05 verdict
  ACCEPTABLE with the non-overlapping-band argument.
- **De-dilution tripwire** `rel=0.02 → rel=0.03` (l.437-447). Inline 3-line
  justification: lower median cash weight (6.5%→4.9%) makes the 1/(1−w)
  first-order prediction more sensitive; observed ratio 1.076 vs predicted
  1.052 = 2.3%. 05 verdict ACCEPTABLE with a caveat (carried to risks).

A future reader can follow each from the comment alone.

### 6. Own full-suite run — SATISFIED

`python scripts/run_all_tests.py` from repo root: EXIT 0. Backend
`979 passed, 49 warnings in 31.47s`; frontend `359 passed (40 files)`; tsc
`--noEmit` clean; dead-code strict clean. Consistent with 04b (17:50) and 06
(18:07).

### Falsifiability check (gates.md § 2)

The acceptance target is a green suite against the committed Aug-28 export plus
a bounded change surface. The observation that would prove it false — a non-zero
`run_all_tests.py` exit, or a diff touching schema/analytics/registry — was
actively looked for: the suite was re-run from a clean invocation (exit 0,
979/359) and `git status` + `git diff` were read directly, not taken from the
upstream reports. The withheld-set falsifier (a shortened list or a
withheld→unavailable relabel) was checked by reading the literal assertions, not
inferred from "05 covered it".

## Verdict: PASS

All six definition_of_done items are met. No blocking findings. Observations for
the human / docs lane are in `risks` and `handoff` — none hold the run.
