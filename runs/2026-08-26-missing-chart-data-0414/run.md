# RUN 2026-08-26-missing-chart-data-0414
request:      looks like there is missing data for 04/14/2026 on chart for
              my portfolio, investigate this bug and fix it
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       DISPATCHING
next:         US-41.1 approved by user (confirmed via a follow-up request
              describing the same symptom, resumed into this run rather
              than duplicating it). (06) tech-lead DESIGN dispatched —
              contract for the new field, frontend annotation treatment,
              and the dead-branch deletion question. Awaiting head.
route:        review
express:      no
gates:        <not yet determined>

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | haiku | 01-scout.md | DONE | — |
| 02 | product | — | producer | sonnet | 02-delivery-brief.md | DONE | — |
| 03 | quant | RESEARCH | quant-analyst | opus | 03-quant-research.md | DONE | — |
| 04 | docs | — | docs-engineer | sonnet | 04-docs.md | DONE | — |
| 05 | story | — | story-author | sonnet | 05-story.md | DONE | — |
| 06 | design | DESIGN | tech-lead | sonnet | 06-technical-plan.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| protocol_note | 01-scout | 01-head.txt | shell-less lane self-typed head disagreed with derived head on 3 counts (changed/contract_notes/pack_corrections 1→0, handoff 9→11) — orchestrator derived via --emit-head, used that | ABSORBED |
| finding | 01-scout | § handoff | 2026-04-14 is a real trading day (Tuesday, 5 real IB2026.csv executions incl. LQQ) — intentionally, fail-closed withheld under US-33.2/US-33.4's LQQ share-unit-discontinuity guard, not a market-holiday/cache gap; return_is_publishable=False, one of exactly 4 withheld dates on the current statement | OPEN |
| finding | 01-scout | § handoff | Dashboard chart (PerformanceBenchmarkCard.tsx) nulls the point, Line connectNulls=false renders a genuine break — this is the withheld-day mechanism working as designed (guardrail 4: never fabricate), not a data bug | OPEN |
| finding | 01-scout | § handoff | the gap IS disclosed elsewhere on the same tab (ReplayDisclosuresCard + a summary note on PerformanceBenchmarkCard itself) but neither annotates the chart's actual line-break inline — a user looking only at the line has no inline explanation | OPEN |
| finding | 01-scout | § risks | not confirmed whether the just-closed chart-audit run's fix changed gap *rendering* — that run's own log explicitly separated gap-handling as pre-existing/unmodified, worth a downstream re-confirm | OPEN |
| finding | 01-scout | § handoff, § risks | 3 other candidate charts (MonthlyReturnsGrid whole-month reliability, Exposure drift chart, Risk-tab drawdown/VaR) share the same return_is_publishable mechanism but rendering was not confirmed for any of them — genuine ambiguity about which chart the user means | ABSORBED |
| finding | 01-scout | § risks | central open question: is this "the bug" at all (correct, disclosed withholding — nothing to fix) or is the actual complaint a UX gap (no inline annotation on the chart itself)? Scout explicitly left this for a human/downstream judgment, not concluded | ABSORBED |
| human_decision | user | this turn | chart confirmed: Dashboard Performance & Benchmark card. Behavior confirmed intentional/correct; user wants an inline annotation added on the chart itself at the withheld-date gap | ABSORBED |
| finding | 02-delivery-brief | § Placement | verdict: new story, no fitting open epic (Epic 33/34/40 all closed, never-reopen applies); NOT express-eligible — disqualified on "no new user-visible scope" alone, other 4 criteria pass | ABSORBED |
| finding | 02-delivery-brief | § Stories | PROPOSED story: inline marker/tooltip on PerformanceBenchmarkCard.tsx's chart at each withheld-date null point; scope explicitly excludes the 3 other candidate charts (Exposure drift, Risk drawdown/VaR, MonthlyReturnsGrid) as follow-on candidates, not built now | ABSORBED |
| human_decision | user | this turn | hold as Backlog story, no new epic yet — per project's "Backlog until it has siblings" convention | ABSORBED |
| human_decision | user | this turn | cause-derivation approach: thin backend field (single source of truth), not client-side re-derivation of replay_disclosures()'s classification logic | ABSORBED |
| finding | 02-delivery-brief | § Open decisions | flat run_metadata.withheld_return_reason string is incidentally correct today (all 4 withheld dates share one cause) but structurally wrong for a future statement with multiple simultaneous causes on different dates — this is exactly why thin-backend-field was the right call, not just a style preference | ABSORBED |
| finding | 03-quant-research | § Classification branches | delivery brief's "two-branch" framing was stale: only unbacked_cash_flow materiality withholds a return today (US-34.8); reconciliation_adjustment never does — confirmed 3 ways (code, existing test, independent recompute against live IB2026 fixture) | ABSORBED |
| finding | 03-quant-research | § Field proposal | proposed PerformancePoint.withheld_reason: str\|None, computed via a new shared _withheld_return_cause(state) classifier in performance.py's existing per-state loop — single source of truth also usable by replay_disclosures() | OPEN |
| finding | 03-quant-research | § Scope of what the field explains | portfolio_return_pct=null has 3 distinct causes, only 1 (state-level withholding) is per-date/state-carried — the other 2 (basis suppression, zero-denominator gap) must NOT get a fabricated per-point reason; narrows the story's AC accordingly | OPEN |
| finding | 03-quant-research | § Methodology doc status | guardrail-3/4 (trust/disclosure honesty) territory, not guardrail-1 (formula) — small doc addition warranted, not a new formula section | OPEN |
| finding | 03-quant-research | § Methodology doc status | pre-existing CRITICAL-class doc defect found (unrelated to this story): financial-methodology.md:2436-2443 states the stale pre-US-34.8 withholding rule, directly contradicting the doc's own corrected section (lines 565-638), the shipped code, and an existing test. Same stale framing also in a code comment (dashboard_history_engine.py:504-505) | OPEN |
| finding | 03-quant-research | § Open questions | 2 unresolved design questions flagged for tech-lead: (a) delete replay_disclosures()'s now-provably-dead reconciliation_adjustment branch or leave with a comment; (b) fix the doc defect now (express) or bundle into this story's close-out | ABSORBED (b resolved: fix now, separately) |
| human_decision | user | this turn | fix the financial-methodology.md self-contradiction now, as a separate express docs dispatch, not bundled into the eventual story | ABSORBED |
| finding | 04-docs | § changed | fixed 2 locations (2436-2454, 2563-2568) plus a stale cross-reference and a matching code comment (dashboard_history_engine.py:504-509); orchestrator independently re-ran the verification grep, confirms all mentions now consistent with US-34.8 rule | ABSORBED |
| finding | 04-docs | § handoff, § risks | found and fixed a SECOND, previously-unflagged echo of the same stale claim (lines 2556-2558) beyond the order's cited range — judged same underlying contradiction, not scope creep; flagged for awareness | ABSORBED |
| protocol_note | 05-story | 05-head.txt | shell-less lane self-typed head disagreed with derived head on 2 counts (pack_corrections 1→0, handoff 4→5) — orchestrator derived via --emit-head, used that | ABSORBED |
| finding | 05-story | draft | docs/product/stories/US-41.1-inline-withheld-return-annotation.md written — Backlog status, 6 ACs (narrowed per guardrail 4), 4 tickets, both open design decisions reproduced unresolved, out-of-scope surfaces named explicitly | OPEN |
| finding | 05-story | § Open decisions | numbering "US-41.1" is an explicit placeholder (40 is the highest epic in use, every story conventionally lives under some epic number even Backlog-status) — flagged for renumbering/confirmation whenever an epic is actually opened | OPEN |
| human_decision | user | this turn | US-41.1 approved as drafted (re-confirmed via a follow-up /agentic-core:feature invocation describing the same symptom with explicit dates — resumed this run rather than starting a duplicate one) | ABSORBED |
| finding | 06-technical-plan | § Decision: delete the dead branch | replay_disclosures()'s reconciliation_adjustment branch DELETED, not left with comment — compelled by AC4 (one classification, not two), and the branch was found to be a latent disclosure-honesty defect (could misattribute a cause) not just dead code | ABSORBED |
| finding | 06-technical-plan | § Lane split and order | corrects a real story/pack conflict: story's T-41.1.1 text bundled types.ts + dashboard-fields.md into "Backend" ticket, but backend.md forbids backend-engineer from touching apps/desktop/** or docs/** — dispatch per the plan's actual lane split, not the ticket's literal wording | OPEN |
| finding | 06-technical-plan | § Frontend visual treatment | marker = ReferenceDot diamond at y=100 (chart's existing neutral baseline) in --color-status-warn, keyboard-focusable (tabIndex/role=img/aria-label with full reason), reveals a caption paragraph on focus/hover reusing the card's existing helper-text pattern — no floating tooltip, no opportunistic design-system migration | ABSORBED |
| finding | 06-technical-plan | § Test-plan resolution | 2-tier test fix needed: (1) extend existing LineChart mock's data dump to include withheldReason, (2) test the marker component in isolation (must be a named component, not inline) — existing mock never mounts anything inside LineChart today | OPEN |
| finding | 06-technical-plan | § risks | 3 unverified-but-flagged implementation risks for test-engineer: ReferenceDot shape prop confirmed from typings not live render; jsdom SVG focus-event delivery unconfirmed; aria-label path holds regardless if jsdom focus fails | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | — |
| rounds | — |
| by model | — |
| escalations | none |
