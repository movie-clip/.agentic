REPORT 2026-08-21-dynamic-sector-classification/16
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-37.1-dynamic-equity-sector-classification.md — Status: Backlog to Done; all 10 ACs + 4 tickets ticked (all SATISFIED per 15-review.md)
  - docs/product/stories/README.md — new "Epic 37 — Dynamic Equity Sector Classification (complete)" index section, US-37.1 row, Status: Done
  - docs/product/epic-roadmap.md — intro summary now names Epic 37 as most-recently-shipped
  - docs/product/epic-roadmap.md — new "Completed Epic: Epic 37" header + one-row story snapshot (no slice log — deferred per order)
  - docs/product/current-product-state.md — Exposure-section bullet: dynamic FMP sector classification, "Unclassified" bucket, explicit F-B (ETF look-through) exclusion

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs-only close-out, no runnable command named by the order (matches 08-docs's own precedent)

contract_notes:
  - none new — every contract_note from 02/05/06/07 already landed via 08-docs; re-confirmed against the live exposure-fields.md and financial-methodology.md text this pass

pack_corrections:
  - none

handoff:
  - Draft slice-log line (not written, per order) awaits human confirmation — see § Draft slice-log line
  - epic-37 PRD's "Status:" header still reads "Backlog" — file is outside this order's scope list, needs a follow-up touch
  - Could not run check_report.py — no Bash tool in this session; format checked manually against PROTOCOL.md § 3/§ 4 instead

risks:
  - Carried forward from 08-docs: the new methodology section was auto-written, not flagged per capabilities/docs.md's usual convention — recommend human review before final
  - docs/product/stories/US-24.12-...md tombstone still exists — no lane has a delete tool; already tracked in run.md's Open table, not attempted here
  - epic-37 PRD's stale "Backlog" header (see handoff) is the same drift class Epic 36/US-36.3 (F-R7) fixed for Epic 24's PRD — a fast follow-up avoids re-discovering it
  - No Bash/git in this session; verified the shipped code directly (equity_sector_resolution.py, registry.py) against 14-integration.md/15-review.md's claims before writing docs — matched in every case checked

## Orchestrator brief

- Story US-37.1 closed out: Status Done, all 10 ACs + 4 tickets ticked (reviewer confirmed all 10 SATISFIED, none GAP/DRIFTED).
- Epic 37 flipped to Completed in both epic-roadmap.md (header + 1-row story snapshot) and stories/README.md (index section) — single-story epic, both now agree.
- current-product-state.md gained one Exposure-tab bullet: FMP sector classification for non-registry equities, "Unclassified" bucket, explicit F-B (ETF look-through) exclusion.
- Slice-log line intentionally NOT written to epic-roadmap.md — drafted below for human confirmation before a follow-up order writes it in, per this order's explicit instruction.
- All contract_notes from every prior lane confirmed already landed (08-docs was the terminus); nothing new outstanding.
- Two carried-forward risks need human attention: the auto-written methodology section (flag-for-human bypassed by design of a prior order) and the epic-37 PRD's stale "Backlog" header (out of this order's file scope).
- Section below: § Draft slice-log line — the proposed row, plus how its test-count delta was derived.

---

## Draft slice-log line

Not written to epic-roadmap.md — per this order's explicit instruction, drafted
here for the human to confirm before a follow-up order writes it in.

| 2026-08-21 | US-37.1 | Equities outside the static registry now get identity-gated FMP sector classification (ISIN-matched against the statement, 11-entry taxonomy map); an equity nothing resolves is disclosed under a distinct "Unclassified" bucket, never "Other", weight still counted in the total. CR-1 fixed a second hardcoded "Other" in the no-imported-instrument catch-all quant-audit found (registry.py:337-346). ETF look-through constituents (F-B) explicitly out of scope. 802 → 840 backend (+38), 331 frontend unchanged; tsc + dead-code gate clean; dashboardGoldens.ts untouched. |

Backend delta derived from the roadmap's own running total (779 after US-35.3,
+10 US-36.1, +10 US-36.2, +3 US-36.3 = 802 baseline) against this run's
verified final total (840, confirmed independently by 09-test/14-integration/
15-review) — not a number this lane invented.
