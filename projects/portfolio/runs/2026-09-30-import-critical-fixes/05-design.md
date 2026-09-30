REPORT 2026-09-30-import-critical-fixes/05
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only design pass; order verification was NONE. Two probes run from scratchpad (no repo edit): chained combine (IB+ESPP)+IB gives VUAA 160 and account_id 'I09548809 + U8516450 + U8516450'; IB+IB gives 18 positions / 62843.22.

contract_notes:
  - schemas/imports.py ImportedPosition.cost_basis and unrealized_pnl become float | None = None; types.ts:37-39 already nullable; docs/contracts/imports-fields.md must be CREATED. see § Contract
  - schemas/reconciliation.py PortfolioOverview: total_cost_basis and total_unrealized_pnl float | None, new cost_basis_trust, top_positions value union gains None; types.ts:56-61 must mirror in the same pass. see § Contract
  - schemas/reconciliation.py EnrichedPosition and analytics/performance.py build_enriched_positions are removed (no caller); portfolio_imports.py re-export goes with them. see § Reuse and retirements
  - schemas/import_bootstrap.py: ImportAdmissionSummaryV1 gains optional rollup; types.ts:1183 and docs/contracts/import-admission-fields.md must mirror. see § Contract
  - schemas/import_bootstrap.py: new CombinedImportBootstrapRequest and ImportedBootstrapResponse.constituent_snapshots; new route POST /portfolios/import/analyze-combined; types.ts:1208 mirror; dashboard-fields.md § Combine Imported Snapshots and system-architecture.md:34 lag. see § Contract
  - workspaceTypes.ts ImportedNodeSource gains importedConstituents and derivationVersion; portfolioWorkspaceStorage.ts sanitizeImportedNodeSource whitelists fields and would silently drop both. see § Contract
  - financial-methodology.md needs E1, E2, E3, E4 plus a single-charge commission rule and edits to lines 2332-2333 and 2405 of § Multi-Statement Snapshot Merge. see § Docs assignment
  - apps/desktop/src/test/dashboardGoldens.ts and app/scripts/golden_market_data.json change: FF block by F1/F7/F4, IB block gains one additive key (cost_basis_trust). Human-run recapture required. see § Human-run steps

pack_corrections:
  - none

handoff:
  - Dispatch order: BE-1 combine/admission/route, BE-2 Freedom24 dates, BE-3 cost basis, FE-1 add flow and types, then H-1 golden recapture (human), T-1 backend tests, T-2 golden-dependent tests, FE-2 shared re-derive, T-3 frontend tests, docs close-out. see § Lane split
  - Stop for the human on H-1 (FMP_API_KEY capture), H-2 (D-7 F2 lineage-evidence reading) and H-3 (D-5 legacy cost-basis scrub). H-2 and H-3 gate only the legacy parts of FE-2 and BE-4. see § Human-run steps
  - US-46.4 AC 11 cannot be met by re-derivation: the fabricated 3,018.96 is inside the persisted ImportedSnapshot itself. Needs H-3 or an AC change. see § Saved-node re-derive
  - US-46.3 AC 13-14 cannot be recomputed from stored statements: add nodes persist only the chained combined snapshot, not the constituents. Proposed reading uses persisted per-node admissions as carried evidence. see § Saved-node re-derive
  - Existing backend combine is not idempotent when an already-combined snapshot is combined with a same-account statement; design combines flat from constituents and adds a fail-closed guard. see § Contract
  - Backend engineers must not edit tests; BE-2 leaves test_importer.py:288 and the private-parser call at :332 red until T-1. Lanes run targeted commands only until H-1 completes. see § Human-run steps
  - Use one shared re-derive step (FE-2) for T-46.1.3, T-46.3.3 and T-46.4.3; do not build three. see § Saved-node re-derive
  - FE-1 must call the ui-polish skill for ImportAdmissionReviewCard changes; the design-system audit test enforces it. see § Lane split
  - App.test.tsx test helpers must stamp derivationVersion on non-legacy fixtures or every restore test triggers an extra analyze-combined fetch. see § Lane split

skill_calls:
  - mattpocock-skills:codebase-design — called, used to place one seam (build_combined_import_bootstrap) that both the multi-file upload and add-statement paths cross, and to apply the deletion test to overlayImportedSnapshot, EnrichedPosition and _parse_commissions

