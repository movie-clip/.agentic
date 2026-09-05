REPORT 2026-09-03-us43.3-trust-gate-module/08
status:      DONE
verdict:     NONE

changed:
  - docs/architecture/system-architecture.md — added `trust_gate.py` to the shared/supporting services inventory (beside `synthetic_history.py`) as the output-trust decision's engine-side home, framed relocation-not-unification
  - docs/architecture/system-architecture.md — extended the architecture-level trust rule section to name `app/services/trust_gate.py` (US-43.3) as the single home of the output-trust decision for the dashboard-history + diagnostics engines, cross-referencing guardrail #3
  - docs/tech-debt-register.md — US-43.3 row marked RESOLVED 2026-09-03 (new `services/trust_gate.py`; 14 helpers moved verbatim + 1 constant; single merge `has_any_symbol_price_history`; cross-import removed; AC1 extended by `build_diagnostics_drawdown_summary`); the SectionTrust/return-basis-unification clause left OPEN
  - docs/product/epic-roadmap.md — `Updated:` header → 2026-09-03; Epic 43 status line US-43.3 → Done 2026-09-03; US-43.3 epic bullet gained a "Shipped 2026-09-03" clause; story-snapshot table row → Done
  - docs/product/epic-roadmap.md — slice-log entry added, dated 2026-09-03, house style with test-count delta (backend 982 → 984)
  - docs/product/stories/README.md — US-43.3 index row status → Done
  - docs/product/stories/US-43.3-relocate-the-trust-gate.md — Status Backlog → Done; Last updated → 2026-09-03; AC1–AC6 and T-43.3.1..T-43.3.4 ticked; "Close-out (2026-09-03) — as-built" subsection added to Notes / decisions (AC1 extension, the constant that rode along, the sanctioned rename, the relative-return pair left as follow-up, the wider dead-import cleanup, the moot test-retarget instruction, the plan's "15 functions" miscount)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification field was NONE — docs lane, read-only reconciliation. Upstream suite evidence: 03-backend / 05-quant-audit / 06-integration / 07-review all report `python scripts/run_all_tests.py` PASS (backend 984, frontend 359, tsc + dead-code strict clean, dashboardGoldens.ts diff empty).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - US-43.4 (collapse `import_engine_composer` into `import_engine`) is the last open Epic 43 story — after it ships, flip `## Epic 43 — Engine Seam Consolidation` to `## Completed Epic: …` and the PRD Status to Completed.
  - docs/tech-debt-register.md portfolio_proof.py note (the "revisit post-Epic-43" register note) says its admission-half split is "worth doing only after US-43.3 names the trust-decision vocabulary" — US-43.3 has now done that, so the note is actionable; left untouched here (outside this order's scope, which is the US-43.3 row only).

risks:
  - CONTEXT.md § "### trust gate" was confirmed-only, not edited: the module path `services/trust_gate.py` and the relocation-not-unification framing match 02 § B. One imprecision left as-is (outside the order's "correct only if framing differs" scope) — it reads "only the byte-identical primitives are shared" (plural) where `has_any_symbol_price_history` is the single primitive shared by both engines; `has_replay_outputs` also moved but is dashboard-only.
  - docs/product/current-product-state.md — no edit made: verbatim relocation, no user-visible surface change. The "~25 service files" count is approximate and was not bumped by sibling US-43.1 (which likewise added one service file), so it is left consistent with that precedent.
  - The story's AC1 was extended at design time (02 § A, human-approved) to move `build_diagnostics_drawdown_summary`, which AC1's literal list omits. The ticked AC1 box reflects the extended scope; a strict diff against the story's original AC1 text would show one extra name. Recorded in the story's close-out notes so the audit trail is explicit.
