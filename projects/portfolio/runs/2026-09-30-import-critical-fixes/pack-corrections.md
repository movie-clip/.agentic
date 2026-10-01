# Pack corrections — 2026-09-30-import-critical-fixes

- from 02-quant.md: capabilities/quant.md § The analytics modules — `ls app/analytics/` shows factor_model.py, which the table omits; add a row "factor_model.py | rolling factor regression (residuals feed risk.py residual_vol)".
- from 09-frontend.md § risks (last bullet, lane filed it as a risk): capabilities/frontend.md — does not warn that knip fails on exported-but-unused types (new exported types must be consumed), nor that retiring a shared helper turns its tests red until the test lane runs.
- from 13-test.md: capabilities/testing.md § Where things live — add src/test/combinedImportFixtures.ts, fakePortfolioDb.ts and fetchHarness.ts as the shared frontend scaffolding for App-level and storage tests
- from 13-test.md: capabilities/testing.md § Gotchas — add: a restore-path App test can use real storage over createFakePortfolioDb().install() and assert no write to portfolio_nodes, workspaces or working_drafts; workspace_state is written by restore by design
