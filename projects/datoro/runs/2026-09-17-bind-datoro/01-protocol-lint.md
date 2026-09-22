REPORT 2026-09-17-bind-datoro/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Anchor: protocol/authoring.md (subject is a project profile, not authoring.md itself, so the rule text is the valid anchor). Plugin manifest + all 11 agent frontmatter blocks parse. 9 scope files read end to end. 3 BLOCKING index findings, 1 SHOULD_FIX.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (BLOCKING, capabilities/frontend.md:23) — `Guardrails, in code terms` is filed conditional; authoring.md § "Indexing a pack or profile" rule 3 names guardrails as always-read regardless. Owner: the lane that authored the profile. See § FINDING 1.
  - FINDING 2 (BLOCKING, capabilities/backend.md:25) — `Reuse — do not re-derive these` is filed conditional on "you are about to write a new service"; authoring.md names this exact condition as non-evaluable. See § FINDING 2.
  - FINDING 3 (BLOCKING, project.md:149) — `## Reference` exists in the file and appears nowhere in the `## Index` block, neither always-read nor as a table row. Violates indexing rule 1. See § FINDING 3.
  - FINDING 4 (SHOULD_FIX, runs/README.md:13-25) — the `## Retention` rule is a verbatim second copy of `projects/portfolio/runs/README.md` and has already drifted from it. See § FINDING 4.

risks:
  - 13 of 79 bullets in the datoro files exceed authoring.md's 200-character instruction-file limit. Not raised as blocking: the rule states no enforced/advisory split, and the existing corpus sits at the same rate (portfolio 22/170, tradingview 24/102, protocol/ 22/83). See § Bullet lengths.
  - Three repo facts are duplicated across packs: the `vitest.config.js` setup.js/setup.ts mismatch and the e2e/localhost:7071 precondition (backend.md and testing.md), and the `lint:check` CI drift (backend.md, testing.md, architecture.md). A `pack_corrections` entry applied to one will not reach the other.
  - `capabilities/testing.md:22` files `Mocking conventions` conditional; its condition ("your test touches FMP, Redis, Prisma or auth") is evaluable from the order, but the section also carries a reuse instruction. Judged acceptable, not a finding. Same call on `frontend.md:22` `Charts`.
  - Two DoD checklist items restate protocol rules rather than citing them: product.md:98 ("no files written outside the report artifact", core § 3) and testing.md:98 ("the order's verification command was actually run and passed", core § 7). Judged a checklist, not a second definition.
  - No `.agentic.json` exists at or above cwd (`C:\projects\investments\.agentic`); I bound by the order's absolute paths and `datoro/.agentic.json`, which resolves to this agenticRoot. Not a scope file, so not a finding.
  - I did not open `C:\projects\investments\datoro`. Every claim the packs make about that repo's paths, scripts and CI files is unverified by me and outside this gate (authoring, not fact).

## Orchestrator brief

- Verdict: FAIL. Three BLOCKING findings, all in `## Index` blocks, all one-line fixes. One SHOULD_FIX.
- Nothing in the four-layer split, the tool-premise check or the lane/phase cross-checks failed. The profile is structurally sound; the index blocks are where it slipped.
- Owner for all four: whichever lane authored the profile. Scope fence is the three named files plus `runs/README.md`.
- Sections: § FINDING 1 · § FINDING 2 · § FINDING 3 · § FINDING 4 · § What passed · § Bullet lengths.
- FINDINGS 1-3 are independent of each other and dispatchable together in one order.

## FINDING 1

`projects/datoro/capabilities/frontend.md:23`, in the `## Index` table:

```
| Guardrails, in code terms | your order surfaces data that can be missing or partial |
```

**Rule:** `protocol/authoring.md` § "Indexing a pack or profile", rule 3 —
"Sections that describe *hazards the reader cannot anticipate* — gotchas, reuse
inventories, unit and sign conventions, edge cases, guardrails — are always-read
regardless of length."

