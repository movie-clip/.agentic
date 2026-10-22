REPORT 2026-10-22-grill-plan-skill/01
status:      DONE
verdict:     FAIL
verification:
  command:   claude plugin validate ./plugins/agentic-core; yaml.safe_load on both SKILL.md frontmatters
  result:    PASS
  detail:    validate passed (only LICENSE/icon directory notes); both skill frontmatters parse; 8 BLOCKING, 0 SHOULD_FIX; anchors orchestrator.md, producer.md, story-author.md, tech-lead.md, portfolio+budget phases.md; 3 UNVERIFIED

changed:
  - none

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1 rule 9 — grill-plan/SKILL.md:21,37,46,89 bare § 3/§ 4 collide with the skill's own numbered § 3/§ 4; prefix each with orchestrator.md. see § Findings
  - BLOCKING F2 rules 9+1 — grill-plan/SKILL.md:32 sends facts to a `scout` order distinct from ground-truth; orchestrator.md:738 says an unsourced needed claim IS ground-truth. see § Findings
  - BLOCKING F3 rule 9 — grill-plan/SKILL.md:45 dispatches before the human round; orchestrator.md:408-409 says stop and ask, do not dispatch past an unanswered decision. see § Findings
  - BLOCKING F4 rule 2 — grill-plan/SKILL.md:88-89 adds a re-plan trigger (a ruling contradicting the plan) absent from orchestrator.md:507-513's list of four. see § Findings
  - BLOCKING F5 rule 9 — grill-plan/SKILL.md:53 "one lane-gap round per artifact" resets, since :50-51 makes each revision a new slot, i.e. a new artifact. see § Findings
  - BLOCKING F6 rule 9 — build-go stop: grill-plan:3 grills the tech lead's plan, orchestrate-feature:129-130 presents the run plan; :163-165 "the plan" fits both. see § Findings
  - BLOCKING F7 rule 9 — orchestrate-feature/SKILL.md:186-190 specification note still says hand the draft and resolve escalated decisions; :163-165 says grill it instead. see § Findings
  - BLOCKING F8 rule 2 — grill-plan/SKILL.md:47 restates orchestrator.md § 1/§ 3 (each dispatch a row, counts toward budget) without citing it. see § Findings
  - README.md:34 names `scout`; if F2 is fixed by routing facts to ground-truth, re-word the tree comment to match.

skill_calls:
  - none

risks:
  - UNVERIFIED: grill-plan:22 "the plan's decisions section" — tech-lead.md:175,188 describe decisions in the plan body but fix no heading a reader can search for.
  - UNVERIFIED: ground-truth is bound to `recon` (scout) only in the portfolio and budget phases.md I opened; other bound projects not checked.
  - UNVERIFIED: no recon capability pack opened, so whether scout's pack covers grill's fact orders is unconfirmed.
  - Outside scope: `claude plugin validate` reports LICENSE_MISSING for plugins/agentic-core (directory profile only; validation itself passed).

## Orchestrator brief
- verdict: FAIL, 8 BLOCKING findings, all in the three scoped files; no SHOULD_FIX.
- F1, F5, F8 are local wording fixes in grill-plan/SKILL.md.
- F3 and F4 put new rules into a skill; the fix that satisfies rule 2 edits protocol/orchestrator.md § 3, which must then join the re-lint scope.
- F2 re-routes fact questions through the ground-truth phase; README.md:34 follows it.
- F6, F7 are orchestrate-feature/SKILL.md consistency fixes.
- sections below: Findings — each finding's rule, anchor, conflict and what would satisfy it.

## Findings

**F1 — rule 9 (Two instructions may not disagree).** grill-plan/SKILL.md numbers its own sections 1–5, then cites orchestrator.md sections by bare number. :21 "Read the artifact the way § 4 says" (meant orchestrator.md § 4; the skill's § 4 is Human rounds). :37 and :89 "re-plan (§ 3)" (the skill's § 3 is the lane-gap step). :46 "§ 3's parallel conditions". :34 "§ 4's rounds" is the skill's own. A reader cannot tell which file a bare § resolves to. *Satisfied by:* writing `orchestrator.md § n` at :21, :37, :46, :89 (or un-numbering the skill's headings).

