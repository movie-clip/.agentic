REPORT 2026-08-24-sbio-still-unclassified-bug/AUDIT
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   cd apps/desktop && npx vitest run src/app/App.test.tsx
  result:    PASS
  detail:    1 file, 24 tests, all passed. Override-specific tests present and green: "applies the persisted exposure override instead of runExposureEngine's lossy response immediately after a replace-mode import", "...after a session restore", "never applies the persisted exposure override on the draft branch, and reuses it when switching back to the imported snapshot", "leaves an add_snapshot node without an exposure override, so the merged view stays on runExposureEngine's lossy output". anchor: methodology-doc/code-reading — see § Anchor used.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 fix target: BenchmarkPositioningCard.tsx:37-45 (getBenchmarkTrust) must stop mixing frozen availability with live run_metadata.source_status.benchmark_holdings.
  - FINDING 1 fix options: extend ImportedExposureOverride to also freeze run_metadata, or derive the badge from availability alone — either closes the mismatch.
  - FINDING 2 needs a producer/human decision: no UI surface discloses that a persisted base-import's look-through/benchmark/availability data is frozen at import time — see § Finding 2.

risks:
  - Finding 1 is newly introduced by this fix — pre-fix, run_metadata and availability always came from the same live call and could never diverge.
  - Finding 1 is not named in 03-technical-plan.md's decisions/risks, and not covered by T2 (grepped App.test.tsx for run_metadata/benchmark_holdings/BenchmarkPositioningCard — zero matches).
  - Finding 2 is explicitly framed by the work order as possibly a legitimate carried risk — I am not treating it as automatically CRITICAL; see § Finding 2.

## Orchestrator brief
- DoD items 1-4 (§ below) all PASS on direct code verification: availability really does share lookthrough/market_overlap's exact inputs (exposure_engine.py:56-64); the frontend override is a single atomic spread at both call sites, no partial-field path; run_metadata's staleness coupling is real and accurately disclosed in the plan; docs/contracts/exposure-fields.md's new subsection is accurate, does not overclaim freshness.
- FINDING 1 (CRITICAL, verdict FAIL): BenchmarkPositioningCard.tsx's `getBenchmarkTrust` combines the now-frozen `exposure_availability.benchmark_overlap_status` with the still-live `run_metadata.source_status.benchmark_holdings` into one displayed trust badge — a concrete, walked-through scenario where this overstates the true basis of the frozen `market_overlap` numbers shown beside it. See § Finding 1 for the numeric walkthrough.
- FINDING 2 (MATERIAL, does not by itself change the verdict): no UI element tells the user that a persisted base-import's look-through/benchmark/availability data is frozen at import time — the one candidate proxy (snapshot picker label) renders literally "base" for the node that carries the override, no date at all. See § Finding 2.
- anchor used throughout: methodology-doc/code-reading (this is a semantics/code-correctness audit per the order, not a live-data audit) — no formula changed, so no numeric recomputation was applicable; verification is by direct source reading plus the named test run.
- Sections below: § DoD verification (evidence per item), § Finding 1, § Finding 2, § Anchor used.

---

## DoD verification

**1. `_build_exposure_availability` shares lookthrough/market_overlap's inputs — CONFIRMED.**
Read `exposure_engine.py:45-104` directly. `build_exposure_result` computes `lookthrough_constituents, etf_resolution, uncovered_positions, covered_market_value = build_lookthrough_exposure(...)` once (line 51), then:
- `market_overlap` (line 57) is built from `lookthrough_constituents` + `benchmark_holdings`.
- `lookthrough` (lines 93-100) is built from `lookthrough_constituents`/`uncovered_positions`/`total_market_value`.
- `availability` (lines 59-64, via `_build_exposure_availability`, lines 165-215) takes `total_market_value`, `lookthrough_constituents`, `uncovered_positions`, `benchmark_holdings` — the identical four inputs.

This validates the plan's "availability must travel with lookthrough/market_overlap" reasoning exactly as claimed, not just as asserted.

