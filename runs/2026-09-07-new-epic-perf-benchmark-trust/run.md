# RUN 2026-09-07-new-epic-perf-benchmark-trust
request:      take this points, create one new Epic with 4 stories:\nP1 — Monthly returns can publish a fabricated return on a withheld day. The monthly calculation ignores return_is_publishable and terminal reconciliation adjustments, unlike the main performance chain. An unbacked-cash day can therefore appear as, e.g., a +100% monthly return even though the daily return was explicitly withheld. I reproduced this with a withheld state. See dashboard_history_engine.py:855 versus the shared withholding rule in reconciliation.py:588.\nP2 — The withheld-return warning gets the direction wrong for negative impact. The UI correctly displays a signed impact, but always says the shown return "understates" performance. If including withheld days would lower the return, the shown value instead overstates it. See PerformanceBenchmarkCard.tsx:249.\nP2 — A benchmark outage suppresses all portfolio-performance output. The imported engine returns the fully unavailable dashboard result when benchmark history is absent, even if holdings history and replay states are usable. Portfolio TWR, MWR, contributions, and monthly returns should be independently available with benchmark fields marked unavailable. See dashboard_history_engine.py:304 and performance.py:305.\nMissing capability — Benchmark is effectively fixed to the default. The visible flow has no benchmark selector, and /run-imported accepts only a snapshot, so users cannot choose an appropriate comparison index despite the underlying service accepting an optional symbol. This matters for non-US, multi-asset, or mandate-specific portfolios. See dashboard_history.py:19 and PerformanceBenchmarkCard.tsx:128.
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
close_note:   planning run — Epic 44 created (fresh minimal doc skeleton) with 4 approved Backlog stories US-44.1..US-44.4. Implementation is 4 separate later story-route runs. Nothing shipped; nothing committed.
reverted:     2026-09-09 — HUMAN changed their mind before any implementation. All portfolio-repo output of this run deleted: docs/product/epic-roadmap.md, docs/product/prd/ (README + epic-44 PRD), docs/product/stories/ (README + US-44.1..US-44.4). The 06 pack edits to capabilities/product.md + story.md were git-restored to committed state. Run artifacts + this ledger kept as the audit record. NOTE: capabilities/product.md + story.md still carry PRE-EXISTING references to the docs/product/ surface deleted in ce9c97d (2026-09-07) — not introduced by this run, still unaddressed.
signoff:      HUMAN 2026-09-07 — (1) restore doc-based model as a FRESH MINIMAL SKELETON (Epic 44 only; pre-cleanup history stays deleted); (2) one Epic 44 for all four points; (3) S2 takes the full route + quant-audit. HUMAN 2026-09-08 — (4) all four stories APPROVED; (5) decision #2: fold the per-month partial-month marker INTO US-44.1 (adds schema hook); (6) US-44.4 implementation run opens with a focused quant RESEARCH pass on non-verified-benchmark return basis
route:        full
express:      no
gates:        quant-audit skipped — planning-only run, no implementation to audit (runs per-story at each US-44.x implementation; US-44.1/US-44.2/US-44.3 quant-gated, US-44.4 opens with quant RESEARCH T-44.4.0) · integration skipped — same, no build lanes ran · review skipped — the 4 story drafts went to the human approval gate (approved 2026-09-08), not the reviewer acceptance gate

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | quant | RESEARCH | quant-analyst | opus | 02-quant-research.md | DONE | — |
| 03 | product | — | producer | sonnet | 03-delivery-brief.md | PARTIAL | — |
| 04 | story | — | story-author | sonnet | 04-stories.md | DONE | — |
| 05 | story | — | story-author | sonnet | 05-stories-revision.md | DONE | — |
| 06 | docs | — | docs-engineer | sonnet | 06-docs.md | DONE | — |
| 07 | story | — | story-author | sonnet | 07-story-status.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| decision | 02,03 | 02 § Methodology gaps (a)(c)(d) | methodology-doc wording for the P1 exclude-day rule, the P2 general signed reading, and the P3 benchmark-outage rule — human ratifies at each story's implementation close-out; ACs already written to the settled quant reading | CARRIED |
| contract_note | 04-story | 04-stories.md § contract_notes | US-44.1/US-44.3/US-44.4 each move TS types + docs/contracts/dashboard-fields.md (US-44.1 + marker adds the schema hook; US-44.4 adds it via the request-shape change) — handled inside each story's implementation run | CARRIED |
| finding | 03,04 | 03 § Already covered; US-44.2 Notes | US-41.1 (deleted Backlog story — inline withheld-gap chart annotation) is adjacent to US-44.2, not a duplicate — cross-reference if US-41.1 is ever restored | CARRIED |
| conflict | 06-docs | 06-docs.md § handoff/risks | CLAUDE.md still says roadmaps are "not maintained as active documentation" and its Canonical-docs table omits epic-roadmap.md + prd/README.md — contradicts the rebuilt surface; needs a human CLAUDE.md edit (already M in the working tree) | CARRIED |
| note | 06-docs | 06-docs.md § handoff | project.md § Sources of truth is accurate as-is post-restore; optional one-line refinement noting the 2026-09-08 rebuild — non-blocking | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| decision | 03-product | human signoff 2026-09-07 | #1 plan surface — RESOLVED: restore doc-based model as a fresh minimal skeleton (Epic 44 only) |
| decision | 03-product | human signoff 2026-09-07 | #4 S2 route — RESOLVED: full route + quant-audit |
| decision | 03-product | human signoff 2026-09-07 | #8 epic scope — RESOLVED: one Epic 44 for all four points |
| decision | 03-product | human signoff 2026-09-08 + 05-story | #2 per-month disclosure marker (02 gap b) — RESOLVED: folded into US-44.1 (adds the schema hook) |
| decision | 03-product | US-44.3 T-44.3.1 (04-stories) | #3 S3 valuation calendar — RESOLVED into a tech-lead DESIGN ticket that blocks the impl tickets |
| design-note | 01-recon | US-44.3 T-44.3.1 (04-stories) | valuation_dates anchored to benchmark dates — absorbed into the US-44.3 DESIGN ticket |
| contract_note | 01-recon | 04-stories.md § contract_notes | dashboard-fields.md:105 + :98-101 reconciliations — subsumed by the 04 contract notes and US-44.1/US-44.3 ACs |
| followup | 04-story | human signoff 2026-09-08 + 05-story | US-44.4 return-basis of a non-verified benchmark — RESOLVED: US-44.4 impl run opens with a focused quant RESEARCH pass (T-44.4.0) |
| pack_correction | 03,04 | 06-docs | product.md + capabilities/story.md § Files reworded against the fresh skeleton; project.md half deferred to the CLAUDE.md/project.md conflict row |
| contract_note | 01-recon | 04-stories + 06-docs (PRD F-1/F-3) | dashboard-fields.md:105 + :98-101 reconciliations recorded as PRD findings; land at US-44.1 T-44.1.4 / US-44.3 T-44.3.5 |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 7 |
| rounds | 0 |
| by model | sonnet 6 · opus 1 |
| escalations | none — 02 opus is the quant-analyst agent's pinned default, not an escalation |