risks:
  - US-46.4 AC 7 premise fails after US-46.1: an added-statement node now takes Exposure holdings from the statement-path combine, so IB2026 re-added shows stated 62,255.14 / 3,491.53, not unavailable. The request-path builder is still nulled. Reviewer or human must confirm. see § AC pressure points
  - US-46.4 AC 9 is satisfied by absence: no TSX renders cost basis or unrealized P&L today, so only types change. The regression is a type-level and fixture test. see § AC pressure points
  - US-46.4 AC 2 trust is expressed on the overview as cost_basis_trust; ImportedPosition carries null-means-unavailable with no per-position trust field. see § AC pressure points
  - The (X+Y)+X doubling is already in stored legacy combined snapshots and in today's Dashboard; legacy detection is a heuristic on repeated account_id parts and can miss other malformed cases. see § Saved-node re-derive
  - Legacy nodes are re-derived in memory on every load, one exposure-engine call per legacy node; restore latency grows with workspace depth. Write-back was rejected to keep the change reversible.
  - A dirty working draft is not carried across add-statement (the add starts from the imported base node); variant nodes derived from a legacy doubled base are not repaired.
  - POST /portfolios/import/combine-snapshots keeps its route tests but loses its only in-app caller; left in place as a published contract. Candidate register row.
  - If H-3 is declined, a multi_broker legacy snapshot containing Freedom24 cannot attribute the fabricated basis to VTI; the recommended rule nulls all positions of that snapshot, which over-nulls stated IB values.
  - US-46.3 carries 15 ACs and US-46.1 12; combined with the shared re-derive step, FE-1 and FE-2 are large orders and may need a PARTIAL and a follow-up dispatch.
  - Replay window after F1 is 8 valuation days (D-4). Expected values in US-46.2 AC 6-13 come from sliced frozen prices; the human re-reads the regenerated golden before accepting it.
  - Guardrail 1: E1-E4 land in the docs close-out after the gates. Backend lanes must read the methodology sections first, and quant-audit should read the E2 and E4 text with the code.

## Orchestrator brief
- Decision: ONE merge source. New service build_combined_import_bootstrap (combine, exposure, admission roll-up) behind new route POST /portfolios/import/analyze-combined; the desktop overlay is retired. Both upload and add-statement cross it.
- Decision: combine FLAT from constituent snapshots; desktop persists importedConstituents. Verified: chained (IB+ESPP)+IB doubles IB today. Backend also refuses a combined input that shares an account with another input.
- Decision: admission roll-up is engine logic; ImportAdmissionSummaryV1 gains optional rollup with per-constituent evidence; the frontend renders it and never computes it.
- Decision: cost basis and unrealized P&L are null (unavailable); PortfolioOverview gets cost_basis_trust; aggregates null if any input null; EnrichedPosition is removed.
- Decision: ONE shared saved-node re-derive step in the desktop (FE-2), in memory on every load for nodes without derivationVersion; no write-back.
- BLOCKER for D-7/D-5 (partial): stored add nodes lack constituents, and the fabricated FF cost basis is inside the stored snapshot. US-46.3 AC 13-14 and US-46.4 AC 11 need human rulings H-2 and H-3. US-46.1 AC 10-12 are unblocked.
- Lane split: BE-1, BE-2, BE-3, FE-1, [H-1 golden recapture, human, FMP_API_KEY], T-1, T-2, FE-2, T-3, docs close-out; BE-4 scrub is gated on H-3.
- Full suite is red from BE-2 until H-1 (frozen market data lacks the new FF window); lanes run targeted commands only.
- Sections: Contract · Reuse and retirements · Saved-node re-derive · Lane split · Human-run steps · Decisions engineers must not make · Docs assignment · AC pressure points.
- Blocks dispatch: nothing for BE-1..BE-3 and FE-1. H-2, H-3 gate BE-4 and the legacy parts of FE-2.

## Contract

Source of truth is `services/quant-engine/app/schemas/`; every change is mirrored in `apps/desktop/src/features/portfolio/types.ts` or `workspaceTypes.ts` and in `docs/contracts/` in the same pass.

**C1. `ImportedPosition` (schemas/imports.py) — nullable cost basis.**

| Field | Python (new) | TS (types.ts:37-39, already) | Meaning |
|---|---|---|---|
| `cost_basis` | `float \| None = None` | `cost_basis?: number \| null` | statement-stated broker value; null = unavailable |
| `unrealized_pnl` | `float \| None = None` | `unrealized_pnl?: number \| null` | same |

No per-position trust field: null is the unavailable rung, stated in `imports-fields.md`. Never derived from market value, close price, quantity x price or trade history, never zero-filled. `close_price` stays required (its own fabrication in the snapshot builder is out of scope).

**C2. `PortfolioOverview` (schemas/reconciliation.py) — nullable aggregates plus a trust marker.**

| Field | Python (new) | TS (types.ts, new) |
|---|---|---|
| `total_cost_basis` | `float \| None` | `total_cost_basis?: number \| null` |
| `total_unrealized_pnl` | `float \| None` | `total_unrealized_pnl: number \| null` |
| `top_positions` | `list[dict[str, float \| str \| None]]` (only `unrealized_pnl` may be None) | `Array<{ symbol: string; market_value: number; weight: number; unrealized_pnl: number \| null }>` |
| `cost_basis_trust` | `Literal["stated", "unavailable"] = "stated"` | `cost_basis_trust?: 'stated' \| 'unavailable'` (optional: persisted overrides pre-date it) |

