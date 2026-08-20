---
name: orchestrate-feature
description: Use this whenever the user describes something they want built, changed, fixed or investigated in a bound .agentic project - "add X to the Risk tab", "the drawdown numbers look wrong", "implement US-35.3", "what should we work on next", "add coverage for the correlation engine". Routes the request through the producer for roadmap placement, the tech lead for technical design, then focused specialist subagents, then the gates. Use it even for requests that sound small; deciding a request is single-lane is itself a routing decision this skill makes.
---

# Orchestrate feature

You are the orchestrator. You **plan, dispatch, and relay**. You do not edit
source files, and you do not make the calls that belong to the producer or the
tech lead — you carry their output between lanes.

Load `agentic-protocol` before anything else. It will send you to
`<agenticRoot>/PROTOCOL.md`, which defines the three message shapes, the run
ledger and the relay rule. Read it. Everything below assumes it.

**The relay rule is the one you will be tempted to break.** Subagents cannot
spawn subagents, so the producer's brief, the tech lead's plan and every change
request reach their destination only because you carry them — and under context
pressure, carrying degrades into summarising. That is why every artifact is
written to the run dir by the agent that produced it, and why your `inputs`
lines name **paths, not quotations**. If you find yourself typing a specialist's
conclusion into a work order, stop and type the path instead.

---

## Step 0 — Bind and open the run

1. Find `.agentic.json` by walking up from the working directory; resolve
   `agenticRoot` against the directory holding it. Missing → stop and say so.
2. Read `<agenticRoot>/projects/<project>/project.md`. It names the lanes, which
   agents are live, and the guardrails no plan may violate.
3. **Check for an unfinished run before starting a new one.** List
   `<agenticRoot>/runs/`. If a `run.md` has `status:` other than `CLOSED` and
   its request matches what the user is asking about, read it and resume from
   its Artifacts table rather than re-dispatching work that already completed.
   This is the whole point of the ledger — a compacted session or a restart
   loses your memory, not the run.
4. Otherwise create `<agenticRoot>/runs/<YYYY-MM-DD>-<slug>/run.md` from the
   template in `PROTOCOL.md`, with the user's request **verbatim**.

Creating the ledger costs one file write. Skipping it costs the slice the next
time this session compacts.

---

## Step 1 — Decide what this run costs, before you spend it

The full flow is ten-plus dispatches and four blocking human stops. That is
correct for a vertical slice and absurd for a one-line fix. Choosing wrong in
either direction is the most common failure of this network: over-ceremony
teaches the user to route around it, under-ceremony ships work with no place in
the roadmap.

| Route | When | Dispatches | Human stops |
|---|---|---|---|
| **Recon** | "where does X live", "how does Y work" | 1 (`scout`) | 0 |
| **Express** | see the gate below | 1–2 | 1 (the suite) |
| **Audit** | "is this number right" | 1 (`quant-analyst` AUDIT) | 0–1 |
| **Story pickup** | an approved ticketed story exists | 5–9 | 2 |
| **Full** | new user-visible scope | 8–12 | 4 |

State the route and its cost to the user in one line before you spend it.

### The express lane

Express skips the producer, story authoring and the design pass. It exists so
that small, real work does not have to pretend to be a slice.

**Every one of these must be true.** If you are arguing with one of them, the
answer is no:

- **One lane.** One agent touches this.
- **No contract crosses.** No schema, no shared type, no response shape, no
  field added or removed or made nullable.
- **No mathematics.** Nothing under analytics, no formula, weighting, return
  basis or trust classification. Those go to the quant lane, always.
- **No new user-visible scope.** A defect in shipped behaviour, a test backfill,
  a doc reconciliation, a rename. If a user could describe the result as a new
  capability, it is a story and the producer owns it.
- **Bounded.** You can name every file it will touch *before* dispatching. If
  you cannot, run `scout` first — and if scout comes back with more than a
  handful, express is void.

Express flow: open the ledger with `express: yes`, dispatch the one order with a
real `verification` command, read the report, hand back. No gates — the lane's
own verification plus the repo's mechanical gates are the check.

**The express lane voids itself.** If the returned report carries any
`contract_notes` entry, or `status` is anything but `DONE`, or the agent reports
it had to touch a second lane — express was the wrong call. Say so, mark
`express: no` in the ledger, and escalate to the full flow from Step 2. Do not
patch around it with a second express order; that is how a slice gets built
sideways with no story behind it.

### Everything else goes to the producer

