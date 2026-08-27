REPORT 2026-08-27-next-epic-or-story/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - docs/architecture/system-architecture.md is ~30 epics stale: its entire "Current Implemented Backend Seams" + "Data Flow" + all "Persisted ... artifact rule" sections describe /backtests, /construction, /strategy-lab, /optimizer routes and services removed in Epic 8; none of the 15 actual route modules are documented there — see § A. system-architecture.md (doc-vs-code, high)
  - docs/product/stories/README.md carries 6 stale epic-status labels: Epic 35/34/32/26/24 headed "(active)" and Epic 28 headed "(backlog)" while epic-roadmap.md has all six as "Completed Epic" — see § B. stories/README.md
  - docs/product/stories/README.md has no Epic 30 heading — US-30.1..30.6 are listed under the "Epic 28" heading though a real Epic 30 roadmap section and PRD file both exist — see § B. stories/README.md
  - "PRD: none" for Epic 40 is stated in three places (epic-roadmap.md:83, stories/README.md:23, both US-40.1/US-40.2 headers) but docs/product/prd/epic-40-snapshot-trust-and-fidelity-follow-through.md exists — a retrospective PRD added after close-out — see § C. Epic 40 PRD
  - docs/product/stories/US-41.1-inline-withheld-return-annotation.md exists on disk but appears in no index in stories/README.md (no Epic 41 section anywhere) — orphan, placeholder number US-41.x — see § B. stories/README.md
  - docs/product/prd/README.md § Index lists only Epic 5 ("Active") and Epic 3 and promises "PRDs for Epics 6 and 7" — ~35 epics / 32 PRD files out of date, no pointer to epic-roadmap.md — see § D. prd/README.md
  - docs/product/current-product-state.md header (line 3) reads "Updated: 2026-08-19 (after Epic 34 ...)" while its body covers US-35.1, a 2026-08-26 audit, US-37.1, US-38.1, US-39.1, US-40.1/40.2 — header date never bumped — see § E. current-product-state.md
  - docs/finance/financial-methodology.md's pre-US-34.8 stale withholding rule (fixed by run 2026-08-26-missing-chart-data-0414/04-docs.md) is now internally consistent — passages at 2438-2446, 565-638 and 2563-2568 all state the US-34.8 supersession coherently; no residual "terminal day is withheld" live framing found — see § F. financial-methodology.md
  - financial-methodology.md quotes the terminal reconciliation adjustment as "-$58.11" (line 2424) and "-$19.98" (line 587); story US-34.3 says "-$53.13" — the -$53.13 is unreconciled with either (low) — see § F. financial-methodology.md
  - CLAUDE.md lines 41 and 203 name epic-34 PRD as "most-recently shipped" / "the most recent is Epic 34"; actual most-recent is Epic 40 — both sites explicitly hedge and defer to epic-roadmap.md (self-admitted, by design, now 6 epics behind) — see § G. CLAUDE.md and pack
  - stories/README.md:504-505 and prd/README.md:29 instruct agents to invoke the build-story skill, which .agentic project.md says is "superseded and must not run" — see § G. CLAUDE.md and pack
  - contract-doc vs schema drift was sampled (dashboard-fields.md), not exhaustively diffed across all 12 contracts x 20 schemas — sample was clean — see § H. contracts vs schemas
  - epic-roadmap.md snapshot ("every epic complete / no epic active / next unscoped") is consistent with git state and current-product-state.md body; no active-epic drift of the kind US-32.3 fixed — see § I. what is NOT drifted

risks:
  - The 12-contract x 20-schema field-level diff (DoD item 5) was not performed exhaustively; a recon budget cannot carry it. Sample (dashboard-fields.md) showed no drift, and mechanical guards exist (schema_edit_reminder.py PostToolUse hook, test_docs_paths.py). A dedicated docs-lane pass is the right tool if exhaustive certainty is wanted.
  - I did not run the test suite, so "route file X does not exist" is from a Glob of app/api/routes/, not from an import graph; a route could in principle be registered from elsewhere (none observed).
  - Severity tags are my reading of the DoD's ordering (financial/trust contradiction > stale label > cosmetic); the producer sets the real priority.
  - "Epic 40 PRD exists" vs three "PRD: none" statements: the PRD's own Notes section says it was written retrospectively and "does not change any acceptance verdict" — so this is a pointer-staleness finding, not a shipped-state discrepancy.

