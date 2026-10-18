REPORT 2026-10-17-mvp-backlog-revision/06
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   python scripts/check_network_edit.py --help; python scripts/check_network_edit.py --verbose; claude plugin validate plugins/agentic-core
  result:    PASS
  detail:    plugin validate passed; check_network_edit lists project.md and product.md as UNLINTED (this artifact covers them); 0 BLOCKING, 4 SHOULD_FIX (rule 8); 3 UNVERIFIED premises; anchor: authoring.md + architecture/docs packs, phases.md
contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SHOULD_FIX (rule 8, one fact per bullet <200) project.md:149-151 — Mechanical gates bullet is ~210 chars with two facts; split "the gate is npm run gate" from "integration cannot pass until it exits 0".
  - SHOULD_FIX (rule 8, <200 chars) project.md:106-108 — build-lane BLOCKED bullet is ~210 chars; shorten, e.g. drop "to complete its order".
  - SHOULD_FIX (rule 8, cut provenance) project.md:17 — "The repo was bound before its first line of code." is history that changes no lane's action; delete the sentence.
  - SHOULD_FIX (rule 8) project.md:18 and :99-100 — "decisions 0001-0011" is stated twice, changes no action and goes stale at decision 0012; cite CLAUDE.md § Stack without the range.

skill_calls:
  - none

risks:
  - UNVERIFIED: project.md:89 and product.md:29 say the build order is the "Slice field" on Project 3 stories; the board was not opened (no GitHub tool in this lane).
  - UNVERIFIED: project.md:19 and product.md:4 say tracer-bullet slices A and B exist; only CLAUDE.md's mention of slice B was seen, no run or branch was checked.
  - UNVERIFIED: project.md:149-150 describes npm run gate as lint, typecheck, tests and e2e; matched against CLAUDE.md § Commands, not against package.json.
  - Fact, not authoring: docs/decisions/ holds 9 files (no 0003 or 0005), so "decisions 0001-0011" reads as 11 decisions that do not all exist.
  - Interpreted: project.md:100-101 "propose it and stop" vs docs.md § Recording an owner decision; judged consistent, as a decisions.md approval is the owner's call.
  - Out of scope: architecture.md:86 § Integration review item 1 still says "a lint and a test command"; project.md:151 cites it for the stricter npm run gate rule. Compatible, so not a finding.
  - Out of scope, untouched: project.md:8 "the stack (once chosen)" and :130-131 "set by the first stack decision" are now stale wording; neither contradicts an edited line.
  - Index heading "Building before the stack exists" is dated but resolves, and architecture.md:53 cites it by that name; renaming it means editing both together.

## Orchestrator brief

Verdict PASS: no BLOCKING finding on project.md or capabilities/product.md.
Guardrails unchanged (five, numbered, same wording). Both Indexes resolve.
Four rule 8 SHOULD_FIX items in handoff, all in project.md, become Open rows; the owning lane is the orchestrator or docs, since project.md is outside docs' capabilities/** close-out scope.
Section below: "Checks against the order's definition_of_done" (one row per check).

## Checks against the order's definition_of_done

| Check | Result |
|---|---|
| Layer split (rule 1) | No message shape or role definition added; repo paths and commands stay in the capability layer. |
| Index resolves (rule 5) | project.md: all 6 entries match `##` headings at lines 47, 95, 147, 76, 114, 139. product.md: all 5 match lines 23, 61, 75, 34, 52. |
| Always-read vs conditional (rule 6) | Unchanged. § Building before the stack exists still always-read; it carries the "do not reopen the stack" hazard, which is right. |
| Tools (rule 7) | No new command for the producer (`tools: Read, Write, Glob, Grep, Bash`). The GitHub Project 3 row is a location, not an instruction. |
| Contradictions (rule 9) | None found among the profile's always-read sections, product.md, architecture.md, docs.md and phases.md. phases.md's "not chosen" clauses are now false conditions, not conflicts. |
| Guardrails | `git diff` shows lines 47-74 unchanged: still five, numbered, same wording. |
| Bullet style | Reported as SHOULD_FIX only (see handoff). |
