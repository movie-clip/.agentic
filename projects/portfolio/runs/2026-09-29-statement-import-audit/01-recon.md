REPORT 2026-09-29-statement-import-audit/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only recon; order verification was NONE

contract_notes:
  - docs/contracts/ has no field contract for services/quant-engine/app/schemas/imports.py (ImportedPortfolioSnapshot, ImportedPosition, ImportedLedgerEntry, ImportedStatementTotals); only import-admission-fields.md exists, so the import boundary itself has no backend-TS-UI traceability doc.
  - apps/desktop/src/features/portfolio/types.ts:41-42 types ImportedSnapshot.ledger_entries and .instruments as Array<unknown>; the TS mirror does not carry ImportedLedgerEntry or ImportedInstrument shapes.
  - docs/architecture/testing-architecture.md:104-108 names docs/IB2026.pdf as an active reference (file does not exist; canonical is docs/IB2026.csv per :144) and :59 cites a tech-debt-register "Epic 24" section that the register no longer contains.
  - docs/product/current-product-state.md:12 says "Import or append Interactive Brokers PDF/CSV statements"; Freedom24 and ESPP importers are routed (statement_importer.py:37-47) and route-tested but not listed as shipped scope.

pack_corrections:
  - none

handoff:
  - Canonical re-derivation fixture is docs/IB2026.csv (period 2026-01-01 to 2026-08-28, account U8516450); pinned expected values live in services/quant-engine/app/tests/statement_truths.py (totals :73-85, FX :88, positions :45-52, ledger counts :61-69). See § Fixtures and test coverage.
  - Highest-value numeric checks for the next lane: (a) position market_value sum in base currency vs statement stock_total 65746.67; (b) implied FX (EURUSD 1.1583, GBPUSD 1.3535) from Open Positions Total pairs; (c) ledger counts BUY 93 / SELL 77; (d) LQQ 200:1 split in the unparsed Corporate Actions section (IB2026.csv:585). See § Suspicions.
  - Freedom24 (docs/FF2026.pdf) and ESPP (docs/ESPP2026.pdf) are PDF-layout parsers with fixed offsets and hard-coded literals; re-deriving them needs a PDF text extractor, not the CSV. See § Broker parser specifics.
  - Sections of docs/finance/financial-methodology.md that govern this pipeline: Trust... (import admission rule L55, importer resilience L59-92, section-role registry L94-118, reconciliation scoping L120-134), Share-Unit Discontinuity L335, Sector/Industry L1322, Base-currency weighting L1744, Multi-Statement Snapshot Merge L2328, FX Conversion Fallback L2414. See § Pipeline map.
  - The suspicion that build_reconciliation_summary has no production caller (S-02) and that multi-currency statements cannot reach admission `verified` (S-24) need a runtime check by a lane that can run code; this scout could not.

skill_calls:
  - fmp-data — not called, order excluded market-data client internals; only the import-to-sector-resolution call sites were read.

risks:
  - Not read (outside the import path or excluded by non_goals): analytics/reconciliation.py, analytics/risk.py build_lookthrough_exposure, instruments/etf_sector_resolution.py, engine/portfolio_state.py replay, schemas/import_bootstrap.py, App.test.tsx and the other desktop tests beyond names/greps. "First consumer" beyond the bootstrap response (run-imported engines) is named, not traced.
  - S-02 rests on a repo-wide grep excluding tests/ that found no caller of build_reconciliation_summary other than a re-export in analytics/portfolio_imports.py; dynamic dispatch or a vulture allowlist entry was not checked.
  - S-24 (admission never `verified` for multi-currency statements) is inferred by reading import_admission.py:75-79,236,257,330,351 against statement_truths.py:37; not executed.
  - Freedom24 and ESPP behaviours were read from source only; the PDFs were not opened, so layout claims (page indexes, offsets) are as coded, not as observed.
  - Everything under Suspicions is a suspicion per the order, not a verified defect; several may be intended conventions documented in comments (e.g. absolute-value totals, US-14.1 summing on overlay).

## Orchestrator brief
- Pipeline is 12 stages: desktop pick (App.tsx:661) -> analyze-upload route (imports.py:71) -> format detection (statement_importer.py:19) -> 4 parsers -> combine (:66) -> bootstrap (import_engine.py:50) -> admission (import_admission.py:462) -> desktop projection/persist (IndexedDB).
- Parsers: IBKR CSV (canonical, docs/IB2026.csv), IBKR PDF, Freedom24 PDF, ESPP PDF; only IBKR CSV/PDF are advertised in current-product-state.md.
- Corporate actions are NOT parsed by any importer; the CSV has a Corporate Actions section (LQQ 200:1 split, IB2026.csv:585) and Forex trades that are dropped; splits are handled downstream by a price-ratio heuristic.
- Only tech-debt-register entry on import is the Medium "Currency provenance" row (portfolio_snapshot_builder.py); the snapshot builder also fabricates cost_basis, unrealized_pnl, quantity and importer (S-27).
- Persisted-import doc claims ("content-addressed, immutable", "no derived analytics persisted") are contradicted by the desktop code (S-34, D-01, D-02).
- Desktop has a second, different merge (overlayImportedSnapshot) that sums by symbol across accounts and currencies; backend combine replaces same-account (S-31).
- No blocker for dispatch; premise holds except that Freedom24/ESPP exist beyond the IBKR-only product doc.
- Section "Pipeline map": stage-by-stage table with file:line, inputs, outputs, truth class, methodology section.
- Section "Broker parser specifics": per-parser extraction rules, defaults and hard-coded literals.
- Section "Fixtures and test coverage": statements/fixtures inventory, tests per stage, gaps G-01..G-08.
- Section "Known debt and documented limitations": register and doc entries touching import.
- Section "Suspicions": S-01..S-36 with file:line, grouped by stage (silent default/drop/zero, sign, truth-class mixing).
- Section "Doc and code disagreements": D-01..D-07.

