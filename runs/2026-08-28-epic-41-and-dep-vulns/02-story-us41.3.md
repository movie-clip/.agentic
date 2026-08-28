REPORT 2026-08-28-epic-41-and-dep-vulns/02
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md — new drafted story: 6 item ACs + a suite-green AC, 3 firm tickets + 1 DESIGN-conditional test ticket, test plan, Open decisions, Notes

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only drafting order; no verification command named. Story is a draft for human review, not an approved story.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - story path: docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md — Epic 41, Status "Next phase", PRD referenced at expected path docs/product/prd/epic-41-documentation-and-roadmap-accuracy-reconciliation.md (docs lane writes it at close-out)
  - tickets: T-41.3.1 docs reconciliation (items 2/4/5/6, AC2/AC4/AC5/AC6); T-41.3.2 verify DriftWindow TS columns vs types.ts (item 1, AC1, frontend-or-test lane); T-41.3.3 current-product-state.md body re-audit (item 3, AC3, its own ticket, quant-referral branch); T-41.3.4 conditional roadmap-ordering guard (only if DESIGN elects)
  - open decision (does not hard-block): whether US-41.3 ships a re-drift guard test for epic-roadmap.md section ordering — left to tech lead at DESIGN per 01-delivery-brief.md § Open decisions; T-41.3.4 exists only if yes
  - open decision (branch, not resolvable up front): item 3's body re-audit may surface a stale methodology/trust claim in current-product-state.md — if so it routes to the quant lane as a finding, not edited in this story
  - open decision (soft dependency): Epic 41's PRD does not exist yet — docs lane writes it at close-out; F-n references and the header PRD path resolve against it once written
  - not this story's to resolve: Epic 41 charter / US-41.1 placement — owner decision tracked in 01-delivery-brief.md § Open decisions

risks:
  - Status set to "Next phase" per the work order DoD; the story pack default absent explicit human pull-in is "Backlog". Flagged as a draft pending owner approval in the story header and Notes. The pack convention is not broken, only the stricter default not applied.
  - The six items' factual particulars (types.ts L~1519 for DriftWindow, correlation-fields.md L84 citation, RollingRiskPoint in reconciliation.py, roadmap Epic 25/23/24 ordering, currency-risk-fields.md exists) are taken from 01-delivery-brief.md and 02-scout.md as authoritative; not independently re-verified against the live files this run.
  - Item 6 (AC6) is deliberately open-ended — the live residue list from 02-scout.md § B–G is to be re-confirmed at implementation time, since 01-delivery-brief.md § "Already covered" shows some sub-items already closed by US-41.2 and run-2026-08-27 docs passes. If the docs lane finds nothing left open, AC6 is satisfied by recording that.
  - PRD slug in the header (epic-41-documentation-and-roadmap-accuracy-reconciliation.md) is a guess at the expected path; the docs lane sets the real slug at close-out.

## Orchestrator brief

- Decision: drafted US-41.3 as a six-item doc-reconciliation bundle under Epic 41, sibling shape to US-32.3 / US-36.3. Number follows US-41.1/US-41.2, no rename.
- Decision: Status "Next phase" per the work order DoD; story is a draft pending owner approval (said plainly in the story and this report).
- Decision: did NOT resolve the guard-test question, the item-3 quant-referral branch, or the missing Epic 41 PRD — all reproduced in the story's `## Open decisions`. None hard-blocks ticketing.
- Decision: 3 firm tickets + 1 DESIGN-conditional test ticket. Lane split — T-41.3.1 docs; T-41.3.2 frontend-or-test; T-41.3.3 docs (own ticket, unbounded item, quant-referral branch); T-41.3.4 test, conditional.
- No AC specifies a schema field name, type, or function signature; carried facts (RollingRiskPoint module, DriftWindow location) are cited as constraints, not promoted to contract.
- Story file: docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md — the deliverable; full text reproduced below.
- Blocks dispatch: nothing hard. Owner should approve the draft; the guard-test question is a DESIGN input.
- Sections below: the full drafted story — Story · Context · Acceptance criteria (AC1–AC7) · Test plan · Tickets (T-41.3.1–T-41.3.4) · Out of scope · Open decisions · Notes / decisions.

