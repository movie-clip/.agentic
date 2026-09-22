# RUN 2026-09-17-fix-mm-cot-long-short-index
request:      Fix the bugs and ship the improvements the prior audit found in tradingview/mm_cot_long_short_index.pine. The audit is already done — read it before doing anything else, do not re-derive it: C:\projects\investments\.agentic\projects\tradingview\runs\2026-09-16-audit-mm-cot-long-short-index\02-quant-audit.md (and 01-recon.md). Fix all 8 findings. FINDING 3 is decided (D-1, decisions.md): rescale on NET (long − short) position to 0..100 per Briese/Williams, dropping the two independent gross-side indices; keep gross long/short as raw table rows only. This also resolves FINDING 2 (the inverted short-plot guide label goes away with the redesign) and FINDING 4 (use the conventional 80/20 guide lines on the new 0..100 net scale). FINDING 1: fix lookbackWeeks to mean weeks on every chart timeframe, not chart bars. FINDING 5: cite Briese (2008)/Williams (2005) once the net-index change makes the "standard COT Index" claim true. FINDING 6: the header's Gold symbol reconstruction should move from the _OLD suffix to _ALL (Gold has no crop-year breakout) — still flagged unverified until confirmed in TradingView's own symbol search. FINDING 7: add explicit lookahead=barmerge.lookahead_off to both request.security() calls. FINDING 8: add an as-of/staleness indication so a frozen feed cannot look live. This is mathematics-touching work on guardrail-heavy financial code: quant (RESEARCH) fires before backend types anything, and quant-audit (AUDIT) independently re-derives the fixed values afterward. The compile check in TradingView is mandatory before this closes.
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       CLOSED
phase:        close
plan:         v5
budget:       14 — 13 prior dispatches + 1 final close/docs pass citing compile.md
spent:        14
next:         none — CLOSED
gates:        quant-audit PASS (round 2) · integration PASS (round 2, post symbol fix) · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script, or rests on an unverified claim | not triggered (prior artifacts already cover the area, cited by path: 01-recon.md and 02-quant-audit.md in run 2026-09-16-audit-mm-cot-long-short-index) |
| framing | product | the request is a new script, or changes what an existing script is for | not triggered (defect fix in shipped behaviour; not a new script, purpose unchanged) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula, a normalisation or a threshold | satisfied — 01 |
| specification (story) | story | framing produced scope no approved story covers, and the slice spans >1 script or a published signature | not triggered (framing did not fire; single-script slice; the audit + quant research brief are the specification; no evidence this script is published to the TradingView community) |
| design | design | more than one script changes together, or a published input/plot/alert signature changes | not triggered (single script; no evidence of publication; no cross-script contract) |
| build | backend, test, docs | anything edits the .pine file, a fixture or the header | satisfied — 02,03,04 |
| verify — quant-audit | quant-audit | any lane touched a formula/threshold/normalisation | satisfied — 08 (PASS, round 2) |
| verify — integration | integration | any build lane was dispatched | satisfied — 09 (PASS) |
| verify — review | review | the run carries a story whose criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 10 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | quant | RESEARCH | quantitative-researcher | opus | 01-quant.md | DONE | NONE |
| 02 | backend | — | backend-engineer | sonnet | 02-backend.md | DONE | — |
| 03 | test | — | test-engineer | sonnet | 03-test.md | DONE | — |
| 04 | docs | — | docs-engineer | sonnet | 04-docs.md | DONE | — |
| 05 | quant-audit | AUDIT | quantitative-researcher | opus | 05-quant-audit.md | DONE | FAIL |
| 06 | backend | — | backend-engineer | sonnet | 06-backend.md | DONE | — |
| 07 | docs | — | docs-engineer | sonnet | 07-docs.md | DONE | — |
| 08 | quant-audit | AUDIT | quantitative-researcher | opus | 08-quant-audit.md | DONE | PASS |
| 09 | integration | INTEGRATION | tech-lead | sonnet | 09-integration.md | DONE | PASS |
| 10 | docs | — | docs-engineer | sonnet | 10-docs.md | DONE | — |
| 11 | backend | — | backend-engineer | sonnet | 11-backend.md | DONE | — |
| 12 | docs | — | docs-engineer | sonnet | 12-docs.md | DONE | — |
| 13 | integration | INTEGRATION | tech-lead | sonnet | 13-integration.md | DONE | PASS |
| 14 | docs | — | docs-engineer | sonnet | 14-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | 08-quant-audit | 08-quant-audit.md § FINDING 8 | MINOR: 6D/7D charts slip under the >W threshold and silently skip weekly reports (72.65/76.84 vs true 61.42) | CARRIED |
| should_fix | 09-integration | 09-integration.md § Repo-wide static check | pre-existing pine_check --strict debt in strategy13_trend_carry.pine (missing slippage, guardrail 4) and systemic_stress_dashboard.pine (missing lookahead x4) — neither touched by this run; recommend a separate follow-up run | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| bug | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 02-backend (net-index redesign per D-1 dissolves the dual-plot label; re-verified independently by 05-quant-audit) | CRITICAL: -80 guide line inverted for short plot (resolved by the net-index redesign, D-1) |
| bug | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 02-backend (net-index redesign per D-1; re-verified independently by 05-quant-audit) | MATERIAL: gross-side index vs. cited net methodology — decided, see D-1 |
| bug | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 02-backend (conventional 80/20 guide lines on the new 0..100 net scale; re-verified by 05-quant-audit) | MATERIAL: guide lines are 90/10 not 80/20 (resolved by the net-index redesign, D-1) |
| should_fix | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 04-docs (Briese 2008/Williams 2005 cited in header; re-verified by 05-quant-audit) | MATERIAL: header cites no source; Briese (2008)/Williams (2005) are citable |
| should_fix | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 02-backend (explicit lookahead=barmerge.lookahead_off added; re-verified by 05-quant-audit) | MATERIAL: missing explicit lookahead=barmerge.lookahead_off |
| bug | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 02-backend (as-of date + staleAfterDays flag added; re-verified by 05-quant-audit) | MATERIAL: no as-of date/staleness test |
| should_fix | ../2026-09-16-audit-mm-cot-long-short-index/03-docs.md | 04-docs (docs/mm-cot-long-short-index.md rewritten to reflect the redesign) | docs/mm-cot-long-short-index.md goes stale the moment any finding is fixed — must be updated as part of this run's close |
| bug | 05-quant-audit | 06-backend (CR-1 remedy a: tfTooCoarse gate on both eval paths; re-verified by 08-quant-audit) | CRITICAL, now MATERIAL: fixed for chart TF <= W; above W the array collects one obs per chart bar not per report. Tracked by cr/CR-1.md |
| should_fix | 05-quant-audit | 07-docs (line citations re-taken against current file) | MINOR: docs' line-number citations are 26-34 lines short of current file |
| should_fix | 05-quant-audit | 07-docs (summary count corrected and made internally consistent) | MINOR: docs' summary line says 'two remain open' inconsistently with its own table |
| should_fix | 05-quant-audit | 06-backend (unconditional text_color removed) | MINOR: table row 3 sets unconditional white text, unreadable on light theme for most readings |
| should_fix | 05-quant-audit | 06-backend (minval=2 added to lookbackWeeks) | MINOR: lookbackWeeks has no minval; 0 or 1 breaks the window silently |
| should_fix | 05-quant-audit | 07-docs (provisional-current-week disclosure added to header) | MINOR: live/provisional-bar disclosure dropped from header despite being in spec |
| should_fix | 05-quant-audit | 07-docs (tooltip clarifies age basis shifts with chart timeframe) | MINOR: staleness tooltip's day-count basis shifts with chart timeframe, undisclosed |
| bug | ../2026-09-16-audit-mm-cot-long-short-index/02-quant-audit.md | 11-backend + orchestrator's live TradingView symbol-search verification (bare 088691_F_MMP_L / 088691_F_MMP_S confirmed to resolve; guardrail 3 now genuinely satisfied, not merely reasoned) | MATERIAL: _OLD ticker suffix does not apply to Gold. Fixed to _ALL (reasoned, not confirmed) — symbol confirmation itself stays open by design, no lane holds a browser tool |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| CR-1 | backend | 1 | 2 | — |

## Replans
| plan | because | change |
|---|---|---|
| v2 | CR-1's fix round touched both code and header/docs (06-backend, 07-docs), needing 3 dispatches (fix, fix, re-audit) to close instead of the 2 originally budgeted for one change-request round | budget 9 -> 10 |
| v3 | the mandatory TradingView compile check (main session) found the symbol guess itself was wrong beyond FINDING 6's known gap: neither `COT2:` nor `COT:` is a valid exchange prefix for these tickers — TradingView resolves them bare, with no exchange prefix. Verified directly in the Pine editor and via TradingView's own symbol search before writing this row. | budget 10 -> 12 |
| v4 | the symbol correction needed a second backend round (order text was stale, then the `_ALL` suffix also had to go) plus a docs round, leaving no budget for the integration re-check both edits still owe | budget 12 -> 13 |
| v5 | the run's own `close` phase already satisfied (10-docs) needs one more docs pass now that compile.md exists, to reconcile the doc's "compile check outstanding" language against the actual PASS result | budget 13 -> 14 |
