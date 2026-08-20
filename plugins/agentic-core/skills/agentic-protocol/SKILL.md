---
name: agentic-protocol
description: The shared contract between the orchestrator and specialist agents in the .agentic network - work-order shape, agent report shape, change requests, the run ledger, gate rules, and how an agent binds itself to a project context pack. Load this whenever you are writing, dispatching, or fulfilling a work order, or when authoring a new agent or capability pack for .agentic.
---

# Agentic protocol

**This skill does not contain the protocol. It tells you where it is.**

Read `<agenticRoot>/PROTOCOL.md` in full, now, before dispatching or fulfilling
anything. It is the single definition of:

- **Binding** — how an agent finds `.agentic.json`, the project profile and its
  capability pack.
- **The run ledger** — `runs/<run-id>/`, `run.md`, and why a slice's state does
  not live in the orchestrator's memory.
- **The relay rule** — `inputs` names a path, never a quotation.
- **Shape 1** — the work order.
- **Shape 2** — the report, and why `status`, `verdict` and
  `verification.result` are three different fields.
- **Shape 3** — the change request.
- **Gate rules**, including what makes a gate independent rather than merely
  consistent.
- **Pack maintenance** — how `pack_corrections` closes the loop.
- **Authoring rules** for new agents and packs.

## Why this file is a stub

Until v0.3 this skill carried a full copy of the protocol, with a note saying
`PROTOCOL.md` wins if they disagree. They had already disagreed. A contract with
two copies and a tiebreak rule is a contract that drifts, and this network's
whole purpose is catching drift — so the copy is gone.

If you find yourself about to paste a message shape into an agent file, a
capability pack, or here: don't. Point at `PROTOCOL.md`.

## Finding it

You are probably in a bound repo. `.agentic.json` at (or above) the working
directory names `agenticRoot`, resolved relative to the directory containing
that file:

```json
{ "agenticRoot": "../.agentic", "project": "portfolio" }
```

No `.agentic.json` anywhere up the tree → stop and report `BLOCKED`. Do not
reconstruct the protocol from memory; a half-remembered contract is worse than
an admitted missing one.
