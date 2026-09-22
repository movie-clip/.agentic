# Capability pack: frontend — project `datoro`

For the `frontend-engineer` lane. Everything about `src/**`. Where this
contradicts general Vue instincts, this file wins.

Companion sources: `datoro/CLAUDE.md`, `datoro/AGENTS.md` (house style — this
pack does not repeat its naming/import conventions in full).

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Component and composable conventions** · **Reuse — do not re-derive these** · **Guardrails, in code terms** · **Definition of done for this lane**

| Section | Read it when |
|---|---|
| Layout | you are adding a file, or looking for where one lives |
| Charts | your order touches an ECharts component or chart data |

---

## Layout

```
src/
  components/
    auth/ charts/ common/ dashboard/ dcf/ hero/ layout/ macro/
    modals/ news/ pages/ subscription/ tables/
  composables/   useXxx.ts — reusable stateful logic
  services/
    ai/          reads the static public/ai-insights.json bundle
    analytics/   gaService.ts
    charts/ company/ dcf/ deepFinder/ financials/ health/ macro/ market/
    news/ performance/
  stores/        authStore.ts, tickerStore.ts
  types/         centralized TypeScript type exports
  schemas/       frontend-side validation
  plugins/, config/, utils/, styles/, assets/
```

`src/services/financials/batchChartService.ts` and `batchTableService.ts` are
where batch-ticker extraction belongs, per `AGENTS.md` — the frontend
counterpart of the server's `batchDataService.ts`.

## Component and composable conventions

Per `AGENTS.md` § "Vue Frontend Patterns" and "Naming Conventions":

- `<script setup lang="ts">`, typed `defineProps` / `withDefaults` /
  `defineEmits`.
- Components: `PascalCase.vue`. Composables: `useXxx.ts`. Types/interfaces:
  `PascalCase`.
- Reuse shared UI primitives — `src/components/common/BaseDropdown.vue` is
  named explicitly for dropdowns; check `common/` before writing a new
  primitive.
- Keep state in composables when logic is reusable or data-heavy; keep
  component-scoped styles local, shared CSS only when more than one feature
  needs it.
- Frontend commonly uses the `@/` alias; some files use relative imports —
  follow the existing style of the file you are editing rather than
  rewriting for consistency.

## Charts

- ECharts via `vue-echarts` is the only charting library in this repo.
  **Do not introduce Chart.js-based patterns**, even for a one-off.
- For large datasets, preserve existing performance patterns — progressive
  rendering, sampling, stable keys.
- **Do not force a chart rerender with a data-dependent `:key` prop** when a
  smooth update is expected; that pattern has already caused regressions here.

## Reuse — do not re-derive these

- `healthIndicatorService.ts` (`src/services/health/`) — the only health
  scoring logic. `AGENTS.md` names this explicitly.
- `src/services/dcf/dcfCalculator.ts`, `dcfDataService.ts`,
  `valuationMethodsService.ts` — DCF logic. A component computing its own
  valuation number instead of calling these is a duplicate-formula defect,
  the same class `portfolio`'s backend pack warns about, one repo over.
- `src/services/ai/insightsService.ts` — the only reader of
  `public/ai-insights.json`. The main app does not call an LLM at runtime; a
  request that implies otherwise is out of scope for this lane — see
  `capabilities/product.md` § "The AI insights boundary".

## Guardrails, in code terms

**External data degrades honestly (guardrail 5).** A field that the API
returns as missing or `null` renders as missing — an explicit empty/placeholder
state, never a fabricated number, never a silent zero. If the backend lane's
`contract_notes` describes a new nullable field, render its absence
explicitly rather than assuming it is always present.

**No secrets in client code.** Nothing under `src/**` embeds an API key,
webhook secret, or JWT signing secret. `VITE_`-prefixed env vars are the only
ones reaching the client build, by Vite's own convention — do not add a
non-`VITE_` secret to a client-readable config to work around that.

## Definition of done for this lane

- [ ] `<script setup lang="ts">`, typed props/emits, no `any` without a named
      local justification
- [ ] Reused `common/` primitives, `healthIndicatorService`, `dcf/**` and
      `ai/insightsService` rather than re-deriving them
- [ ] ECharts only; no forced-rerender `:key` anti-pattern
- [ ] Missing/partial data renders as missing, not fabricated or zeroed
- [ ] No secret or key embedded in client-shipped code
- [ ] `contract_notes` names any assumption about a backend response shape
      that the backend lane's own notes did not already confirm
- [ ] No test files touched — that is the test lane
