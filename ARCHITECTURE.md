# `.agentic` — agent network architecture

Version 0.1. Lives at `C:\projects\investments\.agentic`, one level above the
repos it drives. First bound project: `portfolio` (quant-research-lab).

---

## 1. The problem this solves

Today `portfolio/.claude/skills/` holds a **linear pipeline**:

```
quant-research → write-story → build-story → write-tests → verify-story → update-docs
```

It works, but everything runs in one context. `build-story` carries the whole
project in its head — backend conventions, UI design system, pytest fixtures,
FMP caching, doc contracts — and hands the model 2,500 lines of skill text for a
change that might touch three files. Two consequences:

- **Context dilution.** The test conventions compete for attention with the
  Recharts shim and the trust-ladder rules, even on a backend-only ticket.
- **No isolation.** A wrong turn in the UI slice pollutes the reasoning of the
  backend slice, because they share one transcript.

The fix is not more skills. It is **separating who decides from who does.**

## 2. The model

```
   you (chat) ── "add a per-sector drawdown breakdown to the Risk tab"
        │
        ▼
  ┌──────────────┐   1. PRODUCER — where does this belong?
  │              │──────► roadmap · epic · story shape · dependencies
  │              │◄────── delivery brief          ── you approve ──┐
  │              │                                                  │
  │              │   [story authoring — human gate, repo skill] ◄───┘
  │ ORCHESTRATOR │
  │              │   2. SCOUT — read-only map of the area
  │  main session│
  │  plans       │   3. TECH LEAD (design) — the contract, reuse, lane split
  │  dispatches  │──────► technical plan  ── you approve the lane plan ──┐
  │  relays      │                                                        │
  │              │   4. ENGINEERS, one order at a time ◄──────────────────┘
  │              │──────► backend → frontend → test → docs
  │              │◄────── reports · contract_notes · handoff
  │              │
  │              │   5. TECH LEAD (integration) — engineering gate
  │              │◄────── PASS │ CHANGES_REQUESTED ──┐
  │              │                                    │ relayed verbatim
  │              │──────► back to the owning lane ────┘
  │              │
  │              │   6. REVIEWER — acceptance gate vs the story
  └──────┬───────┘◄────── PASS │ FAIL
         ▼
   you run the suite and commit
```

Each specialist runs in its own context with its own tools and its own
capability pack. The orchestrator sees only their reports.

Three layers, deliberately separated:

| Layer | Lives in | Changes when |
|---|---|---|
| **Roles** — what a test engineer *is*, how it reports | `plugins/agentic-core/agents/` | never (project-agnostic) |
| **Protocol** — work-order + report shapes, gate rules | `plugins/agentic-core/skills/agentic-protocol/` | rarely |
| **Context packs** — how *this* repo does testing | `projects/<name>/capabilities/` | every time the repo evolves |

That split is the whole point of putting `.agentic` outside the repo. Point it
at a second project later and only the `projects/<name>/` folder is new.

## 3. Binding a repo to the network

The repo declares its own binding. `portfolio/.agentic.json`:

```json
{ "agenticRoot": "../.agentic", "project": "portfolio" }
```

Every agent's first action is: read `.agentic.json` from the repo root, resolve
`agenticRoot`, load `projects/<project>/project.md` plus its own capability
pack. Nothing else in the network hardcodes a path, so moving `.agentic` or
adding a second repo is a one-line edit.

## 4. Roster (v0.1)

| Agent | Tools | Job |
|---|---|---|
| `quant-analyst` | read-only + bash | **Owns guardrail one.** Research mode: formulas, grounding, trust-class analysis before a story exists. Audit mode: independently *recomputes* published numbers and checks trust labels against the basis they rest on. |
| `producer` | read-only | **The front door.** Owns the roadmap: does this already exist, does it fit the active epic, is it a new epic, should it be declined. Shapes stories as vertical slices, sequences them, names dependencies. |
| `scout` | read-only | Recon. "Where does this live, what already exists, what will this touch" — compressed to the two hundred words that matter. |
| `tech-lead` | read-only + bash | **Manages the engineers.** Design mode: settles the contract and reuse before anyone codes. Integration mode: the engineering gate, returning change requests per lane. |
| `backend-engineer` | read/write/bash | Schemas → service → route → registration. Owns the contract source of truth. |
| `frontend-engineer` | read/write/bash | TS types mirroring schemas; cards built on the design-system primitives. |
| `test-engineer` | read/write/bash | Everything under a test file. Knows the network guard, shared fixtures, goldens, the assertion-brittleness rules. |
| `docs-engineer` | read/write | Contracts, methodology, slice log, shipped-state inventory. |
| `reviewer` | read-only + bash | The acceptance gate: ACs one by one, test-plan fidelity, trust-state spot checks. PASS / FAIL. |

