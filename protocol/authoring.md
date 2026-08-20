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
