REPORT 2026-08-27-next-epic-or-story/10
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && python -m pytest app/tests/test_architecture_doc_route_inventory.py app/tests/test_route_inventory.py -q  (plus git stash red-before check)
  result:    PASS
  detail:    6 passed in 1.67s (green-after). Red-before confirmed by execution: doc hunk stashed, guard alone -> 3 failed (all three call _doc_stated_count_and_modules(); assert count_match fires on the pre-US-41.2 doc). AC12 red/green property holds by test, not just reasoning.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - AC12 red-before was verified here by re-running the guard against the stashed doc (09-test.md left it at reasoning only). It is genuinely red-before. No action needed; recorded so the reviewer's AC12 pass has an execution basis.
  - 07-plan pack_corrections item (capabilities/architecture.md "The seams" omits `currency-risk` from the `/engines/{...}` list) is still open and correct: `POST /engines/currency-risk/run` is registered (main.py:21). Out of this story's scope; for the close-out docs lane.

## Orchestrator brief

Verdict: PASS. The US-41.2 slice coheres — the doc rewrite and the new guard bind to the same format and agree.

- 08-docs.md § risks item 1 (blank line between count-header and list): ADJUDICATED CORRECT. The plan's § R2 *rendered example* showed a blank line; the plan's own parsing spec and § R2 constraints forbid it. A blank line makes the guard permanently red. Landed doc has no blank line, matching the parser and test_route_inventory.py. No fix.
- 08-docs.md § risks item 2 (dropped "or persisted immutable research artifacts"): ADJUDICATED CORRECT. Narrowing to "import artifacts" would be false; there is no persisted-artifact flow post-story. Sentence reads correctly. No fix.
- Guard binds to the doc as landed (verified: 15 stems parsed, all match app/api/routes/, all registered in main.py). Not green by luck.
- Three protected fences (trust rule, market-data section, accepted-tradeoff note): byte-identical — diff -U0 shows no hunk in old lines 122-245 / 251-274. Verified.
- No phantom route path or phantom service file survives anywhere in the doc (grep clean). AC1-AC13 spot-checked at engineering level, all pass.
- No BLOCKING items. No SHOULD_FIX items. No change requests written.

Sections below:
- What was reviewed — the diff, inputs, ground truth pulled.
- Adjudications — the two 08-docs risks items, in full.
- Protected fences — untouched, proven by hunk ranges.
- AC-level engineering check — AC1-AC13, one line each.

---

## What was reviewed

- `git diff` on `docs/architecture/system-architecture.md` (tracked, 46 insertions / 155 deletions) and the untracked new file `services/quant-engine/app/tests/test_architecture_doc_route_inventory.py` (read in full).
- Working tree also carries unrelated Unit-1 doc-reconciliation edits (orders 04/05) on 9 other doc files — excluded from this review per the order.
- Inputs read: 07-technical-plan.md (full), 08-docs.md §§ changed/handoff/risks, 09-test.md §§ changed/handoff/risks, the US-41.2 story file, PROTOCOL.md + gates.md + project.md + capabilities/architecture.md.
- Ground truth pulled from the tree:
  - `app/api/routes/` has exactly 15 non-`__init__` modules; `app/api/main.py:4` imports all 15 and lines 18-32 call `include_router` on all 15.
  - The 15 module stems in the doc's `### Registered routers` list = the 15 on disk, exactly (attribution, cache, correlation, currency_risk, dashboard_history, diagnostics, distribution, drawdown, drift, exposure, health, imports, market_data, provenance, stress).
  - All 25 service files named in the doc's new `### Service layer` subsection exist under `app/services/`.

## Adjudications

### 08-docs.md § risks item 1 — blank line between count-header and bullet list — CORRECT AS LANDED

The DESIGN plan (07) § R2 rendered its example block with a blank line between
`The engine registers 15 routers (...):` and the first `- \`health\`` bullet.
Order 08 landed it with **no** blank line. This is the right call, not a defect:

- The plan's own parsing pseudocode (07 § "Parsing spec"): `block = text[m.end():]; nl = block.find("\n\n"); block = block[:nl]` — the parsed block **ends at the first blank line after the header**.
- The plan's own § R2 constraints: "one contiguous 15-bullet block, no blank lines between bullets"; "the guard's block boundary is the first `\n\n`".
- The guard as shipped (`_doc_stated_count_and_modules`): identical logic — `list_block = text[count_match.end():]`, truncated at `list_block.find("\n\n")`.
- If a blank line sat directly after the header line, `list_block` would truncate to the header-line remainder (` (\`...main.py\`):`), `_LIST_ITEM_RE.findall` would return `[]`, and the guard would be **permanently red**: `test_stated_count_matches_actual_router_count` (0 != 15) and `test_the_scan_is_not_vacuous` (empty `stated_modules`).

