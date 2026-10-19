<!-- Extension: the rules the AUTHORING gate enforces, and the spec anyone
     writing an agent, skill, pack or protocol section writes to.
     `protocol-linter` reads this file in full on every dispatch. -->

# Protocol extension — authoring rules

Read in full. Every section is a rule `protocol-linter` can fail a file on, and
a `FAIL` must cite one by name — except § "Writing for the reader you actually
have", which it reports as `SHOULD_FIX` and never fails on alone.

## Contents

- **The four-layer split** — which of the four files a given line belongs in
- **One rule, one home** — no rule in two files, and where to place a new one
- **The frontmatter has to parse, or none of it applies** — `model:`,
  `effort:` and `tools:` are text until it does
- **Choosing a model for an agent** — `model:`, `effort:`, and escalation
- **Writing for the reader you actually have** — what earns a line its place
- **Two instructions may not disagree** — a lane reading both must know which
  action to take
- **Indexing a pack or profile** — `## Index` vs `## Contents`, and the
  always-read test
- **A pack may not instruct a tool the lane does not have** — check `tools:`
  before writing a command
- **The project tool server** — per-lane grants and what they may assume
- **Adding a project** — the files a new project needs
- **Wiring a tracker** — the `## Tracker` block, and what the repo needs
  before it

## The four-layer split

| Layer | Lives in | Contains | Must not contain |
|---|---|---|---|
| Protocol | `PROTOCOL.md` + `protocol/*.md` | message shapes, binding, gates | anything about a specific repo, anything about a specific role's craft |
| Role | `plugins/agentic-core/agents/<name>.md` | what this lane judges, tool discipline | any path, framework or convention from a specific repo |
| Capability | `projects/<project>/capabilities/<lane>.md`, `project.md`, and `phases.md` | paths, frameworks, fixtures, commands, gotchas, external anchors; **which lane fills each phase and the clause that fires it** | message shapes, role definitions |
| Skill | `plugins/agentic-core/skills/<name>/SKILL.md` | **sequence** — how a run is opened, what happens between a head returning and the next dispatch, how one is closed | any rule the protocol states, and any lane or trigger the project declares; it cites both |

If you are tempted to write `pytest` in an agent file, that line belongs in a
capability pack. If you are tempted to paste the report block into a pack, it
belongs nowhere — point at `PROTOCOL.md`.

## One rule, one home

**Agent files do not restate the shapes.** The work order, report, head and
change request are defined in the protocol and nowhere else. An agent file that
pastes the report block creates a copy that will drift.

**The protocol partition is not an exception to this.** `PROTOCOL.md` and each
file under `protocol/` are disjoint: no rule appears in two of them. When you
add a rule, place it in exactly one file, chosen by *who needs it*:

- every lane needs it → core
- only the dispatcher → `orchestrator.md`
- only a gate → `gates.md`
- only the docs lane at close-out → `packs.md`
- only a human or an agent writing network files → `authoring.md`

A rule that seems to belong in two places is usually two rules stated at the
wrong level of abstraction. Split it before duplicating it.

**A skill is not a fifth place to put a rule.** It is the only layer that can
restate one without looking like a copy, because a step reads naturally as
"here is what to do now" rather than as a second definition. The test is
whether the text would still be true if the run happened in a different order:
if it would, it is a rule and belongs in the protocol, and the step cites it.
`orchestrate-feature` opens by telling you to read `orchestrator.md` and that
everything below assumes it — so a step that re-argues an extension's rule is
arguing with a file the reader has already read, and the two copies drift
against a reader who cannot tell which is current.

## The frontmatter has to parse, or none of it applies

`model:`, `effort:` and `tools:` are declarations only for as long as the YAML
block around them parses. When it does not, Claude Code still loads the agent —
with its name taken from the filename and **every other field silently
dropped**. The lane then runs on the session's default model and effort, and
with the parent's entire tool roster in place of its own allowlist, which also
means losing the `mcp__*` tools it declared and nothing else grants.

Nothing warns, at any verbosity. The file still reads correctly to anyone
checking the `model:` and `effort:` rules below by eye, which is why this rule
sits above them.

The break is almost always a colon in the `description:`, the one field long
enough to contain a sentence:

```yaml
description: ... turn an approved story into a technical plan: layer sequencing
```

