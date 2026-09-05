REPORT 2026-09-02-us43.1-synthetic-history-module/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification field was NONE; a DESIGN pass edits and runs nothing.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Contract statement for all build lanes: no schema / response-shape / field / docs-contracts boundary is crossed. see § 1
  - Final shape of app/services/synthetic_history.py: two public functions, exhaustive 3-line import list, leaf layering. see § 2
  - Per-lane ordered edit list with exact file:line for backend, test and docs lanes. see § 6
  - Ruling: independent quant re-audit NOT required for this verbatim move, conditional on an integration char-diff. see § 7
  - Lane split and dispatch order: backend -> test -> integration -> review -> docs; no frontend lane, no quant lane. see § 8

risks:
  - diagnostics_engine.py L43 `DailyPortfolioState` import: grep shows uses only inside the moved region; safe to drop but the backend lane must let the dead-code gate confirm, not hand-assert. see § 9
  - AC2's literal "all six consumers import the helper" is imprecise: diagnostics consumes the thin wrapper, the other five the coverage variant. Gradeable reading in § 5. see § 5
  - The story Test plan says "~7 cases"; the coverage test has 6 parametrised call sites. Reviewer should count actual `def test_` funcs. see § 9

## Orchestrator brief

Technical plan for the behaviour-neutral relocation of the two synthetic-history
builders from `diagnostics_engine.py` into a new leaf module
`app/services/synthetic_history.py`. Recon 01 is confirmed on every line number
and import; three story premises are wrong and restated in § 4.

Decisions taken:
- Module home `services/synthetic_history.py`; rationale re-grounded (returns engine-domain schema types, consumed only by `services/*_engine.py` — NOT "MarketDataService input", which is false).
- Contract: crosses NO schema / response-shape / field / docs-contracts boundary (§ 1).
- Quant-audit gate NOT required for this verbatim body move (§ 7), conditional on the integration gate char-diffing the moved bodies.
- Backend edits (T-43.1.1 + T-43.1.2 source) = ONE backend order; test edits a separate test order; docs at close-out.
- Dispatch: backend -> test -> integration -> review -> docs. No frontend lane, no quant lane.

Sections below: `1. Contract` · ``2. Final shape of `app/services/synthetic_history.py` `` · `3. Reuse` · `4. Story-premise corrections` · `5. AC1 / AC2 accurate reading` · `6. Per-lane ordered edit list` · `7. Ruling on the quant-audit gate` · `8. Lane split and dispatch order` · `9. Risks`.

---

## 1. Contract

**This relocation crosses no contract boundary.**

- **No Pydantic schema changes.** `app/schemas/**` is untouched. The moved
  functions consume `ImportedPortfolioSnapshot` (`app.schemas.imports`) and
  return `list[DailyPortfolioState]` / `tuple[list[DailyPortfolioState],
  SyntheticHistoryCoverage]` (`app.schemas.reconciliation`) — all pre-existing,
  all unchanged.
- **No route response shape changes.** No file under `app/api/routes/` or
  `app/api/main.py` is touched. Every `/engines/*` response is byte-identical.
- **No `docs/contracts/<area>-fields.md` change.** No backend field ↔ TS type ↔
  UI row is added, removed or retyped. `apps/desktop/src/**` is not touched —
  there is no frontend lane on this slice.
- **No `dashboardGoldens.ts` change** (AC3). Backend goldens are byte-identical
  because no computed value on any route changes.

**The only "contract" the build lanes share is internal and Python-level:**

| Element | Before | After |
|---|---|---|
| Thin wrapper | `diagnostics_engine._build_synthetic_snapshot_history_states(snapshot, price_histories, valuation_dates) -> list[DailyPortfolioState]` | `synthetic_history.build_synthetic_snapshot_history_states(...)` — same signature, `_` dropped |
| Coverage variant | `diagnostics_engine._build_synthetic_snapshot_history_states_with_coverage(snapshot, price_histories, valuation_dates) -> tuple[list[DailyPortfolioState], SyntheticHistoryCoverage]` | `synthetic_history.build_synthetic_snapshot_history_states_with_coverage(...)` — same signature, `_` dropped |
| Call convention | keyword args `snapshot=`, `price_histories=`, `valuation_dates=` at every call site | unchanged |