## Pipeline map

Legend: TC = truth class (BT Broker Truth, SA Snapshot Analytics, PI Persisted Imports, none = pre-truth). MD = methodology section in docs/finance/financial-methodology.md.

| # | Stage | Anchor | Takes in | Emits | TC | MD |
|---|---|---|---|---|---|---|
| 1 | File selection (Tauri dialog or hidden `<input>`) | apps/desktop/src/app/App.tsx:661 openImportPicker; :195-218 resolveTauriImportFiles (filters pdf/csv :203, empty file rejected :213); :849 input accept | user click | `File[]` | none | none |
| 2 | Upload form build + POST | App.tsx:141-153 buildImportFormData (MIME by extension :137; benchmark_symbol fixed 'SPY' :150; symbol_overrides fixed '{}' :19,:151); :716-823 processImportedFiles; :732/:746 fetch `/api/portfolios/import/interactive-brokers/analyze-upload`; Tauri 30 s timeout :23 | `File[]`, mode replace or add_snapshot | multipart request | none | none |
| 3 | Route: temp-file spool | services/quant-engine/app/api/routes/imports.py:71-101 (suffix default `.pdf` :89; temp files :90-93; cleanup in finally :99-101; ValueError -> 400 :97-98) | multipart, overrides JSON | temp paths handed to build_import_bootstrap | none | Accepted local file-read tradeoff: architecture.md L222 |
| 3b | Other import routes (not used by desktop upload) | imports.py:37 `/interactive-brokers` (import only), :49 `/combine-snapshots`, :59 `/analyze` (server-side path, `_resolve_statement_paths` :24-34 checks existence only), :104 `/analyze-snapshot` | JSON | ImportedPortfolioSnapshot or ImportedBootstrapResponse | BT (path routes) | Multi-Statement Snapshot Merge L2328 (combine) |
| 4 | Format detection / broker dispatch | services/statement_importer.py:19-52 import_statement: `.csv` -> IBKR CSV only (:22-26); `.pdf` -> try IBKR (:31-35, ValueError swallowed) -> Freedom24 (:37-41) -> ESPP (:43-47); other suffix ValueError (:27-28). Each `preview_*` is the detector: IBKR CSV needs BrokerName contains "Interactive Brokers" and Title == "Activity Statement" (importers/interactive_brokers_csv.py:180-195); IBKR PDF needs "Activity Statement" and "Open Positions" text (importers/interactive_brokers.py:84); Freedom24 needs "Freedom24" (freedom24.py:97); ESPP needs "YEAR-END INVESTMENT REPORT", "Participant Number:", "Stock Plan" (espp.py:43) | temp file path | one ImportedPortfolioSnapshot | BT | Importer resilience rule L59-92 |
| 5 | Parse (four parsers) | see § Broker parser specifics. Entry points: IBKR CSV importers/interactive_brokers_csv.py:447 import_statement; IBKR PDF importers/interactive_brokers.py:564; Freedom24 importers/freedom24.py:416; ESPP importers/espp.py:220 | text/CSV rows | ImportedPortfolioSnapshot (schemas/imports.py:93-105): statement, statements, statement_totals, instruments, cash_balances, positions, ledger_entries | BT | L59-92 (resilience, per-record skip), L120-134 (reconciliation scoping, implied FX) |
| 5a | Normalisation: symbols | IBKR: verbatim `Symbol` column (csv:272, :309); PDF open-positions regex `[A-Z0-9. ]+` (ib.py:228); instruments take first comma part of Underlying (ib.py:541); Freedom24 strips `.US` suffix (freedom24.py:36,178,254,394); ESPP hard-codes MSFT (espp.py:124). Downstream canonicalisation is in the registry, not the importer (registry.py:180 normalize_symbol -> core/symbols.py:132 canonicalize_symbol; rules :19-70) | raw tickers | ImportedPosition.symbol etc. | BT | none |
| 5b | Normalisation: currency, FX | Currency comes from the statement group heading/column. FX rates implied only from IBKR Open Positions `Total` pairs (csv:233-260, CSV) or a regex with literal `1.0353` (ib.py:174, PDF, EUR only); Freedom24/ESPP set `{"USDUSD": 1.0}` only (freedom24.py:109, espp.py:68). No importer converts amounts (L91-92). Conversion at read time: analytics/currency.py:55-81 (static period-end rate; missing rate -> carried unconverted and disclosed :73-77) | per-currency rows | ImportedStatementTotals.fx_rates | BT (rates), SA (conversion) | Base-currency weighting L1744; FX Conversion Fallback L2414; L128-134 |
| 5c | Normalisation: quantities, cost basis, cash | Quantity/cost_basis/close/market value/unrealized taken verbatim from Open Positions Summary rows (csv:263-291; ib.py:222-255); Freedom24 synthesises cost basis (freedom24.py:177-183); ESPP takes statement cost (espp.py:110-131). Cash: IBKR Cash Report per real currency, "Base Currency Summary" excluded (csv:406-425; ib.py:457-508); Freedom24 fixed page 9 (freedom24.py:207-232); ESPP core-fund value as ending cash (espp.py:134-137) | rows | ImportedPosition, ImportedCashBalance | BT | none |
| 5d | Normalisation: trades, fees, dividends, tax, interest, deposits | IBKR CSV trades: only `Order` discriminator and `Stocks` category (csv:300-337); BUY if qty>0 else SELL (:323); fee=abs(Comm/Fee) (:315); net=Proceeds-fee (:330). Dividends/Withholding/Interest/Fees via one shared function (csv:340-375); deposits by Settle Date (csv:378-403). PDF equivalents ib.py:262-454. Freedom24 grouped entries (freedom24.py:235-378). ESPP synthesised entries (espp.py:140-211) | rows | ImportedLedgerEntry (schemas/imports.py:77-90) | BT | L94-118 (section labels are provenance) |
| 5e | Corporate actions / splits | No importer parses them. Repo grep of importers/ for "corporate action"/"split" finds only string-split calls. IB2026.csv:584-587 carries `Corporate Actions` (LQQ split 200 for 1, quantity 199) and it is ignored by interactive_brokers_csv.py (no `_SECTION_` constant). Downstream: share-unit discontinuity heuristic engine/portfolio_state.py:65 with REPLAY_SHARE_UNIT_DISCONTINUITY_RATIO = 5.0 (core/constants.py:95) | n/a | n/a | BT to SA boundary | Share-Unit Discontinuity Withholding L335 |
| 6 | Vendor enrichment (Freedom24 only) | freedom24.py:454-467 calls instrument_enrichment.enrich_imported_instruments(snapshot, MarketDataService()) inside `except Exception: pass`; services/instrument_enrichment.py:54-100 overwrites description and instrument_type from FMP company profile for symbols not in INSTRUMENT_DEFINITIONS | ImportedInstrument | ImportedInstrument (vendor-derived fields) | BT + market data mixed | Sector/Industry L1322 (related) |
| 7 | Multi-file combine | statement_importer.py:55-63 import_statements -> :66-98 combine_imported_snapshots; sort :101-114; compat check (base currency, non-empty account_id) :130-147; totals merge :190-243; latest snapshot per account :256-266; positions merge :269-293; cash merge :296-311; instruments :314-332; ledger dedupe :335-360 | list of snapshots | one snapshot; statement.importer "multi_broker" if mixed (:80) | BT | Multi-Statement Snapshot Merge L2328-2412 |
| 8 | Ledger / domain semantics | domain/ledger.py:140-218 snapshot_to_ledger (section-role registry :46-64; evidence :143-154; classification :156-169; bucket :171-178; signed qty :180-187); :221-300 reconstruct_position_lots; :303-325 classify_opening_state | snapshot | LedgerRecord list (cash_effect = net_amount, :204) | BT (derived classification) | L94-118 |
| 9 | Instrument identity / sector | instruments/registry.py:325 attach_snapshot_metadata (static hit :341-349; imported ETF or equity -> classify_imported_instrument :232-323; no instrument -> sector None :366-374); equity sector via FMP gated by ISIN match instruments/equity_sector_resolution.py:66-95; identity flags services/instrument_identity.py:48-103 | snapshot.instruments + positions | Instrument metadata with classification_source | SA | Sector/Industry L1322-1739 |
| 10 | Trust / provenance labelling | services/import_admission.py:462-493 build_import_admission_summary: six checks (cash :82, symbol identity :187, positions market value :232, NAV :325, description consistency :392, ISIN consistency :423); decision `withheld` if any fail, `admitted/verified` only if all pass, else `degraded` (:471-480); tolerance absolute 0.01 (:15) | snapshot | ImportAdmissionSummaryV1 (read-only evidence) | BT evidence | Import admission rule L55-57 |
| 11 | Bootstrap response (first analytics consumer) | services/import_engine.py:14-17 build_import_bootstrap; :50-79 build_import_bootstrap_from_snapshot -> exposure_engine.py:45 build_exposure_result (-> analytics/overview.py:16 build_portfolio_overview; analytics/currency.py:119 total_base_market_value; build_lookthrough_exposure in analytics/risk.py; build_currency_exposure) + history_context_builder.py:7,20 + risk_summary stub with all None (:66-77) | snapshot | ImportedBootstrapResponse | SA over BT | Base-currency weighting L1744; Currency Exposure L1973 |
| 12 | Desktop projection and persistence | features/portfolio/importedBootstrapMapper.ts:34 projectImportedBootstrap; features/portfolio/portfolioSnapshot.ts:42 buildPortfolioSnapshotFromAnalysis (normalise :10-40); app/portfolioWorkspaceStorage.ts:95-176 createWorkspaceFromImport, :301-350 saveImportedSnapshotNode; app/portfolioDb.ts IndexedDB `portfolio-workstation` v18 (stores :4-8); add-statement branch App.tsx:767-809 (overlay portfolioSnapshot.ts:92-165; backend combine via portfolioAnalysisAdapter.ts:173 to `/combine-snapshots`) | bootstrap response | PortfolioSnapshot, workspace, root node, draft, plus importedHistorySnapshot (full engine snapshot) and importedExposureOverride | PI | Truth Classes L22-33 |

