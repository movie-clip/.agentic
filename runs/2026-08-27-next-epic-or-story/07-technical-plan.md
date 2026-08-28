REPORT 2026-08-27-next-epic-or-story/07
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only DESIGN order, no verification command named

contract_notes:
  - US-41.2 changes NO Pydantic schema, NO route, NO response shape. Scope is one Markdown doc (docs/architecture/system-architecture.md) plus one new pytest file. No docs/contracts/<area>-fields.md entry and no apps/desktop TS type is affected — there is nothing for a downstream lane or the integration gate to mirror. This is not a REFUSED surprise; the story is buildable as written.

pack_corrections:
  - capabilities/architecture.md "The seams" section — its `/engines/{...}` route-prefix list omits `currency-risk`, but `POST /engines/currency-risk/run` is registered (app/api/routes/currency_risk.py:6,9). Fix: add `currency-risk` to that brace list.

handoff:
  - Lane split: T-41.2.2 (docs-engineer) rewrites the doc; T-41.2.3 (test-engineer) adds the guard. Dispatch T-41.2.2 first, then T-41.2.3 — the guard parses a structured block that T-41.2.2 creates, and AC12 requires the guard red on today's doc and green only after the rewrite. See § Lane split and dispatch order.
  - Guard decision (i): NEW sibling file services/quant-engine/app/tests/test_architecture_doc_route_inventory.py, not an extension of test_route_inventory.py. See § Guard test design.
  - Guard decision (ii): the rewritten inventory is keyed on route MODULE NAMES (bare stems, e.g. `exposure`, `dashboard_history`), presented as one unbroken 15-item bullet list under a fixed count-header sentence. Exact doc format the rewrite must emit is in § Guard test design → "Doc format contract".
  - Guard decision (iii): non-vacuous check mirrors test_the_scan_is_not_vacuous one-for-one — doc exists, routes dir exists, actual modules non-empty and contains `exposure`, header regex matched with count > 0, list regex matched and contains `exposure`. See § Guard test design.
  - "Data Flow" rewrite bounds CONFIRMED by reading lines 267-345: line 275 reworded, lines 280-344 deleted wholesale, lines 267-274 + 276 + 278 survive byte-identical. See § Data Flow rewrite bounds (confirmed).
  - Byte-identical fences confirmed at current line numbers: market-data section 131-239 (AC8), trust-rule bullets 122-129 (AC9), accepted-tradeoff note 252-265 (AC10). See § Replacement structure.
  - Region-by-region replacement structure for the six stale regions (seams inventory, implementation-reality service list, engine-purpose line 14, truth-class list 113-118, API Boundary 246/248/250, Data Flow) grounded in the 15 registered routers and their real services. See § Replacement structure.
  - AC traceability: all 13 ACs mapped to ticket + code/doc path. See § AC traceability.

risks:
  - Three removed-surface references fall OUTSIDE the story's AC map: lines 24, 25 (Core Architecture Rules — "persisted artifacts / hypothetical outputs", "fail-closed loading for … persisted artifacts") and line 357 (Desktop Workspace Model — "Review artifacts and persisted references …"). Same drift class as AC1/AC5/AC7; no AC names them.
  - Recommendation on lines 24/25/357: T-41.2.2 sweeps them (trivial word surgery) for internal consistency; the integration gate and reviewer should NOT block on them, as they are not AC-mapped. Flagged so leaving them is a conscious call.
  - Line 246 ("… or persisted immutable research artifacts") is inside the "API Boundary" section AC7 puts in scope though AC7's text names only 248/250. Treat 246 as in-scope-by-section — narrow to "import artifacts" or drop.
  - Dispatch may run T-41.2.2 and T-41.2.3 concurrently since this plan pins the doc format. Sequential is recommended anyway (one green run_all_tests.py pass; test author sees the real block). If concurrent, the integration gate must verify AC12's red-before property by reverting the doc hunk and re-running the guard.
  - The doc's optional grouped rendering of routers must not put blank lines inside the machine-parsed 15-bullet list — the guard's block ends at the first blank line, mirroring the existing test. The grouped view lives elsewhere in the section.