---

## Drafted story (full text — also written to docs/product/stories/US-41.3-status-and-navigation-doc-reconciliation.md)

# US-41.3: The agent-facing status and navigation docs match the roadmap, git and the shipped code

**Epic:** 41 — Documentation & Roadmap Accuracy Reconciliation
**PRD:** `../prd/epic-41-documentation-and-roadmap-accuracy-reconciliation.md`
— the docs lane writes this PRD at close-out (run `2026-08-28-epic-41-and-dep-vulns`
§ "Epic 41 setup"); the final slug is the docs lane's, and the `F-n` finding
references in this story resolve against it once written. See `## Open decisions`.
**Status:** Next phase
**Last updated:** 2026-08-28

**Draft for human review.** Authored by the `story-author` lane from
`01-delivery-brief.md` § "Stories" (Story A — US-41.3), § "Sequence" and
§ "Open decisions" of run `2026-08-28-epic-41-and-dep-vulns`, and the carried
follow-ups in run `2026-08-27-next-epic-or-story` (`run.md` § "Open", CARRIED
rows; `02-scout.md` § B–G). Not yet approved. The `US-41.3` number follows
US-41.1 (Backlog) and US-41.2 (Done) under Epic 41 — no file rename.

## Story

As an **agent or developer** who reaches for `docs/product/stories/README.md`,
`docs/product/prd/README.md`, `docs/product/current-product-state.md`,
`docs/product/epic-roadmap.md`, `CLAUDE.md`'s "Where to find what" doc map, or a
contract-doc `**Backend schema:**` citation header to orient before doing work,
I want each of those to state something that matches the roadmap, git history and
the shipped code — not a stale pointer, date, ordering or citation — so that I
plan against the product that exists rather than one the docs describe.

## Context

Run `2026-08-27-next-epic-or-story` was a between-epics documentation health
review. Its largest finding (`system-architecture.md` ~30 epics stale) shipped as
**US-41.2** with a mechanical guard. Its exhaustive 12-contract × 20-schema field
diff also completed that run (`correlation-fields.md` + `diagnostics-fields.md`
corrected for field drift). What remains is a bundle of six smaller
reconciliations with no epic home until now:

1. `docs/contracts/correlation-fields.md`'s `DriftWindow` table and its relocated
   `coverage` row carry TS-type columns that were added from the schema but never
   checked against `apps/desktop/src/features/portfolio/types.ts` (which has
   `DriftWindow` at ~L1519 and `coverage` present).
2. `correlation-fields.md` (L84) and `factor-drift-fields.md` each have a
   `**Backend schema:**` header line that cites an analytics *builder function*
   (`analytics/risk.py` — `build_rolling_risk_series`) rather than the module
   where the cited Pydantic model class (`RollingRiskPoint`) is actually defined
   (`reconciliation.py`).
3. `current-product-state.md`'s header now asserts "body current through Epic 40"
   but that rests on run-2026-08-27 spot-checks, not a fresh line-by-line audit.
4. `epic-roadmap.md`'s per-epic sections are in a non-monotonic order (the brief
   notes Epic 25 at ~L1250, Epic 23 at ~L1291, Epic 24 at ~L1343).
5. `CLAUDE.md`'s "Where to find what" doc map has no row for
   `docs/contracts/currency-risk-fields.md` (the file exists; only the map row is
   missing).
6. Any remaining pointer / label / date / citation residue that run
   2026-08-27 `02-scout.md` § B–G caught and that US-41.2 and that run's docs
   passes did not already fix.

