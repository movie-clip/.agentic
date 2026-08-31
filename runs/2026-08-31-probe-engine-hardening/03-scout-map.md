REPORT 2026-08-31-probe-engine-hardening/03
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon; work order verification field is NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `mcp_server/` is 5 files: `__init__.py` (package docstring only) · `server.py` (5 `@server.tool()` wrappers, zero logic, `MCPServer("project")`, `server.run()` stdio) · `tools/__init__.py` (docstring) · `tools/probing.py` (`engine_module_for`, `build_snapshot_impl`, `probe_engine_impl`, helpers `_Patcher` + `_market_data`) · `tools/testing.py` (`_run`, `_tail`, `_parse_failures`, `run_tests_impl`, `check_gates_impl`, `reset_goldens_impl`, module constants). No registry module — wrappers are decorated in `server.py` directly. see § mcp_server file map
  - `_impl`/wrapper split today: every `server.py` fn is `def name(args) -> dict[str,Any]: return <module>.<name>_impl(**kwargs)` — one delegating call, no branching. Wrapper→impl pairs: `run_tests`→`testing.run_tests_impl` · `check_gates`→`testing.check_gates_impl` · `reset_goldens`→`testing.reset_goldens_impl` · `build_snapshot`→`probing.build_snapshot_impl` · `probe_engine`→`probing.probe_engine_impl`. `probe_engine` wrapper sig has 6 params (route, payload, histories, default_rows, vendor_by_symbol, engine_module); `run_tests` has 3 (scope, path, k); the other three take 0–5. server.py:30-90.
  - `probe_engine_impl` (probing.py:106-149): computes `target = engine_module or engine_module_for(route)`; `context = _market_data(target,…) if target else nullcontext()` (probing.py:130-134 — this is the F-3 live-path); runs `TestClient(app).post(route, json=payload)` inside `context`; returns dict `{status, ok, engine_module, mocked, body}` where `ok = response.status_code < 400` (probing.py:143) and `mocked = target is not None`. `body` is `response.json()` when content-type is JSON else `.text`. No trust inspection, no shape check, no truncation, no `fields`/`allow_unmocked` args. see § probing.py detail
  - `engine_module_for` (probing.py:64-77): pure string fn. `parts = [p for p in route.split("/") if p]`; if `len(parts) >= 2 and parts[0] == "engines"` → `f"app.services.{parts[1].replace('-', '_')}_engine"`, else `None`. Note it keys only on `parts[1]` (the engine name), ignores the action segment (`run` / `run-imported` / `multi` / `intra`) — so both `/engines/diagnostics/run` and `/engines/diagnostics/run-imported` derive `app.services.diagnostics_engine`.
  - market-data mock install for /engines/ routes: `_market_data` contextmanager (probing.py:44-61) builds a `_Patcher` (probing.py:20-42, an `unittest.mock`-backed adapter exposing `.patch(target,new)` + `.stop_all()` since there is no pytest `mocker` outside a session) and calls `fixtures.install_market_data_mock(patcher, engine_module, histories=, default_rows=, vendor_by_symbol=)` which does `mocker.patch(f"{engine_module}.MarketDataService", mock_svc)` (fixtures.py:189-229). `finally: patcher.stop_all()` unwinds. `TestProbeEngine.test_patches_are_unwound_after_the_probe` pins the unwind.
  - `testing._run` (testing.py:66-74): `subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, env=env)` — NO `timeout=` (F-4). Single call site inside `_run`; every tool goes through it. `run_tests_impl` call sites (testing.py:149): `full`→`[sys.executable, RUN_ALL_TESTS]` in ROOT · `backend`→`[sys.executable,-m,pytest,-q,--no-header,(path),(-k k)]` in BACKEND_DIR with `extra_env={"SKIP_GOLDEN_FRESHNESS_CHECK":"1"}` · `frontend`→`[npx, vitest, run,(path),(-t k)]` in FRONTEND_DIR · `typecheck`→`[npx, tsc, --noEmit]` in FRONTEND_DIR. `check_gates_impl` (testing.py:173-175): 3 `_run` calls — deadcode `[sys.executable, DEADCODE_SCRIPT, --strict]` in ROOT, typecheck `[npx, tsc, --noEmit]` in FRONTEND_DIR, drift `[git, status, --porcelain, --, GOLDENS_PATH]` in ROOT. `reset_goldens_impl` (testing.py:204): one `_run` `[git, checkout, --, GOLDENS_PATH]`, returns `{ok, path, stderr}` only (F-5 — no diff capture).
  - constants `tools/testing.py` imports FROM `scripts/run_all_tests.py` (testing.py:40-45): `BACKEND_DIR`, `FRONTEND_DIR`, `TEST_PASS_MARKER`, `npx_command`. Locally defined in testing.py:47-54: `GOLDENS_PATH="apps/desktop/src/test/dashboardGoldens.ts"`, `DEADCODE_SCRIPT`, `RUN_ALL_TESTS`, `VALID_SCOPES=("backend","frontend","typecheck","full")`, `MAX_FAILURES=25`, `TAIL_LINES=15`. `_repo_root()` walks up for `scripts/run_all_tests.py` (testing.py:23-33) and inserts `ROOT/scripts` on `sys.path` before the import. In run_all_tests.py: `ROOT=parents[1]`, `BACKEND_DIR=ROOT/services/quant-engine`, `FRONTEND_DIR=ROOT/apps/desktop`, `TEST_PASS_MARKER=ROOT/.claude/.last-test-pass`, `npx_command()` returns `"npx.cmd"` on nt.
  - module-docstring rule (testing.py:1-11): "Thin wrappers only. `scripts/run_all_tests.py` and `scripts/detect_deadcode.py` remain the single source of truth … nothing here restates a step list or a path." + "Return values are deliberately bounded … a failing suite must come back as parsed failures plus a short tail — never the full stdout dump."
  - 14 /engines/ POST routes, count matches run.md exactly. Shape split matches the backend-pack route-to-shape table verbatim: 7 flat / 5 snapshot-wrapped / 2 bare-snapshot. see § engine-route request-model landscape
  - request-model recovery at runtime: every one of the 14 routes has exactly ONE body param, so `route.body_field.type_` on the FastAPI `APIRoute` gives the bound Pydantic model class directly (`app.routes` → filter `isinstance(r, APIRoute)` → match `r.path` + `"POST" in r.methods` → `r.body_field.type_`; `r.dependant.body_params` is the alternative). Shape is then derived from the model: subclass of `PortfolioEngineRequest` → flat; is `ImportedPortfolioSnapshot` → bare-snapshot; has field `snapshot: ImportedPortfolioSnapshot` → snapshot-wrapped; else unclassified. I could not execute this (no Bash) — attribute path is standard FastAPI 0.119 / Starlette 0.48. see § runtime request-model recovery
  - `test_mcp_tools.py` has 4 classes today, NOT the set the story lists: `TestEngineModuleDerivation`, `TestBuildSnapshot`, `TestProbeEngine`, `TestRunTestsParsing`, `TestGates` — that is 5; there is NO `TestProbeEngineShape`/trust class and NO tool-registration test anywhere in the file. see § test_mcp_tools.py structure
  - the "five-tool registration check" the story references (US-43.1 test plan, AC-F3.4 mention) DOES NOT EXIST in `test_mcp_tools.py` or any other test file — DESIGN must decide whether to add one or drop the reference.
  - `pytest.ini` (whole file, 13 lines): `addopts = --disable-socket --allow-hosts=127.0.0.1,::1 --allow-unix-socket -m "not live_data"`. Loopback stays allowed because in-process `TestClient` uses 127.0.0.1 socketpairs; external hosts (FMP, Yahoo) blocked. This guard does NOT cover `probe_engine_impl` (runs outside a pytest session — probing.py:116-118 docstring says so).
  - `requirements-dev.txt` pins: `mcp>=2.0` (line 16). starlette trap comment (lines 17-24), verbatim: "WARNING: `pip install mcp` pulls sse-starlette, which wants starlette>=0.49.1, while requirements.txt pins starlette==0.48.0 (FastAPI 0.119.1 raises \"Router.__init__() got an unexpected keyword argument 'on_startup'\" on newer starlette, which breaks collection of EVERY backend test). Keep starlette on its pin and ignore the resulting `pip check` complaint: sse_starlette IS imported when the server starts, but it works against 0.48.0 anyway … Verified: app/mcp_server/server.py registers all five tools on starlette 0.48.0." Also `ruff==0.15.17`, `vulture==2.16`, `pip-audit==2.10.1`.

