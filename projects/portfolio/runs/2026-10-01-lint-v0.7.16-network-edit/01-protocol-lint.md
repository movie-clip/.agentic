REPORT 2026-10-01-lint-v0.7.16-network-edit/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    validate PASS, 0 errors; a scratch copy with a colon-broken description DID error, so the check covers agent frontmatter. check_agents() returned []. Anchor: the 10 other agent files listed from disk, plus core, gates, orchestrator, packs, check_report.py. 4 UNVERIFIED risks.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING — rule 9, `authoring.md:349` contradicts `authoring.md:309-310` on which lanes hold the probing tools; see § Finding 1.
  - SHOULD_FIX — rule 8, `authoring.md:316-318` carries run provenance ("In the first closed run the docs lane hit exactly this three times") that belongs in `CHANGELOG.md`; see § Finding 2.
  - SHOULD_FIX — rule 8, `authoring.md:258-261`: "Every one of them opens with:" is separated from the `## Index` block it introduces by the `## Contents` exception paragraph; see § Finding 3.

skill_calls:
  - none

risks:
  - UNVERIFIED: `authoring.md:324-326` asserts a bound repo registers its tool server in `.mcp.json` under the key `project`. The order's non_goals forbid opening the portfolio repo, so no `.mcp.json` was read.
  - UNVERIFIED: `authoring.md:141-143` asserts Claude Code's implicit `effort` default is `xhigh`, second-highest of five. Platform behaviour; not observable from any file in scope.
  - UNVERIFIED: `authoring.md:169-177` asserts extended thinking is inherited per-session with no per-agent override, and that `maxTurns` caps agentic turns. Platform behaviour; not confirmed.
  - UNVERIFIED: `authoring.md:376-383` asserts `check_report.py` resolves a run's profile and takes the gate set from the `## Phases` table's `verify` rows. The module's profile-resolution path was not executed against a real ledger.

## Orchestrator brief

- Verdict `FAIL` on one blocking finding: § Finding 1 — BLOCKING, rule 9 — a
  contradiction inside `protocol/authoring.md` about per-lane `mcp__project__`
  grants. That is the only section to route from.
- § Finding 2 — SHOULD_FIX, rule 8: run provenance in an instruction file.
- § Finding 3 — SHOULD_FIX, rule 8: a dangling colon in § Indexing. Neither
  rule-8 finding contributes to the verdict; both are `Open` rows.
- § Anchor — the files used in place of the rule text, and rules 3, 4, 9 and the
  rule-8 demotion checked against the live roster.
- § What passed — `protocol-linter.md` rule by rule; it needs no change.
- § Coverage — what this lint did not open, and the four `UNVERIFIED:` risks.
- No lane owns `protocol/`; the fix is a main-session edit to one sentence.

## Anchor

