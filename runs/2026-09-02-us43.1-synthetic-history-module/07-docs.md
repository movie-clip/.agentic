REPORT 2026-09-02-us43.1-synthetic-history-module/07
status:      DONE
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — 3 symbol-path text updates: §Synthetic History Coverage Rule (`_build_synthetic_snapshot_history_states*` "in diagnostics_engine.py" -> `build_synthetic_snapshot_history_states*` "in services/synthetic_history.py"); drawdown-contribution `q_i` citation -> public `build_synthetic_snapshot_history_states` in services/synthetic_history.py; §Synthetic path (Risk tab) -> public `build_synthetic_snapshot_history_states_with_coverage` in services/synthetic_history.py. No formula, rule, coverage-wording or citation-target change.
  - docs/architecture/system-architecture.md — added `synthetic_history.py` to the "Shared / supporting" services inventory line, noting the public builders and the six consuming engines, extracted from diagnostics_engine.py in US-43.1.
  - .claude/skills/quant-research/SKILL.md — L71: "uses `_build_synthetic_snapshot_history_states` from `diagnostics_engine.py`" -> "uses `build_synthetic_snapshot_history_states_with_coverage` from `services/synthetic_history.py`".
  - docs/tech-debt-register.md — US-43.1 row (Epic 43 section): appended "RESOLVED (US-43.1, 2026-09-02)" note — new services/synthetic_history.py with the two public builders, all six consumers rewired, goldens byte-identical, full suite green.
  - docs/product/epic-roadmap.md — Epic 43: status line (US-43.1 Done 2026-09-02, 43.2-43.4 Backlog); US-43.1 bullet marked "Shipped 2026-09-02"; Story snapshot row -> Done; new "### Slice log" section with a 2026-09-02 US-43.1 entry.
  - docs/product/stories/README.md — Epic 43 index: US-43.1 status -> Done.
  - docs/product/stories/US-43.1-extract-synthetic-history-construction.md — Status: Backlog -> Done; AC1-AC5 ticked; T-43.1.1 / T-43.1.2 / T-43.1.3 ticked.
  - CONTEXT.md — §Modules "synthetic-history construction" (L28-36) confirmed accurate against the shipped module (path, both function names, six consumers) — no edit needed.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification field was NONE — docs-lane close-out, no command to run. Upstream gates: integration (05) and review (06) both PASS on `python scripts/run_all_tests.py` (backend 980 passed, frontend 359 passed, tsc + dead-code gate clean, dashboardGoldens.ts diff empty).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CONTEXT.md L28-36 was pre-seeded (run setup) with the correct public names and correct six-consumer list; verified against synthetic_history.py and the six engine imports — accurate, left unchanged.
  - epic-roadmap.md header "Updated: 2026-08-28" left as-is — not in the order's edit list and the intro paragraph already carries the 2026-09-02 Epic 43 framing.

risks:
  - Story file's "Implementer must read" and "Notes / decisions" sections still carry the two premises recon 01 / plan 02 §4 corrected — consumers pass `(snapshot, price_histories, valuation_dates)` not `(snapshot, benchmark_symbol, market_data, …)`, and the builder takes a plain `dict[str, list[dict]]` of price rows, not `MarketDataService`-shaped input. Left untouched: the order scopes this lane to US-43.1-delivery status/symbol-path edits only, and non_goals bar touching pre-existing drift. A follow-up doc order should correct the story's stale rationale.
  - Slice-log one-liner wording is drawn from the order's `definition_of_done` text (behaviour-neutral relocation; new services/synthetic_history.py; goldens byte-identical; backend 980 / frontend 359 green; integration + acceptance gates PASS; quant-audit not required per verbatim-move ruling), not user-confirmed — docs pack Step 3 asks for user confirmation on the slice-log line, and this lane runs without a user to confirm with.
  - financial-methodology.md drawdown-contribution `q_i` citation now spans one extra line inside the ```text``` block to carry the `services/synthetic_history.py` path; the formula lines above/below it are byte-unchanged.
  - Epic 43 remains Active (US-43.2-US-43.4 still Backlog) — no epic-header flip; correct.
