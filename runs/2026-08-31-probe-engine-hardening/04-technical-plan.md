REPORT 2026-08-31-probe-engine-hardening/04
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    design pass, read-only; work order verification field is NONE. FastAPI introspection path spot-checked against the pinned stack (fastapi 0.119.1 / starlette 0.48.0 / pydantic 2.12.3) via a throwaway python -c, no repo file touched.

contract_notes:
  - .agentic backend.md:166 ("The response is not truncated") and quant.md:166-169 go stale once T-43.1.2 lands — docs lane must flip them to "bounded head/tail, original count preserved" at close-out (T-43.1.5). see § 8
  - .agentic testing.md:154-156 ("does not validate the payload shape") goes stale once T-43.1.1 lands — reword to "classifies the expected shape and warns on a top-level `snapshot`-key mismatch; still does not 422". see § 8
  - No repo doc (`docs/contracts/`, `docs/finance/`) is in scope — the tool reports engine trust strings verbatim, it defines no contract field. Confirmed with owner decision in run.md (tech-debt-register + capability packs only).

pack_corrections:
  - none

handoff:
  - TECHNICAL PLAN follows; full detail in the named sections, this block is the index.
  - contract: `probe_engine_impl` return envelope — 9 new keys, `ok` meaning narrowed, `body` content may be bounded/filtered, all existing keys retained. see § 1
  - contract: refusal return (non-derivable route, `allow_unmocked=False`) is a structured dict with `refused: True`, NOT a raise. see § 1 + § 4
  - reuse: shape + model name come from `APIRoute.body_field.type_` on the live app — no hand table; predicate chain verified across all 14 routes (7 flat / 5 wrapped / 2 bare). see § 2
  - decision: `fields=` filters top-level body keys only, no dotted paths; trust keys always retained; filter runs before array truncation. see § 3
  - decision: any typo (route segment OR explicit `engine_module`) still raises `ModuleNotFoundError` loudly; structured refusal is only for legitimately non-derivable routes. see § 4
  - decision: F-2 truncation replaces an over-long array's middle with one `{"__probe_truncated__": {...}}` sentinel, array stays an array, order preserved, recurses the whole body. see § 5
  - decision: `_run` gains `*, timeout=None` (keyword-only) so `run.call_args[0][2]` positional `extra_env` assertions survive; `_run` raises `TimeoutExpired`, the `_impl` fns catch and structure it. see § 6
  - decision: per-scope timeout budgets are a local `TIMEOUTS` dict in tools/testing.py (seconds); not imported, not a step-list run_all_tests.py owns. see § 6
  - decision: `reset_goldens_impl` runs `git diff --stat` then bounded `git diff` then `git checkout`, in that order; capture survives a checkout failure. see § 7
  - decision: strike the "five-tool registration check" from the ACs/test plan — it never existed and testing it means importing the mcp SDK the constraints ringfence. see § 8
  - decision: existing `test_drawdown_route_returns_a_response_with_mocked_market_data` sends a mismatched shape — test lane repoints it to the correct flat payload and adds a dedicated mismatch-warning case. see § 8
  - verdict: F-1 stays ONE ticket (T-43.1.1). US-43.1 ticket list unchanged: T-43.1.1..T-43.1.5. see § 9
  - lane split: backend WO-A (probing.py + 2-line server.py sig) ∥ backend WO-C (testing.py); then ONE test WO-E (both stories, same test file); then gates; then docs close-out. see § 10
  - reuse map: `engine_module_for`, `_market_data`, `_Patcher`, `install_market_data_mock`, `_run`, `_tail`, `_parse_failures`, imported run_all_tests constants, `build_snapshot_impl`, `price_rows_from_returns`. see § 11
  - guardrails 1-5: none engaged; quant-audit stays SKIPPED — the tool passes engine trust strings through, it computes/classifies nothing. see § 12

