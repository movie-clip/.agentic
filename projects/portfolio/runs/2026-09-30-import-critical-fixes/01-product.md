REPORT 2026-09-30-import-critical-fixes/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; no command result to report

contract_notes:
  - F4 fix crosses a contract boundary: ImportedPosition cost_basis/unrealized_pnl become Optional in schemas/imports.py, mirrored in desktop types.ts:37-39, and docs/contracts/imports-fields.md does not exist yet (register row "import boundary has no field contract").
  - F2/F3 story drafts must cite docs/contracts/import-admission-fields.md (the only imports-adjacent contract on disk) and methodology § Multi-Statement Snapshot Merge (L2328-2412) as the traceability anchors.

pack_corrections:
  - none

handoff:
  - 4 stories proposed, no epic (US-46.1 F3, US-46.2 F1, US-46.3 F2, US-46.4 F4) — see § Stories
  - order: 46.1 and 46.2 first, in parallel (different lanes/files); 46.3 after 46.1; 46.4 after 46.2 — see § Sequence
  - quant RESEARCH must answer three questions before design: F2 label rule, F3 cross-currency, F4 null-cost-basis downstream — see § Sequence
  - open decision: epic or no epic (default: no epic, series US-46) — see § Open decisions
  - open decision: 4 stories or paired into 2 (default: 4) — see § Open decisions
  - open decision: Freedom24/ESPP supported-scope question (register row, not blocking per D-1) — see § Open decisions
  - out of scope: F5-F20, the two ungraded register rows, F10/F12/F13 held for a methodology ruling — see § Already covered

risks:
  - Took on trust from 02-quant-audit.md: all F1-F4 line numbers and the TWR figures (-1.20% vs +5.89%); I did not re-open source files (pack rule: code facts come from recon/audit artifacts).
  - Verified myself: freedom24.py still holds _statement_grouped_date / GROUPED_ENTRY_DAY=1 (no fix commit since the audit), and no epics dir or US-46 story exists in git.
  - Recorded decision touched: US-14.1 (commit 4a3df95) deliberately made the overlay SUM same-symbol positions; F3 narrows this to distinct accounts only, and the tests it pinned will need to change for the same-account case.
  - Story shape is proposed against the register's F-numbers, not a story-file findings home; pack says findings live in an epic or audit story, but D-1 put them in the register, so I followed D-1.
  - F4 is weak on the Valuable criterion (audit says no current tsx renders the fabricated value); I kept it as a story because of guardrail 4 and D-1, not because a user perceives it today.

skill_calls:
  - none

## Orchestrator brief
- verdict: New story, no existing epic (no epics exist on disk; ROADMAP has 0 Active, 0 Backlog). Audit-first already satisfied by run 2026-09-29-statement-import-audit.
- epic: none recommended; use series US-46 (44.1 and 45.1 are the last on disk). Epic-or-not is an open decision, non-blocking.
- 4 stories PROPOSED: US-46.1 (F3) adding a statement no longer doubles same-account holdings on Exposure.
- US-46.2 (F1) a Freedom24 import dates its trades from the statement, so Dashboard TWR stops showing -1.20% against +5.89%.
- US-46.3 (F2) the Exposure trust label after add-statement never claims more than its weakest constituent.
- US-46.4 (F4) a Freedom24 position with no stated cost basis carries unavailable, not a fabricated cost and zero P&L.
- order: 46.1 || 46.2 first; 46.3 after 46.1; 46.4 after 46.2. Lanes: 46.1/46.3 frontend (46.3 may cross into backend admission); 46.2/46.4 backend (46.4 crosses schema and TS).
- quant RESEARCH needed before design: F2 label rule, F3 cross-currency convert-or-refuse, F4 null cost-basis effect at ledger.py:244.
- out of scope: F5-F9, F11, F14-F20 (backlog debt), F10/F12/F13 (held for methodology ruling per D-1), ungraded register rows, F7 (same lines as F1 but MATERIAL).
- blocks dispatch: nothing. Three open decisions have defaults (epic, split, Freedom24 scope).
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

No epic on disk: `docs/product/epics/` does not exist and `ROADMAP.md` shows only two shipped stories (US-44.1, US-45.1), both stand-alone with `epic: -`. So the nearest precedents are those two, which set the pattern: a story without an epic is well-formed.

The four fixes do share a rationale (the 2026-09-29 statement-import audit), but that rationale is already recorded once, in the register rows citing the run, and each story will cite its row. An epic would add a file that duplicates the register. The case for one is real but later: F5-F20 (16 findings) will need scheduling, and that is where an epic pays for itself. Recommendation: no epic now; open one when a second batch of F-findings is pulled forward. Epic placement is the owner's call, so it is listed as an open decision with this default.