**Why it matters, not just which rule.** The section carries two facts a
`frontend-engineer` cannot know it needs before reading them. The second one,
"No secrets in client code", has nothing to do with missing or partial data at
all, so a lane adding a component that reads a config value evaluates the stated
condition correctly as false and never sees it. Guardrail 5's rendering rule is
the same shape: a lane only knows a field can be null after the backend lane's
contract note says so, and a lane building the first version of a surface has no
such note.

The companion pack does this correctly: `backend.md:19` lists
`Guardrails, in code terms` under **Always read**. Two packs in the same profile
disagree about the same section name.

**What would satisfy it:** move `Guardrails, in code terms` out of the table and
into the `Always read:` line at `frontend.md:17`, beside the three sections
already there.

## FINDING 2

`projects/datoro/capabilities/backend.md:25`, in the `## Index` table:

```
| Reuse — do not re-derive these | you are about to write a new service |
```

**Rule:** `protocol/authoring.md` § "Indexing a pack or profile", rule 3. The
rule text names this condition as its own worked example: "The same trap catches
'read Reuse when you are about to write a helper': an agent that knew it was
re-deriving something would not be re-deriving it."

**Why it matters.** The section is not only a reuse inventory — it is where
guardrails 1, 2 and 3 are bound to specific files (`auth.ts`,
`constructWebhookEvent`, `logger.ts`). A backend order that edits an existing
route rather than adding a service evaluates the condition as false, skips the
section, and never reads that binding. `Guardrails, in code terms` is
always-read and restates the guardrails in prose, but not the file paths that
make them actionable.

Again the companion pack is right: `frontend.md:17` has
`Reuse — do not re-derive these` under **Always read**.

**What would satisfy it:** move the row into the `Always read:` line at
`backend.md:19`.

## FINDING 3

`projects/datoro/project.md:149` defines `## Reference`. The `## Index` block at
`project.md:32-48` names five sections: `Hard guardrails` and `Mechanical gates`
as always-read, and `Delivery model`, `Lane routing`, `Why quant is not bound`
as table rows. `Reference` appears in neither list.

**Rule:** `protocol/authoring.md` § "Indexing a pack or profile", rule 1 —
"Every section is findable by the name a lane would search for."

**Why it matters.** The index block opens with "You are not expected to read
this file end to end — read what your order touches", which is an explicit
instruction to route by the index. A section the index omits is therefore not
merely harder to find, it is one the profile has told every lane it may skip.
The content is addressed to `recon` and `product` orders — check
`docs/PROJECT_REVIEW_PLAYBOOK.md` and `docs/reviews/` before treating a finding
as new — so the two lanes it is for are exactly the two that will not see it.

**What would satisfy it:** add a row —
`| Reference | you are a recon or product order checking whether something was already flagged |`.
The condition is evaluable from the order, so a table row is correct here;
always-read is not required.

Noted but not part of the finding: `product.md` § "Finding precedent" already
carries this instruction for the `product` lane, with the commands. If the
`Reference` section exists for `recon` alone, saying so in the row is what makes
the two copies distinguishable.

## FINDING 4

`projects/datoro/runs/README.md:13-25` — `## Retention`.

The section is a copy of `projects/portfolio/runs/README.md:13-26`. The two have
already diverged: portfolio's carries a sentence about `CHANGELOG.md` naming run
ids as the durable form of a citation, which datoro's drops.

**Rule:** `protocol/authoring.md` § "One rule, one home" — "place it in exactly
one file, chosen by *who needs it*". The retention policy, and the rule that a
pruned run is cited by id and never by path, are network-wide statements about
how any project's run directory is kept. Neither is a fact about `datoro`.

**Severity is SHOULD_FIX, not BLOCKING:** the verdict does not rest on it, and
nothing in the network reads this file mechanically.

**What would satisfy it, either way:**

- state the rule once — in `authoring.md`, which already owns "the files a new
  project needs" — and reduce both READMEs to a pointer; or