risks:
  - `request_shape`/`request_model` recovery depends on `APIRoute.body_field.type_`. Verified on the pinned stack for all 14 routes this pass, but it is FastAPI-internal — if a future FastAPI bump changes it, the fallback is `route.dependant.body_params[0].type_`, and failing that `request_model: None` + `request_shape: "unclassified"` (never guess). Build lane must keep that three-step fallback.
  - Supplied-payload shape is detected only on presence/absence of a top-level `"snapshot"` key; flat vs bare-snapshot is not disambiguated on the supplied side. Acceptable: both put snapshot fields at top level and flat's extra keys all default, so they never mis-warn against each other.
  - A caller who nests the body under a differently-named key gets `shape_mismatch: null` and no warning — a known gap in the § 2c heuristic, not a defect. Full model validation cannot close it because the F-1 hazard is that the wrong shape still validates on defaults.
  - Depth-1 trust scan: only top-level `trust` / `*_trust` keys downgrade `ok`. Per-episode / per-scenario nested trust (drawdown decomposition, stress per-scenario) does NOT downgrade. This matches "the engine answered nothing" but a reviewer expecting nested-trust gating will read it as under-strict — AC-F1.4 only names the body-level trust, so this is in-spec.
  - Timeout budgets (full 1800s / backend 600 / frontend 600 / typecheck 300 / gate 300 / git 30) are first-pass numbers. If CI's own full-suite wallclock is known to exceed 1800s the build lane should raise `full` rather than let a healthy run trip the ceiling. Flagged for the build lane to sanity-check against a real `run_all_tests.py` duration.
  - `check_gates_impl` gains a top-level `timeouts` key, so `TestGates.test_check_gates_reports_every_gate`'s exhaustive `set(result) == {...}` assertion WILL fail until the test lane updates it. Named in § 8 as a required test edit, not an incidental one.
  - `_run` raising `TimeoutExpired` rather than returning a sentinel means `check_gates_impl` must wrap each of its three `_run` calls individually (not one try around all three) to satisfy AC-F4.5 "still returns results for the gates that completed". Called out in § 6; a single outer try/except would silently regress that AC.

## Orchestrator brief

- Design pass for US-43.1 (probe_engine, F-1/F-2/F-3) and US-43.2 (suite-runner tools, F-4/F-5). Backend + test lanes only; no schema, no frontend, no quant, no repo docs.
- Decision: F-1 stays ONE ticket. US-43.1 ticket list unchanged (T-43.1.1..T-43.1.5); US-43.2 unchanged (T-43.2.1..T-43.2.4).
- Decision: shape + request-model name come from live-app FastAPI introspection (`APIRoute.body_field.type_`), verified across all 14 routes — no hand-maintained table; AC-F1.1 stands as written, not softened.
- Decision: `fields=` = top-level keys only; `allow_unmocked` default-refusal is a structured return; typos still raise loudly; truncation = one sentinel dict mid-array.
- Decision: `_run` gains keyword-only `timeout`; budgets are a local `TIMEOUTS` dict; `reset_goldens` captures diff-stat + bounded diff before checkout.
- Decision: strike the non-existent "five-tool registration check" reference; test lane repoints the mismatched-shape drawdown test and updates `TestGates` exhaustive key-set assertion.
- Lane split (Section 10): WO-A backend probing.py ∥ WO-C backend testing.py → WO-E single test WO (both stories, one shared test file) → integration → review → docs close-out (T-43.1.5 + T-43.2.4) → human runs full suite + commits.
- Sections: 1. probe_engine_impl return envelope · 2 shape classification mechanism F-1 · 3 fields F-2 · 4 allow_unmocked F-3 · 5 F-2 truncation marker · 6 F-4 run timeout · 7 F-5 reset_goldens · 8. Test-reference reconciliation · 9 F-1 verdict and tickets · 10. Lane split and dispatch order · 11. Reuse map · 12. Guardrails and quant-audit.
- Blocks dispatch: none.

---

# TECHNICAL PLAN

## 1. probe_engine_impl return envelope

Both build lanes and the test lane read this section. `probe_engine_impl` keeps
its positional signature and gains two trailing keyword args:

```python
def probe_engine_impl(
    route, payload,
    histories=None, default_rows=None, vendor_by_symbol=None, engine_module=None,
    fields: list[str] | None = None,          # NEW  (F-2)
    allow_unmocked: bool = False,             # NEW  (F-3)
) -> dict[str, Any]:
```

`server.py`'s `probe_engine` wrapper gains the same two params in its signature
and passes them through in the one delegating call. Docstring stays 2 lines. No
other wrapper change.

### 1a. Engine-route probe (route resolved, mock installed) — full return dict