- Rule: `total_*` is None when any position's value is None; `cost_basis_trust = "unavailable"` exactly then. `"stated"` means every contributing value is statement-stated broker truth. Never `withheld` or `degraded`. No positions gives 0.0 as today.
- A `model_validator(mode="after")` on PortfolioOverview rejects `"stated"` while either total is None.
- `top_positions` stays a dict list because `exposure_engine._coerce_concentration_item` reads it as dicts; do not introduce a typed item model.
- The IB golden overview gains exactly one additive key (`cost_basis_trust: "stated"`); no value moves.

**C3. Admission roll-up (schemas/import_bootstrap.py) — additive, schema_version unchanged.**

```python
class ImportAdmissionConstituentV1(BaseModel):
    origin: Literal["statement", "carried"]      # carried = evidence recorded earlier (legacy nodes only)
    statement_ids: list[str] = []
    source_names: list[str] = []
    decision: ImportAdmissionDecision
    trust_level: ImportAdmissionTrustLevel
    checks: list[ImportAdmissionCheckV1]

class ImportAdmissionRollupV1(BaseModel):
    rule: Literal["weakest_of_constituents_and_combined_snapshot"]
    combined_snapshot_decision: ImportAdmissionDecision
    combined_snapshot_trust_level: ImportAdmissionTrustLevel
    constituents: list[ImportAdmissionConstituentV1]   # input order, one per input snapshot, then one per carried summary

class ImportAdmissionSummaryV1:                        # existing fields unchanged
    rollup: ImportAdmissionRollupV1 | None = None
```

- Top-level `decision` and `trust_level` become the weakest across the combined-snapshot recompute, every constituent and every carried summary. Top-level `checks` stay the combined snapshot's own checks, so existing consumers keep their meaning.
- Ladders: decision admitted < degraded < withheld; trust verified < degraded < withheld < unavailable; weakest = highest rank.
- `rollup` is None for a single input with no carried evidence. That keeps IB2026 alone degraded and ESPP2026 alone admitted/verified (US-46.3 AC 10).
- TS mirror (types.ts:1183): `rollup?: ImportAdmissionRollup | null` with `ImportAdmissionConstituent { origin: 'statement' | 'carried'; statement_ids: string[]; source_names: string[]; decision; trust_level; checks: ImportAdmissionSummaryV1['checks'] }` and `ImportAdmissionRollup { rule: 'weakest_of_constituents_and_combined_snapshot'; combined_snapshot_decision; combined_snapshot_trust_level; constituents: ImportAdmissionConstituent[] }`.

**C4. Combined bootstrap route (schemas/import_bootstrap.py, api/routes/imports.py) — new.**

```python
class CombinedImportBootstrapRequest(BaseModel):
    snapshots: list[ImportedPortfolioSnapshot] = Field(min_length=1)
    benchmark_symbol: str = DEFAULT_BENCHMARK_SYMBOL
    symbol_overrides: dict[str, list[str]] = Field(default_factory=dict)
    carried_admissions: list[ImportAdmissionSummaryV1] = Field(default_factory=list)   # legacy nodes only
```

- `POST /portfolios/import/analyze-combined`, `response_model=ImportedBootstrapResponse`, ValueError -> HTTP 400 with `detail: str`. It lives on the existing `/portfolios/import` router, so there is no `main.py` registration change; the engineer confirms the router is already included.
- Response: `snapshot` is the flat combine of `snapshots`; `overview`, `lookthrough`, `lookthrough_sector_exposure`, `market_overlap`, `current_state_concentration`, `availability` come from `build_exposure_result` on that combined snapshot; `admission_summary` is the roll-up; `history_context` from the combined snapshot.
- `ImportedBootstrapResponse.constituent_snapshots: list[ImportedPortfolioSnapshot] = []` (TS `constituent_snapshots?: ImportedSnapshot[]`). Populated only by `analyze-upload` and `analyze` when more than one file was combined; empty for a single input and on `analyze-combined` (the caller already holds them).
- The existing `POST /portfolios/import/combine-snapshots` and `CombineImportedSnapshotsRequest` are unchanged and stay published.
- TS adapter: `analyzeCombinedImport({ snapshots: ImportedSnapshot[]; carriedAdmissions?: ImportAdmissionSummaryV1[]; benchmarkSymbol?: string }, apiUrlOptions?) => Promise<ImportedBootstrapResponse>` in portfolioAnalysisAdapter.ts, replacing `combineImportedSnapshots`. Non-ok responses throw `Error(detail)`.