Findings-first: the house pattern (epics 33/34) makes the first story an audit. That has been done outside the structure: the audit run has an examined-and-correct record (IB2026.csv, 0 mismatches over all direct fields; ESPP admitted/verified is supported). No audit story is needed; these are the "subsequent stories that close findings". Each story names its finding in its scope line.

Fresh check that these are not already fixed: `_statement_grouped_date` and `GROUPED_ENTRY_DAY = 1` are still in `freedom24.py:29,46-51`; the last commits on that file predate the audit; `overlayImportedSnapshot` last changed in US-14.1 (4a3df95) and the register rows are the only uncommitted change of substance. Not shipped, not storied.

Recorded prior decision touched: US-14.1 made the overlay SUM same-symbol positions, motivated by IB MSFT + ESPP MSFT (two different accounts). That is consistent with the methodology rule (different accounts sum). F3 narrows the behaviour: same account replaces. US-14.1 did not consider the same-account refresh case, but the human should know the fix changes two tests US-14.1 pinned (`does not duplicate symbols...`, `applies three sequential overlays...`).

## Stories

Numbering is a proposal (next free series, US-46). Story-author sets final ids.

**US-46.1 — Adding a refreshed statement from the same account no longer doubles my Exposure view.** (closes F3)
  value:      the researcher can add an updated IB YTD statement and see the correct holdings, not 2x every position and total (IB2026 twice today: MV 62,843.22 -> 125,686.44, VUAA 80 -> 160).
  slice:      in: the Exposure tab's snapshot after add-statement follows the documented merge rule (same account replaces, distinct accounts sum, missing account_id fails closed, cross-currency not summed silently). Out: any change to the backend combine, statement_totals, or TWR (F10/F12).
  depends_on: none. Quant RESEARCH on cross-currency behaviour (convert with which rates, or refuse) before design.
  invest:     Estimable is weak until design settles overlay-fix vs drive-Exposure-from-backend-combine (audit offers both); the fix choice is the tech lead's, the outcome is fixed. Must confirm the chosen path does not read the merged `statement_totals` block, or it inherits F10/F12.

**US-46.2 — A Freedom24 statement's Dashboard performance reflects the trades on the dates the statement gives.** (closes F1)
  value:      Dashboard TWR/MWR for FF2026 stops being computed on 9 VTI held from 2025-12-01 (a date before the statement period) and shows a return consistent with the statement's own +5.89% NAV return instead of -1.20%.
  slice:      in: per-trade dates parsed from the Transactions rows; unparseable rows dropped, never synthesised; the committed FF2026 golden regenerated and reviewed. Out: F7 fee double count (same code region), F8 totals, F4 cost basis.
  depends_on: none.
  invest:     Testable needs care: after F1 alone the TWR will still differ from +5.89% (audit's own true-date path is +5.77%, and F7's 6.76 remains), so ACs must not assert equality with the statement return. State a tolerance and the reason, or the acceptance will fail on a residual this story does not own.

**US-46.3 — After I add a statement, the Exposure trust label says no more than the weakest statement supports.** (closes F2)
  value:      IB (degraded) + ESPP (verified) stops showing "admitted / verified" over a portfolio that is 95% IB holdings.
  slice:      in: the persisted/displayed admission for an added-statement node is derived from all constituents (rule from quant research); never the last file's alone. Out: any change to admission rules themselves, and the multi-currency ceiling (F13).
  depends_on: US-46.1 (soft): if 46.1 drives Exposure from the backend-combined snapshot, "admission on the combined snapshot" has a natural home; otherwise weakest-of-constituents is a frontend-only rule. Quant RESEARCH must choose the rule.
  invest:     may cross into backend (`import_admission.py`) if the combined-snapshot rule is chosen; the tech lead confirms the lane split. A combined multi-currency snapshot will be `degraded` under F13 regardless: acceptable and conservative, and this story must not unlock a higher rung.

**US-46.4 — A Freedom24 position with no stated cost basis shows P&L as unavailable, not zero.** (closes F4)
  value:      the imported broker-truth block stops asserting cost basis 3,018.96 and unrealized P&L 0.00 for VTI; nothing derived from it (overview totals, top positions, the persisted override) reads a zero as broker truth.
  slice:      in: `cost_basis`/`unrealized_pnl` Optional in the schema, mirrored in desktop types and a contract doc for the touched import fields; downstream consumers handle null (unavailable), including the opening-lot estimate at `ledger.py:244`. Out: typing the two `Array<unknown>` fields in `types.ts` and covering the whole imports boundary in the contract doc, unless the tech lead finds it free.
  depends_on: US-46.2 (soft): both edit `freedom24.py`, and the ledger.py:244 consumer means null cost basis can shift Dashboard replay numbers, which would otherwise be attributed to the wrong change.
  invest:     weak on Valuable: the audit states no tsx renders the value today, so a user cannot perceive it yet. Kept as a story because guardrail 4 forbids the fabrication and D-1 named F4; its visible payoff is that persisted imports stop carrying a false zero. If the human prefers, it can merge into US-46.2 to give it a user-visible carrier (see decision 2).

