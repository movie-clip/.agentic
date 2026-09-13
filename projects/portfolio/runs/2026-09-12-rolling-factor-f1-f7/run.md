# RUN 2026-09-12-rolling-factor-f1-f7
request:      fix F1 from docs/tech-debt-register.md: RollingFactorLoadingsCard.tsx never reads the engine's status field, so a degraded_unverified_return_basis result renders identically to a verified one. Make the card honor trust-state semantics (verified > degraded > withheld > unavailable) per guardrail 4 and fix F7 from docs/tech-debt-register.md: RollingFactorLoadingPoint.alpha is always null in the real pipeline but a test fixture fabricates a non-null value, masking the gap. Align the fixture with real behavior or implement alpha properly, and add a contract_notes row for statistical_factor_model.status if still missing.
agentic_root: C:\projects\investments\.agentic
project:      portfolio
story:        NONE
status:       CLOSED
phase:        close
plan:         v4
budget:       14 — v3's 13, +1: 06-frontend.md emitted a pack_correction (capabilities/frontend.md's TrustBadge type table is stale), making protocol-lint accountable per phases.md/orchestrator.md § "gates: accounts for every gate" — this was noted in gates: at the time but not folded into the budget until now. +1 protocol-lint dispatch after docs applies the correction.
spent:        14
next:         none — CLOSED
gates:        quant-audit PASS (round 3, after 2 fix rounds — see 05/08/11-quant-audit.md) · integration PASS (12) · review skipped (no story) · protocol-lint PASS (14, on the capabilities/frontend.md pack correction)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the area is unfamiliar / unverified claim about correctness | not triggered (same-day run 2026-09-12-rolling-factor-audit already mapped this exact card, schema, and fixture; F1/F7 in docs/tech-debt-register.md carry file:line citations from that audit) |
| framing | product | the request changes what the product does | not triggered (defect in shipped behaviour — trust-label rendering and a stale test fixture — no new capability or scope change requested) |
| specification | quant (RESEARCH) | work introduces/changes a metric | not triggered (F1 wires the card to an already-computed, already-defined status field; F7 either removes or documents a field that was never populated — neither changes what a formula, weighting, return basis, or trust classification means) |
| specification | story | framing produced unticketed scope | not triggered (framing did not fire, so the precondition — unticketed scope from a framing brief — is false) |
| design | design | contract boundary crossed / multi-lane build | satisfied — 01 |
| build | backend/frontend/test | anything that edits the repo | satisfied — 02, 03, 04 |
| verify | quant-audit | analytics/formula/weighting/return-basis/trust-label touched | satisfied — 05 (FAIL), 08 (FAIL), 11 (PASS) |
| verify | integration | any build lane dispatched | satisfied — 12 (PASS) |
| verify | review | run carries a story | not triggered (no story) |
| close | docs | always | satisfied — 13 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | design | DESIGN | tech-lead | sonnet | 01-design.md | DONE | — |
| 02 | backend | — | backend-engineer | sonnet | 02-backend.md | DONE | — |
| 03 | frontend | — | frontend-engineer | sonnet | 03-frontend.md | DONE | — |
| 04 | test | — | test-engineer | sonnet | 04-test.md | DONE | — |
| 05 | quant-audit | AUDIT | quantitative-researcher | opus | 05-quant-audit.md | DONE | FAIL |
| 06 | frontend (CR-1) | — | frontend-engineer | sonnet | 06-frontend.md | DONE | — |
| 07 | test (CR-2) | — | test-engineer | sonnet | 07-test.md | DONE | — |
| 08 | quant-audit | AUDIT | quantitative-researcher | opus | 08-quant-audit.md | DONE | FAIL |
| 09 | frontend (CR-3) | — | frontend-engineer | sonnet | 09-frontend.md | DONE | — |
| 10 | test (CR-4) | — | test-engineer | sonnet | 10-test.md | DONE | — |
| 11 | quant-audit | AUDIT | quantitative-researcher | opus | 11-quant-audit.md | DONE | PASS |
| 12 | integration | INTEGRATION | tech-lead | sonnet | 12-integration.md | DONE | PASS |
| 13 | docs | — | docs-engineer | sonnet | 13-docs.md | DONE | — |
| 14 | protocol-lint | — | protocol-linter | opus | 14-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | 11-quant-audit | § Tooltip precedence | CR-3 changed which cause (missing proxy vs. unverified return basis) the 252d tooltip names when both apply; both render Degraded correctly, only the stated cause differs, no test pins the order | CARRIED |
| should_fix | 11-quant-audit | § risks | `modelPartialTooltip` still carries an unreachable `?? ''` fallback (RollingFactorLoadingsCard.tsx:211) — latent dead branching, not removed | CARRIED |
| should_fix | 12-integration | § TrustBadge docstring staleness | TrustBadge.tsx:5-11 docstring still lists 'degraded' as future work and omits RollingFactorLoadingsCard.tsx from its consumer list — a source-file comment, outside docs-engineer's docs/** scope | CARRIED |
| should_fix | 14-protocol-lint | § Out-of-scope observations | capabilities/frontend.md:184 checklist still lists synthetic/unavailable only, not degraded — future frontend/docs dispatch | CARRIED |
| should_fix | 14-protocol-lint | § Out-of-scope observations | capabilities/frontend.md:160 says withheld+degraded always badge, but TrustBadge's type union has no 'withheld' member — needs someone to open TrustBadge.tsx and resolve which side is wrong | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| finding | 05-quant-audit | 06-frontend (CR-1) | FINDING 1 — badge must also read model.status, not window status alone |
| finding | 05-quant-audit | 07-test (CR-2) | FINDING 3 — windows[].status="partial" test relabeled as defensive, not a live engine state |
| finding | 08-quant-audit | 09-frontend (CR-3) | FINDING 4 — badge gated on missingFactorKeysForWindow, not model.status, to stop false "missing proxy" claims on short-history-only fits |
| finding | 08-quant-audit | 10-test (CR-4) | FINDING 4 test — inverted the now-false badge assertion for short-history-only fixtures |
| finding | 11-quant-audit | dismissed — confirmed fixed, no further action | FINDING 4 re-verified against shipped engine; FINDING 1/3 re-verified not regressed |
| contract_note | 05-quant-audit | 13-docs | doc contract row for statistical_factor_model.status/windows[].status written with the corrected 5-value enum |
| pack_correction | 06-frontend | 13-docs | capabilities/frontend.md TrustBadge type table corrected to include 'degraded' |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| CR-1 (FINDING 1) | frontend | 1 | 2 |
| CR-2 (FINDING 3 + coverage) | test | 1 | 2 |
| CR-3 (FINDING 4) | frontend | 1 | 2 |
| CR-4 (FINDING 4 test) | test | 1 | 2 |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 05-quant-audit FAILed: FINDING 1 contradicts 01-design.md § F1 decision (model-level `partial` from a missing factor proxy renders no badge; design's plan only wired window-level status) | budget 7 → 10: +CR-1 (frontend), +CR-2 (test), +quant-audit round 2 |
| v3 | 08-quant-audit (round 2) FAILed: new FINDING 4 — CR-1's fix badges short-history-but-complete fits as "missing proxy," conflating two distinct causes of model.status="partial" | budget 10 → 13: +CR-3 (frontend), +CR-4 (test), +quant-audit round 3 |
| v4 | pack-corrections.md became non-empty at 06-frontend.md (dispatch 6), making protocol-lint accountable per phases.md — omitted from budget until now | budget 13 → 14: +protocol-lint, after docs applies the correction to capabilities/frontend.md |
