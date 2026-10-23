REPORT 2026-10-22-run-review-fixes/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core ; python scripts/check_report.py <this file> --lane protocol-lint
  result:    PASS
  detail:    plugin validate passed, 0 frontmatter errors; 7 files judged against authoring.md; 6 BLOCKING, 1 SHOULD_FIX; 2 UNVERIFIED premises. Anchor: authoring.md, plus untouched PROTOCOL.md, orchestrator.md and profile lane maps for rule 9.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1, rule 1 (four-layer split): grill-plan/SKILL.md:35 names `mvp.md`, a los-tres file, in an agnostic skill. Fix: say "a repo doc the profile or CLAUDE.md names as authoritative (product spec, decision record)". see § Findings
  - BLOCKING F2, rule 9: reviewer.md:83-85 tells CHECK mode to write scratch files outside run_dir and remove them; PROTOCOL.md:146-151 calls that a violation and :198 says no lane deletes. Fix: carve-out in core § 3 or reword CHECK. see § Findings
  - BLOCKING F3, rules 2 and 9: grill-plan/SKILL.md:58-62 extends orchestrator.md:491-493's SendMessage preference (fixes only) to lane gaps, and restates its "still a new slot" sentence. Fix: generalise § 3 step 2 there; skill cites it. see § Findings
  - BLOCKING F4, rules 2 and 9: grill-plan/SKILL.md:108-110 records an unobjected item as a decisions.md ruling; orchestrator.md:708-709 says one entry per decision the human actually resolved, in their words. Fix: put the form in orchestrator.md § 5. see § Findings
  - BLOCKING F5, rule 9: PROTOCOL.md:36-37 says use `agentic_root:` over resolving, but reviewer.md:13-15 and tech-lead.md:20-22 say resolve, and run first, before PROTOCOL.md is found. Fix: add the agentic_root clause to each Bind first. see § Findings
  - BLOCKING F6, rule 9: orchestrator.md:743-746 sends run-to-know recon to reviewer CHECK; the profile lane maps the orchestrator also reads map recon to `scout` alone, and neither says which wins. Fix: one precedence clause in § 6. see § Findings
  - SHOULD_FIX S1, rule 8: orchestrator.md:747 "Skipping it" now follows "Never a general-purpose agent", so "it" reads as that agent, not the phase. Fix: move the inserted two sentences after the paragraph ends (line 755).

skill_calls:
  - none

risks:
  - reviewer.md:60 (untouched) says the verdict goes "in `verification.result`"; core § 3 and § 6 put it in `verdict`. Pre-existing, outside the diff, so not part of this verdict.
  - reviewer.md CHECK mode does not say what `verification.result` is when a claim is REFUTED; core § 7 makes DONE require PASS, so a lane may report DONE + FAIL or PARTIAL inconsistently.
  - F5's resolve wording also sits in the other ten agent files' Bind first sections, outside this order's scope; the fix needs them added to scope.
  - F6's other side is in los-tres/portfolio/budget agentic/project.md lane maps (recon -> scout), outside scope and not network files.
  - UNVERIFIED: that the orchestrator's main session can resume a returned subagent by id with SendMessage (grill-plan:59, orchestrator.md:491).
  - UNVERIFIED: that a dispatched reviewer has a session scratchpad directory to run in (reviewer.md:83).
  - plugin validate reports LICENSE_MISSING and ICON_MISSING directory checks against plugin.json, outside scope and not frontmatter errors.

## Orchestrator brief
- Verdict FAIL: six BLOCKING findings, one SHOULD_FIX; all fixes are authoring in the main session (authoring.md § "Linting a network edit", step 3).
- § Findings holds each finding with both cited locations and the wording that would satisfy it.
- F5 and F6 need files outside this order's scope (other agent files; profiles) to be fully fixed; the in-scope half is named in each.

## Findings

**F1 — rule 1, four-layer split.** `plugins/agentic-core/skills/grill-plan/SKILL.md:35`: "`mvp.md`, `CLAUDE.md` or a decision record". `mvp.md` is one bound repo's file (los-tres); the Skill layer may not carry a project's paths (authoring.md § "The four-layer split", and § "Adding a project": "The `plugins/` layer is untouched"). In budget or portfolio the row names a file that does not exist. Satisfied by: "a repo doc — `CLAUDE.md`, or a product spec or decision record the profile names — already answers it".

