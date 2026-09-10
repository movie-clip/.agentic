REPORT 2026-09-09-risk-annualized-volatility/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   none
  result:    NOT_RUN
  detail:    Read-only recon lane; order verification field is NONE.

contract_notes:
  - docs/contracts/risk-fields.md documents only the three existing Risk-tab engine surfaces (US-13.1/13.2/13.3) and has no section for any portfolio-level volatility figure; surfacing portfolio_volatility_pct on the Risk tab needs a new section there (and a cross-reference in diagnostics-fields.md), regardless of Option A or B.

pack_corrections:
  - none

handoff:
  - RiskPanel composition: RiskPanel.tsx renders exactly three cards in `.risk-shell-stack` (StressScenariosCard, DrawdownAnalyticsCard, VarDistributionCard); it self-fetches only the stress engine and has no summary or figure surface. see § RiskPanel and the three cards
  - Per-card fetch model: DrawdownAnalyticsCard and VarDistributionCard each self-fetch their engine via a useEffect on [snapshot, selectedWindow] and own their WindowSelector state; StressScenariosCard is prop-driven from RiskPanel. see § Fetch models compared
  - Dashboard vs Risk fetch: the Dashboard does one App-level diagnostics fetch reused across its cards; the Risk tab makes three independent per-card engine calls and shares no state. see § Fetch models compared
  - Wire origin: `volatility_summary.portfolio_volatility_pct` originates at analytics/risk.py:507 and is carried on both `volatility_summary` and the full `risk_summary` in the diagnostics response. see § Backend origin of portfolio_volatility_pct
  - Formula and convention: sample (N-1) stdev x sqrt(252); documented at financial-methodology.md:1012-1016; no minimum-observation floor in this path. see § Backend origin of portfolio_volatility_pct
  - Dashboard consumption: RiskSummaryCard.tsx reads `diagnosticsAnalysis.volatility_summary.portfolio_volatility_pct`, fed from App.tsx state through DashboardPanel. see § Dashboard consumption
  - Is diagnostics fetched in the Risk tab data path? No — but the response object already sits in App state (`diagnosticsAnalysis`, App.tsx:287) before the Risk tab renders; RiskPanel is currently passed only `snapshot`. see § Two options for surfacing on the Risk tab
  - 60-obs gate input already on the wire: `risk_summary.observations` (schemas/reconciliation.py:90; TS types.ts:86); DiagnosticsEngineResponse carries the full `risk_summary`. see § The 60-observation gate
  - No existing withhold gate on `portfolio_volatility_pct` (risk.py:507 gates only on a non-empty sample list); the 20-obs MIN_DAILY_OBSERVATIONS floor lives only in the distribution/drawdown engines, so a 60-obs gate is net-new wherever it lands. see § The 60-observation gate
  - ui-polish card scaffold: `<CardShell title badge={<TrustBadge/>} actions={<WindowSelector/>}>` plus EmptyState/LoadingState/ErrorState and ChartShell/chartDefaults, tokens only, enforced by designSystem.audit.test.ts. see § ui-polish pattern
  - Full frontend + backend touch list, enumerated by lane for both options. see § Blast radius by lane

risks:
  - `_calculate_annualized_volatility` (risk.py:2118) returns 0.0 (not None) when `len(values) < 2`, and build_portfolio_risk_summary only null-guards on an empty list — so at exactly 1 paired return the wire carries `portfolio_volatility_pct = 0.0`. The current Dashboard figure is not strictly clean at tiny N; a 60-obs gate would mask this.
  - I did not run the app or engine. Whether `diagnosticsAnalysis` is reliably non-null in App state when the Risk tab renders for the committed IB2026 portfolio is inferred from the analyze/restore code paths (App.tsx:483-513, 542-590), not observed; if exposure analysis throws, `setDiagnosticsAnalysis` may not fire.
  - `risk_summary.observations` counts PAIRED portfolio+benchmark daily returns (risk.py:492-503), not the distribution engine's unpaired `return_count`. A 60-obs gate keyed on it gates a slightly different series than the VaR card's N — quant lane should confirm that is acceptable.
  - `docs/contracts/dashboard-fields.md` and `risk-fields.md` ("Last updated 2026-06-01") predate recent epics; they look current for the surfaces they cover but neither anticipates cross-tab reuse of the volatility figure.

## Orchestrator brief

