REPORT 2026-09-18-vertical-volume-indicator/12
status:      PARTIAL
verdict:     NONE

changed:
  - C:\projects\investments\tradingview\volume_profile.pine — wrapped the `profileBoxes` and `profileLabels` clearing loops (lines ~268/271) in `if array.size(...) > 0`, matching the guard style already used at lines 227, 239 and 311.

verification:
  command:   python <agenticRoot>/scripts/pine_check.py volume_profile.pine --strict
  result:    FAIL
  detail:    volume_profile.pine:207: SHOULD_FIX P008 request.security() without an explicit lookahead - pass barmerge.lookahead_off so the intent is on the page — the same known P008 false positive present on every prior pass in this run (pattern-matches `request.security(` generically and fires on `request.security_lower_tf()`, which has no `lookahead` parameter). No new findings from this fix.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Both clearing loops now run zero times when their array is empty (size 0), matching CR-3's definition of done — a case worth covering in the next live compile attempt (every chart's first render).

risks:
  - status is PARTIAL not DONE because --strict's result is FAIL, matching 03-backend.md's, 06-backend.md's and 10-backend.md's own precedent for this identical pre-existing P008 false positive — not something this change introduced.