All nine are live, each with a capability pack for `portfolio`.

### Why three gates

| Gate | Question | Runs |
|---|---|---|
| `quant-analyst` | Are the numbers correct and honestly labelled? | first, when analytics changed |
| `tech-lead` | Do the lanes cohere — contracts, reuse, design followed? | second |
| `reviewer` | Does this satisfy the story? | last |

None subsumes another, and the order matters. A wrong formula can be engineered
flawlessly, tested thoroughly, and satisfy every acceptance criterion — the
second and third gates would both pass it, because neither is looking at the
arithmetic. That is why the quant gate runs first: if the mathematics is wrong,
the other two are measuring the wrong thing.

The converse holds too. Correct math can be wired into the wrong lane, or ship
a feature nobody asked for. One gate holding all three standards in one context
is exactly the dilution this network exists to avoid.

### Why the producer is the entry point

A request that arrives as "add X" is a request to change the plan. Without a
producer, the orchestrator either changes the plan implicitly — producing work
with no place in the roadmap — or the human does it manually every time.

The producer is also where **"no" lives**: already shipped, already storied,
deliberately left open with a recorded reason, or out of scope. In a repo with
131 stories across 35 epics, that check is the highest-leverage thing in the
flow.

## 5. Design rules

**The orchestrator does not write code, and does not make specialist calls.** It
plans, dispatches and relays. If it starts editing files you have lost the
isolation you paid for; if it starts deciding scope or contracts, you have lost
the specialists.

**The orchestrator stays in the main session.** Assume a subagent cannot spawn
another subagent. Fan-out is one level deep, driven from the top. So the
producer cannot commission a story and the tech lead cannot dispatch an
engineer — they emit briefs, plans and change requests, and the orchestrator
carries them. Relay **verbatim**: a paraphrased change request is the
orchestrator's judgment wearing the tech lead's authority.

**Managing is relaying, and that is enough.** "The tech lead can request changes
from any engineer" works, mechanically, as: tech lead emits a change request →
orchestrator opens a new work order on the owning lane, scope fenced to that
finding, request text quoted → engineer fixes exactly that → integration review
re-runs. Two rounds on the same finding, then escalate to the human.

**Vertical slice is the unit of work, lane is the unit of dispatch.** One story
= one vertical slice = several work orders across lanes (schema, engine, UI,
tests, docs). Never dispatch a lane that does not trace to a story ticket.

**Every dispatch is a contract.** A work order names goal, scope, inputs,
definition of done, and explicit non-goals. An agent that has to guess its
boundary will expand it.

**Reports are structured, not prose.** The orchestrator only sees the report —
if it is chatty, integration is guesswork. See `agentic-protocol`.

**Gates stay mechanical.** `run_all_tests.py`, the pre-commit hook and CI remain
the actual authority. The reviewer agent is a *pre-*check that catches problems
cheaply; it never replaces a green suite.

**Skills stay in the repo, agents stay in `.agentic`.** A skill is procedural
knowledge the repo owns and versions with its code (`ui-polish`, `fmp-data`).
An agent is a worker with a context budget. Agents *invoke* repo skills — the
existing eight are not replaced, they become tools the specialists reach for.

## 6. Relationship to the existing skills

| Existing skill | Fate |
|---|---|
| `quant-research` | unchanged — a research lane the orchestrator can route to |
| `write-story` | unchanged — still authors the story before any dispatch |
| `build-story` | **thins out.** Its per-lane knowledge migrates to capability packs; what remains is ticket sequencing, which the orchestrator absorbs |
| `write-tests` | becomes the body of `capabilities/testing.md`, invoked by `test-engineer` |
| `verify-story` | becomes the `reviewer` agent's checklist |
| `update-docs` | becomes `docs-engineer`'s capability pack |
| `ui-polish`, `fmp-data` | stay as-is — reference skills the specialists load on demand |

Nothing is deleted in v0.1. The network reads the existing skills; migration is
incremental and reversible.

## 7. Roadmap

- **v0.1** — protocol, orchestrator, `scout` + `test-engineer`, portfolio profile.
- **v0.2 (this)** — `producer` and `tech-lead` added; all eight roles live; backend / frontend / docs / product / architecture packs written; two-gate model; change-request relay.
- **v0.2.1** — `quant-analyst` added, owning guardrail one; three-gate model.
- **v0.3** — run it on one real story end to end and correct the protocol where it chafes. The work-order and change-request shapes are still guesses until something real passes through them.
- **v0.4** — thin `build-story` down now that its per-lane knowledge lives in packs; retire the overlap deliberately rather than letting two sources of truth drift.
- **v0.5** — persisted run log under `.agentic/runs/` so a plan survives a session restart, and the producer can see what was attempted.
- **v0.6** — second project bound, to test whether the agnostic/specific split actually holds.
