# Capability pack: frontend — project `portfolio`

For the `frontend-engineer` lane. Everything about `apps/desktop/`.

The design system here is **mechanically enforced** —
`apps/desktop/src/test/designSystem.audit.test.ts` runs five checks every test
run and fails the build. A card built from generic React instincts will be red.
Read this pack and `portfolio/.claude/skills/ui-polish/SKILL.md` before writing
a component; the skill has the full token inventory.

Contract doc: `docs/contracts/ui-design-system.md`.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Tokens — never a literal** · **Guardrails, in UI terms** · **Do not opportunistically migrate** · **The five audit checks** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Layout | you are adding a file, or looking for where one lives |
| The eight primitives | your order builds or changes any UI |
| The canonical card pattern | your order adds or changes a card |

---

## Layout

```
apps/desktop/src/
  app/
    App.tsx, apiBase.ts, dashboardSession.ts, portfolioDb.ts, styles.css
    primitives/           the eight design-system primitives + chartDefaults
  features/
    portfolio/            holdings, exposure, diagnostics, dashboard cards
      types.ts            TS types — MUST mirror Pydantic schemas exactly
      portfolioAnalysisAdapter.ts   engine call adapters
    market-data/, llm/, settings/
  test/
    setup.tsx             Recharts ResponsiveContainer shim
    designSystem.audit.test.ts      the audit — read ALL_CARD_FILES
    dashboardGoldens.ts   GENERATED — never hand-edit
```

## Tokens — never a literal

All tokens live in the `:root` block of `app/styles.css`. Use
`style={{ color: 'var(--color-text-muted)' }}`. Never a hex, never a raw pixel
on a spacing/size style prop.

- Text: `--color-text-primary | -secondary | -muted | -disabled | -on-accent`
- Surfaces: `--color-surface-panel | -elevated | -overlay`
- Borders: `--color-border-subtle | -default | -strong | -card`; `--border-thin: 1px`, `--border-medium: 2px`
- Spacing: `--space-xxs 2 · xs 4 · sm 8 · md 12 · lg 16 · xl 24 · 2xl 32`
- Type: `--font-chart-tick 11 · caption 12 · body-sm 13 · body 14 · heading-sm 16`
- Radius: `--radius-sm 3`, `--radius-md 8`
- Semantic value: `--color-value-positive | -negative`; error: `--color-error`, `--color-error-border`
- Chart lines: `--color-line-correlation | -beta | -portfolio | -benchmark`
- Correlation palette (5 levels for ρ), factor palette (one token per factor,
  `--color-factor-*` with `--color-factor-default` fallback), trust-badge trio —
  see the `ui-polish` skill for the full lists.

**The JSDOM exception.** CSS variables do not parse in *numeric* CSS props
(`opacity`, `lineHeight`, `zIndex`). Use the literal with a comment there;
`--opacity-unavailable: 0.55` exists for CSS-class usage, not React inline
style on a numeric prop. `BenchmarkCorrelationTable.tsx` documents the pattern.

## The eight primitives

At `app/primitives/`, imported individually (no barrel export):

| Primitive | Use |
|---|---|
| `CardShell` `{title, badge?, actions?, className?}` | outer wrapper for **every** card; gives `role="region"` + `aria-labelledby` |
| `TrustBadge` `{type: 'synthetic'\|'unavailable', tooltip?}` | the only legal way to render a trust badge |
| `WindowSelector<T>` `{options, value, onChange, labelFn?, ariaLabelFn?}` | window/option groups; `aria-pressed` + focus-visible |
| `EmptyState` `{title, detail?}` | no-data path |
| `LoadingState` `{message?}` | async fetch |
| `ErrorState` `{title?, detail?}` | fetch failed — **distinct from EmptyState**, so the researcher can tell "failed" from "nothing there" |
| `ChartShell` `{ariaLabel, height?}` | wraps every Recharts chart; `ariaLabel` required |
| `chartDefaults` (named exports) | `defaultChartGrid`, `defaultAxisTickStyle`, `defaultMinTickGap`, `defaultTooltipContentStyle` |

Every primitive has a colocated `<Name>.test.tsx`. A new primitive without one
is not acceptable.

## The canonical card pattern

