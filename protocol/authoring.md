<!-- Extension: AUTHORING a new agent, pack or protocol section.
     Not read at runtime by anyone. -->

# Protocol extension — authoring rules

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
| `opus` | `quant-analyst`, `protocol-linter` | **Neither has a downstream check.** A wrong formula is engineered perfectly, tested thoroughly, satisfies every acceptance criterion and passes every other gate; a wrongly passed agent file bills wrong on every dispatch for the rest of its life, and surfaces as a run that cost too much, never as a failure. Both are also the rarest lanes — quant runs only when the substance is mathematical, the linter only on an authoring order. |
| `sonnet` | `producer`, `story-author`, `tech-lead`, `reviewer`, `backend-engineer`, `frontend-engineer`, `test-engineer`, `docs-engineer`, `scout` | Each produces work a later step can catch: a failing test, a gate verdict, `check_report.py`, or the human's approval. |
| `haiku` | none today | Read-only retrieval where **both** halves are cheap: the claims are verifiable by opening the file they cite, *and* the report's own structure is simple enough that getting it wrong costs nothing. `scout` was the occupant and met the first half, never the second — see below. The tier stays because the criterion is sound; nothing currently qualifies. |

**`scout` moved from `haiku` to `sonnet` (v0.5.4).** The old row's reasoning was
about *claim accuracy*, and on that scout was never wrong — every ledger that
checked its findings recorded them as coherent and independently reconfirmed.
What it missed is that a recon report is not only claims. Of five dispatches,
**two returned a head disagreeing with its artifact and one produced a brief
that failed to name six of its own sections** — and that last one is the
expensive kind, because the orchestrator routes off the brief. A brief that does
not index its sections costs a full artifact read, which is the exact cost the
whole head-and-brief design exists to avoid. Deriving the head (v0.5.0) fixes
the counting half; indexing your own document is comprehension, and no script
can do it for you.

### Effort is the second dial, and it is not the model

`model` decides which model runs; **`effort` decides how hard it works.** They
are independent frontmatter fields, and a lane that pins one and inherits the
other is only half-configured.

**Claude Code's implicit default is `xhigh`** — the second-highest of five. So
an agent with no `effort:` line is not running "normally", it is running near
the top of the range. Every lane was doing exactly that until v0.4.4.

**`medium` is this network's baseline.** Two levels are in use:

| Effort | Lanes | Why |
|---|---|---|
| `high` | `producer`, `tech-lead`, `reviewer`, `backend-engineer`, `frontend-engineer` | The lanes that **decide** something: where work belongs, what the contract is, whether it is acceptable, and the two that write the code the contract describes. |
| `medium` | `quant-analyst`, `protocol-linter`, `story-author`, `docs-engineer`, `test-engineer`, `scout` | Everything else. Drafting, applying, testing and retrieval all work against something another lane already fixed; the two Opus lanes sit here because the tier, not the dial, is what buys their judgment. |

`quant-analyst` and `protocol-linter` sit at `medium` **on the model tier, not
on the effort dial**: they are the two lanes on Opus, and the tier is what buys
their judgment. This is a deliberate trade — see the caveat below.

`low` and `max` are not defaults anywhere. `max` is the escalation for a lane
the run has shown to be struggling, on the same evidence rule as a model
escalation: a `BLOCKED` that is not a missing input, or a second change-request
round.

**Lower effort is not just cheaper, it is different.** It produces fewer and
more-consolidated tool calls, less preamble, and terser confirmations. That is
usually an improvement for a lane whose output is a structured report, but it
changes what those lanes do, not only what they cost.

**Two things to watch on the next full run**, because both are untested at these
settings:

- **`quant-analyst` at `medium`.** It found the run's one MATERIAL defect at
  `xhigh`. Opus at `medium` is a reasonable bet — the tier is doing the work —
  but the gate that has no downstream check is the worst place for a silent
  regression. If an audit passes something a later gate catches, raise it.