**F2 — rule 9, and rule 1 (four-layer split).** grill-plan/SKILL.md:32 routes "a fact" to "a `scout` order, or `ground-truth` if it is a claim about whether something works", making fact-finding an off-phase dispatch. orchestrator.md:738 says "If you need a claim and have neither, that is the `ground-truth` trigger. The phase exists for this and nothing else", and orchestrator.md:332 defines ground-truth as what is true in the repo. The lane that fills ground-truth is the profile's (portfolio and budget phases.md: `recon`), not a name a skill may hard-code. *Satisfied by:* routing every fact node to the `ground-truth` phase's lane as `phases.md` binds it, and stating that if that row was `not triggered` this is a re-plan per orchestrator.md § 3 ("a phase recorded as not triggered turns out to be triggered").

**F3 — rule 9.** grill-plan/SKILL.md:45-47 "Dispatch the fact orders and the lane-gap order before the human round that depends on them." orchestrator.md:408-409 (loop step 4): "If that phase carries a human stop the human has not given, stop and ask. Do not dispatch past an unanswered decision"; orchestrate-feature/SKILL.md:110 repeats "stop at an unanswered human stop". At a stop the two direct different actions and neither says which wins. *Satisfied by:* stating the carve-out where the rule lives — orchestrator.md § 3 step 4, e.g. dispatches that question the stop's own artifact (its lane re-dispatched, ground-truth facts) are not "past" it — with grill-plan citing that step; add protocol/orchestrator.md to the re-lint scope. A carve-out only in the skill would be broader than the section that grants it.

**F4 — rule 2 (One rule, one home; "A skill is not a fifth place to put a rule").** grill-plan/SKILL.md:88-89 "A ruling that contradicts the plan is a re-plan (§ 3)". orchestrator.md:507-513 lists exactly four re-plan triggers; a human ruling is none of them (the second is "a lane's result contradicts"). The sentence would be true in any run order, so it is a rule, and it is new. "the plan" is also ambiguous between the ledger `plan:` and the planning artifact. *Satisfied by:* adding the trigger to orchestrator.md § 3 "Re-plan on evidence" (naming the ledger plan) and citing it here, or deleting the sentence if the existing triggers already cover the case.

**F5 — rule 9.** grill-plan/SKILL.md:50-51 "The lane returns a revised artifact as a new slot" and :53 "One lane-gap round per artifact." Each revision is a new slot, hence a new artifact, so the cap can be read as resetting on every round — the cap-by-naming failure gates.md § 4 guards against. *Satisfied by:* "One lane-gap round per human stop" (or "per planning artifact, counting its revisions").

**F6 — rule 9.** Which artifact is grilled at the build go is stated three ways. grill-plan/SKILL.md:3: "the tech lead's plan before the build go". orchestrate-feature/SKILL.md:129-130: "Before `build`, present the plan and wait for a go: the lane list, one line of intent for each, the dispatch count and the budget" — the orchestrator's run plan, not a lane artifact. orchestrate-feature/SKILL.md:163-165: "the plan before the build go", which fits either. When design did not fire there is no tech-lead plan to grill. *Satisfied by:* naming it in both skills, e.g. "the design phase's plan, when design fired", and saying that :129-130's run-plan go is unchanged (or grilled too).

**F7 — rule 9.** orchestrate-feature/SKILL.md:188-190 (specification note): "Hand the draft to the user, and get every open decision it escalates resolved and written into `decisions.md`". :163-165 now says a stop handing over the story draft "runs the `grill-plan` skill on it instead of relaying its open decisions as a list", and grilling also sends lane gaps back to the story lane, which the note does not allow for. The framing note (:184) was updated; this one was not. *Satisfied by:* rewording :188-190 to "Grill the draft (§ Human stops)", matching :184.

**F8 — rule 2.** grill-plan/SKILL.md:47 "Each dispatch is a ledger row and counts toward `budget`." restates orchestrator.md § 1 (:125 "`spent` increments when you dispatch") and § 3 (:458) without citing them. *Satisfied by:* replacing it with a citation, e.g. "(orchestrator.md § 3, 'The budget is derived')".

Judged and not filed: § 2's sorting table does not restate gates.md § 4 (that cap governs change requests on gate findings, and a lane-gap order is not one); :77-78 cites orchestrator.md § 5 for decisions.md and is consistent with it; :16-17 cites orchestrator.md § 7 correctly; producer.md § Open decisions (:205-207) and :229 match § 2's "human decision" row and :36-38; the README tree row is correct; frontmatter parses.
