REPORT 2026-09-12-rolling-factor-f1-f7/02
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/reconciliation.py — removed `alpha: float | None = None` from `RollingFactorLoadingPoint` (line 483).
  - services/quant-engine/app/tests/test_analytics.py — removed the `"alpha": None,` key from the expected-output dict at line 5419.

verification:
  command:   cd services/quant-engine && pytest app/tests/test_analytics.py -k "rolling_loadings or factor_model" -v
  result:    PASS
  detail:    8 passed, 212 deselected in 7.01s

contract_notes:
  - `RollingFactorLoadingPoint.alpha` removed from the schema (`services/quant-engine/app/schemas/reconciliation.py`).
  - `apps/desktop/src/features/portfolio/types.ts` must drop `alpha: number | null` from the three mirrored element types (`rolling_loadings_20d`/`_60d`/`_252d`, ~lines 839/861/883) — frontend lane, out of this order's scope.
  - `apps/desktop/src/test/portfolioFixtures.ts:958-960` still fabricates `alpha: 0.0002`/`alpha: null` and must be updated — test lane.
  - `apps/desktop/src/features/portfolio/FactorDriftSummaryCard.test.tsx:13`'s `REQUIRED_LOADING_KEYS` array still lists `'alpha'` and must drop it — test lane.
  - No `docs/contracts/<area>-fields.md` row ever named `alpha` for this field (confirmed via the design pass's grep of the methodology doc) — nothing to retract there.

pack_corrections:
  - none

handoff:
  - Repo-wide grep for `alpha` in `services/quant-engine/` turned up 14 files, all unrelated to `RollingFactorLoadingPoint` (a `risk.py` comment about not computing a global-intercept alpha, an unrelated local OLS variable at test_analytics.py:5353, importer/optimizer/registry/settings material).
  - Confirmed no other backend code constructs or reads `.alpha` on `RollingFactorLoadingPoint` — no additional backend fix needed beyond the two named sites.
  - The schema-edit reminder hook fired on the `reconciliation.py` edit as expected; its instruction to update TS types and contract docs is satisfied via the `contract_notes` entries, per this order's scope fence, not by editing those files here.

risks:
  - none
