REPORT 2026-08-24-sbio-still-unclassified-bug/T0
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/import_bootstrap.py — ImportedBootstrapResponse gains lookthrough, lookthrough_sector_exposure, market_overlap, current_state_concentration, availability (required) + imports
  - services/quant-engine/app/services/import_engine.py — build_import_bootstrap_from_snapshot now passes exposure_result's 5 fields into compose_import_bootstrap_response
  - services/quant-engine/app/services/import_engine_composer.py — compose_import_bootstrap_response accepts and forwards the 5 new params into ImportedBootstrapResponse(...)
  - apps/desktop/src/features/portfolio/types.ts — ImportedBootstrapResponse and ImportedPortfolioSnapshotSource TS types mirror the same 5 fields, non-optional

verification:
  command:   cd services/quant-engine && pytest app/tests/ -k "import_bootstrap or import_engine" -q; also pytest app/tests/test_analytics.py app/tests/test_routes.py app/tests/test_importer.py app/tests/test_import_admission.py -q; also full pytest app/tests/ -q; also cd apps/desktop && npx tsc --noEmit
  result:    FAIL
  detail:    pytest: 3 passed (filtered), 289 passed (broader consumer files), 905 passed full suite, 0 failed. tsc --noEmit: 2 errors, both outside T0 scope — importedBootstrapMapper.ts(36,5) (T1 non-goal) and test/portfolioFixtures.ts(1241,3) (test lane).

contract_notes:
  - ImportedBootstrapResponse (import_bootstrap.py) widened with 5 required fields — apps/desktop/src/features/portfolio/importedBootstrapMapper.ts (T1, out of this order's scope per non_goals) must forward them into the workspace object it builds, or the new backend fields are silently dropped before reaching workspace storage.
  - apps/desktop/src/features/portfolio/types.ts already mirrors the 5 new fields on both ImportedBootstrapResponse and ImportedPortfolioSnapshotSource in this same pass, per this project's schema-change convention.
  - docs/contracts/exposure-fields.md needs the analyze-upload/ImportedBootstrapResponse root-source subsection per 03-technical-plan.md § Schema change — that is T0-docs, a separate docs-engineer dispatch, not done here.
  - apps/desktop/src/test/portfolioFixtures.ts's ImportedBootstrapResponse-shaped fixture (~line 1241) no longer satisfies the widened type — needs the 5 new fields; test lane (T2), not touched here.

pack_corrections:
  - none

handoff:
  - T1 (frontend-engineer): importedBootstrapMapper.ts's projectImportedBootstrap must add lookthrough/lookthrough_sector_exposure/market_overlap/current_state_concentration/availability to the returned workspace object — see tsc error at importedBootstrapMapper.ts(36,5).
  - T2 (test-engineer): apps/desktop/src/test/portfolioFixtures.ts's ImportedBootstrapResponse fixture needs the 5 new fields to satisfy the widened type — see tsc error at portfolioFixtures.ts(1241,3).
  - Full backend pytest suite (905 passed, 0 failed) confirms no regression anywhere in services/quant-engine from the widened schema.
  - No import cycle: app.schemas.exposure does not import app.schemas.import_bootstrap; confirmed by reading exposure.py's import block before adding the new import there.

risks:
  - Order's verification asks tsc to compile clean against existing consumers, but non_goals forbid touching importedBootstrapMapper.ts — the one file causing the failure.
  - This is the expected, by-design interim state of the T0→T1 sequencing in 03-technical-plan.md (T1 owns fixing that file); reported FAIL/PARTIAL, not a false clean compile.
  - apps/desktop/src/test/portfolioFixtures.ts (test-lane file) also fails tsc post-widening; left untouched since this lane does not touch test files per backend.md's definition of done.
