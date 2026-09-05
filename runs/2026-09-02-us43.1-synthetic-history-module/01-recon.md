## Orchestrator brief

Recon map for relocating the two synthetic-history builders out of
`diagnostics_engine.py` into a new `services/synthetic_history.py`. All exact
line numbers below; the story's approximations are confirmed except two premises
that are wrong (call signature, M="MarketDataService input") — see `risks` and
the one named section.

- Definitions, spans, self-call line, every consumer import + call site, both
  test touch-points: in `handoff`.
- Blast radius is split into backend T-43.1.1 / backend T-43.1.2 / test /
  docs bullets in `handoff`, ready to become work orders.
- One section below: **§ Call-signature correction** — the verbatim call shape
  and the two function signatures, correcting the story.
- No verification (read-only). No contract notes, no pack corrections.

REPORT 2026-09-02-us43.1-synthetic-history-module/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE (read-only recon)
  result:    NOT_RUN
  detail:    Order verification field was NONE; no command to run.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - DEFINITIONS. `services/quant-engine/app/services/diagnostics_engine.py` — `_build_synthetic_snapshot_history_states` thin wrapper: `def` at L761, signature L761-765 `(snapshot, price_histories, valuation_dates) -> list[DailyPortfolioState]`, body L766-771, ends `return states` L771. `_build_synthetic_snapshot_history_states_with_coverage`: `def` at L774, signature L774-778 `-> tuple[list[DailyPortfolioState], SyntheticHistoryCoverage]`, docstring L779-794, body L795-924, `return` statement spans L919-924. Contiguous block to move verbatim: L761-924 (blank L772-773 between the two; next unrelated `def` is L927).
  - SELF-CALL in diagnostics_engine.py is at L733 exactly (story said ~733): `daily_states = _build_synthetic_snapshot_history_states(snapshot=..., price_histories=symbol_price_histories, valuation_dates=valuation_dates)` — it calls the thin wrapper, not the `_with_coverage` variant. The thin wrapper internally calls `_build_synthetic_snapshot_history_states_with_coverage` at L766. The thin wrapper has exactly ONE caller in the whole tree (this L733) and is imported nowhere else.
  - CONSUMER IMPORTS — all import the `_with_coverage` variant only, each a single-line `from app.services.diagnostics_engine import _build_synthetic_snapshot_history_states_with_coverage`: `attribution_engine.py:24`, `correlation_engine.py:35`, `distribution_engine.py:25`, `drawdown_engine.py:26`, `stress_engine.py:26`. Story's list confirmed exact.
  - CONSUMER CALL SITES — one each, identical shape: `attribution_engine.py:98`, `correlation_engine.py:122`, `distribution_engine.py:117`, `drawdown_engine.py:117`, `stress_engine.py:95`. Every one is `daily_states, coverage = _build_synthetic_snapshot_history_states_with_coverage(snapshot=snapshot, price_histories=symbol_price_histories, valuation_dates=valuation_dates)`. Return unpacking `(daily_states, coverage)` confirmed at all five. See § Call-signature correction.
  - TESTS (1). `app/tests/test_synthetic_history_coverage.py` — import is a parenthesised `from app.services.diagnostics_engine import (` at L21 with `_build_synthetic_snapshot_history_states_with_coverage,` on L22, `)` on L23. It calls the bare unqualified name at 6 sites: L61, L89, L111, L124, L146, L177 (each `states, coverage = _build_synthetic_snapshot_history_states_with_coverage(snapshot=..., price_histories=..., valuation_dates=...)`). Retargeting import + renaming touches L22 plus all 6 call lines unless an `as` alias is used.
  - TESTS (2). `app/tests/test_correlation_engine.py:310` — patch string is exactly `"app.services.correlation_engine._build_synthetic_snapshot_history_states_with_coverage"` (inside `mocker.patch(...)` opening L309, `return_value=(crafted_states, SyntheticHistoryCoverage(...))` L311). Patched on the consuming module, so it survives the re-home; only the leading underscore drops. Repo-wide grep for `_build_synthetic_snapshot_history_states` returns only these two test files plus the six `services/*_engine.py` — no other patch or import anywhere.
  - NEW MODULE IMPORTS (exhaustive, from the moved bodies): `ImportedPortfolioSnapshot` from `app.schemas.imports`; `DailyPortfolioState`, `DailyStatePosition`, `SyntheticHistoryCoverage` from `app.schemas.reconciliation`; `SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT` from `app.core.constants`. Nothing else — only builtins (`sum`, `min`, `max`, `set`, `round`, `float`) and the two functions calling each other. It does NOT reference `MarketDataService`.
  - NO PRIVATE-TO-DIAGNOSTICS SYMBOLS ARE CALLED. The two bodies define one local closure `_weight` (L814, stays inline) and otherwise call only each other plus the imports above. No other module-private helper of `diagnostics_engine.py` is used, so nothing else must move or be imported back.
  - IMPORT-CYCLE CHECK: clean. `app/schemas/reconciliation.py` imports no `app.services`/`app.engine`/`app.analytics`. `app/schemas/imports.py` imports only `app.core.constants`. `app/core/constants.py` imports no `app.*`. The new `services/synthetic_history.py` is a leaf; `diagnostics_engine.py` and the five engines importing it back cannot cycle (it imports none of them).
  - DEAD-CODE FALLOUT in diagnostics_engine.py after the two defs are removed (US-23.8 gate will flag): `SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT` (L3 import, used only in moved code) must be dropped from the `app.core.constants` import, keeping `DEFAULT_BENCHMARK_SYMBOL`. `DailyStatePosition` (L44) and `SyntheticHistoryCoverage` (L55) become unused → drop from the `app.schemas.reconciliation` import block. `DailyPortfolioState` (L43) is referenced only inside the moved bodies (L765/778/886/909); the L725/L733 `daily_states` assignments are unannotated → likely also unused after the move, drop unless the re-import is typed.
  - BLAST RADIUS backend T-43.1.1: create `services/quant-engine/app/services/synthetic_history.py` with `build_synthetic_snapshot_history_states` + `build_synthetic_snapshot_history_states_with_coverage` (bodies verbatim from L761-924, underscore dropped); in `diagnostics_engine.py` delete L761-924, add `from app.services.synthetic_history import ...`, repoint the L733 self-call to the public name, clean the 4 now-dead imports named above.
  - BLAST RADIUS backend T-43.1.2: rewire import line + call-site name in `attribution_engine.py` (L24, L98), `correlation_engine.py` (L35, L122), `distribution_engine.py` (L25, L117), `drawdown_engine.py` (L26, L117), `stress_engine.py` (L26, L95).
  - BLAST RADIUS test lane (T-43.1.2): `test_synthetic_history_coverage.py` import L22 + 6 call lines (L61/89/111/124/146/177); `test_correlation_engine.py` patch string L310; add the AC2 pin test asserting each consuming engine module now exposes `build_synthetic_snapshot_history_states_with_coverage` sourced from `app.services.synthetic_history`.
  - BLAST RADIUS docs lane (T-43.1.3): `docs/architecture/system-architecture.md` (engine inventory, ~L52); `docs/finance/financial-methodology.md` L180 (`_build_synthetic_snapshot_history_states*` "in diagnostics_engine.py"), L890, L968 (private-name references + home); `.claude/skills/quant-research/SKILL.md:71` (says helper is imported "from diagnostics_engine.py"); `docs/tech-debt-register.md:338` (US-43.1 row → Resolved); `docs/product/epic-roadmap.md` L111-113 + L137 (slice log + status); `docs/product/stories/README.md:27` (status); the story file → Done. `CONTEXT.md` L28-36 is already seeded with the correct public names and correct 6-consumer list — accurate, confirm only.
  - SOURCES OF TRUTH governing this area: `docs/finance/financial-methodology.md` §"Synthetic History Coverage Rule" (L177) and §"Synthetic History" — current (US-27.7 audit F8); moved body implements exactly that rule, move is behaviour-neutral so only symbol-path text changes. `docs/architecture/system-architecture.md` — backend seam / engine inventory. `docs/tech-debt-register.md` L330-338 — Epic 43 framing, explicit "behaviour-neutral relocation, goldens byte-identical". `CONTEXT.md` §Modules → "synthetic-history construction". All appear current.

