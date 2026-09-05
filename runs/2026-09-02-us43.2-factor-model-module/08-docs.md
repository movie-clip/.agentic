REPORT 2026-09-02-us43.2-factor-model-module/08
status:      DONE
verdict:     NONE

changed:
  - docs/finance/financial-methodology.md — §Statistical Factor Model "Implementation:" list re-pointed: factor-model internals (FactorDefinition, DEFAULT_FACTOR_DEFINITIONS, FACTOR_PROXY_MAP, FACTOR_KEY_MAP, ROLLING_RIDGE_FLOOR, orthogonalize_factors_window, fit_factor_model) now credited to analytics/factor_model.py; risk.py keeps the build_* entry points and factor_model_methodology(). Path text only — no formula, rule, ridge-floor, factor-definition or citation wording changed.
  - docs/architecture/system-architecture.md — new "Analytics layer" paragraph after the service-layer inventory: analytics/factor_model.py, its contents, and the transitional shape (leaf module; risk.py imports names back; build_statistical_factor_model still owned by risk.py; four consumers rewired; ReturnBasis literal → schemas/return_basis.py).
  - docs/tech-debt-register.md — row US-43.2 (~L339): consumer list corrected to 4 (added services/attribution_engine.py, services/diagnostics_engine.py); appended RESOLVED (US-43.2, 2026-09-02) recording the moved symbols, the AC3 linalg disposition (trio moved private, no non-factor caller), and the AC1 amendment (selected_history_return_series stayed in risk.py, renamed public — import-cycle avoidance). L345-362 divergence note left OPEN.
  - docs/product/epic-roadmap.md — "Updated:" header → 2026-09-02; Epic 43 status line → US-43.1 and US-43.2 Done; US-43.2 bullet gains "Shipped 2026-09-02" detail; story-snapshot row US-43.2 → Done; new slice-log row dated 2026-09-02 for US-43.2 in house style.
  - docs/product/stories/README.md — US-43.2 index row status Backlog → Done.
  - docs/product/stories/US-43.2-extract-factor-model-internals.md — Status Backlog → Done; AC1-AC6 and T-43.2.1..T-43.2.4 ticked; new "Delivery record (2026-09-02)" subsection recording the AC1 amendment, the AC3 disposition, the AC5 wording note, and the gate outcomes.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order verification field was NONE — docs-only reconciliation lane, no Bash. All upstream gates (quant-audit 05, integration 06, review 07) reported PASS on run_all_tests.py (backend 982, frontend 359); reviewer marked AC1-amended through AC6 SATISFIED, so no box was ticked that a gate did not confirm.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - CONTEXT.md "factor model" section already names analytics/factor_model.py and its module split correctly (Epic 43 authoring that predates this run — not touched per non_goals). Its parenthetical still spells the two fit helpers with the pre-rename underscore (`_fit_factor_model`, `_orthogonalize_factors_window`); they shipped public as `fit_factor_model` / `orthogonalize_factors_window`. Cosmetic; a source lane or a later CONTEXT.md pass can drop the underscores.
  - Pre-existing stale docstrings mention a deleted `_orthogonalize_factor_series` (attribution.py file header; risk.py:1703 docstring). Flagged out-of-scope by the backend (03 §Backend edit list #5), integration (06) and review (07) lanes. Not a docs/ file — needs a source lane, not this one.
  - docs/tech-debt-register.md L345-362 (the four-diverged-daily-return-implementations note, incl. attribution.py::_portfolio_return_series) left OPEN per the order DoD — it is a methodology-reviewed follow-up, not part of this relocation.
  - docs/product/current-product-state.md: confirmed no edit needed — verbatim behaviour-neutral refactor, no user-visible surface change; its only analytics/risk.py reference (L76, build_lookthrough_sector_exposure) is to a symbol that stayed in risk.py.
  - .claude/skills/write-story/SKILL.md: the analytics/factor_model.py table row added by the test lane (04) was checked — accurate, matches the table's row format, no wording change made.

risks:
  - The slice-log entry was drafted from the lane diffs and upstream reports in the house style and written without the "confirm with the user before writing" step the docs capability pack asks for — this dispatch has no interactive user. Test totals (backend 982, frontend 359) taken from the integration and review verification runs.
  - Bumped the epic-roadmap "Updated:" header to 2026-09-02 (not named in the DoD) because the status rows and slice log changed; the US-43.1 close-out had left it at 2026-08-28.
  - The financial-methodology "Implementation:" list now names the moved symbols to say where they live. Read as a path/location change permitted by DoD item 1 ("re-point ... phrasing for the MOVED symbols"); no formula, rule, ridge-floor description, factor-definition wording or citation was altered. The L1121-1129 "named policy constants ... at the top of risk.py" paragraph was left as-is — every constant it names (FACTOR_MODEL_MIN_SHARED_OBSERVATIONS, the VOLATILITY_REGIME_* cutoffs, the UCITS rubric weights) stayed in risk.py.
