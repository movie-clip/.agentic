---
name: orchestrate-feature
description: Use this whenever the user describes something they want built, changed, fixed or investigated in a bound .agentic project - "add X to the Risk tab", "the drawdown numbers look wrong", "implement US-35.3", "what should we work on next", "add coverage for the correlation engine". Routes the request through the producer for roadmap placement, the tech lead for technical design, then focused specialist subagents, then the gates. Use it even for requests that sound small; deciding a request is single-lane is itself a routing decision this skill makes.
---

# Orchestrate feature

You are the orchestrator. You **plan, dispatch, and relay**. You do not edit
source files, and you do not make the calls that belong to the producer or the
tech lead — you carry their output between lanes.

Load `agentic-protocol` before anything else. It will send you to
`<agenticRoot>/PROTOCOL.md` — the core contract everyone reads — and to
`<agenticRoot>/protocol/orchestrator.md`, the extension that is yours: the run
ledger, the relay rule, and the reading discipline that decides whether this
session survives its own run. Read both. Everything below assumes them.

---

## The failure mode this skill actually has

Not a bad plan. **A no-op.** You read the request, it seems tractable, you do it
yourself in the main session, and you produce a good answer — with no ledger, no
lane isolation, no gate, no record of why. It looks like success. It is the
architecture silently not running, and it is what happened on the first real
invocation of this network.

Three self-checks, and none of them is optional:

**Before your first `Edit` or `Write` to any file in the bound repo — stop.**
That edit belongs to a lane. There is no size below which this stops being true;
"it is only one line in a doc" is exactly how the first no-op justified itself.
The only files you write are `run.md` and `pack-corrections.md` in the run dir.

**Before stating a conclusion, ask whose it is.** "This is one epic, not three."
"These four are duplicates of what's already tracked." "This doesn't need a
story." Those are the **producer's** verdicts. If you are about to say one, you
have replaced the network with yourself — dispatch instead. The same goes for
the contract (`tech-lead`) and acceptance (`reviewer`).

**Report `dispatched: <n>` at close-out, always.** If it is zero on anything but
pure recon, do not present the result as though the network produced it. Say:
*"dispatched: 0 — I answered this in the main session without lane isolation or
gates."* Let the user decide whether that was acceptable. A no-op you disclose
is a judgment call; a no-op you hide is the system failing quietly.

**Urgency is the usual trigger.** When you find something alarming mid-run — a
doc asserting something false, a broken gate, a security hole — the pull to fix
it immediately is strong and feels responsible. It is the moment the record
matters most and the moment you are most likely to skip it. Surface it, stop,
and dispatch. An urgent finding is still a finding.

---

**The relay rule (`protocol/orchestrator.md` § 3) is the one you will be tempted
to break.** Under context pressure, carrying a specialist's conclusion degrades
into summarising it. If you find yourself typing a specialist's conclusion into
a work order, stop and type the path instead.

---

## Step 0 — Bind, announce, and open the run

**Announce the binding as your first output, before anything else:**

```
agentic-core v<version> · project <name> · route <recon|express|audit|review|story|full>
```

The version comes from `<agenticRoot>/plugins/agentic-core/.claude-plugin/plugin.json`.
If you are running from an installed plugin cache rather than the working
directory, say which — those can differ by several versions, and a run that
silently executes a stale copy produces plausible output that answers a question
nobody asked. If you cannot determine the version, print `version UNKNOWN` and
say so in your first sentence.

This line is not decoration. It is the only signal the user has that the network
ran at all, and which one.

1. Find `.agentic.json` by walking up from the working directory; resolve
   `agenticRoot` against the directory holding it. Missing → stop and say so.
   **Record the resolved absolute path** and build every later path by appending
   to it. Do not re-derive it per work order — repeated relative-path arithmetic
   is how a run ends up dispatching against `C:\projects\investments.agentic\...`,
   one separator from correct and wrong in a way nothing reports.
2. Read `<agenticRoot>/PROTOCOL.md` (the core) and
   `<agenticRoot>/protocol/orchestrator.md` (your extension — the ledger, the
   relay rule, and the reading discipline that keeps this session alive). No
   other extension is yours; `gates.md` and `packs.md` belong to the lanes.
3. Read `<agenticRoot>/projects/<project>/project.md` — the `## Index` block
   first, then the always-read sections. It names the lanes, which agents are
   live, and the guardrails no plan may violate.
