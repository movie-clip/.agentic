REPORT 2026-09-18-vertical-volume-indicator/06
status:      PARTIAL
verdict:     NONE

changed:
  - volume_profile.pine:262-286 — intrabar loop now skips a contribution when its close or volume is na (na(p) or na(v)), instead of computing binIdx / calling array.set on it.
  - volume_profile.pine:245-254 — added `int naIntrabars = 0`, incremented once per skipped intrabar, to carry the count out to the Status row.
  - volume_profile.pine:347-349 — statusText now reads "OK — N na intrabar(s) skipped" instead of bare "OK" whenever naIntrabars > 0, and still renders the existing reason string unchanged when reason != "".
  - volume_profile.pine:356-358 — Status cell bgcolor now turns orange (matching the Coverage/Intrabars-per-bar convention) when naIntrabars > 0 and reason == "", in addition to the existing gray-on-n/a state.
  - volume_profile.pine:59-70 (header, guardrail-5 section) — added a "Status" bullet documenting that OK now specifically means every intrabar had both close and volume, and what the flagged text means; the all-na case is called out as unchanged.

verification:
  command:   python ../.agentic/scripts/pine_check.py volume_profile.pine --strict
  result:    FAIL
  detail:    Exit 1, single hit: "volume_profile.pine:193: SHOULD_FIX P008 request.security() without an explicit lookahead". This is the same pre-existing false positive on request.security_lower_tf() documented in 03-backend.md and 05-integration.md (line number shifted from 182 to 193 only because of the header addition); non-strict run (`python ../.agentic/scripts/pine_check.py volume_profile.pine`) exits 0 with the identical single line. No other finding, strict or otherwise.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Status row has a new text form: "OK — N na intrabar(s) skipped", alongside the existing "OK", "OK — PROVISIONAL" and reason strings.
  - Confirm the composed case at the compile check: includeCurrentBar=true plus at least one na intrabar should read "OK — PROVISIONAL — N na intrabar(s) skipped".
  - test-engineer needs a partial-na fixture: some intrabars na, some not — assert na intrabars are excluded from V_j (not poisoning it), Status is not bare "OK".
  - test-engineer needs a close-is-na fixture confirming no runtime error and a visible degrade, not a crash.
  - the all-na case's reason string and branch are unchanged by this fix (traced by hand: every vj bin stays exactly 0.0, vMax stays 0.0, the same `vMax <= 0` branch fires) — a regression fixture re-running 04-quant-audit's all-na scenario is still worth having on file since I could not compile.

risks:
  - status is PARTIAL not DONE because --strict's result is FAIL, matching 03-backend.md's own precedent for this identical pre-existing P008 false positive — not something my change introduced.
  - I could not execute Pine, only read the code. My only evidence is the static checker (a pattern matcher, not a compiler) and my own hand-trace of the all-na case's arithmetic.
  - I picked "skip the intrabar + flag Status with a count" over CR-1's other offered option ("set reason so the whole profile goes n/a on any na"). It keeps one stray na intrabar out of thousands from blanking an otherwise-good profile.
  - that skip-and-flag choice is a judgment call the human could reasonably make the other way — worth confirming at close-out that the softer degrade, not full n/a, is the intended reading of CR-1.
  - the CR's scope fence names volume_profile.pine:262-275; I also touched the declaration block just above (245-254) to add the naIntrabars counter, since the loop had nowhere to accumulate a count without it — read as inside the fenced na-handling path, flagged here since the fence's line range starts at 262.
