REPORT 2026-09-22-bind-impact/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    Anchor: protocol/authoring.md (subject is a project profile, not authoring.md itself, so the rule text is the valid anchor), plus the eleven `tools:` lines under plugins/agentic-core/agents/ for rule 7. Manifest validation passed. 9 files checked: 1 BLOCKING finding, 3 SHOULD_FIX. 44 bullets, 0 over 200 chars.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - FINDING 1 (BLOCKING) is one lane's fix: `capabilities/product.md:3-4` states a false premise about the `producer` lane's tools. See § FINDING 1 for the exact replacement.
  - SHOULD_FIX 1 — `capabilities/testing.md:11` files an always-true condition as a conditional index row. See § SHOULD_FIX 1.
  - SHOULD_FIX 2 — `project.md:141` says "Any lane may reach for the `unity-cli` skill"; three lanes have no `Bash`. See § SHOULD_FIX 2.
  - SHOULD_FIX 3 — `backend.md:18` and `project.md:45` gate the Unity CLI sections on a condition only the section's own content can answer. See § SHOULD_FIX 3.

risks:
  - I did not open `C:\projects\impact`. Every claim these files make about that repo's paths, scripts, packages and CI remains unverified by me — authoring, not fact, per the order's non_goals.
  - The package dependency chain is stated three times — `project.md:60-62`, `backend.md:24-26`, `architecture.md:19-21` — for readers who all also read `project.md`. Not raised as a finding; see § Duplication considered and not raised.
  - `runs/README.md:17` points at `projects/portfolio/runs/README.md` for the retention policy, inheriting datoro round 2's open FINDING 4 (a network-wide rule homed in one project's directory). Not a new defect in this profile.
  - `testing.md:37-38,48-49` use `.\Tools\Run-UnityTests.ps1` while `project.md:151` and `architecture.md:63` use `Tools/Run-UnityTests.ps1`, and the repo has two candidate working directories (git root and `Impact/`). Resolving that is a fact about the repo, outside this gate.

## Orchestrator brief

- Verdict: FAIL, on one BLOCKING finding. It is a two-line edit to one file, owned by whoever authored the profile — not a build lane.
- FINDING 1: `capabilities/product.md` tells the `producer` lane it has no `Bash`. It does, and `producer.md:49` instructs it to use `git log -S` for exactly the question this pack assigns it. Rule 7, inverted — the pack did not open the agent file.
- Three SHOULD_FIX findings do not hold the slice (core § 5) and become `Open` rows.
- What passed: the plugin manifest, all six `## Index` blocks (complete, no section named twice), `phases.md`'s `## Contents` and phase order against `orchestrator.md` § 2, the ten-row lane routing table against the roster, the four-layer split, bullet length, and the `mcp__project__*` denial.
- Sections: § FINDING 1 · § SHOULD_FIX 1 · § SHOULD_FIX 2 · § SHOULD_FIX 3 · § Duplication considered and not raised · § What passed.

## FINDING 1

**Severity: BLOCKING.**

**Rule.** `protocol/authoring.md` § "A pack may not instruct a tool the lane
does not have" — "Before writing a command into a capability pack, open the
agent file and read its `tools:` line."

**Where.** `projects/impact/capabilities/product.md:3-4`:

```
Read-only lane. No `Bash` — findings about "is this already covered" come
from `Read`/`Glob`/`Grep` over the repo, not from running anything.
```

**The false premise.** `plugins/agentic-core/agents/producer.md:4`:

```
tools: Read, Write, Glob, Grep, Bash
```

The `producer` lane has `Bash`. The rule is usually broken in the other
direction — a pack naming a tool the lane lacks — but the check is the same
one and it was not run: the pack asserts a `tools:` line that does not exist.

**Why it matters, and it is not cosmetic.** `producer.md:49-56` instructs this
lane to use that exact tool for this exact question:

```
**Use git for it.** You have `Bash`, and the history answers "was this already
done?" better than any document can — a doc can be stale about the code, but a
commit that touched the file cannot be.
```

