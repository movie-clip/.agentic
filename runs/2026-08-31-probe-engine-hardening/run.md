# RUN 2026-08-31-probe-engine-hardening
request:      Harden the `probe_engine` MCP tool in `services/quant-engine/app/mcp_server/`. It is the one tool in the project server that is not a thin wrapper over an existing command, and a review found it will hand lanes confidently wrong answers in its current form. Five fixes, ranked. All findings below were measured, not inferred — the numbers are reproducible. [1] ok:true on a probe that answered nothing — detect payload-shape mismatch (flat / snapshot-wrapped / bare-snapshot across 14 engine routes), report matched request-model name, warn on shape mismatch, stop reporting ok:true when body carries trust:"unavailable". [2] Unbounded response — truncate long arrays head/tail with original count preserved, add fields= arg; drawdown probe over 750d = 34,135 chars / ~8,500 tokens mostly underwater_series. [3] Non-engine routes run unmocked — engine_module_for returns None for non-/engines/ routes, probe then uses nullcontext() and goes live; add allow_unmocked: bool = False, refuse by default naming the flag; keep typo'd engine name failing loudly. [4] No subprocess timeout in tools/testing.py — every subprocess.run in _run omits timeout=; add per-scope timeout, return structured timeout result not raise. [5] reset_goldens destroys uncommitted work with no record — capture git diff --stat (and bounded diff) before git checkout --, return it. Constraints: keep the _impl / thin-wrapper split (no logic in server.py); every change covered in app/tests/test_mcp_tools.py calling _impl directly; don't restate paths/steps scripts/run_all_tests.py owns (tools/testing.py imports constants from there); server.py tool docstrings capped at 2 lines (new args documented in the capability pack, not the docstring); do NOT upgrade the mcp pin or let pip lift starlette past ==0.48.0 (broke 944-test collection once; trap documented in requirements-dev.txt). The .agentic side is done (route-to-shape table, "read trust before believing a 200", context-cost warning are in backend/quant/testing packs as of v0.5.5) — keep tool behaviour consistent with those packs. Verification: `SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q` from services/quant-engine, then full `python scripts/run_all_tests.py` from repo root before any commit. MCP handshake itself CANNOT be verified in this run — needs a fresh interactive session; the report must say so.
agentic_root: C:\projects\investments\.agentic
story:        NONE
status:       CLOSED
next:         none — CLOSED
route:        full
express:      no
gates:        quant-audit SKIPPED (tool passes engine trust strings through, computes/classifies nothing — guardrail 1 not engaged; .agentic trust packs already v0.5.5) · integration PASS (08 — 63 tests, 0 BLOCKING, 3 SHOULD_FIX) · review PASS (09 — all 30 ACs MET, test plan delivered, 63 pass, +1 SHOULD_FIX)
note:         05/06 verification-FAIL was the 2 predicted TestGates cases, closed by WO-E; test_mcp_tools.py green at 63. Heads from 06-10 omitted `headline` after `--emit-head` — orchestrator read those artifacts directly (pack-process note recorded in 10-docs handoff). Human pre-commit `run_all_tests.py` is the ONLY run of the dead-code --strict gate + full suite; new probing.py helpers all used per 08. MCP transport/handshake NOT verified this run — needs a fresh interactive session.

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | NONE |
| 02 | story | — | story-author | sonnet | 02-stories.md | DONE | NONE |
| 03 | recon | — | scout | sonnet | 03-scout-map.md | DONE | NONE |
| 04 | design | DESIGN | tech-lead | sonnet | 04-technical-plan.md | DONE | NONE |
| 05 | backend | — | backend-engineer | sonnet | 05-backend-probing.md | DONE* | NONE |
| 06 | backend | — | backend-engineer | sonnet | 06-backend-testing.md | DONE* | NONE |
| 07 | test | — | test-engineer | sonnet | 07-test.md | DONE | NONE |
| 08 | integration | INTEGRATION | tech-lead | sonnet | 08-integration.md | DONE | PASS |
| 09 | review | — | reviewer | sonnet | 09-review.md | DONE | PASS |
| 10 | docs | — | docs-engineer | sonnet | 10-docs.md | DONE | NONE |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| should_fix | 07-test | § risks | shape/trust probes ride on engine request models NOT setting extra="forbid" (wrong-shape => 200+unavailable, not 422); adding extra="forbid" later flips them to 422 | CARRIED — human; 08 weighed non-blocking |
| should_fix | 07-test | § risks | synthetic-history row-count probes (60 rows pass / 600 trigger truncation) not pinned to MIN_DAILY_OBSERVATIONS=20; a large rise in that constant breaks the 60-row case | CARRIED — human; 08 weighed non-blocking |
| should_fix | 09-review | § risks | AC-F5.2 `_bound_diff` head/tail cap (testing.py:140-155) wired at :342 but no test exercises the truncation branch — WO-E listed a long-diff case, did not deliver it | CARRIED — human / follow-up test ticket |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| context | user | 01 | producer pass scoped to placement + dedupe — done, verdict relayed to human |
| constraint | user | 04+05+06 / 08 | no-logic-in-server.py + 2-line docstring + no pin bump + testing.py keeps importing constants — all held, verified by 08 integration |
| constraint | user | 10 | MCP handshake NOT verified this run — stated in 10-docs handoff + this ledger + close-out report |
| decision | 01 | owner | epic placement — RESOLVED: track as .agentic-internal tech debt, no docs/product/ artifact, no tech-debt-register entry (does not fit house schema per 10) |
| decision | 01 | 04 § 9 | F-1 sub-scoping — RESOLVED: F-1 stays ONE ticket; request-model name via live FastAPI introspection, no hand table |
| plan | 02 | 04→07 | US-43.1 + US-43.2 human-approved; built + gated PASS/PASS |
| decision | 02 | 10 | pack docs as close-out tickets T-43.1.5/T-43.2.4 — applied by 10 |
| handoff | 03 | 04 § 8 | "five-tool registration check" struck; drawdown test repointed + TestGates key-set updated by 07 |
| handoff | 03 | 04 § 6 | `_run` gains `*, timeout=None` keyword-only — done, positional assertions survive |
| handoff | 03 | 04 § 2 | request-model recovery via `APIRoute.body_field.type_`, verified across all 14 routes |
| contract_note | 04+05 | 10 | backend.md/quant.md "not truncated" reworded to bounded head/tail + __probe_truncated__ sentinel |
| contract_note | 04+05 | 10 | testing.md "does not validate payload shape" reworded to request_shape classification + warn-only shape_mismatch |
| contract_note | 06 | 10 | backend.md/testing.md suite-runner descriptions given the structured timeout result + reset_goldens diff capture |
| contract_note | 04+05+06 | 10 | confirmed: no docs/contracts/, docs/finance/, TS-type, app/schemas/ or pin change needed |
| note | 07 | 09 | verified/degraded non-downgrade helper-only — adequate; helper is the single ok-narrowing path |

## Rounds
| finding | lane | round | of |
|---|---|---|---|

## Cost
| metric | value |
|---|---|
| dispatches | 10 |
| rounds | 0 |
| by model | sonnet 10 |
| escalations | none |
