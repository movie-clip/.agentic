REPORT 2026-09-09-risk-annualized-volatility/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   none
  result:    NOT_RUN
  detail:    Order verification field is NONE; read-only lane, no command to run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - verdict: defer to Backlog as one story; secondary verdict — the computation, the annualization convention and a minimum-history rule are ALREADY shipped on the Dashboard. See § Orchestrator brief.
  - blocks dispatch: the planning-doc corpus (epic-roadmap.md, prd/**, stories/**) was deleted from the tree in commit ce9c97d; this brief is built from git blob a1c60c8. Human must confirm intent before story-author runs. See § Placement.
  - 1 story proposed (Backlog, PROPOSED-vol-on-risk-tab) — see § Stories.
  - open decision (a): annualization convention — reuse house sqrt(252) or a Risk-tab-native variant. See § Open decisions.
  - open decision (b): minimum return history before a number may display — inherit the product-wide 20-observation floor or set a stricter annualized-vol floor. See § Open decisions.
  - already covered: portfolio annualized volatility ships on the Dashboard Risk Summary card (volatility_summary.portfolio_volatility_pct). See § Already covered.
  - quant RESEARCH needed only if the user rejects the existing sqrt(252) / 20-obs conventions — see § Open decisions.

risks:
  - Placement and dedupe were read from git blob a1c60c8 (parent of HEAD); HEAD commit ce9c97d deleted the roadmap, prd/** and stories/** from the tree. If that deletion was deliberate, the placement verdict is moot.
  - "Already covered" rests on claims I opened myself: financial-methodology.md:1012-1015, :1725-1739; dashboard-fields.md:37,:237; diagnostics-fields.md:216-222; risk-fields.md:240,:432; apps/desktop/src/features/portfolio/RiskPanel.tsx.
  - I did not run the app or the engine; whether portfolio_volatility_pct currently renders non-null for the committed IB2026 portfolio is asserted from the contract's trust rules, not observed.

## Orchestrator brief

- verdict: defer to Backlog (one story) — with a strong secondary "already covered" at the engine/methodology layer.
- epic: none active fits. Epic 41 (doc reconciliation) and Epic 42 (dependency vuln) are the only open epics; Epic 43 (seam consolidation) is Done. Epic 13 (Risk Analytics Tab) and Epic 25 (Dashboard Performance & Risk Summary) are the precedents; both complete.
- epic call: do NOT create a new epic for this (epic inflation — one small presentation slice with unresolved design questions). Backlog story, provisional sibling of Epic 25 / Epic 13; owner may instead pull it into a small new Risk-tab epic alongside the other carried Backlog UI story US-41.1.
- 1 story: PROPOSED-vol-on-risk-tab — "the researcher sees the portfolio's annualized volatility on the Risk tab". Single vertical slice, no dependency chain.
- dedupe: portfolio-level annualized realized volatility from synthetic-history daily returns is ALREADY computed and ALREADY shipped — on the Dashboard, in RiskSummaryCard, as volatility_summary.portfolio_volatility_pct. Formula: stdev(daily_returns) * sqrt(252), financial-methodology.md:1012-1015. Minimum-history rule already exists (MIN_DAILY_OBSERVATIONS = 20; the three Risk-tab engines already withhold below 20). It is NOT on the Risk tab, which has no summary area — RiskPanel.tsx hosts exactly Stress / Drawdown / VaR-Distribution cards.
- the request carries a false premise: there is no "risk summary area" on the Risk tab to place this "alongside". The Risk Summary card is Dashboard-only.
- both deferred decisions are already answered in methodology if the existing path is reused (sqrt(252); 20 observations). They are only genuinely open if the user wants a Risk-tab-native computation sourced from one of that tab's own engines (e.g. the distribution engine, which uses population-N std and 60/252/504 windows). Framed in § Open decisions — not resolved here.
- blocks dispatch: (1) human verdict on the two open decisions; (2) human confirmation that the ce9c97d deletion of the planning docs was not intended — story-author writes into docs/product/stories/, which does not currently exist.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**No active epic owns this.** From the roadmap snapshot (git blob `a1c60c8`,
`epic-roadmap.md:1-91`): Epic 41 (Documentation & Roadmap Accuracy
Reconciliation) and Epic 42 (Dependency Vulnerability Remediation) are the only
active epics; Epic 43 (Engine Seam Consolidation) is Completed. Neither active
epic is a feature epic and neither is a plausible home.

**Nearest precedents:**

- **Epic 25 — Dashboard Performance & Risk Summary** (complete). Story
  **US-25.3** built the `RiskSummaryCard` and its `volatility_summary`
  (portfolio / benchmark / downside volatility, tracking error) sourced from the
  already-fetched diagnostics response. Story **US-25.5** is an even closer
  shape match: it *surfaced an already-computed metric* (Information Ratio,
  "found unrendered during a project review") and *backfilled the methodology
  section* — no new math. This request is the same move, one tab over.
- **Epic 13 — Risk Analytics Tab** (complete). Created the Risk tab and its
  three cards. Any new Risk-tab surface is a sibling of this epic's work.
- **Epic 15 — Position-Level Analytics** (complete). Precedent for *adding a
  figure into an existing Risk-tab card* (drawdown decomposition into the
  Drawdown card) rather than adding a new card.

**Why this is not a new epic.** The product pack's epic-inflation rule: a
one-story epic needs a reason beyond "this needs somewhere to live", and the
Epic 16 quick-win precedent explicitly does not apply when the single story is
"small-to-medium with an unresolved design decision" — which this is (two, in
fact, plus the placement question). Backlog until it has siblings is the honest
verdict. If the owner wants it built now, the low-inflation route is to pull it
into a small Risk-tab epic together with the other carried Backlog trust-UI
story **US-41.1** (inline withheld-return annotation) — but epic creation is the
owner's call, not this lane's.

**Blocker on any placement.** HEAD commit `ce9c97d "cleanup"` deleted
`docs/product/epic-roadmap.md` (2090 lines), every file under
`docs/product/prd/`, every file under `docs/product/stories/`,
`stories/README.md`, `roadmap.md`, and the standalone review/findings docs, and
also gutted `CLAUDE.md` and `CONTEXT.md`. Untracked files
`agentic-architecture-build-brief.md` and `agentic-network-canary-test.md` sit
at the repo root. This looks like a deliberate repo-slimming, possibly a network
test fixture — but the order's own `scope` names those deleted paths as
authoritative, so the orchestrator that wrote the order does not know they are
gone. The human must rule on whether the PRD -> Story -> Ticket delivery model
is still in force before `story-author` (which writes into the now-absent
`docs/product/stories/`) can be dispatched.

## Stories

### PROPOSED-vol-on-risk-tab — The researcher sees the portfolio's annualized volatility on the Risk tab

  outcome:    A researcher looking at the Risk tab can read the portfolio's
              annualized volatility there, without switching to the Dashboard,
              rendered with the same "Synthetic" trust treatment as the tab's
              other figures; when return history is too short to compute it
              responsibly the surface shows a trust state, never a number.
  value:      Removes a tab-switch and a mental cross-reference. Today the
              figure exists only on the Dashboard Risk Summary card; the Risk
              tab — the product's designated pre-decision risk-budget view —
              shows stress, drawdown and a per-period (daily, non-annualized)
              std but no annualized portfolio volatility.
  slice:      IN — one annualized portfolio-volatility figure on the Risk tab
              with its trust/withheld state and a methodology reference.
              OUT (nearest) — benchmark volatility, downside volatility,
              tracking error and the concentration figures that share the
              Dashboard Risk Summary card; a full "Risk Summary" card on the
              Risk tab; any new engine computation if the existing
              diagnostics path is reused.
  depends_on: none — no other story. BUT gated by the human's ruling on the two
              open decisions below, and (if the user picks a Risk-tab-native
              computation) by a quant RESEARCH pass to settle the std
              convention and the minimum-observation floor before the story is
              authored.
  invest:     Weak on Estimable until decision (a) is made — "reuse the
              diagnostics figure" is a thin frontend slice; "new figure from a
              Risk-tab engine" is backend + quant + frontend. Weak on Valuable
              in the strict sense: the number is already reachable in the
              product, so the value is convenience/context, not a new
              capability. Both are acceptable for a Backlog item whose purpose
              is to hold the decision for the owner.

## Sequence

Single story — no internal sequence. The only ordering constraint is external:

1. Human rules on Open decisions (a) and (b), and on the deleted-planning-docs
   blocker in § Placement.
2. If the ruling selects a Risk-tab-native computation rather than reuse of the
   Dashboard diagnostics figure: quant RESEARCH pass (std convention,
   annualization factor, minimum-history floor) — risk-first, because its
   outcome decides whether this is a one-lane frontend slice or a full-stack
   story.
3. story-author drafts PROPOSED-vol-on-risk-tab.
4. Human approves the story.

## Open decisions

These are the user's to decide. Realistic options and trade-offs are laid out;
the quant lane supplies the rigor. Nothing here is picked.

### (a) Annualization convention

The house convention already exists and is documented:
`realized_vol = stdev(daily_returns) * sqrt(252)`, sample (N-1) standard
deviation, `financial-methodology.md:1012-1015` (§Annualized realized
volatility); the same `sqrt(252)` basis is used for downside volatility,
tracking error and currency-leg volatility across the product. So the real
decision is *which return series and which std convention this Risk-tab figure
draws on*, not what the annualization factor is:

- **Option A — reuse the Dashboard diagnostics figure.** Surface
  `volatility_summary.portfolio_volatility_pct` (already `stdev * sqrt(252)`,
  N-1) on the Risk tab. Pro: one formula, one code path (guardrail 2:
  methodology traceability); the Risk-tab number matches the Dashboard number to
  the cent; methodology already written; smallest slice. Con: couples the Risk
  tab to the diagnostics fetch, which is a different request from the tab's
  three self-fetching card engines.
- **Option B — Risk-tab-native from the distribution engine.** That engine
  already computes `std_pct` as population (N) std of daily returns over a
  60/252/504 window (`risk-fields.md:412`). Annualize it in place
  (`std_pct * sqrt(252)`), or add a sibling row. Pro: same engine, same trust
  badge, same window selector as the card it would sit in — "consistent with the
  other Risk tab metrics" in the literal sense. Con: population-N vs the
  Dashboard's sample-(N-1) makes the two figures differ by `sqrt(N/(N-1))`
  (~0.2% at N=252, ~0.8% at N=60) — the exact cross-surface discrepancy
  `financial-methodology.md` §US-27.9 already documents and tolerates, but the
  user should decide whether a sub-percent mismatch between the Risk tab and the
  Dashboard for "the same" metric is acceptable, or whether they must be
  sourced identically.
- **Option C — calendar / observed-trading-day basis** (e.g. scale by the
  actual trading-day count rather than a fixed 252). Rejected by house
  precedent everywhere else in the product; listed only for completeness. Con:
  the Risk-tab figure would then be the only annualized number in the product
  not on a `sqrt(252)` basis.

Question for the user: **one portfolio-volatility number surfaced in two
places, or a Risk-tab-native figure that may differ sub-percent from the
Dashboard's?** If Option A, decisions (a) and (b) are effectively already made
and no quant RESEARCH pass is needed. If B or C, quant RESEARCH settles the std
convention and annualization factor before story-authoring.

### (b) Minimum return history before a number may display

The product already has a floor, applied consistently across all three
Risk-tab engines: **20 daily observations** (`MIN_DAILY_OBSERVATIONS`).
Distribution withholds (`trust = unavailable`) below 20 daily returns
(`risk-fields.md:432`); drawdown withholds below 20 observations
(`risk-fields.md:240`); per-position beta/correlation/volatility go null below
20 (`financial-methodology.md:1725-1739`).

- **Option A — inherit the 20-observation floor.** Pro: consistency with every
  sibling metric on the tab; no new constant; a researcher never sees the
  distribution card populate while the volatility figure withholds at the same
  N. Con: 20 trading days is ~1 month; annualizing a one-month sample by
  `sqrt(252)` scales its estimation error with it and produces a noisy yearly
  figure — arguably exactly the "not enough history to compute it responsibly"
  case the user wants withheld.
- **Option B — a stricter annualized-vol floor**, e.g. 60 (~3 months) or 252
  (~1 year) trading days, on the argument that annualization multiplies
  sampling error and a sub-quarter base should not be scaled to a year. Pro: a
  more defensible published number. Con: introduces a new threshold more
  restrictive than the sibling metrics, so the tab would show a daily `std_pct`
  at N=40 but withhold its annualized form — needs a one-line UI rationale for
  the asymmetry.
- **Option C — tie the floor to the window selector.** If the figure lives in
  the distribution card (windows 60/252/504), the effective minimum is the
  smallest window, 60. If it is a standalone summary with a "Max" option like
  the Drawdown card, the floor question is live and independent.

Question for the user: **does annualized volatility inherit the product-wide
20-observation floor, or does annualization justify a stricter minimum — and if
stricter, what number?** The quant lane supplies the estimation-error argument
and a defensible threshold; the choice between "consistency" and "a stricter,
more defensible number" is the user's.

## Already covered

**Portfolio-level annualized volatility from synthetic-history daily returns is
already computed and already shipped — on the Dashboard, not the Risk tab.**

- `RiskSummaryCard.tsx` renders "Portfolio Volatility" from
  `diagnosticsAnalysis.volatility_summary` (`dashboard-fields.md:37`, `:237`).
- The field is `volatility_summary.portfolio_volatility_pct`, sourced from
  `risk_summary.portfolio_volatility_pct` (`diagnostics-fields.md:216-218`).
- Formula: `realized_vol = stdev(daily_returns) * sqrt(252)`, in
  `analytics/risk.py`, documented at `financial-methodology.md:1012-1015`
  (§Annualized realized volatility, under §Volatility and Relative Risk).
- Trust class: synthetic history; `n/a` per null field, whole-card `EmptyState`
  when the diagnostics payload or its summary sub-objects are absent
  (`dashboard-fields.md:237`).
- Built by **US-25.3** (Epic 25); `stories/README.md:264-274` (git blob
  `a1c60c8`).

**A minimum-history rule already exists.** `MIN_DAILY_OBSERVATIONS` = 20, from
`core/constants.py`, applied as the withhold/null floor by the distribution
engine (`risk-fields.md:432`), the drawdown engine (`risk-fields.md:240`) and
per-position risk statistics (`financial-methodology.md:1725-1739`).

**What is genuinely not covered:** the figure appearing on the **Risk tab**.
`apps/desktop/src/features/portfolio/RiskPanel.tsx` hosts exactly three cards —
`StressScenariosCard`, `DrawdownAnalyticsCard`, `VarDistributionCard` — and
`risk-fields.md` documents only those three surfaces (US-13.1 / 13.2 / 13.3).
There is **no risk-summary area on the Risk tab**; the request's phrase "the
risk summary area" describes the Dashboard's card, not anything on the Risk tab.
The Risk tab's only volatility-adjacent figure today is the VaR/Distribution
card's `std_pct` — a per-period (daily) population-N standard deviation, not
annualized (`risk-fields.md:412`).

**No existing or prior story proposes this.** Searched the story index and all
story filenames at `a1c60c8`: US-25.3 and US-25.5 put volatility on the
*Dashboard* Risk Summary card; US-30.5b gates *per-position* volatility;
US-13.x built the Risk tab's three cards. None proposes a portfolio-level
annualized volatility figure on the Risk tab. No deliberately-left-open finding
covers it either (Epic 34's open findings F-1a / F-10 / F-12 are drawdown- and
replay-scoped; the roadmap's open-items list at `epic-roadmap.md:21-60` does not
mention Risk-tab volatility).