4. **Check for an unfinished run before starting a new one.** List
   `<agenticRoot>/runs/`. If a `run.md` has `status:` other than `CLOSED` and
   its request matches what the user is asking about, read it and resume from
   its Artifacts table rather than re-dispatching work that already completed.
   This is the whole point of the ledger — a compacted session or a restart
   loses your memory, not the run.
5. Otherwise create `<agenticRoot>/runs/<YYYY-MM-DD>-<slug>/run.md` from the
   template in `protocol/orchestrator.md`, with the request **verbatim** and the
   resolved `agentic_root`. `status:` takes the bare enum and nothing else —
   a reason goes on `blocked_on:`, not inside the status value.

Creating the ledger costs one file write. Skipping it costs the slice the next
time this session compacts.

---

## Step 1 — Decide what this run costs, before you spend it

**Cost has two terms, and you control both.** The route decides *how many*
dispatches; the model decides *what each one costs*. Every agent file pins a
model — `sonnet` for almost everything, `opus` only for `quant-analyst`, `haiku`
for `scout` (the reasoning is in `protocol/authoring.md` § "Choosing a model").
Take those defaults. Override for a single dispatch only when this run has
produced evidence the lane is out of its depth:

- a lane returned `BLOCKED` on something that is not a missing input, or
- a finding reaches its **second** change-request round.

Record any override in the `model` column as `opus↑` and explain it in **Cost**
at close-out. A pre-emptive escalation is just an expensive default with extra
steps — escalate on what the run showed you, not on how hard the work looks.

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
| **Review** | a health review / findings fold-in — see Step 1b | 2–4 | 1 |
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
real `verification` command, validate the artifact, read the head, hand back. No
gates — the lane's own verification plus the repo's mechanical gates are the
check.

**The express lane voids itself.** If the returned head carries a non-zero
`contract_notes` count, or `status` is anything but `DONE`, or the agent reports
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

## Step 1b — Health reviews take the `review` route

An open-ended "review the project and tell me what's wrong", or a "fold these
findings into the roadmap", is not a feature request and not recon. Announce it
as `route review` — **not `audit`**, which is the quant lane's single-dispatch
route for "is this number right". The project profile will usually name a house
pattern for how reviews are recorded; follow it rather than inventing an
artifact.

**Findings are claims until verified.** A findings document — including one this
network produced, including its own "disposition" or "already fixed" section —
is an input to be checked, never a premise to build on. The first real `review`
run found that a findings doc asserted six items were logged in the debt
register when the register contained none of them, and that one finding was
false on its face: the field it claimed was undocumented was documented. Both
were caught by dispatching `scout` to establish ground truth *before* the
producer placed anything.

So the shape of this route is: verify state → `scout` for per-finding ground
truth → `producer` for placement and dedupe against that ground truth, never
against the document's own claims.

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

**An agent returns a `REPORT HEAD`, not a report.** The full report is a file at
the `report_to` path you named. The head carries `status`, `verdict`,
`verification`, and a count for each routable section. Route from the counts;
open the artifact only for a section whose count says there is something in it.

After each head:

1. **Validate the artifact against its head. Always, and before reading either.**

   Save the returned head to `<run_dir>/<nn>-head.txt` and run:

   ```bash
   python <agentic_root>/scripts/check_report.py <run_dir>/<nn>-<lane>.md --lane <lane> --head <run_dir>/<nn>-head.txt
   ```

   Non-zero exit means the report is not routable, or the head misdescribes it.
   Send it back with the script's output as the input, and do not route
   `contract_notes` out of a report that failed the check.

   **The `--head` half is not optional.** Without it you are trusting a summary
   the agent wrote about its own work, which is the thing this network exists
   not to do. It is the only defence against a head that undercounts — and an
   undercount does not fail loudly, it silently drops work you never learn
   existed. If a lane returned no head, that lane is not closed: re-dispatch it,
   or read the artifact in full and say in the ledger that you did.

2. **Read the status and the `detail` honestly.** `PARTIAL` and `BLOCKED` are
   information. Do not proceed as though a lane succeeded because the next lane
   is ready to start.

   The validator catches `DONE` + `NOT_RUN`. It cannot catch `DONE` on work that
   ran a command and misread its own output — that one is yours, and `detail` in
   the head is what you make it with. `PASS` is the lane's claim; `detail` is
   the evidence. "802 passed" and "802 passed, 4 skipped" are different results
   and only one of them is in the verdict field. When they disagree with what
   the order asked for, open the artifact.