**2. Frontend override is atomic at the override site — CONFIRMED, with a caveat (see Finding 1).**
Both call sites (`App.tsx:489` in `analyzeExposureSnapshot`, `App.tsx:573` in `analyzeRestoredSnapshot`) use the identical single-expression pattern:
```ts
const exposure = importedExposureOverride ? { ...rawExposure, ...importedExposureOverride } : rawExposure
```
One spread, six fields (`overview`, `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration`, `availability`), applied together or not at all — no code path overrides a subset. The override mechanism itself is exactly as atomic as the plan claims.
The caveat: atomicity of the override does not make the *result object* internally consistent, because `run_metadata` sits on the same `ExposureResult`/`ExposureAnalysis` shape but is outside the `ImportedExposureOverride` Pick, so it stays on `rawExposure` (live) permanently. A downstream consumer that reads both `availability` and `run_metadata` off the same `exposure`/`result` object can still combine one frozen field with one live field — this is exactly what Finding 1 documents. The override boundary is honest; a consumer one layer further out is not.

**3. `run_metadata` residual is real and accurately disclosed — CONFIRMED.**
`run_metadata.source_status` (`_build_exposure_source_status`, `exposure_engine.py:131-149`) takes the same four inputs as `availability`. `run_metadata.confidence` (`exposure_engine.py:89`) is `_combine_exposure_confidence(availability.lookthrough_confidence, availability.benchmark_overlap_confidence)` — derived from that *same render's* `availability` local variable, so it is self-consistent within one `build_exposure_result()` call but, once `availability` is later overridden by an older frozen value on the frontend, `run_metadata` (unoverridden) reflects a *different*, more recent construction. The plan's § Risk detail states this precisely and correctly; nothing here is silently worse than disclosed. What the plan's risk note does not do — and what I add in Finding 1 — is name the concrete, already-shipped UI consumer that acts on this mismatch today.

**4. `docs/contracts/exposure-fields.md` subsection — CONFIRMED accurate, does not overclaim freshness.**
Read the added item 3 under "Current Root Sources" (lines 32-37) directly. It correctly states the fields are "computed once, at import time, and ... persisted and replayed ... rather than recomputed on every render; they are frozen-at-import values, not live/per-render values." This is exactly true per §§1-2 above. No overclaim found. This is a developer-facing contract doc, not end-user UI — see Finding 2 for the separate question of whether the *end user* sees any equivalent disclosure.

## Finding 1

```
FINDING 1
severity:   CRITICAL
where:      apps/desktop/src/features/portfolio/BenchmarkPositioningCard.tsx:37-45 (getBenchmarkTrust)
claim:      the function computes one BenchmarkTrust badge ('verified' | 'degraded' | 'partial' | 'unavailable') shown on the Dashboard's Benchmark Positioning card, gating the coverage-note text shown next to the card's numeric values
actual:     it reads result.exposure_availability?.benchmark_overlap_status (frozen at import time for a persisted base-import node, per T1's override) together with result.run_metadata?.source_status?.benchmark_holdings (never overridden — always the current render's live MarketDataService().get_etf_holdings() classification, exposure_engine.py:55/138). These two fields, which were always derived from the same live call before this fix and could never diverge, can now be computed at different times.
impact:     concrete walkthrough — at import time, benchmark_holdings coverage was e.g. 85% (< the 99% VERIFIED_COVERAGE_PCT threshold, exposure_engine.py:38), so _build_exposure_availability classifies benchmark_holdings_status='degraded' and, because lookthrough_status=='live', sets the frozen availability.benchmark_overlap_status='live' (exposure_engine.py:189-191, the 'degraded but live overlap' branch). market_overlap (also frozen) is computed from that same 85%-coverage snapshot. Weeks later, on a live render, FMP's benchmark constituent data happens to read >=99% coverage, so the LIVE run_metadata.source_status.benchmark_holdings now classifies 'verified'. getBenchmarkTrust's logic: overlapStatus (frozen) == 'live' -> falls through to check holdingsSupport (live) == 'verified' -> returns 'verified'. The card now displays "Positioning available versus SPY" (the verified-tier coverage note, line 88) beside market_overlap numbers that were actually computed under only 85%-coverage benchmark data — a trust label at the top of the ladder describing a number whose actual basis was degraded.
expected:   the badge must be derived entirely from data of one vintage — either read run_metadata from the same frozen snapshot availability came from (extend ImportedExposureOverride, mirroring the plan's own reasoning for why availability had to travel with lookthrough/market_overlap), or drop the run_metadata.source_status.benchmark_holdings branch from getBenchmarkTrust and derive verified/degraded purely from availability.benchmark_overlap_confidence (already frozen, already carries a coarser verified/degraded-equivalent signal via lookthrough_confidence/benchmark_overlap_confidence)
```

