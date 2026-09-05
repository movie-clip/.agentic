REPORT 2026-09-04-us43.4-collapse-import-composer/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only DESIGN order; no verification command applies

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - see § Lane sequence for the ordered work orders and the two human stops
  - see § Fold shape for the exact backend edit (helper signature, import merge, call-site edit)
  - see § Docs blast radius for the T-43.4.2 file list and which mentions are correctness bugs vs out of scope

risks:
  - recon's risk bullet "CONTEXT.md does not exist yet" is stale — CONTEXT.md exists at the portfolio repo root (created 2026-09-02) and its "import bootstrap" section (line 57-62) already describes the POST-fold state ("the response-assembly step is a private helper, not its own module"), i.e. it is currently ahead of the code, not behind it — docs lane needs zero edits there, only confirmation
  - epic-8's PRD and epic-43's own PRD both name `import_engine_composer` but are planning/historical documents, not current-state inventories — I ruled them out of the T-43.4.2 edit set; flag to the human if that reading is wrong, see § Docs blast radius

## Orchestrator brief

- Quant-audit: NOT required — ruled in § Quant-audit ruling (pure Pydantic-construction relocation, no analytics/formula/trust code touched).
- § Contract disposition: `ImportedBootstrapResponse` schema unchanged, no TS/contract mirror owed; one contract-doc *name* correction owed (exposure-fields.md), not a contract change.
- Lane sequence (§ Lane sequence): backend (scoped verify) → HUMAN STOP `git rm` → test (full-suite verify) → integration → docs (T-43.4.2) → review → human commits. Quant-audit skipped entirely.
- Backend lane's own verification is deliberately scoped to `pytest` only, NOT `run_all_tests.py` — the dead-code strict gate is expected red until the human's `git rm` runs; see § Why the gate splits across two checkpoints.
- Exact fold shape (helper name, signature, import merge vs new lines, call-site edit) is in § Fold shape — read before dispatching backend.
- Test lane instruction (exact insertion point + assertion body) is in § Test lane instruction.
- Docs lane's required file list (5 files + story + register, NOT the two PRDs) is in § Docs blast radius.

---

## Quant-audit ruling

**Not required for this slice.** Recon (input 01) and my own read of both source files confirm: `compose_import_bootstrap_response` does exactly one thing — constructs `ImportedBootstrapResponse` from arguments passed straight through by its caller, plus one delegated call to `build_import_admission_summary(snapshot)` (an existing function, itself untouched and not being moved). No formula, no weighting, no return-basis logic, no trust-classification logic lives in the function being relocated. Nothing under `analytics/` is touched. Per `project.md` § "Any change touching `analytics/`, a formula, a weighting, a return basis, or a trust classification must go through the quant lane" — none of those conditions hold.

**Condition that would flip this ruling:** if, during implementation, the backend lane does anything beyond a verbatim move — e.g. changes a `PortfolioRiskSummary` field, alters what `build_import_admission_summary` is called with, or introduces any conditional/computed value that wasn't in the original composer body — that is no longer a pure relocation and the tech-lead INTEGRATION review must escalate for quant-audit at that point rather than pass it. The integration reviewer (§ below, same lane, later mode) is the backstop for this, not a second dispatch scheduled in advance.

## Contract disposition

`ImportedBootstrapResponse` (in `app/schemas/import_bootstrap.py`) is untouched — no field added, removed, renamed, or retyped. No TS mirror and no `docs/contracts/*.md` schema-shape edit is owed by this slice.

**contract_notes: none** — confirmed by direct read of both `import_engine.py` and `import_engine_composer.py`; the fold is a straight cut-paste-rename with an import merge, not a schema change.

One *name* correction is owed, not a contract change: `docs/contracts/exposure-fields.md:34` currently says fields are forwarded onto `ImportedBootstrapResponse` "via `compose_import_bootstrap_response(...)` (`services/quant-engine/app/services/import_engine_composer.py`)" — after the fold this sentence points at a deleted file. This is a traceability-doc correctness bug (a dangling code pointer), not a contract-shape change, so it is routed to the docs lane (§ Docs blast radius), not treated as a `contract_notes` entry.

## Fold shape

