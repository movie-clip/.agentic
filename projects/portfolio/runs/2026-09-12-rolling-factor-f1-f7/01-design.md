REPORT 2026-09-12-rolling-factor-f1-f7/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification field was NONE (read-only design pass; no code written)

contract_notes:
  - F1 needs no schema, type, or adapter change — `statistical_factor_model.status` and `windows[].status` are already typed in `types.ts:793,800,1481,1488` and passed through unchanged by `buildExposureFactorModel` (`portfolioAnalysisAdapter.ts:508-514`). This is a pure frontend-consumption fix.
  - F7 removes `RollingFactorLoadingPoint.alpha` from `reconciliation.py:483`, its three mirrors in `types.ts:839,861,883`, and `ExposureFactorModelResponse` inherits the removal automatically (it references `StatisticalFactorModel['rolling_loadings_*d']` by type alias, not a separate literal).
  - `TrustBadge.tsx`'s `TrustType` union gains a `'degraded'` member — its own docstring (lines 10-11) already names this as the intended extension path.
  - `docs/contracts/dashboard-fields.md:248` gets a new row for `statistical_factor_model.status` / `windows[].status` — close-phase only, per tech-debt-register's own instruction and this order's non_goals.

pack_corrections:
  - none

handoff:
  - Lane split, in dispatch order: 1) backend (F7 schema) 2) frontend (F1 card+badge, F7 types.ts) 3) test (F1 badge/card tests, F7 fixture cleanup) 4) integration gate 5) docs (close-phase contract row). See § Lane split for exact files and verification per lane.
  - Backend work order: delete `reconciliation.py:483` (`alpha: float | None = None`). Nothing else in `services/quant-engine/app/**` references this field — see § F7 decision.
  - Frontend work order covers both findings in one dispatch (no file conflict, no dependency ordering needed between F1 and F7 within the lane) — see § Lane split for the itemized diff each finding requires.
  - Test work order covers both findings in one dispatch — see § Lane split; it must land after backend+frontend since it asserts against the post-removal schema and the new badge markup.
  - Docs work order (close-phase, separate dispatch after frontend+test are green) — see § Doc contract row for the exact row content to write.
  - Quant-audit gate, if the orchestrator dispatches one per run.md's phase table: F7 is a dead-field deletion with no formula change, and F1 renders an already-computed status — flag this so quant-audit scopes its recompute effort correctly and doesn't re-derive the rolling regression.

risks:
  - `FactorDriftSummaryCard.test.tsx:13` independently hand-builds a `REQUIRED_LOADING_KEYS` array containing `'alpha'` for its own fixture rows — a second, easy-to-miss site F7 must also touch. Named explicitly in § Lane split so the test lane doesn't stop at `portfolioFixtures.ts`.
  - `RollingFactorLoadingsCard.tsx` is not in `designSystem.audit.test.ts`'s allowlists and carries 16 legitimate hex-literal factor colors — do not add it to `ALL_CARD_FILES`/`CARDS_WITH_BADGE` alongside the `TrustBadge` import; that would drag in unrelated hex/px remediation. See § Reuse and placement.
  - The badge's trust source is `selectedWindowSummary.status` alone, not the model-level `status` — verified they degrade identically today from the same return-basis check, so this is not true by coincidence. See § F1 decision and § Status enum and treatment; revisit if a future change makes window- and model-level degrade diverge.
  - Guardrail 1 (methodology-first for trust-state logic changes) does not gate either fix: F1 changes no backend logic, only consumes an existing computed value; F7 deletes a field the methodology doc never mentions (grepped — zero hits for a rolling "alpha" anywhere in `financial-methodology.md`). Confirmed by reading the doc, not assumed.

---

## Orchestrator brief