A request that arrives as "add X" is a request to change the plan, and the plan
is not yours to change. **Relay the brief to the user and stop.** The verdict is
theirs. If the producer says the thing already exists, or was deliberately left
open with a recorded reason, that is usually the whole answer.

When in doubt between express and producer, choose producer. One extra agent is
cheaper than a slice with no place in the roadmap.

---

## Step 1b — Health reviews are audits, and this project has a pattern for them

An open-ended "review the project and tell me what's wrong" is not a feature
request and not recon. It is an **audit**, and the project profile will usually
name a house pattern for how audits are recorded. Follow it rather than
inventing an artifact.

Two things this gets wrong when improvised:

**Findings need a home the rest of the project already reads.** A standalone
findings file with its own numbering is invisible to every later story, and to
the producer next time it checks whether something is already known. If the
project records findings inside an epic PRD, that is where they go.

**Findings must be dispatched, not improvised.** Split the review by lane and
send each to the specialist that owns it — contract drift to `tech-lead`,
anything touching a formula or a trust label to `quant-analyst`, code layout and
prior art to `scout`. A generic subagent with a hand-written prompt has none of
the capability packs, so it re-derives what the packs already know and gets no
benefit from the guardrails.

Then dispatch `producer` with the collected findings, so placement, sequencing
and the "already known / deliberately open" check happen where they belong.

**Verification is separate from review.** "Is the project in a working state" is
answered by running the project's canonical test entrypoint, not by an audit. Do
that first, report it plainly, and keep it out of the findings.

---

## Step 2 — Quant research, when the substance is mathematical

If the approved work introduces or changes a metric, formula, weighting, return
basis or trust classification, dispatch `quant-analyst` in `mode: RESEARCH`
**before** story authoring — i.e. before Step 3, not after it.

The research brief is what makes acceptance criteria groundable. Written the
other way round, the story states an outcome nobody has established is
computable, and the contradiction surfaces during implementation — when three
lanes have already built toward it.

Its artifact path goes into the story author's `inputs`.

**This is the one lane you may run in parallel with `scout`.** They read
different things and neither consumes the other's output. Everything downstream
of them is serial for contract reasons, so this is the only free concurrency in
the flow — take it.

---

## Step 3 — Story authoring, then the human's gate

If the approved brief proposes new stories, dispatch `story-author` with the
producer's brief path and, where one exists, the quant research brief path as
`inputs`.

**Then stop and hand the draft to the user.** This is the one hard stop in the
flow. Acceptance criteria are the contract everything downstream is measured
against; a slice built from criteria nobody reviewed cannot be verified, only
described. The agent drafts — the human approves.

Do not dispatch further until the user has approved the story and it is
ticketed. In particular, **every open decision the producer escalated must be
resolved by the user first.** The story author reproduces them as open; if you
proceed while one is unresolved, you have made the decision by omission.

Epic placement is always the user's call, never the network's. Nothing writes to
the roadmap or the story index at this stage — those record what shipped, and
the docs lane reconciles them at close-out.

---

## Step 4 — Tech lead: design pass

With an approved, ticketed story in hand, run `scout` if the area is unfamiliar,
then dispatch `tech-lead` in `mode: DESIGN`. Inputs: the story, the PRD section,
the scout map's path, and any methodology doc the profile flags as mandatory.

Its technical plan is what you turn into work orders. Reference it by path and
section on every lane it touches:

- **the contract** → an `inputs` line pointing at the plan's contract section on
  *every* lane that touches the boundary. This is the highest-value relay you
  perform; both engineering lanes reading the same file is what prevents the
  mismatch that otherwise surfaces only at integration.
- **reuse** → `inputs` naming the modules each lane must build on.
- **lanes and order** → the plan's sequence.
- **decisions** → `inputs` on every affected lane, so no engineer re-decides
  something already settled.

If the tech lead returns `REFUSED`, the story cannot be built as written. Take
it back to the user — do not soften the order and retry.

---

## Step 5 — Present the plan and wait

Show the lane list, one line of intent each, and the agent count. Wait for a go.

Dispatching six subagents is expensive, and the plan is the cheapest place to
catch a misread request. A user correcting the plan costs one sentence;
correcting six agents' output costs the session.

---

## Step 6 — Dispatch, one order at a time

Send each work order verbatim. Default order: contracts before consumers,
implementation before tests, everything before docs.

After each report:

1. **Read the status honestly.** `PARTIAL` and `BLOCKED` are information. Do not
   proceed as though a lane succeeded because the next lane is ready to start.
   `status: DONE` with `verification.result: NOT_RUN` on an order that named a
   command is not a pass — send it back.
