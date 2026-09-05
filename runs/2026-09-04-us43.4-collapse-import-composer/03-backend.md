REPORT 2026-09-04-us43.4-collapse-import-composer/03
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/services/import_engine.py — added module-private `_compose_import_bootstrap_response`, verbatim body from the composer including the delegated `build_import_admission_summary(snapshot)` call. See § Fold detail.

verification:
  command:   cd services/quant-engine && pytest
  result:    PASS
  detail:    984 passed, 50 warnings in 98.98s (0:01:38)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - services/quant-engine/app/services/import_engine_composer.py still exists, untouched, with its now-unused `compose_import_bootstrap_response` function — per § Why the gate splits, resolved by the human `git rm services/quant-engine/app/services/import_engine_composer.py` (dispatch 2's HUMAN STOP), not by this lane.
  - Confirmed by direct read after the edit: all three public entry functions (`build_import_bootstrap`, `build_import_bootstrap_from_portfolio_snapshot_request`, `build_import_bootstrap_from_snapshot`) kept their exact prior names and signatures — only the internal call-site line changed.

risks:
  - none

## Orchestrator brief

- Fold applied verbatim per § Fold shape (inputs/02): helper, three new imports, merged reconciliation import, one call-site rename. See § Fold detail.
- Composer file left untouched, still imports cleanly — the human `git rm` (dispatch 2) is the remaining half of AC1/AC4, not this lane's to do.
- Backend `pytest` is green (984 passed) — the scoped checkpoint named in § Why the gate splits (inputs/02), not the full `run_all_tests.py` gate.

## Fold detail

- Removed line: `from app.services.import_engine_composer import compose_import_bootstrap_response`.
- Added lines: `from app.schemas.exposure import ExposureAvailability, ExposureCurrentStateConcentration`; `from app.schemas.portfolio_engine import PortfolioHistoryContext`; `from app.services.import_admission import build_import_admission_summary`.
- Merged (not duplicated): `app.schemas.reconciliation` import now reads `LookThroughOverview, LookThroughSectorExposure, MarketOverlapSummary, PortfolioOverview, PortfolioRiskSummary` on one line.
- Call-site: the single line `return compose_import_bootstrap_response(` inside `build_import_bootstrap_from_snapshot` became `return _compose_import_bootstrap_response(`; every keyword argument below it is unchanged.