| key | type | status | meaning |
|---|---|---|---|
| `status` | `int` | unchanged | HTTP status code |
| `ok` | `bool` | **meaning narrowed** | `status < 400` **AND** not trust-downgraded **AND** not refused. Was `status < 400` alone. |
| `engine_module` | `str \| None` | unchanged | module whose `MarketDataService` was patched (`= target`) |
| `mocked` | `bool` | unchanged | `True` when a market-data mock was installed |
| `unmocked` | `bool` | **NEW** | `True` only when the route ran with no mock via `allow_unmocked=True`. `False` otherwise. |
| `refused` | `bool` | **NEW** | `False` here. `True` only in the 1b refusal return. |
| `request_shape` | `"flat" \| "snapshot-wrapped" \| "bare-snapshot" \| "unclassified"` | **NEW** | shape the route's bound request model implies (§ 2). `"unclassified"` when no `APIRoute` matches or the model matches no predicate. |
| `request_model` | `str \| None` | **NEW** | bound model class name, e.g. `"DrawdownEngineRequest"`. `None` when unresolved/unclassified. |
| `shape_mismatch` | `None \| {expected, supplied, note}` | **NEW** | `None` when the supplied payload shape is consistent with `request_shape` or cannot be determined. Otherwise names `expected` (= `request_shape`), `supplied` (`"snapshot-wrapped"` or `"flat-or-bare"`), and a one-line `note`. A mismatch **warns only** — the probe still POSTs and returns the real response. |
| `ok_downgraded_by` | `None \| {"<trust-key>": "unavailable"}` | **NEW** | populated when a top-level `trust` / `*_trust` key held `"unavailable"`; that is what set `ok=False` despite `status < 400`. |
| `truncation` | `list[str]` | **NEW** | dotted paths of every array the tool bounded (§ 5). `[]` when nothing was truncated. |
| `fields_kept` | `list[str] \| None` | **NEW** | present (non-null) only when `fields=` was supplied: the top-level keys retained. |
| `fields_omitted_count` | `int \| None` | **NEW** | count of top-level body keys dropped by `fields=`. `None` when `fields=` not supplied. |
| `body` | `dict \| list \| str \| None` | **content may change** | the route's JSON body, with arrays bounded (§ 5) and, if `fields=` given, filtered (§ 3). Non-JSON responses still return `.text` unchanged. |

Nothing is removed. `status`, `engine_module`, `mocked`, `body` keep their
identity; only `ok` changes semantics and only `body` changes content.

### 1b. Refusal return (non-derivable route, `allow_unmocked=False`)

A **structured dict, not a raise**:

```python
{
  "status": None, "ok": False,
  "engine_module": None, "mocked": False, "unmocked": False,
  "refused": True,
  "reason": ("route '<route>' has no derivable engine module and would run live "
             "against real market data; pass allow_unmocked=True to run it "
             "without a market-data mock"),
  "request_shape": "unclassified", "request_model": None,
  "shape_mismatch": None, "ok_downgraded_by": None,
  "truncation": [], "fields_kept": None, "fields_omitted_count": None,
  "body": None,
}
```

`reason` MUST contain the literal string `allow_unmocked`.

### 1c. Unmocked run (`allow_unmocked=True`, non-derivable route)

As 1a but `mocked=False`, `unmocked=True`, `engine_module=None`,
`request_shape="unclassified"` (no engine model to classify), `refused=False`,
no `reason` key. `unmocked: True` is the AC-F3.2 disclosure.

### 1d. Trust-downgrade rule (F-1, AC-F1.4 / F1.5)

Scan **top-level body keys only** (depth 1). If any key is exactly `trust` or
ends in `_trust` and its value is the string `"unavailable"`:
- set `ok = False`
- set `ok_downgraded_by = {"<that key>": "unavailable"}` (first such key wins;
  include all if more than one).

`verified`, `degraded`, `withheld`, `synthetic` and any nested per-row trust do
**not** downgrade `ok` — AC-F1.5. This covers the real wrapper keys: plain
`trust` (drawdown / stress / drift / distribution / correlation / intra) and
`portfolio_return_trust` (dashboard-history) via the `*_trust` suffix.

## 2. Shape classification mechanism (F-1)

**Verified this pass** against fastapi 0.119.1 / starlette 0.48.0 / pydantic
2.12.3: `APIRoute.body_field.type_` returns the un-wrapped bound model class for
every one of the 14 engine routes (each has exactly one body param, no
`embed=True`).

### 2a. Recover the model

```python
from fastapi.routing import APIRoute
from app.api.main import app   # already imported in probe_engine_impl

def _request_model_for(route: str):
    for r in app.routes:
        if isinstance(r, APIRoute) and r.path == route and "POST" in r.methods:
            bf = getattr(r, "body_field", None)
            if bf is None:
                return None
            # primary; fallbacks in order:
            return (getattr(bf, "type_", None)
                    or getattr(getattr(bf, "field_info", None), "annotation", None)
                    or (r.dependant.body_params[0].type_ if r.dependant.body_params else None))
    return None            # no route match -> caller treats as unclassified
```

