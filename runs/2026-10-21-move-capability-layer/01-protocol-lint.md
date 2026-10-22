REPORT 2026-10-21-move-capability-layer/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:/projects/investments/.agentic/plugins/agentic-core
  result:    PASS
  detail:    Validation passed, 0 frontmatter errors. 18/18 scoped files judged: 9 BLOCKING, 0 SHOULD_FIX. Anchors: check_report.py, check_network_edit.py, 6 bound repos' .agentic.json/.gitignore, run.md, and the other agent files for authoring.md and protocol-linter.md. 1 UNVERIFIED premise.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1, rule 9: authoring.md:389-391 says fix a lint FAIL in the main session, but orchestrator.md § 3 and § 7 (752-756) say a FAIL goes to the owning lane and network edits are work orders. see § Findings
  - BLOCKING F2, rule 2: orchestrator.md:203-205 says packs are project docs that owe no gate. authoring.md:404-405 already states this rule. see § Findings
  - BLOCKING F3, rule 9: authoring.md:405-408 requires a protocol-lint at onboarding but never says where that run is filed. orchestrator.md:17-20 and 201-203 then leave its verdict unaccounted. see § Findings
  - BLOCKING F4, rule 2: the rule that pack-corrections.md exists only when a correction applies appears twice, at orchestrator.md:207-211 and packs.md:16-19. see § Findings
  - BLOCKING F5, rule 2: packs.md:23-26 restates the commit rule from orchestrator.md § 8, and the copy has drifted. It drops "only once build has fired" (orchestrator.md:782-784). see § Findings
  - BLOCKING F6, rule 9: orchestrator.md:215-217 says check_report.py checks gates: against pack-corrections.md. The script no longer does, and the same section's 201-205 says corrections owe no gate. see § Findings
  - BLOCKING F7, rule 2: orchestrator.md:263-265 puts a rule about gate reports in the orchestrator-only file, and designer.md:120-122 restates it. That breaks orchestrator.md:2 ("nothing here is restated in any agent file"). see § Findings
  - BLOCKING F8, rule 2: agentic-protocol/SKILL.md:43-46 restates the projectDir definition from PROTOCOL.md:34-37. The skill needs agenticRoot to find the protocol, but not projectDir. see § Findings
  - BLOCKING F9, rule 5: the ## Contents of authoring.md (11-28) does not list the new § "Linting a network edit" at line 375. see § Findings

skill_calls:
  - none

risks:
  - UNVERIFIED: authoring.md:400 assumes the lanes' Grep/Glob honour the repo's .ignore, so old reports are skipped. I did not test it.
  - plugin validate printed a LICENSE_MISSING notice under the directory profile. It is about plugin.json/LICENSE, outside scope, and not a parse error.
  - The order's input C:\projects\investments\impact\.agentic.json does not exist. I used C:\projects\impact\.agentic.json, which is at the repo root as the order described.
  - authoring.md and protocol-linter.md are subjects as well as my anchor. Both were judged against the other files, not themselves (gates.md § 2). The only change to protocol-linter.md (its description) agrees with check_network_edit NETWORK.

## Orchestrator brief
Verdict FAIL, with 9 BLOCKING findings and no SHOULD_FIX. The main session that wrote the edit owns every fix (authoring.md § "Linting a network edit" step 3).
Explicit checks: no scoped file still points at `<agenticRoot>/projects/` or `projects/<project>/` (grep returned nothing). The run location and the retention rule each have one home. The protocol-lint trigger does not (F2, F3). The bind text resolves for impact and for protocol-linter from .agentic.
§ Findings holds F1-F9. Each finding gives the rule, the file:line, and what would satisfy it.
§ Explicit checks holds the evidence for the four checks in definition_of_done.

## Findings

### F1 — rule 9, "Two instructions may not disagree" (a rule split from its exception)
- Where: protocol/authoring.md:377-378 and 389-391, against protocol/orchestrator.md:479-499 (§ 3, "A gate that fails routes") and 752-756 (§ 7, "What the main session writes").
- What is wrong: authoring.md says network files are edited in the main session, and that a lint FAIL is fixed there too. orchestrator.md § 3 says each FAIL becomes a change request (CR) and goes to the lane that owns the file. § 7 says "every other edit to the bound repo or the network is a work order".
- Why it matters: the main session running a lint run reads both files, because step 1 tells it to use the ledger shape from orchestrator.md § 1. Neither file says which one wins.
- Also: step 3 cites core § 5 for the two-round cap, but the cap lives in gates.md § 4 and orchestrator.md § 3.
- What would satisfy it: in authoring.md step 3, state that for a run in `<agenticRoot>/runs/` this step replaces orchestrator.md § 3's CR routing and § 7's boundary. Cite gates.md § 4 for the cap.

### F2 — rule 2, "One rule, one home"
- Where: protocol/orchestrator.md:203-205 ("A project's packs are project docs: a correction applied to them is reviewed in the pull request … and owes no gate") and protocol/authoring.md:404-405 ("The profile and packs are project docs … an edit to them owes no `protocol-lint`").
- What is wrong: the same rule is stated in two protocol files.
- What would satisfy it: delete orchestrator.md:203-205 after the `authoring.md` citation, so orchestrator.md only points to authoring.md.

### F3 — rule 9, "Two instructions may not disagree" (a rule split from its exception)
- Where: protocol/authoring.md:405-408 (the onboarding exception: "dispatch `protocol-linter` once over a new profile"), against protocol/orchestrator.md:17-20 and 201-203.
- How the two files combine:
  - orchestrator.md:17-20 files every run under `<projectDir>/runs/`, except runs that lint edits to the network itself.
  - orchestrator.md:201-203 says protocol-lint is "owed by lint runs in `<agenticRoot>/runs/`", and that a project's ledger does not mention it.
  - An onboarding lint is not a network edit, so by these rules its run goes to `<projectDir>/runs/`. There, check_report.py takes the owed gates from the profile, which does not declare protocol-lint (check_report.py:775-807). The verdict is then owed by nothing.