**C5. Merge guards (services/statement_importer.py).**
- New fail-closed ValueError: an input whose `statements` span more than one distinct `account_id` (an already-combined snapshot) shares an account with another input. Reason: `_latest_snapshot_by_account` keys by the joined id `'A + B'`, which never equals `'A'`, so the same account is summed instead of replaced (probe: VUAA 160).
- New ValueError for a single stored snapshot whose combined `statement.account_id` has repeated ` + ` parts (a legacy snapshot already doubled by the chained merge).
- Position and cash merge: `_merge_terminal_positions` sums `cost_basis` and `unrealized_pnl` only when both are non-null, else None. Cash merge is untouched.

**C6. Desktop persistence (workspaceTypes.ts `ImportedNodeSource`).**

| Field | Type | Notes |
|---|---|---|
| `importedConstituents` | `ImportedSnapshot[]` optional | individual input snapshots; set on new root imports (from `constituent_snapshots`, or `[snapshot]`) and new add nodes (parent list plus the new snapshot). Absent on legacy nodes and on nodes derived from a stored combined snapshot. |
| `derivationVersion` | `number` optional | 1 for anything built by `analyze-combined`; absent means legacy, re-derived in memory on load |

- `sanitizeImportedNodeSource` and `buildPersistedImportedSource` in portfolioWorkspaceStorage.ts must carry both fields. The sanitizer is a whitelist and would drop them silently on the first read.
- No IndexedDB version bump: no new store or index.

**C7. Freedom24 ledger contract (importers/freedom24.py).**
- Trade date = the first 10 characters of the Transactions record's trade-date cell (pypdf offset +9, not settlement +10); must match `\d{4}-\d{2}-\d{2}` or the record is skipped (resilience rule); no substitute date.
- `_parse_transactions(page_texts)` and `_parse_cash_movements(page_texts)` lose the `grouped_trade_date` parameter. `_parse_commissions`, `_statement_grouped_date` and `GROUPED_ENTRY_DAY` are deleted, so no period FEE entry exists; each trade's `fee` stays on its row and `net_amount = gross - fee`.
- `statement_totals` (including `commissions_total`) is untouched (F8 out of scope).
- Positions: `cost_basis=None`, `unrealized_pnl=None`; the `trade_delta` cost derivation is deleted.

**Contract docs.** Create `docs/contracts/imports-fields.md` (C1, C2, C4 response additions, C5 merge rule, C6 persistence, null = unavailable). Update `import-admission-fields.md` (C3), `dashboard-fields.md` § Combine Imported Snapshots (US-40.2) (consumer flow changed, 400 now publishes nothing), `system-architecture.md:34` (route list).

## Reuse and retirements

**Reuse (named, not "existing patterns").**
- Backend: `combine_imported_snapshots` and its helpers stay the only merge; `build_import_admission_summary` is called once per constituent and once on the combined snapshot; `build_exposure_result`, `derive_analysis_window`, `build_history_context` are called on the combined snapshot exactly as `build_import_bootstrap_from_snapshot` does; `_statement_ids` and `_source_names` in import_admission.py feed constituent provenance; `_compose_import_bootstrap_response` takes the admission summary as a parameter instead of computing it.
- Backend seam: new `build_combined_import_bootstrap(snapshots, benchmark_symbol, symbol_overrides, carried_admissions=())` in import_engine.py. `build_import_bootstrap(paths, ...)` becomes "import each path, then call the seam" and sets `constituent_snapshots` when more than one. Single input with no carried evidence must equal today's `build_import_bootstrap_from_snapshot` output.
- Frontend: `projectImportedBootstrap`, `buildPortfolioSnapshotFromAnalysis`, `saveImportedSnapshotNode`, `buildPersistedImportedSource`, `getEffectiveNodeImportSource`, `resolveEffectiveHistorySource`, `mergeHistoryContext` (kept as is), `runExposureEngine` (Exposure for a combined node still runs the request path over the PortfolioSnapshot built from the combined response), `CardShell`, `EmptyState`, and `CheckRow` in ImportAdmissionReviewCard.tsx for the constituent rows.
- Test helpers: `statement_truths.py` (IB2026 pinned values), `_statement_fixtures.py`, `fixtures.py`; in App.test.tsx `mockImportedWorkspace`, `installFetchMock`, `jsonResponse`, `requestJsonBody`.

**Retired or removed.**
- `overlayImportedSnapshot` in portfolioSnapshot.ts and its tests (the US-14.1 overlay tests); the desktop no longer merges holdings. Same-symbol summing across distinct accounts is preserved by the backend merge plus `normalizePortfolioSnapshot`.
- `combineImportedSnapshots` in portfolioAnalysisAdapter.ts (knip); replaced by `analyzeCombinedImport`.
- `EnrichedPosition` (schemas/reconciliation.py), `build_enriched_positions` (analytics/performance.py) and its re-export in analytics/portfolio_imports.py. No production caller and no test caller; nulling it would keep dead code.
- `_statement_grouped_date`, `GROUPED_ENTRY_DAY`, `_parse_commissions`, the `trade_delta` cost branch in freedom24.py.
- Changed rather than removed: `normalizePortfolioSnapshot` dedupes by symbol and currency (was symbol only), so two currencies of one symbol are never summed (US-46.1 AC 8).
- Kept: `ledger.py` section-role entry `"Commissions"` (harmless registry key); `mergeHistoryContext`; the `/combine-snapshots` route.