The subject is `authoring.md` and this lane's own definition, so the rule text
could not be the anchor (`protocol-linter.md` § "When the file you judge is the
file you judge by"; `gates.md` § 2). The anchor was the network's live files,
listed from disk rather than remembered:

- `plugins/agentic-core/agents/` — 11 files, the 10 other than
  `protocol-linter.md`: `backend-engineer`, `docs-engineer`,
  `frontend-engineer`, `producer`, `quantitative-researcher`, `reviewer`,
  `scout`, `story-author`, `tech-lead`, `test-engineer`.
- `PROTOCOL.md`, `protocol/gates.md`, `protocol/orchestrator.md`,
  `protocol/packs.md`, `plugins/agentic-core/skills/orchestrate-feature/SKILL.md`.
- `scripts/check_report.py` — `GATE_LANES`, `check_agents`, the CR/`Open`
  cross-checks.

The inverted question — do these rules still describe what the files do —
answered yes on rules 3 and 4, and no on one sentence of § "The project tool
server" (§ Finding 1).

**Rule 3 and rule 4 against the live roster.** Every lane in
`authoring.md`'s model table and effort table matches its file, with no lane
missing from either table and no table row naming a lane that does not exist:

| Lane | file `model:` | table | file `effort:` | table |
|---|---|---|---|---|
| `quantitative-researcher` | opus | opus | medium | medium |
| `protocol-linter` | opus | opus | medium | medium |
| `producer` | sonnet | sonnet | high | high |
| `tech-lead` | sonnet | sonnet | high | high |
| `reviewer` | sonnet | sonnet | high | high |
| `backend-engineer` | sonnet | sonnet | high | high |
| `frontend-engineer` | sonnet | sonnet | high | high |
| `story-author` | sonnet | sonnet | medium | medium |
| `docs-engineer` | sonnet | sonnet | medium | medium |
| `test-engineer` | sonnet | sonnet | medium | medium |
| `scout` | sonnet | sonnet | medium | medium |

`haiku` is declared occupied by nothing, and nothing declares it.

**Rule 9, new in v0.7.16, against the live files.** It is not violated by the
roster: no pair of always-read instructions in core, `gates.md`,
`orchestrator.md` or `packs.md` was found directing different actions in one
situation, so the rule does not arrive condemning its own subjects. It is
violated once by the file that introduces it — § Finding 1.

**The rule-8 demotion against the live files.** `authoring.md:7-9` names the
exempt section by heading; `protocol-linter.md:71-78` routes it to `SHOULD_FIX`;
`orchestrator.md:464-466` and `SKILL.md:381` already require a `SHOULD_FIX` to
carry an `Open` row, and `check_report.py` reads CR files against `Open` rather
than `Open` against CR files — so a rule-8 finding reported through `handoff`
with an `Open` row, and no CR, is routable as written. No file still describes
bullet length as blocking. The demotion is consistent across the roster.

## Finding 1 — BLOCKING, rule 9

**Rule.** `protocol/authoring.md` § "Two instructions may not disagree",
first bullet: "Within a file and across files a lane reads together".

**File and line.** `protocol/authoring.md:349`, against
`protocol/authoring.md:309-310`.

Line 349, in § "The project tool server" under **Grant per lane, and grant
narrowly**:

> The current grants: engines and tests get everything;

Lines 309-310, in § "A pack may not instruct a tool the lane does not have":

> A pack section telling `frontend-engineer` to call `probe_engine` names a tool
> that lane was deliberately not given

`frontend-engineer` is an engineering lane, so "engines ... get everything"
reads as covering it, and the two sentences then direct opposite actions in the
same situation: an author writing a pack section that calls `probe_engine` or
`build_snapshot` for the frontend lane is told by line 349 that the grant is
there and by line 310 that it is deliberately absent.

The files settle which is wrong. `plugins/agentic-core/agents/frontend-engineer.md:5`:

```
tools: Read, Write, Edit, Glob, Grep, Bash, Skill, mcp__project__run_tests, mcp__project__check_gates, mcp__project__reset_goldens
```

Three of the five, not everything. `backend-engineer.md:5` and
`test-engineer.md:5` each carry all five, so the sentence is true only of those
two lanes.

**Why it matters.** This is the premise rule 7 is checked against, and rule 7 is
the one no other mechanism catches — `pack_corrections` is aimed at facts about
the code, and § "A pack may not instruct a tool the lane does not have" records
the same class of failure happening three times without one correction filed. An
author or linter that resolves the ambiguity toward line 349 grants the frontend
lane a tool it does not have, and the failure then looks like the agent ignoring
its pack.

**What would satisfy it.** Reword line 349 to name the lanes rather than a
class — "the backend and test lanes get everything; `frontend-engineer` gets
`run_tests`, `check_gates` and `reset_goldens`" — or state which sentence wins.
Per the rule's own closing line, silence is not a resolution. No other line
needs to change; lines 309-310 are correct as written.

## Finding 2 — SHOULD_FIX, rule 8

`protocol/authoring.md:316-318`:

> In the first closed run the docs lane hit exactly this three times and never
> once filed it as a pack correction.

This is the history of how the rule was discovered, which the same section
directs to `CHANGELOG.md`: "It is worth recording — in `CHANGELOG.md`, whose
reader is a human deciding whether to trust the design. It changes no agent's
behaviour, and every agent pays for it on every dispatch." The sentence before
it already carries the behavioural *why* (an agent substitutes and files a
risk instead of a correction), so cutting the count loses nothing a lane acts
on. Non-blocking by `authoring.md:7-9`.

## Finding 3 — SHOULD_FIX, rule 8

`protocol/authoring.md:258-261`. The sentence "Packs and profiles are read by
index (core § 1, steps 4-5). Every one of them opens with:" ends in a colon
whose referent — the `## Index` code block at line 268 — is separated from it by
the whole `## Contents` exception paragraph, which opens "**Unless it is read in
full ...**". A linear reader meets the exception before the thing excepted.
Moving the code block directly under the colon and the exception paragraph below
it fixes it; the rule and its exception stay adjacent either way, so rule 9 is
not at issue. Non-blocking by `authoring.md:7-9`.

## What passed

`plugins/agentic-core/agents/protocol-linter.md`, rule by rule:

| Rule | Result |
|---|---|
| parse | `claude plugin validate` reports no error against it; `check_agents()` returns `[]` |
| 1 four-layer split | no bound-repo path, framework or command; its two commands are `claude plugin validate` and `scripts/check_report.py`, both network-layer |
| 2 one rule, one home | § "Required output format" cites core § 3 and § 4 and restates neither; no shape block pasted |
| 3 model declared | `opus`, matching the model table's test — nothing downstream checks this lane, and it runs only on an authoring order |
| 4 effort declared | `effort: medium`, matching the effort table |
| 5 index | not a pack or profile; no `## Index` owed |
| 6 always-read | not a pack or profile; read in full |
| 7 tool premises | both commands need `Bash`, which line 4 grants |
| 8 written for a model | tables where the content is a mapping; no provenance; no multi-fact bullet |
| 9 instructions agree | three candidate pairs examined and each resolves — see below |

The three pairs checked for rule 9 inside `protocol-linter.md`, none of them a
finding:

- Line 80-82 ("a contradiction is never a `risks` bullet") against line 110-111
  ("a file outside `scope` is a `risks` bullet"). Different subjects: a rule-9
  finding is located in the in-scope file and cites the out-of-scope one, which
  is what lines 65-67 instruct. No situation takes both actions.
- Line 133-136 (return `PARTIAL` when the anchor is unreachable) against line
  140 (`verdict` is `PASS` or `FAIL`, nothing in between). Different fields, per
  core § 6: `PARTIAL` is a `status`, and "nothing in between" governs
  `PASS`-with-notes. `check_report.py` permits a gate lane to write
  `verdict: NONE`, so the pair is also mechanically coherent.
- Line 78 (a rule-8 finding is listed in `handoff`) against line 74 (it becomes
  an `Open` row). Core § 5 and `orchestrator.md:464-466` make these one route,
  and core § "You cannot delete or rename files" already carries a `should_fix`
  in `handoff` as the worked example.

`protocol/authoring.md` passed rules 1, 2, 3, 4, 5, 6, 7 and the parse check.
On rule 2 specifically: § "Two instructions may not disagree" is new, and no
other protocol file states it. Core § "When the order and your capability pack
disagree" governs a runtime conflict between an order and a pack, with a
different remedy (`REFUSED` on a numbered guardrail, `PARTIAL` plus a `risks`
bullet on a convention); the new section governs two instruction files at
authoring time. Two rules, one home each.

## Coverage

Nothing in the bound repo was opened — the order's non_goals forbid it — so no
path, skill name, fixture or setting asserted anywhere in either file was
confirmed. The four `UNVERIFIED:` risks above are the premises a lane will act
on that this lint did not open. The budget capability packs v0.7.16 also touched
are outside `scope` and were not read.
