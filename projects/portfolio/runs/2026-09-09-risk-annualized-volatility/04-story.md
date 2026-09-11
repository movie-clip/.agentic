REPORT 2026-09-09-risk-annualized-volatility/04
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-44.1-risk-tab-annualized-volatility.md — new drafted story (Backlog); recreates the docs/product/stories/ directory deleted at HEAD, as the work order expects.

verification:
  command:   none
  result:    NOT_RUN
  detail:    Order verification field is NONE; story-author is a shell-less drafting lane with no command to run.

contract_notes:
  - docs/finance/financial-methodology.md § "Annualized realized volatility" needs an amendment (not a new section): the Risk-tab 60-observation publication floor plus sub-floor trust states (N=0 unavailable, 1-59 withheld, not collapsed), kept separate from the per-position 20-observation rule. Ticket T-44.1.1 carries it.
  - docs/contracts/risk-fields.md needs a new portfolio-level volatility section; docs/contracts/diagnostics-fields.md needs a cross-reference.
  - The Risk-tab sibling engines' trust vocabulary is synthetic|unavailable only and carries no withheld rung this figure requires.

pack_corrections:
  - none

handoff:
  - Story drafted at docs/product/stories/US-44.1-risk-tab-annualized-volatility.md — draft for human review, not approved.
  - Tickets (provisional on the DESIGN pass): T-44.1.1 contract + methodology amendment; T-44.1.2 apply floor + emit states in engine; T-44.1.3 render on Risk tab; T-44.1.4 behavioural + cross-surface coverage; T-44.1.5 close-out reconciliation.
  - Open decision blocking ticketing: story ID / Epic 44 formalization — draft uses US-44.1 per the order; no index exists to check it against. Human confirms at approval.
  - Open decision blocking ticketing: zero-variance series at N >= 60 — publish 0.00% (reused house path) or withhold (pack rule). ACs do not assert it.
  - Open decision (DESIGN, tech-lead not human, listed for visibility): how the withheld state is represented on the Risk tab given sibling cards expose only synthetic|unavailable.
  - Open decision blocking ticketing: cross-surface divergence band is ~2 <= N < 60, not 20-59 — the Dashboard figure has no floor today.
  - Net-new trust-state logic (guardrail 1): quant-audit must follow implementation; no ticket self-invokes it.

risks:
  - The order's premise that the Dashboard figure already has a 20-observation floor is wrong (02-quant-research.md 1.3, 03-scout.md): it publishes from N>=2, returns 0.00% at N=1. Story drafted to the corrected ~2<=N<60 band; raised as Open decision 4.
  - Sibling stories could not be read for register calibration — the docs/product/stories/ corpus was deleted at HEAD. Draft follows the write-story conventions and the story pack instead.
  - Epic 44 / US-44.1 numbering is taken on the order's instruction with no index to verify against; flagged as Open decision 1.
  - Zero-variance behaviour at N>=60 is left unasserted pending the human's ruling; the test lane has nothing to encode for that case until it is resolved.
  - Tickets imply a lane split the order reserves for tech-lead DESIGN; framed as provisional on the design pass and traced to ACs, but a design pass may re-cut them.

## Orchestrator brief

- Drafted US-44.1 (Backlog): docs/product/stories/US-44.1-risk-tab-annualized-volatility.md. Draft for human review, not approved.
- Decision: written on the order's settled assumptions — reuse the Dashboard computation; 60 paired-observation publication floor; N=0 unavailable, 1-59 withheld, >=60 published.
- Decision: 12 acceptance criteria; zero-variance behaviour at N>=60 deliberately left unasserted.
- Decision: 5 ordered tickets T-44.1.1..5, contract+methodology first, dedicated coverage its own, close-out last; provisional on the DESIGN pass.
- Lane split: none beyond ticket order; withheld-state wire/card representation left to tech-lead DESIGN.
- Blocks ticketing (human): story ID / Epic 44 formalization; zero-variance -> 0.00% or withhold; divergence band is ~2<=N<60 not 20-59.
- Contract notes to route: methodology amendment target; missing risk-fields.md section + diagnostics-fields.md cross-ref.
- Story body reproduced below; the standalone file is authoritative and carries the status header. Sections named: Open decisions (block ticketing); Story statement; Context; Acceptance criteria; Test plan; Tickets; Out of scope; Notes / decisions.

## Open decisions (block ticketing)

None of these are resolved in this draft. The story below is written on the
assumptions recorded as *settled* in the work order; these four are not.

