REPORT 2026-10-19-designer-lint-fixes/01
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    validate passed. F1-F7 all RESOLVED; 0 BLOCKING, 1 new SHOULD_FIX (rule 8). Anchor for authoring.md tables: frontmatter of the 12 files in agents/ (all match). 8 premises UNVERIFIED.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - N1 SHOULD_FIX rule 8 — protocol/authoring.md:197-199 "These two have the most structure" then "`ux-review` sits on Sonnet for the same reason" restates the retitled heading as if ux-review were a third gate. see § Findings

skill_calls:
  - none

risks:
  - UNVERIFIED: `curl -s <url>` returns server-rendered HTML holding every focusable element (projects/los-tres/capabilities/ux.md:101-104); client-only widgets would be missed.
  - UNVERIFIED: skill `frontend-design:frontend-design` (ux.md:57) is installed and callable from a dispatched lane.
  - UNVERIFIED: `npx playwright screenshot` with --viewport-size/--full-page/--lang works and a browser is installed (ux.md:89-92).
  - UNVERIFIED: `/api/health` returns 200 on a healthy stack (ux.md:81).
  - UNVERIFIED: `docker compose run --rm app import-feeds` loads the demo data (ux.md:83).
  - UNVERIFIED: APP_PORT is 3010 on the owner's machine (ux.md:80).
  - UNVERIFIED: demo slug `/producto/demo-filtro-de-aceite-oc-1234` exists with two shops (ux.md:110).
  - UNVERIFIED: paths src/app/globals.css, src/components/*.module.css, messages/es-ES.json exist (ux.md:47-49).
  - Binding: no .agentic.json above the agenticRoot; bound via C:\projects\investments\los-tres\.agentic.json, which resolves agenticRoot to this repo.
  - Not filed (pre-existing, no rule fits): protocol/orchestrator.md:462 "one shape for all four of them" and :466 omit ux-review; PROTOCOL.md § 5 list "quant-audit, reviewer, protocol-lint" omits it too.
  - Not filed (pre-existing, outside the diff): protocol/orchestrator.md:486-488 restates gates.md § 3 and PROTOCOL.md § 5 on non-blocking findings becoming Open rows.

## Orchestrator brief
Verdict PASS: F1-F7 RESOLVED; one new SHOULD_FIX (N1, protocol/authoring.md) for an Open row.
Parser clean. Model/effort tables in protocol/authoring.md and ARCHITECTURE.md match the 12 agent frontmatters.
Earlier out-of-scope notes: all five fixed (ARCHITECTURE.md, orchestrator.md, SKILL.md, docs.md, PROTOCOL.md).
Sections below: `Findings` — per-finding status with file:line, plus N1 and what would satisfy it.

## Findings

Files judged: protocol/authoring.md, PROTOCOL.md, plugins/agentic-core/agents/designer.md, projects/los-tres/capabilities/ux.md, projects/los-tres/capabilities/docs.md, projects/los-tres/phases.md, ARCHITECTURE.md, protocol/orchestrator.md, plugins/agentic-core/skills/orchestrate-feature/SKILL.md.

**F1 — RESOLVED.** protocol/authoring.md:119 names the tech-lead exception at the test; :128 says tech-lead fails the test and is on Opus by ruling; :157-159 now "the two lanes with no downstream check"; :184 retitled "Why `review` and `ux-review` are on Sonnet", :189-190 says integration runs on tech-lead by the ruling. Matches tech-lead.md frontmatter (opus/low).

**F2 — RESOLVED.** designer.md:151-154 files taste in `handoff` as `SHOULD_FIX`, becoming an Open row per gates.md § 3; ux.md:160 DoD agrees. Consistent with orchestrator.md:486-488 and PROTOCOL.md § 5 severity derivation.

**F3 — RESOLVED.** designer.md:137-141 takes both focus checks from the pack's method, labelled consistency checks, else `not checked`. ux.md:97-104 gives a method for visibility (CSS) and order (curl + document order). `curl` is runnable: designer.md:4 `tools: Read, Write, Glob, Grep, Bash, Skill`.

**F4 — RESOLVED.** phases.md:63-66 routes the spec and decisions.md to the close-out docs order when direction is new/changed and approved. docs.md:25 index condition is now evaluable from the order's inputs; docs.md:48-51 and ux.md:46 agree.

**F5 — RESOLVED.** PROTOCOL.md:67 mode line now carries `designer: UX | UX-REVIEW`, matching designer.md:40-41.

**F6 — RESOLVED.** designer.md:121 reads "Reading the component source"; no framework name remains in the role file.

**F7 — RESOLVED.** No date remains (grep for 2026-10-18 in protocol/, PROTOCOL.md, ARCHITECTURE.md: none). The `low` restatement line is gone; :162 starts with `max`. "owner's ruling" remains at :128 and :190 — the second is what F1's fix asked for.

**Earlier out-of-scope notes — all fixed.** ARCHITECTURE.md:242-245 adds tech-lead Opus and `low`; :248 "Why five gates" with a designer row. orchestrator.md:550-551 and SKILL.md:154 list `ux` as a planning lane. docs.md:3-6 names ux-review. PROTOCOL.md:138-140 lists designer as read-only.

**N1 — SHOULD_FIX — authoring.md § "Writing for the reader you actually have" (rule 8) — protocol/authoring.md:192-199.**
After the retitle, "these two" (:197) already means `review` and `ux-review`, but :198 says "`ux-review` sits on Sonnet for the same reason" as though it were a third gate — a leftover of the old `integration`/`review` framing that every reader pays to untangle.
Satisfy: replace :197-199 with one sentence per gate, e.g. "`review` leans on falsifiable acceptance criteria; `ux-review` on spec checks that each name the screenshot that would prove them false, and taste never blocks."