Read directly from both files (not recon's summary) — the composer's body makes one delegated call recon's handoff paraphrased as "a single return call"; that delegated call (`build_import_admission_summary(snapshot)`) must move with the rest of the body verbatim.

**New module-private helper**, added to `services/quant-engine/app/services/import_engine.py` (name and full signature per the story's own AC1 wording):

```python
def _compose_import_bootstrap_response(
    snapshot,
    overview: PortfolioOverview,
    lookthrough: LookThroughOverview,
    lookthrough_sector_exposure: list[LookThroughSectorExposure],
    market_overlap: MarketOverlapSummary,
    current_state_concentration: ExposureCurrentStateConcentration,
    availability: ExposureAvailability,
    risk_summary: PortfolioRiskSummary,
    history_context: PortfolioHistoryContext | None,
) -> ImportedBootstrapResponse:
    return ImportedBootstrapResponse(
        snapshot=snapshot,
        overview=overview,
        lookthrough=lookthrough,
        lookthrough_sector_exposure=lookthrough_sector_exposure,
        market_overlap=market_overlap,
        current_state_concentration=current_state_concentration,
        availability=availability,
        risk_summary=risk_summary,
        admission_summary=build_import_admission_summary(snapshot),
        history_context=history_context,
    )
```

Verbatim body of the current `compose_import_bootstrap_response`, only the `def` line's name changes (leading underscore) and its home moves from `import_engine_composer.py` to `import_engine.py`.

**Import edits in `import_engine.py`** (current lines 1-5 read: line 1 `app.schemas.imports`, line 2 `app.schemas.import_bootstrap.ImportedBootstrapResponse`, line 3 `app.schemas.reconciliation.PortfolioRiskSummary`, line 5 the composer import):

- **Remove** line 5: `from app.services.import_engine_composer import compose_import_bootstrap_response`.
- **Add**, new: `from app.schemas.exposure import ExposureAvailability, ExposureCurrentStateConcentration`.
- **Add**, new: `from app.schemas.portfolio_engine import PortfolioHistoryContext`.
- **Add**, new: `from app.services.import_admission import build_import_admission_summary`.
- **Merge, do not duplicate**: line 3 already reads `from app.schemas.reconciliation import PortfolioRiskSummary` — extend this single line's import list to `from app.schemas.reconciliation import LookThroughOverview, LookThroughSectorExposure, MarketOverlapSummary, PortfolioOverview, PortfolioRiskSummary` rather than adding a second `from app.schemas.reconciliation import ...` line. `ImportedBootstrapResponse` (line 2) needs no change — already imported, already correct name.

**Call-site edit**, inside `build_import_bootstrap_from_snapshot` (current lines 23-52): the single line `return compose_import_bootstrap_response(` (line 31) becomes `return _compose_import_bootstrap_response(` — every keyword argument below it (lines 32-52, including the inline `PortfolioRiskSummary(...)` construction) is unchanged.

**AC2 confirmation** (direct read, not inference): all three public entry functions —
`build_import_bootstrap(statement_paths: str | list[str], benchmark_symbol: str, symbol_overrides: dict[str, list[str]]) -> ImportedBootstrapResponse` (lines 12-15),
`build_import_bootstrap_from_portfolio_snapshot_request(request: SnapshotAnalysisRequest) -> ImportedBootstrapResponse` (lines 18-20),
`build_import_bootstrap_from_snapshot(snapshot: ImportedPortfolioSnapshot, benchmark_symbol: str, symbol_overrides: dict[str, list[str]]) -> ImportedBootstrapResponse` (lines 23-52) —
require **zero** signature or name changes. Only one line inside the third function's body changes (the call-site edit above).

## Test lane instruction

Existing pattern for this exact assertion shape lives at `app/tests/test_mcp_tools.py:361-367` (`with pytest.raises(ModuleNotFoundError): ...`) — follow it. Insert into `services/quant-engine/app/tests/test_analytics.py` immediately after line 778 (the last line of `test_build_import_bootstrap_from_snapshot_falls_back_to_ledger_and_position_dates_when_statement_period_missing`), before the blank-line-separated next test at line 781:

```python
def test_import_engine_composer_module_is_gone() -> None:
    with pytest.raises(ModuleNotFoundError):
        import app.services.import_engine_composer  # noqa: F401
```

This assertion is **only true after the human's `git rm`** (§ Lane sequence) — it is not a valid target for the backend lane's own checkpoint, and the test lane must not be dispatched before that `git rm` has actually run, or its own verification will fail for a reason that has nothing to do with its own work.

## Why the gate splits across two checkpoints

No lane holds a delete tool (`PROTOCOL.md` § 3), so the backend lane can fold the composer's body into `import_engine.py` and remove its own import of the composer, but **cannot** remove `import_engine_composer.py` itself. At that point the file still exists, physically unreferenced from anywhere under `app/` (confirmed by recon: no test imports it either). Two consequences follow, and both block a full-suite green run at that checkpoint specifically:

1. `detect_deadcode.py --strict` (vulture) now has a genuinely-unused function sitting in a file nothing calls — this is not a false positive to allowlist (`vulture_allowlist.py` entries are for real dynamic-use cases, not "pending deletion"), it is correctly flagging real dead code that the human has not yet deleted.
2. The test lane's pin assertion (`pytest.raises(ModuleNotFoundError)`) cannot pass either, for the same reason — the module still imports cleanly.

Both are resolved by the same single human action, so the design puts exactly one `git rm` between the two dispatches rather than trying to make either lane's checkpoint carry a command that is known in advance to fail.

## Lane sequence

Ordered work orders for the orchestrator. Ticket T-43.4.1 spans two dispatches (backend, then test) with a human stop between; T-43.4.2 is the docs dispatch.

1. **backend** — scope: `services/quant-engine/app/services/import_engine.py` only (do not touch `import_engine_composer.py` — it cannot be deleted by this lane and should not be edited in place). Apply § Fold shape verbatim. Verification: `cd services/quant-engine && pytest` (backend suite only — **not** `run_all_tests.py`, **not** `detect_deadcode.py --strict`; see § Why the gate splits). `status: DONE` on this scoped command passing is correct and expected; it is not the whole ticket.
2. **HUMAN STOP** (blocking — must complete before dispatch 3): `git rm services/quant-engine/app/services/import_engine_composer.py`. This is the only remaining half of AC1/AC4; no lane can do it.
3. **test** — scope: `services/quant-engine/app/tests/test_analytics.py` only. Apply § Test lane instruction. Verification: `python scripts/run_all_tests.py` (full gate — this is the actual proof of AC1/AC3/AC4: dead-code clean because the file and its dead function are both gone, pin assertion passes because the module genuinely no longer imports, goldens byte-identical because nothing analytics-facing changed).
4. **integration** (tech-lead, INTEGRATION mode) — confirm: full suite green per dispatch 3's run; `app/api/main.py` untouched (no route registration was ever involved, confirm nothing drifted); no dangling `import_engine_composer` reference anywhere under `app/` or `app/tests/`; `dashboardGoldens.ts` untouched (`git diff` empty); contract alignment trivially holds (schema untouched, confirmed above).
5. **quant-audit** — skipped entirely per § Quant-audit ruling; do not dispatch.
6. **docs** (T-43.4.2) — scope per § Docs blast radius. Dispatch after integration passes, before review, so the reviewer can confirm the *whole* story (code + docs) is closed in one pass.
7. **review** (reviewer, acceptance gate) — checks AC1-AC4 against the merged backend+test diff, and confirms T-43.4.2's doc updates landed.
8. **Human commits.** No lane commits at any point in this sequence.

## Docs blast radius (T-43.4.2)

Grepped directly (not trusting recon's list unread) for `import_engine_composer` and `compose_import_bootstrap_response` under `docs/`. Two classes:

**Must edit — current-state or status claims that become false or stale:**
- `docs/architecture/system-architecture.md:62` — "Import path: `import_engine.py`, `import_engine_composer.py`, ..." — remove `import_engine_composer.py` from the list. This is the story's own T-43.4.2 wording target.
- `docs/contracts/exposure-fields.md:34` — describes the current field-forwarding call chain including `compose_import_bootstrap_response(...)` / `import_engine_composer.py` — update to point at `_compose_import_bootstrap_response(...)` inside `import_engine.py`. A stale code pointer in a contract-traceability doc is a correctness bug, not tidying.
- `docs/tech-debt-register.md` (row US-43.4) — mark Resolved, per the story's own instruction.
- `docs/product/epic-roadmap.md:133,151` — flip the US-43.4 status-table entry (line 151) from Backlog to Done, and update the slice-log line (133) to reflect completion.
- `docs/product/stories/README.md:30` — flip the US-43.4 status column from Backlog to Done.
- `docs/product/stories/US-43.4-collapse-import-engine-composer.md` — flip Status header to Done, check all AC/ticket boxes.

**No edit needed:**
- `CONTEXT.md:57-62` ("import bootstrap" section) — already describes the **post-fold** state ("the response-assembly step is a private helper, not its own module"). It exists (created 2026-09-02) — recon's flag that it "doesn't exist yet" is stale; confirm only, do not edit.
- `docs/product/prd/epic-8-reset-to-analysis-core.md:72` — a historical module inventory for an already-shipped epic. Out of this story's stated scope; PRDs for closed epics are not treated as living current-state docs elsewhere in this repo. Do not edit; flag to the human if this reading is wrong.
- `docs/product/prd/epic-43-engine-seam-consolidation.md:35,48,80` — the current epic's own PRD, describing the planned fold. This is intent/planning text, not a current-state claim; the roadmap slice log (above) is what carries the "done" signal for this repo's convention. Do not edit.
