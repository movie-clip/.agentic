# RUN 2026-09-14-audit-systemic-stress-dashboard
request:      research pine languange, or how it is called in TradingView, find how you can test your scripts localy, to have deterministic tests. after review systemic_stress_dashboard.pine, analyze it, try to spot any bugs or missimplementation
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       CLOSED
phase:        close
plan:         v2
budget:       4 — ground-truth (recon, 1) + verify/quant-audit (2, one LOST to rate limit) + close/docs (1)
spent:        4
next:         none — CLOSED
gates:        quant-audit FAIL · integration skipped (no build lane dispatched) · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script (systemic_stress_dashboard.pine) | satisfied — 01 |
| framing | product | the request is a new script, or changes what an existing script is for | not triggered (pure analysis/audit request, no new script and no change to purpose) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula | not triggered (no new formula being introduced; auditing an existing one) |
| specification (story) | story | framing produced scope no approved story covers, spanning >1 script or a published signature | not triggered (framing did not fire; nothing being built) |
| design | design | more than one script changes together, or a published signature changes | not triggered (nothing changes) |
| build | backend/test/docs | anything edits a .pine file, fixture or header | not triggered (read-only investigation; no repo edits planned) |
| verify — quant-audit | quant-audit | any lane touched a formula/threshold/sizing/normalisation/symbol mapping | satisfied — 03 |
| verify — integration | integration | any build lane was dispatched | not triggered (no build lane dispatched) |
| verify — review | review | the run carries a story whose criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 04 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | quant-audit | AUDIT | quantitative-researcher | opus | 02-quant-audit.INTERRUPTED.md.txt (renamed out of the numbered-slot pattern — cut off mid-write by the session rate limit; superseded by 03) | LOST | — |
| 03 | quant-audit | AUDIT | quantitative-researcher | opus | 03-quant-audit.md | DONE | FAIL |
| 04 | docs | — | docs-engineer | sonnet | 04-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| risk | 01-recon | 01-recon.md § Repo listing notes | CLAUDE.md documents fixtures/ and docs/ dirs but neither exists in repo | CARRIED |
| bug | 03-quant-audit | 03-quant-audit.md § FINDING 1 | CRITICAL: ta.percentrank on a zero-variance/stale series publishes 100 not n/a, breaches guardrail 5 | CARRIED |
| bug | 03-quant-audit | 03-quant-audit.md § FINDING 2 | CRITICAL: stressImpulse conflates a component appearing/dropping out with real stress movement (-24 on no movement) | CARRIED |
| bug | 03-quant-audit | 03-quant-audit.md § FINDING 3 | MATERIAL: renormalisation silently switches basis at the 272-bar credit warm-up boundary, 14pt jump | CARRIED |
| bug | 03-quant-audit | 03-quant-audit.md § FINDING 4 | MATERIAL: header's blank-cell diagnostic is false during warm-up and one-bar data gaps | CARRIED |
| bug | 03-quant-audit | 03-quant-audit.md § FINDING 5 | MATERIAL: last bar repaints intrabar, undisclosed in header | CARRIED |
| should_fix | 03-quant-audit | 03-quant-audit.md § FINDING 6-8 | MINOR x3: missing lookahead arg, unvalidated weights/thresholds, symbols not confirmed via TV search | CARRIED |
| should_fix | 04-docs | 04-docs.md § handoff | missing docs/<slug>.md and fixtures/ dirs are a pre-existing, repo-wide gap — human to decide whether to open as its own order | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| risk | 01-recon | 03-quant-audit (FINDING 8, same fact, independently confirmed and superseded) | header never states whether the 4 symbols (VIX/COR1M/LQD/HYG) were confirmed via TV symbol search per guardrail 3 |
| should_fix | 01-recon | 03-quant-audit (FINDING 6, same fact, independently confirmed and superseded) | pine_check.py P008 likely flags all 4 request.security() calls for missing explicit lookahead arg (SHOULD_FIX, not blocking; integration gate not dispatched this run) |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
| v2 | dispatch 02 (quant-audit) was LOST to a session-wide rate limit and had to be re-dispatched as 03, consuming an extra budget slot the original derivation did not account for | budget 3 → 4 |