- Decision: F1 is frontend-only. The `status` contract already exists end-to-end (schema → adapter → types.ts); nothing to add, only to consume. Do not dispatch a backend order for F1.
- Decision: F7 → **remove `alpha`**, not reserved-null. It has zero methodology documentation, zero code path, and the repo already has a hard rule elsewhere (`attribution-fields.md:16`) against a residual-shaped field ever being labelled `alpha`. See § F7 decision.
- Decision: badge trust source is `selectedWindowSummary.status` (per-window), not the model-level status — they carry the same signal for the rendered window, model-level is redundant here. See § Status enum and treatment.
- Decision: reuse `TrustBadge` primitive (extend with `'degraded'`), inserted into the card's existing hand-rolled header markup — do **not** migrate the card onto `CardShell`. See § Reuse and placement.
- Lane split, in order: backend (F7 schema) → frontend (F1 card+badge, F7 types.ts) → test (both) → integration gate → docs (close-phase contract row only). See § Lane split for exact files, diffs, and verification commands per lane.
- Sections below: **Status enum and treatment** (F1's DoD #1), **F1 decision** (contract, already-passed-through), **F7 decision** (remove vs. reserved-null), **Reuse and placement**, **Lane split**, **Doc contract row** (content for the close-phase docs order), **Risks carried forward**.
- Nothing blocks dispatch of either finding.

---

## Status enum and treatment

Read directly from `risk.py` (not assumed — recon flagged this enum as unverified, so it was read line-by-line for this pass):

- Model built at `build_statistical_factor_model` (risk.py:1321-1373): `"insufficient_history"` (early return, empty rolling series) or `"ok"` / `"partial"` (`"partial"` when any window's `insufficient_history` list entry exists — missing factors or short history on *some* window).
- Window built at `_build_window_summaries` (risk.py:1086-1110): per window, `"ok"` if `len(common_dates) >= WINDOW_MIN_OBSERVATIONS[window]`, else `"partial"` if any point produced a real value, else `"insufficient_history"`.
- Degrade overlay, `_degrade_status_for_unverified_return_basis` (risk.py:773-776), applied uniformly to model.status and every window.status by `apply_return_basis_status_to_factor_model` (risk.py:954-969): if the benchmark or any factor's return basis is not `"verified_adjusted_close"` **and** the status is currently `"ok"` or `"partial"`, it becomes `"degraded_unverified_return_basis"`. `"insufficient_history"` is never touched by the degrade (there's nothing to degrade — no series to mistrust).

Full producible enum for this component: `{"ok", "partial", "insufficient_history", "degraded_unverified_return_basis"}`. No `"unavailable"` or `"withheld"` literal is ever produced for `statistical_factor_model.status` / `windows[].status` — do not add a treatment for either; guardrail 4's ladder is honored by *ordering* the treatments below, not by matching its exact words.

Treatment, ordered `verified > degraded > withheld > unavailable` (no withheld rung applies — nothing here is deliberately hidden pending a policy decision):

| status | rung | visible treatment |
|---|---|---|
| `ok` | verified | no badge — current rendering, unchanged |
| `partial` | degraded | `<TrustBadge type="degraded" tooltip="This window has less than the full recommended history; loadings may be noisier than a fully-seasoned window.">` |
| `degraded_unverified_return_basis` | degraded | `<TrustBadge type="degraded" tooltip="Return basis for the benchmark or a factor proxy is not fully verified (close-only price data, not adjusted-close).">` |
| `insufficient_history` | unavailable | no badge needed — this status is always paired with an empty `rolling_loadings_*d` series (confirmed: the early-return branch in `build_statistical_factor_model` that yields `"insufficient_history"` also yields `rolling_loadings_20d=[]` etc.), which already routes to the existing empty-state panel (`RollingFactorLoadingsCard.tsx:312-317`). That panel's copy is F10's territory (out of scope) — leave it. |
| any other string (the type's own `\| string` escape hatch) | treat as unavailable, never as ok | no badge, but do **not** fall through to the `ok` (no-badge) branch by default — see § F1 decision for the exact conditional shape |

Two literal strings — `"partial"` and `"degraded_unverified_return_basis"` — get the *same* visual badge (`type="degraded"`) with *different* tooltip text. They are the same trust rung for different reasons (data completeness vs. return-basis provenance); inventing two separate visual badge styles for one rung is not warranted by the ladder and was rejected as over-engineering relative to what F1 asks for.

## F1 decision

**The contract already exists end-to-end.** Confirmed by reading the adapter, not assumed:

- `types.ts:1481` and `:1488` — `ExposureFactorModelResponse.statistical_factor_model.status` and `.windows[].status` are both typed `'ok' | 'insufficient_history' | 'partial' | string`.
- `portfolioAnalysisAdapter.ts:508-514` (`buildExposureFactorModel`) does a straight passthrough: `statistical_factor_model: result.statistical_factor_model` — no field is dropped or renamed between the diagnostics engine response and the prop the card receives.
- Therefore **no backend, schema, or adapter change is needed for F1.** The defect is entirely that `RollingFactorLoadingsCard.tsx` never reads a field it already has.

Required card change (frontend lane only):

1. Compute `selectedWindowSummary` (already exists, `RollingFactorLoadingsCard.tsx:203`, via the already-existing `getWindowSummary` helper) — no new selector needed.
2. Derive a badge node: `ok` → `null`; `partial` or `degraded_unverified_return_basis` → the `TrustBadge` per § Status enum and treatment; anything else (including `undefined`/missing summary) → render the `unavailable`-shaped path, i.e. also `null` badge is acceptable **only** because it is paired with the empty-series branch per the table above — do not add a badge-less `ok`-equivalent render path for an unrecognized string that has a non-empty series. Concretely: `const trustStatus = selectedWindowSummary?.status; const badge = trustStatus === 'partial' || trustStatus === 'degraded_unverified_return_basis' ? <TrustBadge .../> : null`.
3. Render the badge inside the existing header block (`RollingFactorLoadingsCard.tsx:258-261`, the `section-header-inline sector-list-header` div), next to the `panel-label` — see § Reuse and placement for why not `CardShell`.

## F7 decision

**Remove `alpha`.** Not reserved-null. Grounds, all read directly rather than assumed:

- `_build_rolling_factor_loadings` never sets it — confirmed by the audit (`02-quant-audit.md` FINDING 7) and by `risk.py:1352-1354`'s own comment: the model deliberately dropped a global-period intercept and specific-risk pair in Epic 23 because "methodology forbids labelling the OLS intercept 'alpha'." There is no rolling-window intercept computed anywhere in the current pipeline — this is not a value waiting on a future computation, it is a vestige of a removed feature.
- `docs/finance/financial-methodology.md` has zero mentions of a rolling-loadings `alpha` (grepped in full) — guardrail 2 ("every displayed metric has one documented formula and one code path") fails on **both** counts, not just the code-path half. Documenting it as reserved-null would mean writing a methodology section for a field that structurally can never be non-null, which is worse than removing it.
- The repo already has a standing rule against this exact mislabeling one contract doc over: `docs/contracts/attribution-fields.md:16` — "The residual must be labelled `unexplained` or `idiosyncratic`. It must never be labelled `alpha`." Removing this field is consistent with that precedent, not a new policy.

Every site that references it (found by repo-wide grep, not assumed complete from the audit alone):

- `services/quant-engine/app/schemas/reconciliation.py:483` — the field itself.
- `apps/desktop/src/features/portfolio/types.ts:839,861,883` — the three `rolling_loadings_{20,60,252}d` element types.
- `apps/desktop/src/test/portfolioFixtures.ts:958-960` — the fabricated `alpha: 0.0002` / `alpha: null` values (the fixture the audit named).
- `apps/desktop/src/features/portfolio/FactorDriftSummaryCard.test.tsx:13` — a **second**, independently-built fixture helper (`REQUIRED_LOADING_KEYS`) that also lists `'alpha'`. Not named in the tech-debt entry or the audit; found in this pass. Must be updated in the same change or it silently keeps testing a field that no longer exists on the type.
- `services/quant-engine/app/tests/test_analytics.py:5419` — `"alpha": None,` inside an expected-output dict for a golden-shaped assertion. Must drop the key.

No other production code path reads `.alpha` (confirmed: `RollingFactorLoadingsCard.tsx` never references it; `DriftBenchmarkPanel.tsx`'s `drift-alpha-row` and `settings.py`'s `fmp_alpha_pit_snapshot_dir` are unrelated string collisions, not this field — checked and excluded).

## Reuse and placement

- **`TrustBadge`** (`apps/desktop/src/app/primitives/TrustBadge.tsx`) is the named reuse point, not a new inline badge. Its own docstring instructs exactly this extension: add `'degraded'` to the `TrustType` union and a `LABELS.degraded = 'Degraded'` entry. No new CSS — the existing `.attribution-trust-badge` class is intentionally type-agnostic (same style for `synthetic` and `unavailable` today); do not add a `degraded`-specific style variant.
- **Do not migrate `RollingFactorLoadingsCard.tsx` onto `CardShell`**, even though `CardShell`'s own docstring describes it as replacing exactly this hand-rolled `section-header-inline` + `panel-label` + badge pattern. This card's header also carries a coverage helper line and a two-row toolbar (window toggle, factor-group filter) that don't match the simpler title/badge/actions shape every current `CardShell` consumer uses, and the card's outer class (`dashboard-bottom-grid factor-master-detail-section`) is not `compact-chart-panel` — forcing the migration risks a visual/layout regression for a trust-label defect fix. Insert `<TrustBadge>` directly into the existing header `div`, next to `panel-label`. This is a scope-boundary decision, not a quality compromise — a future card-shell migration for this card is a separate, larger tech-debt item.
- **Reuse `createExposureEngineFixture` + `createDiagnosticsEngineFixture` + `composeExposureView` + `buildExposureFactorModel`** (all already exported from `portfolioAnalysisAdapter.ts` / `portfolioFixtures.ts`) for the new render tests, overriding `.statistical_factor_model.windows[]` per case, rather than hand-building a parallel `ExposureFactorModelResponse` literal in the test file. Building a test fixture that bypasses the real adapter chain is exactly the class of defect F7 exists to fix — do not reintroduce it while fixing it.
- `portfolioFixtures.ts:949-960`'s `createImportedStatisticalFactorModelFixture` already carries `windows` statuses `'ok'` / `'partial'` / `'insufficient_history'` — reuse it for those three cases. It does **not** carry a `'degraded_unverified_return_basis'` case; the test lane must add one (either a fourth window override or a second small fixture variant).

## Lane split

**1. Backend** — `services/quant-engine/app/schemas/reconciliation.py`
   - Delete line 483 (`alpha: float | None = None`) from `RollingFactorLoadingPoint`.
   - Verify: `cd services/quant-engine && pytest app/tests/test_analytics.py -k "rolling_loadings or factor_model" -v` (will fail loudly if anything else in the backend still constructs `alpha=`).

**2. Frontend** — `apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.tsx`, `apps/desktop/src/app/primitives/TrustBadge.tsx`, `apps/desktop/src/features/portfolio/types.ts`
   - F1: extend `TrustBadge`'s `TrustType` union + `LABELS` with `'degraded'` → `'Degraded'`.
   - F1: import `TrustBadge` into `RollingFactorLoadingsCard.tsx`; add the badge per § F1 decision, inside the existing header markup per § Reuse and placement.
   - F7: delete `alpha: number | null` from all three `rolling_loadings_{20,60,252}d` element types in `types.ts` (lines ~839, 861, 883).
   - Do not touch `ExposureFactorModelResponse`'s optional/required factor-key mismatch (F9) or `residual_vol`'s missing unit suffix (F8) — separate tech-debt items, out of scope.
   - Verify: `cd apps/desktop && npx tsc --noEmit` (catches any remaining `.alpha` reference or badge-prop typo).

**3. Test** — `apps/desktop/src/app/primitives/TrustBadge.test.tsx`, `apps/desktop/src/features/portfolio/RollingFactorLoadingsCard.test.tsx`, `apps/desktop/src/test/portfolioFixtures.ts`, `apps/desktop/src/features/portfolio/FactorDriftSummaryCard.test.tsx`, `services/quant-engine/app/tests/test_analytics.py`
   - F1: add a `renders_degraded_label` case to `TrustBadge.test.tsx` mirroring the existing `renders_synthetic_label` / `renders_unavailable_label` pattern.
   - F1: add render cases to `RollingFactorLoadingsCard.test.tsx` (currently only tests `sortTooltipPayloadRows`) asserting: no "Degraded" text when the selected window's status is `'ok'`; "Degraded" text present when `'partial'`; "Degraded" text present when `'degraded_unverified_return_basis'` (construct this window override explicitly — no existing fixture has it). Build the `factorModel` prop via the adapter chain per § Reuse and placement, not a hand-rolled literal.
   - F7: remove the `alpha: 0.0002` / `alpha: null` entries at `portfolioFixtures.ts:958-960`.
   - F7: remove `'alpha'` from `REQUIRED_LOADING_KEYS` at `FactorDriftSummaryCard.test.tsx:13`.
   - F7: remove the `"alpha": None,` key at `test_analytics.py:5419`.
   - Verify: `cd apps/desktop && npx vitest run` and `cd services/quant-engine && pytest app/tests/test_analytics.py -k "rolling_loadings or factor_model"`.

**4. Integration gate** (tech-lead, INTEGRATION) — after 1-3 report DONE. Full suite: `python scripts/run_all_tests.py`. Specifically check: `designSystem.audit.test.ts`'s `ALL_CARD_FILES`/`CARDS_WITH_BADGE` were **not** modified to add `RollingFactorLoadingsCard.tsx` (would be unscoped overreach per § Reuse and placement); no stray `.alpha` reference survives anywhere; the badge's visual rung ordering matches § Status enum and treatment field-by-field.

**5. Docs** (close-phase only, dispatched after 1-4 pass) — see § Doc contract row.

## Doc contract row

For `docs/contracts/dashboard-fields.md`, in the "Factor / Composition cards" table (the existing "Rolling Factor Analysis" row is at line 248): add a new row, or extend the existing row's Notes column, naming:

- Field: `statistical_factor_model.status` / `windows[].status`.
- Producible values: `ok`, `partial`, `insufficient_history`, `degraded_unverified_return_basis` (cite `risk.py:773-776`, `:954-969`, `:1086-1110`, `:1321-1373` — the same line ranges this plan verified them against).
- UI mapping: `ok` → no badge; `partial` / `degraded_unverified_return_basis` → `TrustBadge type="degraded"` (distinct tooltips); `insufficient_history` → routes to the existing empty-state panel (no series to badge).
- Do not write this row before the frontend change lands — the tech-debt entry and this order's non_goals both require code-then-doc sequencing here.

## Risks carried forward

See the `risks` block above the Orchestrator brief for the full list (design-system allowlist boundary, the second fixture site, the windows-vs-model status redundancy assumption, and the guardrail-1 scoping check). Not repeated here to keep this section from duplicating the routable bullets.
