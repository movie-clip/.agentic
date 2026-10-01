REPORT 2026-10-01-lint-v0.7.16-network-edit/02
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    validate PASS, 0 errors, no error against any file in scope. Anchor: the 11 agent `tools:` lines read from disk, not the rule text, plus core, gates.md and round 1's artifact. All 4 grant bullets checked lane by lane; all 4 true. 4 UNVERIFIED risks.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Round 1 Finding 1 (BLOCKING, rule 9) — SATISFIED. `authoring.md:344-361` now names lanes, not classes, and every bullet matches the `tools:` line on disk; see § Round 1, finding by finding.
  - Round 1 Finding 2 (SHOULD_FIX, rule 8) — SATISFIED. The run-provenance sentence is gone from `authoring.md:313-316`; nothing in the file referred to it.
  - Round 1 Finding 3 (SHOULD_FIX, rule 8) — SATISFIED. `authoring.md:258-274`: the `## Index` block now sits under the colon that introduces it, exception below.
  - SHOULD_FIX — rule 8, `authoring.md:357-360`: the new `frontend-engineer` / `tech-lead` bullet is 263 characters against rule 8's own 200 limit, and carries two facts; see § Finding 4.
  - SHOULD_FIX — rule 8, `authoring.md:220`, `:223`, `:230`: three pre-existing bullets run 228, 298 and 271 characters; the last is the bullet stating the 200-character rule; see § Finding 5.

skill_calls:
  - none

risks:
  - UNVERIFIED: `authoring.md:323-335` asserts a bound repo registers the server in `.mcp.json` under key `project` and exposes those five tools. The order's non_goals forbid opening the portfolio repo, so no `.mcp.json` was read.
  - UNVERIFIED: `authoring.md:141-143` asserts Claude Code's implicit `effort` default is `xhigh`, second-highest of five. Platform behaviour, not observable from any file in scope.
  - UNVERIFIED: `authoring.md:169-177` asserts extended thinking is inherited per-session with no per-agent override, and that `maxTurns` caps agentic turns. Platform behaviour, not confirmed.
  - UNVERIFIED: `authoring.md:378-385` asserts `check_report.py` takes a run's gate set from the `## Phases` table's `verify` rows. That path was not executed against a real ledger.
  - Out of scope, noticed in passing: `CHANGELOG.md:172` says the quant lane gets "the probing pair" where `authoring.md:355` says "the three probing tools". No lane reads `CHANGELOG.md`, so this is not a rule-9 finding, only stale wording in a file this order does not cover.
  - `claude plugin validate` printed only the manifest line this run. Round 1 proved it reaches agent frontmatter by erroring on a scratch copy with a colon-broken `description:`; that probe was not repeated, so the coverage claim rests on round 1.

## Orchestrator brief

- Verdict `PASS`. All three round-1 findings are satisfied, and the replacement
  text is true about every grant — see § Round 1, finding by finding and
  § The four grant bullets against the `tools:` lines.
- No blocking finding. The edit introduced no rule-9 defect, which is the
  failure this round existed to catch.
- § Finding 4 — SHOULD_FIX, rule 8 and § Finding 5 — SHOULD_FIX, rule 8 are
  bullet-length items, non-blocking by `authoring.md:7-9`; both become `Open`
  rows.
- § Regression on the two touched sections carries rules 1, 2, 5, 6 and 7,
  including the one rule-2 candidate the edit created and why it is not a
  finding.
- § Anchor and coverage names the anchor used in place of the rule text and the
  four `UNVERIFIED:` premises.
- No lane owns `protocol/`; both `SHOULD_FIX` items are main-session edits.

## Anchor and coverage