risks:
  - The existing `TestProbeEngine.test_drawdown_route_returns_a_response_with_mocked_market_data` (test_mcp_tools.py:95-114) sends `{"snapshot": build_snapshot_impl(...)}` to `/engines/drawdown/run`, which is a FLAT route — the test itself sends a mismatched shape and its own comment concedes "The route may reject the payload shape". F-1's shape-mismatch warning would fire on this existing test; DESIGN/build must expect to update it, not just add cases.
  - `build_snapshot_impl` shorthand-vs-full: `probe_engine` callers for flat routes must splat the snapshot at top level (`{**snap, "benchmark_symbol": ...}`) per backend.md:162; for wrapped routes it goes under `"snapshot"`. The two `run-imported` routes take the snapshot as the whole body. Any shape-classifier that keys on route path alone (not the resolved model) will misclassify `/engines/diagnostics/run` vs `/engines/diagnostics/run-imported` because `engine_module_for` already collapses them.
  - `engine_module_for` returns non-None for ANY path whose second segment follows `engines` — including a typo like `/engines/drawdon/run` → `app.services.drawdon_engine`, which then fails at import inside `install_market_data_mock`. run.md F-3 wants "typo'd engine name failing loudly" preserved; that loud failure currently comes from the `mocker.patch(f"{target_module}.MarketDataService", …)` raising `ModuleNotFoundError`, not from any explicit check in probing.py.
  - Non-/engines/ POST routes that a caller could aim `probe_engine` at with `allow_unmocked`: `/portfolios/import/interactive-brokers` (+ `/analyze`, `/analyze-upload`, `/analyze-snapshot`), `/portfolios/import/combine-snapshots`, `/cache/clear`. GET-only groups: `/health`, `/market-data/quote-short`, `/market-data/historical-price-light`, `/cache/stats`. `engine_module_for` returns `None` for all of these (pinned by `TestEngineModuleDerivation.test_non_engine_routes_derive_nothing`).
  - I did not run the FastAPI introspection to confirm `route.body_field.type_` resolves to the un-wrapped model for the single-param endpoints; this is the documented FastAPI behaviour for one body param without `embed=True`, but the `*_engine/run-imported` endpoints declare the param name `snapshot` (not `request`), which does not change embedding but is worth a DESIGN spot-check.
  - `check_gates_impl`'s `_run` signature is `_run(command, cwd, extra_env=None)` and `TestGates.test_check_gates_flags_goldens_drift` monkeypatches a `fake_run(command, cwd, extra_env=None)` — any F-4 change to `_run`'s signature (e.g. adding a `timeout`/`scope` positional) breaks that test's stub and `TestRunTestsParsing`'s `run.call_args[0][2]` positional assertions (test_mcp_tools.py:195, 204).

