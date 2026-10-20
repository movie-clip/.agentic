REPORT 2026-10-20-designer-lint-followup/01
status:      DONE
verdict:     FAIL
changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    validate passed. N1 RESOLVED, both risks RESOLVED; Open-row sweep rule kept (core § 5 + check_report.py:1203). 1 new BLOCKING (rule 9). Anchor: designer.md/reviewer.md frontmatter, 3 run ledgers. 1 premise UNVERIFIED.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - B1 BLOCKING rule 9 — protocol/orchestrator.md:487 "never a round" contradicts core § 5 `round:` (PROTOCOL.md:305) and check_report.py:1189-1191, which needs a Rounds row for every CR. see § Findings

skill_calls:
  - none

risks:
  - UNVERIFIED: that every UX spec check names its falsifying screenshot (protocol/authoring.md:199-200); I did not open a UX spec, only the rationale's wording.
  - Not filed (outside the diff): protocol/gates.md:68-70 restates core § 5 on non-blocking findings becoming Open rows; gates.md is not a judged file here.
  - Not filed (outside the diff): protocol/orchestrator.md:78 example ledger has SHOULD_FIX CR-2 with no Rounds row, which check_report.py:1189 would fail if cr/CR-2.md existed.
  - Binding: bound via C:\projects\investments\los-tres\.agentic.json, agenticRoot ../.agentic, as the order directed.

## Orchestrator brief
Verdict FAIL on one new BLOCKING finding (B1, protocol/orchestrator.md:487); all three leftovers resolved.
Parser clean. Files judged: protocol/authoring.md, protocol/orchestrator.md, PROTOCOL.md (diff hunks only).
Sections below: `Findings` — status of N1 and the two risks with file:line, the sweep-rule check, and B1 with what would satisfy it.

## Findings

**N1 (SHOULD_FIX, protocol/authoring.md:197-199) — RESOLVED.** protocol/authoring.md:197-200 now reads "These two have the most structure to lean on: `review` checks criteria that each name a falsifying observation, and `ux-review` checks a UX spec…". No third-gate reading remains; reviewer.md:5 and designer.md:5 are `model: sonnet`, matching the heading at :184.

**Risk 1 (orchestrator.md:462-466 and PROTOCOL.md § 5 omit ux-review) — RESOLVED.** protocol/orchestrator.md:462 "all five of them" and :465 list `ux-review`; PROTOCOL.md:314-315 lists `quant-audit`, `ux-review`, `reviewer`, `protocol-lint`. Five agrees with protocol/gates.md:14. No other stale gate count in PROTOCOL.md, protocol/, ARCHITECTURE.md or SKILL.md (grep).

**Risk 2 (orchestrator.md:486-488 restates core § 5) — RESOLVED** as a restatement, but the replacement line introduced B1.

**Sweep rule not dropped.** The removed sentence ("A `SHOULD_FIX` change request with no `Open` row … the close-out sweep fails it") is still carried by PROTOCOL.md:334-336 ("through that table or not at all, and the check reads it") and enforced at scripts/check_report.py:1203-1207.

**B1 — BLOCKING — authoring.md § "Two instructions may not disagree" (rule 9) — protocol/orchestrator.md:487.**
New text: "Non-blocking findings follow core § 5: an `Open` row, never a round."
- Core § 5 does not say this. Its CR shape requires `round: <n> of 2` on every request, SHOULD_FIX included (PROTOCOL.md:303-305). It says only that BLOCKING holds the slice (PROTOCOL.md:334).
- scripts/check_report.py:1189-1191 fails any CR file with no `## Rounds` row ("a dispatch the cap cannot see is a dispatch outside the cap").
- Practice agrees with the script, not with the new line. SHOULD_FIX CRs were dispatched and given Rounds rows in projects/los-tres/runs/2026-10-18-s1-1-go-redirect/run.md:75-77 (CR-5..7), projects/impact/runs/2026-10-07-ecs-animation-approach/run.md:72 and projects/impact/runs/2026-10-07-s2-animation-bridge-contract/run.md:84.
- Effect: an orchestrator holding a SHOULD_FIX CR reads "never a round" and skips the Rounds row. Core § 5 says to fill `round:`, and the close-out sweep then fails the ledger. The line also credits core § 5 with a rule it does not state.
Satisfy: replace :487 with a pointer that adds no rule, e.g. "Non-blocking findings follow core § 5: they do not hold the slice, and reach the human through an `Open` row." If SHOULD_FIX CRs really must never be dispatched, that is a new rule. It belongs in core § 5, with check_report.py and the orchestrator.md:78 example changed to match.
