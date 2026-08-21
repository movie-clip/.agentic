REPORT 2026-08-21-sector-classification-followup/03
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/instruments/equity_sector_resolution.py — taxonomy lookup now normalizes (strip+casefold) both sides before matching.

verification:
  command:   cd services/quant-engine && python -c "from app.instruments.equity_sector_resolution import SECTOR_TAXONOMY_MAP, resolve_equity_sector; print('import ok')"
  result:    PASS
  detail:    printed "import ok". Ad-hoc manual check confirmed 4 casing/whitespace variants of "Technology" all resolve identically, and a genuinely unmapped sector still resolves to unavailable.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-37.2.4 can pin AC1/AC2 against the new normalized lookup; SECTOR_TAXONOMY_MAP itself is untouched (exact-case), existing direct-read assertions unaffected.
  - Normalization uses strip + casefold(), not upper() like normalize_isin — relevant if a test asserts the literal transform, not just the outcome.

risks:
  - Only this order's named verification command (import smoke check) was run; run_all_tests.py / dead-code gate deferred to the next lane that runs it, per non_goals excluding test files here.