## Orchestrator brief

Decisions taken:
- Guard lands in a NEW sibling file `app/tests/test_architecture_doc_route_inventory.py` (not an extension of `test_route_inventory.py`) — matches US-36.3's own "narrow sibling, not widened" precedent and keeps that file's "only current-product-state.md" docstring true.
- Rewritten inventory is keyed on route MODULE NAMES as one unbroken 15-bullet list under a fixed count-header sentence (`The engine registers 15 routers`), so the guard reuses the existing test's regex+blank-line-boundary parsing almost verbatim.
- "Data Flow" bounds CONFIRMED (lines 267-345 read): reword line 275, delete lines 280-344, keep 267-274 / 276 / 278 byte-identical.
- Contract: US-41.2 changes no schema/route/response shape — nothing to mirror.
- Lane split: T-41.2.2 (doc rewrite) then T-41.2.3 (guard); guard must be red on today's doc, green after.

Blocks dispatch: none. Epic placement / story number are settled outside this lane (no new epic; number provisional) per the order's non_goals.

Sections below:
- § Ground truth (read from the tree, not the story) — the 15 routers, their paths, their real services.
- § Data Flow rewrite bounds (confirmed) — line-by-line: what is reworded, deleted, kept.
- § Replacement structure — the doc, region by region — the six stale regions + the three protected fences, with the router/service facts the docs lane writes prose from.
- § Guard test design — file placement rationale, the doc-format contract between T-41.2.2 and T-41.2.3, parsing spec, non-vacuous spec.
- § AC traceability — all 13 ACs → ticket → code/doc path.
- § Lane split and dispatch order — the two tickets, the dependency, the order, the AC12 red/green verification.

---

## Ground truth (read from the tree, not the story)

`services/quant-engine/app/api/routes/` — 15 non-`__init__` modules; `app/api/main.py` imports all 15 and calls `include_router` on all 15:

| Module | Prefix | Routes | Response model |
|---|---|---|---|
| `health` | (none) | GET /health | — |
| `imports` | /portfolios/import | POST /interactive-brokers, /combine-snapshots, /interactive-brokers/analyze, /interactive-brokers/analyze-upload, /interactive-brokers/analyze-snapshot | ImportedPortfolioSnapshot / ImportedBootstrapResponse |
| `exposure` | /engines/exposure | POST /run | ExposureResult |
| `diagnostics` | /engines/diagnostics | POST /run, /run-imported | DiagnosticsResult |
| `dashboard_history` | /engines/dashboard-history | POST /run, /run-imported | DashboardHistoryResult |
| `drift` | /engines/drift | POST /run | DriftResult |
| `attribution` | /engines/attribution | POST /run | FactorAttributionResponse |
| `correlation` | /engines/correlation | POST /multi, /intra | MultiBenchmarkCorrelationResult / IntraCorrelationResult |
| `stress` | /engines/stress | POST /run | StressEngineResponse |
| `drawdown` | /engines/drawdown | POST /run | DrawdownEngineResponse |
| `distribution` | /engines/distribution | POST /run | DistributionEngineResponse |
| `provenance` | /engines/provenance | POST /run | ProvenanceResult |
| `currency_risk` | /engines/currency-risk | POST /run | CurrencyRiskResult |
| `market_data` | /market-data | GET /quote-short, /historical-price-light | (raw) |
| `cache` | /cache | GET /stats, POST /clear | CacheStats / CacheClearResult |

`services/quant-engine/app/services/` — real files, mapped to their route:

- Per-engine: `exposure_engine`, `diagnostics_engine`, `dashboard_history_engine`, `drift_engine`, `attribution_engine`, `correlation_engine`, `intra_correlation_engine`, `stress_engine`, `drawdown_engine`, `distribution_engine`, `provenance_engine`, `currency_risk_engine`.
- Import path: `import_engine`, `import_engine_composer`, `statement_importer`, `import_admission`, `portfolio_snapshot_builder`, `history_context_builder`.
- Market data: `market_data` (`MarketDataService`).
- Cache: `cache_admin`.
- Shared / supporting: `benchmark_service`, `holdings_history`, `instrument_enrichment`, `instrument_identity`, `portfolio_proof`.

