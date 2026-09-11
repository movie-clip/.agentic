REPORT 2026-09-11-risk-summary-audit-foldable/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order's verification field was NONE (read-only producer order)

contract_notes:
  - none

pack_corrections:
  - projects/portfolio/capabilities/product.md "Where the plan lives" — `epic-roadmap.md`, `prd/**` and `stories/README.md` no longer exist; deleted at commit `ce9c97d` — see § Placement.

handoff:
  - 1 story proposed, unticketed (Backlog-tier) — a fold/collapse toggle on the Dashboard's RiskSummaryCard — see § Stories
  - open decision: does the project still track epics now the planning corpus is deleted, or is US-44.1's no-epic pattern the norm — see § Open decisions
  - open decision: should this story set a reusable collapsible-card pattern, or stay a one-off toggle — see § Open decisions
  - no precedent for whole-card fold/collapse exists in the codebase today — see § Already covered

risks:
  - the deleted-roadmap finding rests on US-44.1's own account plus the deletion commit itself; no separate human ruling document was found
  - I did not open 01-quant-audit.md (not yet written when I read the run dir) — my verdict does not depend on its findings, per this order's non_goals

## Orchestrator brief
- verdict: new scope, Backlog-tier — not already covered, not a known-open deferral
- epic: none — the epic-roadmap and PRD corpus was deliberately deleted at `ce9c97d` (confirmed intentional via `US-44.1`'s recorded ruling); no active epic exists to place this under
- 1 story: PROPOSED, unticketed — "let the researcher collapse the Dashboard Risk Summary card"
- decision: needs a ticketed story, not a direct single-lane dispatch — the project's express-lane rule explicitly excludes "anything a user would see as new," and a fold/collapse control is a new interaction, even though its technical footprint (no schema/contract impact) is express-shaped
- blocks dispatch: nothing technical; two open decisions need the human before `story-author` runs — see § Open decisions
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement
There is no epic to place this under. `docs/product/epic-roadmap.md`, `docs/product/prd/**`, and `docs/product/stories/README.md` were deleted in commit `ce9c97d` ("cleanup", 2026-09-07), one commit before the current story file `US-44.1-risk-tab-annualized-volatility.md`. That story's own "Open decisions" section records the ruling directly: *"Epic 44 is not formalized: the planning corpus... was deleted at commit `ce9c97d` and is intentionally staying deleted, so there is no index to reconcile against and this file is the sole product-doc record."* That is a human ruling already made, not a gap I am filling in — I am not proposing to reopen it, only to apply it consistently.

Given that, the honest placement answer is: **no epic** (the concept has been retired), and this becomes a new one-off story file following the `US-44.1` precedent — the next available number in sequence (`US-45.1`, pending confirmation nothing else has claimed 45 since). The nearest *topical* precedent, if the human wants a loose grouping label rather than a formal epic, is `US-44.1` itself — both concern a Dashboard/Risk-tab risk card, though `US-44.1` touched the Risk tab's annualized-volatility card and this request touches the Dashboard tab's `RiskSummaryCard`, a different component.

## Stories

### PROPOSED: "Let the researcher collapse the Risk Summary card"
value: The researcher can collapse the Dashboard's Risk Summary card to a compact header when they don't need risk detail at a glance, and re-expand it, without losing anything else on the Dashboard. Checked against real density rather than asserted: `RiskSummaryCard.tsx` (`apps/desktop/src/features/portfolio/RiskSummaryCard.tsx`) renders up to 14 stat rows (11 always-shown metrics plus 2 conditional relative-risk metrics), the densest card on the Dashboard tab — the "clutter" claim holds up against the actual component, not just the request's framing.
slice: In — a fold/collapse control on `RiskSummaryCard` only: a toggle, an `aria-expanded` state, a collapsed rendering that keeps the card header and (recommended, not mandated — tech lead's call) a one-line rolled-up summary, e.g. current trust badge or nothing more than the label. Out — rolling the same control onto any other Dashboard/Exposure/Risk card; persisting the collapsed/expanded preference across sessions is a nice-to-have the story can accept or defer, not a hard requirement, since it needs no engine round-trip either way (pure client state or `localStorage`, no schema/contract touch).
depends_on: none hard. Soft: if `01-quant-audit` (running in parallel, not read for this brief per this order's non_goals) finds a correctness defect inside `RiskSummaryCard`'s rendering, sequencing the audit's fix before this story avoids the frontend lane touching the same file twice in close succession — not a blocker, just a scheduling preference for whoever runs both.
invest: Small and Valuable are solid (checked against real card density above). Weak on Independent only in the soft-dependency sense above. Estimable is solid — this is a bounded, single-component UI change with no data dependency.

## Sequence
1. (Optional, soft) Let `01-quant-audit`'s findings on `RiskSummaryCard` land first, or at least become known, so the frontend lane doing the fold/collapse work isn't racing a correctness fix to the same file. Not a hard gate — if the audit is still running when the human wants to proceed, proceeding first is fine; the fold control does not touch any value the audit would be checking.
2. `story-author` drafts `US-45.1` (or whatever number the human confirms is next) from this brief, once the two open decisions below are answered.
3. Ticketed story dispatches to `frontend-engineer` (single lane — no schema/contract impact, `ui-polish` skill governs the card work per the project's routing table) plus `test-engineer` for the toggle's test coverage.

## Open decisions
- **Epic/numbering going forward.** Does the project want to keep using bare `US-<n>.<m>` story files with no epic or roadmap index (the `US-44.1` precedent), or was the roadmap deletion meant to be temporary/is it due for reinstatement? This brief assumes the former (continuing the current precedent) since that is the only recorded ruling, but the human should confirm before `story-author` picks a number.
- **Scope of the fold pattern.** Should this story also produce a reusable collapsible-card primitive (e.g. a `<CollapsibleCard>` wrapper, documented in `docs/contracts/ui-design-system.md` and the `ui-polish` skill) since no whole-card fold/collapse precedent exists anywhere in the codebase today — see § Already covered — or should it stay a one-off toggle scoped to `RiskSummaryCard`, deferring the shared pattern until a second card actually needs it? Either is defensible; this is a design-investment call for the human/tech-lead, not something I should decide as the placement lane.

## Already covered
Not already covered, not a recorded/deferred decision. Checked:
- `docs/tech-debt-register.md` — no fold/collapse/interaction-pattern entry.
- `docs/contracts/ui-design-system.md` — no collapse/expand token, primitive, or pattern documented.
- `docs/product/stories/US-44.1-risk-tab-annualized-volatility.md` (the only story file that exists) — no mention of card foldability.
- Codebase precedent check: `DrawdownAnalyticsCard.tsx` (`apps/desktop/src/features/portfolio/DrawdownAnalyticsCard.tsx:420,470,494,499,510,545`) implements expand/collapse, but at the **row level** — each drawdown-episode table row toggles via `expandedKey` state and `aria-expanded` — not at the whole-card level. `FactorAttributionCard.tsx:329` has a comment referencing a "collapsible, scrollable" table body but no actual fold control in the code. No component in `apps/desktop/src/features/portfolio/**` collapses an entire card today. This request is the first instance of that pattern, which is why § Open decisions asks whether to build it as a reusable primitive now.
