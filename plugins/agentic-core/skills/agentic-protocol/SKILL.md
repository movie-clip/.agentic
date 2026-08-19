---
name: agentic-protocol
description: The shared contract between the orchestrator and specialist agents in the .agentic network - work-order shape, agent report shape, gate rules, and how an agent binds itself to a project context pack. Load this whenever you are writing, dispatching, or fulfilling a work order, or when authoring a new agent or capability pack for .agentic.
---

> **Single source:** the canonical contract lives in `<agenticRoot>/PROTOCOL.md`,
> which every agent reads during binding. This skill mirrors it for the
> orchestrator's use. If they ever disagree, `PROTOCOL.md` wins and this file
> needs updating.


# Agentic protocol

Two message shapes and one binding rule. Everything in the network speaks these.

## Binding: how an agent finds its project context

Every specialist agent, as its **first action**, before reading any source file:

1. Read `.agentic.json` at the repo root of the current working directory.
   ```json
   { "agenticRoot": "../.agentic", "project": "portfolio" }
   ```
2. Resolve `<agenticRoot>/projects/<project>/project.md` — the project profile
   (stack, paths, commands, hard guardrails). Read it fully.
3. Read `<agenticRoot>/projects/<project>/capabilities/<your-lane>.md` — your
   capability pack. Read it fully.
4. Only then start work.

If `.agentic.json` is missing, **stop and report `BLOCKED`**. Do not guess the
project layout — a specialist working from inference is exactly the failure mode
this network exists to prevent.

## Shape 1 — the work order (orchestrator → agent)

Dispatch this verbatim as the subagent prompt. Never send free-form prose.

```
WORK ORDER <id>
lane:        product | quant | recon | design | backend | frontend | test | docs | integration | quant-audit | review
mode:        <for lanes with modes — tech-lead: DESIGN | INTEGRATION; quant-analyst: RESEARCH | AUDIT>
story:       <path to story file, or NONE>
tickets:     <T-x.y.z, ...  or NONE>

goal:        <one sentence, outcome not method>

scope:
  - <file / dir / glob this order may touch>
  - <...>

inputs:
  - <path to doc, prior report, AC list the agent must read>

definition_of_done:
  - <checkable statement>
  - <checkable statement>

non_goals:
  - <thing an eager agent would do that it must not>

verification:  <exact command(s) to run, or NONE if read-only>
```

Rules for writing one:

- **`scope` is a fence, not a hint.** Anything outside it requires the agent to
  stop and report, not to proceed.
- **`goal` states an outcome.** "Cover the sector-drawdown engine's withheld
  path" — not "add three tests to test_drawdown.py".
- **`non_goals` is where you spend your effort.** It is the field that prevents
  scope creep, and the one people skip.
- One lane per order. If an order needs both a schema and a component, it is two
  orders with a dependency.

## Shape 2 — the report (agent → orchestrator)

The orchestrator sees **only this**. Return it as the last thing in your run,
with no trailing commentary.

```
REPORT <id>
status:      DONE | PARTIAL | BLOCKED | REFUSED | CHANGES_REQUESTED

changed:
  - <path> — <what changed, one line>

verification:
  command:   <what you ran>
  result:    PASS | FAIL | NOT_RUN
  detail:    <failure summary, or the counts on pass>

contract_notes:
  - <any schema / type / doc that now needs a matching change elsewhere>

handoff:
  - <what the next lane needs to know: new fixture names, prop shapes, route paths>

risks:
  - <anything you were unsure about, or a guardrail you had to interpret>
```

Field discipline:

- `status: PARTIAL` is honourable. Claiming `DONE` on unverified work is the
  single most expensive failure in this network.
- `REFUSED` when the order contradicts a project guardrail — say which one.
- `CHANGES_REQUESTED` is the tech lead's verdict when engineer output does not
  integrate. The change requests go in `handoff`, one block each.
- `contract_notes` is how cross-lane drift gets caught. A backend agent that
  changes a Pydantic schema **must** emit a contract note naming the TS type and
  the `docs/contracts/<area>-fields.md` that now lag.
- Empty sections stay in with `- none`. Silence is ambiguous.

## Shape 3 — the change request (tech lead → engineer, relayed)

The tech lead cannot dispatch. It emits change requests; the orchestrator
relays each one to the owning lane as a fresh work order whose `inputs` carry
the request verbatim.

```
CHANGE REQUEST <n>
lane:     <owning lane>
severity: BLOCKING | SHOULD_FIX
finding:  <what is wrong — file:line, specific>
why:      <the consequence, not the rule>
expected: <what would satisfy it>
```

- Only `BLOCKING` holds the slice. `SHOULD_FIX` is recorded and surfaced to the
  human at close-out.
- An engineer receiving a change request fixes **only** what it names. Adjacent
  improvements are a new order, not a bonus.
- Two rounds maximum on the same finding. A third means the request is unclear
  or the design is wrong — escalate to the human rather than looping.

## Gate rules

- A lane is not closed until its `verification.result` is `PASS`, or the order
  was explicitly read-only.
- The mechanical gates in the repo (test runner, pre-commit hook, CI) are the
  final authority. No agent may bypass, weaken, or work around a hook. If a
  commit is blocked, the answer is to fix the work, never to skip the gate.
- Three gates, in order, checking different things. The **quant analyst** gates
  the mathematics: are the numbers correct and honestly labelled. The **tech
  lead** gates engineering: contracts aligned across lanes, design followed. The
  **reviewer** gates acceptance: does this satisfy the story.
  They are not substitutes. A wrong formula can be engineered perfectly, tested
  thoroughly, and satisfy every acceptance criterion — and every gate but the
  first will pass it. Where a change touches analytics, the quant gate runs
  first, because the others are meaningless if it fails.
- The reviewer's `FAIL` blocks close-out. The orchestrator re-dispatches to the
  owning lane with the failure text as an input — it does not fix things itself.

## Authoring rules for new agents and packs

**Agent file** (`plugins/agentic-core/agents/<name>.md`) is project-agnostic.
It contains: the role, the binding steps above, tool discipline, report shape.
It must contain **zero** paths, framework names, or conventions from any
specific repo. If you are tempted to write `pytest` in an agent file, that line
belongs in a capability pack.

**Capability pack** (`projects/<project>/capabilities/<lane>.md`) is where all
repo specifics live: paths, frameworks, fixtures, gotchas, commands, the
"things that bit us before" list. This is the file that goes stale — treat it
as documentation of hard-won friction, and update it whenever a run surfaces
something the pack did not warn about.
