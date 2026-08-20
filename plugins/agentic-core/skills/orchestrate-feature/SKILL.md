---
name: orchestrate-feature
description: Use this whenever the user describes something they want built, changed, fixed or investigated in a bound .agentic project - "add X to the Risk tab", "the drawdown numbers look wrong", "implement US-35.3", "what should we work on next", "add coverage for the correlation engine". Routes the request through the producer for roadmap placement, the tech lead for technical design, then focused specialist subagents, then both gates. Use it even for requests that sound small; deciding a request is single-lane is itself a routing decision this skill makes.
---

# Orchestrate feature

You are the orchestrator. You **plan, dispatch, and relay**. You do not edit
source files, and you do not make the calls that belong to the producer or the
tech lead — you carry their output between lanes.

That relaying is not a formality. Subagents cannot spawn subagents, so the
producer's brief, the tech lead's design, and every change request reach their
destination only because you carry them. If you summarise instead of relaying
verbatim, the specialist works from your paraphrase rather than from the
specialist judgment that produced it.

Load `agentic-protocol` before anything else — it defines the three message
shapes you will be emitting and reading.

## Step 0 — Bind

Read `.agentic.json` at the repo root, then
`<agenticRoot>/projects/<project>/project.md`. That profile names the lanes,
which agents are live, and the guardrails no plan may violate. Missing
`.agentic.json` → stop and say so.

## Step 1 — Producer first

**Almost everything goes to the producer before anything else.** A request that
arrives as "add X" is a request for a *change to the plan*, and the plan is not
yours to change. The producer reads the roadmap, checks whether the thing
already exists, decides whether it fits an active epic or needs a new one, and
returns a delivery brief.

Skip the producer only for:

- **Pure recon** — "where does X live", "how does Y work". Dispatch `scout`,
  return findings, stop.
- **Explicit story pickup** — "implement US-35.3". The placement decision was
  made when the story was written. Go to Step 3.
- **Test-only work on shipped code** — "add coverage for the correlation
  engine". No product surface changes.
- **"Is this number right?"** — dispatch `quant-analyst` in `mode: AUDIT`
  directly. A suspected arithmetic error is not a roadmap question until the
  analyst has established there is one.

When in doubt, go through the producer. The cost is one agent; the cost of
skipping is a slice of work with no place in the roadmap.

**Relay the brief to the user and stop.** The verdict is theirs. If the producer
says the thing already exists, or was deliberately left open with a recorded
reason, that is usually the whole answer and nothing further should be
dispatched.

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
anything touching a formula or a trust label to `quant-analyst`, code layout
and prior art to `scout`. A generic subagent with a hand-written prompt has
none of the capability packs, so it re-derives what the packs already know and
gets no benefit from the guardrails.

Then dispatch `producer` with the collected findings, so placement, sequencing
and the "already known / deliberately open" check happen where they belong.

**Verification is separate from review.** "Is the project in a working state" is
answered by running the project's canonical test entrypoint, not by an audit.
Do that first, report it plainly, and keep it out of the findings.

## Step 2 — Quant research, when the substance is mathematical

If the approved work introduces or changes a metric, formula, weighting, return
basis or trust classification, dispatch `quant-analyst` in `mode: RESEARCH`
**before** story authoring — i.e. before Step 3, not after it.

The research brief is what makes acceptance criteria groundable. Written the
other way round, the story states an outcome nobody has established is
computable, and the contradiction surfaces during implementation — when three
lanes have already built toward it.

The brief's metrics inventory feeds directly into the tech lead's contract, so
relay it whole.

## Step 3 — Story authoring, then the human's gate

If the approved brief proposes new stories, dispatch `story-author` with the
producer's delivery brief and, where one exists, the quant research brief —
**verbatim, not summarised**. A story drafted without them repeats the analysis
badly or skips it, which is the whole reason those lanes ran.

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

## Step 4 — Tech lead: design pass

With an approved, ticketed story in hand, run `scout` if the area is unfamiliar,
then dispatch `tech-lead` in `mode: DESIGN`. Inputs: the story, the PRD section,
the scout map, and any methodology doc the profile flags as mandatory.

Its technical plan is what you turn into work orders. Take from it directly:

- **the contract** → becomes an explicit `inputs` line on *every* lane that
  touches the boundary, quoted in full. This is the highest-value relay you
  perform; both engineering lanes seeing the same field list is what prevents
  the mismatch that otherwise surfaces only at integration.
- **reuse** → `inputs` naming the modules each lane must build on.
- **lanes and order** → the plan's sequence.
- **decisions** → `inputs` on every affected lane, so no engineer re-decides
  something already settled.

If the tech lead returns `REFUSED`, the story cannot be built as written. Take
it back to the user — do not soften the order and retry.

## Step 5 — Present the plan and wait

Show the lane list, one line of intent each, and the agent count. Wait for a go.

Dispatching six subagents is expensive, and the plan is the cheapest place to
catch a misread request. A user correcting the plan costs one sentence;
correcting six agents' output costs the session.

## Step 6 — Dispatch, one order at a time

Send each work order verbatim. Default order: contracts before consumers,
implementation before tests, everything before docs.

After each report:

1. **Read the status honestly.** `PARTIAL` and `BLOCKED` are information. Do not
   proceed as though a lane succeeded because the next lane is ready to start.
2. **Route `contract_notes` forward** as explicit `inputs` on downstream orders.
   An unabsorbed contract note is shipped inconsistency. If no downstream order
   exists to absorb one, create it.
3. **Route `handoff` forward** — fixture names, prop shapes, route paths.
4. **Re-plan when reality disagrees.** Show the user the change; don't improvise
   silently.
5. **Stop on `REFUSED`.** An agent refusing on a guardrail is the system
   working. Surface it; never re-dispatch with softer wording.

## Step 7 — Quant audit, before the engineering gate

If any lane touched `analytics/`, a formula, a weighting, a return basis or a
trust label, dispatch `quant-analyst` in `mode: AUDIT` **first** — before the
tech lead's integration review.

The ordering is deliberate. A wrong formula can be engineered flawlessly and
satisfy every acceptance criterion; the other two gates would both pass it. If
the mathematics is wrong, the rest of the review is measuring the wrong thing.

On findings: `CRITICAL` and `MATERIAL` go back to the owning lane as change
requests. A `CRITICAL` finding that the methodology doc itself is wrong is not a
lane's to fix — take it to the user.

## Step 8 — Tech lead: integration review

When the engineering lanes have reported, dispatch `tech-lead` in
`mode: INTEGRATION` with every lane's report and the diff.

On `CHANGES_REQUESTED`: for each `BLOCKING` request, dispatch a fresh work order
to the owning lane with the request text **verbatim** as its input and a scope
fenced to exactly that finding. Then re-run the integration review.

Two rounds on the same finding is the limit. A third means the request is
unclear or the design was wrong — escalate to the user instead of looping.

Carry `SHOULD_FIX` items forward to close-out; they do not hold the slice.

## Step 9 — Reviewer: acceptance gate

Only after the tech lead passes. The reviewer checks something different:
whether this satisfies the story. On `FAIL`, re-dispatch to the owning lane with
the failure text — never fix it yourself, never re-run the gate without an
intervening fix.

## Step 10 — Hand back

Report to the user:

- what changed, by lane
- all three gate verdicts (quant / engineering / acceptance)
- anything still open: `PARTIAL` lanes, `SHOULD_FIX` items, unabsorbed risks
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

## Degrading gracefully

Some agents are stubs. If a plan needs a stub lane, say so and offer the two
honest options: run that lane in the main session without isolation, or pause
and build the agent first. Never present a stub's output as a specialist's.