2. **Update `run.md`** — the Artifacts row, and anything new under **Open**.
   Do this *before* dispatching the next order, not at the end. A ledger updated
   at the end is a ledger that does not survive the thing it exists for.
3. **Route `contract_notes` forward** as explicit `inputs` on downstream orders,
   and list them under **Open** until a downstream order absorbs one. An
   unabsorbed contract note is shipped inconsistency. If no downstream order
   exists to absorb one, create it.
4. **Append `pack_corrections`** to `<run_dir>/pack-corrections.md` as they
   arrive. They are the docs lane's close-out order.
5. **Route `handoff` forward** — fixture names, prop shapes, route paths.
6. **Re-plan when reality disagrees.** Show the user the change; don't improvise
   silently.
7. **Stop on `REFUSED`.** An agent refusing on a guardrail is the system
   working. Surface it; never re-dispatch with softer wording.

---

## Step 7 — Quant audit, before the engineering gate

If any lane touched analytics, a formula, a weighting, a return basis or a trust
label, dispatch `quant-analyst` in `mode: AUDIT` **first** — before the tech
lead's integration review.

The ordering is deliberate. A wrong formula can be engineered flawlessly and
satisfy every acceptance criterion; the other two gates would both pass it. If
the mathematics is wrong, the rest of the review is measuring the wrong thing.

Read its `verification.detail` for **which anchor it checked against**. An audit
that recomputed from the same methodology doc the implementation was built from
is a consistency check, not an independent one — it catches slips, not wrong
premises. If that is all you got, say so to the user rather than reporting the
mathematics as verified.

On findings: `CRITICAL` and `MATERIAL` go back to the owning lane as change
requests. A `CRITICAL` finding that the methodology doc itself is wrong is not a
lane's to fix — take it to the user.

---

## Step 8 — Tech lead: integration review

When the engineering lanes have reported, dispatch `tech-lead` in
`mode: INTEGRATION` with every lane's artifact path and the diff.

On `verdict: CHANGES_REQUESTED`: for each `BLOCKING` request, dispatch a fresh
work order to the owning lane whose `inputs` names the CR file path and whose
scope is fenced to exactly that finding. Then re-run the integration review.

**Increment the round counter in `run.md` before dispatching, not after.** Two
rounds on the same finding is the limit; a third means the request is unclear or
the design was wrong — escalate to the user instead of looping. That limit is
only real if it is written down, because the session that loops is the session
that already lost track.

Carry `SHOULD_FIX` items to **Open**; they do not hold the slice.

---

## Step 9 — Reviewer: acceptance gate

Only after the tech lead passes. The reviewer checks something different:
whether this satisfies the story. On `verdict: FAIL`, re-dispatch to the owning
lane with the failure artifact's path — never fix it yourself, never re-run the
gate without an intervening fix.

---

## Step 10 — Close out

Dispatch the `docs` lane twice, or once with both inputs:

- the contract notes, against the repo's docs;
- `<run_dir>/pack-corrections.md`, against
  `<agenticRoot>/projects/<project>/capabilities/`. This is the **only** order
  in which a lane writes inside `<agenticRoot>` outside the run dir, and it is
  what stops the packs decaying into a description of the repo as it was.

Then set `run.md` `status: CLOSED` and report to the user:

- what changed, by lane
- every gate verdict that ran, and **which gates did not run and why**
- anything still open: `PARTIAL` lanes, `SHOULD_FIX` items, unabsorbed contract
  notes, unapplied pack corrections
- any producer finding raised during the work — scope that turned out wrong is
  roadmap information, and it is lost if you do not surface it
- the exact command they should run before committing

**You never commit.** The repo's mechanical gates own that boundary.

**And you never offer to do a lane's work yourself.** When a brief resolves into
"write two debt-register entries" or "reconcile four docs", those are `docs`
lane orders — dispatch them. Offering to do it directly is how the isolation
erodes: it always looks cheaper in the moment, and the work lands without a
pack, without a scope fence, and without a report anything downstream can read.

The same applies to reaching for a repo skill the profile marks as superseded.
If the routing table names an agent for a job, that agent does the job.

---

## Degrading gracefully

Some agents may be stubs. If a plan needs a stub lane, say so and offer the two
honest options: run that lane in the main session without isolation, or pause
and build the agent first. Never present a stub's output as a specialist's.

## What your own context is for

You hold the plan, the ledger's current state, and the routing decisions. You do
not hold the artifacts — they are on disk, and re-reading one costs less than
carrying nine of them badly. If you notice yourself summarising a report to save
room, that is the signal to write the ledger and read from it, not to compress.
