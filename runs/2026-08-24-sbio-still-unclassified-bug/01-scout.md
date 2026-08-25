REPORT 2026-08-24-sbio-still-unclassified-bug/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order named verification: NONE (read-only recon order).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - PRIMARY root cause: `portfolio_snapshot_builder.py:32` (`build_imported_snapshot_from_request`) hardcodes `instruments=[]` — every position reconstructed from a `SnapshotAnalysisRequest` loses ISIN/description/listing_exchange evidence entirely.
  - `SnapshotAnalysisPosition` (schemas/imports.py:107-112) has no `isin`/`description`/`instrument_type`/`listing_exchange` fields, and its `sector` field is accepted but never read by `build_imported_snapshot_from_request` — dead on the wire.
  - `apps/desktop/.../portfolioAnalysisAdapter.ts:48-73` (`buildSnapshotAnalysisRequest`) sends only `{symbol, market_value, quantity, currency, sector}` per position — matches the schema gap, confirms no ISIN is ever sent from the frontend either.
  - Real app flow confirmed via App.tsx: `processImportedFiles` → `analyze-upload` (CSV parsed server-side, full `ImportedInstrument` records, correctly resolves SBIO) → but the response is NOT rendered directly. It calls `restoreImportedWorkspaceFromPersistedState` → `analyzeRestoredSnapshot` (App.tsx:536-565) → `runExposureEngine(snapshot)`, which POSTs the instrument-less `SnapshotAnalysisRequest` to `/api/engines/exposure/run` and OVERWRITES the correct initial result with a re-derived one.
  - `run_exposure_engine` (api/routes/exposure.py) → `build_exposure_result` → `build_snapshot_from_exposure_request` → `build_imported_snapshot_from_request` — this is the code path that actually renders, and it is where `instruments=[]` bites.
  - Consequence in `registry.py`: with `instruments=[]`, `attach_snapshot_metadata`'s `imported_by_symbol` lookup for SBIO is always `None`, so SBIO falls into the "no matching ImportedInstrument record at all" catch-all (registry.py:359-374), which sets `sector=None` unconditionally — `classify_imported_instrument`/`resolve_etf_sector` is never even reached, regardless of `market_data`, FMP plan/key, cache state, or the SBIO.L symbol rule.
  - This is a DIFFERENT bug class from T-39.1.7 (which was "market_data not threaded"). Here `market_data` IS threaded correctly (overview.py:26-27 constructs a real `MarketDataService()` when None) — the loss is upstream, in snapshot reconstruction, before classification is even attempted.
  - Everything US-39.1's own gates verified (identity gate, SBIO.L symbol rule, dominance threshold, FMP endpoint wiring) is confirmed correct by this scout too — see § Ruled-out checks. The defect is entirely in how the real app re-derives the snapshot for engine calls, not in anything US-39.1 shipped.
  - Secondary, unrelated gap (not the cause of this symptom, but same missing-market_data shape T-39.1.7 fixed elsewhere): `risk.py:612` (`build_lookthrough_exposure`) and `risk.py:1483` (`build_etf_overlap_pairs`) both call `registry.attach_snapshot_metadata(snapshot)` with no `market_data` argument. Currently harmless for SBIO's sector specifically (both call sites only read `instrument.asset_class`, not `.sector`), but is a live instance of the pattern and would matter if either function's metadata use is ever extended to read sector.
  - A fix needs to either (a) thread ISIN/description/listing_exchange through `SnapshotAnalysisRequest`/`SnapshotAnalysisPosition` and `buildSnapshotAnalysisRequest` end to end so `build_imported_snapshot_from_request` can populate real `ImportedInstrument` records, or (b) have the frontend persist and reuse the `analyze-upload` response's already-correct `overview`/`exposure` instead of re-deriving via `runExposureEngine` on every render — a design decision, not this scout's call.

risks:
  - Could not execute code (no Bash) — the `instruments=[]` finding is confirmed by reading `portfolio_snapshot_builder.py` and the schema, and by tracing App.tsx's call graph, but not by running the actual request/response.
  - Could not verify FMP_API_KEY (present in `services/quant-engine/.env`, non-placeholder 32-char value) is live/valid or that `/stable/etf/sector-weightings` is reachable on the current plan — no network access from this lane. Moot for THIS symptom since the classification code is never reached on the real render path, but would matter for a from-scratch statement import via `/portfolios/import/interactive-brokers` (non-upload route) if that is ever exercised directly.
  - Could not verify whether the currently-running backend process (if any) was started before or after US-39.1 landed — `--reload` should pick up changes, but this scout cannot inspect a live process.
  - Did not find any frontend IndexedDB/localStorage staleness bug — `portfolioDb.ts` stores workspace/node state but the exposure re-fetch itself (`runExposureEngine`) is a live network call on every render; staleness is not the mechanism here, the request payload itself is structurally incomplete.

## Orchestrator brief
- VERDICT (informational, this lane issues none): the real desktop-app render path never reaches `resolve_etf_sector` for SBIO at all. `build_imported_snapshot_from_request` (`portfolio_snapshot_builder.py:32`) always sets `instruments=[]`, so `attach_snapshot_metadata` can't match SBIO's `ImportedInstrument` (ISIN/description) and routes it to the "no imported instrument" catch-all — `sector=None` unconditionally, before `market_data`/FMP/cache/the SBIO.L rule ever matter.
- The one-time `analyze-upload` response DOES resolve SBIO correctly (full CSV-parsed instruments, live FMP) but the frontend discards that overview/exposure and immediately re-fetches via `runExposureEngine`, which uses the lossy `SnapshotAnalysisRequest` shape — this happens on the very first render after import, not just later navigation.
- Everything US-39.1 itself shipped (identity gate, SBIO.L rule in `symbols.py`, dominance threshold, FMP endpoint) reads correctly and matches the quant-audit's account — not implicated.
- Sections: § Ruled-out checks (per-DoD-item evidence).

## Ruled-out checks
- Statement data unchanged: `docs/IB2026.csv` SBIO row still has ISIN `IE00BQ70R696`, `LSEETF`, "INVESCO NASDAQ BIOTECH" (line 764).
- `scripts/manage_cache.py clear` (no `--namespace`) → `JsonFileCache.clear(namespace=None)` globs `*.json` in `settings.fmp_cache_dir` and deletes everything — this is the post-Epic-35/US-35.2 fixed version; not the F-2 gap.
- `symbols.py:69` still has the SBIO rule with only `SBIO.L` as its quote candidate, no bare `"SBIO"` — matches shipped design.
- `services/quant-engine/.env` has a non-placeholder `FMP_API_KEY` present; `.env` is read from `services/quant-engine` cwd, which is how `run_dev.py` launches uvicorn (`cwd=BACKEND_DIR`) — key is configured for the dev server.
- `overview.py:26-27` correctly constructs a live `MarketDataService()` when `market_data=None` — this specific call site does NOT reproduce the T-39.1.7 bug shape.