No `APIRoute` match (unknown/misspelled route, or a GET-only path) → `None` →
`request_shape="unclassified"`, `request_model=None`, no mismatch check, probe
still POSTs (expect 404/405).

### 2b. Model → shape

```python
import inspect
from app.schemas.portfolio_engine import PortfolioEngineRequest
from app.schemas.imports import ImportedPortfolioSnapshot

def _shape_of(model) -> str:
    if inspect.isclass(model):
        if issubclass(model, PortfolioEngineRequest):
            return "flat"
        if model is ImportedPortfolioSnapshot:
            return "bare-snapshot"
        f = getattr(model, "model_fields", {}).get("snapshot")
        if f is not None and f.annotation is ImportedPortfolioSnapshot:
            return "snapshot-wrapped"
    return "unclassified"
```

Verified output across all 14 routes: **7 flat** (stress, exposure, drawdown,
distribution, drift, dashboard-history/run, diagnostics/run), **5
snapshot-wrapped** (provenance, correlation/multi, correlation/intra,
attribution, currency-risk), **2 bare-snapshot** (dashboard-history/run-imported,
diagnostics/run-imported). Matches backend.md:156-160 exactly.

This is why `/engines/<x>/run` vs `/run-imported` disambiguate correctly:
classification keys on the **model** (`DiagnosticsEngineRequest` vs
`ImportedPortfolioSnapshot`), never on the route string — so
`engine_module_for`'s collapse of the action segment is irrelevant here. Note
`engine_module_for` is still used unchanged for *which module to patch*; the new
introspection is a parallel lookup for *shape reporting only*.

### 2c. Supplied-shape check → `shape_mismatch`

Structural, keyed on one thing: does `payload` (a dict) have a top-level
`"snapshot"` key?

| `request_shape` | payload has top-level `"snapshot"` | verdict |
|---|---|---|
| `flat` | yes | mismatch — `supplied: "snapshot-wrapped"` |
| `bare-snapshot` | yes | mismatch — `supplied: "snapshot-wrapped"` |
| `snapshot-wrapped` | no | mismatch — `supplied: "flat-or-bare"` |
| any | consistent with above | `shape_mismatch = None` |
| `unclassified` | — | `shape_mismatch = None` (nothing to compare) |
| `payload` not a dict | — | `shape_mismatch = None` |

`note` examples: `"payload has a top-level 'snapshot' key but the route expects
a flat body"` / `"route expects the body wrapped under 'snapshot' but the
payload has snapshot fields at the top level"`.

Flat vs bare-snapshot is deliberately **not** disambiguated on the supplied
side (both are top-level snapshot fields, mutually payload-compatible). A
full `model.model_validate(payload)` is NOT used to gate — the F-1 hazard is
precisely that the wrong shape still validates on defaults. `model_validate`
may optionally be run and its `ValidationError` string folded into `note`, but
it must never raise out of the tool and never set `shape_mismatch` on its own.

## 3. `fields=` semantics (F-2)

- `fields: list[str] | None`. **Top-level body keys only. No dotted paths, no
  nested selection.** Rationale: interpretable, non-brittle, and the envelope
  the caller needs ("stay interpretable") is a small fixed set.
- When `fields` is supplied and `body` is a `dict`:
  - kept = `{k: body[k] for k in fields if k in body}`
  - **always additionally retain** every top-level `trust` / `*_trust` key even
    if not listed — so trust-gating stays visible and `ok`/`ok_downgraded_by`
    remain explainable. That is the concrete meaning of "enough envelope to stay
    interpretable".
  - set `fields_kept = sorted(kept.keys())`,
    `fields_omitted_count = len(body) - len(kept)`.
- When `fields` is supplied but `body` is a list / str / `None`: ignore it,
  `fields_kept = None`, `fields_omitted_count = None`, add the fact to a
  `note`-style entry is not required — just no-op.
- **Order of operations:** filter first, then run array truncation (§ 5) over
  what remains. `truncation` paths are relative to the filtered body.
- When `fields` is omitted: `body` is the bounded-but-otherwise-complete body;
  `fields_kept` / `fields_omitted_count` are `None`.

## 4. `allow_unmocked` semantics + typo handling (F-3)

Control flow at the top of `probe_engine_impl`:

