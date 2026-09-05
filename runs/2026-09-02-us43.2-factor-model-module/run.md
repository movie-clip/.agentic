# RUN 2026-09-02-us43.2-factor-model-module
request:      take US-43.2 and start working on it
agentic_root: C:\projects\investments\.agentic
story:        C:\projects\investments\portfolio\docs\product\stories\US-43.2-extract-factor-model-internals.md
status:       CLOSED
next:         none — CLOSED
route:        story
express:      no
gates:        quant-research SKIP — HUMAN APPROVED 2026-09-02; skip-conditions DISCHARGED by 05 (char-diff proved byte-for-byte; no formula/floor/threshold/factor-def/trust change) · quant-audit PASS (05, anchor = git blob 6b63ae1) · integration PASS (06) · review PASS (07)
signoff:      RESEARCH-skip + AC1 amendment (selected_history_return_series stays, renamed public) + AC5 wording note + UcitsCandidateMapping added — HUMAN APPROVED 2026-09-02

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | design | DESIGN | tech-lead | sonnet | 02-technical-plan.md | DONE | — |
| 03 | backend | — | backend-engineer | sonnet | 03-backend.md | PARTIAL | — |
| 04 | test | — | test-engineer | sonnet | 04-test.md | DONE | — |
| 05 | quant-audit | AUDIT | quant-analyst | opus | 05-quant-audit.md | DONE | PASS |
| 06 | integration | INTEGRATION | tech-lead | sonnet | 06-integration.md | DONE | PASS |
| 07 | review | — | reviewer | sonnet | 07-review.md | DONE | PASS |
| 08 | docs | — | docs-engineer | sonnet | 08-docs.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| followup | 07-review | 07-review.md § risks | other five risk.py concerns still leak non-factor privates (_build_wealth_index etc.) — explicit tracked follow-up (full risk.py split), not this slice | CARRIED |
| note | 08-docs | 08-docs.md § risks | slice-log entry written without interactive-user confirmation (none available); test totals taken from gate runs | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| decision | 01-recon | 02-technical-plan.md § Cycle decision | cycle via select_history_return_series RESOLVED — option (b) |
| recon-note | 01-recon | 02-technical-plan.md § Cross-seam importers | 5 importers itemised in backend edit list T-43.2.3 |
| recon-note | 01-recon | 03-backend handoff | linalg trio moved (zero non-factor callers) — AC3 disposition recorded |
| risk | 01-recon | 02-technical-plan.md § Contract | apply_return_basis_status_* reference no moving symbol, stay in risk.py |
| contract_note | 01-recon | 03-backend contract_notes | recon's 4 contract_notes subsumed by 03's |
| partial | 03-backend | 04-test.md | suite red on 3 monkeypatch retargets + 1 docs guard — all fixed; full suite green (982 backend / 359 frontend / tsc / dead-code) |
| needs-signoff | 02-design | 05-quant-audit.md | RESEARCH-skip conditions DISCHARGED — char-diff proves byte-for-byte |
| contract_note | 03-backend | 06-integration.md | schema hook fired on return_basis.py — integration CONFIRMED no ts/contract mirror owed (grep-verified) |
| contract_note | 03-backend/06 | 08-docs.md | methodology §Statistical Factor Model repointed to analytics/factor_model.py (path text only) |
| contract_note | 03-backend/06 | 08-docs.md | system-architecture.md analytics inventory now lists analytics/factor_model.py |
| scope-gap | 03-backend/04 | 08-docs.md | SKILL.md factor_model.py row (added by 04) confirmed accurate by docs lane |
| amendment | 02-design | 08-docs.md | AC1 amendment + AC3 disposition + AC5 wording note folded into story Notes + tech-debt row |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 8 |
| rounds | 0 |
| by model | sonnet 7 · opus 1 |
| escalations | none — 05 opus is the quant-analyst agent's pinned default, not an escalation |
