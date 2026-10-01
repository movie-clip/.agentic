# RUN 2026-09-15-fix-systemic-stress-dashboard
request:      Fix the bugs the prior audit found in tradingview/systemic_stress_dashboard.pine. The audit is already done — read it before doing anything else, do not re-derive it: C:\projects\investments\.agentic\projects\tradingview\runs\2026-09-14-audit-systemic-stress-dashboard\03-quant-audit.md. Fix, in this priority order: 1. FINDING 1 (CRITICAL) — ta.percentrank has no dispersion guard, so a flat/frozen/near-constant input series publishes a confident 100 (or 0) instead of n/a. Needs a variance/range floor on the lookback window that forces the result to na below it. 2. FINDING 2 (CRITICAL) — stressImpulse differences systemicStress across bars that may have been renormalized over a different set of non-na components, so a component appearing or dropping out reads as a real stress move. Needs the impulse to be na whenever the composite's basis differs between the two bars being compared (or reweight component-level differences instead of differencing the composite). 3. FINDING 3 (MATERIAL) — the same basis-switch defect as FINDING 2, triggered by warm-up length instead of a data gap (credit needs 272 bars, VIX/COR1M need 252, so bar 272 jumps ~14 points with nothing moving). Whatever fix resolves FINDING 2 should resolve this too — verify it does explicitly, don't assume. 4. FINDING 4 and FINDING 5 (MATERIAL, header-disclosure gaps, not logic bugs) — add the two missing admissions to the script header: (a) a blank component cell can mean warm-up or a one-bar data gap, not only "the symbol didn't resolve" — the current header text is misleading; (b) the last bar's reading is provisional and can change intrabar before the close (harmless, but currently undisclosed). 5. FINDING 6, 7, 8 (MINOR) if time/scope allows: add explicit lookahead=barmerge.lookahead_off to the four request.security() calls (currently relies on the implicit default — pine_check.py's P008 flags this); add minval/ordering validation on the weight and threshold inputs; state in the header whether the four symbols (TVC:VIX, CBOE:COR1M, AMEX:LQD, AMEX:HYG) were confirmed against TradingView's own symbol search, per guardrail 3. This is mathematics-touching work on guardrail-heavy financial code, so expect quant (RESEARCH) to fire before backend types anything, and quant-audit (AUDIT) to independently re-derive the fixed values afterward — not just re-read the diff. The compile check in TradingView is mandatory before this closes; nothing here has been run in the actual Pine editor yet. Preserve the header's existing honest admissions (the "ORIGINAL approximation" framing, the untuned-weights caveat) — add to them, don't soften them.
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       DISPATCHING
phase:        specification
plan:         v1
budget:       9 — 7 triggered-phase dispatches (specification/quant 1, build backend+docs+test 3, verify quant-audit+integration 2, close/docs 1) + 2 for one anticipated change-request round on the math gate (a fix dispatch plus the gate re-run)
spent:        1
next:         dispatch 02 backend on 01-quant.md §§ FINDING 1 fix / FINDING 2 and 3 fix plus decisions.md § D-1 (Basis row adopted, table.new 2,6 -> 2,7)
gates:        quant-audit pending · integration pending · review skipped (no story to accept)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script, or rests on an unverified claim | not triggered (prior artifacts already cover the area, cited by path: 01-recon.md and 03-quant-audit.md in run 2026-09-14-audit-systemic-stress-dashboard) |
| framing | product | the request is a new script, or changes what an existing script is for | not triggered (defect fix in shipped behaviour; not a new script, purpose unchanged) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula, a normalisation or a threshold | satisfied — 01 |
| specification (story) | story | framing produced scope no approved story covers, and the slice spans >1 script or a published signature | not triggered (framing did not fire; single-script slice; the audit + quant research brief are the specification) |
| design | design | more than one script changes together, or a published input/plot/alert signature changes | not triggered (single script; repo is for the author's own use, nothing here is published to the TradingView community; no signature change, only added guards/validation) |
| build | backend, docs, test | anything edits the .pine file, a fixture or the header | pending |
| verify — quant-audit | quant-audit | any lane touched a formula/threshold/normalisation | pending |
| verify — integration | integration | any build lane was dispatched | pending |
| verify — review | review | the run carries a story whose criteria someone must accept | not triggered (no story) |
| close | docs | always | pending |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | quant | RESEARCH | quantitative-researcher | opus | 01-quant.md | DONE | NONE |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| bug | ../2026-09-14-audit-systemic-stress-dashboard/03-quant-audit.md | § FINDING 1 | CRITICAL: ta.percentrank on zero-variance/stale series publishes 100 not n/a | OPEN |
| bug | ../2026-09-14-audit-systemic-stress-dashboard/03-quant-audit.md | § FINDING 2 | CRITICAL: stressImpulse conflates component appear/drop-out with real stress move | OPEN |
| bug | ../2026-09-14-audit-systemic-stress-dashboard/03-quant-audit.md | § FINDING 3 | MATERIAL: same basis-switch defect at 272-bar credit warm-up boundary | OPEN |
| bug | ../2026-09-14-audit-systemic-stress-dashboard/03-quant-audit.md | § FINDING 4 | MATERIAL: header blank-cell diagnostic is misleading (warm-up/gap vs unresolved) | OPEN |
| bug | ../2026-09-14-audit-systemic-stress-dashboard/03-quant-audit.md | § FINDING 5 | MATERIAL: last-bar intrabar repaint undisclosed in header | OPEN |
| should_fix | ../2026-09-14-audit-systemic-stress-dashboard/03-quant-audit.md | § FINDING 6-8 | MINOR x3: missing lookahead arg, unvalidated weights/thresholds, symbols not confirmed via TV search | OPEN |
| should_fix | ../2026-09-14-audit-systemic-stress-dashboard/04-docs.md | § handoff | missing docs/<slug>.md and fixtures/ dirs are a pre-existing, repo-wide gap — human to decide whether to open as its own order | CARRIED |
| risk | ../2026-09-14-audit-systemic-stress-dashboard/01-recon.md | § Repo listing notes | CLAUDE.md documents fixtures/ and docs/ dirs but neither exists in repo | CARRIED |
| contract_note | 01-quant | 01-quant.md § Header disclosure required | docs must add dispersion-floor disclosure paragraph (wording supplied) | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 01-quant | decisions.md § D-1 | table.new row count 6->7 needed IF basis row adopted (pending human decision) |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