No positional-arg reshuffle, no new parameter, no return-type change. The
bodies move **verbatim** — the only in-body edit is the thin wrapper's internal
self-call name (`_build_..._with_coverage` -> `build_..._with_coverage`).

**Truth-class note (guardrail #3).** The Synthetic History truth class is not
reclassified — it is given a public home named for it. No trust label, no trust
rung, and no `SyntheticHistoryCoverage` field (`requested_start_date`,
`effective_start_date`, `limiting_symbol`, `excluded_symbols`) changes. The seam
becomes more honest, not different.

---

## 2. Final shape of `app/services/synthetic_history.py`

**Two functions, both public (no leading underscore), bodies verbatim from
`diagnostics_engine.py` L761–924:**

1. `build_synthetic_snapshot_history_states(snapshot, price_histories, valuation_dates) -> list[DailyPortfolioState]`
   — thin wrapper, body = current L766–771, with its internal call repointed to
   the public `build_synthetic_snapshot_history_states_with_coverage`.
2. `build_synthetic_snapshot_history_states_with_coverage(snapshot, price_histories, valuation_dates) -> tuple[list[DailyPortfolioState], SyntheticHistoryCoverage]`
   — body = current L795–924; the L779–794 docstring moves with it unchanged.
   The local closure `_weight` (current L814) stays inline.

**Import list — exhaustive, confirmed against the moved bodies (recon "NEW
MODULE IMPORTS" is correct):**

```python
from app.core.constants import SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT
from app.schemas.imports import ImportedPortfolioSnapshot
from app.schemas.reconciliation import (
    DailyPortfolioState,
    DailyStatePosition,
    SyntheticHistoryCoverage,
)
```

Nothing else. The bodies otherwise use only builtins (`sum`, `min`, `max`,
`set`, `round`, `float`) and call each other. **No `MarketDataService`, no
`benchmark_symbol`, no `app.services.*` / `app.engine.*` / `app.analytics.*`
import.**

**Module docstring intent** (build lane writes the prose): this module owns the
**Synthetic History** truth-class reconstruction — a daily portfolio-state
series from current holdings × historical prices — under the US-27.7 coverage
rule (`docs/finance/financial-methodology.md` §"Synthetic History Coverage
Rule"). Extracted verbatim from `diagnostics_engine.py` in US-43.1 so the seam
is importable as a public function and testable on its own.

**Layering position — cycle-free, confirmed:** `app.core.constants` imports no
`app.*`; `app.schemas.imports` imports only `app.core.constants`;
`app.schemas.reconciliation` imports no
`app.services`/`app.engine`/`app.analytics`. So `synthetic_history.py` is a
**leaf**. `diagnostics_engine.py` and the five `*_engine.py` consumers import
it; it imports none of them → acyclic.

---

## 3. Reuse

- **Backend lane** builds on: `app.schemas.reconciliation`
  (`DailyPortfolioState`, `DailyStatePosition`, `SyntheticHistoryCoverage` —
  moved, not redefined), `app.schemas.imports.ImportedPortfolioSnapshot`,
  `app.core.constants.SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT`. This is a pure move
  — **no new logic**; the coverage rule, fallback branches and `(states,
  coverage)` shape are lifted character-for-character.
- **Test lane** builds on: the existing
  `app/tests/test_synthetic_history_coverage.py` coverage-matrix cases (the
  behaviour-neutrality regression proof — must stay green with no substantive
  edit), `app/tests/fixtures` (`imported_snapshot`, `position`), and
  pytest-mock `mocker.patch` / `mocker.spy` as already used in
  `test_correlation_engine.py`.
- **Docs lane** builds on: `docs/architecture/system-architecture.md`
  engine/services inventory, `docs/finance/financial-methodology.md` §"Synthetic
  History" / §"Synthetic History Coverage Rule", `docs/tech-debt-register.md`
  US-43.1 row, `docs/product/epic-roadmap.md` slice log, repo-root `CONTEXT.md`
  §Modules (already seeded — confirm only).

---

## 4. Story-premise corrections

**(a) Call signature.** The story's "all pass `(snapshot, benchmark_symbol,
market_data, …)`" is **wrong**. Every consumer call site passes exactly three
keyword arguments — `snapshot=snapshot`,
`price_histories=symbol_price_histories`, `valuation_dates=valuation_dates` —
and the five engines unpack `daily_states, coverage = ...`. The diagnostics
self-call (L733) passes the same three keywords to the **thin wrapper** and does
**not** unpack. No consumer passes `benchmark_symbol` or `market_data`.

**(b) No `MarketDataService`.** The story Notes' premise that the function
"needs `MarketDataService`-shaped input" is **wrong**. It takes a plain
`dict[str, list[dict]]` of per-symbol price rows and a `list[str]` of valuation
dates. It neither imports nor references `MarketDataService`. Each caller
fetches its own price histories (via its own `MarketDataService`) and passes the
resulting dict in.

**(c) Module-home rationale, re-grounded.** The conclusion "`services/` not
`analytics/`" still holds, but not for the stated reason. Correct grounds:
- the functions return **engine-domain schema objects** (`DailyPortfolioState`,
  `SyntheticHistoryCoverage` from `app.schemas.reconciliation`) and orchestrate
  a multi-step snapshot × price-history reconstruction with fallback branches —
  business logic, not a stateless formula primitive;
- they are already consumed **exclusively** by `services/*_engine.py` modules;
- `analytics/` in this repo holds pure formula kernels (returns, drawdown,
  distribution, risk); a reconstruction that assembles portfolio states from a
  snapshot does not belong there;
- there is no schema consumer, so there is no layering pull toward `core/`.

**(d) "all six import the helper" imprecision** — see § 5.

---

## 5. AC1 / AC2 accurate reading

**AC1 — falsifiable checks:**
- `app/services/synthetic_history.py` exists and defines both
  `build_synthetic_snapshot_history_states_with_coverage` and
  `build_synthetic_snapshot_history_states`, bodies verbatim (char-diff vs the
  pre-move L761–924 shows only the two `def` names and the one internal
  self-call name changed).
- `grep -n "def _build_synthetic" app/services/diagnostics_engine.py` → **zero
  matches**.
- `diagnostics_engine.py` contains
  `from app.services.synthetic_history import build_synthetic_snapshot_history_states`.

**AC2** — the literal phrase "all six consumers import the helper from
`services.synthetic_history`" is imprecise: **diagnostics_engine consumes the
thin non-coverage wrapper, the other five consume the coverage variant** — they
do not all import the same object. The gradeable reading:
- `grep -rn "from app.services.diagnostics_engine import _build_synthetic" app/ app/tests/`
  → **zero matches** (the real checkable half of AC2).
- Each of the six modules — `diagnostics_engine`, `attribution_engine`,
  `correlation_engine`, `distribution_engine`, `drawdown_engine`,
  `stress_engine` — has a `from app.services.synthetic_history import ...` line:
  the five engines import
  `build_synthetic_snapshot_history_states_with_coverage`, diagnostics imports
  `build_synthetic_snapshot_history_states`.
- The new AC2 pin test asserts object identity:
  `<engine>.build_synthetic_snapshot_history_states_with_coverage is
  synthetic_history.build_synthetic_snapshot_history_states_with_coverage` for
  all five engines.

**Reviewer:** do not fail an implementation that imports the thin wrapper into
diagnostics and the coverage variant into the other five — that is the correct
behaviour-neutral shape, not a deviation.

---

## 6. Per-lane ordered edit list

### Backend order — T-43.1.1 + T-43.1.2 source edits (one `backend-engineer` work order)

**Step 1 — create `app/services/synthetic_history.py`** (T-43.1.1):
- Module docstring per § 2.
- The 3-import block from § 2.
- `build_synthetic_snapshot_history_states` — body verbatim from current
  L766–771; repoint its internal call to
  `build_synthetic_snapshot_history_states_with_coverage`.
- `build_synthetic_snapshot_history_states_with_coverage` — body + docstring
  verbatim from current L779–924.

**Step 2 — gut `app/services/diagnostics_engine.py`** (T-43.1.1):
- Delete L761–924 (both `def`s + the blank gap between them).
- Add `from app.services.synthetic_history import build_synthetic_snapshot_history_states`.
- L733: `_build_synthetic_snapshot_history_states(` → `build_synthetic_snapshot_history_states(` (keyword args unchanged).
- L3: `from app.core.constants import DEFAULT_BENCHMARK_SYMBOL, SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT`
  → drop `SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT`, keep `DEFAULT_BENCHMARK_SYMBOL`.
- L42–60 `from app.schemas.reconciliation import (…)` block: drop
  `DailyPortfolioState` (L43), `DailyStatePosition` (L44),
  `SyntheticHistoryCoverage` (L55). Keep every other name in that block.
- Let `python scripts/detect_deadcode.py --strict` (folded into
  `run_all_tests.py`) confirm no orphaned import remains — do not hand-assert
  `DailyPortfolioState` is dead (see § 9).

**Step 3 — rewire the five engines** (T-43.1.2). Each is a one-line import swap +
one call-site rename; keyword args unchanged:

| File | Import line | Call-site line |
|---|---|---|
| `app/services/attribution_engine.py` | L24 | L98 |
| `app/services/correlation_engine.py` | L35 | L122 |
| `app/services/distribution_engine.py` | L25 | L117 |
| `app/services/drawdown_engine.py` | L26 | L117 |
| `app/services/stress_engine.py` | L26 | L95 |

Each import line becomes
`from app.services.synthetic_history import build_synthetic_snapshot_history_states_with_coverage`;
each call site drops the leading `_`.

**Verification:** `python scripts/run_all_tests.py` green; `git diff
apps/desktop/src/test/dashboardGoldens.ts` empty; dead-code gate green.

### Test order — T-43.1.2 test edits (one `test-engineer` work order, after backend)

- `app/tests/test_synthetic_history_coverage.py`:
  - L21–23 import block: retarget to `from app.services.synthetic_history import
    ( build_synthetic_snapshot_history_states_with_coverage, )`.
  - Rename the 6 call sites — L61, L89, L111, L124, L146, L177 — dropping the
    leading `_` (explicit rename preferred over an `as` alias so
    `grep -r "_build_synthetic" app/tests/` returns clean, per AC2 spirit).
- `app/tests/test_correlation_engine.py` L310: patch string
  `"app.services.correlation_engine._build_synthetic_snapshot_history_states_with_coverage"`
  → `"app.services.correlation_engine.build_synthetic_snapshot_history_states_with_coverage"`
  (still patched on the consuming module — patch survives the re-home).
- **New AC2 pin test** in `test_synthetic_history_coverage.py`: import
  `app.services.synthetic_history` and each of the five engines; assert
  `<engine>.build_synthetic_snapshot_history_states_with_coverage is
  synthetic_history.build_synthetic_snapshot_history_states_with_coverage` for
  `attribution_engine`, `correlation_engine`, `distribution_engine`,
  `drawdown_engine`, `stress_engine`; and assert
  `not hasattr(diagnostics_engine, "_build_synthetic_snapshot_history_states")`.
- **Verification:** `python scripts/run_all_tests.py` green. The existing
  coverage-matrix cases must pass **unchanged in substance** — the
  behaviour-neutrality proof.

### Docs order — T-43.1.3 (one `docs-engineer` work order, at close-out)

- `docs/architecture/system-architecture.md` — engine/services inventory
  (~L52): add `synthetic_history` to the `services/` list.
- `docs/finance/financial-methodology.md` — L180, L890, L968: private-name
  references `_build_synthetic_snapshot_history_states*` "in
  diagnostics_engine.py" → public names "in `services/synthetic_history.py`".
  **Text-path only — no methodology content changes.**
- `.claude/skills/quant-research/SKILL.md:71` — "imported from
  diagnostics_engine.py" → "from `services/synthetic_history.py`".
- `docs/tech-debt-register.md:338` — US-43.1 row → Resolved.
- `docs/product/epic-roadmap.md` L111–113 + L137 — slice log + status.
- `docs/product/stories/README.md:27` — status.
- `docs/product/stories/US-43.1-extract-synthetic-history-construction.md` —
  Status → Done.
- Repo-root `CONTEXT.md` L28–36 — already seeded with correct public names +
  6-consumer list; **confirm accuracy only** (docs order scope must name
  `CONTEXT.md` explicitly — it is not under `docs/`).

---

## 7. Ruling on the quant-audit gate

**No independent financial re-audit is required.** The byte-identical-goldens
gate + full-suite-green + the `test_synthetic_history_coverage.py` coverage
matrix + the integration gate's verbatim-body check are sufficient — *conditional*
on the integration gate performing the char-diff named below.

**Justification against guardrail #1 and the profile's quant-lane rule:**

- The profile makes the quant lane mandatory for a change "touching
  `analytics/`, a formula, a weighting, a return basis, or a trust
  classification." This slice touches **none** of those: it moves two function
  bodies out of `services/diagnostics_engine.py` into
  `services/synthetic_history.py` with zero character change to the logic (only
  the two `def` names and one internal self-call name). `analytics/` is not
  touched.
- Guardrail #1's trigger is a **change to the mathematics or trust-state
  logic**. A verbatim move changes no formula, no weighting, no return basis,
  and no trust label or `SyntheticHistoryCoverage` field. There is nothing an
  independent recompute could find that the byte-identical golden comparison
  does not already prove more strictly — the goldens *are* the independently
  recomputed reference values, and byte-identity is a stronger statement than
  "an auditor re-derived it and agrees."
- Guardrail #1 also requires "update its tests in the same pass." Satisfied: the
  test lane retargets `test_synthetic_history_coverage.py` and adds the AC2 pin
  test in this slice; the coverage-matrix cases run against the moved function
  unchanged.
- The methodology-doc changes are **symbol-path text only** (§ 6 docs order) —
  not a methodology change, so §"Financial accuracy first" is not engaged.

**Condition on the ruling (assigned to `tech-lead` INTEGRATION):** diff the two
moved function bodies against their pre-move form
(`git show HEAD:app/services/diagnostics_engine.py` L761–924 vs the new file).
The diff must be empty except for: (1) `def _build_...` → `def build_...` ×2,
(2) the thin wrapper's internal `_build_..._with_coverage(` →
`build_..._with_coverage(`. **Any other in-body delta voids this ruling and
triggers the quant lane** — it is then no longer a verbatim relocation.

---

## 8. Lane split and dispatch order

| # | Lane | Agent | Scope |
|---|---|---|---|
| 1 | backend | `backend-engineer` | § 6 backend order — T-43.1.1 module creation + `diagnostics_engine.py` gut/rewire/dead-import cleanup + T-43.1.2 five-engine rewire. Non-test source only. |
| 2 | test | `test-engineer` | § 6 test order — `test_synthetic_history_coverage.py` import + 6 call sites, `test_correlation_engine.py:310` patch string, new AC2 pin test. |
| 3 | integration | `tech-lead` INTEGRATION | § 1 contract alignment (confirm no schema/route/golden/TS drift) + **the § 7 verbatim char-diff condition** + dead-code + `run_all_tests.py` + `git diff dashboardGoldens.ts`. |
| 4 | review | `reviewer` | AC1–AC5 against § 5's gradeable reading. |
| 5 | docs | `docs-engineer` | § 6 docs order — T-43.1.3, at close-out. |

- **No frontend lane** — `apps/desktop/src/**` is not touched.
- **No quant lane** — per the § 7 ruling.
- Steps 1 and 2 are strictly ordered (test edits import the new module path).
  Steps 3–4 gate; step 5 closes out.

---

## 9. Risks

- **`DailyPortfolioState` import (diagnostics_engine.py L43).** Direct grep
  confirms uses only at L43/765/778/886/909 — all inside the moved region.
  Dropping it is correct, but the backend lane must rely on
  `detect_deadcode.py --strict` (in `run_all_tests.py`) to confirm; if the gate
  flags an unexpected remaining use, stop and report.
- **Import alias vs 6 renames in the coverage test.** The plan prefers explicit
  renames so `grep -r "_build_synthetic" app/tests/` returns clean (AC2 spirit).
  An `as` alias satisfies the import-path AC but leaves the old underscore name
  in the file — avoid.
- **Ordering hazard.** If the five engines are rewired before
  `synthetic_history.py` exists, imports break. The backend order's steps are
  numbered for that reason — create the module first.
- **The story Test plan says "~7 cases."** The coverage matrix has 6
  parametrised call sites (L61/89/111/124/146/177); the reviewer should count
  the actual `def test_` functions, not the "~7", when checking the test plan
  was delivered.
- **`CONTEXT.md` is at the repo root, not under `docs/`.** The docs lane's scope
  must name it explicitly or the confirm-only step is silently skipped.