Read-only recon: Risk-tab metric fetch/shape/trust/render, plus the shortest path to surface portfolio annualized volatility on the Risk tab with a 60-observation withhold gate. Nothing changed.

- Risk tab = 3 self-fetching cards, no summary surface; Dashboard uses one App-level diagnostics fetch. See § RiskPanel and the three cards, § Fetch models compared.
- `portfolio_volatility_pct` = sample-(N-1) stdev x sqrt(252) at analytics/risk.py:507; carried on `volatility_summary` + `risk_summary`; consumed by RiskSummaryCard. See § Backend origin of portfolio_volatility_pct, § Dashboard consumption.
- Diagnostics response not wired to the Risk tab but already in App state (App.tsx:287): Option A = prop-thread, no new fetch; Option B = new gated field. See § Two options for surfacing on the Risk tab, § Blast radius by lane.
- No withhold gate on the figure today; `risk_summary.observations` is on the wire as the 60-obs gate input; any gate is net-new trust logic (quant lane). See § The 60-observation gate.
- Trust-state rendering and the card scaffold a new figure must match: see § Trust-state representation and rendering, § ui-polish pattern, § Sources of truth.

## RiskPanel and the three cards

`apps/desktop/src/features/portfolio/RiskPanel.tsx` (103 lines total):
- Props: `{ snapshot: PortfolioSnapshot | null }` (line 23-25). Mounted in
  App.tsx:909-914 inside `{tab === 'risk' ? ... }`, lazy-loaded (App.tsx:16),
  passed `snapshot={dashboardSnapshot}` and nothing else.
- No-snapshot branch (lines 59-72): thin `<main className="exposure-shell">`
  header, no cards.
- Self-fetches the stress engine only: `useEffect(... runStressEngine(snapshot)
  ...)` lines 36-55, into a `StressState` union.
- Render (lines 79-101): `<main className="exposure-shell">` + `<header
  className="exposure-header">` (eyebrow `panel-label` + `<h2>`), then
  `<div className="risk-shell-stack">` containing:
  - `<StressScenariosCard scenarios trust loading error coverage />` — fully
    prop-driven (RiskPanel owns the fetch).
  - `<DrawdownAnalyticsCard snapshot={snapshot} />` — self-fetching.
  - `<VarDistributionCard snapshot={snapshot} />` — self-fetching.

`StressScenariosCard.tsx`: pure presentational; `CardShell` title "Stress
Scenarios", `TrustBadge type={trust}` (trust is `'synthetic'|'unavailable'`),
no WindowSelector. EmptyState when `trust === 'unavailable'`.

`DrawdownAnalyticsCard.tsx`: self-fetching, owns `selectedWindow`
(252/756/1260/null) + a fallback cascade. `CardShell` title "Drawdown
Analytics", `TrustBadge`, `WindowSelector` in actions. Local
`MIN_OBSERVATIONS = 20` (line 63) — a defensive mirror of the engine constant;
EmptyState when `trust === 'unavailable'` OR `underwater_series.length < 20`
(lines 699-705).

`VarDistributionCard.tsx`: self-fetching, owns `selectedWindow` (60/252/504,
default 252). `CardShell` title "VaR & Distribution", `TrustBadge`,
`WindowSelector`. Local `MIN_OBSERVATIONS = 20` (line 42); EmptyState when
`trust === 'unavailable'` OR `return_count < 20` (lines 342-348). Renders a
"Std" row (`response.std_pct`) in its "Distribution shape" section (line 267) —
this is a per-period (daily) population-basis std, NOT annualized.

## Fetch models compared

Risk tab: three independent `POST /api/engines/{stress,drawdown,distribution}
/run` calls, each triggered by a card's own `useEffect`, each rebuilding the
request via `buildSnapshotAnalysisRequest(snapshot)` in
`portfolioAnalysisAdapter.ts` (runStressEngine line 461, runDrawdownEngine
line 402, runDistributionEngine line 432). No shared state; RiskPanel holds
only the stress result.

Dashboard / App: `runDiagnosticsEngine` / `runImportedDiagnosticsEngine`
(adapter lines 133-171) is called once inside `analyzeExposureSnapshot`
(App.tsx:483-488, `Promise.all([runExposureEngine, runDiagnosticsEngine])`)
and `analyzeRestoredSnapshot` (App.tsx:553-570). Result stored in App state
`diagnosticsAnalysis` (App.tsx:287, `setDiagnosticsAnalysis` line 498) and
passed down to DashboardPanel → RiskSummaryCard. These analyze paths run on
import and on workspace restore, independent of which tab is active.