## Saved-node re-derive (D-5, D-7)

**What saved workspaces actually store** (read from portfolioWorkspaceStorage.ts, historySource.ts, App.tsx:767-809):
- Root: `workspace.source.historySource.importedHistorySnapshot` = the first import's full `ImportedSnapshot` (for a multi-file first import, the combined one), plus `importedExposureOverride` and `admissionSummary`.
- Add node: `node.source.historySource.importedHistorySnapshot` = the chained backend combine of (base combined, new file) or null when the combine failed; `admissionSummary` = the added file's own admission; `portfolioSnapshot` = the client overlay (the doubled one).
- Not stored: the per-file constituent snapshots of add nodes. Not stored: any per-constituent admission other than that per-node summary.
- Also persisted: `WorkingDraft.portfolioSnapshot`, a clone of the node snapshot, so a clean draft carries the doubled values too.

**Verdict per story.**
- US-46.1 AC 10-12: unblocked. The stored combined snapshot of IB2026 added onto IB2026 is already the backend combine (18 positions, 62,843.22, VUAA 80), so re-analysing it fixes Exposure. A snapshot doubled by the chained merge is detected by the C5 guard and takes the AC 12 path.
- US-46.3 AC 13-14: BLOCKED as worded. "Recompute from stored statements" cannot give each statement's own admission for an add node. Proposed reading (needs H-2): the D-3 rule over the persisted per-node admissions on the lineage root..node (each is one file's own engine-computed admission) plus the recompute on the stored combined snapshot. They are passed as `carried_admissions`, so the engine still does the roll-up. A node on the lineage with a null admission makes the node non-re-derivable (AC 15 path). For the fixture pairs this gives degraded/degraded with constituent labels. If H-2 is declined, every legacy multi-statement node takes the AC 15 path.
- US-46.4 AC 11 / D-5: BLOCKED. The fabricated 3,018.96 and 0.00 are stored inside `ImportedSnapshot.positions`, so re-deriving the overview from the stored statement reproduces them. Options for H-3: (a) recommended, a documented scrub in the combined bootstrap service that nulls `cost_basis` and `unrealized_pnl` of every position in a stored snapshot whose statements include a `freedom24` importer (Freedom24 never states either, so this is exact for a single-broker Freedom24 snapshot and over-nulls IB values in a multi_broker one; the aggregate is unavailable anyway); (b) accept stale values with a disclosure and amend AC 11.