## Orchestrator brief

- verdict: NONE — recon only. A ground-truth map of documentation drift for the producer's cleanup verdict.
- biggest single finding: docs/architecture/system-architecture.md is a pre-Epic-8 document — its route/seam inventory (the thing CLAUDE.md and project.md both name it as source of truth for) describes a ranking/construction/optimizer product deleted ~30 epics ago. § A.
- second cluster: docs/product/stories/README.md — 6 stale "(active)"/"(backlog)" epic labels, a missing Epic 30 heading, an orphan US-41.1 file, build-story instructions that contradict the agentic pack. § B.
- Epic 40 PRD DOES exist (contra a prior run's flag and contra 3 "PRD: none" statements) — it is a retrospective PRD; the drift is 3 stale pointers, not a missing artifact. § C.
- prd/README.md § Index is ~35 epics stale (lists Epic 5 as Active). § D.
- current-product-state.md: body is current (~Epic 40), header date/parenthetical stuck at "2026-08-19 / after Epic 34". § E.
- financial-methodology.md: the withholding-rule fix from run 2026-08-26-missing-chart-data-0414 is complete and consistent — confirmed, no residual stale framing. One minor cross-doc numeric mismatch (-$53.13 vs -$58.11/-$19.98). § F.
- CLAUDE.md epic-34 pointer is stale-but-hedged (by design, US-32.3); build-story guidance in repo docs conflicts with the pack. § G.
- contracts vs schemas: sampled clean, not exhaustively diffed (see risks). § H.
- epic-roadmap.md snapshot itself is NOT drifted — consistent with git + current-product-state. § I.
- sections below: A system-architecture.md · B stories/README.md · C Epic 40 PRD · D prd/README.md · E current-product-state.md · F financial-methodology.md · G CLAUDE.md and pack · H contracts vs schemas · I what is NOT drifted

---

## A. system-architecture.md

`docs/architecture/system-architecture.md` (365 lines). CLAUDE.md:45 names it
"System seams, route inventory, truth class semantics"; project.md § Sources of
truth names it "What are the backend seams?". Its route inventory is unguarded
by any mechanical test (`test_route_inventory.py` from US-36.3 checks
`current-product-state.md`, not this file).

Stale sections (describe features removed in Epic 8, US-8.5/US-8.6):

| Lines | Content | Reality |
|---|---|---|
| 14 | engine purpose = "imports, diagnostics, ranking, construction, optimizer preview, and replay" | ranking/construction/optimizer/replay all removed |
| 28-98 | "Current Implemented Backend Seams" — `POST /backtests/portfolio-allocation*`, `/construction/run`, `/construction/artifacts/{id}`, `/strategy-lab/etf-ranking*`, `/strategy-lab/ranking/*`, `/optimizer/preview`, `/ranking/etf-replacements` | none of these routes exist |
| 100-107 | services `portfolio_backtest_engine.py`, `construction_run_service.py`, `construction_artifact_service.py`, `strategy_lab.py`, `replacement_ranking.py`, `replacement_ranking_artifact_service.py`, `optimizer_preview_service.py`, `optimizer_handoff_constraints.py` named as "current" seams | none of these service files exist |
| 267-345 | "Data Flow → Ranking, construction, optimizer, and replay" + 6 "Persisted ... artifact rule" subsections + "Optimizer handoff rule" | entire flow describes removed product |
| 116-118, 248-250, 355 | truth classes / API groups referencing "persisted construction artifacts", "optimizer previews and handoffs", "replay-derived hypothetical outputs" | not shipped |

Actual `app/api/routes/` (15 non-`__init__` modules, none documented in this
file): `health`, `market_data`, `exposure`, `dashboard_history`, `diagnostics`,
`drift`, `attribution`, `stress`, `drawdown`, `distribution`, `correlation`,
`provenance`, `cache`, `currency_risk`, `imports`.

Sections that ARE current and accurate:
- "Market-data providers and data provenance" (lines 131-239) — updated through
  US-35.1, US-18.x, US-19.x, US-20.2, US-20.3.
- "Truth Classes and Trust Semantics" (109-129).
- "Accepted tradeoff — unauthenticated local file-read" (252-265) — added by US-36.3.
- Line 18's note that `ImportAdmissionReviewDispositionV1` was removed in US-23.9
  is correct.
- "Documentation Rule" (359-365).

Severity: high (canonical doc, self-describes as route-inventory source of
truth, ~30 epics / ~2 months stale, mechanically unguarded). Not itself a
financial/trust claim.

## B. stories/README.md

`docs/product/stories/README.md`.

Stale epic-status labels (all contradicted by `epic-roadmap.md`, which has each
as `## Completed Epic`):

| Line | Heading | Roadmap says | Story rows |
|---|---|---|---|
| 82 | Epic 35 — Market-Data Failure Honesty **(active)** | Completed, closed 2026-08-19 | all 3 Done |
| 92 | Epic 34 — An Answerable Dashboard **(active)** | Completed, closed 2026-08-19 | all Done |
| 125 | Epic 32 — Project Hygiene **(active)** | Completed Epic 32 | all 3 Done |
| 221 | Epic 26 — Currency Exposure & Risk **(active)** | Completed Epic 26 | US-26.1/26.2 Done |
| 232 | Epic 24 — Codebase Improvement **(active)** | Completed Epic 24 | all 12 Done |
| 162 | Epic 28 — IBKR CSV Importer **(backlog)** | Completed Epic 28 | all rows Done |

Structural:
- No `### Epic 30` heading. US-30.1, US-30.2, US-30.3, US-30.4, US-30.5a,
  US-30.5b, US-30.5c, US-30.6 (lines 166-175) are listed under the
  `### Epic 28 ... (backlog)` heading. A real `## Completed Epic: Epic 30 —
  Exposure Improvements` section exists in epic-roadmap.md:1036 and a PRD file
  `docs/product/prd/epic-30-exposure-improvements.md` exists.
- Orphan: `docs/product/stories/US-41.1-inline-withheld-return-annotation.md`
  exists but is in no index here (no Epic 41 section, not in any backlog list).
  Its header: `Epic: Unassigned`, `PRD: none yet`, `Status: Backlog`; number
  `US-41.x` is a self-declared placeholder (matches 01-delivery-brief.md
  § Placement).

Pointer/staleness:
- Lines 21-23 (Epic 40 block): `PRD: none — see US-40.1/US-40.2 ...` — the PRD
  file exists (see § C).
- Lines 504-505: "To implement a story, invoke the `build-story` skill. To
  author a new story from a feature idea, invoke the `write-story` skill." —
  build-story is "superseded and must not run" per
  `.agentic/projects/portfolio/project.md`.

Cosmetic:
- "(complete)" vs "(completed)" mixed (Epics 20/21/22 use "completed").
- Section order non-monotonic: ...29, 28, 27, 25, 26, 24, 23...

Severity: stale labels (6x) + one structural (missing Epic 30 heading) + one
orphan file. No financial/trust claim affected.

## C. Epic 40 PRD

`docs/product/prd/epic-40-snapshot-trust-and-fidelity-follow-through.md` EXISTS
(34 PRD files total; this is one of them). Header: `Status: Completed`,
`Created: 2026-08-25`, `Closed: 2026-08-25`. Its own `## Notes` section (lines
169-180): "This epic's own PRD was itself a close-out gap, corrected
retrospectively ... This file is that correction, written by a dedicated
follow-up order once the gap was noticed."

Three places still say the PRD does not exist:
- `docs/product/epic-roadmap.md:83-88` — "**PRD:** none — this close-out's scope
  excluded `docs/product/prd/`, so no retrospective PRD file was created".
- `docs/product/stories/README.md:23` — "PRD: none".
- `docs/product/stories/US-40.1-...md` and `US-40.2-...md` `**PRD:**` headers
  (per the PRD's Notes, "see both story files' `**PRD:**` headers").

`epic-roadmap.md`'s snapshot line 3 ("Updated: 2026-08-25") predates the PRD's
retrospective creation, which explains but does not resolve the drift.

Severity: stale pointer (3-4 sites). The PRD Notes confirm no shipped-state /
verdict / test-count discrepancy — content-wise the roadmap and story files are
accurate, only the "PRD: none" pointer is wrong.

01-delivery-brief.md § Placement asserts "no PRD file" for Epic 40 implicitly by
saying the highest real epic is 40 and a prior run flagged Epic 40 "may have
shipped with no PRD" — that prior flag is now stale; the PRD landed.

## D. prd/README.md

`docs/product/prd/README.md` § Index (lines 41-49):

```
| PRD | Epic | Status |
| epic-5-usable-core-flow.md | Epic 5 — Usable Core Flow | Active |
| epic-3-construction-optimizer-methodology.md | Epic 3 ... | Foundation complete |
PRDs for Epics 1, 2, 4 are not written separately ...
PRDs for Epics 6 and 7 will be written when those epics become active.
```

Reality: 34 PRD files in `docs/product/prd/`, epics through 40 shipped. Epic 5
is `complete — superseded by Epic 8 pivot` (per stories/README.md). No pointer
to `epic-roadmap.md` as the real epic index.

Also line 29: "An agent delivers a story with the `build-story` skill" — same
build-story conflict as § B / § G.

Severity: severe staleness, low real impact (no agent is likely routed here for
"which epic is current"; CLAUDE.md and project.md both point at epic-roadmap.md).

## E. current-product-state.md

`docs/product/current-product-state.md:3`:
"*Canonical shipped-state inventory. Updated: 2026-08-19 (after Epic 34 — an
answerable Dashboard: ...).*"

Body content past that point:
- line 33: "The chart's portfolio line and range-filtering are now both correct
  (2026-08-26 audit)"
- line 34: US-35.1 (Epic 35)
- lines 66-72: US-37.1 (Epic 37)
- lines 76-88: US-38.1 (Epic 38)
- lines 89-99: US-39.1 (Epic 39)
- line 129: US-40.1 (Epic 40); line ~130/175 (omitted-long lines) likely US-40.2

So the header's date (2026-08-19) and "(after Epic 34)" parenthetical lag the
body by ~4 epics plus a dated audit. Body spot-checks as accurate (e.g. it does
not claim `PerformancePoint.withheld_reason`, consistent with US-41.1 being
unbuilt).

Severity: stale label (header date/epic ref only; body is current).

## F. financial-methodology.md

DoD item: confirm the pre-US-34.8 stale withholding-rule fix (run
2026-08-26-missing-chart-data-0414, artifact 04-docs.md, ~lines 2436-2568) is
complete and consistent.

Finding: it is consistent now. The three relevant passages agree:
- lines 2438-2446: "Rule (US-34.8, superseding the withholding rule this section
  stated before US-34.8 shipped): the reconciled terminal day is CORRECTED, not
  withheld." + points to `market_derived_terminal_value(states)`.