**None** of the eight service files the doc names today (`portfolio_backtest_engine.py`, `construction_run_service.py`, `construction_artifact_service.py`, `strategy_lab.py`, `replacement_ranking.py`, `replacement_ranking_artifact_service.py`, `optimizer_preview_service.py`, `optimizer_handoff_constraints.py`) exists. **None** of the `/backtests/*`, `/construction/*`, `/strategy-lab/*`, `/optimizer/*`, `/ranking/*` route paths resolves.

---

## Data Flow rewrite bounds (confirmed)

Recon flagged "~267-345" without reading it. Read line-by-line now. The section is `## Data Flow` at line 267 through line 345 (line 346 is `## Desktop Workspace Model`). Verdict:

| Lines | Content | Disposition |
|---|---|---|
| 267 | `## Data Flow` heading | **keep byte-identical** |
| 268 | blank | keep |
| 269-270 | `### Portfolio import and analytics` + blank | **keep byte-identical** |
| 271-274 | steps 1-4 (import → normalize → build snapshot → persist) | **keep byte-identical** |
| 275 | step 5 — "call dedicated engines for diagnostics, **ranking, construction, replay, optimizer preview,** and monitoring" | **REWORD** — strip the removed capabilities. Replacement: "call dedicated engines (exposure, diagnostics, dashboard-history, drift, attribution, correlation, currency-risk, stress, drawdown, distribution, provenance) as appropriate". |
| 276 | step 6 — "send derived outputs to the UI with explicit provenance and trust metadata" | **keep byte-identical** |
| 277 | blank | keep |
| 278 | "Import admission evidence is finite-only for numeric observed…" paragraph | **keep byte-identical** — describes shipped import-admission behaviour (ImportAdmissionSummaryV1), still accurate. |
| 279 | blank | keep |
| 280-288 | `### Ranking, construction, optimizer, and replay` subsection (heading + 6 steps + blanks) | **DELETE** |
| 289-295 | `### Persisted ETF ranking artifact rule` (heading + 4 bullets + blank) | **DELETE** |
| 296-307 | `### Persisted intent-bound ETF replacement ranking artifact rule` | **DELETE** |
| 308-318 | `### Generalized ranking artifact discovery rule` | **DELETE** |
| 319-331 | `### Persisted generic ranking artifact rule` | **DELETE** |
| 332-339 | `### Persisted construction artifact rule` | **DELETE** |
| 340-345 | `### Optimizer handoff rule` (heading + 3 bullets + trailing blank) | **DELETE** |

**Net result:** `## Data Flow` retains exactly one subsection — `### Portfolio import and analytics` — with step 5 reworded and the finite-only import-admission paragraph intact. ~65 lines (280-344) are removed. No new prose is required beyond the step-5 reword; the docs lane may optionally add a one-line sentence noting the engines are all snapshot-analytics / synthetic-history reads with no persisted-artifact or replay flow, but that is discretionary.

---

## Replacement structure — the doc, region by region

The docs lane writes the prose. This section fixes the structure and the facts.

### R1 — Engine-purpose sentence, line 14 (AC4)

Today: "deterministic finance and quant engines for imports, diagnostics, ranking, construction, optimizer preview, and replay".

Becomes a sentence naming only shipped capability, e.g.: "deterministic finance and quant engines for portfolio import and for snapshot / synthetic-history analytics — exposure, diagnostics, dashboard history, drift, attribution, correlation, currency risk, stress, drawdown, distribution, and provenance". No ranking / construction / optimizer / replay.

### R2 — "Current Implemented Backend Seams", lines 28-98 (AC1, AC2)

