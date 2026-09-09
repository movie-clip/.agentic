REPORT 2026-09-07-new-epic-perf-benchmark-trust/03
status:      PARTIAL
verdict:     NONE

changed:
  - none

verification:
  command:   NONE (read-only producer order)
  result:    NOT_RUN
  detail:    Roadmap contradiction resolved from git (commit ce9c97d wiped the plan surface). Prior-art dedupe run against git history, merged PRs, and prior .agentic run ledgers. Four points classified; epic + 4-story breakdown proposed.

contract_notes:
  - none

pack_corrections:
  - product.md ("Where the plan lives") and project.md ("Sources of truth") name docs/product/epic-roadmap.md as "the authority" plus docs/product/prd/** and docs/product/stories/** as the story surface; all were deleted in repo commit ce9c97d (HEAD, 2026-09-07). Replacement wording waits on Open decision 1 — see § Placement and § Open decisions for the evidence and the options.

handoff:
  - Verdict: NEW EPIC (proposed Epic 44), 4 stories, one per point — producer recommends; epic placement is the owner's call — see § Placement
  - Not audit-first: the cause of P1/P2/P3 is already named by 01-recon + 02-quant-research; record F-1..F-4 in the Epic 44 PRD, no US-44.1 audit story — see § Placement
  - BLOCKS story-author: the repo has no plan surface — roadmap/PRD/story docs deleted in ce9c97d, GitHub issue tracker empty (gh issue list, all states) — see § Open decisions
  - Open decision: P1 per-month withheld-day disclosure — schema flag on DashboardMonthlyReturn vs inherit the run-level withheld_return_* disclosure (decides whether S1 pulls the schema hook) — see § Open decisions
  - Open decision: S3 (P3) needs a tech-lead DESIGN pass first — valuation_dates is derived from benchmark_rows, so a benchmark-independent calendar must be designed before the outage gate can be split — see § Open decisions
  - Open decision: S2 (P2) route — express-eligible (frontend-only, no schema) vs full route + quant-audit because it is a trust-disclosure change; producer recommends full route — see § Open decisions
  - Quant methodology gaps a-d (02-quant-research) map to close-out of S1 (a, b), S2 (c), S3 (d) — none blocks arithmetic — see § Open decisions
  - Sequence: S1 -> [S2 parallel] -> S3 -> S4; S1 risk-first (live guardrail-1/4 fabrication bug), S3 before S4 (selector makes benchmark outages reachable) — see § Sequence
  - 01-recon's two contract notes (dashboard-fields.md:105 unreachable "unavailable" state; :98-101 monthly source_status) map to S3 and S1 respectively — see § Stories
  - Adjacent, not a duplicate: US-41.1 (Backlog, unimplemented) adds an inline withheld-gap chart annotation — different from P2's over/under-states copy fix — see § Already covered

risks:
  - DoD item 1 sub-clause ("name the concrete artifact a new epic would be recorded in") is unmet: the repo's planning-doc surface was deleted in ce9c97d and not replaced, and the GitHub issue tracker is empty. The contradiction itself is resolved (see § Placement); the placement target is Open decision 1. This is why status is PARTIAL.
  - Prior-art dedupe used git history, merged PRs, and prior .agentic run ledgers. The pre-cleanup docs/tech-debt-register.md (455 lines, now 5 rows) is not in the working tree, so a carried low-severity row could be missed; the 2026-08-26 and 2026-09-01 run ledgers are explicit about what they carried and neither carried P1-P4.
  - US-41.1's Backlog status and prior human approval are taken on trust from run 2026-08-26-missing-chart-data-0414's ledger; the story file itself was deleted in ce9c97d and could not be re-read.
  - P1's reported "+100% monthly return" repro is taken on trust from the reporter via 01-recon; recon confirmed the code path but built no runtime repro, and _monthly_returns_are_reliable's >100 guard means the observable severity depends on the fabricated magnitude.

---

## Orchestrator brief

- verdict: NEW EPIC — proposed Epic 44 (highest epic in git history is 43), four stories, one per reported point. Producer recommends one epic; owner confirms.
- epic: PROPOSED. No epic is active. Nearest precedent: Epic 34 (answerable-dashboard-and-reachable-trust) — same surface, same shape (trust-honesty defects + reachability in the imported-dashboard performance chain).
- not audit-first: 01-recon + 02-quant-research already are the audit; F-1..F-4 go straight into the Epic 44 PRD. No US-44.1 audit story.
- S1 (P1) PROPOSED — monthly returns honour the shared withholding gate; no month contains a fabricated withheld/reconciled-day return. Quant-gated. Risk-first.
- S2 (P2) PROPOSED — the withheld-days warning states over- vs under-statement by the sign of the impact. Frontend-only. Smallest, independent.
- S3 (P3) PROPOSED — a benchmark-history outage degrades only the benchmark section; portfolio TWR/MWR/contributions/monthly stay available. Quant-gated. Needs DESIGN.
- S4 (P4) PROPOSED — the researcher can choose the comparison index for the imported dashboard. Schema change -> not express-eligible, schema hook fires. Quant-touched.
- blocks dispatch: YES — Open decision 1: the repo has no plan surface (roadmap/PRD/story docs deleted in ce9c97d; GitHub issues empty). Story-author cannot place a story until the human designates where epics/stories now live.
- other open decisions: P1 disclosure-marker shape (schema or not); S3 DESIGN pass (benchmark-independent calendar); S2 route; quant gaps a-d; epic number/scope confirmation.
- sequence: S1 -> [S2 in parallel] -> S3 -> S4.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

---

## Placement

### Where the plan actually lives right now — the contradiction resolved

01-recon flagged that `docs/product/epic-roadmap.md` and `docs/product/prd/**`
are absent from the working tree though named in scope, CLAUDE.md and
`project.md`, and that the last .agentic run on 2026-09-05 still edited them.

**Resolution (git evidence):** commit `ce9c97d` "cleanup" — current `HEAD`,
authored 2026-09-07 06:33, working tree clean, branch level with
`origin/main` — deleted the entire planning-doc surface in one change: 207
files, 34,819 deletions. Removed: `docs/product/epic-roadmap.md`,
`docs/product/roadmap.md`, `docs/product/technical-roadmap.md`, every
`docs/product/prd/epic-*.md`, every `docs/product/stories/US-*.md`, the story
`_TEMPLATE.md`, `review-2026-08-20-findings.md`, and
`app/tests/test_roadmap_epic_ordering.py` (the test that enforced roadmap
structure). Only `docs/product/current-product-state.md` survives in that tree.
CLAUDE.md was rewritten in the same commit to delete the "PRD -> User Story ->
Ticket" model text and add: *"Historical implementation tickets and roadmaps
are preserved in Git history, not maintained as active documentation."*

`docs/agents/issue-tracker.md` (committed earlier, in `6b63ae1` US-43.1) says
issues live in **GitHub Issues** via `gh`. But `gh issue list` across all
states returns **zero issues**, and that file carries only wayfinder-map
conventions, no epic/story convention. So the surface was not migrated — it
was removed, with nothing put in its place.

**Concrete artifact a new epic would be recorded in: none exists.** This is
Open decision 1 and it blocks the story-author. The `.agentic` `product.md` /
`project.md` packs are now stale on this point (see `pack_corrections`).

### Why one new epic, and which epic it is a sibling of

The four points sit on **one surface**: the imported-dashboard performance /
benchmark chain. P1, P2 and P3 all live in exactly two files —
`services/quant-engine/app/services/dashboard_history_engine.py` and
`apps/desktop/src/features/portfolio/PerformanceBenchmarkCard.tsx` — and are
all **trust-honesty defects** (publish a fabricated value / mislabel a
disclosure / suppress usable output). P4 is a **capability gap** on the same
route (`dashboard_history.py`) and the same card.

**Precedent epic: Epic 34 — "Answerable Dashboard & Reachable Trust."** Same
surface, same shape: a cluster of trust-honesty corrections in the
imported-dashboard performance chain plus reachability of an
honestly-labelled output, delivered as one epic with numbered findings
(F-1..F-13) and one story per finding-group. Also in the family: Epic 27
(financial-calculation-correctness — audited monthly-return chaining, which is
where P1 was last touched) and Epic 25 (dashboard-performance-risk-summary —
shipped this card and the monthly grid). A new epic here is a **sibling of
Epic 34**, not a new kind of thing, and it is not epic inflation: four stories,
shared surface, and P1 alone is a live guardrail-1 + guardrail-4 bug.

**Corrected framing.** The reporter's text labels two different points "P2"
(the withheld-warning direction and the benchmark-outage suppression). They
are distinct: P2 = a UI copy/logic defect, P3 = a backend fail-closed
collapse. The epic covers **four** points: P1, P2, P3, P4.

**Not audit-first.** The house pattern makes `US-<epic>.1` an audit when the
cause is only suspected. Here 01-recon and 02-quant-research already located
and confirmed every point with `file:line` and a methodology reading. The
finding record (F-1 = P1, F-2 = P2, F-3 = P3, F-4 = P4) belongs in the Epic 44
PRD, assembled from those two reports; each story names the finding it closes.
No US-44.1 audit story.

**Who decides.** Epic creation, number (44) and scope are the owner's call.
This brief recommends; it does not settle it.

---

## Stories

Finding IDs below (F-1..F-4) are the proposed Epic 44 PRD entries.

### S1 (proposed US-44.1) — closes F-1 (P1)

**Outcome:** the researcher can trust that no cell in the monthly-returns grid
contains a return fabricated from a day whose daily return was withheld or
carried a terminal reconciliation adjustment.

  value:      today an unbacked-cash day (US-33.2 share-unit discontinuity) or
              a reconciled terminal day compounds its un-interpretable move into
              that month's figure; the only backstop hides the entire grid when
              any month exceeds +/-100%. After S1 the grid stays intact and the
              affected month shows its real partial-month return.
  slice:      IN — route `_compute_contribution_adjusted_monthly_returns`
              (dashboard_history_engine.py:837-863) through the same
              publishable-day gate + `market_derived_terminal_value` correction
              the TWR chain uses (`performance.py::_time_weighted_daily_return`);
              a month with all days withheld emits no row; MonthlyReturnsGrid
              tolerates omitted months; methodology § "Monthly Returns
              (Dashboard)" made explicit; regression tests.
              OUT (own decision) — a per-cell "partial month" disclosure marker
              (Open decision 2); reconciling `source_status.monthly_returns`
              wording (01-recon contract note dashboard-fields.md:98-101) is a
              close-out doc task, not new scope.
  depends_on: none to start. Soft: S3 also touches the monthly path under
              benchmark-absent; doing S1 first means S3 builds on a corrected
              path.
  quant:      GATED — `analytics/`-adjacent trust logic, a return basis, a
              publication rule. Quant RESEARCH done (02 § P1); quant-audit after.
  invest:     Estimable/Small only once Open decision 2 is answered — if a
              schema flag is added it pulls the schema hook (types +
              dashboard-fields.md) and grows a lane. May spawn a successor
              story for the disclosure marker.

### S2 (proposed US-44.2) — closes F-2 (P2)

**Outcome:** the withheld-days warning on the Performance & Benchmark card
tells the researcher whether the shown return is over- or under-stated, and by
how much, matching the sign of the impact.

  value:      the card already renders a signed impact but the words are
              hard-coded to "understates"; when including withheld days would
              lower the return (negative impact) the shown value overstates and
              the copy is backwards. Quant 02 § P2 settles the rule: understates
              iff `withheld_return_impact_pct > 0`, overstates iff `< 0`,
              no directional claim at `0.00` or null.
  slice:      IN — `PerformanceBenchmarkCard.tsx:246-258` copy selection on the
              sign; null / zero handling; a test with a negative-impact fixture;
              a one-sentence methodology addition (Open decision 5 / gap c).
              OUT — any engine change (`withheld_return_impact_pct` sign is
              already correct).
  depends_on: none. Fully independent — can run in parallel with S1.
  quant:      LIGHT — no formula, no analytics change; the rule is already
              stated. Touches a trust disclosure, so quant-audit is the
              conservative call (Open decision 4).
  invest:     Strong on all six INVEST tests; the smallest story in the epic.

### S3 (proposed US-44.3) — closes F-3 (P3)

**Outcome:** when benchmark history is unavailable, the researcher still sees
portfolio TWR, money-weighted return, net contributions and monthly returns
(each at its own trust level), with only the benchmark fields marked
`unavailable`.

  value:      today `dashboard_history_engine.py:304` and `performance.py:305`
              return the fully-unavailable dashboard whenever `benchmark_rows`
              is empty, discarding usable holdings history and replay states.
              Quant 02 § P3: five portfolio-economics outputs are
              benchmark-independent; collapsing them to `unavailable` because a
              different field's input is missing violates guardrails 3 and 4.
  slice:      IN — split the two fail-closed gates so the portfolio leg is
              keyed independently of `benchmark_rows`; `section_trust` /
              `source_status` report the benchmark section `unavailable` without
              forcing the portfolio path to match (this makes the state
              dashboard-fields.md:105 documents actually reachable — 01-recon
              contract note); frontend tolerates portfolio-present /
              benchmark-absent; benchmark-absent test fixture; methodology rule
              (Open decision 6 / gap d).
              OUT — changing what any benchmark-derived metric means; drawdown's
              own withholding policy is untouched.
  depends_on: Soft on S1 (shared monthly path). HARD on a tech-lead DESIGN
              pass — `valuation_dates` is currently `sorted({row["date"] for
              row in benchmark_rows})` (line 313); removing the gate leaves the
              replay calendar undefined. Needs a benchmark-independent calendar
              designed first (Open decision 3).
  quant:      GATED — `analytics/performance.py`, trust classification. Quant
              RESEARCH done (02 § P3); quant-audit after.
  invest:     Largest story; Estimable only after the DESIGN pass. Consider
              whether the calendar rework is its own ticket inside S3.

### S4 (proposed US-44.4) — closes F-4 (P4)

**Outcome:** the researcher can select the comparison index for the imported
dashboard instead of always being compared to SPY.

  value:      `current-product-state.md` advertises "selectable periods" only;
              the imported route accepts a bare snapshot and the card shows the
              symbol as a label with no control. The service already accepts
              `benchmark_symbol: str | None = None`
              (dashboard_history_engine.py:263). Matters for non-US,
              multi-asset and mandate-specific portfolios.
  slice:      IN — carry a chosen symbol from the card (with workspace
              persistence, App-level, US-25.2 range-selector pattern) through
              the adapter, the route, and into the service; a selector control
              on the card; trust handling for a non-allowlisted symbol (cannot
              be `verified_total_return`); frozen-fixture prices for any test
              symbol; docs (route inventory, current-product-state).
              OUT — a benchmark selector on the non-imported `/run` path (that
              route is an always-unavailable stub, judged intentional in the
              2026-08-26 run).
  depends_on: Risk-ordered AFTER S3 — a user-chosen obscure index is exactly
              what makes a benchmark-history outage reachable; S3's graceful
              degradation should exist before S4 ships the ability to trigger
              it (02-quant § risks, 01-recon § P4).
  quant:      TOUCHED — return-basis / trust implications of a non-allowlisted
              benchmark. Quant RESEARCH before this one is authored.
  invest:     Not express-eligible — `ImportedPortfolioSnapshot` (or the route
              signature) changes, under `app/schemas/`; the schema hook fires
              and TS types + `docs/contracts/dashboard-fields.md` move in the
              same pass. Independent and Valuable; medium size.

---

## Sequence

Recommended order: **S1 -> S2 (parallel with S1) -> S3 -> S4.**

- **S1 first — risk-first.** It is a live guardrail-1 + guardrail-4 fabrication
  bug (a withheld day published as performance). It also shares the
  monthly-returns code path with S3, so correcting it first means S3 does not
  build on a broken helper. Edge: soft dependency S1 -> S3.
- **S2 in parallel.** Frontend-only, zero shared code with S1, no schema. It is
  a quick correctness win that can land while S3/S4 are still in DESIGN. No
  dependency in either direction.
- **S3 after S1, before S4.** After S1: soft, shared monthly path. Before S4:
  risk-ordering — S4 lets the researcher point at an index whose history may be
  thin or absent, which is precisely the condition S3 makes safe. Shipping S4
  first re-opens P3 for every non-default benchmark. S3 also has a hard
  internal dependency on a tech-lead DESIGN pass before implementation.
- **S4 last.** Depends on S3 by risk-ordering; carries the schema hook and the
  most lanes (schema, route, frontend, market-data, docs, quant).
- **Expect a successor.** S1 may spawn its own follow-up if Open decision 2
  resolves toward a visible per-month disclosure marker rather than inheriting
  the run-level disclosure.

---

## Open decisions

Each bullet is one question for the human.

- **1 (BLOCKING — blocks the story-author).** Where do epics and stories live
  now? Commit `ce9c97d` deleted `docs/product/epic-roadmap.md`, every PRD and
  every story file, and CLAUDE.md now says roadmaps are "not maintained as
  active documentation." `docs/agents/issue-tracker.md` points at GitHub
  Issues, but `gh issue list` (all states) is empty and there is no epic/story
  convention there. Options: (a) restore the deleted roadmap/PRD/story docs and
  keep the doc-based model; (b) adopt GitHub Issues and define an epic/story
  convention; (c) another surface. Nothing downstream can place a story until
  this is answered, and the `.agentic` product/project packs need the same
  answer to stop pointing at a deleted file.
- **2.** P1 disclosure shape: does a month that dropped a withheld interior day
  need its own visible marker (a per-cell flag on `DashboardMonthlyReturn`, a
  footnote), or does inheriting the run-level `withheld_return_dates` /
  `withheld_return_impact_pct` disclosure suffice? A schema flag pulls the
  schema hook into S1 (types + `dashboard-fields.md`) and may split S1.
  (02-quant-research § Methodology gaps (b).)
- **3.** P3 valuation calendar: `valuation_dates` is derived from
  `benchmark_rows` (dashboard_history_engine.py:313). A benchmark-independent
  trading calendar (union of in-window dates across the replay price
  histories, or an exchange calendar) must be designed before the line-304
  collapse can be removed. This is a tech-lead DESIGN decision — confirm S3
  gets a DESIGN pass before any implementation lane. (01-recon § risks,
  02-quant § P3.)
- **4.** P2 route: S2 is frontend-only with no schema change, which is
  express-lane eligible in this repo — but it changes a trust disclosure.
  Producer recommends the full route with a quant-audit gate. Confirm.
- **5.** P1 methodology resolution (02-quant gap a): confirm the fix is
  "exclude the withheld day from the month's product" (preserves the
  `Prod(1+monthly) = Prod(1+daily)` chaining identity) rather than "withhold
  the whole month." Quant 02 is confident; the human ratifies because it is a
  methodology-doc change at S1 close-out.
- **6.** P2 signed-interpretation doc wording (02-quant gap c):
  `financial-methodology.md` § "Publication rungs" documents
  `withheld_return_impact_pct` only through an understatement example; the
  general signed reading needs a one-sentence addition. Docs lane at S2
  close-out; confirm the wording.
- **7.** P3 methodology rule (02-quant gap d): no section states that a total
  benchmark-history outage must still publish portfolio-economics on the
  imported dashboard path. Guardrails 3 and 4 imply it; the operative rule is
  unwritten. Decide the intended rule before or during S3 authoring.
- **8.** Epic scope and number: confirm this is Epic 44 and that all four
  points belong in one epic, rather than folding P1 into a
  calculation-correctness epic and P4 into a capability epic. Producer
  recommends one epic (shared surface, Epic 34 precedent); epic placement is
  the owner's call.

---

## Already covered

Prior-art dedupe for each point, against git history, merged PRs, prior
`.agentic` run ledgers, and the surviving in-tree docs. **None of the four is
covered by an open story or by a recorded deliberate-deferral decision.**

| Point | Verdict | Evidence |
|---|---|---|
| **P1** monthly fabricated return | **Not tracked; prior work superseded, not duplicative** | `US-27.2` (commit `4efdb31`, PR #33, Epic 27) fixed monthly-return *chaining* and max-drawdown basis — but predates `return_is_publishable`, introduced in Epics 31/33/34. The monthly path was never re-wired to the shared predicate; 02-quant § "Duplication" confirms it is now "a third, ungated re-implementation" of the daily-return formula. No open row in `docs/tech-debt-register.md`; its one "Trust semantics" row concerns *over*-withholding, the opposite failure. |
| **P2** warning direction | **Not tracked** | No doc records the sign semantics of `withheld_return_impact_pct`. `US-34.5` shipped the disclosure; nothing since has touched the card's "understates" copy. Not in the tech-debt register. |
| **P3** benchmark outage suppresses all | **Not tracked** | The 2026-08-26 audit run judged the *non-imported* `/run` route's always-unavailable stub "intentional fail-closed" (its CR-2 #3, carried to the pre-cleanup register) — a *different* code path. The *imported* path's `line 304` / `performance.py:305` collapse when `benchmark_rows` is empty has never been raised. `dashboard-fields.md:105` documents a `benchmark_history:"unavailable"`-within-a-valid-run state the code cannot currently produce. Closest precedent (class, not duplicate): `US-35.1` "an auth failure is not missing data" — same fail-closed-collapses-usable-output class, different subsystem. |
| **P4** benchmark selector | **Observed, never storied** | The 2026-08-26 audit run's scout explicitly noted "no benchmark-symbol selector exists on this chart/tab — symbol is hardcoded 'SPY'"; the ledger marked it `ABSORBED` (acknowledged, not carried to any register or story). `git log -S benchmark_symbol` on the imported route and `imports.py` schema: only the initial commit. `current-product-state.md:13` advertises "selectable periods" only. |

**Adjacent, explicitly not a duplicate of P2:** `US-41.1` "inline
withheld-return annotation" (Status: Backlog, unimplemented; file deleted in
`ce9c97d` but recorded in run `2026-08-26-missing-chart-data-0414`). It adds an
*inline chart annotation at the break point* explaining why a day was withheld.
P2 fixes the *direction of the summary warning copy*. Different mechanism,
different defect. If Open decision 1 restores the story surface, S2 and US-41.1
should cross-reference but stay separate.

**Deliberately-open findings check:** Epic 34 left F-1a, part of F-10, and F-12
open by decision. None of P1-P4 maps to those (they concern replay opening
quantities and immaterial-day withholding, not the monthly grid, the warning
copy, the outage gate, or benchmark selection). This brief reverses no recorded
decision.
