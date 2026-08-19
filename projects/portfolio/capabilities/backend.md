# Capability pack: backend — project `portfolio`

For the `backend-engineer` lane. Everything about `services/quant-engine/`.
Where this contradicts general FastAPI/Pydantic instincts, this file wins.

Companion sources: `portfolio/CLAUDE.md`,
`docs/architecture/system-architecture.md`, `docs/finance/financial-methodology.md`,
`docs/contracts/<area>-fields.md`.

---

## Layout

```
services/quant-engine/app/
  schemas/      Pydantic models — CONTRACT SOURCE OF TRUTH
  api/routes/   thin FastAPI routers, one file per engine
  api/main.py   router registration
  services/     *_engine.py — the business logic
  analytics/    pure computation: returns, drawdown, distribution, risk,
                attribution, correlation, currency, performance, reconciliation
  clients/      FMP client (with caching) — the only place market data enters
  core/         settings, logging, caching infrastructure
  domain/       ledger + accounting model
  importers/    broker parsers (Interactive Brokers, Freedom24, ESPP)
  instruments/  instrument registry
  tests/        pytest — NOT your lane
```

Existing engine areas, for finding prior art: `attribution`, `correlation`,
`intra_correlation`, `currency_risk`, `dashboard_history`, `diagnostics`,
`distribution`, `drawdown`, `drift`, `exposure`, `imports`, `provenance`,
`stress`, `cache`, `market_data`, `health`.

## The four-file rhythm

Every engine feature is the same four files in the same order. Deviating from
the order is how contracts drift.

**1. `schemas/<area>.py` — first, always.**

```python
"""<Area> engine schemas (Epic N — <tab>).

<What this surfaces and under which truth class.>
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

from app.schemas.portfolio_engine import PortfolioEngineRequest

FooTrustLevel = Literal["synthetic", "unavailable"]
FooWindow = Literal[252, 756, 1260]

class FooEngineRequest(PortfolioEngineRequest): ...
class FooEngineResponse(BaseModel): ...
```

Conventions visible throughout the existing schemas, and expected of new ones:

- Module docstring names the epic and the **truth class** the outputs belong to.
- Requests extend `PortfolioEngineRequest`. Do not re-declare snapshot fields.
- `Literal` type aliases for every enum-like value — trust levels, windows.
- Class docstrings carry the **methodology reference and the formula**, e.g.
  "`contribution_pct = weight_at_peak × return × 100`", plus units and sign
  conventions. This is not decoration: it is how methodology traceability is
  maintained at the point of definition.
- Units are in the field name (`_pct`, `_pp`, `_usd`), not left to the reader.
- Trust granularity can differ by level. `drawdown.py` carries both a
  wrapper-level `DrawdownTrustLevel` and a per-episode
  `DrawdownDecompositionTrust` with an extra `partial` member, because a
  decomposition can be partial while the overall response is still synthetic.
  Model the levels that actually exist; do not flatten them.

**2. `services/<area>_engine.py`** — a `run_<area>_engine(request) -> Response`
entrypoint. Business logic here; pure computation delegates to `analytics/`.

**3. `api/routes/<area>.py`** — thin. This is the whole shape:

```python
router = APIRouter(prefix="/engines/<area>", tags=["<area>-engine"])

@router.post("/run", response_model=FooEngineResponse)
def run_foo(request: FooEngineRequest) -> FooEngineResponse:
    try:
        return run_foo_engine(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

No logic in the route. `detail=str(exc)` matters — the frontend adapter surfaces
it as the user-visible error message.

**4. `api/main.py`** — import the module and `app.include_router(<area>.router)`.
Forgetting this is the classic silent failure: everything imports, nothing fails
at build time, the route simply is not there.

## Reuse — do not re-derive these

- `_build_synthetic_snapshot_history_states` in `diagnostics_engine.py` — the
  synthetic daily portfolio state pipeline (current holdings × historical
  prices). Any engine needing synthetic history uses this one.
- `_lookback_calendar_days(window) = ceil(window * 1.6) + 30` in
  `attribution_engine.py` — trading-days-to-calendar-days conversion.
- `app/clients/fmp.py` via `MarketDataService` — **never** call FMP from a route
  or an engine directly. Caching lives in the client.
- `history_context_builder.py`, `holdings_history.py`,
  `portfolio_snapshot_builder.py`, `benchmark_service.py` for shared assembly.

A second copy of a formula is a real defect class here — US-34.8 found `risk.py`
holding its own copy of the daily-return formula. If a computation exists,
import it.

## Guardrails, in code terms

**Trust semantics.** Any field that can be null because of missing data is
paired with an explicit trust enum — `'synthetic' | 'unavailable'` for
synthetic-history paths, `'verified' | 'degraded' | 'withheld' | 'unavailable'`
for broker-truth paths. Never silently null, never a plausible substitute,
never collapse `withheld` into `unavailable`. The two mean different things:
withheld is "we have it and do not trust it"; unavailable is "we do not have it".

**Truth-class separation.** Broker truth, snapshot analytics, synthetic history
and persisted imports never mix in one response. If a response needs two, they
are two labelled sections, not one blended number.

**Methodology first.** Touching analytics, a factor formula, a weighting or
trust-state logic → read `docs/finance/financial-methodology.md` before writing.
If the formula you need is not documented there, that is a finding to report,
not a gap to fill with your own derivation.

**Fail closed.** Where the code withholds rather than guesses, that behaviour is
load-bearing. Do not weaken an admission gate to make a number appear. Epic 34
is largely a record of what happens when a number is published on a basis it
cannot support — read that PRD before touching a trust classification.

## Dead-code gate

`run_all_tests.py` runs `detect_deadcode.py --strict` (ruff + vulture + knip,
zero findings) plus `tsc --noEmit`. New dead code **fails the suite**.

For a genuine dynamic-use false positive — pytest fixture, Pydantic/FastAPI
hook, signature-match kwarg, persistence sanitizer, CLI entry point — add a
**reasoned** entry to `services/quant-engine/vulture_allowlist.py`. Every entry
must name why. An unexplained allowlist entry is how the gate stops working.

## Contract notes you must emit

The `schema_edit_reminder.py` hook fires on any edit under `app/schemas/`. Any
schema change means your report's `contract_notes` names, explicitly:

- the mirroring TS type in `apps/desktop/src/features/portfolio/types.ts`
- the contract doc `docs/contracts/<area>-fields.md`
- the methodology section, if a formula changed

This is not bookkeeping. The frontend and docs lanes work from your notes, and a
note you skip becomes drift nobody is looking for.

## Changing a published contract

If a change would alter a field already consumed by a route response or a
committed type, **stop and report it** rather than changing it. US-35.2 hit
exactly this: `clear()` kept its `int` return because `CacheClearResult.removed`
on the `/cache` route was typed from it — a published contract that story had
no mandate to change. The breakdown was derived at the CLI instead.

Widening a contract is usually safe; narrowing or re-typing one is a scope
decision that belongs to the tech lead and the producer.

## Definition of done for this lane

- [ ] Schema changed first; docstring carries methodology reference, units, sign convention
- [ ] Trust enum present on every nullable field
- [ ] Engine logic in `services/`, pure computation in `analytics/`, route thin
- [ ] Router registered in `api/main.py`
- [ ] No re-derived formula, lookback, or synthetic-history builder
- [ ] `python scripts/detect_deadcode.py --strict` clean, or a reasoned allowlist entry
- [ ] `contract_notes` names every downstream artifact that now lags
- [ ] No test files touched — that is the test lane
