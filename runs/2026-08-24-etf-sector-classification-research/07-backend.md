REPORT 2026-08-24-etf-sector-classification-research/07
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/schemas/instruments.py — ClassificationSource gains "fmp_etf_sector_weighting_confirmed"; docstring bullet added per plan § Contract (T-39.1.1)
  - services/quant-engine/app/core/symbols.py — new SBIO SymbolResolutionRule in DEFAULT_SYMBOL_RULES (SBIO.L only, no bare SBIO, no proxy_candidates) (T-39.1.2)
  - services/quant-engine/app/clients/fmp.py — new FmpClient.get_etf_sector_weightings(symbol), one-line _get delegation (T-39.1.3)
  - services/quant-engine/app/services/market_data.py — new MarketDataService.get_etf_sector_weightings(symbol, overrides), mirrors get_company_profile shape (T-39.1.3)

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_fmp_client.py app/tests/test_market_data.py app/tests/test_instrument_registry.py -x -q; python scripts/detect_deadcode.py --strict
  result:    PASS
  detail:    85 passed (pytest, no failures/errors); detect_deadcode.py --strict: ruff clean, vulture clean, knip clean, "STRICT: no dead-code findings — clean."

contract_notes:
  - instruments.py's ClassificationSource literal changed; schema_edit_reminder hook fired as expected.
  - Per plan § Contract this literal is backend-internal, not serialized; no TS type exists for it (confirmed at exposure-fields.md:222-236), so no TS type change is owed.
  - docs/contracts/exposure-fields.md:225-226's enumeration prose needs the new literal name added — that edit is T-39.1.5 (docs-engineer), not this dispatch's scope.

pack_corrections:
  - none

handoff:
  - Confirmed before adding: no existing "SBIO" or "SBIO.L" key in DEFAULT_SYMBOL_RULES' canonical/alias set — no collision.
  - get_etf_sector_weightings (FmpClient + MarketDataService) is new and currently uncalled — T-39.1.4 wires it into etf_sector_resolution.py.
  - All three tickets built exactly to 06-technical-plan.md's given code (§ Contract, § T-39.1.2, § T-39.1.3); no deviation, no proxy_candidates added for SBIO.

risks:
  - none
