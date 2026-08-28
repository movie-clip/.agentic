REPORT 2026-08-27-next-epic-or-story/11
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py  (+ pytest on the two route-inventory guard files, + git stash red-before check)
  result:    PASS
  detail:    Full suite green: backend 947 passed, frontend 359 passed (40 files), tsc --noEmit clean, dead-code gate (ruff+vulture+knip) clean. Guard files: 6 passed. Red-before verified by execution: doc hunk stashed -> all 3 new tests fail. Anchor: live tree (app/api/routes/ = 15 modules, main.py 15 include_router calls, app/services/ = 25 files) + git diff -U0 hunk ranges, not the build artifacts.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - AC11 guard keys on the app/api/routes/ glob, not on main.py include_router calls; a module present but unregistered would still pass. Plan-adjudicated (07 § Decision ii); all 15 are in fact registered. Observation.
  - AC1 guard is module-stem structure-scoped; a phantom route path reintroduced into surrounding prose is caught only by review. Story and 07-plan both acknowledge this. Observation.
  - Working tree also carries unrelated Unit-1 doc-reconciliation edits (orders 04/05) on 9 other files. Out of this story's scope; excluded from this gate. The full-suite run covers the whole tree regardless.
  - 07-plan pack_corrections item (capabilities/architecture.md omits currency-risk from the /engines/{...} list) remains open, for close-out docs lane. Not this story.

## Orchestrator brief

Verdict: PASS. All 13 acceptance criteria for US-41.2 are satisfied against the live repo and the diff; the test plan is delivered in full; `python scripts/run_all_tests.py` is green (backend 947, frontend 359, tsc clean, dead-code clean).

- AC1 / AC3 (grep of the whole doc for the 5 phantom route-path families and the 8 removed service files): both clean — no match anywhere; the only removed-surface word left is one negative-assertion sentence at line 235.
- AC8 / AC9 / AC10 (three protected sections byte-identical): confirmed via `git diff -U0` — no hunk in old lines 119-245 or 251-274, which contain all three fences.
- AC11 / AC12 (guard exists, bidirectional, names offenders, non-vacuous, red-before/green-after): confirmed by running the tests and by a `git stash` red-before check — 3 fail on the old doc, 6 pass on the new.
- No change requests. No BLOCKING or SHOULD_FIX. Nothing to route.

Sections below: `## AC-by-AC verdict` (one block per AC1-AC13 with evidence); `## Test plan fidelity`; `## Trust-state spot checks`; `## Repo hygiene`.

## AC-by-AC verdict

Every criterion checked against the live repo and the diff, not the integration gate's word.

### AC1 — No phantom route in the seams inventory — PASS
`grep -nE '/backtests|/construction|/strategy-lab|/optimizer|/ranking'` on the whole doc: no match. `grep -niE 'ranking|construction|optimizer|replay|strategy.lab|backtest'`: one hit only, line 235, a negative assertion ("there is no persisted-artifact, ranking, construction, optimizer-handoff, or replay flow"). Every route path in `### Registered routers` (lines 33-47) resolved against the routers: `imports` prefix `/portfolios/import` + the 5 named subpaths (imports.py:14,37,49,59,71,104); `market_data` `/market-data/{quote-short, historical-price-light}` (market_data.py:6,9,19); `cache` `/cache/{stats, clear}` (cache.py:6,9,17); `exposure` `/engines/exposure/run` (exposure.py:7,10); `correlation` `/engines/correlation/{multi, intra}` (correlation.py:14,17,27); `currency_risk` `/engines/currency-risk/run` (currency_risk.py:6,9); the remaining `/engines/<x>/run` entries match their route modules. No `/backtests/*`, `/construction/*`, `/strategy-lab/*`, `/optimizer/*`, `/ranking/*` entry remains anywhere.

### AC2 — Every shipped router area represented — PASS
`app/api/routes/` non-`__init__` modules (15): attribution, cache, correlation, currency_risk, dashboard_history, diagnostics, distribution, drawdown, drift, exposure, health, imports, market_data, provenance, stress. `main.py:4` imports all 15; `main.py:18-32` calls `include_router` on all 15. Doc `### Registered routers` list (lines 33-47) names exactly those 15 stems. `test_stated_module_list_matches_actual_route_modules` enforces set-equality bidirectionally — passes.

### AC3 — No phantom service file — PASS
`grep -nE 'portfolio_backtest_engine|construction_run_service|construction_artifact_service|strategy_lab|replacement_ranking|replacement_ranking_artifact_service|optimizer_preview_service|optimizer_handoff_constraints'` on the doc: no match — all 8 removed files gone. All 25 files named in `### Service layer` (lines 61-65) exist under `app/services/` (verified by `ls`): the 12 `*_engine.py` incl. `intra_correlation_engine.py`, the 6 import-path files, `market_data.py`, `cache_admin.py`, and the 5 shared files.

### AC4 — Engine purpose matches shipped capability — PASS
Line 14 now: "deterministic finance and quant engines for portfolio import and for snapshot / synthetic-history analytics — exposure, diagnostics, dashboard history, drift, attribution, correlation, currency risk, stress, drawdown, distribution, and provenance". No ranking / construction / optimizer / replay.

### AC5 — Truth-class list carries no removed surface — PASS
Lines 73-76: `broker-truth historical diagnostics`, `snapshot current-state analytics`, `synthetic snapshot-history diagnostics`, `persisted import artifacts (content-addressed, immutable)`. The three removed entries (`persisted construction artifacts`, `hypothetical optimizer previews and handoffs`, `replay-derived hypothetical outputs`) are gone (diff hunk `@@ -116,3 +76 @@`). The four that remain are CLAUDE.md's four truth classes.