1. **Story ID / Epic 44 formalization.** This draft uses `US-44.1` under a new
   Risk-tab epic ("Epic 44 (new, Risk-tab)") because the work order directs it.
   The epic itself is not defined here, and the planning corpus that would
   normally carry the numbering (`epic-roadmap.md`, `prd/**`, `stories/**`) was
   deleted at HEAD, so the ID cannot be checked against an index. If a different
   ID or epic placement is warranted, the human resolves it at approval; this
   lane does not pick a different one silently.

2. **Zero-variance series at N ≥ 60 — publish `0.00%` or withhold?** For a
   constant daily-return series the reused computation returns `0.00%`
   (`std 0 → 0.0 * sqrt(252)`). The quant pack's edge-case rule says a
   zero-variance input should yield `null`. The research brief
   (`02-quant-research.md` § 3, edge-case table) flags this as genuinely open:
   a dispersion statistic over a truly constant series arguably *has* a
   well-defined value of exactly zero, unlike a ratio such as beta. The human
   decides which behaviour the Risk tab publishes; the acceptance criteria
   below deliberately do not assert it.

3. **How the withheld state is represented on the Risk tab.** This is a
   **design question for the tech lead**, not for the human to resolve now —
   listed here only so it is visible. The Risk tab's sibling engines expose a
   trust vocabulary of `synthetic | unavailable` only; they have no `withheld`
   rung. This figure needs a `withheld` state those surfaces do not currently
   carry (`02-quant-research.md` § 3.2, `03-scout.md` § Trust-state
   representation and rendering). The wire and card representation is settled in
   the design pass.

4. **Divergence band is ~2 ≤ N < 60, not 20–59.** The work order assumed the
   Dashboard figure already has a 20-observation floor. It does not
   (`02-quant-research.md` § 1.3, `03-scout.md` § The 60-observation gate): the
   Dashboard surface publishes an unfloored estimate from N ≥ 2 (and `0.00%` at
   N = 1). So once this story's 60-observation floor lands, the Risk tab and the
   Dashboard disagree (number vs. withheld) across roughly 2 ≤ N < 60, a wider
   band than the order anticipated. The human confirms whether that wider
   divergence changes anything for them.

## Story statement

**As a** portfolio researcher,
**I want** the portfolio's annualized volatility shown on the Risk tab, held
back below a 60-trading-day history floor,
**so that** I can judge the portfolio's yearly dispersion inside the
pre-decision risk-budget view without switching to the Dashboard and mentally
reconciling a daily, population-basis figure against an annualized one.

## Context

Portfolio annualized realized volatility already ships — on the **Dashboard**,
in the Risk Summary card, as `volatility_summary.portfolio_volatility_pct`
(`docs/contracts/diagnostics-fields.md`, `docs/contracts/dashboard-fields.md`).
Its formula — `stdev(daily_returns) * sqrt(252)` on the sample (N−1) standard
deviation of the cash-flow-neutral daily portfolio return series (synthetic
history basis) — is documented in `docs/finance/financial-methodology.md`
under **"Annualized realized volatility"**.

This story is a **Risk-tab surfacing of that same scalar**, not a new metric
and not a Risk-tab-native recomputation. The one behavioural difference is a
stricter **publication floor**: the Risk tab, as the higher-bar pre-decision
view, publishes the figure only with **at least 60 paired daily-return
observations**, and holds it back below that. The Dashboard surface is
unchanged. The 60-observation floor is a new threshold, distinct from the
existing product-wide 20-observation minimum (`MIN_DAILY_OBSERVATIONS`); its
estimation-error grounding is in `02-quant-research.md` § 2.

The Risk tab has no summary area today — it hosts exactly the Stress, Drawdown,
and VaR/Distribution cards (`03-scout.md` § RiskPanel and the three cards). Where
the figure sits on the tab (a new small surface, or a row on an existing card)
is a design decision, not fixed here.

The implementer must read: `docs/finance/financial-methodology.md`
§ "Annualized realized volatility"; `docs/contracts/risk-fields.md`;
`docs/contracts/diagnostics-fields.md`; `02-quant-research.md` §§ 2–3, 5.

## Acceptance criteria

Truth class throughout: **synthetic history** (current holdings valued over
historical prices; no trade replay).

1. **On the tab.** A researcher on the Risk tab can read the portfolio's
   annualized volatility there, without navigating to the Dashboard.

2. **Consistent presentation.** The figure is rendered inside the Risk tab's
   card layout using the same trust-badge vocabulary and the same numeric
   label styling as the tab's existing cards, so it does not read as a
   foreign element.

3. **Synthetic trust, not more.** When the figure is published it carries the
   `Synthetic` trust treatment and never presents as `verified` or `degraded`.