Notes on the first consumer: the immediate consumer in the import call is `build_exposure_result` (stage 11). On the desktop, the persisted `importedHistorySnapshot` is later fed back to the `run-imported` engines (dashboard_history, diagnostics; routes named in system-architecture.md L37-38) which run the ledger replay; that path was named but not traced.

## Broker parser specifics

IBKR CSV (`importers/interactive_brokers_csv.py`, US-28.1):
- Reader `_read_records` :109-136 tracks the current Header per section (mid-file Header restatement handled; `Trades` restates at IB2026.csv:250 and :488); rows shorter than header omit keys, extra cells dropped silently.
- `_parse_number` :143-149 rejects blank and `--`; every record parser wraps it and skips the record on ValueError (positions :288, trades :318, cash flows :357, deposits :389, cash :421).
- Statement totals :198-230: Change in NAV fields (:67-76) stored as `abs()` (:205); NAV section for cash_total/stock_total/TWR (:211-227).
- Positions :263-291: only `DataDiscriminator == Summary` and `Asset Category == Stocks`.
- Trades :300-337: only `Order` rows of `Stocks`; Forex rows (IB2026.csv:489) and any non-Stocks are skipped.
- Ledger sign convention: trade gross_amount = Proceeds (negative for buys); dividends/interest/fees carry the statement sign; `tax=abs(amount)` for Withholding Tax rows (:369); `fee=abs(amount)` for Fees (:368).
- Instruments :428-444 carry description, ISIN (`Security ID`), exchange, type; no currency.
- Statement identity :180-195; `import_statement` :447-486 raises only if the period is undetermined (:451) or the file is not an IBKR activity statement.

