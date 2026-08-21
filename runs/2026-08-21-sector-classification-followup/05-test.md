REPORT 2026-08-21-sector-classification-followup/05
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/fixtures.py — added `FakeMarketData` class + `DEFAULT_COMPANY_PROFILE` constant, the shared FMP-profile fake for AC5.
  - services/quant-engine/app/tests/test_instrument_enrichment.py — removed local `_FakeMarketData`; imports `FakeMarketData as _FakeMarketData` from fixtures.
  - services/quant-engine/app/tests/test_equity_sector_resolution.py — removed local `_FakeMarketData`; imports `FakeMarketData as _FakeMarketData` from fixtures; updated module docstring.
  - services/quant-engine/app/tests/test_instrument_registry.py — removed local `_SpyMarketData` class; imports `FakeMarketData as _SpyMarketData` from fixtures.

verification:
  command:   cd services/quant-engine && pytest app/tests/test_instrument_enrichment.py app/tests/test_equity_sector_resolution.py app/tests/test_instrument_registry.py -q
  result:    PASS
  detail:    57 passed in 1.93s — all pre-existing tests green, no assertion changed.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New shared fake: `app.tests.fixtures.FakeMarketData(responses=None, *, profile=None, raise_for=None)` for `get_company_profile`. See § Shared fake shape.
  - `app.tests.fixtures.DEFAULT_COMPANY_PROFILE` pins the old `_SpyMarketData()` no-arg default profile, for reuse via `profile=DEFAULT_COMPANY_PROFILE`.
  - T-37.2.4 should import `FakeMarketData` directly from `app.tests.fixtures`, not add a fourth local fake — this ticket's whole point.
  - All three files kept their old local name as an import alias, so every existing call site is unchanged — only the one import line differs per file.

risks:
  - Two no-arg `_SpyMarketData()` calls never invoke `get_company_profile`, so the new default-profile behavior is unobserved today. See § Unobserved default.
  - Ran `detect_deadcode.py` (clean) and the order's named pytest command (PASS); did not run the full `run_all_tests.py` gate — order's verification named only the narrower command.

## Orchestrator brief

T-37.2.3 done. Shared `FakeMarketData` fake added to `fixtures.py`; all three
named test files migrated, local classes removed; 57 tests green; dead-code
gate clean. `§ Shared fake shape` = new fixture API for T-37.2.4 to reuse.
`§ Unobserved default` = risk on an untested default-profile edge case.

## Shared fake shape

`FakeMarketData(responses=None, *, profile=None, raise_for=None)`: `responses`
is a per-symbol dict (`symbol -> profile dict | None`); `profile` is the
fallback for any symbol not in `responses` (default `None`, matching the old
`_FakeMarketData`); `raise_for` is a set of symbols whose call raises
`RuntimeError`. `.calls` records every symbol looked up, in call order.

## Unobserved default

`test_static_registry_equity_never_calls_fmp_even_when_market_data_supplied`
and `test_etf_branch_ignores_market_data_and_makes_no_fmp_call` both construct
`_SpyMarketData()` with no `profile` kwarg, then assert `market_data.calls ==
[]` — the code paths under test never call `get_company_profile` at all. The
old class's implicit default profile and the new class's `profile=None`
default are therefore never actually exercised by either test today. If a
future edit to either test starts exercising the call path, it will silently
start observing `None` instead of the old fixed default — worth a comment or
an explicit `profile=DEFAULT_COMPANY_PROFILE` at that point.
