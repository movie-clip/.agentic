REPORT 2026-10-06-lint-v0.8.0-simplify/01
status:      DONE
verdict:     PASS
changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Validation passed. Anchor: authoring.md + 02/03 reports + PROTOCOL.md § 3 + runs/README.md; 0 BLOCKING, 0 SHOULD_FIX new; covered: orchestrator.md, SKILL.md; 1 UNVERIFIED premise.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Covered files: protocol/orchestrator.md and plugins/agentic-core/skills/orchestrate-feature/SKILL.md, scoped sections only.
  - Withdrawn mechanisms: grep for runs.py, ABANDONED and orchestrator_edit_gate finds no match in either file, nor in any .md outside runs/.
  - orchestrator.md:40: the status enum is back to PLANNING | DISPATCHING | GATING | BLOCKED | CLOSED, with no ABANDONED.
  - orchestrator.md:179: 'every run' needs no exception now that ABANDONED is gone, so the 02 F1 contradiction cannot recur.
  - orchestrator.md:510 resume paragraph: status is 'mid-flight' only; no ABANDONED wording remains.
  - orchestrator.md:736-740 § 7 and SKILL.md:22-24 agree: write only the run dir, every other edit is a work order, and git rm/mv go to the human (agrees with PROTOCOL.md § 3 lines 186-196).
  - SKILL.md step 3: grep -L "^status: *CLOSED" was tested on a CLOSED and a GATING ledger in the template's padded header format; it printed only the GATING one.
  - SKILL.md step 3 and orchestrator.md:238-249 agree: list every ledger not CLOSED, show it to the human, then resume, drop or leave it.
  - orchestrator.md:245-246 'drop' has the human delete the run dir (core § 3: no lane deletes) and cite it by id, matching portfolio runs/README.md:22 'cite a pruned run by its id'.
  - Carried from 02, non-blocking and unchanged: SHOULD_FIX rule 8, SKILL.md bullets over 200 characters.

skill_calls:
  - none

risks:
  - orchestrator.md:246 cites runs/README.md, but tradingview has no runs/README.md (only budget, datoro, impact, portfolio do). The id-citation instruction stands on its own, so this is not a finding.
  - SKILL.md step 3 'a run that matches this request is resumed' read with orchestrator.md:242 'do what they say' means resume once shown; judged compatible, not a contradiction.
  - UNVERIFIED: that scripts/check_report.py is reverted and the two scripts deleted. On disk now, check_report.py:300/760/885 still handle ABANDONED, and runs.py and orchestrator_edit_gate.py both still exist.