The plan's rendered example was internally inconsistent with its own spec and with `test_route_inventory.py`, which it mirrors. Order 08 resolved toward the working repo pattern and flagged it in § risks; order 09 codes to the same no-blank-line contract and flagged it too. The doc and the guard agree. No change request.

### 08-docs.md § risks item 2 — "or persisted immutable research artifacts" dropped, not narrowed — CORRECT

Old line: `engine outputs are derived runtime artifacts or persisted immutable research artifacts`.
Landed: `engine outputs are derived runtime artifacts`.

Plan § R5 offered "drop or narrow to 'persisted immutable import artifacts'".
Order 08 dropped, reasoning that engine outputs (ExposureResult,
DiagnosticsResult, ...) are not import artifacts, so narrowing would assert
something false. That reasoning is sound: post-story there is no
persisted-artifact flow at all, and the very next bullet already covers what the
frontend may persist (`PortfolioSnapshot` + workspace metadata, not derived
analytics). The remaining sentence is accurate and complete. No change request.

## Protected fences — untouched, proven by hunk ranges

`git diff -U0` on the doc produces hunks at old lines: 14, 24-25, 30-107,
116-118, 246, 248-250, 275, 280-344, 357. **No hunk touches old lines 122-245 or
251-274.** That span contains all three protected fences:

| Fence (AC) | Location now | Status |
|---|---|---|
| `Architecture-level trust rule:` + `verified_* / degraded_* / withheld / unavailable` bullets + "must not collapse `withheld` into generic `unavailable`" (AC9) | lines 80-87 | byte-identical — no hunk in range |
| `### Market-data providers and data provenance` through "...never auto-corrects the registry or remaps the symbol." (AC8) | line 89 ff. (old ~131-239) | byte-identical — no hunk in range |
| `**Accepted tradeoff — unauthenticated local file-read (import routes).**` paragraph (AC10) | line 207 ff. | byte-identical — read in full, intact; sits in old 251-274, no hunk |

The `@@ -246 +204 @@` and `@@ -248,3 +205,0 @@` hunks are inside the "API
Boundary / Current API direction" list (AC7 in-scope) and stop before the blank
line preceding the Accepted-tradeoff paragraph. Confirmed by reading lines
200-236 of the landed file: the paragraph body is unchanged.

## AC-level engineering check

Engineering-level only; full AC acceptance is order 11's gate.

- AC1 — no phantom route path in seams inventory: PASS. `grep -E '/backtests/|/construction/|/strategy-lab/|/optimizer/|/ranking/'` on the doc → no match.
- AC2 — every shipped router represented: PASS. 15/15 stems present; guard `test_stated_module_list_matches_actual_route_modules` enforces bidirectionally.
- AC3 — no phantom service file: PASS. 8 removed files (`portfolio_backtest_engine`, `construction_run_service`, ...) → no match in doc; 25 named files all exist on disk.
- AC4 — engine-purpose line matches shipped capability: PASS. Line 14 reworded to name only exposure/diagnostics/dashboard-history/drift/attribution/correlation/currency-risk/stress/drawdown/distribution/provenance; no ranking/construction/optimizer/replay.
- AC5 — truth-class list carries no removed surface: PASS. `persisted construction artifacts`, `hypothetical optimizer previews and handoffs`, `replay-derived hypothetical outputs` removed; `persisted import artifacts (content-addressed, immutable)` added — matches CLAUDE.md truth class 4 "Persisted Imports".
- AC6 — Data Flow describes shipped flow only: PASS. All 7 removed-surface subsections deleted (old 280-344); step 5 reworded to the 11 engines; finite-only import-admission paragraph retained byte-identical; one discretionary negative-assertion sentence added (plan-sanctioned).
- AC7 — API Boundary stops asserting removed seams: PASS. "formed candidates, constructed candidates, ..." bullet and "Future normalized API groups should preserve ... construction, optimizer handoff, and replay" line both removed.
- AC8 / AC9 / AC10 — protected fences untouched: PASS (see § Protected fences).
- AC11 — mechanical guard exists: PASS. New sibling file; three tests; bidirectional drift check names the offending module ("Add a bullet row" / "Remove the stale row(s) ... do not create the file").
- AC12 — guard not vacuous, red-before / green-after: PASS. `test_the_scan_is_not_vacuous` present with positive-direction assertions (`"exposure" in actual_modules`, `... in stated_modules`, `stated_count > 0`). Red-before verified by execution here (stash the doc hunk → 3 failed); green-after 6 passed.
- AC13 — full suite green: NOT RUN here by design (order non-goal; orchestrator runs it at close-out). The two route-inventory files pass; new file is pure pytest, no fixture/golden/network, auto-discovered.