4. **Cross-surface equality.** When a portfolio is loaded such that both the
   Risk tab and the Dashboard display the figure, the two shown values are
   equal to the precision each surface displays.

5. **Same computation, reused.** The published value is the Dashboard's
   `volatility_summary.portfolio_volatility_pct` — same return series, same
   formula, same code path. No second implementation of the volatility
   calculation is introduced for the Risk tab. (Constraint carried from the
   work order and `02-quant-research.md` § 1; the observable check is AC 4.)

6. **Published at or above the floor.** With at least 60 paired daily-return
   observations, the Risk tab shows the figure as a number.

7. **Withheld below the floor.** With between 1 and 59 paired daily-return
   observations inclusive, the Risk tab shows a withheld trust state and **no
   number** — not the value, not a zero, not a dash standing in for a computed
   value, and not the Dashboard's unfloored estimate passed through.

8. **Withheld names its reason.** In the withheld state the surface states that
   at least 60 trading days of return history are required, so a researcher
   cross-referencing the Dashboard (which still shows an unfloored estimate for
   the same portfolio) reads the Risk tab as applying a deliberate threshold,
   not as missing data or a defect.

9. **Unavailable when there is no series.** With zero paired daily-return
   observations — empty portfolio, no price coverage for any holding, or no
   history context available — the Risk tab shows an unavailable state.

10. **Withheld is not collapsed to unavailable.** The withheld state (1–59
    observations) is visibly distinct from the unavailable state (0
    observations) and is never rendered or serialized as `unavailable`.

11. **Never a fabricated zero.** The figure is never shown as `0` or `0.00%` to
    stand in for absent or insufficient history. A zero appears only as a
    genuinely computed value at or above the floor.

12. **Methodology reachable from the surface.** A methodology reference for the
    annualized volatility figure is reachable from the Risk-tab surface (for
    example via the trust-badge tooltip or an adjacent link), pointing to the
    documented formula and to the 60-observation publication floor.

**Not asserted here:** the behaviour when N ≥ 60 and the return series has zero
variance — see Open decisions item 2.

## Test plan

Names the files and the behaviours; counts and individual test names are the
test lane's to determine.

**Backend / engine (pytest, `services/quant-engine/app/tests/`)**

- Volatility / risk-summary tests: the Risk-tab surface withholds (no value)
  at N in [1, 59]; publishes a number at N ≥ 60; reports unavailable at N = 0.
- Gate ordering: a sub-floor sample never reaches the computation's
  `len < 2 → 0.0` branch — i.e. the floor check runs *before* the volatility
  calculation, so N = 1 does not produce `0.00%` on this surface.
- Zero-variance case at N ≥ 60: a constant daily-return series is asserted
  against whatever Open decisions item 2 resolves to (publish `0.00%` or
  withhold); until then the test encodes the resolved choice, not a guess.
- Regression: the **Dashboard** surface (`volatility_summary.portfolio_volatility_pct`)
  is unchanged — still publishes its unfloored estimate from N ≥ 2 — and the
  deterministic dashboard goldens still regenerate clean.
- The state below the floor serializes as a distinct withheld signal, never as
  the unavailable signal (guardrail 4).

**Frontend (vitest, `apps/desktop/src/features/portfolio/`)**

- `RiskPanel.test.tsx` and the test colocated with whichever component renders
  the figure: published number with the `Synthetic` badge at N ≥ 60; withheld
  presentation with its stated 60-day reason at N in [1, 59]; unavailable
  presentation at N = 0; withheld and unavailable are visually distinct.
- The figure is never rendered as `0` / `0.00%` / `—` when the state is
  withheld or unavailable.
- A methodology reference is present and reachable from the surface.
- If a new audited card file is added, `apps/desktop/src/test/designSystem.audit.test.ts`
  is updated so the design-system audit still covers every card.

**Cross-surface**

- A single fixture that drives both surfaces confirms the Risk tab and the
  Dashboard show the same value to displayed precision at N ≥ 60, and diverge
  (number vs. withheld) somewhere in 2 ≤ N < 60.

## Tickets

Ordered. Contracts before consumers; the dedicated coverage ticket is its own.
**These tickets assume the tech-lead DESIGN pass has already settled the
contract** — the wire/card representation of the withheld state, the shared
floor constant, and how the reused value reaches the Risk tab. Sequence design
before `T-44.1.1`. No ticket instructs anyone to commit, run the suite, or gate
its own work; the human runs the suite and commits, and the orchestrator
dispatches the gates.