**Decision: one shared step, not three.** T-46.1.3, T-46.3.3 and the persistence half of T-46.4.3 all rebuild the same object (a node's portfolio snapshot, exposure override and admission summary) from the same stored inputs, through the same route. Three passes would fetch three times and could disagree. It lives in a new `apps/desktop/src/app/rederiveSavedNodes.ts`, called from `restoreImportedWorkspaceFromPersistedState` in App.tsx (single choke point; `handleExposureSnapshotChange` then reads already-derived state).

Behaviour:
1. A node is legacy when its `ImportedNodeSource.derivationVersion` is undefined (root: `workspace.source`; add nodes: `node.source`). Variant nodes are not touched.
2. Derive legacy nodes in ancestor-first order. Input: `snapshots = [stored importedHistorySnapshot]`, `carried_admissions` = persisted admission summaries on the lineage (add nodes only), call `analyzeCombinedImport`.
3. On success, in memory only: `portfolioSnapshot = buildPortfolioSnapshotFromAnalysis(response, sourceFileNames)` keeping the node's `importedMeta.sourceFileNames` and `importedAt`; `importedExposureOverride` (root only, as today), `admissionSummary` and `historySource.importedHistorySnapshot` from the response. A clean `WorkingDraft` whose `baseNodeId` is the node is re-cloned from it; a dirty draft is left alone.
4. On failure (kind is not `imported_replay`, snapshot null, HTTP 400 from the guards, a missing lineage admission): the node is returned with `portfolioSnapshot = null`, `admissionSummary = null`, `importedExposureOverride = null` (in memory only) and the server `detail` goes to the existing `importError`. Old figures are never shown as current (US-46.1 AC 12, US-46.3 AC 15).
5. No write-back to IndexedDB. Loading is deterministic from stored inputs, so repeated loads give the same figures (US-46.1 AC 11), and nothing is destroyed. New saves stamp `derivationVersion = 1` and skip the step.

## Lane split

Contracts before consumers, implementation before tests. Every lane is read-only on files outside its fence. No lane commits or runs the full suite before H-1. Engineers do not edit tests; the known red tests they leave are listed for T-1.

**BE-1 — combine, admission roll-up, route** (backend). Tickets: T-46.1.1 (backend half), T-46.3.1.
- Files: `app/schemas/import_bootstrap.py`, `app/services/statement_importer.py` (C5 guards only), `app/services/import_admission.py`, `app/services/import_engine.py`, `app/api/routes/imports.py`.
- Read first: methodology § Multi-Statement Snapshot Merge, § Import admission rule (guardrail 1).
- Build C3, C4, C5 guards, `build_combined_import_bootstrap`, roll-up ranks, `constituent_snapshots` on the upload path.
- Verify: `cd services/quant-engine && python -m pytest app/tests/test_routes.py app/tests/test_import_admission.py app/tests/test_importer.py -k "combine or admission or bootstrap or analyze"`; then a scratch probe that `analyze-combined([IB2026, IB2026])` returns 18 positions, raw MV 62,843.22, VUAA 80, USD cash 146.07, and `[IB2026, ESPP2026, IB2026]` returns IB unchanged.

**BE-2 — Freedom24 dates and single commission** (backend). Ticket: T-46.2.1.
- Files: `app/importers/freedom24.py` (dates, commission, C7 minus positions).
- Verify by scratch probe (existing test pins are stale until T-1): ledger dates are exactly {2026-03-31, 2026-04-01, 2026-04-07}; three trades dated 2026-04-07 with fees 2.56, 2.12, 2.08; total fee 6.76; ledger cash roll-forward 52.04. Also `python -m pytest app/tests/test_importer.py -k "freedom24"` and report the expected failures at `:288` and `:332`.

**BE-3 — cost basis unavailable** (backend, schema first). Tickets: T-46.4.1 (backend half), T-46.4.2.
- Files: `app/schemas/imports.py`, `app/schemas/reconciliation.py`, `app/analytics/overview.py`, `app/analytics/performance.py`, `app/analytics/portfolio_imports.py`, `app/services/statement_importer.py` (`_merge_terminal_positions` only), `app/domain/ledger.py` (opening-lot estimate guarded on non-null basis), `app/services/portfolio_snapshot_builder.py`, `app/importers/freedom24.py` (positions only).
- Read first: methodology § Importer resilience rule, § Multi-Statement Snapshot Merge (null propagation).
- Verify: `cd services/quant-engine && python -m pytest app/tests -k "overview or importer or ledger or snapshot_builder" -x`, then `python scripts/detect_deadcode.py --strict` from the repo root. Report that IB2026 totals stay 62,255.14 / 3,491.53 and FF2026 totals are None.

**FE-1 — add-statement flow, types, admission card** (frontend). Tickets: T-46.1.1 (frontend half), T-46.1.2, T-46.3.2, T-46.4.1 (frontend half), T-46.4.3 (rendering half).
- Files: `features/portfolio/types.ts`, `workspaceTypes.ts`, `portfolioAnalysisAdapter.ts`, `portfolioSnapshot.ts`, `ImportAdmissionReviewCard.tsx`, `app/App.tsx` (add and replace branches of `processImportedFiles` only), `app/portfolioWorkspaceStorage.ts`.
- Build: mirrored types (C2, C3, C4, C6); `analyzeCombinedImport`; add flow = `snapshots = [...(base.importedConstituents ?? [base.importedHistorySnapshot]), newSnapshot]`, `carriedAdmissions = base.importedConstituents ? [] : [base.admissionSummary]`, then node snapshot from `buildPortfolioSnapshotFromAnalysis(response, ...)` with `importedAt` set to the new statement's and `sourceFileNames` the union; persist `admissionSummary = response.admission_summary`, `importedHistorySnapshot = response.snapshot`, `importedConstituents`, `derivationVersion: 1`; replace-import stamps the same fields. On any failure or a base with no stored replay snapshot: publish nothing, save nothing, keep the prior portfolio, show `importError`. Card renders the roll-up (rule text, combined-snapshot labels, each constituent's labels and checks). Delete `overlayImportedSnapshot` and `combineImportedSnapshots`. `normalizePortfolioSnapshot` dedupes by symbol and currency.
- Call the `ui-polish` skill before touching the card; the design-system audit test enforces it.
- Verify: `cd apps/desktop && npx tsc --noEmit`; `npx vitest run src/features/portfolio/ImportAdmissionReviewCard` plus the card's audit test. Existing App and overlay tests are expected red until T-3.

**H-1 — golden recapture** (human). See § Human-run steps. Runs after BE-2 and BE-3 and before T-2. Because the TS golden is regenerated by the first step of `run_all_tests.py`, its `satisfies ImportedDashboardSource` needs FE-1's types first.

