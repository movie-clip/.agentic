REPORT 2026-10-06-lint-v0.8.0-orchestrator/01
status:      DONE
verdict:     FAIL
changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Validation passed. Anchor: protocol/authoring.md (not under edit) + gates.md + git HEAD SKILL.md; 9 BLOCKING, 7 SHOULD_FIX; 4 UNVERIFIED premises.

contract_notes:
  - orchestrator.md:248-249 says nothing asks an abandoned run for gate verdicts, but check_report.py:295 runs check_authoring_gate on ABANDONED too; an abandoned run with a non-empty pack-corrections.md still fails without protocol-lint in gates:.
  - SKILL.md:26-27 says the hook asks on an edit outside the run dir; orchestrator_edit_gate.py:95 tests the project's whole runs/ dir, so an edit inside another run's dir passes unprompted.
  - orchestrator.md:252-254 says every main-session edit is put to the human; the hook (orchestrator_edit_gate.py:84-99) asks only on Edit/Write/NotebookEdit/MultiEdit outside runs/ and on Bash git rm/mv.

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 (Two instructions may not disagree): orchestrator.md:179 'Name every gate ... every run' vs new orchestrator.md:248-249 'nothing asks an abandoned run for gate verdicts'. Satisfy: scope line 179 to runs that close, or state the ABANDONED exception there.
  - BLOCKING rule 2 (One rule, one home): SKILL.md:85-87 restates the abandon procedure that orchestrator.md:245-251 now defines (ruling in decisions.md, status ABANDONED, next: none - ABANDONED). Satisfy: the step cites orchestrator.md § 1 'A run that will not finish is abandoned' and restates nothing.
  - BLOCKING rule 2: SKILL.md:201-209 restates orchestrator.md:468-492 (Rounds row first, SendMessage resume, 2-round cap, caused by, re-run only the failed gate, non-blocking to Open); the SendMessage rule entered both files in this edit. Satisfy: replace with a cite to § 3 'A gate that fails routes'.
  - BLOCKING rule 9: SKILL.md:124-126 says escalate 'only' on BLOCKED-not-input or a second CR round; authoring.md:199-202 adds a third trigger (a gate passed what a later gate caught). Satisfy: cite authoring.md 'Escalating a single dispatch' instead, or list all three without 'only'.
  - BLOCKING rule 2 (dispatcher rule -> orchestrator.md): old SKILL.md:383-385 'a third round ... escalation to the user' was dropped; new SKILL.md:205 and orchestrator.md:480 state the cap with no action. Only gates.md:82-83 has it, not in the orchestrator's set (PROTOCOL.md:11-13).
  - BLOCKING rule 2, fix for the item above: add the at-cap action (stop, hand to the human, no third round) to orchestrator.md § 3 'A gate that fails routes' step 3, and have SKILL.md:205 cite it.
  - BLOCKING rule 1 (four-layer split): the agnostic skill names a project at SKILL.md:24-25 ('tradingview's compile.md') and SKILL.md:193-194 ('tradingview's compile check'). Satisfy: 'acceptance evidence the profile assigns to you' and 'the profile's external acceptance check', no project name.
  - BLOCKING rule 9: SKILL.md:193-195 runs external acceptance 'right after the first build dispatch'; phases.md:124-126 runs it after each build dispatch changing a .pine file, and again before close. Satisfy: SKILL.md defers timing to the profile ('where the profile places it, before the gates').
  - BLOCKING rule 2: the enumerated main-session write boundary at SKILL.md:22-28 is order-independent, so a rule, and lives only in the skill; orchestrator.md § 7 (:740-747) has no list, yet orchestrator_edit_gate.py:22 cites § 7 as its rule. Satisfy: move the list into § 7; the skill cites it.
  - BLOCKING rule 9: phases.md:136-137 lists compile.md in the inputs of the quant-audit, integration and close orders; phases.md:95-97 says review reads compile.md. Satisfy: add review (when it fires) to the list at 136-137.
  - SHOULD_FIX rule 8 (Writing for the reader): orchestrator.md:254-255 'On 2026-10-06, four of the five ledgers...' is provenance; move it to the commit message.
  - SHOULD_FIX rule 8: orchestrator.md:483-486 'Run 2026-10-05-range-projection-quarter-anchor re-ran...' is provenance, and names one project's run in the protocol layer; move it to the commit message.
  - SHOULD_FIX rule 8: phases.md:128-131 run history is provenance; keep the why at 131-133 ('The gates read the source...') and move the rest to the commit.
  - SHOULD_FIX rule 8: SKILL.md bullets at lines 82, 146, 175, 183, 188, 192, 197, 201 exceed 200 characters, and several carry more than one fact.
  - SHOULD_FIX dropped rule (DoD listing): old SKILL.md:181-182 build order (contracts before consumers, implementation before tests, docs last) is in neither the new skill nor orchestrator.md/PROTOCOL.md; only portfolio phases.md:36 carries part.
  - SHOULD_FIX dropped rule (DoD listing): old SKILL.md:247 'If no downstream order exists to absorb a contract note, create it' appears in neither the new skill nor orchestrator.md § 1 Open.
  - SHOULD_FIX dropped rule (DoD listing): old SKILL.md:167-168 'say why [an escalation] at close-out' and old :290-291 / :339-340 (test result kept out of findings; no plan-index write at specification) are not carried.
  - INFO, not a finding (DoD 2): every cited section (orchestrator.md §§ 1-7, core § 2, § 5) exists and says what SKILL.md claims; check_report/ledger/runs flags cited resolve.

skill_calls:
  - none

risks:
  - UNVERIFIED: that SendMessage is available to the main session and resumes a finished subagent with its context (orchestrator.md:477, SKILL.md:202).
  - UNVERIFIED: 'Claude Code itself now lets subagents nest' (orchestrator.md:645); not checked against Claude Code docs.
  - UNVERIFIED: the run-history claims at phases.md:128-131 and orchestrator.md:483-486; the 2026-10-05 run dir was not opened.
  - UNVERIFIED: that tradingview's .claude/settings.json wires orchestrator_edit_gate.py; the bound repo was not opened.
  - Out of scope: authoring.md:60-64 (order-independent text is a rule, belongs in protocol) and authoring.md:395-396 (repo-agnostic sequencing belongs in the skill) give different placement tests.
  - Out of scope: this run's run.md has no budget: line (runs.py shows spent 1/?).
  - Not judged a finding: SKILL.md:3 description examples are portfolio phrasing (Risk tab, US-35.3); pre-existing, and examples rather than declared lanes or triggers.
  - Bound through C:\projects\investments\tradingview\.agentic.json per the order's binding note; cwd .agentic has none (TD-17).
