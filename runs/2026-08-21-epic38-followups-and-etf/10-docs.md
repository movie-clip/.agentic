REPORT 2026-08-21-epic38-followups-and-etf/10
status:      PARTIAL
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — appended "### ETF look-through constituent classification (US-38.1)" subsection under the existing "## Sector/Industry Classification — Source and Resolution (US-37.1)" section
  - docs/contracts/exposure-fields.md — Look-through sector section (sector labels/market value/weight rows) now documents the "Unclassified" bucket, mirroring the current-state-concentration rows
  - docs/tech-debt-register.md:177 — corrected drifted line-number citation and marked the row RESOLVED (US-38.1 / Epic 38, F-B), noting the narrower ETF-side-FMP-reliability part of F-B remains open

verification:
  command:   NONE (no Bash tool granted to this lane; could not run detect_deadcode.py or grep myself — verified the tech-debt-register fix by reading the edited file back)
  result:    NOT_RUN
  detail:    docs-only changes; order named a verification command this lane has no tool to execute — orchestrator/human must run `cd services/quant-engine && python scripts/detect_deadcode.py --strict` and `grep -n "1485-1499\|1537-1549" docs/tech-debt-register.md` to confirm

contract_notes:
  - none — this order absorbed the two contract notes emitted by 03-quant-research.md and 09-backend.md (exposure-fields.md prose, tech-debt-register.md citation); nothing new introduced

pack_corrections:
  - none

handoff:
  - the "Unclassified" bucket's MIN_SECTOR_WEIGHT (0.05%) suppression exemption applies only to `build_lookthrough_sector_exposure`; `_build_shared_sector_overlap` has no suppression filter of any kind (confirmed by reading risk.py:1648-1686) — documented accordingly, not stated as symmetric
  - methodology-doc subsection names `_fund_category_proxy_sector` (risk.py:1633) as a helper the draft research brief predated — verified against landed code, not invented
  - the register row's pre-fix location was cited as risk.py:1613-1627,1665-1677 (the code's location just before T-38.1.1 deleted it), since the functions no longer exist to cite a current location for

risks:
  - this order instructed writing new methodology-doc prose directly (docs/finance/financial-methodology.md), which the docs capability pack (capabilities/docs.md "Auto-update vs flag-for-human") designates flag-for-human, not auto-write, because formula phrasing and edge-case framing are judgment calls the methodology doc's role as source of truth requires a human to review — I followed the order's explicit instruction (it names the exact draft text and the exact insertion point, already human-legible via 03-quant-research.md) but the section should be treated as provisional until a human confirms it, not silently DONE; flagging per protocol's own worked example of this exact conflict shape (PROTOCOL.md §3, "the lane wrote it — correctly flagging the conflict, but reporting DONE")
  - could not run this lane's named verification command (no Bash tool); the grep check I could do by eye (Grep tool) came back clean — see verification.detail