`product.md:16-22` makes "is this already covered" this lane's *narrowed* job
in this repo, and `product.md:30-35` then routes the check to two documents
(`ARCHITECTURE_REVIEW.md`, `PACKAGE_ARCHITECTURE.md`) — substituting the stale
source the role file explicitly warns against for the one it says cannot be
stale. A `producer` dispatch reads the pack as authoritative over its priors
and will not reach for `git log -S` it has just been told it cannot run. In a
repo whose profile says it keeps no roadmap, backlog or ticket doc
(`project.md:66-69`), git history is the only precedent record there is.

This is also the one false premise `pack_corrections` does not catch: a lane
that believes it lacks a tool does not discover it has one, so nothing
downstream ever reports it. That is why the rule sits at authoring time.

**What would satisfy it.** Replace `product.md:3-4` with a line that matches
the `tools:` line and keeps the mutation boundary the original was reaching
for:

```markdown
Read-only lane — `Read`/`Glob`/`Grep` over the repo, plus `Bash` for git
history. You do not edit the repo; the only file you write is your report.
```

and add `git` to the precedent check at `product.md:30-35`, so the section
names the source `producer.md:49` requires alongside the two documents.

Impact is the only project making this claim: `grep -rn "Bash"` over
`projects/datoro/capabilities/product.md` and
`projects/portfolio/capabilities/product.md` returns nothing.

## SHOULD_FIX 1

**Rule.** `authoring.md` § "Indexing a pack or profile", rule 3.

`capabilities/testing.md:11`:

```
| Running the suite | any dispatch, for the exact commands |
```

A condition that is true on every dispatch is an always-read section filed as
a conditional one. It does no harm to a lane that reads the row, but it
weakens the index: "read it when" rows are how a lane decides what to skip,
and a row that never means "skip" trains the reader to read the whole table
anyway, which is the cost the index exists to remove.

**What would satisfy it.** Move the section name into the always-read line at
`testing.md:7` and drop the row:

```markdown
**Always read:** **Gotchas** · **Running the suite** · **Definition of done for this lane**
```

## SHOULD_FIX 2

**Rule.** `authoring.md` § "A pack may not instruct a tool the lane does not
have".

`project.md:141-143`:

```
Any lane may reach for the `unity-cli` skill for exact current CLI syntax
rather than hand-typing a remembered command
```

`project.md` is read by every lane. Three have no `Bash` — `scout`
(`scout.md:4`), `story-author` (`story-author.md:4`) and `docs-engineer`
(`docs-engineer.md:4`) — so for those three the sentence offers CLI syntax for
commands they cannot run. `docs.md:5-7` already states this correctly for its
own lane, which makes the two files disagree.

**What would satisfy it.** Qualify the sentence:

```markdown
Any lane with `Bash` may reach for the `unity-cli` skill for exact current CLI
syntax rather than hand-typing a remembered command
```

Noted but not raised as part of this: no agent's `tools:` line grants a
`Skill` tool. The network's own convention for this is `test-engineer.md:31`
— "If it names a repo skill to consult, read that too" — i.e. a lane reads a
skill file rather than invoking it, which the `Read` grant covers. Naming the
skill is therefore sound; only "any lane" is wrong.

## SHOULD_FIX 3

**Rule.** `authoring.md` § "Indexing a pack or profile", rule 3 — a section is
conditional only if the agent can evaluate its condition *before reading it*.

Two rows gate the Unity CLI material on a fact the section itself supplies:

| File:line | Condition |
|---|---|
| `backend.md:18` | `the Editor is already open and hand-editing/rebuilding is slower than a live command eval loop` |
| `project.md:45` | `your order benefits from a running Editor, fast iteration, or a Unity-domain skill outside plain C#` |