An unquoted YAML scalar may not contain `: `, so the parser reads a mapping
where the line intends prose. A dash, a semicolon, or quoting the whole value
all satisfy it; which one is a matter of taste, and taste is not a finding.

**The check is a command, not a reading.** It names the file and the reason:

```bash
claude plugin validate <agenticRoot>/plugins/agentic-core
```

## Choosing a model for an agent

Every agent file carries an explicit `model:`. **Never `inherit`** — inherit
means the lane silently runs on whatever the main session happens to be, so a
ten-dispatch run quietly bills ten times at the orchestrator's tier and nothing
in the run says so. **Never `fable`.**

**Sonnet is the default**, and the ceiling for any lane that produces work
something downstream can catch — which is most of them.

Opus is reserved for one situation, and it is worth stating as a test rather
than a list:

> **Would a wrong answer from this lane be caught by anything downstream —
> a test, a gate, a validator, or the human approval step?**
> If yes, Sonnet. If no, Opus.

Frequency is the second term. A lane that runs on every dispatch multiplies its
tier by the dispatch count; a lane that runs once per run, or only when the
substance calls for it, pays the premium seldom. Highest consequence × lowest
frequency is the profile that earns Opus.

| Model | Lanes | Why |
|---|---|---|
| `opus` | `quantitative-researcher`, `protocol-linter`, `tech-lead` | **The first two have no downstream check.** A wrong formula is engineered perfectly, tested thoroughly, satisfies every acceptance criterion and passes every other gate; a wrongly passed agent file bills wrong on every dispatch for the rest of its life, and surfaces as a run that cost too much, never as a failure. Both are also the rarest lanes — quant runs only when the substance is mathematical, the linter only on an authoring order. `tech-lead` is the owner's ruling (2026-10-18): its design pass fixes the contract every build lane then follows, and it pairs Opus with `low` effort so the tier, not the dial, carries the judgment. |
| `sonnet` | `producer`, `story-author`, `designer`, `reviewer`, `backend-engineer`, `frontend-engineer`, `test-engineer`, `docs-engineer`, `scout` | Each produces work a later step can catch: a failing test, a gate verdict, `check_report.py`, or the human's approval. |
| `haiku` | none today | Read-only retrieval where **both** halves are cheap: the claims are verifiable by opening the file they cite, *and* the report's own structure is simple enough that getting it wrong costs nothing. `scout` was the occupant and met the first half, never the second — see below. The tier stays because the criterion is sound; nothing currently qualifies. |

**A report is not only its claims**, which is the half that is easy to miss when
tiering a read-only lane. The other half is the artifact's own structure: a head
that matches it, and a brief that names every section below it (core § 4). A
script derives the head; indexing your own document is comprehension, and an
orchestrator routing off an unindexed brief pays a full artifact read — the
exact cost the head-and-brief design exists to avoid.

### Effort is the second dial, and it is not the model

`model` decides which model runs; **`effort` decides how hard it works.** They
are independent frontmatter fields, and a lane that pins one and inherits the
other is only half-configured.

**Claude Code's implicit default is `xhigh`** — the second-highest of five. So
an agent with no `effort:` line is not running "normally", it is running near
the top of the range.

**`medium` is this network's baseline.** Three levels are in use:

| Effort | Lanes | Why |
|---|---|---|
| `high` | `producer`, `designer`, `reviewer`, `backend-engineer`, `frontend-engineer` | The lanes that **decide** something: where work belongs, what the user sees, whether it is acceptable, and the two that write the code the contract describes. |
| `low` | `tech-lead` | Opus at the lowest dial: the model tier buys the design and review judgment, and `low` keeps the report terse and the tool calls few. Owner's ruling, 2026-10-18. |
| `medium` | `quantitative-researcher`, `protocol-linter`, `story-author`, `docs-engineer`, `test-engineer`, `scout` | Everything else. Drafting, applying, testing and retrieval all work against something another lane already fixed; the two Opus lanes sit here because the tier, not the dial, is what buys their judgment. |

`quantitative-researcher` and `protocol-linter` sit at `medium` **on the model
tier, not on the effort dial**: they are the two lanes on Opus, and the tier
is what buys their judgment. This is a deliberate trade — see the caveat
below.

