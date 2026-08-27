REPORT 2026-08-26-missing-chart-data-0414/02
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
  - 1 story proposed, no existing open epic fits — see § Placement and § Stories
  - open decision: which epic hosts it (new epic now vs. hold for siblings) — see § Open decisions
  - open decision: client-side cause re-derivation vs. a thin per-date backend field — see § Open decisions
  - already covered: the gap itself is disclosed today via ReplayDisclosuresCard + a summary note; only the inline-at-the-point annotation is missing — see § Already covered

risks:
  - I verified `withheld_return_reason`'s exact shape myself (services/quant-engine/app/schemas/dashboard_history.py:306-307, app/analytics/performance.py:207-235) rather than trusting scout's paraphrase, because it changes the DoD's schema-vs-client-side verdict: it is ONE run-level string covering every active cause, not per-date.
  - I verified daily_states already reaches PerformanceBenchmarkCard.tsx myself (grep on the component + types.ts:1212-1213, 1415-1416) rather than trusting scout, since "no schema change needed" rests entirely on that prop already being wired.
  - Took on trust from 01-scout: the exact mechanism/date list for the Dashboard chart's null point (performance.py:367, test_ledger_replay_audit.py:735-740) and the unresolved rendering behaviour of the Exposure/Risk/Monthly candidates — re-verifying those was out of this order's scope (DoD only asks to flag plausibility, not resolve them).

## Orchestrator brief
- verdict: new story, no fitting open epic — placement is genuinely open, not a formality
- epic: none active fits (Epic 33/34/40 all closed, "never reopen" applies); nearest sibling by theme is closed Epic 34 — recommend a **new** epic, flagged PROPOSED, human decides
- 1 story: PROPOSED "Explain a withheld-return gap where it appears on the Performance & Benchmark chart" — Backlog-eligible, has one open design decision, otherwise estimable now
- blocks dispatch: epic placement (new epic vs. hold for siblings) and the cause-derivation approach (client-side vs. thin backend field) — both are human/tech-lead calls, not settled here
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**No open epic fits.** `epic-roadmap.md`'s live snapshot (lines 1-14) states "No epic
is active" — Epic 40 closed 2026-08-25, and the roadmap's "never reopen a closed
epic" convention (implicit in every close-out: closed epics get no new stories,
only tech-debt-register follow-ups) rules out riding Epic 33 (origin of the
withholding mechanism), Epic 34 (An Answerable Dashboard — the disclosure-UX
epic this is closest to in spirit), or Epic 40 back open.

**Nearest precedent by theme, closed:** Epic 34 — "An Answerable Dashboard:
Reachable Trust States." That epic's whole premise was making trust/disclosure
states visible and reachable in the UI (US-34.2's degraded-trust marker, the
ReplayDisclosuresCard buildout). This request is the same kind of work — moving
a disclosure from "reachable if you scroll" to "visible at the point of use" —
just discovered after that epic closed.

**Nearest precedent by surface, also closed:** Epic 29 — "Chart First-Render
Reliability," a one-story epic about Recharts mount timing. Thematically weaker
match (rendering mechanics, not disclosure content) but it is this project's
only precedent for a chart-focused epic sized to a single story, which matters
for the epic-inflation call below.

**Not a fit:** the immediately-prior standalone run
(`2026-08-26-performance-benchmark-chart-audit`, `route: review`, `story: NONE`,
no epic) is not a usable precedent for *this* request, even though it touched
the exact same file. That run fixed **defects in already-shipped behaviour**
(US-25.1's range-selector promise, a raw-value-vs-TWR formula bug) — express/
review-eligible because "no new user-visible scope" held: the fixes made
existing ACs true, they didn't add a capability nobody had promised. An inline
gap annotation is the opposite case — see § Stories, express-lane check.

**Epic-inflation tension, stated plainly.** The capability pack's rule: "A
one-story epic needs a reason beyond 'this request needs somewhere to live'...
If the story you are proposing is small-to-medium with an unresolved design
decision, [the Epic-16 quick-win precedent] does not apply, and 'Backlog until
it has siblings' is often the more honest verdict." This story **does** carry
an unresolved design decision (§ Stories, § Open decisions) — no existing
gap/marker pattern exists anywhere in this codebase's charts (checked: every
Recharts usage under `apps/desktop/src/features/portfolio/*.tsx` uses only
`ReferenceLine` for fixed axis references and standard `Tooltip` for hover-on-
data; nothing renders on a *null* point). By the letter of that rule, this
tips toward Backlog-without-a-new-epic.

But this project's convention (checked via `docs/product/stories/README.md`'s
index, lines 19-496) is that **every story lives under some epic** — even a
Backlog-status one (Epic 28 sits at `(backlog)` status with a real PRD and
zero shipped stories). There is no "orphan story, no epic" precedent to fall
back on. So the practical choice is not "epic vs. no epic," it is "new epic
now vs. wait" — and I am flagging both paths rather than picking one, per the
order's non-goal.

## Stories

### PROPOSED: Explain a withheld-return gap where it appears on the Performance & Benchmark chart

**Outcome (one sentence):** the researcher can see, at the exact break in the
Performance & Benchmark line, why that specific day has no return — without
leaving the chart to find ReplayDisclosuresCard or the card's summary note.