The command that answers "is the Editor open" — `unity pipeline list` — is
named only inside `backend.md:96-104`, and a lane that does not know a live
Editor is usable cannot judge whether its order would benefit from one. This
is the shape `authoring.md` names as its own worked example ("read Reuse when
you are about to write a helper"): the condition can only be evaluated after
the fact it depends on has been read.

`backend.md:100-101` also carries a hazard — "the syntax has already drifted
once since this pack's authoring" — and `authoring.md` places gotchas in
always-read "regardless of length".

**What would satisfy it.** Move both sections into their files' always-read
lines (`backend.md:10-12`, `project.md:38`). The cost is roughly nine lines per
dispatch; the tie-break in `authoring.md` is explicit — "When you cannot tell
which one a section is, it is always-read."

## Duplication considered and not raised

The package dependency chain appears in three scope files:

| File:line | Form |
|---|---|
| `project.md:60-62` | guardrail 2, always-read by every lane |
| `backend.md:24-26` | always-read, plus "never add a reference that runs the chain backwards" |
| `architecture.md:19-21` | always-read, plus "a lower package depending on a higher one is wrong by construction" |

`authoring.md` § "One rule, one home" governs *rules across protocol files*,
and this is a fact repeated across the capability layer, each copy carrying a
different lane-specific consequence. `backend` and `design` both also read
`project.md`, so two of the three are genuine duplicates for the same reader
— but each adds a judgment the guardrail does not state, and the chain is the
project's central invariant. Not a finding under any named rule. It is worth
knowing that a package rename now requires three edits.

`docs.md:30-38` restating guardrail 4, and `backend.md:20-33` restating
guardrails 1-3 "in code terms", are the established pattern
(`datoro/capabilities/backend.md` § "Guardrails, in code terms") and bind the
numbered rule to paths. Not raised.

## What passed

| Check | Result |
|---|---|
| `claude plugin validate plugins/agentic-core` | passes — manifest validation clean |
| Frontmatter parses | n/a to scope — no agent file in scope, and none was touched |
| `model:` / `effort:` declared | n/a to scope, same reason |
| Four-layer split | no message shape, report block or role definition in any pack; no lane name or trigger hard-coded outside the profile |
| `## Index` present | `project.md:32`, `backend.md:8`, `testing.md:5`, `architecture.md:7`, `docs.md:9`, `product.md:6` |
| Index complete | 6/6, 7/7, 5/5, 5/5, 4/4, 3/3 sections against `##` headings; no name in both the always-read line and the table |
| `## Contents` not `## Index` | `phases.md:9` — correct, it is the orchestrator's full read (`authoring.md` § "Indexing"); 5 items against 5 headings |
| Always-read vs conditional | correct everywhere except the two rows in § SHOULD_FIX 3 and the row in § SHOULD_FIX 1; gotchas and guardrails are always-read in all five packs |
| Tool premises | one failure (§ FINDING 1), one overreach (§ SHOULD_FIX 2); `docs.md:5-7` correctly states `docs-engineer` has no `Bash`; `dotnet`, `powershell` and `unity` commands in `backend.md`, `testing.md`, `architecture.md` and `project.md` all belong to lanes whose `tools:` line carries `Bash` |
| MCP | `grep -rn "mcp__" projects/impact` returns one hit, `project.md:158`, which denies the grant — consistent with `Impact/.mcp.json` not existing |
| Lane routing table | `project.md:93-104` — all ten rows resolve to `plugins/agentic-core/agents/`; nine distinct agents, `tech-lead` twice; `frontend-engineer` and `quantitative-researcher` unbound and explained at `project.md:110-127` |
| Packs named in the routing table exist | `product.md`, `architecture.md`, `backend.md`, `testing.md`, `docs.md` — 5/5 |
| Phase order | `phases.md:28-37` against `orchestrator.md` § 2: ground-truth → framing → specification → design → build → verify → close, in order; `intake` carries no row, matching `datoro/phases.md` |
| `verify` rows machine-readable | two rows, `integration` and `review`, with `quant-audit` absent and its absence justified at `phases.md:39-43` — this is what `check_report.py` reads |
| Bullet length | 44 bullets across the nine scope files, 0 over `authoring.md`'s 200-character instruction limit |
| `.agentic.json` | `C:\projects\impact\.agentic.json` — `agenticRoot: "../investments/.agentic"` resolves against `C:\projects\impact` to `C:\projects\investments\.agentic`; `project: "impact"` matches `projects/impact/` |
| Written for a model | no provenance or change history in any scope file; mappings are tables; no bullet carries more than one fact |