- **`scout` at `sonnet`/`medium`.** It moved up a model tier on structural
  grounds, not accuracy ones, so watch the thing that moved it: does the
  `## Orchestrator brief` name every section below it, and does the head come
  back matching the artifact? Its citations were already complete at `haiku` and
  are not the question. If the briefs come back clean, the move paid for itself;
  if they do not, the problem is the order's framing, not the tier.
- **`protocol-linter` at all.** It has never run. It is the second Opus lane and
  the second gate with no downstream check, so a wrong `PASS` from it is as
  invisible as a wrong audit. Judge its first dispatches on whether every `FAIL`
  cites a rule, a file and a line — a finding missing any of the three is the
  lane drifting into style review.

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

The other two gates are not: `quant-audit` and `protocol-lint` run on Opus,
for the reason the model table gives — nothing downstream checks them. These two
are different because something does. `integration` is followed by `review`, and
`review` by the human's acceptance of the work itself.

And because v0.4 moved their load-bearing checks off the model and onto
mechanisms. `check_report.py` enforces the report shape, the head's counts and
the brief's completeness; acceptance criteria must name the observation that
would prove them false; the external-anchor rule in `gates.md` says what a
gate must check against. A gate leaning on structure is far less
tier-sensitive than one leaning on the model noticing something — and these
are the two gates with the most structure to lean on.

If gate quality visibly drops, `tech-lead` in `INTEGRATION` mode is the first
lane to move back to Opus — it is the gate with the widest surface and the one
whose misses are hardest to see. Move it because the ledger shows a problem,
not on a hunch.

### Escalating a single dispatch

The frontmatter is a **default, not a ceiling**. The orchestrator may override
the model for one dispatch, and should when the run has produced evidence that
the lane is out of its depth:

- a lane returned `BLOCKED` on something that is not a missing input, or
- a finding reaches its **second** change-request round.

Both are recorded in the ledger, so an escalation is visible after the fact and
the pattern is reviewable. Escalate on evidence the run produced — never
pre-emptively, because a pre-emptive escalation is just a more expensive default
with extra steps.

## Writing for the reader you actually have

Everything under `PROTOCOL.md`, `protocol/`, `projects/` and `agents/` is read
**only by models**, once per dispatch, and by many dispatches per run. That
changes what earns its place:

- **Keep the *why* that changes behaviour.** A rule with a stated consequence is
  followed more reliably than a bare imperative, and the consequence is often
  the thing that lets an agent handle a case the rule did not anticipate.
- **Cut the history of how the rule was discovered.** "v0.2 had eleven copies
  and two had drifted" is provenance. It is worth recording — in
  `CHANGELOG.md`, whose reader is a human deciding whether to trust the
  design. It changes no agent's behaviour, and every agent pays for it on every
  dispatch.
- **Prefer a table to a paragraph** wherever the content is a mapping. Tables
  are shorter, and they make an omission visible as an empty cell.
- **One fact per bullet, under 200 characters.**

The human-facing artifacts are the exception, and there are only four: the
delivery brief's recommendation, the story's acceptance criteria, the gate
verdicts, and the close-out report. Those are read by the person who approves
them. Write those for that person.

## Indexing a pack or profile

Packs and profiles are read by index (core § 1, steps 4–5). Every one of them
opens with:

**Unless it is read in full, in which case it opens with `## Contents`.**
`phases.md` is the case: it has exactly one reader, that reader needs all of
it, and an index inviting it to skip a section would be wrong. Give a
full-read file over ~100 lines a `## Contents` list instead — same job of
letting a partial read see the whole scope, without the instruction to skip.
An index is a claim that skipping is safe; make it only where it is.

```markdown
## Index
Always read: <the sections no lane may skip — guardrails, trust rules>
| Section | Read it when |
|---|---|
| Fixtures | your order adds or changes a test |
| FMP cache | your order touches market data |
```

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
mention it in `risks`, not to emit a correction. In the first closed run the
docs lane hit exactly this three times and never once filed it as a pack
correction.

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
cost for no return. The current grants: engines and tests get everything;
`quant-analyst` gets the probing tools because AUDIT recomputes independently and
must be able to call the engine it is judging rather than read the code and
infer; `reviewer` gets no mutating tool, because a gate that verifies must not
also change the tree it is verifying.

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