```
explicit = engine_module is not None
target   = engine_module or engine_module_for(route)

if target:
    importlib.import_module(target)      # RAISES ModuleNotFoundError on any typo
    context = _market_data(target, ...)  # mock installed
    mocked, unmocked = True, False
else:
    if not allow_unmocked:
        return <1b refusal dict>         # structured, no raise
    context = nullcontext()
    mocked, unmocked = False, True
```

- **Default refusal** (AC-F3.1): `target` falsy (non-`/engines/` route, no
  explicit module) and `allow_unmocked` false → return the 1b dict. Route is
  never POSTed, nothing goes live, `reason` names `allow_unmocked`.
- **Unmocked opt-in** (AC-F3.2): same but `allow_unmocked=True` → run under
  `nullcontext()`, result carries `unmocked: True`.
- **Typo, explicit** (AC-F3.3): `engine_module="app.services.drawdon_engine"` →
  `target` truthy → `importlib.import_module` raises `ModuleNotFoundError`
  naming the module. **Raises — does not** fall through to an unmocked run.
  Today this surfaces later from `mocker.patch(f"{target}.MarketDataService")`;
  this change moves it earlier and makes it unconditional and explicit
  (`import_module` before the context is entered). Message already names the
  module (`No module named 'app.services.drawdon_engine'`).
- **Typo, route segment**: `/engines/drawdon/run` → `engine_module_for` returns
  `app.services.drawdon_engine` (non-None) → same `import_module` raise. Also
  loud. This is the run.md "keep typo'd engine name failing loudly" requirement,
  now covering both entry points.
- **Normal engine route** (AC-F3.4): unaffected — `target` derived, mock
  installed exactly as today, `unmocked=False`, no flag needed.

Distinction to hold: **non-derivable but valid route → structured refusal
(return); any unresolvable module name → raise.** They are different failures —
one is "you pointed me somewhere I refuse to go blind", the other is "you gave
me a name that doesn't exist".

## 5. F-2 truncation marker

Constants in `tools/probing.py` (build lane may tune):
`PROBE_ARRAY_HEAD = 5`, `PROBE_ARRAY_TAIL = 5`.

`_bound_arrays(obj, path="") -> (new_obj, truncated_paths)` walks the whole
decoded body recursively (dicts and lists). For any `list` with
`len > HEAD + TAIL + 1`:

```python
truncated = (
    value[:HEAD]
    + [{
        "__probe_truncated__": {
            "original_count": len(value),
            "dropped": len(value) - HEAD - TAIL,
            "kept_head": HEAD,
            "kept_tail": TAIL,
            "note": "probe_engine truncated this array; the route returned all elements",
        }
      }]
    + value[-TAIL:]
)
```

- The array **stays a `list`**, element order preserved, with exactly one
  sentinel `dict` inserted at the split point. A reader detects truncation by
  the `__probe_truncated__` key; `original_count` and `dropped` are both on it;
  `"probe_engine ... did it"` is in `note`.
- `len <= HEAD + TAIL + 1`: returned whole, no marker.
- `[]` (empty) and `null`/absent body: returned as-is, never a marker
  (AC-F2.3).
- Nested arrays (arrays of objects each holding an array) are all visited;
  every truncated array's dotted path (`underwater_series`,
  `episodes.3.daily_returns`) is appended to the `truncation` list.
- Applies to head/tail even inside `fields`-filtered bodies (§ 3 order).
- Recursion guard: cap traversal depth (e.g. 20) and leave anything deeper
  untouched rather than risk a pathological structure — advisory, not an AC.

AC-F2.5: a drawdown probe over multi-year synthetic history →
`underwater_series` (and any peer long array) truncated to 5+sentinel+5, so the
result is an order of magnitude smaller than the raw body, and `truncation`
lists `["underwater_series", ...]`.

## 6. F-4 — `_run` timeout: signature, budgets, result shapes

### 6a. Signature (scout's keyword-only risk)

```python
def _run(command, cwd, extra_env=None, *, timeout: float | None = None) -> subprocess.CompletedProcess:
    ...
    return subprocess.run(command, cwd=str(cwd), capture_output=True,
                          text=True, env=env, timeout=timeout)
```

`timeout` is **keyword-only** (after `*`). This preserves
`run.call_args[0][2] == extra_env` in `TestRunTestsParsing`
(test_mcp_tools.py:195, 204) and `run.call_args[0][0] == command` everywhere.
`_run` does **not** catch `TimeoutExpired` — it propagates; `subprocess.run`
already raises it, keeping `_run` a one-liner.