The subject is `authoring.md`, which is this gate's own anchor, so the rule text
could not serve as one (`protocol-linter.md` § "When the file you judge is the
file you judge by"; `gates.md` § 2). The anchor was the network's live files,
listed from disk:

- `plugins/agentic-core/agents/` — 11 files, every `tools:`, `model:` and
  `effort:` line read directly.
- `PROTOCOL.md`, `protocol/gates.md`, and round 1's artifact as the statement of
  what had to be satisfied.

The inverted question — do these rules still describe what the files do —
answered yes everywhere this round. Nothing in the bound repo was opened; the
four `UNVERIFIED:` risks are the premises a lane will act on that this lint did
not confirm.

## Round 1, finding by finding

| Round 1 finding | Rule | Verdict |
|---|---|---|
| Finding 1 — "engines and tests get everything" contradicts the frontend carve-out | 9, BLOCKING | **satisfied** |
| Finding 2 — run provenance in § "A pack may not instruct a tool…" | 8, SHOULD_FIX | **satisfied** |
| Finding 3 — `## Index` block separated from the colon introducing it | 8, SHOULD_FIX | **satisfied** |

**Finding 1.** `authoring.md:344-361` no longer names a class. The sentence
beginning "The current grants: engines and tests get everything" is gone, and
the replacement adds "Those `tools:` lines are the authority on who holds what"
plus four bullets naming lanes. The contradiction with `:309-312` is resolved in
the direction the files support: `:357-358` now states that `frontend-engineer`
holds `run_tests`, `check_gates` and `reset_goldens` and deliberately not
`probe_engine` or `build_snapshot`, which is what `frontend-engineer.md:3` says.
No author reading the section can now resolve the ambiguity toward granting the
frontend lane a probing tool.

**Finding 2.** "In the first closed run the docs lane hit exactly this three
times and never once filed it as a pack correction." is deleted; a grep for
"first closed run" and "three times" across `authoring.md` returns nothing. The
behavioural *why* in the preceding sentence survives, so the section still
explains why `pack_corrections` does not catch this class. Nothing elsewhere in
the file depended on the count.

**Finding 3.** `authoring.md:258-274`: "Every one of them opens with:" is now
followed immediately by the `## Index` fenced block, with the `## Contents`
exception paragraph below it and "Three rules keep that honest." after that. The
rule and its exception remain adjacent, so the move raises no rule-9 question.

## The four grant bullets against the `tools:` lines

Each bullet was resolved to the agent file that owns the lane, with `tools:` read
from disk. All four are true; none is a fresh rule-9 finding.

| Bullet | Claim | `tools:` on disk | Verdict |
|---|---|---|---|
| `:352-354` | `backend-engineer` and `test-engineer` hold all five | `backend-engineer.md:3` and `test-engineer.md:3` each carry `run_tests`, `probe_engine`, `build_snapshot`, `check_gates`, `reset_goldens` | true |
| `:355-357` | `quantitative-researcher` holds the three probing tools | `quantitative-researcher.md:3` carries exactly three: `run_tests`, `probe_engine`, `build_snapshot` | true |
| `:357-360` | `frontend-engineer` and `tech-lead` hold `run_tests`, `check_gates`, `reset_goldens`, not `probe_engine` or `build_snapshot` | `frontend-engineer.md:3` and `tech-lead.md:3` each carry exactly those three | true |
| `:361-362` | `reviewer` holds `run_tests` and `check_gates` and no mutating tool | `reviewer.md:3` carries exactly those two; no `Edit`, no `reset_goldens` | true |

Two further checks on the set rather than on the bullets:

- Every lane holding an `mcp__project__*` tool is accounted for. The six are
  `backend-engineer`, `test-engineer`, `quantitative-researcher`,
  `frontend-engineer`, `tech-lead`, `reviewer`. The five holding none —
  `docs-engineer`, `producer`, `protocol-linter`, `scout`, `story-author` — are
  not claimed either way, and the section claims no roster.
- "the three probing tools" at `:355` is **not** filed as a finding. The count
  and the grant agree, and the paragraph above tells the reader the `tools:` line
  is the authority, so the one plausible misreading — that the three are
  `probe_engine`, `build_snapshot` and `check_gates` — is resolvable in one file
  open. Naming them would be better; "better" is a preference, not a rule.

## Regression on the two touched sections

| Rule | § The project tool server | § Indexing a pack or profile |
|---|---|---|
| 1 four-layer split | no bound-repo path, framework or command; the new bullets name lanes and MCP tool names, both network-layer | unchanged by the edit; the example index block illustrates what a pack contains, which is this file's subject |
| 2 one rule, one home | one candidate, examined below — not a finding | no rule restated; `## Index` vs `## Contents` is stated here alone |
| 5 index block | n/a — `authoring.md` is read in full and opens with `## Contents`, which still lists both touched sections under their current headings | same |
| 6 always-read | n/a — not a pack or profile | the three honesty rules and the always-read test survive the move verbatim |
| 7 tool premises | no command added; the section instructs no command at all | no command added |

**The rule-2 candidate, and why it is not a finding.** The fact that
`frontend-engineer` lacks `probe_engine` now appears twice: at `:309-312` as the
worked example of rule 7, and at `:357-360` as a grant with its rationale. These
are not one rule in two homes. `:300-319` states a rule — open the `tools:` line
before writing a command into a pack — and uses the frontend lane as its
illustration; `:344-361` states why each grant has the shape it has. Both defer
to the `tools:` lines as the authority, so neither can become the stale copy rule
2 exists to prevent. Removing the illustration would cost the rule its sharpest
example.

## Finding 4 — SHOULD_FIX, rule 8

**Rule.** `authoring.md` § "Writing for the reader you actually have", fourth
bullet: "One fact per bullet, under 200 characters."

**File and line.** `authoring.md:357-360`, the bullet this edit introduced:

> `frontend-engineer` and `tech-lead` hold `run_tests`, `check_gates` and
> `reset_goldens`, and deliberately **not** `probe_engine` or `build_snapshot`:
> neither lane writes engine code, so a probe either lane needs is a backend
> report it should be reading instead.

263 characters with continuation lines joined, and two facts: what the two lanes
hold, and what an author should do instead of asking for a probe.

**What would satisfy it.** Split "a probe either lane needs is a backend report
it should be reading instead" into its own bullet, or move it into the paragraph
above the list. Non-blocking by `authoring.md:7-9`; the bullet is true about the
grants, which is what this round was convened to check.

## Finding 5 — SHOULD_FIX, rule 8

Three bullets predating this edit exceed the same 200-character limit, measured
with continuation lines joined:

| Line | Length | Bullet |
|---|---|---|
| `:220` | 228 | "**Keep the *why* that changes behaviour.**…" |
| `:223` | 298 | "**Cut the history of how the rule was discovered.**…" |
| `:230` | 271 | "**One fact per bullet, under 200 characters.**…" |

`:230` is the bullet that states the rule. Round 1 passed rule 8 on these
sections without measuring them; they are inside this order's `scope`, so they
are reported rather than carried silently. Non-blocking, and no part of the
verdict.
