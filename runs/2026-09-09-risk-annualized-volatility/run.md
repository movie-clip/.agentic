# RUN 2026-09-09-risk-annualized-volatility
request:      Add a portfolio-level annualized volatility metric to the Risk tab. Compute it from the daily returns of the current portfolio's synthetic history, and show it in the risk summary area alongside the existing risk figures. When there is not enough return history to compute it responsibly, it must not display a number — show the appropriate trust state instead. I have not decided which annualization convention to use, or what the minimum amount of history should be. Treat both as open questions. Keep it sourced and rendered consistently with the other Risk tab metrics.
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
blocked_on:   none
next:         none — CLOSED. Human runs `python scripts/run_all_tests.py` (acceptance command), then commits. No agent commits.
human_story_approval:
  - 2026-09-09: human approved draft US-44.1 ("it looks good, proceed to the tech lead design pass").
  - item (1) story ID US-44.1 / Epic 44: ACCEPTED as drafted.
  - item (4) wider ~2<=N<60 divergence band: ACCEPTED (no Dashboard floor change).
  - item (2) zero-variance at N>=60 publish-0 vs withhold: STILL OPEN — deferred to tech-lead DESIGN for a recommendation, human rules before any implementation ticket runs. Not decided by omission.
  - item (3) withheld-state representation: tech-lead DESIGN owns it.
human_design_approval:
  - 2026-09-09: human approved the DESIGN work-order plan ("1. Approve"). Lane split T-44.1.1 backend -> T-44.1.2 frontend -> T-44.1.3 tests -> quant-audit / integration / review gates -> T-44.1.4 docs. 6 build/gate agents.
  - Open decision 2 (zero-variance return series at N>=60): RULED "publish 0.00%" ("2. publish 0.00%"), matching tech-lead recommendation 05-technical-plan.md § 5. Binding on T-44.1.1 gate logic and T-44.1.3 tests.
route:        full
express:      no
human_decisions:
  - deleted planning docs (ce9c97d): INTENDED — leave deleted. story-author recreates only the single story file; docs close-out scoped to surviving docs.
  - epic placement: NEW small Risk-tab epic (grouped with carried Backlog US-41.1). Orchestrator proposing Epic 44 / US-44.1 pending human confirm.
  - decision (a): OPTION A — reuse Dashboard diagnostics figure volatility_summary.portfolio_volatility_pct (stdev(daily)*sqrt(252), sample N-1).
  - decision (b): OPTION B — stricter annualized-vol floor of 60 trading days (~3 months), NOT the inherited 20-obs floor.