Precedent for the story shape (a doc-accuracy reconciliation bundle closing a
health-review's carried follow-ups): **US-32.3** and **US-36.3**. Like those, the
beneficiary is an agent/developer navigating the repo, not the researcher; the
concrete, checkable deliverables are the specific doc end-states below.

Implementer must read:
- `01-delivery-brief.md` § "Stories" (Story A — US-41.3), § "Open decisions"
  (run `2026-08-28-epic-41-and-dep-vulns`) — scopes this story, records what is
  already partly closed, and leaves the guard-test question open.
- `02-scout.md` § B–G (run `2026-08-27-next-epic-or-story`) — the source list of
  pointer/label residue, with line ranges.
- `run.md` § "Open" (same run) — the eight CARRIED rows naming these items.
- `docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md`
  — the sibling story shape and the immediately-prior Epic 41 story.

## Acceptance criteria

- [ ] **AC1 — The correlation-fields DriftWindow TS columns match the shipped
  type.** Every TS-type column entry in `docs/contracts/correlation-fields.md`'s
  `DriftWindow` table and its relocated `coverage` row matches the corresponding
  declaration in `apps/desktop/src/features/portfolio/types.ts`. Where a column
  was wrong it is corrected; where the table was already right, `## Notes /
  decisions` records it as confirmed-correct against `types.ts` with the date.

- [ ] **AC2 — Contract-doc schema citations name the defining module.** In
  `docs/contracts/correlation-fields.md` and
  `docs/contracts/factor-drift-fields.md`, every `**Backend schema:**` header
  line names the file that actually contains the definition of the Pydantic
  model class it cites, so a reader following the citation lands on the class
  definition. In particular, the line citing `RollingRiskPoint` names
  `reconciliation.py`, not `analytics/risk.py`. (A reference to the analytics
  builder function may remain alongside the class citation, but not in place of
  it.)

- [ ] **AC3 — current-product-state.md's body is re-audited against shipped
  code.** The body of `docs/product/current-product-state.md` has been read
  line-by-line against the shipped code, and the story records the outcome as
  either (a) the body is confirmed accurate as of the audit date, noted in
  `## Notes / decisions`, or (b) an itemised list of each discrepancy found. Any
  discrepancy that is a methodology or trust-semantics claim is recorded as a
  finding routed to the quant lane and is **not** edited in this story; only
  non-methodology factual staleness (dates, epic references, shipped-feature
  descriptions with no trust claim) is corrected here.

- [ ] **AC4 — epic-roadmap.md's epic sections are in one consistent order.**
  `docs/product/epic-roadmap.md`'s per-epic sections appear in a single
  consistent order (matching the majority convention already in the file). The
  sections the brief flags as out of place — Epic 25, Epic 23, Epic 24 — sit in
  sequence with their neighbours; no per-epic section is out of order relative to
  that convention. No slice-log content is lost or reworded in the move.

- [ ] **AC5 — CLAUDE.md's doc map lists currency-risk-fields.md.** `CLAUDE.md`'s
  "Where to find what (canonical doc map)" table contains a row for
  `docs/contracts/currency-risk-fields.md`, consistent in form with the existing
  dedicated row for `docs/contracts/risk-fields.md`, describing what that
  contract doc covers.

- [ ] **AC6 — No stale pointer/label residue from the 2026-08-27 review
  remains.** Every pointer, label, date, ordering or citation item identified in
  run `2026-08-27-next-epic-or-story` `02-scout.md` § B–G that was not already
  fixed by US-41.2 or that run's docs passes is corrected, so that
  `docs/product/stories/README.md`, `docs/product/prd/README.md` and the doc-map
  pointers read a state consistent with `epic-roadmap.md` and git. The live
  remaining list is confirmed against the current repo at ticketing/
  implementation time; an item already closed by earlier work needs no action and
  is recorded as already-closed in `## Notes / decisions`.

- [ ] **AC7 — The full suite is green.** `python scripts/run_all_tests.py` exits
  0 (backend pytest, desktop vitest, `tsc --noEmit`, dead-code strict gate) with
  all changes in place.

## Test plan

Most items are documentation edits to non-`.md`-guarded prose and carry no test.
Two touch points have a mechanical angle:

Backend (pytest):
- **Roadmap section ordering (item 4 / AC4).** This is the only mechanically
  guardable item — an assertion that `epic-roadmap.md`'s per-epic section
  headings are in the file's consistent order, with a non-vacuous-scan check
  (fail loudly if the heading regex stops matching), in the manner of
  `test_route_inventory.py`'s `test_the_scan_is_not_vacuous`. **Whether this
  story ships that guard at all is left to the tech lead at DESIGN** (see
  `## Open decisions`) — US-32.3 shipped no new test, US-36.3 did, and US-41.2
  already added this epic's architecture-doc guard. If DESIGN elects to ship it,
  it is its own test ticket, added at that point.
- The existing doc-path / inventory guards (`test_docs_paths.py`,
  `test_route_inventory.py`,
  `test_architecture_doc_route_inventory.py`) stay green.

Frontend (vitest):
- **DriftWindow contract columns (item 1 / AC1)** is a verification task against
  `apps/desktop/src/features/portfolio/types.ts`, not necessarily a new test. If
  an existing contract/type-consistency test already covers the `DriftWindow` /
  `coverage` shape, note that; a new assertion is only warranted if the check is
  otherwise unguarded and cheap to encode.

Regression / guardrail:
- No engine, analytics, schema, contract *field* or trust behaviour changes in
  this story, so goldens are expected byte-identical (US-32.3 precedent) and no
  methodology or contract test should move.
- If the item-3 body re-audit surfaces a stale methodology or trust claim in
  `current-product-state.md`, **stop** — that is a finding routed to the quant
  lane, not a doc edit made here.

## Tickets

Only the first three are firm; T-41.3.4 is conditional on a DESIGN decision.

- [ ] **T-41.3.1 — Docs reconciliation for items 2, 4, 5, 6 (docs lane).**
  Correct the `**Backend schema:**` citation lines in `correlation-fields.md` and
  `factor-drift-fields.md` to name the class-defining modules (AC2); put
  `epic-roadmap.md`'s per-epic sections into the file's consistent order without
  losing slice-log content (AC4); add the `currency-risk-fields.md` row to
  `CLAUDE.md`'s doc map (AC5); confirm the live remaining `02-scout.md` § B–G
  residue against the current repo and correct what is still open, recording
  already-closed items (AC6). Traces AC2, AC4, AC5, AC6.

- [ ] **T-41.3.2 — Verify the correlation-fields DriftWindow TS columns
  (frontend or test lane).** Compare `correlation-fields.md`'s `DriftWindow`
  table and relocated `coverage` row, column by column, against
  `apps/desktop/src/features/portfolio/types.ts`; correct the doc where it
  disagrees, or record it confirmed-correct with the date. Note whether an
  existing test already guards this shape. Traces AC1.

- [ ] **T-41.3.3 — Re-audit current-product-state.md's body (docs lane).** Read
  the body once, line-by-line, against shipped code. Correct non-methodology
  factual staleness in place. For any discrepancy that is a methodology or
  trust-semantics claim, do not edit it — record it as a finding for the quant
  lane and surface it to the orchestrator. Record the audit outcome (clean, or
  the discrepancy list) in `## Notes / decisions`. Traces AC3. This is the
  story's only unbounded item — its size is "read the body once".

- [ ] **T-41.3.4 — (conditional) Roadmap section-ordering guard (test lane).**
  Only if the tech lead elects at DESIGN to ship a re-drift guard for item 4: add
  a pytest assertion that `epic-roadmap.md`'s per-epic section headings are in the
  file's consistent order, with a non-vacuous-scan check. May be dropped per the
  open decision below. Traces AC4.

No ticket instructs anyone to commit, to run a gate on its own output, or to
mark its own work done — the human runs the suite and commits; the orchestrator
dispatches the gates.

## Out of scope

- The exhaustive 12-contract × 20-schema field diff — completed in run
  `2026-08-27-next-epic-or-story` (`run.md` Closed table).
- `docs/architecture/system-architecture.md` — shipped as US-41.2.
- `docs/finance/financial-methodology.md`'s withholding / terminal-day rule —
  confirmed internally consistent in runs 2026-08-26 and 2026-08-27; not reopened
  here.
- Any behaviour, schema, analytics, contract-field or trust-classification
  change. A stale methodology/trust claim found during item 3 is a quant-lane
  finding, not a doc edit made in this story.
- Writing or restructuring `epic-roadmap.md`'s slice log / snapshot beyond the
  section-ordering fix, the story index `README.md`'s epic grouping, or the
  Epic 41 PRD — the docs lane owns those at Epic 41 close-out (run
  `2026-08-28-epic-41-and-dep-vulns` § "Epic 41 setup").
- `CLAUDE.md`'s Epic-34 "most-recently shipped" pointer — stale in the literal
  number but hedged by design (US-32.3); surfacing it, not scheduling it.
- US-41.1, US-41.2, and anything about Story B (dependency-vulnerability
  remediation) or Epic 42.

## Open decisions

None of these hard-block ticketing, but each must be handled consciously.

- **Does this story ship a re-drift guard test?** Per `01-delivery-brief.md`
  § "Open decisions", whether US-41.3 ships a one-item guard for the
  `epic-roadmap.md` section ordering (item 4) is left to the tech lead at DESIGN —
  not decided in this story. US-32.3 shipped none; US-36.3 shipped one; US-41.2
  already added this epic's architecture-doc guard. T-41.3.4 exists only if
  DESIGN says yes. Not a blocker either way.

- **Item 3 may spawn a quant-lane referral mid-implementation.** The
  `current-product-state.md` body re-audit (T-41.3.3 / AC3) may surface a stale
  methodology or trust-semantics claim. If it does, that specific claim routes to
  the quant lane as a finding and is not edited in this story; the rest of the
  story proceeds without it. This cannot be resolved up front — it is a branch,
  flagged so it is not a surprise.

- **Epic 41's PRD does not exist yet.** The docs lane writes
  `docs/product/prd/epic-41-<slug>.md` at Epic 41 close-out, folding run
  2026-08-27 `02-scout.md` § A–I into `F-1..F-n`. Until then, any `F-n` finding
  reference in this story resolves against that PRD once written, and the PRD
  path in this file's header is the expected path, not a confirmed one. The story
  can be ticketed from the briefs alone; this is a soft dependency.

- **Epic 41 charter / US-41.1 placement.** Whether Epic 41's charter line should
  be widened to acknowledge US-41.1 (a Dashboard-trust feature, not doc-accuracy
  work) as a carried story is an owner decision tracked in
  `01-delivery-brief.md` § "Open decisions" — it is the docs lane's / owner's
  concern at Epic 41 setup, not US-41.3's, and does not block this story.

## Notes / decisions

- **Why a bundle and not six one-line edits.** Five of the six items have a
  single unambiguous correct end-state. Item 3 (the body re-audit) does not —
  its size is "read the body once" and it may branch to quant. That is the
  honest reason this is a reconciliation story with a test plan rather than a
  docs-lane label-correction pass. Same call as US-32.3 / US-36.3.
- **What is already partly closed** (per `01-delivery-brief.md` § "Already
  covered", verified that run): `docs/contracts/currency-risk-fields.md` already
  exists — only the `CLAUDE.md` map row is missing (AC5). The
  `current-product-state.md` header *date* is already bumped to 2026-08-27 — what
  remains is that the header asserts body-currency never established by an audit
  (AC3). The docs lane confirms the full live residue list at implementation time
  (AC6).
- **Status.** Marked `Next phase` per the work order's definition of done, as the
  next story to build in Epic 41's sequence. This file is nonetheless a draft
  pending owner approval.
