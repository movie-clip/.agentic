REPORT 2026-08-28-epic-41-and-dep-vulns/04
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only DESIGN order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-41.3.4 SHIPS. Add a pytest re-drift guard for epic-roadmap.md per-epic section ordering — own test file, test lane — see § T-41.3.4 verdict
  - Lane split: T-41.3.1 + T-41.3.2 + T-41.3.3 are ONE docs-engineer order (all deliverables are docs/** edits); T-41.3.4 is a separate test-engineer order — see § Lane split
  - T-41.3.2 is a docs-lane task with a read of types.ts, NOT frontend/test — the story left the call to DESIGN; deliverable is a docs/contracts edit — see § Lane split
  - AC1 outcome is CONFIRMATION not correction: correlation-fields.md DriftWindow + coverage TS columns already match types.ts field-for-field — see § Item 1
  - AC2 scope shrinks to ONE line: correlation-fields.md:84. factor-drift-fields.md:4 says "_none_" and cites no class — record not-applicable — see § Item 2
  - AC2 target: correlation-fields.md:84 cites `schemas/reconciliation.py` — `RollingRiskPoint` (class at reconciliation.py:122); builder ref may stay alongside — see § Item 2
  - AC4: only Epic 23 / Epic 24 headings are transposed; swap the two section blocks (roadmap L1291-1341 <-> L1343-1420), pure block move, no reword — see § Item 4
  - Dispatch order: docs order + test order run in parallel; both land before the AC7 suite run; then integration + review gates — see § Dispatch order
  - US-41.3 changes NO schema, route, response shape or analytic output — goldens byte-identical, dashboardGoldens.ts must not move, no methodology/contract test moves — see § Contract statement
  - Possible mid-run quant referral from T-41.3.3 only (a stale methodology/trust claim in current-product-state.md body) — not expected; rest of story proceeds without it

risks:
  - Story tension: AC6 names stories/README.md + prd/README.md, but "## Out of scope" excludes index restructure. Working rule: in-place label/pointer/date fixes YES, structural regrouping NO. Story-author clarification worth having; not a blocker
  - Story premise partly false: item 2 / AC2 asserts factor-drift-fields.md has an analytics-builder citation to fix; it has none (header reads "_none_"). Implementer records it not-applicable, not "corrected"
  - Most of scout § B-G residue (AC6) is already closed by prior passes: stories/README.md epic labels all "(complete)", Epic 30 heading present, build-story instruction prose gone. Live AC6 surface is now thin — docs lane confirms at implementation time and records already-closed items
  - AC6 vs prd/README.md § Index (~35 epics stale, "Epic 5 Active"): recommend the minimal fix (de-assert the stale "Active", add an epic-roadmap.md pointer), leave a full index rebuild to Epic 41 close-out. Flagged so the docs lane does not over-reach
  - scout § F numeric nit (-$53.13 vs -$58.11 / -$19.98 in financial-methodology.md): if still live it is a methodology-doc figure reconciliation, not a doc-lane string edit — route to quant if a real discrepancy, ignore if a pure typo

## Orchestrator brief

- DESIGN verdict on T-41.3.4: **ship the guard.** Epic precedent (US-36.3, US-41.2) is "doc-accuracy reconciliation ships a re-drift guard"; roadmap ordering has now drifted twice; the scan is cheap and trivially non-vacuous. Own file, test lane.
- Lane split: **one docs-engineer order** carries T-41.3.1 + T-41.3.2 + T-41.3.3 (every deliverable is a `docs/**` edit); **one test-engineer order** carries T-41.3.4. T-41.3.2 is docs-lane (deliverable is a `docs/contracts` edit; reads `types.ts`), overriding the story's "frontend or test lane" phrasing — the story deferred that call here.
- Dispatch order: docs order and test order run in parallel and independently; both must land before the AC7 full-suite run; then integration (tech-lead) + review (reviewer). No quant-audit unless T-41.3.3 spawns a referral.
- Contract statement: US-41.3 changes no schema, route, response shape or analytic output. Goldens byte-identical; `dashboardGoldens.ts` must not move; no methodology/contract test moves.
- Item 1 (AC1): **confirmation, not correction** — `DriftWindow` table + relocated `coverage` row TS columns in correlation-fields.md already match `types.ts` exactly. Deliverable is a dated confirmed-correct note in `## Notes / decisions`.
- Item 2 (AC2): scope is **correlation-fields.md:84 only**. `RollingRiskPoint` is defined at `services/quant-engine/app/schemas/reconciliation.py:122`; the line currently cites `analytics/risk.py` — `build_rolling_risk_series` (the builder). factor-drift-fields.md:4 reads "_none_" — nothing to fix there.
- Item 4 (AC4): roadmap convention is strictly **descending** (Epic 40 -> Epic 8). Only Epic 23 / Epic 24 are transposed. Fix = swap the two section blocks; content-safe (self-contained `---`-delimited blocks, slice-log tables travel intact).
- Item 3 (AC3): body is ~220 lines. "Read once" line-by-line against shipped code; correct non-methodology staleness in place; any methodology/trust claim found stale is a quant-lane finding, not edited here.
- Item 5 (AC5): add a dedicated CLAUDE.md doc-map row for `docs/contracts/currency-risk-fields.md` in the form of the existing `risk-fields.md` row (currency/FX exposure contract, Epic 26).
- Sections below: Contract statement · Lane split · Dispatch order · Item 1..Item 4 target state · Item 5 · Item 6 (AC6) · T-41.3.4 verdict · AC traceability · Risks (in the report block).

---

# TECHNICAL PLAN — US-41.3

## Contract statement

US-41.3 changes **no** Pydantic schema, no route, no response shape, no
`types.ts` type, and no analytic output. Every deliverable is either a prose
edit under `docs/**` / `CLAUDE.md`, or one new pytest file that only *reads* a
markdown doc.

Consequences for the gates:

- `dashboardGoldens.ts` and every golden artifact stay **byte-identical**. If
  `git diff apps/desktop/src/test/dashboardGoldens.ts` is non-empty at
  integration, it is an FMP-cache artifact and must be reverted
  (`reset_goldens()`), not accepted.
- No methodology test and no contract test moves. If one does, a lane exceeded
  scope.
- No `app/schemas/**` edit — so the schema-edit PostToolUse hook must never
  fire in this story. If it does, stop.
- `contract` field-by-field alignment (the normal DESIGN deliverable) is N/A:
  there is no boundary-crossing shape here. The one place a shape is *checked*
  (Item 1) is a read-only verification of an already-shipped type against its
  contract doc.

## Lane split

| Ticket | Lane | Agent | Deliverable |
|---|---|---|---|
| T-41.3.1 | docs | `docs-engineer` | correlation-fields.md:84 citation fix (AC2); epic-roadmap.md Epic 23/24 block swap (AC4); CLAUDE.md doc-map row (AC5); scout § B-G live-residue sweep (AC6) |
| T-41.3.2 | docs | `docs-engineer` | correlation-fields.md `DriftWindow` + `coverage` TS-column verification vs `types.ts` (AC1) — a dated confirmed-correct note in `## Notes / decisions` |
| T-41.3.3 | docs | `docs-engineer` | current-product-state.md body re-audit against shipped code (AC3); non-methodology staleness corrected in place; methodology/trust staleness recorded as a quant-lane finding |
| T-41.3.4 | test | `test-engineer` | new pytest guard: epic-roadmap.md per-epic section headings are in descending order + non-vacuous-scan check (AC4) |

**T-41.3.1 + T-41.3.2 + T-41.3.3 are ONE docs-engineer work order.** They touch
disjoint files, share a lane, and T-41.3.2's outcome (a confirmation) is small
enough that splitting adds coordination cost for no isolation benefit. Sequence
inside the order does not matter; item 3 is the only unbounded one and can run
first or last.

**Why T-41.3.2 is docs-lane, not "frontend or test lane"** (the story left this
to DESIGN): the deliverable is an edit to `docs/contracts/correlation-fields.md`
(docs-lane's file), the verification input is `types.ts` which `docs-engineer`
can `Read`, and the check turns out to be a confirmation — there is nothing to
implement in `apps/desktop/src/**` and no worthwhile mechanical test to add (a
markdown-table-vs-TS-type string diff is brittle and the story says add one only
if "otherwise unguarded and cheap to encode" — it is neither). Recorded as a
deliberate deviation from the story's phrasing.

**T-41.3.4 is a separate test-engineer order** — different lane, new file under
`services/quant-engine/app/tests/`, and it is authored concurrently with the
docs order (it goes red-before / green-after the roadmap reorder).

## Dispatch order

1. **In parallel:** the docs-engineer order (T-41.3.1/2/3) and the
   test-engineer order (T-41.3.4). No dependency between them beyond the AC4
   target state, which is fixed in this plan (descending order; swap Epic
   23/24). The guard test will be red until the roadmap reorder lands — that is
   the intended red-before state.
2. **After both land:** `python scripts/run_all_tests.py` must exit 0 (AC7).
   The reorder (in the docs order) and the guard (in the test order) must both
   be in place for this to pass.
3. **Gates:** integration (`tech-lead` INTEGRATION) then review (`reviewer`).
   No quant-audit is scheduled. It is pulled in **only** if T-41.3.3's body
   re-audit surfaces a stale methodology/trust claim — that specific claim
   routes to the quant lane as a finding and is *not* edited in this story;
   the rest of the story proceeds.

Item 3 can run parallel to item 1 in the sense that matters (different files) —
but since both are in the same single docs order, "parallel" reduces to "same
agent, either order". There is no reason to spin a second docs agent.

## Item 1 — AC1: DriftWindow + coverage TS columns vs types.ts

**Verified in this pass. The doc is already correct — this is a confirmation.**

`types.ts` (read this pass):
- `DriftWindow` at **L1519-1528**: `label: string`, `start_date: string | null`,
  `end_date: string | null`, `portfolio_return_pct: number | null`,
  `benchmark_return_pct: number | null`, `spread_pct: number | null`,
  `trust: DriftTrust`, `note: string | null`.
- `DriftTrust` at **L1517**: `'synthetic' | 'unavailable'`.
- The "relocated `coverage` row" is `MultiBenchmarkCorrelationResult.coverage`
  at **L1601**: `coverage?: SyntheticHistoryCoverage | null` (i.e.
  `SyntheticHistoryCoverage | null | undefined`).
- `SyntheticHistoryCoverage` at **L949-954**.

`docs/contracts/correlation-fields.md` (read this pass):
- `DriftWindow` table **L55-64**: TS-type column is
  `string` / `string \| null` / `number \| null` / `'synthetic' \| 'unavailable'`
  / `string \| null` — **matches `types.ts` field-for-field, same order.**
- `coverage` row **L128** (in `MultiBenchmarkCorrelationResult`): TS-type column
  `SyntheticHistoryCoverage \| null \| undefined` — **matches** the
  optional-plus-null shape at `types.ts:1601`.

**Target state:** no table edit. Add to `## Notes / decisions` in
`correlation-fields.md`: the `DriftWindow` table and the relocated `coverage`
row were verified column-by-column against
`apps/desktop/src/features/portfolio/types.ts` (`DriftWindow` L1519,
`MultiBenchmarkCorrelationResult.coverage` L1601) on 2026-08-28 and are
confirmed correct.

**Existing test coverage:** none mechanically diffs this markdown table against
the TS type. Do **not** add one — brittle, and out of proportion to a
confirmed-correct table (test plan's own bar).

## Item 2 — AC2: schema citation names the defining module

**Verified in this pass. Scope is one line.**

- `RollingRiskPoint` class is defined at
  `services/quant-engine/app/schemas/reconciliation.py:122` (grep this pass:
  `class RollingRiskPoint(BaseModel):`).
- `build_rolling_risk_series` is a real builder at
  `services/quant-engine/app/analytics/risk.py:572`; it imports
  `RollingRiskPoint` and returns `list[RollingRiskPoint]`.
- `docs/contracts/correlation-fields.md:84` currently reads:
  `**Backend schema:** `services/quant-engine/app/analytics/risk.py` — `build_rolling_risk_series``
  — cites the builder function's module, not the class's module.

**Every `**Backend schema:**` line in the two docs** (grep this pass):

| File:line | Current citation | Verdict |
|---|---|---|
| correlation-fields.md:31 | `schemas/drift.py` (`DriftDailyPoint`) | correct — leave |
| correlation-fields.md:84 | `analytics/risk.py` — `build_rolling_risk_series` | **FIX** |
| correlation-fields.md:111 | `schemas/correlation.py` (`MultiBenchmarkCorrelationResult`) | correct — leave |
| factor-drift-fields.md:4 | `_none_ — this card has no backend route or schema` | **not applicable** — cites no class; record as such, do not invent a citation |

**Target state for correlation-fields.md:84** (AC2 allows the builder ref to
remain *alongside* the class citation, not in place of it):

```
**Backend schema:** `services/quant-engine/app/schemas/reconciliation.py` — `RollingRiskPoint`
(series assembled by `services/quant-engine/app/analytics/risk.py` — `build_rolling_risk_series`)
```

Exact wording is the docs lane's; the constraint is: the file named must be the
one containing `class RollingRiskPoint`, i.e. `schemas/reconciliation.py`.

**factor-drift-fields.md:** AC2 lists it, but the file has no offending
citation (header is `_none_`, and it genuinely has no route/schema — confirmed
by reading the file). Record in `## Notes / decisions` that factor-drift-fields.md
was checked and carries no `**Backend schema:**` class citation to correct.

## Item 4 — AC4: epic-roadmap.md section ordering

**Majority convention:** strictly **descending** by epic number. Headings are
`## Completed Epic: Epic <N> — <title>` (grep this pass, 33 headings, Epic 40
down to Epic 8).

**Out of place:** exactly one transposition — Epic 23 heading (L1291) precedes
Epic 24 heading (L1343). Every other heading is in descending order. The brief
also named "Epic 25 at L1250" but Epic 25 (L1250) correctly follows Epic 26
(L1221) and precedes the 24/23 pair — Epic 25 is **not** misplaced; only 23 and
24 are swapped relative to each other.

**Reorder is content-safe.** Each per-epic section is a self-contained block:
`---` separator, then `## Completed Epic: Epic <N> …`, its `**PRD:**` line, and
its slice-log table, running to the next `---`. Confirmed boundaries this pass:
Epic 23 block ≈ L1289-1341, Epic 24 block ≈ L1343-1420, next section (Epic 22)
starts L1422. Swapping the two blocks (keeping the `---` rhythm) yields
`… 26, 25, 24, 23, 22 …`. **No heading text, PRD link, or slice-log row is
reworded or dropped** — it is a block move only. AC4's "no slice-log content is
lost or reworded" is satisfied by construction.

## Item 3 — AC3: current-product-state.md body re-audit

**Size.** 225 lines total; header is L1-5, body ≈ L7-225 (~220 lines). This is
the story's only unbounded item and its size is exactly "read the body once".

**What "read against shipped code" means here**, concretely — for each
shipped-feature claim in the body:
- a named route still exists in `services/quant-engine/app/api/routes/`;
- a named field / response shape still matches its schema in `app/schemas/`;
- a named card / component still exists under `apps/desktop/src/features/`;
- an epic / story / date reference is consistent with `epic-roadmap.md` and git.

Correct **in place**: stale dates, superseded epic/story numbers, feature
descriptions that no longer match the code **where the mismatch carries no
trust or methodology claim**.

**The quant-referral branch.** If a body statement that is a *methodology* claim
(how a number is computed — TWR, Modified Dietz, VaR/CVaR, factor betas, a
weighting) or a *trust-semantics* claim (`verified`/`degraded`/`withheld`/
`unavailable` behaviour, truth-class assignment) is found stale or wrong:
**do not edit it.** Record it as an itemised finding, name the body line and the
claim, mark it "routed to quant lane", and surface it to the orchestrator. The
rest of the audit and the rest of the story proceed without it. This item stays
entirely docs-lane unless that branch fires.

**Outcome recorded** in `## Notes / decisions` of the story file (per AC3):
either "body confirmed accurate as of 2026-08-28" or the itemised discrepancy
list (with each item tagged corrected-in-place / routed-to-quant).

Note L3 already asserts "body current through Epic 40 … plus Epics 35-39 …" —
AC3 exists precisely because that assertion was never backed by a line-by-line
read. The audit either earns that sentence or replaces it with the discrepancy
list.

## Item 5 — AC5: CLAUDE.md doc-map row for currency-risk-fields.md

`docs/contracts/currency-risk-fields.md` exists (grep this pass:
`**Backend schema:** …/schemas/currency_risk.py`). CLAUDE.md's "Where to find
what" table has a generic `docs/contracts/<area>-fields.md` row and one
*dedicated* row for `docs/contracts/risk-fields.md`:

```
| `docs/contracts/risk-fields.md` | Risk-tab contract: stress, drawdown, VaR & distribution response shapes (Epic 13) |
```

**Target state:** add one dedicated row in the same form, adjacent to the
risk-fields.md row, e.g.:

```
| `docs/contracts/currency-risk-fields.md` | Currency-risk contract: FX exposure & currency-risk response shapes (Epic 26) |
```

Description wording is the docs lane's; the constraint is AC5's: dedicated row,
form consistent with the risk-fields.md row, states what the contract doc
covers. Feature lineage is Epic 26 (Currency Exposure & Risk).

## Item 6 — AC6: residual pointer/label/date/citation sweep

**Most of scout § B-G is already closed** (checked this pass) — the docs lane
confirms the live list at implementation time and records already-closed items
in `## Notes / decisions`:

| scout § B-G item | State this pass |
|---|---|
| stories/README.md 6 stale `(active)`/`(backlog)` epic labels | **closed** — all headings now `(complete)` |
| stories/README.md missing Epic 30 heading | **closed** — heading present at L167 |
| stories/README.md `build-story` instruction prose (was L504-505) | **closed** — gone; only a historical slice-log mention at L149 remains (legitimate) |
| prd/README.md L29 `build-story` instruction | **closed** — L31 now states build-story "is superseded and must not run" |
| `(complete)` vs `(completed)` inconsistency | **closed** — uniform `(complete)` |
| stories/README.md non-monotonic section order | **not drifted** — 25 → 24 → 23 is already descending there (only *epic-roadmap.md* has the 23/24 swap, = AC4) |
| Epic 40 "PRD: none" pointers (stories/README.md, roadmap, story headers) | **spot-check at implementation** — not found in this pass's greps; docs lane confirms Epic 40's blocks |
| prd/README.md § Index ~35 epics stale ("Epic 5 Active") | **likely still live** — see below |
| CLAUDE.md Epic-34 "most recent" pointer | **out of scope** (story explicitly: "surfacing it, not scheduling it") |
| financial-methodology.md −$53.13 vs −$58.11 / −$19.98 (scout § F) | **quant-lane territory if real** — a methodology figure, not a doc-lane string; correct only if a pure typo, else route to quant |

**prd/README.md § Index judgment call.** AC6 names prd/README.md; the story's
`## Out of scope` excludes "the story index README.md's epic grouping" and index
restructure. Working rule for the docs lane: make the **minimal in-place fix** —
de-assert the stale "Epic 5 — Active" and add a one-line pointer to
`epic-roadmap.md` as the authoritative epic index — and **do not** rebuild the
full PRD index table (that is Epic 41 close-out). If the docs lane judges even
the minimal fix to be "restructure", it records prd/README.md as
deferred-to-close-out with the reason.

**General rule for AC6:** in-place label / pointer / date / citation
corrections are in scope; anything that adds, removes, or regroups index
structure is deferred to Epic 41 close-out (per the story's own `## Out of
scope`). Every item the docs lane does not act on is recorded as already-closed
or deferred-with-reason in `## Notes / decisions`.

## T-41.3.4 verdict — SHIP THE GUARD

**Decision: yes, US-41.3 ships the roadmap-ordering guard as T-41.3.4.**

Weighing (per the open decision):
- US-32.3 shipped no guard; **US-36.3 shipped one** (`test_route_inventory.py`);
  **US-41.2 shipped one** (`test_architecture_doc_route_inventory.py`). The
  epic's own precedent — twice now — is "a doc-accuracy reconciliation ships a
  mechanical re-drift guard".
- Roadmap section ordering is a **demonstrated recurring drift**: it is why AC4
  exists, and the scout caught it independently. A one-assertion guard is thin
  in isolation but it guards a failure mode that has actually recurred.
- The scan is **cheap and trivially non-vacuous**: 33 headings match a fixed
  `## Completed Epic: Epic <N> —` prefix today.
- Cost: one new test file, ~2 assertions, zero golden impact, no methodology
  surface.

Only item 4 is mechanically guardable, so this is the whole mechanical angle of
the story — consistent with the epic pattern, not test inflation.

**Guard shape** (test-engineer owns the implementation; these are the
constraints):

- **File placement:** a new sibling file
  `services/quant-engine/app/tests/test_roadmap_epic_ordering.py`. **Not**
  folded into `test_docs_paths.py` (that guards path claims, not ordering) and
  **not** into the `test_route_inventory.py` / `test_architecture_doc_route_inventory.py`
  family (route inventory, unrelated). Follows US-41.2's own-sibling-file
  precedent.
- **Assertion 1 — ordering:** scan `docs/product/epic-roadmap.md` in file order
  for every per-epic section heading, extract the epic numbers, assert the list
  is strictly descending. On failure, name the first out-of-order pair (e.g.
  "Epic 23 section precedes Epic 24 section") — not a bare `assert sorted(...)`.
- **Assertion 2 — non-vacuous scan:** assert the heading scan matched at least
  N headings (N ≈ 25; there are 33 today), in the manner of
  `test_route_inventory.py::test_the_scan_is_not_vacuous`. If the heading regex
  stops matching (format reworded, section renamed, file moved) the test fails
  loudly rather than passing on an empty list.
- **Heading regex breadth:** key on `## Completed Epic: Epic <N> —` for the
  completed-epic slice log. If the test lane finds an *active*-epic heading uses
  a different form (`## Epic <N> —`), widen the capture to include it so no
  per-epic section escapes the scan; the non-vacuous count protects either way.
  (No active-epic heading exists in the file today — Epic 41's section is added
  at close-out, not in this story.)
- **Red-before / green-after:** against the current unmodified file the ordering
  assertion is **red** (… 25, 23, 24, 22 …); it goes green only once T-41.3.1's
  Epic 23/24 block swap lands. The test lane verifies both states by execution.

## AC traceability

| AC | Ticket | File(s) | Deliverable |
|---|---|---|---|
| AC1 | T-41.3.2 | `docs/contracts/correlation-fields.md` | `DriftWindow` + `coverage` TS columns verified vs `apps/desktop/src/features/portfolio/types.ts`; confirmed-correct note dated 2026-08-28 in `## Notes / decisions` |
| AC2 | T-41.3.1 | `docs/contracts/correlation-fields.md` (L84); `docs/contracts/factor-drift-fields.md` | L84 cites `schemas/reconciliation.py` — `RollingRiskPoint`; factor-drift-fields.md recorded not-applicable (no class citation) |
| AC3 | T-41.3.3 | `docs/product/current-product-state.md`; story file `## Notes / decisions` | body read line-by-line vs shipped code; non-methodology staleness fixed in place; methodology/trust staleness → quant-lane finding; outcome recorded |
| AC4 | T-41.3.1 (reorder) + T-41.3.4 (guard) | `docs/product/epic-roadmap.md`; `services/quant-engine/app/tests/test_roadmap_epic_ordering.py` | Epic 23/24 section blocks swapped to descending order, no content reworded; pytest guard asserts descending order + non-vacuous scan |
| AC5 | T-41.3.1 | `CLAUDE.md` | dedicated doc-map row for `docs/contracts/currency-risk-fields.md`, form of the `risk-fields.md` row |
| AC6 | T-41.3.1 | `docs/product/stories/README.md`, `docs/product/prd/README.md`, doc-map pointers | live scout § B-G residue corrected in place (most already closed); structural regrouping deferred to Epic 41 close-out; already-closed / deferred items recorded |
| AC7 | (whole story) | — | `python scripts/run_all_tests.py` exits 0 with all changes + the new guard in place |