### AC6 — Data Flow describes the shipped flow only — PASS
`## Data Flow` (lines 222-235) retains exactly one subsection, `### Portfolio import and analytics`. Diff hunk `@@ -280,65 +235 @@` deletes old lines 280-344 wholesale — the `### Ranking, construction, optimizer, and replay` subsection and all six `### Persisted … artifact rule` / `### Optimizer handoff rule` subsections. Step 5 reworded (hunk `@@ -275 +230 @@`) to name the 11 engines. Finite-only import-admission paragraph (line 233) retained byte-identical. One plan-sanctioned negative-assertion sentence added at line 235.

### AC7 — API Boundary stops asserting removed seams — PASS
Lines 201-205. Diff hunk `@@ -248,3 +205,0 @@` deletes the "formed candidates, constructed candidates, persisted construction artifacts, optimizer previews, optimizer handoffs, hypothetical replays, and saved proposals" bullet and the "Future normalized API groups should preserve … construction, optimizer handoff, and replay" line. Hunk `@@ -246 +204 @@` drops "or persisted immutable research artifacts" from the engine-outputs bullet. What remains: snapshot-first persistence + thin-frontend rules.

### AC8 — Market-data section untouched — PASS
`git diff -U0` hunk old-line ranges: 14, 24-25, 30-107, 116-118, 246, 248-250, 275, 280-344, 357. No hunk falls in old lines 119-245. The market-data section (old ~131-239) is entirely inside that gap. Anchors intact in current file: `### Market-data providers and data provenance` (line 89), "never auto-corrects the registry or remaps the symbol" (line 196).

### AC9 — Trust-semantics rule untouched — PASS
No `-U0` hunk in old lines 119-245; the trust-rule bullets (old ~122-129) are inside that gap. Current file: `Architecture-level trust rule:` (line 80), `Docs and UI must not collapse \`withheld\` into generic \`unavailable\`.` (line 87) — present, unchanged.

### AC10 — Accepted-tradeoff note untouched — PASS
No `-U0` hunk in old lines 251-274; the note (old ~252-265) is inside that gap. Current file: `**Accepted tradeoff — unauthenticated local file-read (import routes).**` (line 207), full paragraph read through line 220 — intact.

### AC11 — A mechanical guard exists — PASS
New sibling `services/quant-engine/app/tests/test_architecture_doc_route_inventory.py`. `test_stated_module_list_matches_actual_route_modules` computes `undocumented = actual - stated` and `phantom = stated - actual`, asserts each empty, and the failure messages name the specific modules ("Add a bullet row for each: …" / "Remove the stale row(s) …: …"). Bidirectional; names the offender, matching `test_route_inventory.py`'s convention. `test_stated_count_matches_actual_router_count` also cross-checks the count-header integer against both the directory and the list length.

### AC12 — The guard is not vacuous — PASS
`test_the_scan_is_not_vacuous` present: asserts the doc and routes dir exist, `actual_modules` non-empty and `"exposure" in actual_modules`, `stated_count > 0`, `stated_modules` non-empty and `"exposure" in stated_modules` — positive-direction resolution, mirroring `test_route_inventory.py`. Falsifiability confirmed: `git stash push -- docs/architecture/system-architecture.md`, then `pytest test_architecture_doc_route_inventory.py` → 3 failed (`assert count_match` fires in `_doc_stated_count_and_modules()`, which all three tests call). `git stash pop`, re-run → 3 passed. Red-before / green-after holds by execution.

### AC13 — The full suite is green — PASS
`python scripts/run_all_tests.py`: golden regen → backend `947 passed, 45 warnings` → frontend `40 passed (40) / 359 passed (359)` → `tsc --noEmit` clean → dead-code strict gate `ruff: clean, vulture: clean, knip: clean`. Final line "All tests passed."

## Test plan fidelity

Story `## Test plan` — Backend (pytest):
- "every route entry … resolves to a route registered … (no phantom entry)" — `test_stated_module_list_matches_actual_route_modules` phantom assertion. Delivered.
- "every registered router area is represented (no undocumented router)" — same test, undocumented assertion. Delivered.
- "a drift failure names the specific missing or phantom entry" — assert messages interpolate `', '.join(undocumented)` / `', '.join(phantom)`. Delivered.
- "a non-vacuous-scan guard … mirroring test_the_scan_is_not_vacuous" — `test_the_scan_is_not_vacuous`, one-for-one. Delivered.

Story `## Test plan` — Regression / guardrail:
- "existing test_route_inventory.py assertions for current-product-state.md stay green" — ran both files together: 6 passed, the 3 sibling tests unbroken. New file is a copy, not an import; `current-product-state.md` checks and `system-architecture.md` checks live in separate files, independently diagnosable by node id. Delivered.
- "No engine, analytics, schema or contract behaviour changes" — diff touches only `docs/architecture/system-architecture.md` (46 ins / 155 del) and the one new test file. No schema, route, analytics or contract-doc change. Holds.

## Trust-state spot checks

No schema field added or changed; no synthetic field, nullable field, or market-data caller introduced. The truth-class list edit (AC5) removes labels for deleted product surfaces and aligns the remainder with CLAUDE.md's four classes; the `verified/degraded/withheld/unavailable` trust-rule bullets are a protected fence (AC9) and are byte-identical. No trust-semantics regression.

## Repo hygiene

No golden artifact changed (the suite's golden-regen step ran and left the tree clean). No stray files from this story beyond the intended two (doc edit + new test). Story status is `Backlog` / "story draft for human review" — consistent with an unaccepted story now passing its acceptance gate; epic placement and final number remain the owner's call per `## Open decisions`, unaffected by this verdict.
