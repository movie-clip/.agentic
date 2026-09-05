# RUN 2026-08-31-tests-failing-statement-stale
request:      check why tests are failing, and fix it
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
route:        full (statement refresh = multi-lane + financial reference truth)
express:      no
gates:        quant-audit PASS (05 — 7/7 CSV anchors CONFIRMED via independent recompute; both tolerance widenings ACCEPTABLE; replay-derived pins plausibility/consistency-checked NOT day-by-day — statement_truths.py pins WERE independently CSV-recomputed) · integration PASS (06 — full suite green 979/359/tsc/deadcode, re-pin diff faithful to CSV, the 2 widenings are the ONLY loosened tolerances, unstaged golden delta = float32 noise) · review PASS (07 — workflow DoD met, trust-state + withheld-day set intact, both widenings gated)
note:         full suite GREEN after 04+04b (backend 979 / frontend 359 / tsc / dead-code). 03 first dispatch died on a session rate-limit (429, no artifact) — retried, no model escalation. 04→04b was an orchestrator re-plan (scope gap: test_analytics.py held class-(c) pins 02/03 missed), NOT a gate change-request round.

## Diagnosis (orchestrator state-check, not a lane verdict)
- `python scripts/run_all_tests.py` → EXIT 1, **41 failed / 938 passed** (backend pytest). `.claude/.last-test-pass` marker is Aug 28 09:32 — stale, predates this.
- Every failure traces to `docs/IB2026.csv` being replaced with a fresh IBKR export (period `Jan 1 – Aug 11` → `Jan 1 – Aug 28, 2026`, generated 2026-08-29; new NAV totals, TWR 4.77%→5.51%, positions, commissions) **without running `python scripts/refresh_statement.py`**.
- `app/tests/statement_truths.py` still pins the Aug-11 export (`IB_STATEMENT_PERIOD = "2026-01-01 - 2026-08-11"`, `IB_POSITION_COUNT`, `IB_POSITIONS_BY_CURRENCY`, terminal market value, currency split). `test_statement_refresh.py::test_committed_statement_yields_zero_truths_diffs` failing is the direct confirmation.
- Failure clusters: test_analytics, test_ledger_replay_audit, test_importer_csv, test_portfolio_state, test_statement_refresh, test_exposure_engine, test_currency_conversion — all IB2026-statement-derived.
- **The 2026-08-31 probe_engine run is NOT implicated**: server.py / probing.py / testing.py / test_mcp_tools.py are not in the failure set; 63/63 mcp tests pass.
- Documented fix (statement_truths.py docstring + docs/architecture/testing-architecture.md#statement-refresh-workflow): run refresh_statement.py (needs FMP_API_KEY) → update pins + instrument-registry entries for new symbols → commit statement+goldens+fixture+truths together.
- **Blockers:** FMP_API_KEY not set in env (refresh_statement.py step 1 hard-errors); working tree is ALL STAGED (something ran `git add` — probe_engine changes staged together with the stale CSV/goldens), so a commit now = red main.

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | NONE |
| 02 | recon | — | scout | sonnet | 02-scout-map.md | DONE | NONE |
| 03 | design | DESIGN | tech-lead | sonnet | 03-technical-plan.md | DONE | NONE |
| 04 | test | — | test-engineer | sonnet | 04-test.md | PARTIAL | NONE |
| 04b | test | — | test-engineer | sonnet | 04b-test.md | DONE | NONE |
| 05 | quant-audit | AUDIT | quant-analyst | opus | 05-quant-audit.md | DONE | PASS |
| 06 | integration | INTEGRATION | tech-lead | sonnet | 06-integration.md | DONE | PASS |
| 07 | review | — | reviewer | sonnet | 07-review.md | DONE | PASS |
| 08 | docs | — | docs-engineer | sonnet | 08-docs.md | DONE | NONE |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| human-action | 06-integration | git | before commit: `git checkout -- services/quant-engine/app/scripts/golden_market_data.json` — drops the unstaged float32-noise delta, keeps the staged refresh_statement.py capture | CARRIED |
| human-decision | 01 + 06 + 07 | git | producer flagged: probe_engine hardening (prior CLOSED run) + this refresh are staged for ONE commit — human chose one-commit; still their call at commit time | CARRIED |
| pack_correction | 04b+04 | 08-docs.md § "Pack correction item 1: suggested wording" | blast-radius heuristic under-counts inline replay pins (3 files not 2); NO capabilities/ pack has a home — docs lane could NOT apply it; suggested wording ready in 08 report | CARRIED — unapplied pack correction (protocol/packs.md: real defect surfaced to human) |
| should_fix | 03 + 08 | test_statement_refresh.py | swap-simulation meta-test is blind to the class-(c) replay pins; a `diff_replay_truths` harness would close it — doc now names it as an unbuilt follow-up but there is no story ID | CARRIED — producer to decide whether to file now |
| should_fix | 06-integration § risks | widening (b) | de-dilution tripwire margin thin (2.32% vs new rel=0.03) — next drift needs a 2nd-order term, not a 3rd widening | CARRIED — human / next refresh |
| should_fix | 06-integration § risks | frozen golden Euro series | DEFS.L/SXRV.DE/SEMI.L end 08-27, 1d before the 08-28 marks — source of widening (a); next refresh re-capture the Euro series, not the tolerance | CARRIED — human / next refresh |
| disclosure | 05-quant-audit § risks | replay pins | replay-derived pins were consistency/plausibility-checked, NOT recomputed day-by-day (frozen replay engine not run); statement_truths.py pins WERE independently CSV-recomputed | CARRIED — stated in close-out per skill Step 7 |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| decision | human | 03→04 | pin the Aug-28 export; fix = documented statement-refresh workflow |
| blocker | human | — | FMP_API_KEY moot — human already ran refresh_statement.py; only the manual pin step remained (no network) |
| placement | 01 | — | NO story; routine Epic 28/US-28.3 maintenance; gates still applied |
| watch | 01 | 02 | scope watch (new-holding FMP coverage / wrong-fund collision) — none; only SBIO gains a BUY, already wired; no registry edit |
| finding | 02 § "41 failing tests"(c) | 03 + 04 + 04b | ~23+ inline replay pins across test_ledger_replay_audit.py + test_portfolio_state.py + test_analytics.py — stay inline, regenerated from observed values with history comments |
| finding | 02 § Docstring drift | 08 | testing-architecture.md "structural tests never fail on refresh" contradicted — amended (option ii): step-3b names the replay-audit pin class + closing paragraph narrowed |
| finding | 02 § Regeneration recipes | 04 | 4 scout hand-derivations (BUY 92→93, raw sum, base weights, HHI) — test lane regenerated from the snippet; observed: BUY 93, raw 62843.22, HHI 0.135814 |
| note | 03 § Engine-dependent pins | 04 | IB_INSTRUMENT_COUNT / IB_TOP_OVERWEIGHTS / IB_ABSENT_SYMBOLS — none moved, no escalation |
| replan | 04 § risks | 04b | SCOPE GAP: test_analytics.py held a 9-test/16-assertion class-(c) cluster 02+03 missed — 14 pins refreshed, no tolerance widened, suite green |
| finding | 04b § risks | 05 | twr["3M"] sign flip + twr["All"] rise + mwr + investment_gain — all explained by the +13-day window / re-mark / SBIO buy / TWR 4.77→5.51%; cross-file consistent |
| finding | 04 § changed | 05 + 06 | 2 tolerance widenings in test_ledger_replay_audit.py — both ACCEPTABLE (05), the only loosened tolerances in the diff (06) |
| finding | 04 § risks | 06 | test_portfolio_state.py l.918/936 plan line-drift — 04's call confirmed correct (real ib2026_snapshot pin, synthetic blocks untouched) |
| finding | orchestrator | 06 | unstaged golden_market_data.json 48-line delta — float32 round-trip noise (24 ACOMO.AS adjClose, ~8th sig digit); human discards before commit |
| finding | 04 § risks | 05 | mwr 2.76→3.49, investment_gain 1645.99→2091.78 — plausible vs statement delta |
| finding | 02 | — | dashboardGoldens.ts + golden_market_data.json (staged) confirmed Aug-28-consistent — user's refresh_statement.py run took; no golden work needed |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 9 |
| rounds | 0 |
| by model | sonnet 8 · opus 1 |
| escalations | none (03 rate-limit retry was a re-dispatch of the same model, not an escalation) |
