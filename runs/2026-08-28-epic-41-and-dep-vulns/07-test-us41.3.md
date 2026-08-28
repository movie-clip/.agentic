REPORT 2026-08-28-epic-41-and-dep-vulns/07
status:      PARTIAL
verdict:     NONE

changed:
  - services/quant-engine/app/tests/test_roadmap_epic_ordering.py — NEW guard: epic-roadmap.md per-epic section headings must run strictly descending + non-vacuous-scan check (AC4 / T-41.3.4)

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_roadmap_epic_ordering.py app/tests/test_route_inventory.py app/tests/test_architecture_doc_route_inventory.py app/tests/test_docs_paths.py -v
  result:    FAIL
  detail:    1 failed, 18 passed. The 1 failure is test_roadmap_epic_ordering.py::test_epic_sections_are_in_descending_order — the intended red-before state: "Epic 23" section heading precedes "Epic 24" heading (assert 24 < 23). Goes green when order 06's Epic 23/24 block swap lands. Non-vacuous test passes (33 headings matched, Epic 40 present). All 3 sibling guards green.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - New test file services/quant-engine/app/tests/test_roadmap_epic_ordering.py — no shared fixture added; it only reads docs/product/epic-roadmap.md via pathlib, mirroring test_architecture_doc_route_inventory.py
  - Guard goes GREEN automatically once order 06 (docs, T-41.3.1) swaps the Epic 23 / Epic 24 section blocks into descending order — no test change needed then
  - Heading regex accepts both `## Completed Epic: Epic <N> —` and a bare `## Epic <N> —` active-epic form; when Epic 41's section is added at close-out either form is swept into the order check
  - _MIN_EXPECTED_HEADINGS = 20 (33 headings match today); raise only if the slice log grows well past that and you want a tighter floor

risks:
  - verification.result is FAIL by design, not a defect: non_goals forbid weakening the ordering rule to pass against the still-broken doc, and order 06 (which fixes the roadmap) has not landed — working tree still has Epic 23 heading at L1291 before Epic 24 at L1343. This is the red-before half of the red-before/green-after property the order asks me to demonstrate.
  - Green-after not executed against a real swapped file (order 06 not landed, and editing the doc is out of scope). Verified by reasoning: observed heading sequence is 40..25, 23, 24, 22..8; swapping only 23/24 yields a fully strictly-descending run, so the single failing pair clears and no other pair is affected.
  - Red-before basis is direct execution against the current unmodified epic-roadmap.md (not reasoning from DESIGN's description) — the failure names the exact Epic 23 / Epic 24 transposition DESIGN § Item 4 predicts.