Delete the three subsections wholesale (`### Replay and portfolio-improvement seams` 30-43, `### Construction seams` 45-56, `### Ranking and optimizer seams` 58-98, including the trailing generalized-platform paragraph at line 98). Replace with a single subsection whose first content is the machine-resolvable block the guard parses:

```
### Registered routers

The engine registers 15 routers (`services/quant-engine/app/api/main.py`):

- `health` — GET /health; liveness probe
- `imports` — POST /portfolios/import/{interactive-brokers, combine-snapshots, interactive-brokers/analyze, interactive-brokers/analyze-upload, interactive-brokers/analyze-snapshot}; IBKR statement + snapshot import, bootstrap analytics
- `exposure` — POST /engines/exposure/run -> ExposureResult
- `diagnostics` — POST /engines/diagnostics/{run, run-imported} -> DiagnosticsResult
- `dashboard_history` — POST /engines/dashboard-history/{run, run-imported} -> DashboardHistoryResult
- `drift` — POST /engines/drift/run -> DriftResult
- `attribution` — POST /engines/attribution/run -> FactorAttributionResponse
- `correlation` — POST /engines/correlation/{multi, intra} -> MultiBenchmarkCorrelationResult / IntraCorrelationResult
- `stress` — POST /engines/stress/run -> StressEngineResponse
- `drawdown` — POST /engines/drawdown/run -> DrawdownEngineResponse
- `distribution` — POST /engines/distribution/run -> DistributionEngineResponse
- `provenance` — POST /engines/provenance/run -> ProvenanceResult
- `currency_risk` — POST /engines/currency-risk/run -> CurrencyRiskResult
- `market_data` — GET /market-data/{quote-short, historical-price-light}; FMP / yfinance passthrough
- `cache` — GET /cache/stats, POST /cache/clear; FMP cache admin
```