The `fake_run(command, cwd, extra_env=None)` side-effect stub in
`TestGates.test_check_gates_flags_goldens_drift` (line 225) will receive a
`timeout=` kwarg it does not accept → the **test lane updates that stub** to
`fake_run(command, cwd, extra_env=None, *, timeout=None)` (or `**kwargs`).
Named in § 8.

### 6b. Budgets — local `TIMEOUTS` dict in `tools/testing.py` (seconds)

```python
TIMEOUTS = {
    "full": 1800, "backend": 600, "frontend": 600, "typecheck": 300,
    "gate": 300,   # each check_gates subprocess (deadcode, tsc)
    "git": 30,     # git status / diff / checkout
}
```

These are wall-clock ceilings per invocation. `scripts/run_all_tests.py` owns
*which steps run, in what order, with what paths* — it does **not** own or
expose a per-call timeout, so defining these here restates nothing. Not
imported. `run_tests_impl` looks up `TIMEOUTS[scope]`; `check_gates_impl` uses
`TIMEOUTS["gate"]` / `TIMEOUTS["git"]`; `reset_goldens_impl` uses
`TIMEOUTS["git"]`.

### 6c. `run_tests_impl` — timeout result

Catch `subprocess.TimeoutExpired` around the single `_run` call:

```python
{
  "ok": False, "timed_out": True,
  "scope": scope, "command": " ".join(command), "cwd": str(cwd),
  "timeout_seconds": TIMEOUTS[scope], "exit_code": None,
  "failure_count": 0, "failures": [], "failures_truncated": False,
  "tail": _tail((exc.stdout or "") + "\n" + (exc.stderr or "")),  # partial output if any
}
```

The **normal-completion dict gains one key**: `"timed_out": False`. All other
keys unchanged. AC-F4.4 branching: `timed_out` True → timeout; `timed_out`
False and `ok` True → pass; `timed_out` False and `ok` False → parsed failure
(`exit_code` is an int, `failures` may be populated).

### 6d. `check_gates_impl` — per-subprocess timeout

**Wrap each of the three `_run` calls in its own try/except** (not one outer
try — AC-F4.5 requires completed gates still report). Each of `deadcode` and
`typecheck` sub-dicts gains `"timed_out": bool`. Add a top-level
`"timeouts": list[str]` naming whichever of `"deadcode"` / `"typecheck"` /
`"goldens"` timed out (`[]` normally). `goldens_drifted` stays `bool` (`False`
if its `git status` timed out, with `"goldens"` in `timeouts`).

New key-set: `{deadcode, typecheck, goldens_drifted, commit_gate, timeouts}` —
`TestGates.test_check_gates_reports_every_gate` updated by the test lane (§ 8).

### 6e. Unchanged completion (AC-F4.6)

A subprocess finishing under budget → exactly today's parsed result +
`"timed_out": False`. `_parse_failures`, `_tail`, `MAX_FAILURES` all untouched.

## 7. F-5 — `reset_goldens_impl` return shape

Three `_run` calls, **strict order**, each `timeout=TIMEOUTS["git"]`:

1. `["git", "diff", "--stat", "--", GOLDENS_PATH]` → capture stdout
2. `["git", "diff", "--", GOLDENS_PATH]` → capture stdout, then bound it:
   first `DIFF_MAX_LINES` (e.g. 120) lines + a `... <n> lines elided ...`
   marker line + last `DIFF_MAX_LINES` lines when longer; else whole.
3. `["git", "checkout", "--", GOLDENS_PATH]`

Return:

```python
{
  "ok": checkout.returncode == 0,
  "path": GOLDENS_PATH,
  "stderr": checkout.stderr.strip(),
  "discarded": bool(diff_stat.strip()),
  "diff_stat": diff_stat.strip(),      # "" when no drift
  "diff": bounded_diff,                 # "" when no drift
  "diff_truncated": <bool>,
  "timed_out": <any of the 3 git calls timed out>,
}
```

- Steps 1-2 run **before** step 3 — AC-F5.3. If checkout fails, `diff_stat` /
  `diff` are already populated and returned alongside `ok: False` + `stderr`.
- No drift (AC-F5.4): `discarded: False`, `diff_stat: ""`, `diff: ""` — not a
  bare `{ok, path, stderr}`.
- `TestGates.test_reset_goldens_checks_out_the_generated_file` asserts
  `run.call_args[0][0] == ["git","checkout","--",PATH]` — `call_args` is the
  **last** call, which is still the checkout, so it keeps passing with the
  default all-empty-stdout mock (→ `discarded: False`, checkout still runs,
  `ok: True`). Test lane adds the capture-order assertions from the test plan;
  it does not need to change the existing assertion.

