REPORT 2026-08-27-next-epic-or-story/08
status:      DONE
verdict:     NONE

changed:
  - docs/architecture/system-architecture.md — rewrote the stale route/seam/data-flow/truth-class inventory to the 15 registered routers; added `### Registered routers` (15-bullet module-stem list under the "The engine registers 15 routers" count-header) + `### Service layer` (real files only); reworded engine-purpose line, truth-class list, Core Architecture Rules bullets, API Boundary, and Data Flow; deleted all removed-surface subsections; left the three protected sections byte-identical

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs lane has no Bash; order's verification field is NONE. Suite runs after order 09 (T-41.2.3) lands.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - T-41.2.3 (order 09) guard parses `docs/architecture/system-architecture.md`: count-header line is exactly `The engine registers 15 routers (\`services/quant-engine/app/api/main.py\`):` matching `^The engine registers (\d+) routers?\b`; the 15-item bullet list follows on the very next line with NO blank line between (mirrors `current-product-state.md` / `test_route_inventory.py`), each line `- \`<module_stem>\` — ...`, list terminated by the first blank line (before `Grouped by role:`). Module stems: health, imports, exposure, diagnostics, dashboard_history, drift, attribution, correlation, stress, drawdown, distribution, provenance, currency_risk, market_data, cache.
  - The `Grouped by role:` bullets and the `### Service layer` bullets sit after the terminating blank line and start `- **` / `- ` + prose, so they are outside the machine-parsed block and cannot leak into `_LIST_ITEM_RE`.
  - AC12 red-before still holds: today's committed doc (pre-this-change) has no `### Registered routers` heading and no count-header sentence, so the guard's `assert m` fails until this rewrite is committed alongside order 09.

risks:
  - Plan § R2's example block shows a blank line between the count-header sentence and the bullet list, but the plan's own parsing pseudocode and the existing `test_route_inventory.py` it mirrors truncate the parsed block at the first `\n\n` after the header — a blank line there would make the guard parse zero modules and stay red. Resolved toward the working repo pattern (no blank line); flagged so order 09 / integration know the R2 rendering was adjusted for parseability, not ignored.
  - API Boundary line ~246 ("engine outputs are derived runtime artifacts or persisted immutable research artifacts"): dropped the "or persisted immutable research artifacts" clause entirely rather than narrowing to "import artifacts", because engine outputs are not import artifacts — narrowing would have asserted something false. Minimal change consistent with "no removed surface" per the order's guidance.
  - Swept the three out-of-strict-AC-map removed-surface references per plan § risks: Core Architecture Rules lines ~24/25 (now "imported broker truth, snapshot analytics, synthetic history, and persisted import artifacts" / "persisted import artifacts"), and Desktop Workspace Model line ~357 ("Persisted snapshots and workspace references should remain lineage-aware…"). Word surgery only.
  - Left "Documentation Rule" line ~253 ("…or persisted-artifact provenance rule changes…") untouched — not AC-mapped, and it still holds for persisted import artifacts (content-addressed, immutable). Noting it was considered.
  - Data Flow: deleted the trailing blank line of the former "Optimizer handoff rule" subsection along with lines 280-344, leaving a single blank line before "## Desktop Workspace Model" (internal-consistency requirement). Added one discretionary sentence per plan § "Data Flow rewrite bounds" allowing it: "Every engine reads from the persisted `PortfolioSnapshot` plus optional history context; there is no persisted-artifact, ranking, construction, optimizer-handoff, or replay flow."
  - Protected fences verified unchanged: market-data section (`### Market-data providers and data provenance` → "…never auto-corrects the registry or remaps the symbol."), the "Architecture-level trust rule" bullets + "must not collapse `withheld` into generic `unavailable`", and the "Accepted tradeoff — unauthenticated local file-read" paragraph. No edit touched their line spans.
