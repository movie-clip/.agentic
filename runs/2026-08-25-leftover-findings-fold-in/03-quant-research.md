REPORT 2026-08-25-leftover-findings-fold-in/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only RESEARCH order; no verification command applies

contract_notes:
  - docs/contracts/exposure-fields.md's existing "distinct truth class" note (line 37, added by the 2026-08-24 fix) covers the 6 `ImportedExposureOverride` fields; it should gain a sibling sentence stating `run_metadata.source_status.*`/`run_metadata.confidence` are always live/per-render, are a redundant re-encoding of `availability`, and must never be read as a trust source for a node carrying a frozen `availability` — this closes the documentation gap regardless of which mechanism tech-lead DESIGN picks.

pack_corrections:
  - none

handoff:
  - Fix direction for tech-lead DESIGN: do NOT extend `ImportedExposureOverride` to freeze `run_metadata.source_status`/`.confidence` (a nested Pick-of-Pick / two-level spread) — recommend option (b): these 3 fields are strictly redundant re-derivations of `availability` (already correctly frozen), so the fix is "never read them as a trust source," codified as a contract-doc note + a repo-wide grep-style regression test, mirroring CR-1's already-shipped pattern for the sibling field. See § Fix direction for the full reasoning and the counter-argument DESIGN should weigh if it disagrees.
  - Zero current frontend consumers of `run_metadata.source_status.lookthrough_resolution`/`.benchmark_holdings`/`run_metadata.confidence` for trust display exist today (exhaustive grep, see § Consumer census) — this residual is dormant, not reachable, unlike Finding 1 which had a live walkthrough. Classify as MATERIAL/preventive for the story, not CRITICAL/urgent.
  - Secondary finding, independent of the freeze question: `_build_exposure_source_status`'s `lookthrough_resolution` duplicates `_build_exposure_availability`'s `lookthrough_status` branching logic (separately written, identical three-way conditional) and `run_metadata.confidence` is a pure recombination of `availability`'s own two confidence fields — see § Duplication finding. Worth a DESIGN note even independent of Story 1's scope.
  - `run_metadata.reproducibility.benchmark_symbol` is confirmed genuinely live (reflects the currently-selected benchmark on every `runExposureEngine` call, independent of any persisted snapshot) — directly verified in App.tsx, not just trusted from the prior plan's claim. Must not be frozen.

risks:
  - If DESIGN weighs defense-in-depth and still wants to freeze `source_status`/`confidence` despite the redundancy, the two-level-merge mechanism needed (top-level flat spread plus a nested `run_metadata` sub-spread) reproduces the exact split-vintage risk shape one layer down inside `run_metadata` itself — name this explicitly in the design doc if chosen, don't let it look like a routine Pick extension.
  - I did not re-open `financial-methodology.md` for a "Exposure Run Metadata" section because none exists — this is trust-classification/plumbing logic, not a numeric formula, and the methodology doc correctly has no section for it (confirmed via grep, zero hits beyond unrelated `run_metadata.*` references in Dashboard/investor-economics sections). No methodology-doc change is implied by this research.
  - The UI-label date-surfacing half of Story 1 (item 1) was out of scope per the order's non_goals; I did not touch it.

## Orchestrator brief
- Affected fields confirmed exactly: `run_metadata.source_status.lookthrough_resolution`, `run_metadata.source_status.benchmark_holdings`, `run_metadata.confidence` — all three recompute live every engine run (`exposure_engine.py:79-91` calling `:131-149` and `:165-215`), never touched by `ImportedExposureOverride`. `run_metadata.reproducibility.*` correctly stays out of scope (independently re-verified, not just trusted) — see § Field census.
- Consumer census (exhaustive grep, non-test code): **zero** current frontend readers of these 3 fields for trust display — CR-1 already removed the one that existed. This is a material difference from Finding 1, which was live/reachable. See § Consumer census, § Same bug class?.
- Recommended fix direction: **(b)**, not (a) — do not extend the freeze mechanism; these fields are redundant re-encodings of already-frozen `availability`, so "never treat as a trust source" (contract-doc note + regression test, mirroring CR-1) closes the trap without adding a nested Pick-of-Pick merge that would recreate the same bug shape one layer down. Full reasoning, and the counter-case DESIGN should weigh, in § Fix direction.
- Bonus, out-of-band finding: `lookthrough_resolution` and `confidence` are literal duplicate/redundant computations of `availability`'s own logic — a duplication smell independent of the staleness question. § Duplication finding.
- Sections below: § Field census, § Consumer census, § Same bug class?, § Fix direction, § Trust-class implications, § Duplication finding.

---

## Field census

