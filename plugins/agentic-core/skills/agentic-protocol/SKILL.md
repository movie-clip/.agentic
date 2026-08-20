---
name: agentic-protocol
description: The shared contract between the orchestrator and specialist agents in the .agentic network - binding, the work-order shape, the report artifact and report head, change requests, the run ledger, gate rules, and pack maintenance. Load this whenever you are writing, dispatching, or fulfilling a work order, or when authoring a new agent or capability pack for .agentic.
---

# Agentic protocol

**This skill does not contain the protocol. It tells you where it is, and which
part of it is yours.**

## The core — everyone reads this

`<agenticRoot>/PROTOCOL.md`, in full, now, before dispatching or fulfilling
anything. It defines binding, the work order you receive, the report artifact
you write, the report head you return, the three result fields, and the
validator.

## Your extension — read exactly one, or none

| Your role | Also read |
|---|---|
| orchestrator (main session) | `protocol/orchestrator.md` — ledger, relay rule, reading discipline |
| `tech-lead`, `reviewer`, `quant-analyst` | `protocol/gates.md` — verdicts, gate independence, change requests |
| `docs-engineer`, on a close-out order | `protocol/packs.md` — applying `pack_corrections` |
| every other lane | nothing else |
| authoring a new agent or pack | `protocol/authoring.md` |

The core and the extensions are **disjoint**. No rule appears in two of them, so
reading only yours loses nothing — and reading one that is not yours costs
context without adding a rule you are bound by.

## Why these files hold no copy of anything

Until v0.3 this skill carried a full copy of the protocol, with a note saying
`PROTOCOL.md` wins if they disagree. They had already disagreed. A contract with
two copies and a tiebreak rule is a contract that drifts, and this network's
whole purpose is catching drift.

The v0.4 partition does not reintroduce that risk: it splits one contract by
audience, it does not duplicate one. If you are about to paste a message shape
into an agent file, a capability pack, or here — don't. Point at the file that
owns it.

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
