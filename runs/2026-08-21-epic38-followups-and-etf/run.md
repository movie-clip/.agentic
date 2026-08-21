# RUN 2026-08-21-epic38-followups-and-etf
request:      take this points and create one epic with two stories, one ETF and
              second everything else, for now I want only created stories and
              epic and updated roadmap with any needed documentation:
              - The same cached: True bug shape exists in 4 other
              MarketDataService methods — undiagnosed, not part of this story.
              - The cache-flag fix re-derives fmp.py's internal cache-key logic
              from outside that file (scope excluded touching it) — correct for
              the primary hit/miss path, but the cleaner fix belongs in fmp.py
              itself.
              - ETF look-through (F-B) remains a known, separate, untouched gap.
              - The new financial-methodology.md section (from US-37.1) was
              written directly rather than flagged for review — worth a read
              before treating it as final.
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       DISPATCHING
next:         resolve the two open decisions in 02-delivery-brief.md § Open decisions
              (epic title; whether Story A needs quant RESEARCH first), then dispatch
route:        review
express:      no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | haiku | 01-scout.md | DONE | — |
| 02 | product | — | producer | sonnet | 02-delivery-brief.md | DONE | — |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| source | .agentic/runs/2026-08-21-sector-classification-followup/run.md | Open row (finding, CARRIED) | cached:True bug shape exists in 4 other MarketDataService methods, undiagnosed | OPEN |
| source | .agentic/runs/2026-08-21-sector-classification-followup/run.md | Open row (should_fix, CARRIED) | cache-flag fix re-derives fmp.py cache-key logic from outside; clean fix belongs in fmp.py | OPEN |
| source | docs/product/stories/US-37.1-dynamic-equity-sector-classification.md | § F-B | ETF look-through / constituent classification — known, separate, untouched gap | OPEN |
| source | user (this request) | (prior turn, US-37.1 quant-research) | financial-methodology.md section from US-37.1 written directly, not flagged for review | OPEN |
| human_decision | user | (this request) | placement: one new epic, two stories (Story A = ETF look-through F-B, Story B = everything else) | CARRIED |

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