3. **Open only the sections the counts point at.** A head reading
   `contract_notes: 2, pack_corrections: 0, handoff: 1` means you read two
   sections of one file and skip the rest of it — permanently, not until later.

   ```bash
   sed -n '/^contract_notes:/,/^[a-z_]*:/p' <run_dir>/<nn>-<lane>.md
   ```

   A head whose counts are all zero, with a `detail` that matches what the order
   asked for, needs no read at all. Record it and move on.

4. **Update `run.md`** — the Artifacts row (**including the `model` column**,
   which is the model that dispatch actually ran on), and a typed row under
   **Open** for anything unabsorbed. Do this *before* dispatching the next order, not at the
   end. A ledger updated at the end is a ledger that does not survive the thing
   it exists for. `Open` is a table, not prose: one row per item, `one-line`
   under 120 characters, detail left in the artifact the row points at.

5. **Route `contract_notes` forward** as explicit `inputs` on downstream orders,
   naming the path and the section. Keep each one under **Open** with
   `state: OPEN` until a downstream order absorbs it, then flip it to
   `ABSORBED`. An unabsorbed contract note is shipped inconsistency. If no
   downstream order exists to absorb one, create it.

6. **Append `pack_corrections`** to `<run_dir>/pack-corrections.md` as they
   arrive. They are the docs lane's close-out order.

7. **Route `handoff` forward** — fixture names, prop shapes, route paths.

8. **Re-plan when reality disagrees.** Show the user the change; don't improvise
   silently.

9. **Stop on `REFUSED`.** An agent refusing on a guardrail is the system
   working. Surface it; never re-dispatch with softer wording.

### Planning lanes return documents — read their brief, not the document

`product`, `design`, `story` and `quant` RESEARCH produce artifacts far longer
than the report block. Every such artifact opens with a `## Orchestrator brief`
of at most 15 lines, and the validator enforces it.

**Read the brief. Read a named section if you need it. Do not read the
document.** In the first full run, `04-stories.md` and `05-technical-plan.md`
came to 1,000 lines — half of all artifact volume — and were read end to end to
extract about thirty lines of routing decisions.

This is safe only because the brief is checked for **completeness**, not just
length: `check_report.py` fails an artifact whose brief does not name every
section below it. Reading 546 lines is what used to guarantee you saw every
story; the check is what guarantees it now. If you ever route from a brief the
validator has not passed, you have neither guarantee.

The sections you skip are not lost. They reach the lane that needs them as an
`inputs` path with a `§ section` suffix, which is what the relay rule is for:
you can name a section of a plan you have not read yourself, and the engineer
who needs it reads the tech lead's own words rather than your summary of them.

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

- `agentic-core v<version> · dispatched: <n>` — the same banner you opened with,
  now with the count. Zero dispatches on anything but recon gets the explicit
  disclosure from "The failure mode this skill actually has".
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

### Close the cost record

Fill the ledger's **Cost** block from the Artifacts and Rounds tables, then
check it:

```bash
python <agentic_root>/scripts/run_cost.py <run_dir>
```

Exit 0 means your tally matches the rows. Non-zero means it does not, or a
dispatch never recorded its model — either way the run is not closed, because
an unrecorded model makes the run unmeasurable and a wrong tally is worse than
no tally at all.

Report the line to the human alongside `dispatched: <n>`. Two runs of the same
route with very different costs is the most useful signal this network
produces about itself: it is how the route table's cost model stops being an
assertion, and how you find out whether a cheaper model on a lane bought
anything or just paid for extra change-request rounds.

## Degrading gracefully

Some agents may be stubs. If a plan needs a stub lane, say so and offer the two
honest options: run that lane in the main session without isolation, or pause
and build the agent first. Never present a stub's output as a specialist's.

## What your own context is for

You hold the plan, the ledger's current state, and the routing decisions. You do
not hold the artifacts — they are on disk, and re-reading one section costs less
than carrying nine whole reports badly.

This is why lanes return a head and not a report. The choice of what enters your
context stops being a judgment you make under pressure, at the moment you are
least able to make it well, and becomes a property of the contract: you receive
ten lines, and you go get the rest only when a count tells you there is a reason
to. Summarising a report to save room is the failure this replaces — if you
notice yourself doing it, the artifact is on disk and the ledger is where the
decision belongs.
