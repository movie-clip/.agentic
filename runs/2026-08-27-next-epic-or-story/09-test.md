REPORT 2026-08-27-next-epic-or-story/09
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_architecture_doc_route_inventory.py — NEW sibling guard: parses system-architecture.md's `### Registered routers` count-header + bullet list, asserts bidirectional drift vs app/api/routes/ naming offending modules, plus a non-vacuous-scan test

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_architecture_doc_route_inventory.py app/tests/test_route_inventory.py -v
  result:    PASS
  detail:    6 passed, 0 skipped, 0 failed, 0 xfail. New file alone: 3 passed (test_stated_count_matches_actual_router_count, test_stated_module_list_matches_actual_route_modules, test_the_scan_is_not_vacuous). Sibling test_route_inventory.py -q: 3 passed, unbroken.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New test file services/quant-engine/app/tests/test_architecture_doc_route_inventory.py is a copy-not-import sibling of test_route_inventory.py (constants + regexes differ: this one keys on bare module stems `^-\s+`([a-z0-9_]+)`` vs the sibling's `<module>.py`). No shared fixture added; no fixtures.py change.
  - Guard binds to the doc-format contract in 08-docs.md § handoff: count-header `^The engine registers (\d+) routers?\b`, list on the immediately-following line with NO blank line, block terminated by first `\n\n` (before `Grouped by role:`). If order 08's doc block is later reformatted with a blank line after the header, test_the_scan_is_not_vacuous goes red (stated_modules empty) — intended.
  - 15 route modules today; doc says 15; list has 15 items; all three agree.

risks:
  - AC12 red-before verified by reasoning not execution (order permitted this; doc not reverted): pre-US-41.2 doc has no count-header, so `assert count_match` fails inside `_doc_stated_count_and_modules()`, which all three tests call — all three red against old doc.
  - Confirmed green against the landed post-rewrite doc; the guard's green state depends on order 08's block staying in the 08-docs.md § handoff format.
  - `### Service layer` and `Grouped by role:` bullets sit after the terminating blank line and also fail `^-\s+`([a-z0-9_]+)`` — double-guarded against leaking into the parsed module set.
  - Guard is structure-scoped (module stems), not prose-scoped: a phantom `/backtests/*` path in surrounding prose is not caught here — same by-design limitation as sibling test_route_inventory.py (07-plan § Decision ii). Reviewer covers AC1 prose.