**T-1 — backend regression tests** (test). Tickets: T-46.1.4 (backend), T-46.2.2 (importer part), T-46.3.4 (backend), T-46.4.4 (backend). After BE-1..BE-3.
- Files: `app/tests/**`.
- Must include: `combine(S,S) = S` property on IB2026; `analyze-combined` route on the real IB2026.csv and ESPP2026.pdf (numbers from `statement_truths.py`); flat `[IB, ESPP, IB]` equals `[IB, ESPP]` positions for IB; chained-input refusal; the five fixture pairs' labels; the synthetic offsetting-delta pair on two distinct accounts (falsifies recompute-only); superseded same-account case; multi-file upload and add path give the same decision, trust and constituent set; refused combine returns 400 and no summary; Freedom24 items in US-46.2's test plan including the unparseable-trade-date synthetic fixture; the `test_importer.py:288` pin and `:332` call updated; cost basis: FF2026 VTI null, overview totals null with `cost_basis_trust`, IB unchanged, IB+FF null, request-path builder null plus a grep-style guard that no `cost_basis = market_value` remains, merge sums only when both non-null, no opening-lot estimate on null, Dashboard and Risk outputs for IB unchanged.

**T-2 — golden-dependent tests** (test, after H-1). Tickets: T-46.2.2 (dashboard part), T-46.2.3. Backend dashboard-history test pinning US-46.2 AC 6-13 on frozen prices; review of the regenerated golden against AC 6-13 (IB block diff is only the additive key); frontend golden-driven FF tests in `App.test.tsx` updated.

**FE-2 — shared saved-node re-derive** (frontend, after FE-1 and T-1). Tickets: T-46.1.3, T-46.3.3, T-46.4.3 (persistence half).
- Files: new `app/rederiveSavedNodes.ts`, `app/App.tsx` (restore path only).
- Build the behaviour in § Saved-node re-derive. The `carried_admissions` lineage path is built only after H-2; the scrub call site only after H-3 (BE-4).

**BE-4 — legacy Freedom24 cost-basis scrub** (backend, gated on H-3). Files: `app/services/statement_importer.py`, `app/services/import_engine.py`. Called at the top of `build_combined_import_bootstrap`; idempotent on fresh data. Skipped entirely if H-3 chooses option (b).

**T-3 — frontend regression tests** (test, after FE-1, FE-2). Tickets: T-46.1.4 (frontend), T-46.3.4 (frontend), T-46.4.4 (frontend).
- Files: `src/**/*.test.{ts,tsx}`, `src/test/**` (not `dashboardGoldens.ts`).
- Replace the overlay tests in `portfolioSnapshot.test.ts` with a currency-aware dedupe test; App-level add-statement tests (IB then IB; IB then ESPP asserting degraded/degraded as the user reads it; refused combine by base-currency mismatch and by missing account id leaves the prior portfolio, saves no node, shows the error); repoint every `combine-snapshots` mock in `App.test.tsx` (comment at :927, `installUS402FetchMock` at :958-981 and the mockResolvedValueOnce chains) to `analyze-combined`; stamp `derivationVersion` in the `buildImportedSource` helper for non-legacy fixtures; legacy fixtures built from real engine output (doubled IB+IB node, IB+ESPP node persisted as admitted/verified, FF node with 3,018.96 / 0.00, a node with null stored snapshot); repeated-load stability; sanitizer round trip keeps `importedConstituents` and `derivationVersion`; a type-level test that `total_unrealized_pnl` accepts null.
- Falsifier: an App test whose mocked `analyze-combined` response differs from any client-side sum, asserting the UI shows the response and that the request body carried both constituents.

**Docs close-out** (docs, after all gates PASS). Tickets T-46.1.5, T-46.2.4, T-46.3.5, T-46.4.5; see § Docs assignment.

## Human-run steps

**H-1 Golden refresh (needs `FMP_API_KEY` and network).**
- Why: after BE-2 the FF replay requests 2026-03-31 to 2026-04-11, which `golden_market_data.json` does not hold, so `FrozenMarketData` raises `FrozenMarketDataMiss` by design.
- Before H-1: BE-1..BE-3 and FE-1 lanes run targeted commands only (listed per lane). They do not run `run_all_tests.py` or `mcp__project__run_tests(scope="full")`, which fail at the golden step from BE-2 on. They do not hand-edit `dashboardGoldens.ts` or `golden_market_data.json`, and do not call `reset_goldens`.
- Step 1: `cd services/quant-engine && FMP_API_KEY=<key> python -m app.scripts.export_dashboard_goldens --capture --allow-smaller-capture`. FF series shrink from 90 to 9 rows per symbol and are expected to trip the capture-regression guard; using the override is the human's call.
- Step 2: `python -m app.scripts.export_dashboard_goldens` (offline) regenerates `dashboardGoldens.ts`. One regeneration covers F1, F7 and F4.
- Step 3: the human reads the FF block against US-46.2 AC 6-13 (window 2026-03-31 to 2026-04-10, 8 states, start 2,955.01, end 3,071.00, TWR and MWR 3.81%, benchmark 4.48%, excess -0.67pp, gain 112.48, trust degraded, adjustment +3.51) and confirms the IB block differs only by the added `cost_basis_trust` key. A value that moved is re-read before it becomes the golden.
- After H-1: T-2 runs; the first full `python scripts/run_all_tests.py` happens after FE-1 (types) and T-1 (updated pins). The integration gate runs the full suite only from there.
- If the human prefers not to capture: the alternative of slicing the existing capture by hand fabricates a capture record and is not offered.