**value:** Today the gap is disclosed twice (ReplayDisclosuresCard's prose note,
and PerformanceBenchmarkCard's own summary line saying "N days excluded... see
Replay Disclosures") but neither is *at* the gap. A user reading the line alone
sees an unexplained break. This closes that specific reading gap — it does not
change what is disclosed, only where.

**slice — in:** an inline marker/tooltip on `PerformanceBenchmarkCard.tsx`'s
chart, at each date in `performance_series` where `portfolio_return_pct` is
null and the date is in `run_metadata.withheld_return_dates`, naming the
specific cause for *that* date.

**slice — out (nearest thing deliberately excluded):** the same treatment on
the Exposure tab's drift chart (`IndexedReturnChart.tsx`), the Risk tab's
drawdown/VaR charts, and `MonthlyReturnsGrid.tsx`. Scout traced all three as
sharing the same underlying `return_is_publishable` flag but could not confirm
any of them render a visible line-break the way this chart does — the
drawdown/VaR series *omits* the withheld day from its array entirely rather
than emitting a null point (01-scout.md, Fourth candidate), which may not even
need the same UI treatment (there is no break to explain if there is no gap in
the plotted series). Building those now would be scoping ahead of confirmed
need; noted as follow-on candidates for a future story, not built here.

**Express-lane check (per `project.md` § "The express lane in this repo"),
checked against all five criteria, not asserted:**
- One lane — plausible, frontend-only (see cause-derivation note below).
- No contract crosses — **true**, confirmed by reading the schema directly:
  `daily_states: list[DailyPortfolioState]` (already carrying
  `reconciliation_adjustment` and `unbacked_cash_flow` per date) is already a
  prop reaching `PerformanceBenchmarkCard.tsx` today (it is already consumed
  at line 138 for the terminal-adjustment display), and its TS mirror already
  carries both fields (`types.ts:579-582`). No schema/type/contract-doc change
  is required to build this.
- No mathematics — true in the sense of no formula/return-basis change; see
  the logic-duplication note below for the one place this gets close.
- **No new user-visible scope — false, and this is the disqualifier.** A
  marker/tooltip that does not exist today, on a chart nobody promised one for,
  is exactly the case the rule names: "If a user could describe the result as
  a new capability, it is a story." This confirms the order's suspicion.
- Bounded — plausible (one card, its test file, possibly `chartDefaults.ts`
  if a shared gap-marker style is added there for reuse by future siblings).

  **Verdict: NOT express-eligible**, on the "no new user-visible scope"
  criterion alone — the other four would not have blocked it.

**depends_on:** none technically — the data this needs already reaches the
card. Soft dependency on a design pass (`tech-lead` DESIGN mode) before
build, because there is no existing gap/marker pattern in this design system
to reuse (checked `ui-polish/SKILL.md` and every chart file under
`features/portfolio/`) and the pass should also settle the cause-derivation
question below.

**invest:** weak on nothing structural. The one soft spot is that "small" and
"estimable" both assume the design decision resolves quickly; if the design
pass concludes a backend field is warranted (see below), the story grows by
one small backend ticket and a contract-doc row, not a re-scope.

## Sequence

Single story, no ordering to state. If the human confirms a sibling candidate
(most likely the Risk-tab drawdown/VaR charts, since they share the exact same
`return_is_publishable` flag) is real follow-on work, that becomes a second
story in the same epic — risk-first would then mean tracing what those charts
actually render *before* designing their annotation, since scout could not
confirm they show a visible gap at all.

## Open decisions

- **Epic placement.** New epic now (status Backlog or Next-phase, human's
  choice), scoped broadly enough ("disclosure legibility at the point of use"
  or similar) to plausibly take the three follow-on chart candidates as later
  siblings if they turn out to need it — versus holding this as a Backlog
  story and deferring epic creation until a second sibling is confirmed and
  ready, per this project's stated "Backlog until it has siblings" convention.
  Both are defensible; I am not picking one.

- **Cause-derivation approach — client-side re-derivation vs. a thin backend
  field.** `run_metadata.withheld_return_reason` is a single string built by
  `replay_disclosures()` (`app/analytics/performance.py:207-235`) that
  concatenates *every* cause active anywhere in the run — on the current
  IB2026 statement all four withheld dates share one cause (confirmed:
  `test_analytics.py:8538-8544` asserts only the unbacked-cash sentence fires
  post-US-34.8), so today a per-point tooltip could reuse that flat string
  without being wrong. But that is incidental to this statement, not
  structural: a future statement with *both* causes active on different dates
  would make the flat string misattribute a cause to a specific point. A
  correct-in-general tooltip needs to classify per date — which is possible
  purely client-side today (the raw signal, `reconciliation_adjustment` and
  `unbacked_cash_flow`, is already in `daily_states` per date), but doing so
  means re-implementing `replay_disclosures()`'s two-branch classification
  logic a second time, in TypeScript. The prior chart-audit run's own Finding
  2 (a dead duplicate formula, deleted for exactly this drift risk) is the
  concrete precedent for why that duplication is worth naming rather than
  waving through. The alternative — a small, additive, non-breaking per-date
  reason surfaced from the existing engine-side classification — would keep
  one source of truth at the cost of a schema addition (which would also flip
  the express-lane "no contract crosses" criterion, though that lane is
  already disqualified on user-visible-scope grounds regardless). This is a
  `tech-lead` DESIGN-pass call, not mine to make; flagged so it is not
  discovered mid-build.

## Already covered

The withholding itself, its disclosure on `ReplayDisclosuresCard`, and the
summary note on `PerformanceBenchmarkCard` are all shipped (US-31.3, US-33.2
AC9, US-34.2/US-34.4/US-34.8) and working as designed — confirmed by reading
`dashboard-fields.md`'s rendering-surface paragraph (line 332) and
`replay_disclosures()` directly, not just scout's summary. Nothing here
reopens that work or disputes it. The only gap is the one the user named after
being informed: no annotation *at* the chart's own line-break. No existing
story, PRD finding, or tech-debt-register entry names this specific gap
(checked `docs/tech-debt-register.md` for "annotat"/"tooltip"/"gap" — no
matches), so this is not a duplicate of recorded, deliberately-open work.