## Backend origin of portfolio_volatility_pct

- Route: `POST /engines/diagnostics/run` — `api/routes/diagnostics.py`
  (registered in `app/api/main.py`). Response model `DiagnosticsResult`.
- Schema: `schemas/diagnostics.py` — `DiagnosticsVolatilitySummary`
  (lines 94-98): `portfolio_volatility_pct / benchmark_volatility_pct /
  downside_volatility_pct / tracking_error_pct`, all `float | None = None`.
  `DiagnosticsResult` carries both `volatility_summary` (line 116) and the full
  `risk_summary: PortfolioRiskSummary` (line 118).
- `PortfolioRiskSummary` — `schemas/reconciliation.py:85-95`: has
  `observations: int`, `portfolio_volatility_pct: float | None`,
  `benchmark_volatility_pct: float | None`, plus beta/correlation/r_squared.
- Service: `services/diagnostics_engine.py:326` calls
  `build_portfolio_risk_summary(...)`; lines 408-410 copy
  `risk_summary.portfolio_volatility_pct` into `DiagnosticsVolatilitySummary`.
  The unavailable path (lines 486-497) emits `DiagnosticsVolatilitySummary()`
  (all None) and `PortfolioRiskSummary(... portfolio_volatility_pct=None ...)`.
- Analytics: `analytics/risk.py:491-509` `build_portfolio_risk_summary`.
  Line 507: `portfolio_volatility_pct = round(_calculate_annualized_volatility
  (portfolio_samples) * 100, 2) if portfolio_samples else None`. `portfolio_
  samples` = the portfolio leg of `_paired_portfolio_and_benchmark_returns`
  (line 492-493). `_calculate_annualized_volatility` (risk.py:2117-2120):
  `if len(values) < 2: return 0.0; return _sample_standard_deviation(values)
  * sqrt(252)`. `_sample_standard_deviation` (line 2134) → `_sample_variance`
  (line 2129) uses `/(len-1)` — sample / (N-1) convention.
- Methodology: `docs/finance/financial-methodology.md:1012-1016`
  (§Annualized realized volatility, `realized_vol = stdev(daily_returns) *
  sqrt(252)`). Cross-convention note at :1006-1010 (sample vs population,
  ~0.2% at N=252, US-27.9 "document not standardize"). No explicit minimum-
  observation floor stated in this section (contrast per-position stats at
  :1725-1739 which do cite MIN_DAILY_OBSERVATIONS = 20).

## Dashboard consumption