This is not covered by T2: `App.test.tsx` has zero references to `run_metadata`, `benchmark_holdings`, or `BenchmarkPositioningCard` (grepped directly). T2's coverage was correctly scoped to the 6 `ImportedExposureOverride` fields per the plan, so this gap was never in its brief — it is a genuinely new finding, not a missed item from an existing checklist.

## Finding 2

```
FINDING 2
severity:   MATERIAL
where:      apps/desktop/src/features/portfolio/ExposurePanel.tsx (snapshot picker), apps/desktop/src/features/portfolio/variantLabels.ts:3-4, BenchmarkPositioningCard.tsx / SectorPieCard.tsx (Dashboard cards consuming the frozen fields)
claim:      (implicit) a user viewing Exposure/Dashboard cards for their imported portfolio can tell whether the look-through/benchmark-overlap/availability data they're looking at reflects current market conditions or an older import
actual:     the base imported node — the only node kind that actually carries importedExposureOverride and therefore renders frozen data — is labelled literally "base" in the snapshot picker (variantLabels.ts:4, buildNodePath: `node.kind === 'imported_base' ? 'base' : node.name`), with no date. The dated label (buildImportedSnapshotName, App.tsx:81-83) only applies to add_snapshot child nodes, which are precisely the nodes excluded from the override (they always show fresh/live data). DataSourcesPanel (provenance card) shows pricing-source mix, not a date. The Dashboard tab does show a "Loaded file/statements: <period>" label (DashboardPanel.tsx:12-14) at the page level, which is a genuine proxy for "as of when," but it is not connected in any visible way to "the trust badges and look-through numbers on this page were computed once at that time and are not being refreshed" — a user who has only ever seen this app's exposure data as live (which it always was, pre-fix, per the scout's finding that runExposureEngine was "a live network call on every render") has no cue that the behavior changed for imported snapshots.
impact:     a researcher could treat a months-old frozen lookthrough/market_overlap/availability view as current, act on stale sector concentration or benchmark-overlap numbers, and have no in-product signal prompting them to re-import or distrust the figures.
expected:   either an explicit "as of <import date>" marker on the Exposure/Dashboard cards backed by frozen data, or an explicit decision from the product owner that this is an accepted carried risk (the work order's own framing) — which has not yet been made, since this fix's own docs update (accurately) only documents the truth-class distinction for developers, not for end users.
```

**My explicit judgment, per the work order's request**: this is not itself a defect in what T0-T2 built — the plan never claimed to solve end-user staleness disclosure, and the contract-doc language is honest about the mechanism to a developer audience. But the work order asks me to evaluate, not assume away, whether "a persisted, months-old availability/lookthrough ever get[s] shown without any staleness signal to the user" — and having checked the actual rendered labels (not just the doc), the answer is yes, concretely, for the one node type that matters (the base import). I am reporting this as MATERIAL — a real, evaluated gap in trust-semantics disclosure — and leaving the accept-vs-fix call to the human/producer, per this pack's instruction that un-withholding or otherwise loosening the trust model is not a lane's call.

## Anchor used

`anchor: methodology-doc` / code-reading. This audit's DoD is entirely about trust semantics and code correctness of a plumbing change (no new formula, no new computation — `03-technical-plan.md` and every landed report confirm this is pure pass-through of an already-computed `ExposureResult`). There is no formula to independently recompute, and the work order itself states "this audit is about semantics and code correctness, not live financial data." Verification consisted of: (a) direct reading of `exposure_engine.py`, `import_engine.py`, `import_bootstrap.py`, `App.tsx`, `importedBootstrapMapper.ts`, `portfolioWorkspaceStorage.ts`, `BenchmarkPositioningCard.tsx`, `docs/contracts/exposure-fields.md` against the plan's specific claims; (b) tracing the one concrete degenerate-input scenario in Finding 1 (85%-coverage-at-import vs 99%+-live) to show a reachable overstatement, which functions as the "closed-form/hand-computed case" class of anchor for this kind of state-machine logic (not a numeric formula, but a discrete-state divergence proof); (c) running the named verification command.