gates:        quant-audit PASS (09) · integration PASS (10) · review PASS (11)
dispatched:   12

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | quant | RESEARCH | quant-analyst | opus | 02-quant-research.md | DONE | — |
| 03 | recon | — | scout | sonnet | 03-scout.md | DONE | — |
| 04 | story | — | story-author | sonnet | 04-story.md | DONE | — |
| 05 | design | DESIGN | tech-lead | sonnet | 05-technical-plan.md | DONE | — |
| 06 | backend | — | backend-engineer | sonnet | 06-backend.md | DONE | — |
| 07 | frontend | — | frontend-engineer | sonnet | 07-frontend.md | DONE | — |
| 08 | test | — | test-engineer | sonnet | 08-test.md | DONE | — |
| 09 | quant | AUDIT | quant-analyst | opus | 09-quant-audit.md | DONE | PASS |
| 10 | integration | INTEGRATION | tech-lead | sonnet | 10-integration.md | DONE | PASS |
| 11 | review | — | reviewer | sonnet | 11-review.md | DONE | PASS |
| 12 | docs | close-out | docs-engineer | sonnet | 12-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| contract_note | 05-technical-plan | 06-backend.md changed | schemas/diagnostics.py model + literal + required field LANDED by T-44.1.1 | ABSORBED by 06 |
| contract_note | 06-backend | 07-frontend.md changed | types.ts mirror LANDED by T-44.1.2 (onto ImportedDiagnosticsSource + alias DiagnosticsEngineResponse) | ABSORBED by 07 |
| contract_note | 06+07 | 12-docs.md | ALL doc contract notes ABSORBED by T-44.1.4: methodology amendment, risk-fields.md NEW section (+verbatim card copy), diagnostics-fields.md cross-ref, dashboard-fields.md note, current-product-state.md inventory, story-file status | ABSORBED by 12 |
| risk | 06-backend | 09-quant-audit.md § A3 | zero-variance N>=60 = trust=synthetic 0.00% passthrough — quant-audit CONCURS, sound under g4 | CLOSED |
| risk | 06-backend | 10-integration.md | build_unavailable_diagnostics_result local-var lift — integration confirms behaviour-preserving (obs=0 still -> unavailable) | CLOSED |
| risk | 07-frontend | 08-test.md verification | 07 tsc/vitest gaps: T-44.1.3 ran full run_all_tests.py exit 0 (backend 1001, frontend 369, tsc clean, deadcode clean, goldens no drift) | CLOSED |
| risk | 08-test | 09 + 10 | conftest _mock_price_rows cadence dependency for N-range bounds — both gates saw it; tests assert ranges not exact counts | CLOSED (noted) |
| risk | 08-test | 12-docs.md handoff | withheld copy strings now pinned in BOTH AnnualizedVolatilityCard.test.tsx and risk-fields.md §US-44.1 "Verbatim card copy" — any future copy edit must move both | CARRIED (known, documented) |
| risk | 07-frontend | 10-integration.md | 3-vs-2 shapes RESOLVED: DiagnosticsResult is the single response model; TS has one mirror + alias, both carry the field; 06 wording was loose, no shape missed | CLOSED |
| risk | 07-frontend | 11-review.md | TrustBadge not extended — review RULES acceptable; no AC needs a withheld badge, AC7/8/10 met by distinct EmptyState copy (05 §1.5) | CLOSED |
| risk | 07-frontend | 11-review.md | LoadingState-forever on diagnostics-fetch failure — review RULES acceptable; no AC covers a frontend transport failure | CLOSED |
| note | 11-review | 11-review.md risks | AC12 methodology pointer renders in published state only; withheld/unavailable name the 60-day floor in prose, no link — judged sufficient per 05 §1.5 | CLOSED (noted) |
| risk | orchestrator | git HEAD ce9c97d | planning corpus deleted & staying deleted — docs close-out cannot reconcile roadmap/PRD/index; only current-product-state.md + contracts + methodology survive | CARRIED |
| risk | 05-technical-plan | 09-quant-audit.md § A2 | gating floor on paired risk_summary.observations — quant-audit RULED CORRECT | CLOSED |
| risk | 05-technical-plan | 11-review.md | TrustBadge "withheld" extension NOT taken — review + design agreed EmptyState-copy fallback satisfies AC7/8/10 | CLOSED |
| debt | 09 + 10 + 12 | AnnualizedVolatilityCard.tsx:38 | formatPct has an unreachable `value==null -> '—'` branch (only called in synthetic block); flagged SHOULD_FIX by 3 gates; knip does not catch it, does not block commit; no lane fixed it | CARRIED — deferred code nit |
| debt | 09 + 12 | analytics/risk.py:2120 | pre-existing: `_calculate_annualized_volatility` uses literal sqrt(252) while VOLATILITY_ANNUALIZATION_DAYS=252 exists same module; same value; untouched by US-44.1; not in tech-debt-register | CARRIED — pre-existing, out of scope |
| risk | 12-docs | 12-docs.md risks:3 | methodology amendment cites run-dir path 02-quant-research.md § 2.4 for the CI-width tables — less durable than an in-repo ref if run artifacts are ever pruned | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| decision | orchestrator | human 2026-09-09 | epic number US-44.1 / Epic 44 accepted |
| finding | 02-quant-research | 05-technical-plan §§ 1,3,5 | withheld rung + 60-obs constant + no-Dashboard-floor all resolved in the technical plan |
| finding | 02-quant-research | human 2026-09-09 | ~2<=N<60 divergence band accepted |
| story-draft | 04-story | human 2026-09-09 | US-44.1 draft approved; tickets re-cut by DESIGN |
| finding | 01-delivery-brief | 05-technical-plan | "already ships on Dashboard" — plan reuses that exact scalar/path |
| decision | 05-technical-plan | human 2026-09-09 | zero-variance at N>=60 RULED "publish 0.00%" (matches tech-lead rec 05 § 5) |
| design-plan | 05-technical-plan | human 2026-09-09 | DESIGN work-order plan approved; build lanes cleared to dispatch |
| build | T-44.1.1/2/3 | 06 / 07 / 08 all DONE | backend + frontend + tests landed; canonical run_all_tests.py green (exit 0); contract_notes 0 from test lane |
| gate | quant-audit | 09-quant-audit.md | PASS — all 4 guardrails hold; reused scalar bit-identical on independent recompute; floor placement + paired-N + zero-variance ruling all sound; no change requests |
| gate | integration | 10-integration.md | PASS — contract identical across the seam; 3-vs-2 shape discrepancy = loose wording in 06, no shape unmirrored; wiring intact; unavailable-path refactor behaviour-preserving; gates clean; no dropped doc obligation |
| gate | review | 11-review.md | PASS — all 12 ACs SATISFIED with file/test evidence; every test-plan case is a real passing test; trust rendering honest across 4 states; both routed items ruled acceptable; suite re-run exit 0 (1001 / 369) |
| docs | T-44.1.4 | 12-docs.md | close-out DONE — 6 files reconciled (methodology amendment, risk-fields.md NEW section, diagnostics/dashboard-fields.md, current-product-state.md, story-file status→Done); all contract notes absorbed; report bounced once for a format defect then re-validated |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 12 (run_cost.py) — 01 producer · 02 quant-RESEARCH · 03 scout · 04 story-author · 05 tech-lead-DESIGN · 06 backend · 07 frontend · 08 test · 09 quant-AUDIT · 10 tech-lead-INTEGRATION · 11 reviewer · 12 docs |
| rounds | 0 finding-driven change-request rounds — no gate returned FAIL, no finding reached a 2nd round |
| format re-dispatches | 3, all validator-format only (no content change): 03-scout brief over line limit (pre-compaction), 04-story brief (pre-compaction), 12-docs verification-block command field |
| by model | sonnet 10 · opus 2 (opus = 02 + 09, the two quant lanes, per agent-file pin; no overrides) |
| escalations | none |
| close-out | run_cost.py exit 0 · check_report.py --require-heads exit 0 (03/04 heads were derived via --emit-head at close-out — Bash-less lanes, heads not persisted earlier) |