Self-fetching component: the card calls the adapter in its own `useEffect`
rather than receiving pre-fetched data from `App.tsx`. This avoids wiring
overhead in `App.tsx` and the `PortfolioSnapshot` vs `ImportedSnapshot` type
mismatch between app state and adapter requests. See `FactorAttributionCard` and
`BenchmarkCorrelationTable`.

```tsx
type FooCardProps = { snapshot: ImportedSnapshot | null }
type LoadState = 'idle' | 'loading' | 'error' | 'done'

useEffect(() => {
  if (!snapshot) { setResult(null); setLoadState('idle'); return }
  let cancelled = false                    // prevents stale-result writes
  setLoadState('loading'); setErrorMsg(null)
  runFooEngine(snapshot, window)
    .then(d => { if (!cancelled) { setResult(d); setLoadState('done') } })
    .catch(e => { if (!cancelled) { setErrorMsg(e instanceof Error ? e.message : 'Foo engine failed'); setLoadState('error') } })
  return () => { cancelled = true }
}, [snapshot, window])
```

Then `CardShell` wrapping the four states, with `TrustBadge` in `badge`,
`WindowSelector` in `actions`, and the chart in `ChartShell` with the
`chartDefaults` spread onto the Recharts components. The `ui-polish` skill has
the full copy-paste template.

**Adapter signature:** `runFooEngine(snapshot, options?, apiUrlOptions?)`
returning a typed `Promise<FooResponse>`. Use `resolvePortfolioEngineUrl(...)`
for the URL and surface the backend's `detail` on non-2xx as the error message.

## The five audit checks

| Check | Fix |
|---|---|
| `no_literal_hex_colors_in_card_files` | use a token |
| `no_literal_pixel_values_in_inline_style_props` | use a spacing token (margin/padding/gap/fontSize/borderRadius) |
| `trust_badge_primitive_imported_in_all_badge_rendering_cards` | import and use `TrustBadge` |
| `synthetic_label_string_is_single_source_of_truth` | the JSX text `"Synthetic"` may appear only in `TrustBadge.tsx` |
| `chart_default_props_imported_in_all_chart_files` | import and spread `chartDefaults` |

Escape hatch for a genuine case: `// design-system: escape-hatch: <reason>`
immediately above the literal. Use it rarely and always with a real reason.

`ALL_CARD_FILES` and `CARDS_WITH_BADGE` in `designSystem.audit.test.ts` are the
authoritative audited-surface lists. **Read the constants** rather than trusting
any copy of them, including this one.

## Guardrails, in UI terms

- **No fabrication.** `null` / `unavailable` renders as `"—"`. Never `0`, never
  `""`, never `"N/A"`, never a placeholder.
- **Trust rendered visibly.** `withheld` and `degraded` always show their badge.
  Never silently suppressed.
- **No finance math in components.** Ask the engine. A percentage computed in a
  component is untraceable to a methodology formula, which breaks guardrail 2.
- **Types mirror schemas exactly**, changed in the same pass as the schema.
- **Colour is never the sole encoder.** If colour carries semantic meaning, add
  a symbol or label too — `BenchmarkCorrelationTable` uses ▲▲ / ▲ / • / ▼ / ▼▼.

## Do not opportunistically migrate

The design system covers the Exposure cards, the Risk cards, and the admin cards
(`DataSourcesPanel`, `CacheControlCard`, `ImportAdmissionReviewCard`). It does
**not** cover the Concentration Pack in `ExposurePanel.tsx` or the Dashboard tab
— both are on the older CSS-class pattern, functional and stable, with migration
deliberately deferred to a dedicated story.

If your story touches one of those surfaces, keep the legacy pattern there or
flag it. A half-migration leaves the codebase in a state neither pattern
describes, which is worse than either.

## Definition of done for this lane

- [ ] Outer wrapper is `CardShell`; states use `EmptyState` / `LoadingState` / `ErrorState`
- [ ] Charts wrapped in `ChartShell` with a meaningful `ariaLabel`, `chartDefaults` spread
- [ ] `TrustBadge` for any synthetic/unavailable state; `WindowSelector` for any option group
- [ ] Zero literal hex; zero literal pixels on spacing/size style props
- [ ] TS types mirror the backend schema exactly, per the tech lead's contract
- [ ] Semantic colour also encoded by symbol or label
- [ ] `cd apps/desktop && npx tsc --noEmit` clean
- [ ] No test files touched — that is the test lane; name what needs covering in `handoff`
