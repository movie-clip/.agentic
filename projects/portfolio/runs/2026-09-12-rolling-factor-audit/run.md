# RUN 2026-09-12-rolling-factor-audit
request:      investigate how accurate and financialy correct Rolling Factor Analysis chart in Dashboard tab is. data correctness is most important
agentic_root: C:\projects\investments\.agentic
project:      portfolio
story:        NONE
status:       CLOSED
phase:        close
plan:         v1
budget:       3 — 2 triggered phases (ground-truth + quant-audit) + 1 close (docs), no framing/specification/design/build/integration/review (pure correctness investigation, no product change or code edit requested)
spent:        3
next:         none — CLOSED
gates:        quant-audit FAIL (see Artifacts 02) · integration skipped (no build lane triggered — investigation only) · review skipped (no story) · protocol-lint skipped (pack-corrections.md never opened; 03-docs.md pack_corrections: 0)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the area is unfamiliar / unverified claim about correctness | satisfied — 01 |
| framing | product | the request changes what the product does | not triggered (pure investigation, no new capability or scope change requested) |
| specification | quant (RESEARCH) | work introduces/changes a metric | not triggered (auditing an existing, already-shipped metric, not introducing one) |
| specification | story | framing produced unticketed scope | not triggered (framing did not fire) |
| design | design | contract boundary crossed / multi-lane build | not triggered (no build planned) |
| build | backend/frontend/test | anything that edits the repo | not triggered (investigation only; re-plan if audit finds a defect requiring a fix) |
| verify | quant-audit | analytics/formula/weighting/return-basis/trust-label touched | satisfied — 02 (FAIL) |
| verify | integration | any build lane dispatched | not triggered (no build lane) |
| verify | review | run carries a story | not triggered (no story) |
| close | docs | always | satisfied — 03 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | quant-audit | AUDIT | quantitative-researcher | opus | 02-quant-audit.md | DONE | FAIL |
| 03 | docs | — | docs-engineer | sonnet | 03-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| decision | 02-quant-audit | § F2 | CRITICAL, needs human ruling — 20d window has 3 residual dof and yields mean R² 0.850 on pure noise; not a lane fix | CARRIED |
| should_fix | docs/tech-debt-register.md | F1,F3,F5,F7-F10 | remaining code-level findings logged but unfixed; a future run's `build` would address them if the human approves | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| handoff | 01-recon | 02-quant-audit | shortest audit path named: methodology § Statistical Factor Model → factor_model.py → risk.py:1629 → test_analytics.py |
| handoff | 01-recon | 02-quant-audit | route is diagnostics.py, not exposure.py, despite surfacing via ExposureAnalysis |
| handoff | 01-recon | 02-quant-audit | schema of record is StatisticalFactorModel (reconciliation.py:488) embedded in DiagnosticsResult |
| risk | 01-recon | 02-quant-audit | daily_states/factor_histories/y construction in diagnostics_engine.py not traced — audit must trace return-basis source series |
| risk | 01-recon | 02-quant-audit | full status enum for _degrade_status_for_unverified_return_basis not enumerated — audit must read it directly |
| risk | 01-recon | 02-quant-audit | no route-level test confirmed for statistical_factor_model passthrough — audit must check |
| risk | 01-recon | 02-quant-audit | RollingFactorLoadingPoint field list inferred, not read from class def — audit must confirm exact fields |
| finding | 02-quant-audit | 03-docs (tech-debt-register.md) | F1 CRITICAL logged — card never reads `status`, degraded model renders as verified |
| finding | 02-quant-audit | 03-docs (tech-debt-register.md) | F2 CRITICAL logged, flagged owner-ruling-only — 20d window 3 residual dof, R² 0.850 on pure noise |
| finding | 02-quant-audit | 03-docs (tech-debt-register.md) | F3 logged — residual_vol wrong denominator, understates risk ~63% at 20d |
| finding | 02-quant-audit | 03-docs (financial-methodology.md fixed; F6 logged) | F4/F6 — 20d obs-count doc error fixed; stale λ=0.01 test-docstring error logged |
| finding | 02-quant-audit | 03-docs (tech-debt-register.md) | F5 logged — price-return y regressed against total-return factors, degrade gate blind to it |
| finding | 02-quant-audit | 03-docs (tech-debt-register.md) | F7-F10 logged — alpha always-null vs fabricated fixture, residual_vol missing _pct suffix, types.ts optional/required mismatch, no methodology section for residual_vol |
| risk | 02-quant-audit | 03-docs (tech-debt-register.md) | market-loading test asserts [-2,+4], pure noise only reached 0.46 — cannot fail, masked F2 — logged |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
