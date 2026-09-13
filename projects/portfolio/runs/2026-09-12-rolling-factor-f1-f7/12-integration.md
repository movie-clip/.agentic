REPORT 2026-09-12-rolling-factor-f1-f7/12
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/run_all_tests.py
  result:    PASS
  detail:    exit_code 0, failure_count 0 (via mcp__project__run_tests scope=full). Backend pytest -n auto, desktop vitest, tsc --noEmit, and the dead-code gate (ruff+vulture+knip) all green; "All tests passed." check_gates(): deadcode ok, typecheck 0 errors, goldens_drifted false, commit-gate marker present.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Docs close-phase (phase table: pending) must use the 5-value enum from 05-quant-audit.md § FINDING 2 (adds `unavailable`, diagnostics_engine.py:604), not the 4-value list in 01-design.md § Doc contract row — already tracked as an OPEN contract_note in run.md, not new here.
  - See § TrustBadge docstring staleness for a SHOULD_FIX finding a docs/frontend touch-up should close alongside the close-phase docs order.

risks:
  - SHOULD_FIX, not blocking: `TrustBadge.tsx:9-11`'s docstring still lists `degraded` under "To extend with new types" even though `03-frontend.md` already added it to the union in this run, and its usage-sites sentence (`TrustBadge.tsx:5-7`) names only Exposure-tab cards, omitting the Dashboard-tab `RollingFactorLoadingsCard.tsx` this run wired up. See § TrustBadge docstring staleness.
  - Not re-litigated per non_goals: financial correctness (quant-audit round 3 PASSed), and the two SHOULD_FIX items already in run.md's Open table (tooltip precedence; the unreachable `?? ''` fallback in `modelPartialTooltip`).

---

## Orchestrator brief

- Verdict: PASS. No BLOCKING findings. Full suite green, gates clean, no goldens drift.
- All four `definition_of_done` checks confirmed independently (not by re-reading lane reports): no stray `.alpha`, card absent from both `designSystem.audit.test.ts` allowlists, `TrustBadge`'s `'degraded'` type used consistently, full suite PASS.
- Design deviations (CR-1/CR-3, badge now also reads model-level `status`) are properly declared through the run's own replan mechanism (run.md § Replans, v2/v3) and re-verified by quant-audit round 3 — not a silent divergence, no finding raised here.
- One non-blocking SHOULD_FIX opened this pass, in `risks`: a stale `TrustBadge.tsx` docstring. Does not block; hand to the human at close-out same as the two carried quant items.
- Sections below: **Contract alignment**, **Correctness against design**, **Reuse and consistency**, **Guardrails**, **Coverage adequacy**, **TrustBadge docstring staleness**.
- Nothing blocks dispatch of the close-phase docs order.

---

## Contract alignment

