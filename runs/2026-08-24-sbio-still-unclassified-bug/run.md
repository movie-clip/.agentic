# RUN 2026-08-24-sbio-still-unclassified-bug
request:      After running `python .\scripts\manage_cache.py clear` and
              re-importing docs/IB2026.csv, SBIO still shows Unclassified
              sector in the live app, despite US-39.1 (Epic 39, closed
              2026-08-24 same day) shipping identity-gated dynamic ETF
              sector resolution specifically for this ticker, all three
              gates passed.
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
route:        full (scope grew past express once a contract change entered)
express:      no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | haiku | 01-scout.md | DONE | — |
| 02 | design | DESIGN | tech-lead | sonnet | 02-technical-plan.md | DONE | — |
| 03 | design | DESIGN | tech-lead | sonnet | 03-technical-plan.md | DONE | — |
| T0 | backend | T0 | backend-engineer | sonnet | T0-backend.md | PARTIAL | — |
| T1 | frontend | T1 | frontend-engineer | sonnet | T1-frontend.md | DONE | — |
| T0-docs | docs | T0-docs | docs-engineer | sonnet | T0-docs.md | DONE | — |
| T2 | test | T2 | test-engineer | sonnet | T2-test.md | DONE | — |
| AUDIT | quant-audit | AUDIT | quant-analyst | opus | AUDIT-quant.md | DONE | FAIL |
| CR-1 | frontend | CR-1 | frontend-engineer | sonnet | CR-1-frontend.md | DONE | — |
| INTEGRATION | integration | INTEGRATION | tech-lead | sonnet | INTEGRATION-tech-lead.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| finding | AUDIT-quant | Finding 2 (MATERIAL) | no end-user UI signal that a base-import node's frozen data isn't live — snapshot picker labels it just "base", no date. Human explicitly deferred as accepted gap, not part of this run | CARRIED |
| finding | 03-technical-plan | § Risk detail | run_metadata.source_status.lookthrough_resolution / .confidence retain the identical trust-descriptor staleness risk availability had (Finding 1's class) — not fixed here, candidate follow-up | CARRIED |
| finding | 01-scout | § handoff | risk.py:612/1483 (build_lookthrough_exposure, build_etf_overlap_pairs) call attach_snapshot_metadata with no market_data arg — inert today (only .asset_class read), would matter if either's metadata use ever extends to sector | CARRIED |
| finding | 02-technical-plan | § Decisions | add_snapshot mode stays broken — deliberately excluded both times scope was decided; a future fix needs client-side recombination of two PortfolioOverview-shaped objects, not designed here | CARRIED |
| protocol_note | T1-frontend / CR-1-frontend | verification framing | two lanes reported the same class of situation (a known, pre-scoped, downstream-owned failure) with different status labels (PARTIAL/FAIL vs DONE/PASS) — inconsistent self-reporting style, not a content problem; worth naming as a house convention next time this recurs | CARRIED |
| protocol_note | CR-1-frontend | § Test-writing conflict | orchestrator's own CR asked a frontend-engineer to write tests, violating this project's lane discipline (test-engineer owns test files); work was correct and verified, not worth relocating after the fact — noted so future CRs route test-writing separately | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| finding | 01-scout | orchestrator + T0/T1 | root cause (instruments=[] in build_imported_snapshot_from_request) traced fully; confirmed not an Epic 39 defect |
| finding | 01-scout | T1 | the discarded analyze-upload response is now persisted and reused instead of re-derived |
| finding | 01-scout | 01-scout § Ruled-out checks | confirmed everything US-39.1 shipped (identity gate, SBIO.L rule, threshold, endpoint, cache, API key) was correct and uninvolved |
| finding | 01-scout | 02/03-technical-plan | two fix options named — human chose (b); scope later expanded per human decision to close the wider blast radius too |
| human_decision | user | 02/03 design | fix direction (b), then scope expansion to include lookthrough/market_overlap, add_snapshot excluded |
| finding | orchestrator (App.tsx read) | 03-technical-plan | runExposureEngine's full call-site map confirmed, grounding the design |
| finding+decisions | 02-technical-plan | 03-technical-plan | blast-radius/add_snapshot/duplication/restoredSession findings and decisions all carried into and confirmed by the final design |
| finding | orchestrator (schema reads) | 03-technical-plan | ImportedBootstrapResponse's missing fields and build_exposure_result's already-computed-but-discarded object both confirmed, degrisking the schema-widen decision |
| protocol_note | 03-technical-plan brief | orchestrator direct read | validator's missing-section-reference resolved by reading the full artifact; content was complete |
| decisions (availability inclusion, fx exclusion, bundled type) | 03-technical-plan | T0/T1 | all three implemented exactly as decided |
| human_decision | user | T0 dispatch | approved 03's T0/T0-docs/T1/T2 in full, superseding 02's narrower tickets |
| tests_expected_broken | T0-backend | T1/T2 | both flagged tsc errors resolved by their respective owning lanes |
| infra_failure | T2 first attempt | T2 completion pass | session-limit interruption; on-disk edits reviewed and confirmed complete rather than redone |
| finding | AUDIT-quant Finding 1 | CR-1 | trust-badge vintage-mismatch fixed — getBenchmarkTrust now reads only frozen availability, independently confirmed twice (orchestrator + tech-lead integration) |
| human_decision | user | CR-1 | fix approach chosen (derive from frozen data only) and confirmed behavior-preserving before dispatch |
| finding | CR-1-frontend | tech-lead INTEGRATION | broken DashboardPanel test was testing the buggy path, correctly updated; reviewed and confirmed appropriately scoped |
| finding | orchestrator (BenchmarkPositioningCard read) | tech-lead INTEGRATION | independently confirmed twice; no run_metadata trust dependency remains anywhere |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| Finding 1 (AUDIT) | frontend | 1 | 2 |

## Cost
| metric | value |
|---|---|
| dispatches | 10 |
| rounds | 1 |
| by model | sonnet 8 · opus 1 · haiku 1 |
| escalations | none (1 infra-failure retry, T2's first attempt, session-limit error — same model re-dispatched, not an escalation) |