## 8. Test-reference reconciliation

| item | verdict | who |
|---|---|---|
| "five-tool registration check" (US-43.1 test plan, AC-F3.4 mention) | **STRIKE.** It never existed. Testing tool registration means importing `server.py` → the `mcp` SDK the constraints ringfence. Registration is a `@server.tool()` decorator + the human MCP-handshake check run.md already carves out. | test lane omits; reviewer treats the struck reference as satisfied |
| `TestProbeEngine.test_drawdown_route_returns_a_response_with_mocked_market_data` (:95) — sends `{"snapshot": ...}` to flat `/engines/drawdown/run` | **REPOINT** to the correct flat payload: `{"benchmark_symbol": "SPY", "cash_balances": [], **build_snapshot_impl(...)}`. Add a **separate** dedicated case that sends the wrong shape and asserts `shape_mismatch` is populated and `body` is still returned. | test lane |
| `TestProbeEngine.test_patches_are_unwound_after_the_probe` (:116) — also sends `{"snapshot": ...}` to the flat route | May stay as-is (mismatch warning does not break the unwind assertion) or be repointed for consistency. Non-blocking. | test lane, optional |
| `TestGates.test_check_gates_reports_every_gate` (:208) — exhaustive `set(result) == {4 keys}` | **UPDATE** to include `"timeouts"` → `{deadcode, typecheck, goldens_drifted, commit_gate, timeouts}`. Required — fails otherwise. | test lane |
| `fake_run(command, cwd, extra_env=None)` stub (:225) | **UPDATE** signature to accept `*, timeout=None` (or `**kwargs`). Required. | test lane |
| `TestRunTestsParsing` positional assertions `run.call_args[0][2]` (:195, :204) | **NO CHANGE** — `timeout` is keyword-only, `extra_env` stays positional index 2. | — |
| `.agentic` backend.md:166 / quant.md:166-169 "response is not truncated"; testing.md:154-156 "does not validate the payload shape" | Stale after implementation — reworded at close-out. | docs lane, T-43.1.5 |

Wrapper-thinness (AC-G1) is an **integration-review check** (tech-lead reads the
`server.py` diff), not a required unit test. An optional SDK-free text-scan test
(read `server.py` as a file, assert each wrapper is one `return` + docstring
≤ 2 lines) is permitted but must not `import` the module.

## 9. F-1 sub-scoping verdict + final ticket lists

**F-1 stays ONE ticket — T-43.1.1 is not split.** Reasons:

- Model recovery is ~15 lines (`_request_model_for` + `_shape_of`), verified
  working on the pinned stack this pass — it is not the heavy, uncertain piece
  the producer/story worried it might be. No hand-maintained table.
- Shape reporting, the mismatch warning, the unclassified disclosure and the
  trust-gated `ok` all mutate the **same return envelope** inside the **same
  function** (`probe_engine_impl`). Splitting them creates two lanes editing one
  function with a merge dependency and zero isolation benefit.

**US-43.1 — unchanged:** T-43.1.1 (shape-aware envelope, F-1), T-43.1.2
(bounded body + `fields=`, F-2), T-43.1.3 (fail-safe gating, F-3), T-43.1.4
(tests), T-43.1.5 (capability-pack docs, close-out).

**US-43.2 — unchanged:** T-43.2.1 (per-scope timeouts, F-4), T-43.2.2
(`reset_goldens` records discard, F-5), T-43.2.3 (tests), T-43.2.4
(capability-pack docs, close-out).

Within the single backend WO for US-43.1, sequence the three code tickets
**envelope-first**: T-43.1.1 (defines the dict every downstream key attaches
to) → T-43.1.2 (adds `truncation` / `fields_*` / bounds `body`) → T-43.1.3
(adds `refused` / `unmocked` / control flow). One lane, one file, so this is
ordering guidance inside one dispatch, not three dispatches.

## 10. Lane split and dispatch order

Backend + test only. No frontend, no quant, no schema. `app/schemas/` untouched
(AC-G2). `server.py` changes = `probe_engine` wrapper gains `fields` +
`allow_unmocked` params only; the other four wrappers untouched.