Checked `reconciliation.py` (`RollingFactorLoadingPoint`) against `types.ts` (the three `rolling_loadings_{20,60,252}d` element types) against `docs/contracts/dashboard-fields.md`, field by field, for the `alpha` removal: the field is gone from the schema (`reconciliation.py` diff shows only the one deleted line, nothing else touched) and from all three `types.ts` mirrors (repo-wide grep for `\.alpha\b` across `.py`/`.ts`/`.tsx` returns zero hits; the two `test_analytics.py:5353-5354` hits are an unrelated local OLS variable, matching 01-design.md's own exclusion note). No contract doc ever carried an `alpha` row for this field, so nothing needed retracting there. `ExposureFactorModelResponse` inherits the removal via its type alias, as the design predicted — no separate literal to fix.

`statistical_factor_model.status` / `windows[].status`: no schema or type change was needed or made (confirmed — `types.ts:1481,1488` already typed this pre-run), so there is no new field-shape mismatch to check on this pass; the doc-contract-row gap is a known, already-tracked, not-yet-due item (docs phase is pending by design).

## Correctness against design

F1 and F7 both landed as scoped. The one substantive deviation from `01-design.md` — the badge reading `statisticalFactorModel.status`/`insufficient_history` in addition to the per-window status, added by CR-1 and narrowed by CR-3 — is not an undeclared drift: it was forced by quant-audit FINDING 1 (round 1) and FINDING 4 (round 2), both are recorded in `run.md` § Replans and § Closed with the exact file:line reasoning, and quant-audit round 3 (`11-quant-audit.md`) independently re-measured the shipped resolver against six fresh engine builds and confirmed the fix without regressing FINDING 1 or FINDING 3. The plan and the code agree because the plan was explicitly updated (v2, v3), which is the process working as intended, not a gap.

Read the shipped resolver at `RollingFactorLoadingsCard.tsx:212-220` directly: it is an explicit whitelist over the two known degraded literals plus the `missing_factors`-gated model fallback, falling through to `null` for anything else (including `ok` and any unrecognized string) — this matches 01-design.md § Status enum and treatment's instruction not to implement an implicit "if ok then no-badge" branch that would silently treat an unknown status as verified.

## Reuse and consistency

`TrustBadge` was extended, not reimplemented — one union member, one `LABELS` entry, no new CSS (`.attribution-trust-badge` stays type-agnostic per the design's own instruction). `RollingFactorLoadingsCard.tsx` was correctly not migrated onto `CardShell`; confirmed absent from both `ALL_CARD_FILES` and `CARDS_WITH_BADGE` in `designSystem.audit.test.ts` (read the file directly, lines 25-52). Test fixtures reuse the real adapter chain (`createExposureEngineFixture` / `createDiagnosticsEngineFixture` / `composeExposureView` / `buildExposureFactorModel`) rather than hand-built response literals, including for the new model-level cases added across CR-1/CR-3's test rounds — the `buildFactorModel` helper in `RollingFactorLoadingsCard.test.tsx` layers overrides onto the fixture chain rather than bypassing it.

## Guardrails

Guardrail 4 (trust semantics): quant-audit round 3 independently re-derived the badge/tooltip mapping against the shipped engine across six fresh builds and confirmed no collapse of a degraded/insufficient rung into verified or vice versa. Guardrail 2 (traceability): `alpha` had zero methodology-doc mentions and zero live code path — removal, not documentation, was correct per `01-design.md` § F7 decision, consistent with the existing `attribution-fields.md:16` precedent against mislabeling a residual as alpha. No guardrail violation found.

## Coverage adequacy

The test suite exercises the contract, not a pinned implementation: `TrustBadge.test.tsx`'s new case mirrors the two existing ones exactly (label + rendering), and `RollingFactorLoadingsCard.test.tsx`'s five cases each drive a distinct real engine-shaped state (both-ok, window-partial, window-return-basis, model-partial-with-named-factor, short-history-only) through the adapter chain rather than asserting DOM structure. The one test that pins a currently-unreachable engine state (window-level `partial`) says so explicitly in its name and a comment citing the unreachability proof — this is honest coverage of a defensive branch, not a false claim of live behavior, and quant-audit round 3 independently re-derived the same unreachability proof rather than trusting the comment.

## TrustBadge docstring staleness

`TrustBadge.tsx:1-12`'s docstring was not updated in any of the three frontend passes (`03`, `06`, `09`) that touched this file. Two points are now stale: (1) line 10-11 still instructs "To extend with new types (`verified`, `degraded`, `withheld`)" as future work, when `degraded` was added to the union in this same run; (2) line 5-6 lists only "Exposure tab cards (drift, rolling correlation, factor attribution, multi-benchmark correlation)" as consumers, omitting `RollingFactorLoadingsCard.tsx`, a Dashboard-tab card (rendered via `DashboardPanel.tsx:134`) that this run made the primitive's newest consumer. Not blocking — the code is correct and consistent; the comment describing it is what lags. Whoever picks up the close-phase docs work (or a follow-up frontend touch) should update both lines.