## Sequence

1. **US-46.1 and US-46.2 in parallel first.** Different lanes (frontend vs backend) and disjoint files, so they can run concurrently. 46.1 is first by risk: it hits the primary broker on the normal refresh path and its design choice (overlay fix vs backend-combined view) shapes 46.3. 46.2 is independent and produces the one golden change (FF2026 TWR -1.20% -> about +5.8%) that quant-audit must inspect.
2. **US-46.3 after US-46.1** (soft edge, see above). Rewritten less if the 46.1 design lands first.
3. **US-46.4 after US-46.2** (soft edge). Serialises the two `freedom24.py` edits and separates two possible sources of Dashboard number movement.
4. **Quant RESEARCH runs before design, once, covering three questions** (this project routes formula/trust doubts to quant, not the tech lead):
   - F2: what label rule is honest for an added-statement node: weakest constituent, or admission recomputed on the combined snapshot, and what does the combined multi-currency case show given F13?
   - F3: for a cross-currency add-statement overlay, convert (with which rates and provenance) or refuse and disclose?
   - F4: with `cost_basis` null, how is the opening-lot cost estimate at `ledger.py:244` to behave, and what trust level do the dependent Dashboard numbers carry?
5. **Gates:** quant-audit on all four (a trust label, a return basis and a cost-basis field are all touched); integration for 46.4's schema crossing; a story may spawn its successor, especially 46.1 (a design that adopts the backend-combined view may surface an F10/F12 dependency).

Batching note for the orchestrator: run.md plans one story. This brief recommends four story files, one run, one approval pass; the run can still build 46.1+46.2 in a single batch.

## Open decisions

- **Epic or no epic.** Recommendation and default: no epic, stand-alone stories in series US-46, each citing its register row. Open an epic when F5-F20 are scheduled. Owner's call; not blocking.
- **Four stories or two.** Default: four (one slice, one review each). Alternative: pair F1+F4 ("Freedom24 import fidelity") and F2+F3 ("add-statement path"), which gives F4 a user-visible carrier but makes both stories big (F1+F4 crosses backend, schema, TS and a contract doc). Not blocking; the story-author can draft either.
- **Freedom24 and ESPP supported scope.** The register row (QUESTION, recon contract note 4) records that `current-product-state.md:12` lists only Interactive Brokers while the Freedom24 and ESPP importers are routed and route-tested. F1 and F4 invest in the weakest parser. D-1 already says fix the criticals, so this does not block. Default: proceed with F1/F4, and the close-out docs lane leaves the shipped-scope line for the owner. If the answer is "experimental/remove", the value of 46.2 and 46.4 changes.
- **Confirm F7 stays out although F1 edits the same lines.** F7 (the fee double count, `freedom24.py:253-256` and `:348-378`) is MATERIAL and out of scope, but 46.2 edits `:236-280` and `:348-378`. Default: leave it and record the residual in 46.2's ACs; pulling it in is a scope call for the human.

## Already covered

Nothing here is shipped or storied: `ROADMAP.md` has no Active or Backlog rows, `freedom24.py` still contains the fabricated-date function, and no US-46 file exists in Git history.

**Explicitly out of scope for this batch**
- F10, F12, F13: held for a methodology-owner ruling (D-1 note; register rows say "no lane should open an engineering change request without that ruling"). Interaction to watch: 46.1 must not depend on merged totals or `starting_nav` (F10/F12); 46.3 must not raise any rung (F13).
- MATERIAL, Medium-priority register rows: F5 (Forex ledger rows dropped), F6 (Corporate Actions), F7 (Freedom24 fee double count), F8 (Freedom24 statement_totals), F9 (reconciliation unwired), F11 (None->0 opening-state upgrade).
- MINOR, Low-priority register rows: F14-F20 (description false positives, tax abs, stale doc figures, ESPP inferred entries, PDF EUR regex, cross-listed identity, reconciliation deposits), F16 is a methodology-doc edit.
- Ungraded register rows: `realized_cash_flow` untraceable, and the imports field-contract gap (only the part the F4 schema change needs is in 46.4).
- The register's product-scope question on Freedom24 and ESPP (see § Open decisions).
- Not covered by the register but noted: no UI click-through was done by the audit for F2/F3 (proved by executing the overlay function on real importer output), so the story's tests should include a UI-level path, not only the function.