## Orchestrator brief

- Read-only recon for the tech-lead DESIGN pass on F-1..F-5. No code touched. Verification field was NONE.
- The `_impl`/thin-wrapper split, the `mcp_server/` inventory, and every constant/subprocess call site are mapped with `file:line` anchors in the `handoff` bullets and the four detail sections below.
- Engine-route landscape confirmed: **14** /engines/ POST routes, **7 flat / 5 snapshot-wrapped / 2 bare-snapshot**, matching run.md's "14" and the backend-pack route-to-shape table exactly. Full table in § engine-route request-model landscape.
- Concrete runtime request-model recovery path found (`APIRoute.body_field.type_`); not executed (no Bash). § runtime request-model recovery.
- Two facts that contradict the approved story text, flagged for DESIGN: (1) there is **no** tool-registration test today; (2) the current `TestProbeEngine` drawdown test already sends a mismatched shape and will trip an F-1 warning. Both in `risks`.
- Sections below, all pure reference (no verdicts): § mcp_server file map · § probing.py detail · § testing.py detail · § engine-route request-model landscape · § runtime request-model recovery · § test_mcp_tools.py structure.

---

## mcp_server file map

| file | contents |
| --- | --- |
| `app/mcp_server/__init__.py` | Package docstring only. Rationale: lives under `app/` so ruff/vulture/pytest already reach it; named `mcp_server` to disambiguate from the `mcp` SDK. |
| `app/mcp_server/server.py` (95 lines) | `from mcp.server.mcpserver import MCPServer`; `server = MCPServer("project")`; five `@server.tool()` wrappers (`run_tests`, `check_gates`, `reset_goldens`, `build_snapshot`, `probe_engine`), each a single `return <module>.<name>_impl(...)`; `if __name__ == "__main__": server.run()` (stdio). Docstring: 2-line cap on tool docstrings is stated here (server.py:8-9). No logic, no branching, no imports beyond `probing`/`testing`/`MCPServer`/`typing`. |
| `app/mcp_server/tools/__init__.py` | Docstring only: "Every public function here is a plain `*_impl` callable with no MCP dependency". |
| `app/mcp_server/tools/probing.py` (149 lines) | `_Patcher` class (20-42); `_market_data` contextmanager (44-61); `engine_module_for` (64-77); `build_snapshot_impl` (80-103); `probe_engine_impl` (106-149). Imports `imported_snapshot, install_market_data_mock, position` from `app.tests.fixtures`. |
| `app/mcp_server/tools/testing.py` (209 lines) | `_repo_root` (23-33); module constants (36-63); `_run` (66-74); `_tail` (77-78); `_parse_failures` (81-108); `run_tests_impl` (111-164); `check_gates_impl` (167-199); `reset_goldens_impl` (202-209). Three regexes: `_PYTEST_FAILURE`, `_TSC_ERROR`, `_VITEST_FAILURE`. |

