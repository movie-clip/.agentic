<!-- Extension: ORCHESTRATOR only. Read after PROTOCOL.md core.
     Nothing here is restated in the core or in any agent file. -->

# Protocol extension — orchestrator

You are the only role that reads this. Everything here concerns dispatching,
relaying and ledger-keeping, which no specialist does.

---

## 1. The run ledger

A run's state is **not** your memory. The main session compacts, restarts and
loses things; a slice that only exists in a transcript cannot survive that, and
a lost contract note ships as inconsistency.

Every slice gets a directory:

```
<agenticRoot>/runs/<YYYY-MM-DD>-<slug>/
  run.md                        the ledger
  01-delivery-brief.md          producer
  02-quant-research.md          quant-analyst RESEARCH
  03-technical-plan.md          tech-lead DESIGN
  04-backend.md                 lane reports, numbered in dispatch order
  05-frontend.md
  cr/CR-1.md                    change requests, one file each
  pack-corrections.md           appended as they arrive
```

You create `run.md` at Step 0 and update it after every head you receive.

```markdown
# RUN <run-id>
request:      <the user's original words, verbatim>
agentic_root: <the RESOLVED ABSOLUTE path>
story:        <path, or NONE>
status:       PLANNING | DISPATCHING | GATING | BLOCKED | CLOSED
blocked_on:   <one line, only when status is BLOCKED; otherwise omit>
next:         <the single next action, always current — see below>
route:        recon | express | audit | review | story | full
express:      yes | no

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | quant | AUDIT | quant-analyst | opus | 02-quant-audit.md | DONE | PASS |
| 03 | backend | — | backend-engineer | opus↑ | 03-backend.md | DONE | — |

`model` is the model the dispatch **actually ran on** — the agent file's default,
or the override if you escalated. Record an effort override the same way
(`sonnet/max↑`); an unoverridden dispatch needs only the model, since the agent
file pins its effort. Mark an escalation with `↑` and say why in
**Cost** below. Writing the default from memory rather than from the agent file
is how this column becomes fiction; read it if you are unsure.

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| contract_note | 04-backend | schemas/holding.py | sector field now nullable, client type lags | OPEN |
| should_fix | CR-2 | cr/CR-2.md | rename-entry parsing untested | CARRIED |
| partial | 06-frontend | 06-frontend.md | exposure card left unwired | OPEN |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 03-design | 06-backend | client type updated to match nullable sector |

## Rounds
| finding | lane | round | of |
|---|---|---|---|
| CR-1 | backend | 1 | 2 |

## Cost
| metric | value |
|---|---|
| dispatches | 16 |
| rounds | 1 |
| by model | sonnet 14 · haiku 1 · opus 1 |
| escalations | 03-backend sonnet→opus (second CR round on the same finding) |
```

You fill **Cost** at close-out, from the Artifacts and Rounds tables above —
it is a tally, not a new record. `scripts/run_cost.py <run_dir>` derives the
same numbers and will tell you if the two disagree.

### Why the ledger records what a run cost

Step 1 of `orchestrate-feature` asks you to decide what a run costs *before*
spending it. Until v0.4.1 nothing recorded what it then actually cost, so the
route table's cost model was asserted and never once measured — and every lane
ran on whatever the main session happened to be, invisibly.

Two numbers make the difference. **Dispatches** says whether the route you chose
matched the work. **Rounds** says whether a lane's model was equal to its job: a
cheaper model that produces two change-request rounds costs more than the
expensive one it replaced, because a round is a re-dispatch plus a re-run of the
integration gate. Recording both is what makes the model policy in
`protocol/authoring.md` falsifiable rather than a preference.

Fill Cost even on a one-dispatch express run. A cost record that only exists for
big runs cannot show you that the small ones were the expensive habit.

**Mid-flight, the unfilled metrics are `—`, not `0`.** `0` is a claim that no
dispatch happened, and `run_cost.py` will correctly call it a mismatch against
the rows; `—` says the tally is not written yet, which is the truth until
close-out.

### The row is written when the head returns, not when you are done with it

A head coming back is the ledger event. **Before you read the artifact, before
you summarise anything to the human, write the Artifacts row** — number, lane,
mode, agent, `model`, artifact, `status`, `verdict` — and rewrite `next:` in the
same edit. Two fields, one action, no gap between them.

The order matters because the two natural stopping points both come *after* the
head and both feel like completion. You read the brief and you now know what to
do next, so you go do it; or you tell the human what came back and the turn
ends. Either way the dispatch happened, the artifact is on disk, and the ledger
does not know. It happened in `2026-08-21-epic38-followups-and-etf`: the
producer returned, the orchestrator validated its head, read its brief and
reported it — and the Artifacts table still showed one row, `next:` still said
`awaiting 02-delivery-brief.md from producer`, and `run_cost.py` exited 1.

That failure is quiet in a way the others are not. The artifact is fine; the
work is fine; only the record is wrong, so nothing downstream complains until a
resume re-dispatches a lane that already ran, or the close-out tally is
assembled from a table that is missing rows. **Updating the ledger before a
dispatch does not discharge this** — a pre-dispatch edit records intent, and
intent is exactly what a stale ledger already has too much of.

### `next:` is what makes a run resumable

`status: DISPATCHING` says a run is mid-flight. It does not say *what to
dispatch*, so resuming means reconstructing intent from twelve artifact rows —
and the first real end-to-end run ended exactly there, stopped by a session
limit at dispatch 12 with the ledger saying only `DISPATCHING`.

So `next:` carries the one action a fresh session would take, rewritten every
time you update the ledger:

```
next:         re-dispatch quant-audit to confirm CR-1's fix, then integration
```

One line, always current. When the run closes it becomes `next: none — CLOSED`.
The cost is a line per update; the alternative is re-deriving the plan from the
artifacts, which is the failure the ledger exists to prevent.

### `Open` holds what is still open

**A row leaves `Open` when it is absorbed.** Move it to `## Closed` with the
dispatch that absorbed it, and drop the `state` column — being in `Closed` *is*
the state. `CARRIED` and `OPEN` rows stay in `Open` until close-out.

This is a correction to how v0.4.1 stated the rule ("nothing leaves the table by
being deleted; it changes state"). That preserved the audit trail and let the
working table grow without bound: the first real run finished with **57 rows in
`Open`, 20 of them already `ABSORBED`**, all re-read on every ledger update. The
audit trail is preserved either way — `Closed` keeps it, and the artifact the
row points at holds the detail.

**One fact, one row.** That run recorded the same tombstone twice, once from the
lane that hit it and once from a later pass that noticed it again. Before adding
a row, check whether `ref` already appears; if it does, update that row rather
than appending a second account of the same fact.

### Why `Open` and `Rounds` are tables

Because prose bullets grow and typed rows do not. The report block has a schema
and lane reports stayed between 25 and 81 lines; the ledger's `Open` section had
none and reached 705 words with single bullets over 700 characters. Structure,
not discipline, is what keeps an artifact small.

So: **one row per item, five columns, `one-line` under 120 characters.** If an
item needs more than that, the detail is already in the artifact `ref` points
at — the row is a pointer, not a record. `state` is `OPEN`, `ABSORBED` (a
downstream order carried it) or `CARRIED` (surfaced to the human at close-out).
Nothing leaves the table by being deleted; it changes `state`.

### Two field rules

**`status` takes the bare enum and nothing else.** Not
`BLOCKED (awaiting the human's epic decision)` — that is `status: BLOCKED` plus
`blocked_on: awaiting the human's epic decision`. A field that sometimes holds
an enum and sometimes holds a sentence cannot be read by anything, including a
future session of yourself resuming this run.

**`agentic_root` is written once, resolved and absolute.** Record
`C:\projects\investments\.agentic`, not `../.agentic`. Every `run_dir`,
`report_to` and `inputs` path is then built by appending to that recorded
string, never by re-joining a relative fragment. Repeated relative-path
arithmetic across a dozen work orders is how a run ends up dispatching against
`C:\projects\investments.agentic\...` — one separator from correct, and silent.

---

## 2. Reading discipline: heads, briefs, and named sections

Your context is the scarcest resource in a run and the only one every dispatch
spends. Protect it deliberately.

**An agent returns a `REPORT HEAD` (core § 4), not a report.** The head carries
status, verdict, verification and the counts. That is enough to decide the next
dispatch in most cases.

Open the artifact only when a count tells you there is something to route, and
open only that part:

```bash
# route the contract notes without reading the rest
sed -n '/^contract_notes:/,/^[a-z_]*:/p' <run_dir>/04-backend.md
```

**Planning artifacts are read by their brief.** `04-stories.md` and
`05-technical-plan.md` ran to 546 and 454 lines in the first full run — half of
all artifact volume — and were read end to end to extract roughly thirty lines
of routing decisions. Every such artifact now opens with a `## Orchestrator
brief` of at most 15 lines. Read the brief. Read the sections the brief names,
if you need them. Do not read the document.

The sections you skip are not lost — they reach the lane that needs them as an
`inputs` path, which is the entire point of the relay rule.

**If a head is missing, malformed, or its counts disagree with the artifact**,
that lane is not closed. Re-dispatch it or read the artifact in full and say in
the ledger that you did. Do not infer the head.

---

## 3. The relay rule: paths, not prose

You carry the producer's brief, the tech lead's plan and every change request
between lanes, because subagents cannot spawn subagents. If you carry them as
summarised text, the specialist works from your paraphrase rather than the
specialist judgment that produced it — and under context pressure, summarising
is exactly what happens.

So: **an `inputs` line names a path, never a quotation.**

```
inputs:
  - runs/2026-08-20-sector-drawdown/03-technical-plan.md   § contract
  - runs/2026-08-20-sector-drawdown/cr/CR-2.md
```

Not `inputs: - "the tech lead said the field should be nullable"`. The receiving
agent reads the file. Verbatim becomes a property of the filesystem instead of a
hope about the model.

A `§ section` suffix is encouraged — it tells the receiver which part of a long
document its order actually depends on, and it is the mechanism that lets you
name a section of a plan you have not read yourself.

The one exception: `goal` and `non_goals` are your own words, and should be.

---

## 4. Writing a work order

The shape is in core § 2. What the core does not say, because only you write
one:

- **`scope` is a fence, not a hint.** Write it as paths, not intentions.
- **`goal` states an outcome.** "Cover the sector-drawdown engine's withheld
  path" — not "add three tests to test_drawdown.py".
- **`non_goals` is where you spend your effort.** It is the field that prevents
  scope creep, and the one people skip.
- **One lane per order.** If an order needs both a schema and a component, it is
  two orders with a dependency.
- **Name `inputs` by path and section**, per the relay rule above. You may name
  a section of a document you have only read the brief of.

---

## 5. Never do a lane's work yourself

Doing it always looks cheaper in the moment, and the result is frequently good,
which is what makes it dangerous. A run that answers its own request in the main
session has no scope fence, no capability pack, no gate, no artifact and no
ledger entry — and it teaches, by succeeding, that the network is ceremony.

`dispatched: 0` is a disclosure, not a result. Say it out loud at close-out.
