REPORT 2026-09-11-risk-summary-audit-foldable/13
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd services/quant-engine && pytest && cd ../../apps/desktop && npx vitest run && npx tsc --noEmit
  result:    PASS
  detail:    Backend: 1004 passed, 0 failed, 50 warnings (pre-existing pytest-socket guard warnings) in ~97s. Frontend: 42 test files passed (42), 380 tests passed (380). tsc --noEmit: exit 0, 0 errors. Also ran detect_deadcode.py --strict (ruff/vulture/knip all clean) and confirmed no diff on apps/desktop/src/test/dashboardGoldens.ts.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

risks:
  - SHOULD_FIX: test_routes.py's new pinned floats (active_return_pct=0.8, information_ratio=10.15, test_routes.py:1101-1102) have no hand-derivable provenance, unlike the US-27.1 hand-computed IR fixture in the same file. Already self-flagged by 12-test.md and tracked OPEN in run.md; not blocking.
  - Re-derivation procedure for those pinned floats is already documented by the test lane (run pytest, read the AssertionError, re-pin) — no action needed from this gate, noted only so the SHOULD_FIX isn't mistaken for missing guidance.
  - docs/contracts/diagnostics-fields.md's "Refusal rule" (212-214) and "Benchmark-relative refusal rule" (239-241) still describe `investor_economics_status = withheld` as the norm; stale for the now-available path.
  - That diagnostics-fields.md staleness was already captured as an OPEN docs contract_note by 09-backend.md § risks and is correctly deferred to the docs lane — not a code defect in this slice, not a new finding.

## Orchestrator brief
- VERDICT: PASS. No BLOCKING findings. Full suite green, re-verified independently (not taken on 12-test.md's word): backend 1004/1004, frontend 380/380, tsc clean, deadcode clean, no golden drift.
- Fix 1-4 match the accepted plan exactly — diffed trust_gate.py, diagnostics_engine.py, risk.py against § Fix 1-4 line by line, zero undeclared deviation.
- Both gate functions (`allow_diagnostics_drawdown_outputs`, `_allow_diagnostics_relative_return_outputs`) use one consistent keyword-only call pattern (`historical_sections_available=True`) at their one respective call site each — no inconsistency.
- `investor_economics_status` side effect confirmed benign: it is diagnostics-only (`build_diagnostics_investor_economics_status`, trust_gate.py:301-313), structurally distinct from the dashboard's own `build_dashboard_investor_economics_status` (unconditionally `available=False`, untouched). No frontend component reads `investor_economics_status` for rendering (grep confirmed: only test/fixture references). Confined, not leaking.
- No contract drift: Fix 3 is a frontend string-only change (RiskSummaryCard.tsx:95); Fix 1/2/4 change no schema field, name, type or route — only reachable value space, exactly as the plan's § Contract table specified. `RiskSummaryCard.tsx`'s render paths already handled non-null values with no change needed.
- US-45.1 fold-toggle (concurrently landed, untracked RiskSummaryCard.test.tsx + modified DashboardPanel.test.tsx) coexists cleanly: the `expanded` state wraps only the detail-metrics block; Fix 3's relabeled sentence sits outside the fold, always visible. Verified via `git diff` on both files.
- One SHOULD_FIX (not blocking, already tracked OPEN in run.md): pinned magic-number floats in new route tests lack derivable provenance — see § risks.
- Remaining work is docs-engineer close-out only (already scheduled in run.md's Open table); nothing else to dispatch from this gate.
