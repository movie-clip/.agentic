# RUN 2026-10-17-mvp-backlog-revision
request:      Revise the MVP backlog from run 2026-10-17-mvp-backlog (issues #8-#187 on Project 3). Do not create a new backlog: re-plan and update the existing issues. Review findings to address: Owner rulings (record in decisions.md): - OD3: products from unmapped feed categories are NOT public until mapped. - OD5: YES, legal notice, privacy and affiliate disclosure pages are in MVP scope (LSSI-CE). Take S9.3 off HOLD. I will supply the text (owner task). - OD2: the demo catalogue may be live during network review, but demo products are noindex and excluded from the sitemap, and demo /go links are not counted. - Other ODs stay open with their recommendations. Re-sequencing (producer): 1. Move brand + part-number matching (S7.1) and the review queue (S7.2) before the first real feed (S9.4), so real feeds don't create duplicate products. 2. Move "page stays when offers disappear" (S8.4) before S9.4. Indexed pages must not 404 after offer removal (S3.3). 3. Make S9.4 depend on the affiliate link pattern (S3.6), or justify why not. 4. Make Priority follow the build order: everything on the path to the first real feed is P0 (incl. S8.3 price history, S9.2 backups). Explain any P0 story that comes after go-live. 5. Fix dependency mismatches: S3.2 also depends on S3.1; S1.3 depends on S2.2, not S2.1; the critical path and the edge notes must agree about S8.3. Scope gaps against mvp.md: 6. Product attributes and fitment text from feeds: no story covers them. 7. Price history is "recorded by import", but imports are not scheduled. Say how days without an import appear on the chart. 8. S9.1: no visitor IPs in reverse-proxy or app access logs (guardrail 5). 9. S6.1 vs S8.4 contradiction: JSON-LD for a product with zero offers. 10. The click log must not count bots and crawlers following /go. 11. Feed URLs holding API keys: decide whether encryption (S10.3) must land before the first real feed. Board (orchestrator, after I approve the revised brief): 12. Fill the new "Slice" field on every story with its build-order number. 13. Rewrite every "Depends on" line as #issue references. 14. Create owner tasks O1-O11 as issues (owner work, never agent work), linked to the stories they block. 15. Apply the decision rulings to the issue bodies they block. Close or retitle anything the re-plan removes; never delete. Close: fix the stale "no backlog yet" / "no code" lines in project.md:87 and capabilities/product.md:4.
agentic_root: C:\projects\investments\.agentic
project:      projects/los-tres/project.md
story:        NONE
status:       CLOSED
phase:        close
plan:         v3
budget:       6 — framing (product 1) + build (docs 1) + integration (2: first run + CR-1 re-run) + close docs with CR-1 fix (1) + protocol-lint (1)
spent:        6
next:         none — CLOSED
gates:        integration CHANGES_REQUESTED (03, CR-1) then PASS (05) · review skipped (no story in this run) · protocol-lint PASS (06)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names existing code or rests on an unverified claim about current behaviour | not triggered (repo state is covered by runs/2026-10-17-mvp-backlog/01-recon.md and no code changed since; the findings are claims about the plan 02-product.md, which framing owns) |
| framing | product | the request adds a user-facing surface, changes what one is for, or mvp.md does not exist yet | satisfied — 01 |
| specification | story | framing produced scope no approved brief covers, and the slice crosses more than one lane's contract | not triggered (backlog revision, not a slice; story files are written when each slice run starts) |
| design | design | stack not chosen and code needed, or the change crosses the frontend/backend contract | not triggered (no code change; stack is recorded) |
| build | backend, frontend, test, docs | anything that edits repo code, tests or docs/** | satisfied — 02 |
| verify | integration | any build lane was dispatched | satisfied — 05 |
| verify | review | the run carries a story whose acceptance criteria someone must accept | not triggered (no story) |
| close | docs | always | satisfied — 04 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-product.md | DONE | — |
| 02 | docs | — | docs-engineer | sonnet | 02-docs.md | DONE | — |
| 03 | integration | INTEGRATION | tech-lead | sonnet | 03-integration.md | DONE | CHANGES_REQUESTED |
| 04 | docs | — | docs-engineer | sonnet | 04-docs.md | DONE | — |
| 05 | integration | INTEGRATION | tech-lead | sonnet | 05-integration.md | DONE | PASS |
| 06 | protocol-lint | — | protocol-linter | opus | 06-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| human | orchestrator | tracker.md § slice-map | Slice field missing on Project 3, so item 12 is not done; values are in each story body and tracker.md § slice-map | CARRIED |
| decision | 01-product | 01-product.md § Open decisions | OD1, OD4 (decide before slice 21), OD6-OD9 open; each written into the issues it blocks | CARRIED |
| human | runs/2026-10-17-mvp-backlog | #8 | E0 #8 still open; Done is human-only | CARRIED |
| human | orchestrator | PR #189 | mvp.md amendment awaits the human's merge | CARRIED |
| risk | 01-product | 01-product.md § contract_notes 3 | guardrail 1 wording does not name the unmapped state; owner's call | CARRIED |
| should_fix | 06-protocol-lint | 06-protocol-lint.md § findings | 4 rule-8 style items in project.md (long bullets, history line, decision range); plus stale lines :8, :130-131 | CARRIED |
| risk | 05-integration | 05-integration.md § risks | mvp.md § Search and browsing states schema.org data without the no-offers exception; owner may add a cross-reference | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| risk | 01-product | dismissed — origin/main has merge 8e58f8f (git log origin/main, this turn) | 'PR #7 must be merged before slice 1' |
| contract_note | 01-product | 02-docs (mvp.md edited on 188-mvp-amendment) | mvp.md needs edits for D-1 and the closed gaps; owner decides (would fire build: docs) |
| should_fix | CR-1 | 04-docs (bullet now names both changes); re-check 05 integration | mvp.md 'Only the offer list changes' contradicts 'Structured data is omitted' |
| pack_correction | 01-product | 04-docs (project.md, capabilities/product.md) | 3 corrections + stale project.md lines 13, 18; applied by docs at close |
| stale_profile | runs/2026-10-17-mvp-backlog | 04-docs | 'no backlog yet' / 'no code' lines are false; fix at close |
| contract_note | 01-product | issue bodies #19 #34 #47 #48 #190 (Story file: yes; design names test+doc updates) | S5.1, S8.4, S1.1, S8.3, S8.6 change shipped contracts |
| decision | 01-product | D-3 (OD10, OD11 ruled) and the CARRIED OD row | OD4 critical-path note, new OD10 and OD11 |
| human | orchestrator | the CARRIED slice-map row | no Slice field on Project 3 |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| CR-1 | docs | 1 | 2 | — |

## Replans
| plan | because | change |
|---|---|---|
| v2 | D-3: the human chose to apply the mvp.md amendment in this run | build (docs) and verify integration fire; budget 3 → 5 |
| v3 | 03-integration CHANGES_REQUESTED (CR-1) needs a docs fix and a gate re-run | CR-1 fix merged into the close docs order (one dispatch), integration re-run, protocol-lint; budget 5 → 6 (= ceiling, 2 × 3) |