Constraints for the docs lane:
- The list is **one contiguous 15-bullet block, no blank lines between bullets** (the guard's block boundary is the first `\n\n`).
- Each bullet starts `- \`<module_name>\`` with the **bare module name** (underscores, no `.py`) as the first backticked token.
- The count-header sentence must match `^The engine registers (\d+) routers?\b` — keep that exact phrasing; the integer must be `15`.
- A grouped, human-readable rendering (engines / import / infrastructure) may follow the block as separate prose if desired, but the block above is canonical.

### R3 — "Important implementation reality", lines 100-107 (AC3)

Delete all six bullets (every service file named is phantom). Replace with a "### Service layer" subsection stating that each engine route is a thin wrapper over one service under `app/services/`, and listing the **real** files from § Ground truth (per-engine `*_engine.py` + `intra_correlation_engine.py`; the import-path set; `market_data.MarketDataService`; `cache_admin`; shared `benchmark_service` / `holdings_history` / `instrument_enrichment` / `instrument_identity` / `portfolio_proof`). No file may be named that is absent from `app/services/`.

### R4 — Truth-class bulleted list, lines 113-118 (AC5)

Keep lines 111 (intro "The project uses explicit truth classes…") and 120 ("These must remain visibly distinct…"). In the list (113-118): **keep** `broker-truth historical diagnostics`, `snapshot current-state analytics`, `synthetic snapshot-history diagnostics`. **Delete** `persisted construction artifacts`, `hypothetical optimizer previews and handoffs`, `replay-derived hypothetical outputs`. Add one entry for persisted import artifacts (content-addressed, immutable) so the list matches the four truth classes CLAUDE.md enumerates (Broker Truth / Snapshot Analytics / Synthetic History / Persisted Imports) — every remaining class must be one the shipped engine actually emits.

### R5 — "API Boundary", lines 241-250 (AC7)

Keep lines 243-245 (snapshot-first persistence; engine outputs are derived runtime artifacts; frontend may persist `PortfolioSnapshot` + workspace metadata, not derived analytics as truth). Edit line 246 — "or persisted immutable research artifacts" → drop or narrow to "persisted immutable import artifacts". Delete line 248's clause listing "formed candidates, constructed candidates, persisted construction artifacts, optimizer previews, optimizer handoffs, hypothetical replays, and saved proposals". Delete line 250 ("Future normalized API groups should preserve … construction, optimizer handoff, and replay"). What remains: the snapshot-first persistence rule and the thin-frontend rule.

### R6 — Data Flow, lines 267-345 (AC6)

Per § Data Flow rewrite bounds (confirmed).

### Protected fences — must be byte-identical before/after (AC8, AC9, AC10)

Confirmed at their current line numbers by reading the file:

| Region | Lines | Guarded by |
|---|---|---|
| `### Market-data providers and data provenance` (heading through the instrument-identity mismatch paragraph ending "…never auto-corrects the registry or remaps the symbol.") | 131-239 | AC8 |
| `Architecture-level trust rule:` label + the four `verified_* / degraded_* / withheld / unavailable` bullets + "Docs and UI must not collapse `withheld` into generic `unavailable`." | 122-129 | AC9 |
| `**Accepted tradeoff — unauthenticated local file-read (import routes).**` paragraph | 252-265 | AC10 |

Note the market-data section's uses of "candidate(s)" (lines 135, 140, 166) are symbol-resolution vocabulary ("ordered candidates", "most candidates fail"), unrelated to the removed candidate-construction product — they stay.

### Out of scope for this story (leave alone)

Lines 1-13, 15-21 (System Boundaries body, ImportAdmission paragraph — line 18's US-23.9 removal note is correct per scout), 346-358 (Desktop Workspace Model — but see the risks bullet on line 357), 359-365 (Documentation Rule — current). Line 24-25 (Core Architecture Rules): see risks — recommended sweep, not AC-blocking.

---

## Guard test design

### Decision (i) — new sibling file, not an extension

`services/quant-engine/app/tests/test_architecture_doc_route_inventory.py`, a new file. Rationale:

1. **Precedent.** `test_route_inventory.py`'s own module docstring records that US-36.3 deliberately chose "narrowly scoped rather than folded into `test_docs_paths.py`". A new narrow sibling is the established move for this exact class, not widening an existing guard.
2. **Keeps the existing docstring true.** `test_route_inventory.py` states "Scope is deliberately narrow: only the route-module bullet list. No other claim in `current-product-state.md` is checked here." Adding a second doc target contradicts that.
3. **Independent diagnosability.** The test plan requires the `current-product-state.md` checks and the `system-architecture.md` checks to "both run and both be independently diagnosable on failure". Two files give that structurally — a failure names which doc drifted from the test node id alone.
4. **Different key, minimal shared logic.** `current-product-state.md` lists module filenames with `.py`; the `system-architecture.md` rewrite lists bare module names (decision ii). The regexes differ enough that sharing helpers would be forced.

The new file may copy `test_route_inventory.py`'s structure (module-level path constants, `_actual_route_modules()`, `_doc_stated_count_and_modules()`, three test functions). Copy, do not import — the constants and regexes differ.

### Decision (ii) — keyed on route module names

The rewritten inventory is keyed on **route module names** (bare stems: `exposure`, `dashboard_history`, `currency_risk`, …), presented as the single contiguous 15-bullet block specified in § R2.

Why module names over full route paths:
- **Mechanically cheap and low-maintenance.** `{p.stem for p in ROUTES_DIR.glob("*.py") if p.name != "__init__.py"}` is the exact resolution the existing guard already proves works. Resolving full route paths would require importing the FastAPI app (heavy: builds every engine dependency) or a brittle multi-file regex over `@router` decorators.
- **Satisfies AC1 and AC2 together.** AC2 ("every shipped router area represented") is a module-level claim — a bidirectional set-equality check answers it directly. AC1 ("no phantom route path in the inventory") is satisfied structurally: if the canonical inventory block is a 15-item module list and every item maps 1:1 to a registered router, there is no slot for a `/backtests/*` path to hide. Phantom paths in surrounding *prose* are caught by the T-41.2.2 rewrite + reviewer/integration read, exactly as the existing guard is structure-scoped, not prose-scoped.

### Doc format contract (binds T-41.2.2 ↔ T-41.2.3)

The rewrite MUST produce, inside `## Current Implemented Backend Seams`:

1. A subsection heading `### Registered routers`.
2. A count-header sentence matching `^The engine registers (\d+) routers?\b` (MULTILINE). Integer = number of non-`__init__` modules in `app/api/routes/` (15 today).
3. Immediately after (one blank line), a **single unbroken bullet list**, one bullet per router, each line matching `^-\s+\`([a-z0-9_]+)\`` where the capture is the bare module stem. No blank line inside the list. List ends at the first `\n\n`.

### Parsing spec (T-41.2.3)

```
REPO_ROOT       = Path(__file__).resolve().parents[4]
SYSTEM_ARCH_DOC = REPO_ROOT / "docs" / "architecture" / "system-architecture.md"
ROUTES_DIR      = REPO_ROOT / "services" / "quant-engine" / "app" / "api" / "routes"

_COUNT_HEADER_RE = re.compile(r"^The engine registers (\d+) routers?\b", re.MULTILINE)
_LIST_ITEM_RE    = re.compile(r"^-\s+`([a-z0-9_]+)`", re.MULTILINE)

_actual_route_modules() -> set[str]:
    {p.stem for p in ROUTES_DIR.glob("*.py") if p.name != "__init__.py"}

_doc_stated_count_and_modules() -> (int, set[str]):
    text = SYSTEM_ARCH_DOC.read_text("utf-8")
    m = _COUNT_HEADER_RE.search(text); assert m, "<header-shape-changed message>"
    block = text[m.end():]; nl = block.find("\n\n");  block = block[:nl] if nl != -1 else block
    return int(m.group(1)), set(_LIST_ITEM_RE.findall(block))
```

Test functions (mirror `test_route_inventory.py` names + messages):

- `test_stated_count_matches_actual_router_count` — `stated_count == len(actual)`; failure prints both numbers and the sorted actual set.
- `test_stated_module_list_matches_actual_route_modules` — compute `undocumented = actual - stated` and `phantom = stated - actual`; assert each empty, naming the specific offending module(s) ("add a bullet row" / "remove the stale row — do not create the file"). This is the AC11 "name the offending entry" requirement.
- `test_the_scan_is_not_vacuous` — mirror one-for-one (AC12, decision iii): `SYSTEM_ARCH_DOC.exists()`; `ROUTES_DIR.exists()`; `actual` non-empty; `"exposure" in actual` (positive-direction resolution proof); after parsing, `stated_count > 0`; `stated_modules` non-empty; `"exposure" in stated_modules`. Each with a message explaining that a silently-non-matching regex/moved-section would otherwise make the two checks above pass while reading nothing.

### AC12 red-before / green-after

Against today's unmodified `system-architecture.md` there is no `### Registered routers` heading and no "The engine registers N routers" sentence, so `_COUNT_HEADER_RE.search` returns `None` and `assert m` fails — the guard (specifically `test_the_scan_is_not_vacuous`, and the two drift tests via the shared parser) is **red**. It goes **green** only once T-41.2.2 adds the block in the § R2 format. The integration gate verifies this by applying T-41.2.3 without T-41.2.2 (or reverting the doc hunk) and confirming the failure, then re-running with both.

### Suite integration

Pure pytest, no fixture / golden / network. Auto-discovered by `pytest` and by `python scripts/run_all_tests.py` (AC13). No change to `run_all_tests.py`.

---

## AC traceability

| AC | Ticket | Satisfied by | Verified by |
|---|---|---|---|
| AC1 — no phantom route path in seams inventory | T-41.2.2 | § R2 — delete lines 30-98, replace with the 15-router block; no `/backtests`,`/construction`,`/strategy-lab`,`/optimizer`,`/ranking` path remains | T-41.2.3 guard (module-level) + reviewer prose read |
| AC2 — every shipped router represented | T-41.2.2 | § R2 — the 15-bullet `### Registered routers` block accounts for all 15 modules | T-41.2.3 `test_stated_module_list_matches_actual_route_modules` |
| AC3 — no phantom service file | T-41.2.2 | § R3 — "### Service layer" names only files in `app/services/`; eight removed files gone | reviewer / integration read against `ls app/services/` |
| AC4 — engine purpose matches shipped capability | T-41.2.2 | § R1 — line 14 reworded | reviewer read |
| AC5 — truth-class list carries no removed surface | T-41.2.2 | § R4 — lines 113-118: drop 3, keep 3, add persisted-imports | reviewer read |
| AC6 — Data Flow describes shipped flow only | T-41.2.2 | § Data Flow rewrite bounds — reword 275, delete 280-344 | reviewer read |
| AC7 — API Boundary stops asserting removed seams | T-41.2.2 | § R5 — edit 246, delete 248 clause + 250 | reviewer read |
| AC8 — market-data section untouched | T-41.2.2 (constraint) | § Protected fences — lines 131-239 byte-identical | `git diff` shows no hunk in 131-239 |
| AC9 — trust-semantics rule untouched | T-41.2.2 (constraint) | § Protected fences — lines 122-129 byte-identical | `git diff` |
| AC10 — accepted-tradeoff note untouched | T-41.2.2 (constraint) | § Protected fences — lines 252-265 byte-identical | `git diff` |
| AC11 — mechanical guard exists | T-41.2.3 | new `test_architecture_doc_route_inventory.py`, bidirectional drift check naming the offending entry | the test itself |
| AC12 — guard not vacuous, red-before/green-after | T-41.2.3 | `test_the_scan_is_not_vacuous` mirror; red on today's doc via `assert m` on the missing header | integration gate applies guard without doc rewrite, confirms red |
| AC13 — full suite green | T-41.2.2 + T-41.2.3 | doc + guard together | `python scripts/run_all_tests.py` |

T-41.2.1 (this plan) traces AC1-AC7 and AC11 per the story's ticket list.

---

## Lane split and dispatch order

Two implementation tickets, one dependency.

**T-41.2.2 — docs-engineer.** Rewrite `docs/architecture/system-architecture.md` per § Replacement structure and § Data Flow rewrite bounds: regions R1-R6. Leave the three protected fences byte-identical. Recommended (not AC-blocking) additional sweep of lines 24, 25, 357, 246 per the risks bullets. No other file. This is `docs/**` — squarely the docs lane; no code, no schema, no test.

**T-41.2.3 — test-engineer.** Add `services/quant-engine/app/tests/test_architecture_doc_route_inventory.py` per § Guard test design. `app/tests/**` — the test lane. No source edit.

**Dependency and order.** The guard parses the `### Registered routers` block that T-41.2.2 creates, and AC12 requires the guard red on today's doc and green only after the rewrite. Dispatch **T-41.2.2 first, then T-41.2.3**. This plan fully specifies the doc-format contract, so the test author codes to the spec, not to the finished file — concurrent dispatch is technically possible but sequential keeps `run_all_tests.py` green in one pass and lets the test author eyeball the real block.

**No quant lane.** Nothing here touches `analytics/`, a formula, a weighting, a return basis, or a trust classification. The truth-class list edit (§ R4) removes labels for deleted product surfaces and aligns the remaining labels with CLAUDE.md's four truth classes — it does not change any trust semantic or classification rule (the `verified/degraded/withheld/unavailable` bullets at 122-129 are a protected fence). No RESEARCH or AUDIT pass required.

**No frontend/backend lane.** Per the contract note: no schema, route, or response shape changes.

**Gates.** Integration (tech-lead INTEGRATION) — confirms the 15-router block matches `main.py`, the protected fences are byte-identical (`git diff`), the guard is red-before/green-after, and no removed-surface reference survives in an AC-mapped region. Reviewer — walks AC1-AC13. No quant-audit.