risks:
  - The story's claim that consumers "pass `(snapshot, benchmark_symbol, market_data, …)`" is WRONG — no consumer passes `benchmark_symbol` or `market_data`; all five plus the diagnostics self-call pass exactly `(snapshot, price_histories, valuation_dates)` as keywords. The `(daily_states, coverage)` unpacking claim IS correct. See § Call-signature correction.
  - The story Notes' premise that the function "needs `MarketDataService`-shaped input" is WRONG — it takes plain `dict[str, list[dict]]` price histories and `list[str]` dates; it neither imports nor references `MarketDataService`. The "services/ not analytics/" conclusion may still hold (it returns engine-domain `DailyPortfolioState`), but the stated reason does not.
  - Story line hints "~L761–925" / "~L733" are close; exact: thin wrapper L761-771, coverage fn L774-924, self-call L733. The two defs plus the blank gap span L761-924.
  - Story says the `_with_coverage` helper is imported by "five other engines ... plus `diagnostics_engine.py` itself" — precise: `diagnostics_engine.py` does not import or directly call `_with_coverage`; it calls the thin non-coverage wrapper (L733), which is private-and-local with no other caller. AC1/AC2 wording ("all six import the helper") should read as "the thin wrapper for diagnostics, the coverage variant for the other five".
  - `diagnostics_engine.py` L43 `DailyPortfolioState` import: grep shows matches only at L43/765/778/886/909, but I could not fully rule out a dynamic/annotation use outside the moved region; the build lane should confirm before deleting the import to keep the dead-code gate green.

## Call-signature correction

Every consumer call site is identical in shape (the price-history variable is
`symbol_price_histories` at all five):

```python
daily_states, coverage = _build_synthetic_snapshot_history_states_with_coverage(
    snapshot=snapshot,
    price_histories=symbol_price_histories,
    valuation_dates=valuation_dates,
)
```

- `attribution_engine.py:98-102`
- `correlation_engine.py:122-126`
- `distribution_engine.py:117-121`
- `drawdown_engine.py:117-121`
- `stress_engine.py:95-99`

The diagnostics self-call (L733-737) calls the thin wrapper with the same three
keywords and no unpacking (`daily_states = _build_synthetic_snapshot_history_states(...)`).

Function signatures (both, verbatim intent):

```python
def _build_synthetic_snapshot_history_states(
    snapshot: ImportedPortfolioSnapshot,
    price_histories: dict[str, list[dict]],
    valuation_dates: list[str],
) -> list[DailyPortfolioState]: ...

def _build_synthetic_snapshot_history_states_with_coverage(
    snapshot: ImportedPortfolioSnapshot,
    price_histories: dict[str, list[dict]],
    valuation_dates: list[str],
) -> tuple[list[DailyPortfolioState], SyntheticHistoryCoverage]: ...
```

No `MarketDataService`, no `benchmark_symbol`. Callers fetch price histories
themselves (via their own `MarketDataService`) and pass the resulting dict in.
