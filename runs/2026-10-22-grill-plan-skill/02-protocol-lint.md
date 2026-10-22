REPORT 2026-10-22-grill-plan-skill/02
status:      DONE
verdict:     PASS
verification:
  command:   claude plugin validate ./plugins/agentic-core; yaml.safe_load on both SKILL.md frontmatters
  result:    PASS
  detail:    validate passed (LICENSE/icon directory notes only); both skill frontmatters parse; F1-F8 all RESOLVED; 0 BLOCKING, 0 SHOULD_FIX new; anchors orchestrator.md, tech-lead.md, producer.md, story-author.md, 5 projects' phases.md; 0 UNVERIFIED

changed:
  - none

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F1 RESOLVED — grill-plan/SKILL.md:12 declares bare § = this skill; every orchestrator.md ref is prefixed (:17,:21,:34,:39,:42,:51,:52,:84); bare :36 and :98 are the skill's own.
  - F2 RESOLVED — grill-plan/SKILL.md:34 routes facts to the ground-truth phase, lane per phases.md; :38-39 names the not-triggered re-plan; README.md:34 no longer names scout.
  - F3 RESOLVED — orchestrator.md:409-413 states the asking-order exception in loop step 4; grill-plan/SKILL.md:50-51 cites it rather than granting it. see § Step 4 exception
  - F4 RESOLVED — grill-plan/SKILL.md:41-43 now cites an existing trigger (orchestrator.md:514-515, a lane result contradicting an earlier artifact); a ruling that changes the artifact is a re-dispatch at :92-94, not a new trigger.
  - F5 RESOLVED — grill-plan/SKILL.md:58 caps one lane-gap round per human stop, however many slots the revisions take.
  - F6 RESOLVED — grill-plan/SKILL.md:3 and orchestrate-feature/SKILL.md:164-165 both name the design phase's plan, when design fired; :129-130's run-plan go is a distinct, ungrilled step.
  - F7 RESOLVED — orchestrate-feature/SKILL.md:189-190 now reads 'Grill the draft (§ Human stops) and stop', matching the framing note at :185.
  - F8 RESOLVED — grill-plan/SKILL.md:51-52 replaces the restated budget rule with a citation of orchestrator.md § 1 and § 3.
  - Rounds row F1-F8 can close at round 1 of 2; no fix caused a new finding.

skill_calls:
  - none

risks:
  - Outside scope: ARCHITECTURE.md:99-100 paraphrases loop step 4 without the new exception; human-facing, but it now lags orchestrator.md:409-413.
  - Outside scope: claude plugin validate reports LICENSE_MISSING and ICON_MISSING (directory profile only; validation passed).
  - los-tres phases.md:30 puts a human stop on the `ux` design spec; the 'planning artifact' test at orchestrate-feature:163 covers it, but grill-plan:23 names no decisions heading for a UX spec.

## Orchestrator brief
- verdict: PASS. F1-F8 all RESOLVED; no new BLOCKING or SHOULD_FIX; no fix caused a finding.
- handoff: one RESOLVED bullet per finding with its file:line, plus the Rounds note.
- risks: two out-of-scope notes (ARCHITECTURE.md copy of step 4, plugin directory checks) and one observation on the los-tres UX stop.
- sections below: Step 4 exception — the judgment of the new orchestrator.md § 3 step 4 text against authoring.md.

## Step 4 exception

Text judged: orchestrator.md:409-413, "The one exception is an order that only asks: a `ground-truth` order or a question back to the lane that wrote the artifact, dispatched at the stop so the human is asked about decisions rather than facts. Such an order settles nothing the human was going to rule on."

- **Rule 2 (one rule, one home).** The exception lives once, next to the rule it qualifies. grill-plan/SKILL.md:50-51 cites "`orchestrator.md` § 3, step 4" and does not restate it. Grep of PROTOCOL.md, protocol/*.md, both skills and the agent files finds no other statement of "do not dispatch past a stop". ARCHITECTURE.md:99 paraphrases step 4, but it is outside scope and outside the four layers (risks).
- **Rule 9 (rule and exception together; carve-out no broader than its grant).** The exception sits in the granting step itself. It covers the same two order types grill-plan's sorting table sends out at the stop (:34 fact → ground-truth, :35 lane gap → same lane), and nothing more. grill-plan:54 ("asks; it does not answer") and :45-46 (when unsure, it is a human decision) match "settles nothing the human was going to rule on".
- **Consistency with the rest of orchestrator.md.** Loop step 2 order holds: ground-truth precedes framing in § 2. A fact order on a not-triggered ground-truth row is already a re-plan at :516, and grill-plan:38-39 says so. Serial dispatch (§ 3 'Serial by default') is cited at grill-plan:52 and not overridden. decisions.md writing (§ 5) is at grill-plan:83-84 and keeps the `raised by` field (:72).
- **Consistency with orchestrate-feature.** :108-111 summarises the loop as "stop at an unanswered human stop" and names orchestrator.md § 3 as the loop. Stopping still happens: the exception permits asking-orders, not proceeding. § Human stops (:163-166) routes to grill-plan, which cites the exception. Not a contradiction.
- **Consistency with PROTOCOL.md.** No core rule governs human stops. The exception names a phase and a role-relative lane ("the lane that wrote the artifact"), not a project lane, so rule 1 holds.
- **Mechanical check.** check_report.py check_decisions (:923-962) only requires decisions.md once a stop's phase is satisfied. A re-dispatch at the stop does not trip it early.

Anchor: the network's other files (orchestrator.md § 2/3/5/6, tech-lead.md:78-86 `decisions:`, producer.md:205 and story-author.md:42 `## Open decisions`) and the five bound projects' phases.md `Human stop` columns, not the skill under judgment.
