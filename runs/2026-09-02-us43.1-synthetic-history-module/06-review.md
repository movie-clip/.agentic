REPORT 2026-09-02-us43.1-synthetic-history-module/06
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\portfolio && python scripts/run_all_tests.py
  result:    PASS
  detail:    Full suite green: backend pytest 980 passed (50 warnings); frontend vitest 359 passed (40 files); tsc --noEmit clean; dead-code gate clean (ruff + vulture + knip). git diff dashboardGoldens.ts EMPTY; no backend golden in the diff after regen. Independent anchor: reconstructed pre-move bodies from `git show HEAD:...diagnostics_engine.py` L761-924, applied the 3 permitted renames, diffed vs synthetic_history.py -> zero differences.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-43.1.3 docs close-out still owed (docs-engineer): symbol-path text only in financial-methodology.md, system-architecture.md services inventory, quant-research SKILL.md, tech-debt row -> Resolved, roadmap slice log, story -> Done, CONTEXT.md confirm-only.

risks:
  - Story test plan says coverage matrix is "~7 cases"; test_synthetic_history_coverage.py actually has 12 `def test_` functions (11 pre-existing + 1 new AC2 pin). Plan 02 § 9 flagged the "~7" as approximate — reported as instructed, not a gap.
  - Pre-existing uncommitted drift (CLAUDE.md, epic-roadmap.md, stories/README.md, tech-debt-register.md, CONTEXT.md, docs/agents/, epic-43 PRD, US-43.*.md) is in the tree; work order non_goals declare it out of scope and not from this run — not assessed.

## Orchestrator brief

Acceptance gate over US-43.1 (T-43.1.1 + T-43.1.2), the behaviour-neutral
relocation of the two synthetic-history builders into
`app/services/synthetic_history.py`. Verdict: **PASS**. All five ACs SATISFIED;
test plan delivered; full suite re-run green by this gate. No change requests.
T-43.1.3 docs close-out still owed (handoff). Pre-existing doc drift in the tree
is out of scope per the work order.

Sections below: `AC-by-AC` (per-criterion evidence with file:line) ·
`Test plan delivery` (new pin test + `def test_` count) · `Trust-state spot
checks`.

## AC-by-AC

**AC1 — SATISFIED.** `app/services/synthetic_history.py` defines
`build_synthetic_snapshot_history_states` (L21) and
`build_synthetic_snapshot_history_states_with_coverage` (L34), both public. Bodies
verbatim: independent reconstruction of pre-move `diagnostics_engine.py` L761-924
from `git show HEAD`, renamed per the 3 permitted deltas (2x `def` name, 1x
thin-wrapper self-call), diffed against the new module -> empty. `diagnostics_engine.py`
has no `def _build_synthetic*` and imports the thin wrapper at L58
(`from app.services.synthetic_history import build_synthetic_snapshot_history_states`);
self-call at L731 uses the public name.

**AC2 — SATISFIED** (per plan 02 § 5 gradeable reading). All six modules carry a
`from app.services.synthetic_history import ...` line: attribution_engine:24,
correlation_engine:35, distribution_engine:25, drawdown_engine:26, stress_engine:26
(coverage variant), diagnostics_engine:58 (thin wrapper). Zero
`from app.services.diagnostics_engine import _build_synthetic...` anywhere in `app/`
or `app/tests/`. New pin test
`test_all_engine_consumers_bind_to_the_shared_synthetic_history_symbol`
(test_synthetic_history_coverage.py:338) asserts `is` identity of
`build_synthetic_snapshot_history_states_with_coverage` across the five engines vs
`app.services.synthetic_history`, plus `not hasattr` for both old private names on
`diagnostics_engine`. Falsifiable: a local re-implementation or a retained private
symbol breaks it. Importing the thin wrapper into diagnostics and the coverage
variant into the other five is the correct shape, not a deviation.

**AC3 — SATISFIED.** `git diff apps/desktop/src/test/dashboardGoldens.ts` empty
before and after a full `run_all_tests.py` (which regenerates goldens). No backend
golden file appears in `git diff --name-only HEAD`. Suite re-run by this gate:
backend 980 passed, frontend 359 passed, tsc clean, dead-code gate clean. No
computed value changed on any route.

**AC4 — SATISFIED.** `test_synthetic_history_coverage.py` imports from
`app.services.synthetic_history` (L21-23). The 6 coverage-matrix call sites
changed only by dropping the leading `_`; no assertion, expected value or fixture
body edited — behaviour-neutrality proof intact. `test_correlation_engine.py:310`
monkeypatch string retargeted to
`app.services.correlation_engine.build_synthetic_snapshot_history_states_with_coverage`
— public name, still patched on the consuming module.

**AC5 — SATISFIED.** Dead-code gate green (ruff F401/F811/F841 + vulture + knip,
zero findings); `tsc --noEmit` clean. `diagnostics_engine.py` no longer references
`DailyPortfolioState`, `DailyStatePosition`, `SyntheticHistoryCoverage` or
`SYNTHETIC_COVERAGE_DE_MINIMIS_WEIGHT` — all four dead imports removed, ruff F401
confirms no orphan.

## Test plan delivery

- "1 new test" pinning AC2: present —
  `test_all_engine_consumers_bind_to_the_shared_synthetic_history_symbol`.
- Named regression files: only `test_correlation_engine.py` (patch string) and
  `test_synthetic_history_coverage.py` (underscore-drop renames + pin test) were
  edited; `test_attribution*`, `test_distribution*`, `test_drawdown_analytics.py`,
  `test_stress*`, `test_diagnostics*` untouched and green in the full-suite run.
- `def test_` count in `test_synthetic_history_coverage.py`: **12**
  (L47/76/100/120/133/155/215/235/253/274/299/338). 11 pre-existing (name-only
  edits) + 1 new.

## Trust-state spot checks

No schema, no route, no `analytics/`, no `apps/desktop/src/**` touched. The
Synthetic History truth class is given a public home named for it; no trust label,
trust rung, or `SyntheticHistoryCoverage` field (`requested_start_date`,
`effective_start_date`, `limiting_symbol`, `excluded_symbols`) changed. No new
market-data caller introduced. No truth classes mixed in any response.