- **T-44.1.1 — Contract and methodology.** Establish, per the design pass, the
  representation for the figure and its published / withheld / unavailable
  states on the Risk tab, and the shared 60-paired-observation publication-floor
  threshold (distinct from `MIN_DAILY_OBSERVATIONS`). Amend
  `docs/finance/financial-methodology.md` § "Annualized realized volatility" to
  record the Risk-tab floor and the sub-floor trust states (N = 0 → unavailable,
  1–59 → withheld, not collapsed), keeping it separate from the per-position
  20-observation rule; cite `02-quant-research.md` § 2.4 for grounding. Mirror
  the contract into `docs/contracts/risk-fields.md` (new section) and
  cross-reference from `docs/contracts/diagnostics-fields.md`, plus any desktop
  type mirror. Traces AC 2, 3, 5, 7, 9, 10, 12.

- **T-44.1.2 — Apply the floor and emit the states (engine).** Gate the
  60-observation floor ahead of the volatility computation so a sub-floor sample
  never yields `0.0` on this surface; reuse the existing computed value with no
  recomputation; emit unavailable at N = 0, withheld at 1–59, published at
  ≥ 60. Resolve the zero-variance behaviour per Open decisions item 2 once the
  human has ruled. Carry the methodology test updates in this pass (guardrail
  1). Traces AC 5, 6, 7, 9, 10, 11.

- **T-44.1.3 — Render on the Risk tab.** Surface the published number with the
  `Synthetic` trust treatment; render the withheld state with its stated
  60-day reason and no number; render the unavailable state; make withheld and
  unavailable visually distinct; make a methodology reference reachable from
  the surface. Follow the `ui-polish` card scaffold (`03-scout.md` § ui-polish
  pattern). Traces AC 1, 2, 3, 4, 7, 8, 9, 10, 11, 12.

- **T-44.1.4 — Dedicated behavioural and cross-surface coverage.** The cases
  in the test plan: N = 0, N in [1, 59], N ≥ 60 happy path, cross-surface
  equality vs. the Dashboard, the zero-variance edge case, and the regression
  that the Dashboard surface still publishes its unfloored estimate. Traces
  AC 4, 6, 7, 9, 10, 11.

- **T-44.1.5 — Close-out reconciliation.** Update
  `docs/product/current-product-state.md` to list the annualized volatility
  figure in the Risk-tab shipped scope, reconciled from the actual diff. No
  roadmap, story-index, or status edits (the corpus does not exist; the docs
  lane owns those at close-out).

## Out of scope

- Benchmark volatility, downside volatility, tracking error, and the risk
  concentration figures that share the Dashboard Risk Summary card.
- A full "Risk Summary" card on the Risk tab.
- Any Risk-tab-native recomputation of volatility (for example from the
  distribution engine's population-basis `std_pct`) — the decision is reuse.
- Any change to the Dashboard surface of the figure, including adding a floor
  to it.
- Changing the product-wide `MIN_DAILY_OBSERVATIONS` (20) threshold or the
  sibling Risk-tab engines' trust vocabulary beyond what this figure needs.

## Notes / decisions

- **Reuse, not recompute** (work order; `02-quant-research.md` § 1). The
  producer's Option B (a Risk-tab-native figure from the distribution engine,
  population-N, differing sub-percent from the Dashboard) was considered and
  rejected by the human in favour of one scalar surfaced in two places. This
  keeps one documented formula and one code path (guardrail 2).
- **60-observation floor** (work order; `02-quant-research.md` § 2). At N = 20
  the 95% confidence interval on the estimate spans roughly ±35% of its value
  multiplicatively; at N = 60 the relative standard error roughly halves and
  the half-width at a typical 15% vol falls to about ±3pp. 60 is also the
  smallest window the Risk tab's distribution engine already uses. Full
  argument and citations: `02-quant-research.md` §§ 2.3–2.4.
- **Trust states below the floor** (`02-quant-research.md` § 3): N = 0 →
  unavailable (no input); 1–59 → withheld (input exists, annualized projection
  over a sub-quarter sample not trustworthy). Withheld is never collapsed to
  unavailable (guardrail 4).
- **Methodology change is an amendment, not a new section**
  (`02-quant-research.md` § 5.1) — it extends the existing "Annualized realized
  volatility" section.
- **This is net-new trust-state logic**, so guardrail 1 applies: the RESEARCH
  brief (`02-quant-research.md`) precedes implementation and a quant-audit
  follows it; both are dispatched by the orchestrator, not by a ticket here.
- Sibling stories could not be read for register calibration — the
  `docs/product/stories/` corpus was deleted at HEAD and this file recreates
  the directory.