- lines 2448-2455: `return_is_publishable` is False "only for the OTHER cause"
  (material `unbacked_cash_flow`).
- § Terminal-value input rule (US-34.6), lines 565-638: coherent historical
  narrative — line 573 "which withholds the affected day" describes US-31.3's
  original behaviour and is explicitly corrected at lines 607-624 ("US-31.3 ...
  enforced that by WITHHOLDING the reconciled terminal day — because at the time
  no un-overwritten value existed. This rule creates one ...").
- lines 2563-2568 (risk-basis cross-ref): "The terminal day's
  `reconciliation_adjustment` no longer withholds a return; it is corrected via
  `market_derived_terminal_value` instead."

No residual live "terminal day is withheld" rule found anywhere in the file.

Minor cross-doc numeric mismatch (low severity, not a formula re-derivation):
- methodology:2424 — terminal reconciliation "+$1,366.17 → **−$58.11**"
- methodology:583-587 — "−$19.98" on the 2026-08-17 capture (explained: US-34.9
  re-capture)
- `docs/product/stories/US-34.3-...md` (per 01-delivery-brief.md and the story) —
  "terminal adjustment +$1,366.17 → −$53.13"
The −$53.13 figure is not reconciled with either methodology figure.

## G. CLAUDE.md and pack

- CLAUDE.md:41 — doc-map row: "`docs/product/prd/epic-34-...md` | Most-recently
  shipped epic PRD (Epic 34). **If this looks stale, `docs/product/epic-roadmap.md`
  is the source of truth ...**". Actual most-recent shipped is Epic 40.
- CLAUDE.md:203 — "At the time of writing the most recent is Epic 34 ..., but the
  roadmap is the authority — a named PRD here goes stale every time an epic
  ships."
Both are hedged by design (US-32.3 made the pointer defer to the roadmap), but
the literal statement is now 6 epics behind. Low severity by construction.

- CLAUDE.md repo-layout route list (line ~46): lists exposure, dashboard_history,
  diagnostics, drift, attribution, correlation, stress, drawdown, distribution,
  provenance, imports, market_data, cache, currency_risk, health — matches the
  15 actual route modules. Accurate (US-36.3 confirmed this).

- Build-story conflict: `.agentic/projects/portfolio/project.md` § "`build-story`
  is superseded and must not run"; but `docs/product/stories/README.md:504-505`
  and `docs/product/prd/README.md:29` still tell agents to invoke it. In-repo
  guidance vs agentic-network guidance.

## H. contracts vs schemas

DoD item 5 (documented field with no schema field / schema field with no
contract row) was sampled, not exhaustively diffed:
- `docs/contracts/dashboard-fields.md` vs `app/schemas/dashboard_history.py` and
  `reconciliation.py`: `window_start_date` (US-25.1/2026-08-26 audit) present in
  both; `withheld_return_dates`, `withheld_return_reason`,
  `withheld_return_impact_pct` present in both. `PerformancePoint`
  (`reconciliation.py:510-515`) has exactly `date`, `portfolio_value`,
  `benchmark_price`, `portfolio_return_pct`, `benchmark_return_pct` — no stray
  fields, no missing contract rows in the sample.
- Not checked field-by-field: `risk-fields.md`, `exposure-fields.md`,
  `attribution-fields.md`, `correlation-fields.md`, `intra-correlation-fields.md`,
  `factor-drift-fields.md`, `provenance-fields.md`, `import-admission-fields.md`,
  `cache-fields.md`, `diagnostics-fields.md` against their schemas.
- Mechanical guardrails that reduce (not eliminate) the risk here:
  `scripts/hooks/schema_edit_reminder.py` (PostToolUse on `app/schemas/`),
  `test_docs_paths.py` (bidirectional path claims, US-32.1).

12 contract docs, 20 schema files. A full diff is a docs-lane job.

## I. what is NOT drifted (checked, found current)

- `epic-roadmap.md` snapshot (lines 1-77): "Every epic is complete", "No epic is
  active", "The next epic is unscoped" — consistent with git state (Epic 40 the
  latest) and with `current-product-state.md`'s body. No repeat of the pre-US-32.3
  "Epic 31 active four epics later" failure.
- `epic-roadmap.md` per-epic sections: internally self-consistent on status
  (every closed epic is `## Completed Epic`), unlike stories/README.md.
- CLAUDE.md route list: accurate.
- `current-product-state.md` body: accurate to ~Epic 40.
- `financial-methodology.md` withholding/terminal-day passages: mutually
  consistent (see § F).
- `dashboard-fields.md` sample: in sync with schema.

Cosmetic-only (noted, not worth a cleanup story on their own):
- `epic-roadmap.md:780` heading `## Epic 33 — ... (complete)` vs neighbours'
  `## Completed Epic: Epic NN`.
- `epic-roadmap.md:1866` "Epic 8 — Reset to Portfolio Analysis Core" vs
  stories/README + PRD filename "Reset to Analysis Core".
