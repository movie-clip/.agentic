REPORT 2026-09-18-vertical-volume-indicator/10
status:      PARTIAL
verdict:     NONE

changed:
  - volume_profile.pine:221-224 — closesQueue/volsQueue (`array<array<float>>`, the CE10022 nested-array type that never compiled) replaced with closesFlat/volsFlat (`array<float>`) plus countsQueue (`array<int>`, one entry per bar); barVolQueue's own declaration is untouched.
  - volume_profile.pine:226-244 — push/shift block rewritten: each bar pushes its intrabar closes/vols onto the flat arrays and its intrabar count onto countsQueue; over-length shift removes the oldest bar's exact intrabar count off the front of the flat arrays. barVolQueue's push/shift calls are unchanged, only their guarding size check now reads countsQueue instead of the removed closesQueue.
  - volume_profile.pine:275 — qSize now reads `array.size(countsQueue)`; closesQueue no longer exists to read.
  - volume_profile.pine:304-334 — binning loop's reads rewritten to a running `offset` cursor into closesFlat/volsFlat in place of `array.get(closesQueue/volsQueue, idx)`; `n` now comes from `array.get(countsQueue, idx)`. The na-skip logic (CR-1) and all bin/POC/reconciliation arithmetic are byte-identical — see § Worked-example hand-trace.

verification:
  command:   python ../.agentic/scripts/pine_check.py volume_profile.pine --strict
  result:    FAIL
  detail:    Exit 1, single hit: "volume_profile.pine:207: SHOULD_FIX P008 request.security() without an explicit lookahead — pass barmerge.lookahead_off so the intent is on the page." Same pre-existing false positive on request.security_lower_tf() documented since 03-backend.md/05-integration.md/06-backend.md/08-integration.md (line number shifted 182→193→207 as the file grew); this order's own definition_of_done names it as the expected result. Non-strict run (`pine_check.py volume_profile.pine`, no --strict) exits 0 with the identical single line and no other finding.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - The next TradingView compile attempt (main session) is the acceptance command for this fix — nothing in this report claims the script compiles; I have no browser/compiler access.
  - quant-audit delta requested by CR-2/compile.md (the data representation the binning loop reads from changed): check § Worked-example hand-trace's two hand-derivations against the code directly — the clean 3-bar case (V_j = 550/720/970/230, POC bin 2, 04-quant-audit.md's anchor) and 07-quant-audit.md's partial-na case B (V_j = 550/320/970/230, ratio 0.8381 CHECK).
  - integration (repo-wide static check) is still owed per compile.md's re-verification requirement, before the next compile attempt.
  - Per CR-2's second requirement: `[ltfCloses, ltfVols] = request.security_lower_tf(...)` (tuple destructuring) and `ignore_invalid_timeframe = true` (named argument) are still present, unchanged, at volume_profile.pine:207-208 — grep-confirmed, not re-read from memory.
  - Those two constructs' own compile status is still unverified by me: compile.md § Attempt 1 reported exactly one problem, at line 210, which is after them, but I cannot infer from that alone that lines 207-208 fully type-check — that confirmation is the next live compile attempt showing no further errors there, which has not happened yet.

risks:
  - status is PARTIAL not DONE because --strict's result is FAIL, matching 03-backend.md's and 06-backend.md's own precedent for this identical pre-existing P008 false positive — not something this change introduced.
  - I could not execute Pine, only read and hand-trace the code; my only evidence is the static checker (a pattern matcher, not a compiler) and my own worked-example re-derivation in § Worked-example hand-trace.
  - Scope interpretation: the order's line ranges (210-212, 214-220, ~280-300) are illustrative, and CR-2's prose scope fence says "every read/write/shift site" that touches the queues — under that wording I also changed line 275's `qSize` read from the removed closesQueue to countsQueue.
  - I touched nothing else outside the named blocks; that one extra line was mechanically required, not an opportunistic edit.
  - backend.md's "Gotchas" section does not list Pine's for-loop direction inference: `for i = start to end` with `end < start` and no explicit `step` counts DOWN instead of running zero times.
  - That gotcha is a real trap here — `nIntrabars`, `oldCount` and `startIdx` can legitimately be 0, and an unguarded `for k = 0 to n - 1` would then run twice instead of zero times; I guarded all three sites with `if n > 0` before the loop.