`apps/desktop/src/features/portfolio/RiskSummaryCard.tsx`:
- Props `{ diagnosticsAnalysis: DiagnosticsEngineResponse | null }` (line 32-34).
- `unavailable` guard lines 37-43: null response, or
  `availability.historical_sections_available === false`, or any of
  `volatility_summary` / `drawdown_summary` / `risk_concentration_summary`
  absent → whole-card `<EmptyState title="Risk metrics unavailable" ... />`
  inside `<section className="summary-card risk-summary-card">` (lines 44-54).
  NOTE: this card does NOT use CardShell/primitives beyond EmptyState — it is
  a Dashboard-era card (dashboard-fields.md:237 "not migrated to design
  system").
- Happy path: `formatPct(vol.portfolio_volatility_pct)` → `n/a` when null else
  `${x.toFixed(2)}%`, rendered as the "Portfolio Volatility" metric (lines
  71-74). Trust label from `run_metadata.section_trust.risk_contribution_path`
  via `sectionTrustLabel` → "Verified" / "Degraded" / "Unavailable" (lines
  21-30, 57, 68) — a diagnostics-specific ladder, distinct from the Risk-tab
  `TrustBadge` synthetic/unavailable vocabulary.
- Wiring: App.tsx:870 `diagnosticsAnalysis={diagnosticsAnalysis}` →
  DashboardPanel.tsx:38 prop → DashboardPanel.tsx:125
  `<RiskSummaryCard diagnosticsAnalysis={diagnosticsAnalysis} />`.
- Contract: `docs/contracts/dashboard-fields.md:37, :237` (RiskSummaryCard
  from `diagnosticsAnalysis.volatility_summary`, "separate App.tsx state, not
  `analysis`", `n/a` per null field, whole-card EmptyState). Source field
  chain: `docs/contracts/diagnostics-fields.md:216-224`
  (`volatility_summary.portfolio_volatility_pct` sourced from
  `risk_summary.portfolio_volatility_pct`).

## Two options for surfacing on the Risk tab

Facts only; tech-lead DESIGN chooses.

Option A — reuse the already-fetched diagnostics response.
- The `DiagnosticsEngineResponse` object is already in App state
  (`diagnosticsAnalysis`, App.tsx:287) whenever a portfolio is loaded. No new
  network call.
- Files touched: `App.tsx` (add `diagnosticsAnalysis={diagnosticsAnalysis}` to
  `<RiskPanel>` at line 912); `RiskPanel.tsx` (add prop to `RiskPanelProps`,
  thread to wherever the figure renders); one component to render the figure
  (either a new small card/row in RiskPanel's `.risk-shell-stack`, or a prop
  into an existing Risk card — DESIGN decides). Optionally `RiskPanel.test.tsx`,
  new-component test (test lane).
- No schema, no route, no analytics, no backend. `docs/contracts/risk-fields.md`
  needs a new section; `docs/contracts/diagnostics-fields.md` may need a
  cross-reference.
- Trade-off on record (delivery brief § Open decisions (a)): couples the Risk
  tab to the diagnostics fetch shape rather than to a Risk-tab engine.

Option B — new (gated) field on an existing Risk-tab response, or a new
Risk-tab engine call.
- e.g. add `annualized_volatility_pct` (+ its own gate) to
  `DistributionEngineResponse` (`schemas/distribution.py:46-75`), computed in
  `services/distribution_engine.py` from the same `returns` list it already
  builds (line 123), annualized `* sqrt(252)`. Distribution currently uses
  population-basis std in `analytics/distribution.py` `compute_distribution_
  shape` — quant lane owns whether to reuse that or match risk.py's (N-1).
- Files touched: `schemas/distribution.py`, `services/distribution_engine.py`,
  `analytics/distribution.py` (if a new stat fn), `apps/desktop/src/features/
  portfolio/types.ts` (`DistributionEngineResponse`), `VarDistributionCard.tsx`
  (render the row), `docs/contracts/risk-fields.md`,
  `docs/finance/financial-methodology.md`, backend + frontend + quant-audit
  regression tests. This is the full-stack path and is schema-touching, so it
  is NOT express-lane eligible (project.md § express lane).

## The 60-observation gate

Current state:
- `portfolio_volatility_pct` has NO withhold gate beyond `if portfolio_samples`
  (non-empty) at `analytics/risk.py:507`. With 1 sample it emits 0.0 (see
  risks). With ≥2 it emits a real number regardless of N.
- `MIN_DAILY_OBSERVATIONS = 20` lives in `services/quant-engine/app/core/
  constants.py:19`. Applied in: `distribution_engine.py:124`
  (`len(returns) < MIN_DAILY_OBSERVATIONS` → `_empty_response`),
  `drawdown_engine.py:124` (daily_returns) and `:130` (underwater series),
  plus `correlation_engine.py`, `intra_correlation_engine.py`,
  `currency_risk.py`, and `analytics/distribution.py` (each stat fn re-checks).
  Frontend mirrors: `MIN_OBSERVATIONS = 20` literal in
  `DrawdownAnalyticsCard.tsx:63` and `VarDistributionCard.tsx:42`.
- `analytics/risk.py:83` also defines `WINDOW_MIN_OBSERVATIONS = {20:25, 60:75,
  252:275}` — a per-window OLS buffer, a DIFFERENT concept (constants.py:17-18
  says so explicitly).

What a 60-obs gate needs to hook into:
- Frontend-only (fits Option A): read `diagnosticsAnalysis.risk_summary.
  observations` (already on the wire — schema `reconciliation.py:90`, TS
  `types.ts:86`) and render the withheld/EmptyState/`n/a` treatment when
  `observations < 60`. New constant (e.g. `MIN_ANNUALIZED_VOL_OBSERVATIONS =
  60`) in the frontend; no backend touch.
- Backend (fits Option B, or a stricter diagnostics gate): a new threshold
  constant in `core/constants.py`, applied either in
  `analytics/risk.py:507`/`build_portfolio_risk_summary` (would also change the
  DASHBOARD figure — regression goldens + quant-audit) or in a new Risk-tab
  engine path. Note `risk_summary.observations` counts PAIRED portfolio+
  benchmark returns, not the distribution engine's unpaired `return_count`.
- Either way this is net-new financial/trust logic → guardrail 1: quant lane
  (RESEARCH before, AUDIT after) and a methodology update in the same change.

## Trust-state representation and rendering

Risk-tab engines (schemas): each response has a `trust` field, Literal
`"synthetic" | "unavailable"` (e.g. `schemas/distribution.py:18`,
`DistributionTrustLevel`; stress uses `StressTrustLevel`). No `verified` /
`degraded` on Risk-tab surfaces — `risk-fields.md:8-25` "All fields ...
synthetic history trust class. No Risk-tab field is ever `verified`." Nullable
fields return `null` (never fabricated 0) on the unavailable path.

Diagnostics (schemas): richer ladder. `run_metadata.section_trust.*` is
Literal `"verified_adjusted_close" | "degraded_unverified_return_basis" |
"unavailable"` (`types.ts:1084-1088`); `availability.status` is `"ok" |
"unavailable"` with `historical_sections_available: boolean`
(`types.ts:1117-1122`). Individual metrics are `float | None`.

Risk-tab card rendering of each state (file:line):
- unavailable / withheld → `<EmptyState title detail />`
  (`primitives/EmptyState.tsx`). StressScenariosCard.tsx:150-154 (`trust ===
  'unavailable'`); DrawdownAnalyticsCard.tsx:699-705 (`trust === 'unavailable'
  || underwater_series.length < MIN_OBSERVATIONS`); VarDistributionCard.tsx:
  342-348 (`trust === 'unavailable' || return_count < MIN_OBSERVATIONS`).
- loading → `<LoadingState message />`; error → `<ErrorState title detail />`.
- per-cell missing value → local `formatPct`/`formatMagnitudePct` return `'—'`
  (VarDistributionCard.tsx:61-64, DrawdownAnalyticsCard.tsx:82-85), styled with
  `var(--color-text-disabled)` (VarDistributionCard.tsx StatRow lines 197-225).
- synthetic badge → `<TrustBadge type={trust} tooltip=... />` in the CardShell
  badge slot.
Dashboard RiskSummaryCard differs: whole-card EmptyState on any missing
sub-object (RiskSummaryCard.tsx:37-54); per-field `n/a` string via
`formatPct`/`formatRatio` (lines 4-10); it does NOT use TrustBadge — it prints
a "Risk contribution basis: {Verified|Degraded|Unavailable}" helper line
(line 68) from `sectionTrustLabel`.

## ui-polish pattern

Source: `.claude/skills/ui-polish/SKILL.md` (repo skill; project.md marks it
mandatory for any card work, enforced by
`apps/desktop/src/test/designSystem.audit.test.ts` — 5 checks: no literal hex,
no literal px on margin/padding/gap/fontSize/borderRadius, TrustBadge primitive
imported, "Synthetic" string single-source, chartDefaults imported).

Tokens: all in `apps/desktop/src/app/styles.css` `:root`. Spacing
`--space-xxs..--space-2xl` (2..32px); text colors `--color-text-{primary,
secondary,muted,disabled,on-accent}`; borders `--color-border-{subtle,default,
strong,card}` + `--border-thin/-medium`; typography `--font-{chart-tick,
caption,body-sm,body,heading-sm}`; semantic `--color-value-{positive,negative}`;
trust `--color-trust-badge-{bg,text,border}`; radius `--radius-{sm,md}`. Used
as `style={{ color: 'var(--color-text-muted)' }}` — never literals.

Primitives (`apps/desktop/src/app/primitives/`, no barrel — import each):
`CardShell` (`{ title, badge?, actions?, className?, children }` →
`<section className="compact-chart-panel" role="region" aria-labelledby>` with
header row: `panel-label` title + badge slot right of it + actions far right),
`TrustBadge` (`{ type: 'synthetic'|'unavailable', tooltip? }`), `WindowSelector`
(`<T>`, `{ options, value, onChange, labelFn?, ariaLabelFn? }`, `role="group"`,
`aria-pressed`), `EmptyState` (`{ title, detail? }`), `LoadingState`
(`{ message? }`), `ErrorState` (`{ title?, detail? }`, error accent border),
`ChartShell` (`{ ariaLabel (required), height?, children }`, `role="img"`),
`chartDefaults` (spread `defaultChartGrid`/`defaultAxisTickStyle`/
`defaultMinTickGap`/`defaultTooltipContentStyle` onto Recharts).

Card scaffold a new figure/row must match: wrap in `<CardShell title=...
badge={<TrustBadge type="synthetic" tooltip="Computed from current holdings
applied to historical prices." />} actions={<WindowSelector .../>}>`; render
idle/loading/error/unavailable via the state primitives; a scalar figure that
is not a chart is a labelled row (see VarDistributionCard `StatRow`,
lines 197-226: flex row, `var(--font-body-sm)`, `fontVariantNumeric:
'tabular-nums'`, `'—'` + `var(--color-text-disabled)` when missing). Colocated
`<Name>.test.tsx` with adapter-mocked tests is required. Canonical full example
at SKILL.md lines 196-274. NOTE: if a NEW card file is added to the audited
surface, update `ALL_CARD_FILES` / `CARDS_WITH_BADGE` in
`designSystem.audit.test.ts`.

## Blast radius by lane

Option A (reuse the diagnostics figure) — smallest:
- frontend: `apps/desktop/src/app/App.tsx` (pass `diagnosticsAnalysis` to
  `<RiskPanel>` line 912); `apps/desktop/src/features/portfolio/RiskPanel.tsx`
  (prop + render location); the figure component — either a new file
  `apps/desktop/src/features/portfolio/<Name>.tsx` in `.risk-shell-stack`, or a
  new prop on an existing Risk card; frontend constant for the 60-obs gate.
- test: `apps/desktop/src/features/portfolio/RiskPanel.test.tsx`, new
  `<Name>.test.tsx`; if the component is audited, `apps/desktop/src/test/
  designSystem.audit.test.ts`.
- docs: `docs/contracts/risk-fields.md` (new section); `docs/contracts/
  diagnostics-fields.md` (cross-ref); `docs/finance/financial-methodology.md`
  (§Annualized realized volatility — add the Risk-tab surface + the 60-obs
  withhold rule); `docs/product/current-product-state.md` (Risk tab scope).
- quant: RESEARCH + AUDIT on the 60-obs threshold and the withhold semantics
  (guardrail 1) even though the formula is unchanged.
- backend: none for the figure itself; a backend gate is only needed if the
  team wants the withhold enforced server-side.

Option B (new gated Risk-tab field) — adds, on top of the above frontend/docs/
test/quant work:
- backend: `services/quant-engine/app/schemas/distribution.py` (new field +
  the schema-edit hook fires → TS + contract in same pass);
  `services/quant-engine/app/services/distribution_engine.py` (compute +
  gate); `services/quant-engine/app/analytics/distribution.py` (if a new
  stat fn); possibly `services/quant-engine/app/core/constants.py` (threshold);
  register nothing new (route exists).
- frontend: `apps/desktop/src/features/portfolio/types.ts`
  (`DistributionEngineResponse`); `VarDistributionCard.tsx` (render row).
- test: `services/quant-engine/app/tests/test_analytics.py` +
  distribution-engine tests; `VarDistributionCard.test.tsx`.
- Not express-lane eligible (schema + analytics touch).

Shared (either option): `docs/tech-debt-register.md` only if something is
deferred. `CONTEXT.md` if a new vocabulary term is introduced.

## Sources of truth

- `docs/finance/financial-methodology.md:1012-1016` — §Annualized realized
  volatility (formula). :1006-1010 — sample vs population convention note.
  Governs any math change; looks current.
- `docs/contracts/diagnostics-fields.md:202-228` — History-Derived Summary
  Fields, `volatility_summary` / `risk_summary` field chain. Current for the
  diagnostics response.
- `docs/contracts/dashboard-fields.md:37, 237, 274` — RiskSummaryCard wiring
  and null/EmptyState behaviour. Current for the Dashboard surface.
- `docs/contracts/risk-fields.md` — Epic 13 Risk tab; "Last updated
  2026-06-01"; documents ONLY stress / drawdown / distribution. No portfolio-
  volatility surface — a gap a new figure must fill.
- `docs/product/current-product-state.md` — shipped Risk-tab scope (per
  CLAUDE.md; not re-read here).
- `.claude/skills/ui-polish/SKILL.md` + `docs/contracts/ui-design-system.md` —
  card design system; enforced by the audit test.
- `services/quant-engine/app/schemas/` is the contract source of truth
  (project.md); `app/core/constants.py` is the single home for shared
  analytics thresholds (US-24.3).