IBKR PDF (`importers/interactive_brokers.py`, pypdf text, regex):
- Preview :79-118 reads account/base currency/period from page 1; period only if a line starts "January " (:99); account must start "U" (:95).
- `_collect_section_lines` :185-219 slices sections by heading and stop-prefix list.
- Totals :133-182 via line regexes on page 1, `abs()` (:166); EUR rate only via a regex containing literal `1.0353` (:174).
- Positions :222-255, trades :262-348 (multi-line join), simple cash sections :351-415, deposits :418-454, cash balances :457-508, instruments :511-561.
- as_of_date falls back to `date(2025, 12, 31)` when the period is unparsed (:571).

Freedom24 (`importers/freedom24.py`, fixed page/line offsets):
- Page indexes 3/4/6/7/9 (:38-43) and start offsets 10/7/13/6/7 (:147, :210, :238, :286, :354).
- Position kept only if account == "trading", type == "funds", ending balance > 0 (:177); cost basis synthesised (:180-183).
- Trades grouped to the first day of the statement-start month (:46-51); currency hard-coded USD (:269).
- Cash movements accept only "Dividends" and "Taxes" labels (:292); commissions become one period-total FEE (:348-378).
- Totals regexes bind to "Net assets, USD" and "USD :" (:112-139).
- Base currency from "Commission currency" or default USD (:91,103).
- After import, FMP enrichment (:454-467).

ESPP (`importers/espp.py`, single-statement shape):
- Requires three marker strings (:43); period from page 1 (:46); base currency fixed USD (:55).
- `_normalize_number` :34-35 turns every "-" into "0".
- One position (MICROSOFT CORP (MSFT), :110-131) or ValueError; core cash from the FYIXX fund line (:99-107).
- Ledger: DEPOSIT plus BUY synthesised from the first "Employee Purchase" match (:140-173), tax (:176-192), dividends (:195-211), all dated at purchase date or period end.
- Totals :67-96; `deposits_total` = position cost basis (:92-93).

## Fixtures and test coverage

