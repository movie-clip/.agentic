REPORT 2026-08-27-next-epic-or-story/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only producer order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Next unit of work is US-41.1 — resume run 2026-08-26-missing-chart-data-0414 and dispatch its implementation lanes — see § Already covered
  - No "Epic 41" exists anywhere in docs/ and no epic is active; roadmap's next epic is unscoped — see § Placement
  - open decision: confirm epic placement / numbering for US-41.1 (currently placeholder "US-41.x"; human's 2026-08-26 call was "Backlog, no new epic") — see § Open decisions
  - open decision: confirm the DESIGN pass's deletion of replay_disclosures()'s dead reconciliation_adjustment branch is acceptable — see § Open decisions
  - US-41.1 file still reads Status: Backlog / Epic: Unassigned — a status flip to "Next phase" at pickup, not a re-ticketing pass — see § Stories
  - quant lane required: quant-audit gate after implementation (change touches withholding / disclosure classification) — see § Stories
  - alternative next unit if not US-41.1: dependency-vulnerability bumps (starlette, pypdf, python-multipart, pydantic-settings, python-dotenv) — no story exists yet — see § Already covered

risks:
  - US-41.1's human approval is taken on trust from run 2026-08-26-missing-chart-data-0414/run.md ledger entries; I did not witness the approval directly.
  - The tech-lead DESIGN pass resolved the story's two "flagged, not resolved" decisions itself; if the human rejects the dead-branch deletion, 06-technical-plan.md § Decision needs revisiting before backend dispatch.
  - Epic 28 is headed "(backlog)" in the story index but all its stories show Status: Done — read as a stale label with no actionable work, not independently reconciled.

## Orchestrator brief
- verdict: already covered — an approved, fully-planned story (US-41.1) exists and is mid-run; no new story or epic to author
- epic 41: does not exist — no PRD, no roadmap section, no mention in docs/; "US-41.x" is an explicit placeholder number in one Backlog story
- active epic: none — Epic 40 closed 2026-08-25; roadmap snapshot says "No epic is active", "next epic is unscoped"
- next unit: US-41.1 "Explain a withheld-return gap where it appears on the Performance & Benchmark chart" — resume run 2026-08-26-missing-chart-data-0414
- planning state: story approved · quant RESEARCH done (03-quant-research.md) · tech-lead DESIGN done (06-technical-plan.md, 2026-08-27 06:54) · implementation lanes never dispatched
- code state: unimplemented — no PerformancePoint.withheld_reason field, no inline annotation in PerformanceBenchmarkCard.tsx (both checked this run)
- 1 story ready to build: US-41.1 — 4 tickets T-41.1.1..4, lane split already settled in 06-technical-plan.md § Lane split
- blocks dispatch: nothing hard — 2 one-line confirmations wanted (epic numbering; dead-branch deletion); neither blocks the backend ticket starting
- quant lane: required — quant-audit gate after implementation (withholding / disclosure-honesty classification, guardrails 1 & 4)
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**"Epic 41" is not a thing on this roadmap.** `docs/product/epic-roadmap.md`
(snapshot updated 2026-08-25) states plainly: *"Every epic is complete… No epic
is active… The next epic is unscoped."* The highest real epic is **Epic 40 —
Snapshot Trust & Fidelity Follow-Through**, closed 2026-08-25. A grep of `docs/`
for "Epic 41" / "epic-41" returns nothing: no PRD file, no roadmap section, no
story-index group.

The only artifact carrying a `41` is the story file
`docs/product/stories/US-41.1-inline-withheld-return-annotation.md`, whose own
header says the number is **a placeholder**: *"The `US-41.x` numbering is this
draft's placeholder pending [the epic] decision… 40 is the highest epic number
currently in use and this project's convention is that every story lives under
some epic number."* On 2026-08-26 the human explicitly decided **not** to open a
new epic for it — *"Backlog, no new epic now, per the 'Backlog until it has
siblings' convention"* (recorded in the story's `## Open decisions` and in run
2026-08-26-missing-chart-data-0414's ledger).

**Precedent for the "orphan Backlog story under a placeholder epic number"
shape:** Epic 28 in the story index carries US-30.x stories and is itself headed
"(backlog)"; the project already tolerates a story sitting under a number before
its epic is real. US-41.1 is a sibling of that pattern, not a new kind of thing —
which is exactly why "Backlog until it has siblings" was the right call and no
epic inflation is warranted yet.

So placement is not an open design question. The open question is purely
administrative: what number US-41.1 keeps (see § Open decisions).

## Stories

### US-41.1 — Explain a withheld-return gap where it appears on the Performance & Benchmark chart

The researcher can see, at the exact point on the Performance & Benchmark chart
where the portfolio line breaks, the specific reason that date's return was
withheld — without leaving the chart for `ReplayDisclosuresCard` or the card's
own summary note.

    value:      today the withheld-day gap is disclosed twice (a prose note in
                ReplayDisclosuresCard, a summary line on PerformanceBenchmarkCard)
                but neither sits AT the line break; a researcher looking only at
                the line has no inline explanation. This closes that reading gap.
    slice:      inline annotation on PerformanceBenchmarkCard.tsx's chart at each
                withheld date, fed by a new backend field
                PerformancePoint.withheld_reason: str | None derived from the
                same classifier replay_disclosures() reads. Nearest thing
                deliberately OUT: the same treatment on IndexedReturnChart.tsx,
                the Risk-tab drawdown/VaR charts, and MonthlyReturnsGrid.tsx —
                named as follow-on candidates, not built here.
    depends_on: none — self-contained; run 2026-08-26-missing-chart-data-0414
                already carries the approved story, the quant research brief
                (03-quant-research.md) and the tech-lead DESIGN plan
                (06-technical-plan.md). Nothing upstream is missing.
    invest:     weak on "Estimable at Backlog status" only in the bookkeeping
                sense — the file header still says Status: Backlog / Epic:
                Unassigned and its 4 tickets are unchecked. That is acceptable
                because the ticketing + design work is in fact done
                (06-technical-plan.md gives per-ticket dispatch instructions and
                the settled contract); pickup needs a one-line status flip to
                "Next phase", not a fresh story-author or ticketing pass.

**Readiness is real, not asserted.** Verified this run:

- Schema: `PerformancePoint` (`reconciliation.py:510-515`) has `date`,
  `portfolio_value`, `benchmark_price`, `portfolio_return_pct`,
  `benchmark_return_pct` — **no `withheld_reason`.** Unimplemented.
- Frontend: `PerformanceBenchmarkCard.tsx` has no `ReferenceDot` and no
  per-point annotation — only the existing run-level summary note at line 249.
  Unimplemented.
- Run 2026-08-26-missing-chart-data-0414: artifacts 01–06 all `DONE`,
  `status: DISPATCHING`, implementation lanes (backend/frontend/test/docs) never
  dispatched. `06-technical-plan.md` (2026-08-27 06:54) settled the contract
  (`PerformancePoint.withheld_reason: str | None`, TS mirror
  `PerformanceSeriesPoint.withheld_reason?: string | null`), the shared
  `_withheld_return_cause(state)` helper, the frontend marker treatment
  (`ReferenceDot` diamond at `y=100`, `--color-status-warn`, keyboard-focusable,
  caption on focus/hover), and a lane split that corrects a real story/pack
  conflict (the story's T-41.1.1 text bundles `types.ts` + `docs/contracts/**`
  into a "Backend" ticket, which `backend.md` forbids).

**Quant lane.** This change touches the withholding / disclosure-honesty
classification (`replay_disclosures()`, `return_is_publishable`, the withheld
cause string) — guardrails 1 and 4. RESEARCH is done. **quant-audit is required
after implementation** and is already on the run's gate line.

## Sequence

Only one story, but its tickets have a build order, taken from
`06-technical-plan.md` § Lane split and order:

1. **T-41.1.1 — backend** (`backend-engineer`). Add
   `PerformancePoint.withheld_reason`; extract `_withheld_return_cause(state)` in
   `performance.py`; wire `replay_disclosures()` to read the same helper; delete
   the dead `reconciliation_adjustment` branch (`performance.py:225-229` — see
   § Open decisions). Emits the contract note the frontend and docs lanes
   consume. *First because every other ticket depends on the field shape.*
2. **T-41.1.2 — frontend** (`frontend-engineer`). Inline `ReferenceDot`
   annotation on `PerformanceBenchmarkCard.tsx`, consuming the backend contract
   note for the exact TS field. *Hard dependency on T-41.1.1's contract note.*
3. **T-41.1.3 — test** (`test-engineer`). Backend regression pin
   (`withheld_reason` non-null exactly on `withheld_return_dates`, including the
   two immaterial-unbacked-cash-flow dates 2026-06-10 / 2026-06-23) + the
   frontend render tests. *After 1 and 2 so there is behaviour to pin; note the
   plan's § Test-plan resolution flags the existing full-`LineChart` mock as a
   two-tier fix.*
4. **T-41.1.4 — docs** (`docs-engineer`). `dashboard-fields.md` contract row +
   the short methodology note (two granularities of the same cause, one shared
   classifier). *Last; folds in the backend contract note.*

Then the three gates: **quant-audit → integration → review**.

## Open decisions

- **Epic placement / numbering for US-41.1.** The human decided on 2026-08-26
  "Backlog, no new epic now". Picking it up as the single next unit of work does
  not by itself change that, but the docs lane will need a definite answer at
  close-out before it touches the roadmap or story index: (a) keep it as an
  orphan Backlog story under the placeholder `US-41.x` number, (b) open a small
  Epic 41 to house it, or (c) adopt an explicit numbering convention for
  orphaned Backlog stories. This is the owner's call; it does not block starting
  T-41.1.1.

- **Deletion of `replay_disclosures()`'s dead `reconciliation_adjustment`
  branch** (`performance.py:225-229`). The story's `## Out of scope` and
  `## Open decisions` explicitly left this unresolved ("arguably outside a
  strict reading of 'do not change the withholding classification logic'"). The
  tech-lead DESIGN pass then resolved it to **DELETE** — its stated reason:
  compelled by AC4 (one classification, not two independently maintained), and
  the branch is a latent disclosure-honesty defect (could misattribute a cause),
  not merely dead. quant-audit will gate this regardless. The human should
  confirm they accept the DESIGN pass having settled a decision the story
  flagged for them, or say to keep the branch with a comment instead.

## Already covered

**The request resolves to US-41.1, and US-41.1 is already fully planned — it just
has not been built.** There is no producer work left to do on it beyond this
brief: recon, delivery brief, quant research, story draft and technical plan all
exist in run `2026-08-26-missing-chart-data-0414` and the story was
human-approved. The correct next action is to **resume that run and dispatch the
implementation lanes** per `06-technical-plan.md` § Lane split, in the order in
§ Sequence above.

Nothing else on the roadmap is a stronger claim on "next":

- **US-26.3 / US-26.4** (currency-risk follow-ups) — listed in the roadmap's
  open items and `docs/tech-debt-register.md`, explicitly *"none of which block
  anything"* and US-26.4 marked optional. Not shaped as build-ready stories the
  way US-41.1 is.
- **Epic 36 close-out carries** — 3 `SHOULD_FIX` + 1 operational note from the
  integration gate (untested `audit_dependencies.py` priority rule; untested
  rename-entry parsing in `_commit_gate.changed_files()`; npm-audit marker text
  not yet diffed against a real failure; the shared `.last-test-pass` marker
  race). All engineering-completeness, none user-visible — each is an
  express-sized `test`/`docs` item, not "the next unit", but available if the
  human wants smaller work.
- **Dependency-vulnerability findings** — real advisories against pinned
  `starlette==0.48.0`, `pypdf==6.9.1`, `python-multipart==0.0.20`,
  `pydantic-settings==2.13.1`, `python-dotenv==1.1.1`, plus one low-severity
  transitive frontend package (`@babel/core`). Surfaced by US-36.2, deliberately
  not acted on, *"a follow-up, not part of Epic 36"*. **No story exists yet.**
  This is the strongest alternative to US-41.1 if the human wants a hygiene pass
  instead of the chart annotation — it would need a producer brief and a story
  first.
- **Epic 28** is headed "(backlog)" in the story index but every story under it
  shows `Done` — a stale label, no actionable work (see § risks).
