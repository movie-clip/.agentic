REPORT 2026-10-21-lint-wording-followup/02
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:/projects/investments/.agentic/plugins/agentic-core
  result:    PASS
  detail:    Validation passed, 0 frontmatter errors. F1 RESOLVED (protocol/packs.md:20). 4/4 edits clean, 0 BLOCKING, 0 SHOULD_FIX, 1 UNVERIFIED. Files: PROTOCOL.md, protocol/authoring.md, protocol/packs.md, protocol/orchestrator.md. Anchors: orchestrator.md § 8:783-785, orchestrate-feature/SKILL.md:215,236,256, docs-engineer.md:4.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F1 RESOLVED: protocol/packs.md:20 now reads "Who commits them is `orchestrator.md` § 8's rule." It states no condition, so it cannot drop § 8's `build` clause. see § F1 recheck
  - No new rule 9 contradiction: § 8:783-785, SKILL.md:215, :236 and :256 all carry or point at the build condition. packs.md now defers to them and directs no commit action of its own.
  - No new rule 2 duplicate: the commit rule's only home is orchestrator.md § 8. packs.md and SKILL.md:256 both point at it and restate none of it.
  - PROTOCOL.md:99-100, authoring.md:402-404 and orchestrator.md:251-252 were judged clean in 01. The F1 fix does not touch them, so they are not reopened, per non_goals.

skill_calls:
  - none

risks:
  - UNVERIFIED: carried from 01: authoring.md:406 assumes lanes' Grep/Glob honour .ignore. Not tested here.
  - plugin validate printed LICENSE_MISSING and ICON_MISSING directory-profile checks. Both are outside scope, and neither is a parse error.

## Orchestrator brief
Verdict PASS. F1 from 01 is resolved by the pointer at protocol/packs.md:20, and no new contradiction was found.
§ F1 recheck holds the evidence, line by line.

## F1 recheck

| Check | Evidence | Result |
|---|---|---|
| Restated condition gone | packs.md:17-20 names no commit condition. Line 20 points at § 8 only. | resolved |
| § 8 is the single home | orchestrator.md:774 (untracked: the human commits). :777-781 (grant). :783-785 (no commit unless `build` fired; the close lane's edits stay uncommitted). | consistent |
| SKILL close-out steps | SKILL.md:215 commits "once `build` has fired". :236 checks "tracker declared and `build` fired". :256 points at "the commits § 8 allows". | consistent |
| Reader of packs.md | docs-engineer.md:4 has `tools: Read, Write, Edit, Glob, Grep` and no Bash, so the lane commits nothing. The pointer gives it no action it cannot take (rule 7). | consistent |
| orchestrator.md § 1 "Closed runs are pruned" | "The human commits runs" is about the run dir. "Them" at packs.md:20 is the applied pack edits under `<projectDir>/capabilities/`, which § 8 governs. These are different subjects. | no conflict |