Statement inventory (docs/):
- `docs/IB2026.csv` - canonical current IBKR Activity Statement CSV, 2026-01-01 to 2026-08-28; refreshed every few weeks (testing-architecture.md:142-206). Sections present: Statement, Account Information, Net Asset Value, Change in NAV, Mark-to-Market, Realized/Unrealized, Cash Report, Open Positions, Trades (two headers), Corporate Actions, Deposits & Withdrawals, Fees, Dividends, Withholding Tax, Interest, Interest Accruals, Change in Dividend Accruals, Financial Instrument Information, Codes, Notes.
- `docs/U8516450_2022_2022.pdf`, `..._2023_2023.pdf`, `..._2024_2024.pdf`, `..._2025_2025.pdf` - legacy IBKR annual PDFs (frozen); 2025 is the PDF path fixture (`_statement_fixtures.py:17`), 2022-2024 appear in the multi-year combine test (`test_importer.py:210-236`).
- `docs/FF2026.pdf` (Freedom24) and `docs/ESPP2026.pdf` (ESPP; period January 1, 2025 - December 31, 2025 per test_importer.py:44) - frozen.
- `docs/IB2026.pdf` does not exist; `_statement_fixtures.py:18` and `test_importer.py:23-25` still resolve to it.
- Generated/frozen derivatives: `services/quant-engine/app/scripts/golden_market_data.json` (frozen market data), `apps/desktop/src/test/dashboardGoldens.ts` (generated), `app/scripts/export_dashboard_goldens.py`, `scripts/refresh_statement.py`, `app/tests/statement_truths.py` (importer-derived pins), `app/tests/fixtures.py` (synthetic snapshots).
- `dispute-letter.pdf` also sits under portfolio/ root (not a broker statement; unrelated).

Tests by stage (names only; bodies not audited):
- Route: `app/tests/test_routes.py` - missing path 404 (:33), combine (:67,:82), upload PDF (:125), missing files (:140), Freedom24 (:151), ESPP (:167), bad overrides JSON (:183,:196), analyze-snapshot (:246-325).
- Detection and dispatch: `test_importer_csv.py:333-353`, `test_importer.py:370`.
- IBKR CSV: `test_importer_csv.py` (identity :52-75, totals :76, FX :94, truths :102, positions :111-135, ledger counts :144, reconciliation :157-184, instruments :194, cash :210, failsafe :276-318, reader :372).
- IBKR PDF: `test_importer.py:95-170` (2025 real PDF; the two 2026 PDF tests are vacuous, see gaps), malformed-field degradation :339-368.
- Freedom24: `test_importer.py:258-336`, `test_freedom24_enrichment.py`.
- ESPP: `test_importer.py:37-76`.
- Combine: `test_importer.py:78-92, 186-256, 377-496` (three-broker, same-account latest-wins :461, missing account id :476-495).
- Ledger domain: `test_ledger_domain.py` (9 tests, includes the every-importer-section-registered guard), `test_ledger_replay_audit.py`.
- Admission: `test_import_admission.py` (17 tests :55-308).
- Identity and sector: `test_instrument_identity.py`, `test_registry_isin_integrity.py`, `test_instrument_registry.py`, `test_instrument_enrichment.py`.
- FX and base-currency: `test_currency_conversion.py`, `test_currency_exposure.py`.
- Statement refresh meta-test: `test_statement_refresh.py`.
- Desktop: `portfolioSnapshot.test.ts` (overlay cases :59-172, fxRates :175-197), `portfolioWorkspaceStorage.test.ts`, `importedBootstrapMapper.test.ts`, `portfolioAnalysisAdapter.test.ts`, `App.test.tsx`.

Coverage gaps (by name or absence found; not exhaustive):
- G-01: no test found that parses or asserts on the `Corporate Actions` section or `Forex` trades of IB2026.csv; the importer silently ignores both.
- G-02: `test_importer.py` uses silent `return` when a fixture is missing (:38-39, :82-83, :96-97, :110-111, :127-128, :146-147), against testing-architecture.md:93; `IB2026.pdf` is absent, so `test_preview_pdf_statement_extracts_core_metadata_for_2026` (:109) and `test_import_statement_2026_...` (:145) pass vacuously, and :32-34 checks only the extension.
- G-03: no CSV-specific upload-route test found in `test_routes.py` (PDF, Freedom24, ESPP only); temp-file cleanup and the temp `source_path` provenance (S-22) have no test found.
- G-04: desktop `overlayImportedSnapshot` tests cover same-symbol summing and IB->FF->ESPP; none found for same account across two periods, mixed currencies, base-currency mismatch, or fxRates carry-over.
- G-05: no test found that pins the multi-currency admission outcome for the canonical IB2026.csv (S-24); admission tests use single-currency fixtures.
- G-06: reconciliation (`build_reconciliation_summary`) is exercised only by tests (S-02).
- G-07: no test found for `snapshot_to_ledger` `cash_effect` when `net_amount` is None, nor for the None-to-0.0 cash merge (S-13).
- G-08: Freedom24/ESPP tests pin one frozen statement each; layout-drift behaviour for fixed offsets is covered only by the "skip malformed" unit test (`test_importer.py:307`).

