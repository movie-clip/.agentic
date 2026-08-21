<!-- Extension: AUTHORING a new agent, pack or protocol section.
     Not read at runtime by anyone. -->

# Protocol extension — authoring rules

## The three-layer split

| Layer | Lives in | Contains | Must not contain |
|---|---|---|---|
| Protocol | `PROTOCOL.md` + `protocol/*.md` | message shapes, binding, gates | anything about a specific repo, anything about a specific role's craft |
| Role | `plugins/agentic-core/agents/<name>.md` | what this lane judges, tool discipline | any path, framework or convention from a specific repo |
| Capability | `projects/<project>/capabilities/<lane>.md` | paths, frameworks, fixtures, commands, gotchas, external anchors | message shapes, role definitions |

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

## Choosing a model for an agent

Every agent file carries an explicit `model:`. **Never `inherit`** — inherit
means the lane silently runs on whatever the main session happens to be, so a
ten-dispatch run quietly bills ten times at the orchestrator's tier and nothing
in the run says so. **Never `fable`.**

**Sonnet is the ceiling.** It is the default for any lane that produces work
something downstream can catch.

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
| `opus` | `quant-analyst` | A wrong formula is engineered perfectly, tested thoroughly, satisfies every acceptance criterion, and passes every other gate. **There is no downstream check.** It is also the rarest lane — it runs only when the substance is mathematical. |
| `sonnet` | `producer`, `story-author`, `tech-lead`, `reviewer`, `backend-engineer`, `frontend-engineer`, `test-engineer`, `docs-engineer` | Each produces work a later step can catch: a failing test, a gate verdict, `check_report.py`, or the human's approval. |
| `haiku` | `scout` | Read-only retrieval — glob, grep, read, report `file:line`. Every claim it makes is cheap to verify by opening the file it cites. |

### Effort is the second dial, and it is not the model

`model` decides which model runs; **`effort` decides how hard it works.** They
are independent frontmatter fields, and a lane that pins one and inherits the
other is only half-configured.

**Claude Code's implicit default is `xhigh`** — the second-highest of five. So
an agent with no `effort:` line is not running "normally", it is running near
the top of the range. All ten lanes were doing exactly that until v0.4.4.

**`medium` is this network's baseline.** Two levels are in use:

| Effort | Lanes | Why |
|---|---|---|
| `high` | `producer`, `tech-lead`, `reviewer`, `backend-engineer`, `frontend-engineer` | The lanes that **decide** something: where work belongs, what the contract is, whether it is acceptable, and the two that write the code the contract describes. |
| `medium` | `quant-analyst`, `story-author`, `docs-engineer`, `test-engineer`, `scout` | Everything else. Drafting, applying, testing and retrieval all work against something another lane already fixed. |

`quant-analyst` sits at `medium` **on the model tier, not on the effort dial**:
it is the one lane on Opus, and the tier is what buys its judgment. This is a
deliberate trade — see the caveat below.

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
- **`scout` at `medium`.** Retrieval is the canonical `low` task, so this is
  the one lane deliberately running above the cheapest setting that would do.
  Judge it on whether `file:line` citations stay complete, not on cost.

### Two things `effort` does not control

**Extended thinking is inherited, not per-agent.** A subagent takes the main
session's thinking configuration: on if your session has it on, off if not.
There is no per-agent override, so this is a property of how *you* run the
orchestrator, not something the network can set for a lane.

**`maxTurns` is a separate ceiling** and is also unset here. It caps agentic
turns rather than depth. Leave it unset unless a lane demonstrably runs away —
a turn cap that fires mid-task produces a truncated report, which is worse than
an expensive one, and `status: PARTIAL` will not always catch it.

### Why the gates are on Sonnet

Because v0.4 moved their load-bearing checks off the model and onto mechanisms.
`check_report.py` enforces the report shape, the head's counts and the brief's
completeness; acceptance criteria must name the observation that would prove
them false; the external-anchor rule in `gates.md` says what a gate must check
against. A gate leaning on structure is far less tier-sensitive than one leaning
on the model noticing something.

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
  `ARCHITECTURE.md`, whose reader is a human deciding whether to trust the
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

## Adding a project

Create `projects/<name>/project.md` plus capability packs, and drop
`.agentic.json` in that repo. The `plugins/` layer is untouched — that is the
entire reason for the split, and the test of whether it holds.