Read directly, current line numbers (order's cited 131-149/165-209/79-91 have drifted slightly to 131-149/165-215/79-91 — confirmed, not material):

- `exposure_engine.py:79-91` — inside `build_exposure_result`, `ExposureRunMetadata(...)` is assembled: `source_status=_build_exposure_source_status(...)` (:83-88), `confidence=_combine_exposure_confidence(availability.lookthrough_confidence, availability.benchmark_overlap_confidence)` (:89), `reproducibility=_build_exposure_reproducibility(snapshot, benchmark_symbol)` (:90).
- `_build_exposure_source_status` (:131-149) takes the same four inputs (`total_market_value`, `lookthrough_constituents`, `uncovered_positions`, `benchmark_holdings`) as `_build_exposure_availability` (:165-215), called one line apart (:83 vs :59) in the same `build_exposure_result` invocation — self-consistent within one call, by construction.
- `_build_exposure_reproducibility` (:152-162) takes `snapshot` and `benchmark_symbol`. `benchmark_symbol` is confirmed genuinely per-render: `run_exposure_engine`/`build_exposure_result` receive it as a request parameter, and `App.tsx`'s live `runExposureEngine(...)` call always runs (even when an override is later applied) with whatever benchmark is currently selected — so `reproducibility.benchmark_symbol` on a re-render can legitimately differ from the value at import time if the user changed the benchmark selector. `input_imported_at`/`snapshot_as_of_date` are deterministic functions of the *submitted snapshot* — for a fixed persisted node they don't drift render-to-render, so freezing vs. not is moot for them; `dataset_version` is a constant tied to engine version. None of `reproducibility.*` needs freezing; the order's framing is correct and independently confirmed, not just relayed.

## Consumer census

Exhaustive, non-test, non-fixture grep across `apps/desktop/src`:

- `run_metadata.*` reads found: `BenchmarkPositioningCard.tsx:80` (`.reproducibility.benchmark_symbol` — display string only, not trust), `DashboardPanel.tsx:141` and `PerformanceBenchmarkCard.tsx:96-101` (both read a **different** type, `DashboardHistoryRunMetadata`, off `DashboardAnalysis`/dashboard-history results — confirmed by reading `DashboardPanel.tsx:1-20`, `result` there is `DashboardAnalysis`, not `ExposureAnalysis`), `RiskSummaryCard.tsx:57` (`diagnosticsAnalysis.run_metadata?.section_trust...` — `DiagnosticsRunMetadata`, a third, unrelated type).
- `source_status`, `.confidence` (off the Exposure shape), and `lookthrough_resolution`: **zero** non-test hits anywhere in `apps/desktop/src`. `BenchmarkPositioningCard.tsx`'s `getBenchmarkTrust` (post CR-1) reads only `result.exposure_availability?.benchmark_overlap_status`/`.benchmark_overlap_confidence` — confirmed by reading the current file in full.
- Backend: `services/quant-engine/app` — no function outside `exposure_engine.py` itself and its own tests reads `ExposureRunSourceStatus`/the exposure `confidence` field; nothing computes off it downstream. `export_dashboard_goldens.py`'s `source_status` references are the unrelated `DashboardHistoryRunSourceStatus` dict, confirmed by reading the surrounding code.
- Persistence: `ImportedExposureOverride` (the only persisted/frozen frontend shape) is a `Pick` that excludes `run_metadata` entirely, and `portfolioWorkspaceStorage.ts` persists only that Pick — `run_metadata` is never written to disk, never round-tripped, never exported. No report/PDF/evidence-export feature exists in this repo that touches Exposure's `run_metadata`.

Conclusion: unlike Finding 1 (a live, shipped card combining one frozen and one live field into a rendered badge, with a concrete numeric walkthrough proving overstatement), this residual has **no current consumer of any kind** — backend, frontend, test, or export. It is a structurally real but presently dormant trap.

## Same bug class?

Structurally: **yes**, same shape — `run_metadata` sits on the same `ExposureResult`/`ExposureEngineResponse` object as the 6 now-frozen fields, is excluded from `ImportedExposureOverride`'s Pick, and therefore always reflects the current render's live classification even when displayed alongside a frozen `availability`/`market_overlap`. This is exactly the coupling Finding 1 exploited, one field over.

Materially different in two ways that change the calculus:

1. **Reachability.** Finding 1 was CRITICAL because a shipped, tested card actively read both a frozen and a live field into one badge, with a concrete 85%-then-99% coverage walkthrough proving a wrong "verified" label. Here, confirmed via exhaustive grep, nothing reads these fields for trust today — the trap exists in the data model but nothing currently falls into it. This does not mean "ignore it" (the order is right to fold it in preventively, and a future card reaching for `run_metadata.source_status` to add a badge is exactly how Finding 1 happened the first time), but it does mean this is a MATERIAL/preventive item, not an urgent CRITICAL regression, when the story author sizes it.
2. **Information content.** Finding 1's two fields (`availability.benchmark_overlap_status`, live `run_metadata.source_status.benchmark_holdings`) carried genuinely different information that a naive badge combined incorrectly. Here, all three affected `run_metadata` fields are **redundant re-derivations of `availability`** (see § Duplication finding) — they carry no information `availability` doesn't already carry, more precisely, and already-frozen. This weakens the case for extending the freeze mechanism (there is nothing left to preserve that isn't already preserved) and strengthens the case for simply retiring them as a trust source.

## Fix direction

**Recommendation: option (b)** — stop surfacing `run_metadata.source_status.*`/`run_metadata.confidence` as a trust signal, for any consumer, ever; derive trust exclusively from `exposure_availability`. Concretely for tech-lead DESIGN to build from:

1. No backend schema change is required to fix staleness — the three fields are already self-consistent within one engine call (confirmed above); the defect is purely "a future frontend consumer might read a live field next to frozen ones," which is a consumption-discipline problem, not a computation problem.
2. Extend `docs/contracts/exposure-fields.md`'s existing frozen-fields disclosure (line 37) with an explicit sibling statement: `run_metadata.source_status.*` and `run_metadata.confidence` are always live/per-render, are a redundant subset of `availability`'s own classification, and must never be read as the trust basis for a node whose `availability` is frozen. This is the same discipline the doc already applies to the 6 frozen fields, extended to name the one field group that must stay *unread* for trust purposes rather than frozen.
3. Add a regression test in the same shape as `BenchmarkPositioningCard.test.tsx` (CR-1's pattern): assert no component under `apps/desktop/src/features/portfolio` reads `run_metadata.source_status` or `run_metadata?.confidence` for a trust/badge/status computation — a grep-backed test (mirroring CR-1's own "confirmed via repo-wide grep" step, made permanent instead of ad hoc) is cheap and directly prevents a second occurrence of Finding 1's mistake.
4. Do **not** extend `ImportedExposureOverride`'s Pick to include `run_metadata.source_status`/`.confidence` (option (a)). Reasoning: `ImportedExposureOverride` today is one flat, atomic, top-level spread (audited and praised for exactly that property: "one spread, six fields... no code path overrides a subset"). Freezing part of `run_metadata` while leaving `reproducibility.benchmark_symbol` live requires a second-level merge (`{ ...rawExposure, ...override, run_metadata: { ...rawExposure.run_metadata, ...override.run_metadata } }` or equivalent) at *both* override call sites (`App.tsx:489`, `:573`). That reintroduces a split-vintage object one layer down — some of `run_metadata` frozen, some live, inside the same nested field — which is the precise defect class this story exists to close, not extend. Given the fields being frozen would be strictly redundant with data already correctly frozen elsewhere, the complexity has no offsetting benefit.
5. If DESIGN weighs this differently — e.g., wants `run_metadata` to remain a self-contained, internally-consistent object as a documented invariant regardless of consumer behavior — that is a legitimate but different design goal (belt-and-suspenders, not bug-fix-driven), and the nested-merge risk in point 4 should be named explicitly in that design doc rather than treated as a routine type extension.

## Trust-class implications

Per the ladder (`verified > degraded > withheld > unavailable`) and guardrail 4:

- `availability.lookthrough_status`/`.confidence`, `.benchmark_overlap_status`/`.confidence` — for a persisted base-import node, correctly FROZEN AT IMPORT (T1, already audited PASS). These describe the trust basis *as of import time*, which is the same vintage as the numbers displayed beside them. This is already correct and out of this research's scope to change.
- `run_metadata.source_status.*`/`run_metadata.confidence` — always LIVE, describing *this render's* current market-data classification. For a frozen node, these describe a different moment than the numbers shown. Per guardrail 4 ("never let a badge overstate its basis"), these must never be presented as the trust basis for a frozen view. They remain legitimate as backend-internal/diagnostic values (e.g., a future "how would today's live classification compare" feature) but such a feature would need its own explicit "live, not the basis for what's shown" label — a new feature, not this bugfix.
- Withheld vs. unavailable: not implicated here — none of the 3 fields is ever placed in either state; they are three-way live/partial/unavailable and verified/degraded/unavailable classifications, always populated, never withheld. No collapsing risk found.

## Duplication finding

Independent of the freeze/staleness question, direct code comparison shows genuine redundancy, which the pack flags as a worse smell than coupling:

- `_build_exposure_source_status.lookthrough_resolution` (:137-144) and `_build_exposure_availability.lookthrough_status` (:181) are **two separately-written conditionals over the identical inputs** (`total_market_value <= 0 or not lookthrough_constituents` → unavailable; `elif uncovered_positions` → partial/live), never sharing a helper. Same shape as the `US-34.8` `risk.py` daily-return duplication this pack names as the pattern to hunt.
- `_build_exposure_source_status.benchmark_holdings` (:138) and the `benchmark_holdings_status` local inside `_build_exposure_availability` (:171) both call the identical pure function `_classify_benchmark_holdings_support(benchmark_holdings)` — literally the same computation, invoked twice with the same argument, in the same call.
- `run_metadata.confidence` (:89) is a pure recombination of `availability.lookthrough_confidence`/`.benchmark_overlap_confidence` via `_combine_exposure_confidence` — by definition redundant with information `availability` already carries.

This does not, by itself, cause any currently wrong output (both copies always agree within one call), so it is not a numeric-correctness finding. It is worth naming to tech-lead DESIGN as a candidate simplification alongside the trust-source fix: replacing `_build_exposure_source_status`'s independent conditional with a direct derivation from the already-computed `availability` (or vice versa) would remove the duplicate-formula risk entirely, independent of whatever freeze/no-freeze decision is made for the frontend.
