REPORT 2026-10-22-grill-plan-rebuild/01
status:      DONE
verdict:     FAIL
changed:
  - none

verification:
  command:   claude plugin validate ./plugins/agentic-core; git diff -- plugins/agentic-core/skills/grill-plan/SKILL.md; grep -rn -i grill (network, runs excluded)
  result:    PASS
  detail:    validate passed (0 errors on grill-plan; LICENSE/icon directory notes only). 1 BLOCKING finding (authoring.md § Two instructions may not disagree), 0 SHOULD_FIX. Anchor: authoring.md, orchestrator.md § 3 step 4, orchestrate-feature § Human stops. 0 UNVERIFIED premises.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1 (authoring.md § Two instructions may not disagree): grill-plan/SKILL.md:59-60 "what it leaves open goes to the human" vs § 2:35 (fact -> ground-truth). See § F1.
  - F1 fix: scope the clause to lane gaps and keep facts on ground-truth, e.g. "...no lane-gap round of its own; a fact node it raises still goes to ground-truth (§ 2)." See § F1.

skill_calls:
  - none

risks:
  - grill-plan frontmatter sets neither user-invocable: false nor disable-model-invocation, so /grill-plan stays human-invocable; no network prose says the human may call it (grep: ARCHITECTURE.md:102, README.md:34 tie it to stops).
  - Edit 2 (description) checked: no remaining text in PROTOCOL.md, protocol/, ARCHITECTURE.md, README.md or skills/ offers grill-plan outside orchestrate-feature's human stops.
  - claude plugin validate reports LICENSE_MISSING / ICON_MISSING for the plugin directory profile; outside scope and not an authoring rule.

## Orchestrator brief
One BLOCKING finding, F1 (rule 9), on the § 3 edit. Edit 2 (description) is clean:
nothing in the network still says the human can invoke grill-plan directly.
The rebuild sentence agrees with § 3 "One lane-gap round per human stop", with
§ 2's settled-by-decisions rule, with orchestrator.md § 3 step 4 and with
orchestrate-feature § Human stops — except for fact nodes. Sections below: F1.

## F1
- **Rule:** authoring.md § "Two instructions may not disagree" — an exception
  may not be broader than the section that grants it.
- **Where:** plugins/agentic-core/skills/grill-plan/SKILL.md lines 57-60, the
  new sentence "The revision gets no lane-gap round of its own; what it leaves
  open goes to the human."
- **Conflict:** the same edit says "nodes it raised join" the rebuilt tree. A
  joined node that is a **fact** is, per § 2 line 35, sent to the
  `ground-truth` phase, and § 2 lines 39-40 make that a re-plan. The new clause
  sends everything the revision leaves open to the human. Both apply to one
  situation (a revision raises a repo-fact question) and direct different
  actions. The carve-out being granted is "no second lane-gap round" (§ 3
  line 62 caps lane gaps only), but its wording covers facts too. Sending a
  fact to the human also runs against orchestrator.md § 3 step 4, whose
  stop-time exception exists "so the human is asked about decisions rather
  than facts".
- **What satisfies it:** limit the clause to lane gaps and state where facts
  go. One sentence does it, for example: "The revision gets no lane-gap round
  of its own: a lane gap it leaves open or raises goes to the human, and a
  fact node it raises goes to `ground-truth` (§ 2)." If the author means
  facts to go to the human as well, the sentence has to say so and name
  § 2 as the rule it overrides. The second clause also repeats line 63
  ("Gaps still open after it become human questions") without its labelling
  requirement. Pointing at that paragraph instead of restating it avoids a
  second copy.
