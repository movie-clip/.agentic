REPORT 2026-08-31-probe-engine-hardening/10
status:      DONE
verdict:     NONE

changed:
  - .agentic/projects/portfolio/capabilities/backend.md — "The response is not truncated" paragraph replaced with the bounded head/tail (`len > 11`, HEAD/TAIL = 5) + `__probe_truncated__` sentinel + `truncation` key + `fields=` (top-level keys, trust always retained, applied before bounding) behaviour
  - .agentic/projects/portfolio/capabilities/backend.md — route-to-shape guidance extended (not contradicted): `probe_engine` now reports `request_shape` / `request_model` from live FastAPI introspection and a warn-only `shape_mismatch`, still never 422, still POSTs
  - .agentic/projects/portfolio/capabilities/backend.md — `run_tests` / `check_gates` / `reset_goldens` description gains the structured timeout result, the local `TIMEOUTS` budgets (full 1800 / backend 600 / frontend 600 / typecheck 300 / gate 300 / git 30 s), per-gate subprocess isolation + top-level `timeouts` key, and `reset_goldens`'s pre-checkout `diff_stat` / `diff` capture
  - .agentic/projects/portfolio/capabilities/testing.md — "It does not validate the payload shape" replaced with the `request_shape` classification (`flat` / `snapshot-wrapped` / `bare-snapshot` / `unclassified`) + warn-only `shape_mismatch` on a top-level `snapshot`-key mismatch, still never 422 and never raises
  - .agentic/projects/portfolio/capabilities/testing.md — the `run_tests` / `check_gates` / `reset_goldens` tool bullets gain the timeout result (`timed_out`), per-gate isolation + `timeouts` key, and the pre-checkout bounded-diff capture
  - .agentic/projects/portfolio/capabilities/quant.md — added a "probe body may be bounded" note under Audit mode so a recomputation comparison never treats a `__probe_truncated__` sentinel or a `fields=`-filtered body as engine data

verification:
  command:   NONE (order's verification field is NONE; docs lane, no Bash)
  result:    NOT_RUN
  detail:    Read-only close-out. Reworded pack text verified by eye against the landed probing.py / testing.py — every claim matches: PROBE_ARRAY_HEAD/TAIL=5 and `count > 11` bound; sentinel keys original_count/dropped/kept_head/kept_tail/note; `_apply_fields` before `_bound_arrays`; `_request_model_for` off APIRoute.body_field; `_shape_mismatch` warn-only, POST always runs; TIMEOUTS dict values full 1800/backend 600/frontend 600/typecheck 300/gate 300/git 30; check_gates three isolated try/except + `timeouts` list; reset_goldens diff --stat then bounded diff then checkout, `diff_stat`/`diff`/`diff_truncated`/`discarded`/`timed_out`.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Carry-forward SHOULD_FIX (not docs work): AC-F5.2 `_bound_diff` head/tail truncation branch (testing.py:140-155) is wired at the reset_goldens call site but no test exercises the truncation path — needs a follow-up test ticket
  - Carry-forward SHOULD_FIX (not docs work): the shape/trust probes ride on engine request models that do NOT set `extra="forbid"`, so a wrong-shape payload returns 200 + `trust:"unavailable"`; adding `extra="forbid"` later would flip those to 422 and break the probes
  - Carry-forward SHOULD_FIX (not docs work): synthetic-history row-count probes (60 rows pass / 600 rows trigger truncation) are not pinned to `MIN_DAILY_OBSERVATIONS=20`; a large rise in that constant breaks the 60-row case
  - Process observation for the human (pack-corrections item 6): every Bash-enabled lane in this run (05-09) returned a REPORT HEAD with `headline:` left unfilled after running `check_report.py --emit-head`; consider tightening the head-return step in those agent files / packs. Not actioned here — editing agent files / PROTOCOL.md is out of scope this run.
  - MCP transport/handshake was NOT verified in this run — it needs a fresh interactive session; no lane claimed end-to-end MCP verification, and this close-out does not either
  - tech-debt-register.md: no entry added. The probe_engine / suite-runner hardening produced no repo-code dead-code or hardcode finding, and the three carry-forward SHOULD_FIX items are `.agentic`-internal test-coverage gaps that do not fit the file's Entry schema (no product `owner-story`, not dead code, not a hardcode) without distortion. Per the owner decision to track this as `.agentic`-internal tech debt with no `docs/product/` artifact, the run ledger plus the reworded capability packs are the record.

risks:
  - pack-corrections item 2's premise was partially false: `quant.md` carried no "response is not truncated" claim (that wording lived only at `backend.md:166`). Item 1's replacement was applied to `backend.md` as a reword; `quant.md` got a new bounded-body note instead of a reword of nothing. Both packs now agree with the landed code.
  - pack-corrections item 5 confirmed: `probing.py` / `testing.py` define no Pydantic schema and no contract field, pass engine `trust` strings through verbatim (`_trust_downgrade` only string-matches the literal `"unavailable"`), touch no `app/schemas/` model, no `apps/desktop` TS type, and no `mcp` / `starlette` pin — no `docs/contracts/`, `docs/finance/`, TS-type, or dependency-pin change is needed.

## Orchestrator brief

Close-out docs lane for the probe_engine / suite-runner hardening (T-43.1.5, T-43.2.4). Applied all six pack corrections:

- Items 1, 3, 4: reworded `backend.md`, `testing.md`, `quant.md` to the landed behaviour (bounded head/tail + `__probe_truncated__` sentinel + `fields=`; `request_shape` classification + warn-only `shape_mismatch`, still never 422; structured timeout result + `TIMEOUTS` budgets + per-gate `timeouts` key + `reset_goldens` pre-checkout `diff_stat`/`diff`). All wording verified against `probing.py` / `testing.py`; no residual disagreement, so no new `pack_corrections`.
- Item 2: premise partially false — `quant.md` had no "not truncated" line; added a bounded-body note rather than reword nothing (see `risks`).
- Item 5: confirmed no repo-doc / contract / schema / TS-type / dependency-pin change is needed (see `risks`).
- Item 6: recorded as a process observation for the human in `handoff`; no agent-file edit (out of scope).
- tech-debt-register.md: no entry — does not fit the Entry schema without distortion; run ledger + reworded packs are the record, per the owner decision (see `handoff`).
- Three carry-forward SHOULD_FIX items and the un-verified MCP handshake are in `handoff` for the human.

No repo file was touched. Only the three capability packs under `.agentic/projects/portfolio/capabilities/` changed. Pack indices unchanged (no section added, removed or renamed).
