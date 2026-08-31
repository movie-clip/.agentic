REPORT 2026-08-31-probe-engine-hardening/05
status:      DONE
verdict:     NONE

changed:
  - services/quant-engine/app/mcp_server/tools/probing.py — probe_engine_impl now returns the full 04 § 1 envelope (unmocked, refused, request_shape, request_model, shape_mismatch, ok_downgraded_by, truncation, fields_kept, fields_omitted_count); ok narrowed per § 1d
  - services/quant-engine/app/mcp_server/tools/probing.py — added _request_model_for, _shape_of, _shape_mismatch, _trust_downgrade, _apply_fields, _bound_arrays, _refusal; PROBE_ARRAY_HEAD/TAIL + _MAX_TRAVERSAL_DEPTH constants
  - services/quant-engine/app/mcp_server/tools/probing.py — control flow: derivable target import_module before context; non-derivable + not allow_unmocked returns _refusal; allow_unmocked=True runs via nullcontext with unmocked=True
  - services/quant-engine/app/mcp_server/server.py — probe_engine wrapper signature gains fields + allow_unmocked, both passed through the single delegating call; docstring unchanged at 2 lines

verification:
  command:   cd services/quant-engine && SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q
  result:    FAIL
  detail:    2 failed, 31 passed. Both failures are in TestGates and are predicted by 04 § 8 / § 6a, assigned to WO-E: test_check_gates_reports_every_gate (needs "timeouts" in the exhaustive key-set) and test_check_gates_flags_goldens_drift (fake_run stub needs *, timeout=None). Both stem from WO-C's testing.py edits already on disk, not from probing.py/server.py. Every TestProbeEngine / TestEngineModuleDerivation / TestBuildSnapshot / TestRunTestsParsing test passes. No class-(b) unexpected failure.

contract_notes:
  - .agentic capabilities/backend.md:166 ("The response is not truncated") is now stale — probe_engine bounds long arrays head/tail with a __probe_truncated__ sentinel; docs close-out T-43.1.5 must reword to "bounded head/tail, original_count preserved on the sentinel"
  - .agentic capabilities/quant.md:166-169 (same "not truncated" claim) is now stale — same reword, T-43.1.5
  - .agentic capabilities/testing.md:154-156 ("does not validate the payload shape") is now stale — probe_engine classifies request_shape and warns on a top-level snapshot-key mismatch (still never 422s); reword per 04 § 8, T-43.1.5
  - probe_engine return envelope gained 9 keys and ok changed meaning — the agent-facing tool contract in the capability packs lags until T-43.1.5; no repo doc (docs/contracts/, docs/finance/) is affected — the tool passes engine trust strings through verbatim and defines no contract field
  - no app/schemas/ change; no TS type affected; mcp pin not bumped; starlette untouched

pack_corrections:
  - none

handoff:
  - 2 still-red tests, both class (a) predicted by 04 § 8, owned by WO-E: TestGates::test_check_gates_reports_every_gate and TestGates::test_check_gates_flags_goldens_drift — WO-E adds "timeouts" to the key-set assertion and gives fake_run a keyword-only timeout param
  - new helpers WO-E can import from app.mcp_server.tools.probing: _request_model_for(app, route), _shape_of(model)->str, _shape_mismatch(request_shape, payload)->dict|None, _trust_downgrade(body)->dict|None, _apply_fields(body, fields)->(body, kept, omitted), _bound_arrays(obj)->(obj, paths)
  - envelope keys for WO-E assertions: refused/unmocked (bool), request_shape ("flat"|"snapshot-wrapped"|"bare-snapshot"|"unclassified"), request_model (str|None), shape_mismatch ({expected,supplied,note}|None), ok_downgraded_by ({key:"unavailable"}|None), truncation (list[str] dotted paths), fields_kept (list[str]|None), fields_omitted_count (int|None)
  - refusal reason literal contains "allow_unmocked"; truncation sentinel is {"__probe_truncated__": {original_count, dropped, kept_head, kept_tail, note}}; note contains "probe_engine truncated this array"
  - probe of a snapshot-wrapped payload to a flat route (e.g. the current drawdown test) now returns shape_mismatch populated + ok False via trust downgrade, but still status 200 and a full body — the existing assertions (status is int, body not None) still pass, so WO-E repoints it for correctness not because it is red
  - constants PROBE_ARRAY_HEAD=5, PROBE_ARRAY_TAIL=5: a list is bounded only when len > 11; sentinel replaces the middle, array stays a list of len head+1+tail

risks:
  - Protocol core § 6 says DONE requires verification PASS. Reporting DONE with verification FAIL because the order's definition_of_done explicitly carves out the 2 predicted TestGates failures to WO-E and non_goals forbid me editing app/tests/**. Class (b) is empty; all probing.py/server.py behaviour is verified green plus direct-probe smoke-checked.
  - testing.py was modified on disk by parallel WO-C before I ran verification, so the shared test file already exercises WO-C's new _run(timeout=) signature. If WO-C's testing.py is later reverted/changed, re-run before integration.
  - _shape_mismatch keys only on presence/absence of a top-level "snapshot" key (04 § 2c). A payload nested under a differently-named key gets shape_mismatch=None and no warning — a known § 2c gap, not a defect; full model_validate is deliberately not used to gate (F-1 hazard: wrong shape validates on defaults).
  - request_shape/request_model recovery rides APIRoute.body_field.type_. Verified against all 14 engine routes on the pinned stack (fastapi 0.119.1 / starlette 0.48.0 / pydantic 2.12.3) this pass; the three-step fallback (type_ -> field_info.annotation -> dependant.body_params[0].type_ -> None) is preserved for a future FastAPI bump.
  - Depth-1 trust scan only: nested per-episode / per-scenario trust does not downgrade ok (matches 04 § 1d / AC-F1.5). A reviewer expecting nested-trust gating will read this as under-strict; it is in-spec.
  - vulture flags build_snapshot_impl and probe_engine_impl as "unused" when run file-scoped (they are reached via server.py wrappers + tests) — pre-existing, not introduced here; detect_deadcode.py --strict resolves them across the whole tree.