Registration: tools are registered purely by the `@server.tool()` decorator in `server.py`; there is no separate registry/manifest module and no `.mcp.json` in-repo edit needed (the `project` key lives in the agent network's `.mcp.json`, per the server.py:23-26 comment).

## probing.py detail

- `engine_module_for(route: str) -> str | None` — probing.py:64-77. Split on `/`, drop empties; if `parts[0] == "engines"` and `len(parts) >= 2` return `f"app.services.{parts[1].replace('-', '_')}_engine"`; else `None`. Keys only on the engine-name segment; action segment ignored. Docstring claims "Derived rather than table-driven so a new engine works without touching this file."
- `build_snapshot_impl(positions, instruments, cash_balances, ledger_entries, statement_overrides) -> dict` — probing.py:80-103. Each `positions` entry carrying a `symbol` key is routed through `fixtures.position(**entry)` (defaults fill the rest); everything else passed straight to `fixtures.imported_snapshot(...)`. Pure delegation to fixtures; no validation (a garbage position dict passes through and only fails at `model_validate`, pinned by `TestBuildSnapshot.test_invalid_position_still_fails_validation`).
- `probe_engine_impl(route, payload, histories=None, default_rows=None, vendor_by_symbol=None, engine_module=None) -> dict` — probing.py:106-149.
  - `target = engine_module or engine_module_for(route)` (line 129).
  - `context = _market_data(target, histories, default_rows, vendor_by_symbol) if target else nullcontext()` (lines 130-134). **`nullcontext()` is the F-3 live/unmocked path** — reached whenever `target` is falsy, i.e. non-/engines/ route AND no explicit `engine_module`.
  - `with context: with TestClient(app) as client: response = client.post(route, json=payload)` (136-138). `app` imported from `app.api.main` inside the fn.
  - Return dict keys: `status` (int), `ok` (`response.status_code < 400` — line 143, **the F-1 defect: no trust / shape inspection**), `engine_module` (= `target`, may be `None`), `mocked` (`target is not None`), `body` (`response.json()` if content-type starts `application/json` else `response.text`). **No truncation anywhere — F-2 defect.**
- `_Patcher` (probing.py:20-42) — `.patch(target, new)` does `mock.patch(target, new).start()` and stashes; `.stop_all()` stops in reverse. Exists because `install_market_data_mock` expects a pytest-mock `mocker` and there is none outside a session.
- `_market_data` (probing.py:44-61) — contextmanager: build `_Patcher`, `yield install_market_data_mock(patcher, engine_module, histories=, default_rows=, vendor_by_symbol=)`, `finally: patcher.stop_all()`.
- market-data mock target: `fixtures.install_market_data_mock` (fixtures.py:189-229) does `mocker.patch(f"{target_module}.MarketDataService", mock_svc)` — patches the name as imported into the **engine module**, and stubs `get_historical_prices` / `get_historical_prices_for_symbols` / `last_fetch_meta`. A bad `target_module` raises `ModuleNotFoundError` here (this is the current "fail loudly on typo" behaviour — implicit, not an explicit guard).

## testing.py detail

- `_run(command: list[str], cwd: Path, extra_env: dict|None=None) -> subprocess.CompletedProcess` — testing.py:66-74. `env = dict(os.environ)`, update with `extra_env`, `subprocess.run(command, cwd=str(cwd), capture_output=True, text=True, env=env)`. **No `timeout=` — the single F-4 site.** Every tool subprocess goes through here.
- `_tail(text, n=TAIL_LINES=15) -> list[str]` — non-blank lines, last `n`.
- `_parse_failures(scope, output) -> list[dict]` — testing.py:81-108. `backend`/`full` → `_PYTEST_FAILURE` regex → `{file, test, message}`; `typecheck` → `_TSC_ERROR` → `{file, line, column, message}`; `frontend` → `_VITEST_FAILURE` → `{file, test, message:""}`; else `[]`. Capped at `MAX_FAILURES=25`.
- `run_tests_impl(scope="backend", path=None, k=None) -> dict` — testing.py:111-164. `scope` lowered; unknown scope returns `{ok:False, scope, error:"unknown scope: …", valid_scopes:list(VALID_SCOPES)}` WITHOUT running (pinned by `TestRunTestsParsing.test_rejects_an_unknown_scope…`). Command per scope: see § mcp_server / handoff bullet. `backend` sets `extra_env={"SKIP_GOLDEN_FRESHNESS_CHECK":"1"}`; `full` passes `extra_env=None` (pinned at test_mcp_tools.py:195 / 204 via `run.call_args[0][2]`). Result dict: `{ok(=returncode==0), scope, command(joined str), cwd, exit_code, failure_count, failures, failures_truncated(len==MAX_FAILURES), tail}`.
- `check_gates_impl() -> dict` — testing.py:167-199. Three `_run` calls (deadcode `--strict` in ROOT; `tsc --noEmit` in FRONTEND_DIR; `git status --porcelain -- GOLDENS_PATH` in ROOT). Returns `{deadcode:{ok,tail}, typecheck:{ok,errors}, goldens_drifted:bool(drift.stdout.strip()), commit_gate:{marker_present, marker_path, note}}`. `TestGates` pins the key set `{deadcode, typecheck, goldens_drifted, commit_gate}`.
- `reset_goldens_impl() -> dict` — testing.py:202-209. One `_run(["git","checkout","--",GOLDENS_PATH], ROOT)`; returns `{ok, path:GOLDENS_PATH, stderr:completed.stderr.strip()}`. **No `git diff --stat` / diff capture before the checkout — the F-5 defect.** `TestGates.test_reset_goldens_checks_out_the_generated_file` pins the exact command list.
- Constants: imported from `run_all_tests` → `BACKEND_DIR, FRONTEND_DIR, TEST_PASS_MARKER, npx_command` (testing.py:40-45). Local: `GOLDENS_PATH`, `DEADCODE_SCRIPT`, `RUN_ALL_TESTS`, `VALID_SCOPES`, `MAX_FAILURES=25`, `TAIL_LINES=15` (testing.py:47-54).
- Module docstring rule (testing.py:1-11): thin wrappers only; `scripts/run_all_tests.py` + `scripts/detect_deadcode.py` are the single source of truth for step lists and paths — "nothing here restates a step list or a path"; path constants are IMPORTED. Return values "deliberately bounded" — failing suite comes back as "parsed failures plus a short tail -- never the full stdout dump".

## engine-route request-model landscape

All are `@router.post`. Route file → path → bound request model → shape:

| # | path | request model | shape | model base / key |
| --- | --- | --- | --- | --- |
| 1 | `/engines/stress/run` | `StressEngineRequest` | flat | `PortfolioEngineRequest` subclass, no new fields |
| 2 | `/engines/exposure/run` | `ExposureEngineRequest` | flat | `PortfolioEngineRequest` subclass, `pass` |
| 3 | `/engines/drawdown/run` | `DrawdownEngineRequest` | flat | + `window_trading_days: DrawdownWindow|None` |
| 4 | `/engines/distribution/run` | `DistributionEngineRequest` | flat | + `window_trading_days: DistributionWindow=252` |
| 5 | `/engines/drift/run` | `DriftEngineRequest` | flat | `PortfolioEngineRequest` subclass, `pass` |
| 6 | `/engines/dashboard-history/run` | `DashboardHistoryEngineRequest` | flat | + `history_context: PortfolioHistoryContext|None` |
| 7 | `/engines/diagnostics/run` | `DiagnosticsEngineRequest` | flat | + `history_context: PortfolioHistoryContext|None` |
| 8 | `/engines/provenance/run` | `ProvenanceRequest` | snapshot-wrapped | `BaseModel`, `snapshot` + `lookback_days=30` |
| 9 | `/engines/correlation/multi` | `MultiBenchmarkCorrelationRequest` | snapshot-wrapped | `BaseModel`, `snapshot` + `lookback_days=252` |
| 10 | `/engines/correlation/intra` | `IntraCorrelationRequest` | snapshot-wrapped | `BaseModel`, `snapshot` + `lookback_days=60` + `max_holdings=15` |
| 11 | `/engines/attribution/run` | `FactorAttributionRequest` | snapshot-wrapped | `BaseModel`, `snapshot` + `window=60` + `benchmark_symbol` |
| 12 | `/engines/currency-risk/run` | `CurrencyRiskRequest` | snapshot-wrapped | `BaseModel`, `snapshot` + `window=60`; docstring explicitly says "Snapshot-wrapped, like the sibling Exposure engines … NOT the flat `PortfolioEngineRequest` shape" |
| 13 | `/engines/dashboard-history/run-imported` | `ImportedPortfolioSnapshot` | bare-snapshot | endpoint param `snapshot: ImportedPortfolioSnapshot` — whole body IS the snapshot |
| 14 | `/engines/diagnostics/run-imported` | `ImportedPortfolioSnapshot` | bare-snapshot | same |

Totals: 7 flat, 5 snapshot-wrapped, 2 bare-snapshot = **14**. Matches run.md "14 engine routes" and the backend-pack route-to-shape table (`capabilities/backend.md:156-160`) exactly.

`PortfolioEngineRequest` (schemas/portfolio_engine.py:56-72): flat fields `benchmark_symbol, base_currency, statement_period, imported_at, importer, source_file_names, positions, cash_balances, fx_rates` — every one has a default, so a wrong-shaped body is *accepted* (0 positions → fail-closed → `trust:"unavailable"`), which is the F-1 hazard.

Non-/engines/ route groups where `engine_module_for` returns `None` (`schemas` in parens):
- `/health` — GET, no body (health.py).
- `/portfolios/import/*` (imports.py): `POST /interactive-brokers` + `/interactive-brokers/analyze` + `/interactive-brokers/analyze-snapshot` (`InteractiveBrokersImportRequest` / `SnapshotAnalysisRequest`), `/interactive-brokers/analyze-upload` (multipart), `POST /combine-snapshots` (`CombineImportedSnapshotsRequest`).
- `/market-data/quote-short`, `/market-data/historical-price-light` — GET (market_data.py).
- `/cache/stats` — GET; `/cache/clear` — POST `CacheClearRequest | None` (cache.py).
`TestEngineModuleDerivation.test_non_engine_routes_derive_nothing` pins `["/portfolios/import", "/cache/clear", "/market-data/history", "/health"]` → `None`.

## runtime request-model recovery

The review's "report matched request-model name" is recoverable from the live app without a hand table:

- `from app.api.main import app` (already imported inside `probe_engine_impl`).
- `from fastapi.routing import APIRoute`; iterate `app.routes`, keep `r` where `isinstance(r, APIRoute)`, `r.path == route` (or `.path_format`), and the method matches `r.methods`.
- `r.body_field` is the FastAPI `ModelField` for the request body; `r.body_field.type_` (Pydantic v2: `r.body_field.field_info.annotation` may also apply) is the **model class** — for all 14 routes there is exactly one body param and no `embed=True`, so `type_` is the un-synthesised model (`StressEngineRequest`, `ProvenanceRequest`, `ImportedPortfolioSnapshot`, …). `r.dependant.body_params` is the list-form alternative.
- Shape from the model class (no route-string parsing — avoids the `run` vs `run-imported` collapse in `engine_module_for`):
  - `issubclass(model, PortfolioEngineRequest)` → **flat**
  - `model is ImportedPortfolioSnapshot` → **bare-snapshot**
  - `"snapshot" in model.model_fields and model.model_fields["snapshot"].annotation is ImportedPortfolioSnapshot` → **snapshot-wrapped**
  - else → **unclassified** (disclose, do not guess — AC-F1.3)
- Not executed here (scout has no Bash). Attribute names are FastAPI 0.119.1 / Starlette 0.48.0 (the pinned versions per `requirements-dev.txt`); `body_field` has been stable since FastAPI 0.9x. DESIGN should confirm `body_field.type_` vs `.field_info.annotation` on the pinned Pydantic v2.

## test_mcp_tools.py structure

Module docstring: tests call `*_impl` directly, no transport; "The one thing these tests cannot cover is whether the server actually starts and handshakes. That is a human check." Imports: `probing, testing` from `app.mcp_server.tools`; `ImportedPortfolioSnapshot` from `app.schemas.imports`; `price_rows_from_returns` from `app.tests.fixtures`.

| class | covers | fixtures / mocks |
| --- | --- | --- |
| `TestEngineModuleDerivation` (24-62) | `engine_module_for` for 11 engine routes incl. hyphen→underscore (`currency-risk`, `dashboard-history`); 4 non-engine routes → `None`; every derived module is importable via `importlib` | none — pure fn |
| `TestBuildSnapshot` (65-91) | empty snapshot validates; position shorthand; `statement_overrides` reaches payload and doesn't drop siblings; invalid position still fails `model_validate` | none — calls `build_snapshot_impl` + `ImportedPortfolioSnapshot.model_validate` |
| `TestProbeEngine` (94-133) | drawdown route returns a real HTTP response with mocked market data (asserts `engine_module`, `mocked is True`, `status` is int, `body` not None — **sends `{"snapshot": …}` to a FLAT route**, comment concedes the shape may be rejected); patches unwound after probe; explicit `engine_module` overrides derivation (probes `/health` with `engine_module="app.services.drawdown_engine"`) | `build_snapshot_impl`, `price_rows_from_returns`; real in-process `TestClient` via `probe_engine_impl` |
| `TestRunTestsParsing` (136-204) | unknown scope rejected w/o running; pytest FAILED/ERROR parse; tsc error+position parse; failure list capped at `MAX_FAILURES`; `_tail` bounded + drops blanks; `backend` scope passes `SKIP_GOLDEN_FRESHNESS_CHECK=1` and appends `-k`/path; `full` scope passes `extra_env` None | `mocker.patch.object(testing, "_run", …)` returning a fake `CompletedProcess`; asserts on `run.call_args[0][…]` positionals |
| `TestGates` (207-241) | `check_gates_impl` reports all four gate keys; flags goldens drift when `git status` output non-empty; `reset_goldens_impl` runs exactly `["git","checkout","--",GOLDENS_PATH]` and returns `ok` | `mocker.patch.object(testing, "_run", …)`; one test uses a `fake_run(command, cwd, extra_env=None)` side_effect keyed on `command[0]=="git"` |

Not present: any `TestProbeEngineShape` / trust-gating class, any `probe_engine` truncation test, any `allow_unmocked` test, and **any tool-registration / "five tools" test** (searched the whole file — absent).