## Known debt and documented limitations

- `docs/tech-debt-register.md` "Currency provenance" (Medium): `portfolio_snapshot_builder.py` assigns base or USD currency when a generic request omits a position currency; states "Imported broker statements are unaffected". This is the only open row that concerns import. Code anchor: portfolio_snapshot_builder.py:43.
- Same row's scope is narrower than the builder's other defaults (cost_basis, unrealized_pnl, quantity, importer, account_id; S-27).
- `docs/tech-debt-register.md` rows "Trust semantics" (withheld investor-economics/drawdown) and "Synthetic history" (coverage) touch downstream of import, not import itself.
- All other register rows are Rolling Factor Analysis findings (F2, F3, F5, F6, F8, F9, F10) or dependency advisories (FastAPI/Starlette; and a Medium row naming pypdf and python-multipart, which are import-adjacent: PDF parsing and multipart upload libraries); none concern the import pipeline logic.
- `docs/product/current-product-state.md:52-55`: import API accepts a user-selected filesystem path with no authentication; acceptable only while localhost single-user. `docs/architecture/system-architecture.md:222-235` restates it as an accepted tradeoff (`statement_path`/`statement_paths`, `_resolve_statement_paths` checks existence only; desktop upload does not use those routes).
- `docs/product/current-product-state.md:65-67`: currency-less positions through the generic request path can be assigned a currency.
- `docs/finance/financial-methodology.md:59-92` "Importer resilience rule": malformed records are skipped, never zero-filled; gaps "surface through statement reconciliation". ESPP declared "not reachable" for malformed-number failures (:74-80).
- `docs/finance/financial-methodology.md:3164-3169` "Current Known Financial Limitations" lists nothing specific to import.
- `importers/freedom24.py:251-252` comment references a "tech-debt-register" deferral (realized P&L not modelled); the register has no such row.

## Suspicions

Not verified defects. IDs referenced above. Tags: [default] silent default, [drop] silent drop, [zero] null-to-zero, [sign], [hard-code], [mix] truth-class/provenance mixing, [dup] duplicated logic.

Import route and detection
- S-01 [drop] `interactive_brokers_csv.py:306` and `:269` drop every non-`Stocks` trade/position row; Forex (IB2026.csv:489) and `Corporate Actions` (IB2026.csv:585, LQQ split 200:1, qty 199, no parser) never enter the ledger. Cash effects of Forex conversions therefore have no ledger entry; the Cash Report balance still reflects them.
- S-02 [drop] Per-record skips (csv:288,318,357,389,421; ib.py:289,299,330,397; freedom24.py:196,227,274,339) leave no count, log or flag on the snapshot. The methodology (L59-65) says the gap "surfaces through the statement reconciliation", but `build_reconciliation_summary` (analytics/reconciliation.py:59) has no non-test caller in app/ (only a re-export, analytics/portfolio_imports.py:4,13). Admission (import_admission.py) checks cash, stock total and NAV only, not ledger sums (dividends, fees, deposits).
- S-03 [drop] `statement_importer.py:34-35` swallows the IBKR PDF ValueError and falls through; the final error is the Freedom24 or ESPP message (:49-52), so an IBKR parse failure after a passing preview is reported as another broker's failure. `ib.py:246-250` position numbers are unguarded and would take this path.
- S-04 [default] `imports.py:89`: uploaded file with no suffix defaults to `.pdf`; desktop MIME normalisation `App.tsx:137-139` maps anything not `.csv` to PDF.
- S-22 [mix] Uploaded files are spooled to random temp paths (`imports.py:90-93`) and the importers store `str(path)` as `source_path` (csv:470, ib.py:585, freedom24.py:437, espp.py:238). `history_context_builder.py:14` (`source_file_names`), `import_admission.py:54-60` (`source_names`) and `statement_importer.py:117-127` (dedupe by source_path, never fires) therefore carry temp names; real names exist only on the desktop (`App.tsx:765`).

