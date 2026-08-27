# RUN 2026-08-26-performance-benchmark-chart-audit
request:      check wether Performance & Benchmark chart, data, filtering,
              anything related to this chart is working correctly, UI also
              should be correct and show valid vlues, all numbers that are
              shown in UI must be valid and correct
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
route:        review
express:      no
gates:        quant-audit PASS · integration PASS · review skipped (no story to accept — this run fixed defects in already-shipped US-25.1/US-27.8 functionality, not new scope)

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | haiku | 01-scout.md | DONE | — |
| 02 | quant | AUDIT | quant-analyst | opus | 02-quant-audit.md | DONE | FAIL |
| 03 | frontend | — | frontend-engineer | sonnet | 03-frontend.md | PARTIAL | — |
| 04 | test | — | test-engineer | sonnet | 04-test.md | DONE | — |
| 05 | quant | AUDIT | quant-analyst | opus | 05-quant-reaudit.md | DONE | PASS |
| 06 | integration | INTEGRATION | tech-lead | sonnet | 06-integration.md | DONE | CHANGES_REQUESTED |
| 07 | backend | — | backend-engineer | sonnet | 07-backend.md | PARTIAL | — |
| 08 | frontend | — | frontend-engineer | sonnet | 08-frontend.md | DONE | — |
| 09 | test | — | test-engineer | sonnet | 09-test.md | DONE | — |
| 10 | quant | AUDIT | quant-analyst | opus | 10-quant-audit.md | DONE | PASS |
| 11 | integration | INTEGRATION | tech-lead | sonnet | 11-integration.md | DONE | PASS |
| 12 | test | — | test-engineer | sonnet | 12-test.md | DONE | — |
| 13 | docs | — | docs-engineer | sonnet | 13-docs.md | DONE | — |
| 14 | docs | — | docs-engineer | sonnet | 14-docs-packcorrection.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| protocol_note | 01-scout | 01-head.txt | shell-less lane self-typed head disagreed with derived head on 3 counts (changed/contract_notes/pack_corrections all 1→0, handoff 14→15) — orchestrator derived via --emit-head per updated protocol, used that | ABSORBED |
| finding | 01-scout | § risks | chart-line vs methodology discrepancy: contract doc claims chart's base-100 line follows TWR-indexed §Indexed Return Series, but PerformanceBenchmarkCard.tsx::buildIndexedSeries actually indexes raw portfolio_value (total market value incl. cash flows) client-side — methodology explicitly warns raw market value is NOT a valid line (deposit/withdrawal would fake a move) | ABSORBED (confirmed real CRITICAL by 02-quant-audit, fixed by 03-frontend, re-audit PASS via 05-quant-reaudit) |
| finding | 01-scout | § risks | DashboardPanel.tsx::normalizePerformanceSeries implements the identical (raw-value) rebasing math as buildIndexedSeries but is dead in the render tree (only consumer is its own test) — duplicate implementation, drift risk regardless of which is correct | ABSORBED (deleted by 03-frontend, confirmed gone by 05-quant-reaudit) |
| finding | 01-scout | § risks | no methodology section found describing the Dashboard chart's own client-side indexing formula specifically (only the range-metrics scalar formulas are documented) — either covered by §Indexed Return Series with implementation drift, or a genuine doc gap; scout could not determine which | ABSORBED (resolved: doc's formula citation was already correct per 02-quant-audit; the Implementation-list pointer gap is CR-2 #2, carried to tech-debt-register) |
| finding | 01-scout | § risks | non-imported /api/engines/dashboard-history/run route always returns unavailable regardless of input (both branches call _build_unavailable_dashboard_history_result) — observation only, not judged | ABSORBED (judged intentional/correct fail-closed stub by 06-integration as CR-2 #3, carried to tech-debt-register, no behavior change needed) |
| finding | 01-scout | § handoff | no benchmark-symbol selector exists on this chart/tab — symbol is hardcoded 'SPY' at import time; only filter is the range selector (1M/3M/YTD/1Y/All) shared with MonthlyReturnsGrid | ABSORBED |
| finding | 02-quant-audit | § FINDING 1 (CRITICAL) | chart's portfolio line indexes raw portfolio_value instead of the TWR-indexed chain the doc mandates — confirmed by porting to Python: fabricates +50pp on a synthetic pure-deposit case (true 0%), overstates the repo's own test fixture by 21.97pp (shows +24.40% vs true +2.43%, ~10x). Fix: swap to already-served portfolio_return_pct field, frontend-only, no backend change | ABSORBED (fixed by 03-frontend, re-audit PASS via 05-quant-reaudit) |
| finding | 02-quant-audit | § FINDING 2 (MINOR) | DashboardPanel.tsx::normalizePerformanceSeries is a dead bit-for-bit duplicate of the same wrong formula — no live risk today, but a drift trap if Finding 1 is fixed without resolving this copy too | ABSORBED (fixed by 03-frontend, re-audit PASS via 05-quant-reaudit) |
| finding | 02-quant-audit | § Independently verified correct | all 6 range_metrics summary scalars (TWR, MWR/Modified Dietz, Net Contributions, Portfolio Value, {Symbol} Return, Excess Return) independently recomputed and matched exactly — no finding | ABSORBED |
| finding | 02-quant-audit | § risks | contract doc (dashboard-fields.md:219) is NOT wrong — it correctly cites §Indexed Return Series; the code is wrong. Do not "fix" the doc when Finding 1 lands | ABSORBED (confirmed still true post-fix by 06-integration; doc updated to describe the now-correct code by 13-docs) |
| human_decision | user | this turn | fix now: both Finding 1 (CRITICAL, chart line) and Finding 2 (MINOR, dead duplicate) in the same pass | ABSORBED |
| finding | 03-frontend | § changed | chart's portfolio leg now indexes portfolio_return_pct (100*(1+pct/100)), benchmark leg untouched (correct as-is per audit); dead normalizePerformanceSeries deleted — both per spec | ABSORBED |
| finding | 03-frontend | § handoff | PerformanceBenchmarkCard.test.tsx never exercised buildIndexedSeries's output at all (zero dataKey/indexed assertions) — why Finding 1 shipped unnoticed; needs new coverage for the TWR-indexed line | ABSORBED (added by 04-test) |
| finding | 03-frontend | § handoff | DashboardPanel.test.tsx:6 + lines 171-184 reference the now-deleted normalizePerformanceSeries — both need removal (import + its one test) | ABSORBED (removed by 04-test) |
| finding | 03-frontend | § risks | anchor-rule subtlety: engine's portfolio_return_pct is always 0.0 on the very first daily_state (previous_state is None branch), regardless of whether that state's portfolio_value>0 — different first-point semantics than the old frontend's own assumption; fix consumes the field as-is per FINDING 1's spec, flagged for re-audit to confirm no new edge-case issue | ABSORBED (judged correct, not a fabrication, by 05-quant-reaudit) |
| protocol_note | 03-frontend | 03-head.txt | PARTIAL/verification FAIL correctly reported (not dishonestly claimed DONE) — failure is the anticipated cross-lane split (dead test still referencing deleted function), not a regression in the fix itself | ABSORBED |
| finding | 04-test | § changed | orphaned dead-code test removed; 3 new regression tests added (deposit-vs-raw-value guard, unaffected benchmark leg, first-point-anchor guard) via a local recharts mock exposing exact chart-line values — full command green (tsc clean, 46/46 tests pass) | ABSORBED |
| pack_correction | 04-test | § risks | write-tests/SKILL.md's Recharts section only documents textual smoke checks, no guidance for exact-value chart assertions when the builder fn is unexported — written to pack-corrections.md, missed by 13-docs close-out (dashboard-fields.md/tech-debt-register.md scope only), routed via dedicated 14-docs dispatch to the actual capabilities/testing.md pack | ABSORBED (applied to capabilities/testing.md "Gotchas" section, confirmed by direct read) |
| finding | 04-test | § risks | confirmed via git diff --stat that source files (PerformanceBenchmarkCard.tsx, DashboardPanel.tsx) carry only dispatch 03's changes — this test dispatch touched test files only | ABSORBED |
| finding | 05-quant-reaudit | § Independent recomputation | FINDING 1 re-derived fixed: synthetic case now renders [100,100,100,100] not fabricated 150; realistic case 102.43 not 124.40; benchmark leg confirmed byte-for-byte unchanged via git diff. FINDING 2 confirmed closed: zero live references, 21-line function cleanly removed | ABSORBED |
| finding | 05-quant-reaudit | § Judgment: first-point anchor | not a fabrication, not a new defect: day-0's forced 0.0% is the TWR index's honest base case, gaps stay None (not interpolated), pre-existing engine behavior unmodified by this CR, same field already covered by round-1's passed summary-scalar audit | ABSORBED |
| finding | 05-quant-reaudit | § Duplicate-formula hunt | third indexed-series builder found (IndexedReturnChart.tsx, Exposure tab drift panel) — confirmed NOT a copy of the bug, uses a genuinely correct compound cash-flow-neutral TWR chain from drift_engine.py, different card/module, no finding | ABSORBED |
| finding | 06-integration | CR-2 #1 (BLOCKING) | chart ignores the range selector entirely — always shows full imported history regardless of 1M/3M/YTD/1Y selection, while the summary strip directly above genuinely re-scopes; pre-existing since US-25.1 shipped, AC7 checked "[x]" but only half-implemented, zero test coverage of the gap | ABSORBED (fixed by 07/08/09, quant PASS via 10, integration PASS via 11) |
| finding | 06-integration | CR-2 #2 (SHOULD_FIX) | financial-methodology.md §Indexed Return Series' Implementation list names only drift_engine.py, omits performance.py::build_true_performance_series + PerformanceBenchmarkCard.tsx — wrong-pointer trap, formula text itself remains correct | CARRIED (tech-debt-register at close-out, not fixed this pass) |
| finding | 06-integration | CR-2 #3 (SHOULD_FIX) | non-imported /run route's always-unavailable behavior judged intentional/correct (fail-closed, no ledger to compute TWR from) but undocumented at the point of implementation — comment only, no behavior change | CARRIED (tech-debt-register at close-out, not fixed this pass) |
| human_decision | user | this turn | fix CR-2 #1 (BLOCKING, chart ignores range filter) now; route CR-2 #2 and #3 to tech-debt-register instead of fixing | ABSORBED |
| finding | 06-integration | § Trust label and contract doc | both confirmed accurate post-CR-1-fix: trust label now correctly describes what the chart actually draws; contract doc's citation was already correct (code was wrong, doc wasn't) — no finding on either | ABSORBED |
| contract_note | 06-integration | § contract_notes | DashboardRangeMetrics needs a window-start anchor field for CR-2 #1's fix — backend schema addition, will need types.ts + dashboard-fields.md updates per the schema hook | ABSORBED (field added by 07-backend) |
| finding | 13-docs | § changed | dashboard-fields.md updated: Indexed chart row notes both this-run fixes, new window_start_date entry added; tech-debt-register gained new "Deferred findings" section with 4 entries (CR-2 #2, CR-2 #3, YTD-convention MINOR, typing-strictness+fixture-footgun); current-product-state.md got a one-paragraph note | ABSORBED |
| finding | 13-docs | § risks | current-product-state.md's top banner (dated 2026-08-19, names Epic 34) left untouched — new content is dated 2026-08-26 but this run isn't an epic, bumping felt like overstating it; flagged not silently decided | CARRIED |
| finding | 07-backend | § changed | window_start_date: str \| None added to DashboardRangeMetrics, populated from _slice_performance_series's existing slice (no new computation) — wired into both populated and empty-series branches | ABSORBED |
| contract_note | 07-backend | apps/desktop/src/features/portfolio/types.ts:519 | DashboardRangeMetrics needs mirrored window_start_date: string \| null field | ABSORBED (added by 08-frontend, typed optional not strict — see risks row below) |
| contract_note | 07-backend | docs/contracts/dashboard-fields.md:~322 | new entry needed for range_metrics[*].window_start_date, near portfolio_return_trust | OPEN (still outstanding, docs close-out) |
| finding | 11-integration | § Range-filter re-check | CR-2 #1 confirmed genuinely resolved — re-read current PerformanceBenchmarkCard.tsx directly, range selector now actually changes the chart; PASS, no new BLOCKING | ABSORBED |
| finding | 11-integration | § Typing judgment | optional window_start_date?: string\|null judged SHOULD_FIX not BLOCKING — no runtime defect (?? null normalizes), matches sibling field's existing convention, and is the safe-direction mismatch (frontend-lenient vs backend-strict) | CARRIED |
| finding | 11-integration | § Fixture coverage footgun | shared createImportedDashboardFixture has NO window_start_date in any range — currently fine (both real tests override it inline) but a latent regression-mask: a future test using the fixture unmodified would silently exercise the exact bug CR-2 #1 fixed and pass | ABSORBED (fixed by 12-test, 5 distinct real per-range values, full 40-file/359-test suite green) |
| human_decision | user | this turn | fix the fixture footgun now (give createImportedDashboardFixture real per-range window_start_date values) | ABSORBED |
| finding | 11-integration | § handoff | document 10-quant-audit's Finding 1 (YTD vs sliding-window anchor convention) near window_start_date's docstring or in financial-methodology.md | CARRIED |
| finding | 08-frontend | § changed | buildIndexedSeries now filters performance_series to >= window_start_date and re-bases portfolio leg to 100 at window start; benchmark leg gets same date filter, rebasing formula unchanged | ABSORBED |
| finding | 08-frontend | § handoff | manual trace confirmed window_start_date is non-null whenever range != "All" and slice non-empty — fix is not a no-op for real multi-range data, BLOCKED escape hatch not triggered | ABSORBED |
| finding | 08-frontend | § risks | typed window_start_date as optional (?:) not strict string\|null (matches sibling portfolio_return_trust's convention) to avoid touching goldens/fixtures out of scope — flagged for tech-lead to weigh strict vs optional | CARRIED (judged SHOULD_FIX not BLOCKING by 11-integration — safe direction, no runtime defect; routed to tech-debt-register) |
| finding | 08-frontend | § risks | re-basing pivot (pctAtWindowStart) trusted by construction from backend's own comment that window_start_date IS perf[0].date of the identical slice — not independently re-derived; worth quant confirming this invariant holds | ABSORBED (proved structurally + numerically across all ranges + edge cases by 10-quant-audit) |
| protocol_note | 09-test (attempt 1) | task a716638c3d12d8009 | infra session-limit failure mid-flight, no artifact written, no file edits made (confirmed via git diff — working tree reflected only 03/04/07/08's already-landed work) — clean re-dispatch, not a resume | ABSORBED |
| finding | 07-backend | § verification | dashboardGoldens.ts stale, blocks full suite at setup (session-scoped fixture) — confirmed golden-staleness only via SKIP_GOLDEN_FRESHNESS_CHECK=1 diagnostic rerun (22/22 pass on actual assertions), not a logic regression; regenerate via python -m app.scripts.export_dashboard_goldens | ABSORBED (regenerated by 09-test, 22/22 pass clean) |
| finding | 09-test | § changed, § handoff | golden regen confirmed clean (20 ins/10 del, all window_start_date additions, no unexplained numeric drift); 2 new multi-range chart tests added (PerformanceBenchmarkCard) + 1 new DashboardPanel range-switch assertion checking actual chart data change, not just aria-pressed; 49/49 frontend + 22/22 backend green | ABSORBED |
| finding | 10-quant-audit | § Log/1-3 | re-basing algebra independently re-derived correct (rounding-only gap, pre-existing, unrelated to CR-2); window_start_date invariant proved structurally + numerically across all ranges + single-day/empty edge cases; YTD confirmed real non-null distinct-from-All | ABSORBED |
| finding | 10-quant-audit | § Log/4 FINDING 1 (MINOR) | YTD's anchor-inside-window vs sliding-windows' anchor-outside-window convention undocumented — not a wrong number, chart and summary strip already use the identical (existing) convention per range; doc-completeness gap only | CARRIED (tech-debt-register at close-out, matches user's established preference this run) |
| finding | 10-quant-audit | § Log/5 | pre-existing edge case (window > available history silently returns full series, matches quant.md's documented policy discussion) — untouched by CR-2, not a finding against this fix, recorded for awareness only | ABSORBED |
| finding | 07-backend | § risks | YTD judgment call: RANGE_WINDOWS shows window=None for both "All" and "YTD", but YTD is year-filtered by its own branch so gets a real (non-null) window_start_date while only "All" gets null — reasoned correctly but not explicit in the CR, flagged for downstream confirmation | ABSORBED (confirmed correct by 10-quant-audit § Log/3, numerically verified) |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| 02-quant-audit Finding 1 (chart line fabricates performance) | frontend-engineer | 1 (closed: PASS via 05-quant-reaudit) | 2 |
| 02-quant-audit Finding 2 (dead duplicate formula) | frontend-engineer | 1 (closed: PASS via 05-quant-reaudit) | 2 |
| CR-2 #1 (chart ignores range selector, BLOCKING) | backend-engineer | 1 (closed: PASS via 10-quant-audit) | 2 |

## Cost
| metric | value |
|---|---|
| dispatches | 14 |
| rounds | 3 |
| by model | sonnet 10 · opus 3 · haiku 1 |
| escalations | none |
