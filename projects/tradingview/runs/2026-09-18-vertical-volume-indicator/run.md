# RUN 2026-09-18-vertical-volume-indicator
request:      I need you to research how to show volume of trades in
              TradingView, but not regular graph but the one that goes
              vertically, so botom of the chart is right side of the screen,
              this indicator should show tradig volume, right now I'm mostly
              using VSA Wyckoff Volume indicator, but want better
agentic_root: C:\projects\investments\.agentic
project:      tradingview
story:        NONE
status:       CLOSED
phase:        close
blocked_on:
plan:         v6
budget:       13 — prior 12 (spent 11 of it) + CR-3, a MATERIAL finding the
              delta audit itself turned up (11-quant-audit.md F8): two
              array-clearing loops run backwards on an empty array on every
              chart's first render — pre-existing, masked until CR-2's fix
              let the script's logic actually execute for the first time.
              Fix (1); no further quant-audit round requested (pure
              loop-bounds guard, zero formula surface, matches 3
              already-audited-correct sites) — integration re-run absorbed
              the remaining budgeted dispatch before the next compile
              attempt. spent 13 of 13, exactly on budget.
spent:        13
next:         none — CLOSED
gates:        quant-audit PASS · integration PASS · review skipped (no story)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing script, or rests on an unverified claim | not triggered (no repo script named; the unverified claims — the VSA Wyckoff Volume indicator's behaviour, TradingView's drawing/profile capabilities — are external to the repo and outside recon's read-only repo remit) |
| framing | product | the request is a new script, or changes what an existing script is for | satisfied — 01 (verdict: needs research first; human stop pending) |
| specification (quant) | quant RESEARCH | the work introduces or changes a formula, a normalisation or a threshold | satisfied — 02 |
| specification (story) | story | framing produced scope no approved story covers, and the slice spans >1 script or a published signature | not triggered (single script per 02-quant's brief; nothing here is already published to TradingView) |
| design | design | more than one script changes together, or a published input/plot/alert signature changes | not triggered (02-quant confirms one script, no published signature) |
| build | backend, test, docs | anything edits a .pine file, a fixture or a script header | satisfied — 03, 06 (CR-1), 10 (CR-2), 12 (CR-3) — verification FAIL on every pass is the one documented pine_check.py false positive, see Open — not a guardrail violation |
| verify — quant-audit | quant-audit | any lane touched a formula/threshold/normalisation/symbol mapping | satisfied — 04, re-confirmed 07 (delta, CR-1) and 11 (delta, CR-2) — verdict PASS all three times |
| verify — integration | integration | any build lane was dispatched | satisfied — 05, re-confirmed 08 (CR-1) and 13 (CR-2+CR-3) — verdict PASS all three times (verification FAIL is the known P008 false positive; 6 unrelated pre-existing findings on other scripts, out of scope) |
| verify — review | review | the run carries a story whose criteria someone must accept | not triggered (story not triggered) |
| close | docs | always | satisfied — 09 (header corrected per F6; docs/volume-profile.md created); compile.md Attempt 2 (2026-09-18) confirms the live compile check PASSES on the final, post-CR-3 code |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-product.md | DONE | NONE |
| 02 | quant | RESEARCH | quantitative-researcher | opus | 02-quant.md | DONE | NONE |
| 03 | backend | — | backend-engineer | sonnet | 03-backend.md | PARTIAL | NONE |
| 04 | quant-audit | AUDIT | quantitative-researcher | opus | 04-quant-audit.md | DONE | PASS |
| 05 | integration | INTEGRATION | tech-lead | sonnet | 05-integration.md | DONE | PASS |
| 06 | backend | — | backend-engineer | sonnet | 06-backend.md | PARTIAL | NONE |
| 07 | quant-audit | AUDIT | quantitative-researcher | opus | 07-quant-audit.md | DONE | PASS |
| 08 | integration | INTEGRATION | tech-lead | sonnet | 08-integration.md | DONE | PASS |
| 09 | docs | — | docs-engineer | sonnet | 09-docs.md | DONE | NONE |
| 10 | backend | — | backend-engineer | sonnet | 10-backend.md | PARTIAL | NONE |
| 11 | quant-audit | AUDIT | quantitative-researcher | opus | 11-quant-audit.md | DONE | PASS |
| 12 | backend | — | backend-engineer | sonnet | 12-backend.md | PARTIAL | NONE |
| 13 | integration | INTEGRATION | tech-lead | sonnet | 13-integration.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | 03-backend + pine_check.py source | 03-backend.md § risks | pine_check.py's SECURITY_CALL regex flags request.security_lower_tf() for missing `lookahead`, a parameter that function does not have (confirmed against Pine v6's actual signature via web research) — checker false positive, not a script defect; fix is out of this run's scope (no lane owns scripts/pine_check.py here) | CARRIED |
| should_fix | 04-quant-audit | 04-quant-audit.md F2 | MINOR: C=0 branch depends on unverified empty-vs-na behaviour of request.security_lower_tf() — compile.md Attempt 2 confirmed the C=M happy path (120/120 covered, no error) on SPX Daily but did not exercise C=0 (needs a symbol/timeframe combo with no intrabar data); still open | CARRIED |
| should_fix | 04-quant-audit | 04-quant-audit.md F3 | MINOR: integer division truncates the intrabars/bar diagnostic, can misfire the DEGRADED threshold by rounding alone | CARRIED |
| should_fix | 04-quant-audit | 04-quant-audit.md F4 | MINOR: Coverage row reads "0 of M" both for genuine data loss and for failures that preceded binning entirely — legibility only | CARRIED |
| should_fix | 04-quant-audit | 04-quant-audit.md F5 | MINOR: POC displayed as a full-precision point price when it only resolves to a $-wide bin; no bin-height/bounds shown | CARRIED |
| should_fix | 05-integration | 05-integration.md | 6 pre-existing SHOULD_FIX findings on strategy13_trend_carry.pine and systemic_stress_dashboard.pine, byte-identical to initial commit — unrelated to this run, surfaced as a backlog item, not CR'd here | CARRIED |
| risk | 06-backend | 06-backend.md § risks | implementation judgment call: CR-1's fix skips+flags a na intrabar rather than blanking the whole profile to n/a — a defensible reading, satisfies CR-1's requirement (Status no longer reads bare OK), surfaced at close-out rather than re-opened as a decision | CARRIED |
| should_fix | 07-quant-audit | 07-quant-audit.md F7 | MINOR: "Intrabars/bar (avg)" counts skipped intrabars in its numerator — reports returned-per-bar, not binned-per-bar; now recorded in docs/volume-profile.md Known limits, code itself still unfixed | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 03-backend | 09-docs | docs/volume-profile.md created with all six required sections |
| contract_note | 07-quant-audit F6 | 09-docs | header's Reconciliation bullet corrected — a low ratio now correctly read against the Status text, not unconditionally |
| should_fix | 11-quant-audit F8 (CR-3) | 12-backend | both array-clearing loops now guarded with array.size(...) > 0, matching the file's existing pattern — no more backwards iteration on an empty array |
| should_fix | 04-quant-audit F1 (CR-1) | 06-backend | na close/volume now skipped, not binned; Status flags "OK — N na intrabar(s) skipped" instead of bare OK; close-is-na no longer reaches array.set |
| contract_note | 02-quant | 03-backend | header declares ORIGINAL + candle-derived approximation + not native TV tool |
| contract_note | 02-quant | 03-backend | coverage diagnostic (C of M bars; volume-reconciliation ratio) implemented as always-visible table |
| contract_note | 02-quant | 03-backend | guardrail 3 trivially satisfied — chart symbol only, no input.symbol() needed; confirmed no external symbol in script |
| should_fix | platform-research.md §4 | 03-backend | realised-intrabars/bar diagnostic implemented, flags DEGRADED below the 50-100 target band |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| CR-1 | backend | 1 | 2 | independent |
| CR-2 | backend | 1 | 2 | independent |
| CR-3 | backend | 1 | 2 | independent |

## Replans
| plan | because | change |
|---|---|---|
| v2 | human ruled D-1 (custom build) and D-2 (rendering-only) on 01-product.md's Open decisions | specification(quant RESEARCH) confirmed triggered; budget 1 -> 2 |
| v3 | 02-quant fixed the scope at one script, no open branches; spent reached budget | build/quant-audit/integration/close confirmed triggered, design/story/review confirmed not triggered; budget 2 -> 6 |
| v4 | human ruled D-3 (fix F1 now) on 04-quant-audit's MATERIAL finding | CR-1 opened, round 1 of 2; budget 6 -> 9 for the fix + re-verify pass |
| v5 | live compile check FAILed (compile.md): nested array<array<float>> does not compile in Pine v6 | CR-2 opened, round 1 of 2, BLOCKING by the acceptance command itself; budget 9 -> 12 |
| v6 | delta audit (11-quant-audit) found F8, a MATERIAL runtime-crash-on-first-render defect masked until CR-2 let the code execute | CR-3 opened, round 1 of 2; budget 12 -> 13 |