- if retention is deliberately a per-project policy, say that in one line
  (`Retention: pruned at close-out once the lesson is in the protocol`) rather
  than re-deriving the rationale, so the two copies cannot drift on reasoning.

The second is the cheaper fix and is inside this run's scope; the first is not,
since it edits `protocol/`.

## What passed

Recorded so the next lint does not re-derive it.

| Check | Result |
|---|---|
| `claude plugin validate plugins/agentic-core` | passed — manifest and all 11 agent frontmatter blocks parse |
| Four-layer split | no message shape, report block or role definition in any pack; no lane name or trigger hard-coded where the profile should be read |
| Tool premises — `Bash` | every command in the packs is owned by a lane that has `Bash`: architecture.md → `tech-lead`, testing.md → `test-engineer`, product.md → `producer`. All three declare `Bash` |
| Tool premises — no-`Bash` lanes | `docs.md` names no command and states the constraint itself at :48 ("You have no `Bash`, so you cannot run `git diff`"). `story-author` and `scout` have no pack |
| Tool premises — MCP | `grep -rn "mcp__" projects/datoro` returns one hit, `project.md:108`, which *denies* the grant. No lane is told to call an `mcp__project__*` tool |
| Index present | all seven indexed files carry `## Index`; `phases.md` carries `## Contents`, correct per authoring.md's full-read exception |
| `phases.md` `## Contents` | names all five sections below it |
| Model / effort declarations | not applicable — no agent file in scope; the roster's 11 files all declare both, none `inherit` or `fable` |

**Lane routing (`project.md:93-105`) against `plugins/agentic-core/agents/`.**
All eleven rows resolve, and the two mode annotations are the two core § 2
allows for `tech-lead`:

| Row | Agent file | Mode |
|---|---|---|
| recon / product / story | scout, producer, story-author | — |
| design | tech-lead | DESIGN — valid |
| backend / frontend / test / docs | backend-engineer, frontend-engineer, test-engineer, docs-engineer | — |
| integration | tech-lead | INTEGRATION — valid |
| review / protocol-lint | reviewer, protocol-linter | — |

Every lane name in the table is a value from core § 2's `lane:` enum.
`quantitative-researcher` is the one roster agent not bound, and `project.md`
§ "Why `quant` is not bound" accounts for it rather than leaving it unexplained.

**`phases.md` `## Phases` against `protocol/orchestrator.md` § 2.** Rows appear
in the § 2 dependency order: ground-truth → framing → specification → design →
build → verify → close. No phase is out of order and no row names a phase § 2
does not define.

`intake` has no row. That is correct and not a finding: § 2 fires it always, it
dispatches no lane, and `tradingview/phases.md` omits it on the same grounds.
`quant-audit` has no `verify` row, which is the project's declaration — § 2
leaves the gate set to the profile, and `check_report.py` reads the owed gates
from these rows, so the omission is what makes close-out not demand an account
of it.

## Bullet lengths

Measured across the seven indexed files, joining continuation lines:

| Files | bullets | over 200 chars |
|---|---|---|
| `projects/datoro` | 79 | 13 |
| `projects/portfolio` | 170 | 22 |
| `projects/tradingview` | 102 | 24 |
| `protocol/` + `PROTOCOL.md` | 83 | 22 |
| `plugins/agentic-core/agents/` | 79 | 4 |

The longest in scope: `product.md:74` (327), `product.md:99` (308),
`project.md:138` (350), `frontend.md:81` (274), `backend.md:133` (281).

Not raised as blocking for two reasons. Authoring.md states the 200-character
limit without the enforced/advisory split core § 3 gives report bullets, so
there is no basis in the rule text for failing on it. And at 16% over, datoro
sits below `tradingview` and the protocol files themselves — failing it here
would fail every file in the network, which is a change to the standard rather
than an application of it. If the intent is that the limit binds, that is an
edit to `authoring.md` and it should be made there first.