IBKR CSV / PDF
- S-05 [sign] Statement totals stored `abs()` (csv:205; ib.py:166; freedom24.py:123-132). A withdrawal-dominant period yields a positive `deposits_total`; a negative Other Fees becomes positive. Documented as convention (csv:63-66; L88-91).
- S-06 [sign] `tax=abs(amount)` for every Withholding Tax row (csv:369; ib.py:408), including positive reversals; `fee=abs(Comm/Fee)` (csv:315; ib.py:293) loses a rebate sign. `net_amount` keeps the sign.
- S-07 [default] `quantity > 0 ? BUY : SELL` (csv:323; ib.py:302,333): a zero-quantity row becomes SELL.
- S-08 [default] Base currency: `statement.base_currency = preview.base_currency` may be None (csv:473) while the totals use `"USD"` (csv:456); downstream defaults `"USD"` again (`currency.py:91,30`; `statement_importer.py:131`; `ledger.py:233`). A missing "Base Currency" cell silently becomes USD.
- S-09 [drop] Implied FX only for currencies that have an Open Positions group followed by a base restatement (csv:243-259); a currency held only as cash gets no rate and is carried unconverted (currency.py:73-77, disclosed).
- S-10 [default] IBKR instruments carry no `currency` (csv:435-442; ib.py:548-555), so the only currency-conflict check (`import_admission.py:180-184`) cannot fire for IBKR statements.
- S-11 [hard-code] PDF as_of fallback `date(2025, 12, 31)` (ib.py:571) plus period detection requiring a line starting "January " (ib.py:99); same literal in `history_context_builder.py:27`. A statement not starting in January silently gets 2025-12-31 dates. CSV path raises instead (csv:451).
- S-12 [hard-code] EURUSD extracted by a regex containing literal `1.0353` (ib.py:174); no GBP or other currencies on the PDF path.
- S-13 [zero] `statement_importer.py:306-308` merged cash uses `(x or 0.0)`: None starting/ending/settled cash summed becomes 0.0; and `ledger.py:305` `classify_opening_state` treats any non-None `starting_cash` as `broker_proven`, so a merged 0.0 built from Nones would read as proven.
- S-14 [dup] `ib.py:309` and `:340`: `net_amount = gross - fee if gross > 0 else gross - fee` (identical branches).
- S-15 [drop] `ib.py:228` position regex symbol class `[A-Z0-9. ]+` excludes hyphens and lowercase; `ib.py:285-289` a pending multi-line trade whose joined text fails the regex is dropped.
- S-16 [default] `statement_importer.py:340-358` ledger dedupe key spans all snapshots including within a single one, so identical rows inside one statement collapse on the multi-file path; `_merge_statement_totals` sums dividend/fee/deposit totals across all inputs (:199-203), so overlapping statement periods double count.

Freedom24 and ESPP
- S-17 [mix] Freedom24 position `cost_basis` is synthesised as `ending_balance * close_price` in both branches (freedom24.py:180-183), so `unrealized_pnl = market_value - cost_basis` (:192) is about zero and not broker truth; it flows into overview totals (overview.py:43-44).
- S-18 [hard-code] Freedom24 currency USD hard-coded for trades (:269), instruments (:405) and positions lacking a currency token (:172); base currency default USD (:103); totals bound to "Net assets, USD" (:112-139); `fx_rates` only `USDUSD` (:109). A EUR-commission-currency statement would be labelled inconsistently.
- S-19 [default] Freedom24 trades and fees dated at the first of the statement-start month (:46-51); ledger chronology is month-granular; fallback `date(2026, 1, 1)` at :48 is unreachable (period None raises at :420).
- S-20 [dup] Freedom24 possible fee double count: per-trade `fee` reduces `net_amount` (:253-256) and a separate period-total FEE entry is emitted (:348-378); `commissions_total` and `other_fees_total` are set from the same regex (:125-126). Whether cash_effect double counts is unverified.
- S-21 [drop] Freedom24 sections read `page_texts[idx] if len(page_texts) > idx else ""` (:145,:208,:236,:284,:349): a layout shift yields empty sections without an error; non-"funds" or non-"trading" position rows are dropped (:177).
- S-23 [mix] Freedom24 enrichment (:454-467, `except Exception: pass`) makes the import output depend on network and API key state, and overwrites `description`/`instrument_type` from a vendor profile (instrument_enrichment.py:97-100) with no marker on `ImportedInstrument` that the fields are vendor-derived.
- S-35 [sign] ESPP `_normalize_number` replaces "-" with "0" (espp.py:35): "-1.83" becomes "01.83"; the `-?` regexes at :72-73, :177 rely on later `abs()` for subtractions/tax, but `change_match` is used signed at :95.
- S-36 [hard-code] ESPP: symbol MSFT (:79,:112,:124,:216), FYIXX fund (:101), "Jan 1"/"Dec 31" anchors (:70-71); only the first "Employee Purchase" is read (:141) so multiple offering periods drop; DEPOSIT entry synthesised as price*shares (:150-160) though labelled from the statement; `deposits_total` = position cost (:92-93); `other_fees_total` and `withholding_tax_total` both take "Subtractions" (:87-88).