| WO | lane | files | consumes | tickets |
|---|---|---|---|---|
| **WO-A** | backend | `app/mcp_server/tools/probing.py`, `app/mcp_server/server.py` (2-line sig add) | this plan §§ 1-5, 9 | T-43.1.1, T-43.1.2, T-43.1.3 |
| **WO-C** | backend | `app/mcp_server/tools/testing.py` | this plan §§ 6-7 | T-43.2.1, T-43.2.2 |
| **WO-E** | test | `app/tests/test_mcp_tools.py` | WO-A + WO-C final envelopes; this plan § 8 | T-43.1.4, T-43.2.3 |
| **WO-F** | docs | `.agentic` capability packs (backend/testing/quant) | contract notes from WO-A/WO-C; this plan § 8 table last row | T-43.1.5, T-43.2.4 |

**Order:**

1. **WO-A ∥ WO-C** — parallel. Different files (`probing.py` vs `testing.py`),
   zero shared code, independent ACs. No frontend counterpart.
2. **WO-E** — single test dispatch, after **both** WO-A and WO-C report done.
   Both test tickets edit the **same file** (`test_mcp_tools.py`), so they must
   be one dispatch, not two parallel ones. Verification for WO-A/WO-C/WO-E:
   `SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q`
   from `services/quant-engine`.
3. **integration review** (tech-lead INTEGRATION) — after WO-E. Focus: envelope
   consistency across §§ 1-7, the `server.py` wrapper stayed thin, the struck
   registration-test reference, the two `TestGates` edits landed.
4. **acceptance review** (reviewer) — AC-by-AC against US-43.1 / US-43.2.
5. **WO-F** — docs close-out, after both gates pass.
6. **human** — `python scripts/run_all_tests.py` from repo root, green, then
   commit. Not a ticket. The MCP transport/handshake is **not verified this
   run** — close-out report must state so (run.md constraint).

## 11. Reuse map

**probing.py (WO-A):**
- `engine_module_for(route)` — unchanged; still the source of *which module to
  patch*. The new `_request_model_for` is a **parallel** lookup for shape
  reporting, not a replacement.
- `_market_data` contextmanager, `_Patcher`, `fixtures.install_market_data_mock`
  — unchanged; the mock-install path is untouched.
- `nullcontext()` — still the unmocked path, now reachable only via
  `allow_unmocked=True`.
- New helpers to add: `_request_model_for`, `_shape_of`, `_bound_arrays`,
  `_trust_downgrade` (or inline), `_apply_fields`.

**testing.py (WO-C):**
- `_run` — gains `*, timeout=None` only; body otherwise unchanged.
- `_tail`, `_parse_failures`, `MAX_FAILURES`, `TAIL_LINES`, `VALID_SCOPES` —
  unchanged.
- Imported constants `BACKEND_DIR`, `FRONTEND_DIR`, `TEST_PASS_MARKER`,
  `npx_command` from `run_all_tests` — import unchanged (AC-G2).
- New: `TIMEOUTS` dict, `DIFF_MAX_LINES`, a `_timeout_result(scope, command,
  cwd, exc)` helper, a bounded-diff helper (may reuse the head/tail idea from
  `_bound_arrays` conceptually, but text not JSON — keep separate).

**test_mcp_tools.py (WO-E):**
- `build_snapshot_impl`, `price_rows_from_returns`,
  `mocker.patch.object(testing, "_run", ...)`, `subprocess.CompletedProcess`
  fakes — all existing patterns, reuse directly.
- Existing classes `TestEngineModuleDerivation`, `TestBuildSnapshot`,
  `TestProbeEngine`, `TestRunTestsParsing`, `TestGates` — extend; edits per § 8.

## 12. Guardrails and quant-audit

**None of guardrails 1-5 is engaged.**

- **G1 (financial accuracy / methodology-first):** the tool reads engine
  response `trust` strings and echoes them; it computes, derives and classifies
  nothing. No formula, no weighting, no return basis, no
  `docs/finance/financial-methodology.md` touch. `_trust_downgrade` only
  string-matches the literal `"unavailable"`.
- **G2 (methodology traceability):** no UI metric involved.
- **G3 (truth-class separation):** the body passes through unmodified except
  array bounding and optional field filtering — no truth classes blended.
- **G4 (trust semantics over fabrication):** the F-1 change *narrows* `ok`
  using the engine's own top-level trust string. It never fabricates a value,
  never fills a missing one, and never collapses `withheld` into `unavailable`
  — `withheld` / `degraded` / `verified` all keep `ok` (AC-F1.5). Only the
  literal wrapper-level `"unavailable"` downgrades.
- **G5 (no execution):** N/A.

**quant-audit stays SKIPPED** — consistent with run.md's `gates:` line and the
.agentic trust packs already shipped at v0.5.5. There is no mathematics for it
to check.