**F2 — rule 9, instructions agree.** `reviewer.md:83-85`: "Run everything in your scratchpad or the OS temp directory ... remove only what you created." `PROTOCOL.md:146-151`: Write is for "exactly one purpose: this artifact", and a read-only lane (`reviewer` is named) "writing anywhere else ... is a protocol violation". `PROTOCOL.md:198`: "No lane has a delete tool, deliberately". A CHECK-mode reviewer reads both, and the core states no exception. Satisfied by either: (a) a carve-out sentence in core § 3 — "`reviewer` in CHECK mode may write and remove scratch files in a temp directory outside every repo; nothing else" — with reviewer.md citing it; or (b) CHECK mode restricted to running commands that write nothing outside the temp dir, and the "remove" clause stated as the core's exception.

**F3 — rules 2 and 9.** `grill-plan/SKILL.md:58-62`: "When the lane's agent id is still live, send the order with `SendMessage` ... as `orchestrator.md` § 3 prefers for fixes ... It is still a new slot with its own `report_to`, Artifacts row and head." `orchestrator.md:491-493` grants the preference only for a fix after a gate FAIL, and the last sentence is a verbatim copy. A rule true in any run order belongs in the protocol (authoring.md § "One rule, one home", skill paragraph); a carve-out may not be broader than the section granting it (§ "Two instructions may not disagree"). Satisfied by: generalise orchestrator.md § 3 step 2's resume sentence to "any order back to the lane that wrote the artifact — a fix or a lane-gap question", and in grill-plan replace lines 58-62's two sentences with "Dispatch it as `orchestrator.md` § 3 step 2 says for a returning lane."

**F4 — rules 2 and 9.** `grill-plan/SKILL.md:108-110`: "An assumed item they let stand is an entry too: `ruling: not objected (assumed list, round <n>)`, `by: the human`." `orchestrator.md:708-709`: "One entry per decision the human actually resolved, the ruling in **their words**". The orchestrator reads both; the entry shape is a protocol rule (§ 5 owns it) and the skill now defines a second form. Satisfied by: add the not-objected form to orchestrator.md § 5 beside "in their words" (e.g. "an item on an assumed list the human did not object to is recorded with `ruling: not objected (assumed list, round <n>)`, quoting the list item"), and have grill-plan cite § 5 rather than define it.

**F5 — rule 9.** `PROTOCOL.md:36-37`: "When your work order carries `agentic_root:`, that absolute path is `agenticRoot`; use it rather than resolving one." `reviewer.md:13-15` and `tech-lead.md:20-22`: "Walk **up** from cwd for `.agentic.json`, resolve `agenticRoot` and `projectDir` against the directory that holds it, then read ... `<agenticRoot>/PROTOCOL.md`". The precedence is stated only in a file the lane locates by first applying the losing instruction, which is the failure orchestrator.md:732-733 says this edit exists to stop. Satisfied by: in each agent's Bind first, "take `agenticRoot` from your order's `agentic_root:` when it carries one; otherwise walk up from cwd ...". In scope: reviewer.md, tech-lead.md; the other ten agent files carry the same sentence (risks).

**F6 — rule 9.** `orchestrator.md:743-746`: "A claim that only running something can settle ... is a `recon` order to `reviewer` in `CHECK` mode". The orchestrator also reads the profile's lane map, which binds lanes to agents (orchestrator.md:337-341 — "the lanes that fill them are not [protocol]"); los-tres `agentic/project.md:116`, portfolio `:79` and budget `:98` all read `recon | scout`. Neither text says which wins. Satisfied by: one clause in orchestrator.md § 6 — "whatever agent the profile's lane map names for `recon`" — or adding `reviewer` (CHECK) to each profile's recon row, so the protocol names the lane and the profile the agent.

**S1 — rule 8, SHOULD_FIX.** `orchestrator.md:747`: "Skipping it on the strength of an intake grep" now directly follows "Never a `general-purpose` agent: ... cannot check its model." The antecedent of "it" was the phase. Satisfied by moving the two inserted sentences (lines 743-747) to after "where it hurts." (line 755), or opening line 747 with "Skipping the phase".