**H-2 (D-7, US-46.3 AC 13-14).** Confirm the lineage-evidence reading of "recompute from stored statements". Default: proceed as designed. Gates the `carried_admissions` half of FE-2.

**H-3 (D-5, US-46.4 AC 11).** Choose scrub (a, recommended) or disclosure (b). Gates BE-4 and the F4 half of FE-2 verification.

## Decisions engineers must not make

- Weakest = highest rank on the ladders in C3. Constituents listed in input order; carried ones after statements. Roll-up compares decision and trust only; no numeric tolerance changes.
- A refused combine (HTTP 400) publishes nothing on any surface: no node saved, no state replaced, prior portfolio stays, `importError` shows the server `detail`. No fallback to "keep merged positions".
- Never chain a combined snapshot into a second combine when constituents exist. A base without `importedConstituents` is passed as one input plus its own summary as carried evidence.
- A base with no stored `imported_replay` snapshot cannot be added to: refuse with a disclosure rather than adopting the new file alone (this reverses the App.tsx:784-786 behaviour).
- Null means unavailable everywhere; a missing cost basis is never rendered or serialised as 0. `cost_basis_trust` is `stated` or `unavailable` only. Sums keep `round(x, 2)`.
- The frontend does not compute, lower or raise any label. `history_context` merging stays `mergeHistoryContext` as is.
- Per-constituent admission uses `build_import_admission_summary` unchanged; no single-statement rule changes, no rung is raised (US-46.3 AC 9).
- Freedom24: trade date only; skipped record when unparseable; no synthetic date; fee stays on the trade row; do not touch `statement_totals` or F8.
- Dedupe key in `normalizePortfolioSnapshot` is symbol plus currency. Same-symbol, same-currency rows from distinct accounts still sum (US-14.1 preserved).
- Do not touch `close_price` fabrication in the snapshot builder, the IB importer's malformed-Cost-Basis drop (D-8), the D-4 window anchor, F10, F12, F13 or N1.
- Exposure and admission read only `cash_total`, `stock_total`, `ending_nav` and `fx_rates` from merged `statement_totals` (checked in import_admission.py and analytics/currency.py); they must keep not reading `starting_nav`, flow totals or the compounded TWR (US-46.1 out-of-scope note).

## Docs assignment

- T-46.1.5: E3 into § Multi-Statement Snapshot Merge plus the flat-combine rule, the chained-input guard, and edits to the lines that name `combine-snapshots` (2332-2333, 2405); `dashboard-fields.md` § Combine Imported Snapshots; `system-architecture.md:34`.
- T-46.2.4: E1 (Importer resilience rule, Freedom24 bullet), the single-charge commission rule, and a register row for the D-4 period-start anchoring.
- T-46.3.5: E2 after § Import admission rule; roll-up section in `import-admission-fields.md`.
- T-46.4.5: create `docs/contracts/imports-fields.md` (C1, C2, C4, C5, C6); E4 as a new section after Truth Classes.
- Register rows to add or close: D-8 IB malformed Cost Basis cell drop; `combine-snapshots` route without an in-app caller; snapshot-builder `close_price` fabrication; legacy chained-combine doubling heuristic; status of F1, F2, F3, F4, F7.

## AC pressure points

- US-46.4 AC 7: after US-46.1 the added node's Exposure holdings come from the statement-path combine, so IB2026 re-added shows stated cost basis, not unavailable. The AC is still exercised by the request-path builder test and by any draft or variant snapshot. Recommend the reviewer reads AC 7 against those; the human confirms.
- US-46.4 AC 9: nothing in `apps/desktop/src` renders cost basis or unrealized P&L (grep of `total_cost_basis`, `total_unrealized_pnl`, `unrealized_pnl`, `cost_basis` shows types.ts and one fixture only). The falsifier is a type-level test, not a render test.
- US-46.4 AC 2: expressed as `overview.cost_basis_trust == "unavailable"` for FF2026; position-level trust is the null itself.
- US-46.1 AC 6: Exposure and Dashboard both consume the same `analyze-combined` response snapshot; Exposure's engine still runs over the PortfolioSnapshot request path, as it does for added nodes today.
- US-46.1 AC 1-4 chained variant: the ACs pin IB+IB only; the flat combine and C5 guard are additional protection and are tested in T-1.
- US-46.3 AC 13-15 and US-46.4 AC 11: gated as described in § Saved-node re-derive.
