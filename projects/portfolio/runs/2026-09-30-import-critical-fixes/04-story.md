REPORT 2026-09-30-import-critical-fixes/04
status:      DONE
verdict:     NONE

changed:
  - portfolio/docs/product/stories/US-46.1-add-statement-same-account-replaces.md — D-7 folded in: AC 10-12, persistence test entry, T-46.1.3 (renumbered 46.1.4 tests, 46.1.5 docs), open decision moved to Notes; DRAFT banner replaced by approval line
  - portfolio/docs/product/stories/US-46.3-combined-portfolio-admission-weakest-label.md — D-7 folded in: AC 13-15, persistence test entry, T-46.3.3 (renumbered 46.3.4 tests, 46.3.5 docs), open decision moved to Notes; DRAFT banner replaced
  - portfolio/docs/product/stories/US-46.4-freedom24-cost-basis-unavailable.md — D-8 folded in: malformed IB Cost Basis cell out of scope (register row at close-out), open decision resolved in Notes; DRAFT banner replaced
  - portfolio/docs/product/stories/US-46.2-freedom24-trade-dates-single-commission.md — banner replaced by approval line only (D-9); no AC, test or ticket change

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; document edits only

contract_notes:
  - US-46.1 T-46.1.3 and US-46.3 T-46.3.3 both re-derive saved combined nodes on load from stored statements; whether one shared step or one each is design's call.

pack_corrections:
  - none

handoff:
  - Stories are approved per D-9 and no BLOCKS TICKETING item remains in any of the four. Human approval is on record (D-9), so this report is a record of edits, not a new approval.
  - Frontmatter status is left at `backlog`. Pack enum is backlog/active/done/dropped, and `active` means the human pulled the work into delivery, which D-9 did not say. If the human wants active, it is a one-word change per file. Approval is recorded in each file body citing D-9, not in a status value.
  - Ticket lists now: US-46.1 T-46.1.1..46.1.5; US-46.2 T-46.2.1..46.2.4 (unchanged); US-46.3 T-46.3.1..46.3.5; US-46.4 T-46.4.1..46.4.5 (unchanged). Sequence unchanged: 46.1 || 46.2 first; 46.3 soft-after 46.1; 46.4 soft-after 46.2. Design should note 46.1.3 and 46.3.3 touch the same load path.
  - Close-out for docs lane: register a tech-debt row for the IB malformed Cost Basis cell drop (D-8); also the D-4 period-start anchoring row (already carried by T-46.2.4).
  - Non-blocking items remain listed: Freedom24/ESPP supported scope (46.1, 46.2, 46.3, 46.4); golden re-capture value confirmation (46.2).
  - I did not touch ROADMAP.md; the human runs scripts/build_roadmap.py (no new story files, so the index content is unchanged).

skill_calls:
  - none

risks:
  - US-46.1 AC 12 and US-46.3 AC 15 (saved node that cannot be re-derived: no stale figures or label shown as current, error disclosure shown) are my additions to cover the degraded case. D-7 says only "recomputed". The human may trim them.
  - US-46.3 AC 14 (load recomputation equals what adding now would show) and US-46.1 AC 11 (repeated load is stable) are consequences of D-7, but are my wording.
  - US-46.3 is now 15 ACs, over the pack's dozen. Flagged in its Notes, not split; AC 13-15 form a separable persistence concern if the human wants a split.
  - The saved-node re-derivation depends on saved workspaces retaining their stored statements. D-5 relies on the same; I did not verify the storage shape. Design must confirm, and if a saved combined node does not retain its inputs, AC 12/15 become the only outcome for those nodes.
  - "House value for approved" was read as `backlog` (see handoff). Confirm if the human meant `active`.

## Orchestrator brief
- All four stories are approved per D-9 and no BLOCKS TICKETING remains. Frontmatter status stays `backlog` (the enum has no "approved"; `active` = pulled into delivery, not stated).
- D-7 applied to US-46.1 (AC 10-12, T-46.1.3 persistence, test entry) and US-46.3 (AC 13-15, T-46.3.3 persistence, test entry); open decisions moved to Notes.
- D-8 applied to US-46.4: malformed IB Cost Basis cell drop is Out of scope; the docs lane registers the tech-debt row at close-out. No AC or ticket change.
- US-46.2 changed only in banner (approval line).
- Ticket sets: 46.1 = 5 (1.3 new), 46.2 = 4, 46.3 = 5 (3.3 new), 46.4 = 5. Ordering and dependencies as before (46.1 || 46.2; 46.3 soft-after 46.1; 46.4 soft-after 46.2).
- Non-blocking, still listed: Freedom24/ESPP supported scope; FF golden re-capture value confirmation (human re-reads, 46.2).
- My additions beyond D-7 text: 46.1 AC 12 and 46.3 AC 15 (cannot-re-derive case). Human may trim.
- 46.3 now 15 ACs (over a dozen), flagged, not split.
- Sections below: none beyond this brief; the substance is in the four story files.
- Nothing blocks dispatch to the design lane.
