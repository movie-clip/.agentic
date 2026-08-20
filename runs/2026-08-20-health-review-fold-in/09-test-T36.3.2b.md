REPORT 2026-08-20-health-review-fold-in/09
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_route_inventory.py — NEW. Parses the "N route modules:" bullet header + list in docs/product/current-product-state.md and compares both the stated integer and the named module set against Path("services/quant-engine/app/api/routes").glob("*.py") (excluding __init__.py). Three tests: count match, list match (names the specific missing/extra module by name on failure, mirroring test_docs_paths.py's convention), and a not-vacuous canary (regexes actually match today's doc/tree, positive direction proven via "exposure.py" as a known-present canary).

verification:
  command:   cd services/quant-engine && pytest app/tests/test_route_inventory.py -v ; python scripts/run_all_tests.py
  result:    PASS
  detail:    "`python -m pytest app/tests/test_route_inventory.py -v` (pytest shim resolves via `python -m pytest`, not bare `pytest`, in this shell): 3 passed in 1.72s. `python scripts/run_all_tests.py` (full suite, from repo root): backend `782 passed, 45 warnings in 20.47s`; frontend `Test Files 37 passed (37)`, `Tests 331 passed (331)`; dead-code gate `ruff: clean, vulture: clean, knip: clean`, STRICT clean; `tsc --noEmit` step passed inside the runner; final line `All tests passed.`. `git status --porcelain` after the run shows only my new test file as untouched-by-me addition among the working tree's other pre-existing changes from earlier orders in this run (CLAUDE.md, current-product-state.md, etc.) — dashboardGoldens.ts shows no diff, so no golden-drift cleanup was needed."

contract_notes:
  - none — this is a new, read-only pytest module asserting doc-vs-filesystem consistency; it touches no schema, no TS type, no docs/contracts/<area>-fields.md field.

pack_corrections:
  - none. testing.md's shared-fixture and gotcha sections matched observed behaviour exactly (bare `pytest` is not on PATH in this shell; `python -m pytest` is required — this is a shell-environment fact, not a pack inaccuracy, so not filed as a correction).

handoff:
  - "New pytest module `services/quant-engine/app/tests/test_route_inventory.py`, same directory and naming convention as `test_docs_paths.py`. It reads REPO_ROOT via `Path(__file__).resolve().parents[4]` (same idiom as test_docs_paths.py) and BACKEND_ROOT = REPO_ROOT / 'services' / 'quant-engine'. It parses current-product-state.md's '<int> route modules:' header via regex `_COUNT_HEADER_RE` and the following bullet block via `_LIST_ITEM_RE` (anchored to '- `name.py`' list-item lines, stopping at the first blank line after the header) — if a future doc edit reformats that section (e.g. adds prose between the header and the list, or changes the bullet marker), the not-vacuous canary test will fail loudly rather than the check silently going dark."
  - "No new shared fixture was added to app/tests/fixtures.py — this module needed none (pure filesystem + doc-text parsing, no ImportedPortfolioSnapshot/market-data fixtures involved)."
  - "T-36.3.2a (docs half) was already landed before this order dispatched, per the work order's own statement — confirmed directly: current-product-state.md:96 reads '15 route modules:' and lines 97-111 list all 15 including cache.py/currency_risk.py/provenance.py. The new test passed green on first run against that already-corrected doc, with no red-then-fixed step needed."

risks:
  - none beyond what's already flagged upstream — no new risk surfaced by this narrow, read-only-against-the-repo test addition.