## Orchestrator brief
- Fixed CR-2 (CE10022, nested typed arrays do not compile in Pine v6): closesQueue/volsQueue replaced with flat arrays + a per-bar intrabar-count queue, same push/shift-when-over-length semantics.
- Static check: FAIL under --strict, but only the known pre-existing P008 false positive on request.security_lower_tf(); 0 BLOCKING, non-strict exits 0.
- Hand-traced both the clean 3-bar worked example (04-quant-audit.md's anchor) and 07-quant-audit.md's partial-na case B against the new code by hand — both reproduce exactly — in § Worked-example hand-trace, offered as evidence for the next quant-audit dispatch, not a substitute for it.
- Both of 03-backend.md's other previously-unverified constructs (tuple-destructuring `request.security_lower_tf()`, `ignore_invalid_timeframe` named arg) are still present unchanged; their own compile status is still open pending the next live compile attempt.
- Next steps this run still owes, per handoff: quant-audit (delta), integration (repo-wide), then the live compile attempt.

## Worked-example hand-trace

**Clean case (04-quant-audit.md's anchor).** 3 bars of 4 intrabars each, `B = 4`, `R_lo = 10.00`, `R_hi = 12.50`, `h = 0.625`. Assume these occupy queue positions `idx = 0,1,2` (`startIdx = 0`, `endIdx = 2`):

- Bar 1 → closesFlat[0..3] = 10.2,10.6,10.9,10.4; volsFlat[0..3] = 100,300,200,150.
- Bar 2 → closesFlat[4..7] = 11.4,11.1,10.8,11.9; volsFlat[4..7] = 250,400,120,80.
- Bar 3 → closesFlat[8..11] = 12.3,11.7,11.5,12.0; volsFlat[8..11] = 60,500,220,90.
- countsQueue = [4,4,4].

`startIdx = 0`, so the `if startIdx > 0` guard skips the offset-precompute loop and `offset` starts at 0 — correct, since position 0's slice starts at the front of the flat arrays.

- `idx=0`: `n = countsQueue[0] = 4`. Reads closesFlat/volsFlat[0..3] via `offset+k` (offset=0) — exactly bar 1's tuples. Bins: 10.2→bin0(+100), 10.6→bin0(+300), 10.9→bin1(+200), 10.4→bin0(+150). Running bin0=550, bin1=200. `offset := 0 + 4 = 4`.
- `idx=1`: `n=4`. Reads closesFlat/volsFlat[4..7] (offset=4) — exactly bar 2's tuples. Bins: 11.4→bin2(+250), 11.1→bin1(+400)=600, 10.8→bin1(+120)=720, 11.9→bin3(+80). `offset := 4 + 4 = 8`.
- `idx=2`: `n=4`. Reads closesFlat/volsFlat[8..11] (offset=8) — exactly bar 3's tuples. Bins: 12.3→bin3(+60)=140, 11.7→bin2(+500)=750, 11.5→bin2(+220)=970, 12.0→bin3(+90)=230.

Final: `V_j = (550, 720, 970, 230)`, sum 2470, `vMax=970` at `j=2` (strict `>` on ascending `j`, unchanged) → POC bin 2. Matches 04-quant-audit.md's anchor exactly, digit for digit.

**Partial-na case B (07-quant-audit.md).** Same setup, bar 2's second intrabar volume made `na`: `volsFlat[5] = na` (closesFlat[5] stays 11.1).

- `idx=1`, `k=1`: `p = closesFlat[5] = 11.1`, `v = volsFlat[5] = na`. `na(p) or na(v)` is true → `naIntrabars += 1`, no bin write (CR-1's skip, untouched by this change). The other three intrabars of bar 2 bin exactly as in the clean case: 11.4→bin2(+250), 10.8→bin1(+120), 11.9→bin3(+80).
- bin1 after bar 2 = 200 (from bar 1's 10.9) + 120 (bar 2's 10.8 only, since 11.1's volume was skipped) = 320, not 720.
- `sumBarVolumeCovered` still adds bar 2's full native chart volume via `array.get(barVolQueue, idx)` — unaffected by the skip, since that read did not change.

Final: `V_j = (550, 320, 970, 230)`, sum 2070, POC still bin 2 (970 still the max). Matches 07-quant-audit.md's case B (`2070/2470 = 0.8381` CHECK, `Status: OK — 1 na intrabar(s) skipped`) exactly.
