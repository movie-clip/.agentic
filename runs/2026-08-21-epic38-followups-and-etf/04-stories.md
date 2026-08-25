REPORT 2026-08-21-epic38-followups-and-etf/04
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-38.1-etf-lookthrough-sector-classification.md — new story, drafted, Status: Backlog
  - docs/product/stories/US-38.2-market-data-cache-diagnostic-accuracy.md — new story, drafted, Status: Backlog

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only drafting order; no code/test/build command applies

contract_notes:
  - docs/contracts/exposure-fields.md:203-209 (lookthrough_sector_exposure rows) needs an "Unclassified" row once US-38.1 ships, mirroring lines 216-219
  - docs/tech-debt-register.md:177 cites risk.py:1485-1499,1537-1549; current lines are 1613-1627/1665-1677 — US-38.1's T-38.1.3 tickets this correction
  - US-38.2 introduces no new field/schema — `cached` already exists on `last_fetch_meta`; this is a correctness fix, not a contract change

pack_corrections:
  - none

handoff:
  - US-38.1 (docs/product/stories/US-38.1-etf-lookthrough-sector-classification.md) — ETF look-through sector classification, 7 ACs, 4 tickets
  - US-38.2 (docs/product/stories/US-38.2-market-data-cache-diagnostic-accuracy.md) — cache-diagnostic accuracy, 8 ACs, 3 tickets
  - US-38.1 open decision #1 — epic title wording is a proposed working title only, human must confirm or replace
  - US-38.1 open decision #2 — whether "Unclassified" is exempt from MIN_SECTOR_WEIGHT suppression, unresolved per quant brief's own flag
  - US-38.1 open decision #3 — whether the 8-ticker companion registry curation ships inside this story or as a fast-follow
  - US-38.2 has no open decisions — both findings were fully diagnosed by the delivery brief with a corrected 5-method/6-site count
  - both stories are structurally independent; delivery brief's § Sequence recommends B (US-38.2) before A (US-38.1) but names no hard dependency
  - neither story's epic (Epic 38) exists yet in epic-roadmap.md or the story index — docs-engineer creates both, and the PRD, only after human approval

risks:
  - both stories assume the delivery brief's proposed Epic 38 title and two-story placement; if the human places this work differently, both story headers need a docs-lane correction
  - US-38.1's AC7 (factor-tilt fidelity) is phrased to accept, not block, a legitimate value shift toward 0.0 for uncurated proxy tickers — flagging in case the human reads it as under-specified rather than deliberate
  - US-38.2's INVEST "Value" criterion is the weaker of the two per the delivery brief's own framing (internal/diagnostic, no end-user surface) — reproduced verbatim in the story rather than resolved by this draft
  - I did not verify the exact current line numbers inside get_etf_holdings_for_date beyond what 02/03 already cited — if they have drifted since those briefs were written, T-38.2.1's implementer should re-confirm against live code

## Orchestrator brief

- both stories drafted as Backlog, ready for human review before any DESIGN/RESEARCH dispatch
- decision carried, not made: US-38.1's aggregation rule is the quant research brief's rule verbatim (per-source-slice, Unclassified never pro-rated/dropped) — see US-38.1 § Context
- decision carried, not made: US-38.2 uses the delivery brief's corrected 5-method/6-call-site list, not US-37.2's undercounted "4 methods"
- blocks dispatch: US-38.1's three open decisions (epic title, suppression-threshold exemption, companion-curation timing) — human and/or tech-lead DESIGN must resolve before ticketing
- US-38.2 has no blocking open decisions and could go to tech-lead DESIGN or straight to backend-engineer once epic placement is confirmed
- sections: see § handoff above for story paths, AC/ticket counts, and the sequence note (B before A recommended, not required)
- neither story touches epic-roadmap.md, current-product-state.md, or a PRD — those remain the human's/docs-engineer's close-out work