`low` is used once, for `tech-lead` on Opus (owner's ruling, 2026-10-18). `max` is not a default anywhere; it is the escalation for a lane
the run has shown to be struggling, on the same evidence rule as a model
escalation: a `BLOCKED` that is not a missing input, or a second change-request
round.

**Lower effort is not just cheaper, it is different.** It produces fewer and
more-consolidated tool calls, less preamble, and terser confirmations. That is
usually an improvement for a lane whose output is a structured report, but it
changes what those lanes do, not only what they cost.

### Two things `effort` does not control

**Extended thinking is inherited, not per-agent.** A subagent takes the main
session's thinking configuration: on if your session has it on, off if not.
There is no per-agent override, so this is a property of how *you* run the
orchestrator, not something the network can set for a lane.

**`maxTurns` is a separate ceiling** and is also unset here. It caps agentic
turns rather than depth. Leave it unset unless a lane demonstrably runs away —
a turn cap that fires mid-task produces a truncated report, which is worse than
an expensive one, and `status: PARTIAL` will not always catch it.

### Why `integration` and `review` are on Sonnet

`quant-audit` and `protocol-lint` are on Opus for the reason the model table
gives — nothing downstream checks them. These two are different because
something does: `integration` is followed by `review`, and `review` by the
human's acceptance of the work itself.

The second reason is the one to reuse when tiering a new gate. **A gate whose
load-bearing checks sit on mechanisms is far less tier-sensitive than one
leaning on the model noticing something.** `check_report.py` enforces the report
shape, the head's counts and the brief's completeness; an acceptance criterion
must name the observation that would prove it false; `gates.md` § 2 says what a
gate must check against. These two have the most structure to lean on.
`ux-review` sits on Sonnet for the same reason: every check in the UX spec names
the screenshot that would prove it false, and taste never blocks.

### Escalating a single dispatch

The frontmatter is a **default, not a ceiling**. The orchestrator may override
the model for one dispatch, and should when the run has produced evidence that
the lane is out of its depth:

- a lane returned `BLOCKED` on something that is not a missing input,
- a finding reaches its **second** change-request round, or
- a gate passed something a later gate then caught — raise the gate that missed
  it, and `quant-audit` before any other, since nothing downstream checks it.

All three are recorded in the ledger, so an escalation is visible after the fact
and the pattern is reviewable. Escalate on evidence the run produced — never
pre-emptively, because a pre-emptive escalation is just a more expensive default
with extra steps.

When quality drops across a run rather than in one dispatch, the standing
default to revisit is `tech-lead` in `INTEGRATION` mode: the widest gate surface
and the least visible misses. Change a default because the ledgers show a
problem, not on a hunch.

## Writing for the reader you actually have

Everything under `PROTOCOL.md`, `protocol/`, `projects/`, `agents/` and
`skills/` is read **only by models**, once per dispatch, and by many dispatches
per run. That changes what earns its place:

- **Keep the *why* that changes behaviour.** A rule with a stated consequence is
  followed more reliably than a bare imperative, and the consequence is often
  the thing that lets an agent handle a case the rule did not anticipate.
- **Cut the history of how the rule was discovered.** "v0.2 had eleven copies
  and two had drifted" is provenance. It is worth recording — in the commit
  message that ships the rule, whose reader is a human deciding whether to trust
  the design. It changes no agent's behaviour, and every agent pays for it on
  every dispatch.
- **Prefer a table to a paragraph** wherever the content is a mapping. Tables
  are shorter, and they make an omission visible as an empty cell.
- **One fact per bullet, under 200 characters.** This is the rule for an
  instruction file, not the one core § 3 sets for a report bullet: those carry
  a `file:line` and are measured separately, so the two numbers differ on
  purpose and neither is a stale copy of the other.

The human-facing artifacts are the exception, and there are only four: the
delivery brief's recommendation, the story's acceptance criteria, the gate
verdicts, and the close-out report. Those are read by the person who approves
them. Write those for that person.

## Two instructions may not disagree

A lane that reads two instructions directing different actions in the same
situation picks one, and nothing records which. Neither a test nor a gate sees
it: the lane's report reads as compliant with whichever one it chose.

- **Within a file and across files a lane reads together** — its pack, the
  profile, and the repo skill the pack names.
- **A rule and its exception are one fact.** Splitting them into separate
  bullets is fine only when each bullet still says which cases it covers.
- **An exception may not be broader than the section that grants it.** A
  carve-out naming a tool the Gotchas prescribe for one case covers that case.

The fix is to reword one of them, or to state which wins. "The pack wins" is a
valid resolution; silence is not.

## Indexing a pack or profile

Packs and profiles are read by index (core § 1, steps 4–5). Every one of them
opens with:

```markdown
## Index
Always read: <the sections no lane may skip — guardrails, trust rules>
| Section | Read it when |
|---|---|
| Fixtures | your order adds or changes a test |
| FMP cache | your order touches market data |
```

**Unless it is read in full, in which case it opens with `## Contents`.**
`phases.md` is the case: it has exactly one reader, that reader needs all of
it, and an index inviting it to skip a section would be wrong. Give a
full-read file over ~100 lines a `## Contents` list instead — same job of
letting a partial read see the whole scope, without the instruction to skip.
An index is a claim that skipping is safe; make it only where it is.

Three rules keep that honest.

1. **Every section is findable** by the name a lane would search for.
2. **Every fact lives in exactly one section.**
3. **A section goes in "always read" unless the agent can evaluate its condition
   before reading it.** This is the rule that decides correctness, and it is
   easy to get wrong in the cheap direction.

On the third: "read it when your order adds an endpoint" is evaluable — the
agent knows what its order says. "Read the gotchas when something fails oddly"
is **not** — the entire point of a gotcha is that you do not know it is coming,
so an agent can only evaluate that condition after already being bitten. The
same trap catches "read Reuse when you are about to write a helper": an agent
that knew it was re-deriving something would not be re-deriving it.

Sections that describe *hazards the reader cannot anticipate* — gotchas, reuse
inventories, unit and sign conventions, edge cases, guardrails — are always-read
regardless of length. Sections that describe *procedures for a named situation*
— a mode, a file type, a close-out step — are conditional. When you cannot tell
which one a section is, it is always-read: the cost of one extra section is a
few hundred tokens, and the cost of the other mistake is a wrong number that
passes every gate.

## A pack may not instruct a tool the lane does not have

Before writing a command into a capability pack, open the agent file and read
its `tools:` line. `scout`, `story-author` and `docs-engineer` have no `Bash`;
a pack telling one of them to run `git diff` is a false premise about the lane
itself, and it will be silently worked around rather than reported.

The same applies to the project tool server below, and bites harder: the grants
are **per lane, not blanket**. A pack section telling `frontend-engineer` to call
`probe_engine` names a tool that lane was deliberately not given, and the failure
looks like an agent ignoring its pack rather than a pack naming a tool that is
not there.

This is the one false premise `pack_corrections` does not catch. That loop is
aimed at facts about the *code* — a path that moved, a fixture that was renamed
— and an agent that cannot run a command tends to substitute something and
mention it in `risks`, not to emit a correction.

So the check belongs here, at authoring time: **every command in a pack must be
runnable by the lane that pack belongs to.**

## The project tool server

A bound repo may expose a tool server to the network over MCP, registered in
that repo's `.mcp.json` under the key **`project`**. The key forms the
`mcp__project__<tool>` prefix, which is why it is generic: the lane definitions
live in the agnostic layer, so they cannot name a repo. Any second project
implements the same contract under the same key, or implements none of it.

| Tool | Returns | Exists because |
|---|---|---|
| `run_tests` | parsed failures + a bounded tail | raw suite output is mostly noise, and a lane pays for all of it |
| `probe_engine` | one route's JSON, computed offline | lanes were hand-writing throwaway probe scripts to answer "what does this actually return?" |
| `build_snapshot` | a valid request payload | the fixture shape is the most-tripped gotcha in the repo |
| `check_gates` | per-gate verdicts | a lane can ask whether its commit will be blocked *before* it is |
| `reset_goldens` | discards generated-file drift | the single most-repeated gotcha in the testing pack |

Two rules govern this contract:

**A tool server may not be the only way to do something.** Every tool above
wraps a command a lane could still run under `Bash`. The server buys a bounded,
parsed return value and a removed class of error — not a capability. A lane whose
work becomes impossible when the server is absent has been mis-designed, and the
pack must name the underlying command too.

**Grant per lane, and grant narrowly.** A subagent's `tools:` line is also what
loads into its context on every dispatch, so an unused tool schema is a standing
cost for no return. Those `tools:` lines are the authority on who holds what —
open the one you need, per the section above. What belongs here is why each grant
is the shape it is, because that is what tells you whether a pack section you are
about to write has a tool to stand on:

- `backend-engineer` and `test-engineer` hold all five. They are the two lanes
  that write engine code and its fixtures, which is the work `probe_engine` and
  `build_snapshot` exist for.
- `quantitative-researcher` holds the three probing tools, because AUDIT
  recomputes independently and must be able to call the engine it is judging
  rather than read the code and infer.
- `frontend-engineer` holds `run_tests`, `check_gates` and `reset_goldens`,
  and deliberately **not** `probe_engine` or `build_snapshot`: it writes no
  engine code, so a probe it needs is a backend report it should be reading
  instead.
- `reviewer` and `tech-lead` hold `run_tests` and `check_gates` and no mutating
  tool, because a gate that verifies must not also change the tree it is
  verifying. Goldens drift the integration gate finds goes to a build lane.

## Adding a project

Create `projects/<name>/project.md` and `projects/<name>/phases.md` plus
capability packs, and drop `.agentic.json` in that repo. The `plugins/` layer is
untouched — that is the entire reason for the split, and the test of whether it
holds.

**The profile is two files, split by reader.** `project.md` is what every lane
reads: guardrails, lane map, mechanical gates. `phases.md` is the orchestrator's
alone. The split is not tidiness — a section a lane cannot use is a section it
pays for on every dispatch, and an index telling it to skip one is advice a
whole-file read cannot take.

**`phases.md`'s `## Phases` table is what makes that true for sequencing.**
`protocol/orchestrator.md` § 2 fixes the phases and their dependency order;
the profile binds each one to a lane, in its own order, with the clause that
decides whether it fires here. A project with no mathematics gate declares no
lane against that row and the phase never fires; a project whose unit of
approved scope is an issue rather than a story says so in the `specification`
row. Neither needs a word changed under `plugins/`.

**And the `verify` rows are machine-read.** `check_report.py` resolves a run's
profile directory — from the ledger's `project:` field, or from the run dir's
own path under `projects/<project>/runs/` — reads `project.md` and `phases.md`
together, and takes the gate set from that table's `verify` rows. A project that
has not split the two yet still works: the table is found in whichever file
holds it. So declaring a gate in the profile is what makes close-out demand
an account of it; there is no second list to keep in step, and no project is
measured against another's gates.

So the test for a new sequencing rule is: **would it still be true in a repo
with different lanes?** If yes it belongs in the skill. If it names a lane, a
directory, a formula or a document this project happens to have, it belongs in
the `## Phases` table's `fires when` column, where the orchestrator reads it as
data.

## Wiring a tracker

A tracker is optional and per project. `orchestrator.md` § 8 says what declaring one permits and what holds
without one.

**The repo side comes first**, because the block is checked against it:

1. `.mcp.json` declares the tracker's MCP server under a key; that key is the
   block's `server`. Credentials come from an environment variable, never a
   literal.
2. `.claude/settings.json` enables that server and denies, for `Bash` and
   `PowerShell` alike: the server's merge tool, pushing to the default branch,
   force-pushing, and the host's CLI (`gh` on GitHub), so the MCP server is the
   only route. That file is the human's to edit.
3. The host protects the default branch: pull requests only, no force-push, no
   deletion, no bypass. This is the enforcement; the deny list is the second
   layer.
4. The board's status options and the repo's labels exist under the names the
   block maps.
5. `CLAUDE.md` says that only the orchestrator commits, to the run's branch,
   and that only a human merges. Every lane reads it, and a `CLAUDE.md` that
   still says "the human commits" contradicts the profile.

**The block** goes in `phases.md`, after `## Phases`, and holds data only.
The procedure is the skill's, so a second tracked project copies six rows, not
a procedure:

```markdown
## Tracker

| Key | Value |
|---|---|
| server | `github` — the `.mcp.json` key |
| repo | `<owner>/<repo>` |
| board | Project <n>, owned by <user or org> |
| statuses | new `Backlog` · building `In progress` · reviewing `In review` · human only `Ready`, `Done` |
| labels | epic `type:epic` · story `type:story` · ticket `type:ticket` |
| branch | `<issue>-<slug>` from `main` |
```

The lint checks four things. The server is a key the repo's `.mcp.json`
declares. No agent's `tools:` line holds `mcp__<server>__*`. The `build` row's
human stop reads **yes**, because the go is the ruling a branch is created on.
And no profile text restates the procedure or the limits in
`orchestrator.md` § 8.
