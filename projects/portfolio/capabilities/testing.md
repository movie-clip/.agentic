# Capability pack: testing — project `portfolio`

Everything the `test-engineer` lane needs about how testing actually behaves in
this repo. This is a record of hard-won friction, not a tutorial. Where it
contradicts your general pytest/vitest instincts, this file wins.

Companion sources: `portfolio/.claude/skills/write-tests/SKILL.md` (fuller
prose, read it when this pack is thin on your case) and
`docs/architecture/testing-architecture.md`.

---

## Where things live

| Path | Purpose |
|---|---|
| `services/quant-engine/app/tests/` | all backend pytest |
| `services/quant-engine/app/tests/conftest.py` | autouse fixtures: golden-freshness check + market-data mocks |
| `services/quant-engine/app/tests/fixtures.py` | **the** shared scaffolding module — reuse, never re-implement |
| `services/quant-engine/app/tests/_statement_fixtures.py` | reusable import-statement fixtures |
| `services/quant-engine/app/tests/statement_truths.py` | statement-truth pins live here, in ONE module |
| `apps/desktop/src/**/*.test.tsx` | vitest specs, colocated with components |
| `apps/desktop/src/test/setup.tsx` | vitest setup — Recharts `ResponsiveContainer` shim |
| `apps/desktop/src/test/dashboardGoldens.ts` | **generated** — never hand-edit |
| `apps/desktop/src/test/designSystem.audit.test.ts` | design-system audit; fails the build on violations |
| `scripts/run_all_tests.py` | canonical entrypoint; a green run writes `.claude/.last-test-pass` |

## Running tests

```bash
# Narrow iteration — fastest, skips the golden freshness check
SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_<module>.py -v

# Backend, goldens regenerated
cd services/quant-engine && python -m pytest

# Frontend
cd apps/desktop && npx vitest run
cd apps/desktop && npx vitest run src/features/portfolio/MyComponent.test.tsx
cd apps/desktop && npx tsc --noEmit

# Full suite — the gate
python scripts/run_all_tests.py
```

Use narrow mode while working; run what the work order's `verification` field
names before reporting `PASS`.

## Gotchas that will bite you

**Goldens drift is usually noise.** After `run_all_tests.py` succeeds, check
`git diff apps/desktop/src/test/dashboardGoldens.ts`. If it is modified and your
work did not change dashboard output, `git checkout --` it before reporting.
That diff is an FMP-cache artifact, not a real change. Never hand-edit the file.

**No live network, enforced.** `pytest.ini` sets `--disable-socket
--allow-hosts=127.0.0.1,::1`. A test that forgets to mock market data fails
loudly with `SocketConnectBlockedError` rather than passing online and failing
offline.

- *Engine tests*: `conftest.py` autouse-mocks `MarketDataService` for exposure,
  dashboard-history, diagnostics, stress, drawdown and distribution with
  deterministic synthetic rows. A test-local `mocker.patch` takes precedence.
- *Client tests*: mock the provider library itself (`yfinance.Ticker`, `httpx`
  via an `FmpClient` patch) — never the network layer.
- *Genuinely live* (rare): `@pytest.mark.live_data` + `@pytest.mark.enable_socket`.
  Deselected by default (`-m "not live_data"`); run explicitly with
  `pytest -m live_data`.
- Loopback and file I/O are unaffected — in-process `TestClient`, `tmp_path` and
  `JsonFileCache` all work under the guard.

**Patch the engine module, not the service module.** `install_market_data_mock`
targets `{engine_module}.MarketDataService`, because engines import the class at
module load. Patching `app.services.market_data` will silently do nothing.

**New engine routes must join the response-integrity property test.** Add them
to `test_engine_response_integrity.py`; its route-table coverage check fails the
suite if you forget.

**Frontend charts need the shim.** `src/test/setup.tsx` shims Recharts'
`ResponsiveContainer`; a chart test that bypasses setup renders zero-size and
asserts nothing.

## Shared fixtures — mandatory, do not re-implement

From `app/tests/fixtures.py`:

- `imported_snapshot(positions=…, instruments=…, cash_balances=…)` — the full,
  422-proof `ImportedPortfolioSnapshot` payload, validated against the real
  schema by `test_fixtures.py`
- `position(symbol, market_value, **overrides)` — `ImportedPosition`-shaped dict
- `price_rows(…)` / `price_rows_from_returns(…)` — deterministic series builders
- `install_market_data_mock(mocker, target_module, *, histories, default_rows,
  vendor_by_symbol)`

Need scaffolding that does not exist? Extend this module rather than inlining a
local helper, and name the addition in your report's `handoff`.

## Assertion conventions (backend + frontend)

These came out of real breakages where an *additive* change broke tests that
never meant to forbid it.

**1. Containment for extensible structures; `==` only for closed contracts.**

Anything designed to gain fields over time — `last_fetch_meta`, admission check
sets, provenance metadata, run-metadata dicts — gets a superset assertion. An
`==` on its key set silently claims "these and only these keys, forever", which
is far stronger than the test intends, so every future field reads as a
regression.

```python
# Brittle — broke 5 tests when `vendor` was added, 2 more when a check was added
assert service.get_last_fetch_meta("VUAA") == {"type": "history", "resolved_symbol": "SPY", "cached": True}

# Robust — pins what the test cares about, tolerates additive fields
assert {"type": "history", "resolved_symbol": "SPY", "cached": True}.items() <= service.get_last_fetch_meta("VUAA").items()
```

Exact `==` is right when the set genuinely is closed: requested percentile keys,
an error-response body, a frozen fixture.

**2. Never assert an implicit default the test did not set.**

Changing the chart default window (60d → 20d) broke ten frontend tests that were
testing something else entirely. So: pin a default in exactly one dedicated test
that means to (`it('defaults to window_trading_days=252')`). Every other test
either sets the value explicitly first, or captures it dynamically and asserts
the *delta*.

## Trust-state discipline in tests

The product's core promise is that missing data is surfaced, never fabricated.
That makes trust states a first-class test target, not an edge case:

- Assert `withheld` and `unavailable` **separately**. Collapsing them is the
  exact bug the ladder exists to prevent, and a test that treats them as
  interchangeable will not catch it.
- Assert `degraded` renders its badge rather than silently looking verified.
- For any new field that can be missing, cover: present, missing, and degraded.
- Frontend: assert the unavailable state renders as unavailable — never as zero,
  never as a placeholder.

## Definition of done for this lane

- Tests exist for every behaviour the work order names, including the missing
  and degraded paths.
- Shared fixtures reused; any new scaffolding added to `fixtures.py` and
  reported in `handoff`.
- New engine routes registered in the response-integrity test.
- Assertions follow the containment / no-implicit-default rules.
- The order's `verification` command was actually run and passed.
- `dashboardGoldens.ts` is either unchanged or intentionally regenerated.
- No production code was modified. Defects found are reported, not patched.