- What would satisfy it: authoring.md § "Adding a project" says where the onboarding lint run is filed (for example, `<agenticRoot>/runs/`, as in § "Linting a network edit"). orchestrator.md:201-203 covers that case by citation.

### F4 — rule 2, "One rule, one home"
- Where: protocol/orchestrator.md:207-211 and protocol/packs.md:16-19.
- What is wrong: both files state the same three things: pack-corrections.md is created only on the first correction; the lanes' `pack_corrections: - none` is the record that they looked; and a file opened to say "nothing here" dispatches an order with nothing to do. This edit rewrote both copies.
- What would satisfy it: keep the rule in orchestrator.md, since the orchestrator opens the file. Cut packs.md step 2 to "…creating the file on the first one (`orchestrator.md` § 1)."

### F5 — rule 2, "One rule, one home" (a copy that has already drifted)
- Where: protocol/packs.md:23-26.
- What is wrong: it says "where the profile declares a tracker the corrected packs are committed to the run's branch". orchestrator.md:782-784 says the branch exists only once `build` has fired; otherwise close-lane edits stay uncommitted for the human. The packs.md copy leaves out that condition.
- What would satisfy it: replace packs.md:23-26 with a pointer only: "Committing them is the orchestrator's, per `orchestrator.md` § 8."

### F6 — rule 9, "Two instructions may not disagree"
- Where: protocol/orchestrator.md:215-217 ("…matches it against the Artifacts rows and against `pack-corrections.md` and fails close-out…").
- What is wrong: this is left over from the removed protocol-lint trigger.
  - `check_gates` (check_report.py:683-713) no longer reads pack-corrections.md. The HEAD version's `check_authoring_gate` is gone.
  - Lines 201-205 of the same section now say corrections owe no gate.
- Why it matters: the orchestrator reads both statements and gets two answers about whether pack-corrections.md affects `gates:`.
- What would satisfy it: delete "and against `pack-corrections.md`" from line 216.

### F7 — rule 2, "One rule, one home" (placement: "chosen by who needs it")
- Where: protocol/orchestrator.md:263-265 ("…so a gate's report states each check's result in words"), plugins/agentic-core/agents/designer.md:120-122, and protocol/orchestrator.md:2.
- What is wrong: this rule is about what a gate's report must contain. It sits in the orchestrator-only extension, and designer.md restates it. orchestrator.md:2 promises that nothing in it is restated in any agent file.
- What would satisfy it: cut the "so a gate's report states…" clause from orchestrator.md:264-265 and keep the fact about the images. designer.md keeps its sentence, because this is the designer's craft.

### F8 — rule 2, "One rule, one home" (a skill that re-states a protocol rule)
- Where: plugins/agentic-core/skills/agentic-protocol/SKILL.md:43-46, against PROTOCOL.md:34-37.
- What is wrong: the edit adds the projectDir definition ("this project's own folder: profile, packs and runs") and its resolution rule to the skill. This copies PROTOCOL.md § 1. The skill only needs `agenticRoot` to locate PROTOCOL.md, and its own § "Why these files hold no copy of anything" forbids the copy.
- What would satisfy it: drop the projectDir clause from lines 44-46 and add "the rest of binding is `PROTOCOL.md` § 1". The JSON example may stay.

### F9 — rule 5, Index block (authoring.md § "Indexing a pack or profile": a full-read file's `## Contents` lists its whole scope)
- Where: protocol/authoring.md:11-28.
- What is wrong: `## Contents` lists ten sections but not the new § "Linting a network edit" (line 375).
- What would satisfy it: add a bullet, for example "**Linting a network edit** — the run, the order and the close for an edit to network files".

## Explicit checks
- No pointer to the old layout: `grep -E "projects/|<project>"` over all 18 scoped files returns nothing.
- Run location: project runs live in orchestrator.md § 1. Network lint runs live in authoring.md § "Linting a network edit", and orchestrator.md:18-20 cites it. One home each.
- Retention: orchestrator.md § "Closed runs are pruned" (249-261) only. runs/README.md and orchestrator.md:244 cite it.
- protocol-lint trigger: not one home. See F2 and F3.
- Bind from impact: the walk-up from C:\projects\impact\Impact\… reaches C:\projects\impact\.agentic.json.
  - agenticRoot `../investments/.agentic` resolves to C:\projects\investments\.agentic.
  - projectDir `agentic` resolves to C:\projects\impact\agentic, which holds project.md, phases.md, capabilities/ and runs/.
- Bind from .agentic: `{"agenticRoot": "."}` resolves to .agentic. protocol-linter.md's bind reads no projectDir, which matches PROTOCOL.md:38-40.
- All six bound repos (budget, datoro, los-tres, portfolio, tradingview, impact) have `projectDir: "agentic"` and `agentic/runs/**/*.png` in .gitignore.
- check_report.py matches authoring.md:384-385 and 424-428:
  - `_NETWORK_PHASES` is used when PROTOCOL.md sits three levels above run.md.
  - `project_dir:` is read first, then the run dir's path.
  - `_NO_PROFILE` fails close-out when no profile is found.
- check_network_edit.py matches authoring.md:386-388: the NETWORK patterns, plus path/basename matching over `runs/*/*protocol-lint.md`. `--strict` exists.
