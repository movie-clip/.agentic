REPORT 2026-09-30-import-critical-fixes/03
status:      DONE
verdict:     NONE

changed:
  - portfolio/docs/product/stories/US-46.1-add-statement-same-account-replaces.md — new draft (F3), 9 ACs, 4 tickets, status backlog
  - portfolio/docs/product/stories/US-46.2-freedom24-trade-dates-single-commission.md — new draft (F1+F7), 14 ACs, 4 tickets, status backlog
  - portfolio/docs/product/stories/US-46.3-combined-portfolio-admission-weakest-label.md — new draft (F2), 12 ACs, 4 tickets, status backlog
  - portfolio/docs/product/stories/US-46.4-freedom24-cost-basis-unavailable.md — new draft (F4), 12 ACs, 5 tickets, status backlog

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; drafts only, no command run

contract_notes:
  - US-46.4: ImportedPosition cost_basis/unrealized_pnl and overview totals/top_positions P&L become nullable (schemas, desktop types.ts); docs/contracts has no imports contract file, so T-46.4.5 creates one.
  - US-46.3: docs/contracts/import-admission-fields.md needs a combined-snapshot section; the add-statement combine response must carry a combined admission (shape is design's).
  - US-46.1/46.2/46.3/46.4: methodology edits E3, E1, E2, E4 from 02-quant.md respectively are carried as docs tickets; none applied by this lane. E5 (period-start anchoring) is not drafted per D-4.
  - US-46.2: apps/desktop/src/test/dashboardGoldens.ts (FF block) and app/scripts/golden_market_data.json need a live re-capture with FMP_API_KEY; not runnable in the frozen suite.

pack_corrections:
  - none

handoff:
  - Story files are in portfolio/docs/product/stories/ with status backlog, no epic; the human must run scripts/build_roadmap.py after approval (I did not touch ROADMAP.md).
  - Ticket order: 46.1 and 46.2 first in parallel; 46.3 soft-after 46.1; 46.4 soft-after 46.2. Ticket lists are in each story's § Tickets.
  - Blocks ticketing (human): US-46.1 and US-46.3 saved-workspace behaviour before the fix (D-5 covered F4 only); US-46.4 malformed IB Cost Basis cell drops the position. See § Open decisions in each story.
  - Human step: the FF golden re-capture needs FMP_API_KEY and probably --allow-smaller-capture (T-46.2.3); pinned values are frozen-price numbers to be re-read from the regenerated golden.
  - Docs lane at close-out: record period-start replay anchoring (D-4) in docs/tech-debt-register.md; T-46.2.4 carries it.
  - Route N1 (monthly returns include the reconciliation adjustment) to a quant-audit order or the register; it is named out of scope in US-46.2.

skill_calls:
  - write-story — not called, this lane has no Skill tool; conventions taken from capabilities/story.md and US-45.1

risks:
  - AC 8 of US-46.3 (constituent statement labels visible beside the combined label) is my reading of E2's "constituent evidence is kept alongside the roll-up". It adds UI; the human may trim it.
  - US-46.3 AC 7 (superseded same-account statement still counts) follows 02-quant.md's stated sub-decision "all inputs"; D-3 wording ("each statement's own admission") supports it but did not name it explicitly.
  - US-46.1 AC 8 (no silent cross-currency sum) rests on the backend refusing base-currency mismatch and keying by symbol and currency, per 02-quant.md § F3; I did not re-execute it.
  - US-46.4 AC 7 states request-path (added-node) Exposure cost basis/P&L become unavailable per E4; this also changes IB Exposure for added nodes, where today it shows market-value cost and 0 P&L.
  - US-46.2 is 14 ACs, over the pack's dozen; I flagged rather than split (pack: splitting is the producer's call). Reason: each pinned number is its own assertion.
  - 01-product.md numbers the stories F3=46.1, F1=46.2 in its handoff but its § Stories section lists F3 first as 46.1 as well; the order's numbering was used and is consistent.
  - Valuable criterion for US-46.4 is weak (no tsx renders the value today); stated in its Context rather than hidden.

## Orchestrator brief
- Four DRAFT stories written, status backlog, no epic: US-46.1 (F3), US-46.2 (F1+F7), US-46.3 (F2), US-46.4 (F4). None approved; human approval required.
- Decisions applied as binding: D-2 F7 in 46.2 (TWR 3.81%, trust degraded, window 2026-03-31..04-10); D-3 weakest-of-all+recompute in 46.3; D-4 anchor kept; D-5 recompute on load in 46.4; D-6 split.
- Expected numbers pinned: FF 3.81/3.81 TWR/MWR, 2,955.01 -> 3,071.00, gain 112.48, excess -0.67; IB re-add 18 / 62,843.22 / VUAA 80; IB+ESPP and FF+ESPP degraded/degraded; FF cost basis null+unavailable, incl. portfolio_snapshot_builder.py.
- Sequence: 46.1 || 46.2 first; 46.3 soft-after 46.1; 46.4 soft-after 46.2. Gates: quant-audit on all, integration on 46.4.
- Lanes: 46.1 frontend(+backend per design); 46.2 backend+test(+human FMP capture); 46.3 backend+frontend; 46.4 backend+schema+frontend; docs ticket in each (E3/E1/E2/E4).
- Blocks ticketing (human rulings needed): (1) saved workspaces before fix for 46.1 and 46.3 (default assumed: untouched); (2) IB malformed Cost Basis cell drop for 46.4 (default: out of scope).
- Non-blocking: Freedom24/ESPP supported scope; golden re-capture may move 3.81 slightly (human re-reads).
- Golden refresh needs FMP_API_KEY, a human-run step (T-46.2.3).
- Out of scope named: F10/F12/F13, D-4 period-start anchoring, N1, F5-F9, F11, F14-F20.
- Sections below: Story index (paths, ACs, tickets per story) · Open questions (for the human, none decided by this draft).

## Story index

| Story | Finding | File | ACs | Tickets |
|---|---|---|---|---|
| US-46.1 | F3 | portfolio/docs/product/stories/US-46.1-add-statement-same-account-replaces.md | 9 | T-46.1.1 .. T-46.1.4 |
| US-46.2 | F1 + F7 | portfolio/docs/product/stories/US-46.2-freedom24-trade-dates-single-commission.md | 14 | T-46.2.1 .. T-46.2.4 |
| US-46.3 | F2 | portfolio/docs/product/stories/US-46.3-combined-portfolio-admission-weakest-label.md | 12 | T-46.3.1 .. T-46.3.4 |
| US-46.4 | F4 | portfolio/docs/product/stories/US-46.4-freedom24-cost-basis-unavailable.md | 12 | T-46.4.1 .. T-46.4.5 |

Each ticket set orders any contract or backend change before its consumer, has
tests as their own ticket, and ends with a docs reconciliation ticket. No ticket
instructs a commit, a suite run or a self-gate.

## Open questions

1. Saved workspaces holding a doubled combined node (46.1) or a last-file-only
   admission label (46.3): leave untouched (assumed) or recompute on load? D-5
   covered only the F4 cost-basis values.
2. IB importer drops a whole position when its Cost Basis cell is malformed
   (interactive_brokers_csv.py:275-289). Fix in 46.4 or register separately?
   Assumed: separately.
3. Does the regenerated FF golden, after the live FMP re-capture, still show
   TWR 3.81% and excess -0.67pp? The story pins the frozen-price values; a
   different re-captured value needs a human decision before it becomes golden.
4. Freedom24 and ESPP supported scope (register question): unchanged default,
   proceed.
5. US-46.3 AC 8 (constituent labels visible in the review): keep or trim.
