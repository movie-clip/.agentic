# RUN 2026-09-01-perf-benchmark-vs-statement
request:      analyze and tell me if Performance & Benchmark chart is showing
              correct information when IB2026.csv file is imported, it should
              match the statement itself data
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
route:        audit
express:      no
gates:        quant-audit PASS · integration skipped (audit route, zero code/doc changes) · review skipped (no story to accept)

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | quant-audit | AUDIT | quant-analyst | opus | 01-quant-audit.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| finding | 01-quant-audit | § Answer | Chart portfolio line ends +1.11% vs statement TWR +5.51% (4.40pp gap); correct + labelled degraded/"Replay-derived"; gap = ~2.79pp pre-window week (replay starts 2026-01-08 vs statement 2026-01-01) + ~1.49pp 4 withheld days | CARRIED (to user — by-design, no fix requested by gate) |
| finding | 01-quant-audit | § risks | Whether "Replay-derived" label communicates a ~5x understatement strongly enough is a producer/UX judgment, not a math call | CARRIED (to user — producer scope) |
| finding | 01-quant-audit | § FINDING 1 | financial-methodology.md ~20 IB2026-pinned illustrative figures stale (says published 2.43%/impact 1.80pp; current 1.11%/1.49pp) — statement-refresh workflow does not cover methodology figures, systemic drift | CARRIED (to user — needs a docs run + refresh-checklist change) |
| finding | 01-quant-audit | § FINDING 2 | methodology §Indexed Return Series Implementation list omits performance.py::build_true_performance_series + PerformanceBenchmarkCard.tsx | CARRIED (already tracked in docs/tech-debt-register.md from 2026-08-26 run) |
| context | orchestrator | git status | statement refresh in flight — working tree (CSV, goldens, statement_truths.py) internally consistent, targeted suites green; audit ran against that tree | CLOSED (audit confirmed consistency, § Goldens freshness) |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 1 |
| rounds | 0 |
| by model | opus 1 |
| escalations | none |