Domain, identity, admission, consumer
- S-25 [zero] `ledger.py:204` `cash_effect = entry.net_amount or 0.0`; `ledger.py:205` `asset_currency` from open positions only (None for fully sold symbols); `ledger.py:265` lot unit cost = BUY price ignoring fees; `:244` opening-lot cost estimated from ending average cost (flagged `cost_basis_is_estimated`); FIFO consumption assumed; no split adjustment.
- S-26 [default] `registry.py:246-270` substring keywords ("ETC", "DEF", "QQQ" in description) drive ETF category; `:244` currency default "USD"; `:211` `get_sector` default "Other" (used defensively at overview.py:68) vs "Unclassified" elsewhere; `:181` `.replace(".L", "")`/`.replace(".AS", "")` removes those substrings anywhere in a symbol. A registry-known ticker takes the curated sector even when the ISIN check flags a mismatch (instrument_identity.py:75-83; flag only).
- S-27 [default] `portfolio_snapshot_builder.py:37-43`: `quantity or 0`, `cost_basis := market_value`, `unrealized_pnl := 0`, `close_price := market_value` when quantity missing, currency default; also `importer or 'interactive_brokers'` (:10), `account_id='snapshot-workspace'` (:14), `datetime.utcnow()` (:8). The register covers currency only.
- S-28 [zero] `overview.py:47` `balance.ending_cash or 0` (ignores `ending_settled_cash`, unlike `import_admission.py:47-51`); `overview.py:43-44` cost basis and unrealized P&L converted at the statement-end static rate.
- S-24 [default] Admission single-currency gate: `import_admission.py:75-79,236,257,330,351` comparability requires a single currency across positions, cash and statement currency; the canonical IB2026.csv has USD/EUR/GBP positions (statement_truths.py:37), so positions, NAV and cash checks resolve `unavailable` and the summary cannot reach `admitted/verified` (:471-480) even though `fx_rates` exist. Inferred, not executed.
- S-29 [default] `import_engine.py:66-77` `risk_summary` is a stub (observations 0, all metrics None, methodology 'import_bootstrap'); honest None, but present in the bootstrap payload.

Desktop
- S-30 [zero] `portfolioSnapshot.ts:75` `ending_cash ?? 0`; `:15` and `:36` non-finite market value or amount coerced to 0; a null cash balance is rendered as 0 (CLAUDE.md "never render a missing financial value as zero").
- S-31 [dup] `portfolioSnapshot.ts:92-165` overlayImportedSnapshot is a frontend merge with different rules from backend `combine_imported_snapshots`: sums same-symbol marketValue and quantity regardless of account or period (backend replaces same-account, statement_importer.py:256-266), sums across currencies without conversion (:118), overwrites `baseCurrency` with no mismatch check (:150; backend raises, :131), and does not merge `fxRates`. The comment (:95-101, US-14.1) says summing is intentional for IB+ESPP MSFT.
- S-32 [default] `portfolioSnapshot.ts:4-8` `inferSourceType`: BIL/SGOV/SHV cash-equivalent, any uppercase symbol of 5 chars or fewer "equity" (ETFs included); `:21-30` dedupe by symbol ignoring currency.
- S-33 [mix] `App.tsx:791-806`: if the combine call fails the node is saved with overlaid positions but `importedHistorySnapshot: null`; `admissionSummary: nextAnalysis.admission_summary` (:804) is the newly added statement's alone, not the combined portfolio's.
- S-34 [mix] `portfolioWorkspaceStorage.ts:122-129` persists `importedExposureOverride` (overview, lookthrough, sector exposure, market overlap, concentration, availability) in `workspace.source`, i.e. derived analytics persisted next to snapshots; node and workspace ids are random UUIDs (:76-78) written with `put`; no hashing found under apps/desktop/src (grep for sha/digest/content-address returned no source files).

## Doc and code disagreements

- D-01 `docs/architecture/system-architecture.md:78` and `docs/finance/financial-methodology.md:33` call persisted import artifacts "content-addressed, immutable" and :25 promises fail-closed loading; desktop ids are random UUIDs (`portfolioWorkspaceStorage.ts:76-78`), writes are `put` (:166-170,:341), and the only load-time validation found checks pointer consistency (`startupSelectionValidation.ts:49-81`), not content.
- D-02 `docs/architecture/system-architecture.md:220` and `docs/product/current-product-state.md:48-49` say derived analytics are not persisted as portfolio truth; `portfolioWorkspaceStorage.ts:122-129` persists derived exposure results in the workspace source (S-34).
- D-03 `docs/finance/financial-methodology.md:59-65` says importer gaps surface through statement reconciliation; no production caller of `build_reconciliation_summary` found (S-02).
- D-04 `docs/finance/financial-methodology.md:128-130` describes reconciliation FX fallback as "EUR at 1.0; other currencies excluded"; `analytics/currency.py:73-77` carries unconverted currencies at face value and discloses them. Different consumers; reconciliation.py not read, so agreement is unconfirmed.
- D-05 `docs/architecture/testing-architecture.md:104-108` lists `docs/IB2026.pdf`; the file is absent and :144 names `IB2026.csv` canonical. :59 points at an "Epic 24" register section that does not exist; :73-76 mentions ranking/construction artifact tests, which CLAUDE.md lists as not current surfaces.
- D-06 `docs/product/current-product-state.md:12` and the route names (`/interactive-brokers/...`) present the import as IBKR-only; `statement_importer.py:37-47` also routes Freedom24 and ESPP PDFs and `test_routes.py:151,167` test them.
- D-07 `importers/interactive_brokers_csv.py:9-11` and methodology L59-65 claim "never a fabricated zero"; the same chain contains fabricated or defaulted values downstream (S-13, S-17, S-25, S-27, S-28, S-30).
