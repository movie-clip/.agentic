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
<agenticRoot>/projects/<project>/runs/<YYYY-MM-DD>-<slug>/
  run.md                        the ledger
  decisions.md                  what the human ruled at each stop, in their words
  01-recon.md                   lane reports, numbered in dispatch order
  02-product.md
  03-design.md
  04-backend.md
  05-frontend.md
  cr/CR-1.md                    change requests, one file each
  pack-corrections.md           appended as they arrive
```

You create `run.md` at `intake` and update it after every head you receive.

```markdown
# RUN <run-id>
request:      <the user's original words, verbatim>
agentic_root: <the RESOLVED ABSOLUTE path>
project:      <the profile this run is bound to — `projects/<project>/project.md`>
story:        <path, or NONE>
status:       PLANNING | DISPATCHING | GATING | BLOCKED | CLOSED
phase:        intake | ground-truth | framing | specification | design | build | verify | close
plan:         v<n>
budget:       <n> — <the derivation, from the Phases table>
spent:        <n>
blocked_on:   <one line, only when status is BLOCKED; otherwise omit>
next:         <the single next action, always current — see below>
gates:        <every gate the project declares under `verify` — each a verdict,
              or skipped and why; plus protocol-lint when the run wrote a
              pack-corrections.md>

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the area is unfamiliar | satisfied — 01 |
| framing | product | the request changes what the product does | not triggered (defect in shipped behaviour) |
| build | backend | anything that edits the repo | satisfied — 03 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | product | — | producer | sonnet | 01-delivery-brief.md | DONE | — |
| 02 | quant | AUDIT | quant-analyst | opus | 02-quant-audit.md | DONE | PASS |
| 03 | backend | — | backend-engineer | opus↑ | 03-backend.md | DONE | — |

`model` is the model the dispatch **actually ran on** — the agent file's default,
or the override if you escalated. Record an effort override the same way
(`sonnet/max↑`); an unoverridden dispatch needs only the model, since the agent
file pins its effort. Mark an escalation with `↑`. Writing the default from
memory rather than from the agent file is how this column becomes fiction; read
it if you are unsure.

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

## Replans
| plan | because | change |
|---|---|---|
| v2 | 04-backend found the sector field already nullable upstream | design re-triggered; budget 5 → 7 |

```

### The row is written when the head returns, not when you are done with it

A head coming back is the ledger event. **Before you read the artifact, before
you summarise anything to the human, write the Artifacts row** — number, lane,
mode, agent, `model`, artifact, `status`, `verdict` — and rewrite `next:` in the
same edit. Two fields, one action, no gap between them.

The order matters because the two natural stopping points both come *after* the
head and both feel like completion. You read the brief and you now know what to
do next, so you go do it; or you tell the human what came back and the turn
ends. Either way the dispatch happened, the artifact is on disk, and the ledger
does not know.

That failure is quiet in a way the others are not. The artifact is fine; the
work is fine; only the record is wrong, so nothing complains until a resume
re-dispatches a lane that already ran, or close-out reads a table missing rows.
**Updating the ledger before a dispatch does not discharge this** — a
pre-dispatch edit records intent, and intent is exactly what a stale ledger
already has too much of.

### A dispatch that returned nothing still owes a row

`spent` increments when you dispatch. The Artifacts row is written when the head
comes back. Between those two is the case the table has no natural entry for: a
subagent that errored, a session interrupted mid-dispatch, a head that never
arrived. The budget was spent and the ledger has nothing to show for it.

Write the row anyway:

```
| 05 | frontend | — | frontend-engineer | sonnet | 05-frontend.md | LOST | — |
```

`LOST` is a ledger status, not a report status — no report exists to carry one.
Then **re-dispatch as the next slot number**, never as `05` again. The retry is
a second dispatch and costs a second unit of budget, which is the true account
of what the run spent; and reusing the number overwrites the only evidence that
the first attempt happened.

`check_report.py <run_dir>/ --require-heads` compares `spent` against the number
of Artifacts rows, so a dispatch left out of the table now fails close-out
rather than quietly making the budget look better than it was.

### `gates:` accounts for every gate, including the ones you skipped

```
gates:        quant-audit PASS · integration PASS · review skipped (no story to
              accept — human approved)
```

Name **every** gate the project declares under `verify` (§ 2), every run. A gate
that ran carries its verdict, and the verdict must match its Artifacts row. A
gate that did not run carries `skipped` and the reason. Each has its own trigger
and none is implied by the shape of the run, so a missing row is not by itself
wrong — **a missing row nobody *decided* on is.**

`check_report.py` reads **which** gates are owed from the profile's `## Phases`
verify rows, so the set below is this project's, not the script's. A project
declaring different gates is measured against its own. The triggers are the
profile's too; what follows is portfolio's, as an illustration of the shape.

| Gate | Accountable on a run that |
|---|---|
| `integration` | dispatched a build lane |
| `quant-audit` | changed mathematical substance — a formula, a derived number, a trust classification |
| `review` | carries a story whose criteria someone must accept |
| `protocol-lint` | left a non-empty `pack-corrections.md` |

`protocol-lint` judges the network's own files, so on an ordinary run against
the bound repo it has nothing to say and does not appear at all — a line reading
`skipped (not an authoring order)` every time is a line nobody reads. The
close-out corrections dispatch is the one exception, because `packs.md` § 3
makes it the only order in which a lane writes inside `<agenticRoot>` outside
the run dir: an authoring order arriving inside a delivery run. So the trigger
is the file, not the shape of the run — corrections on disk, therefore the
gate is accountable, by verdict or by `skipped` and why.

**Which means `pack-corrections.md` exists only when a correction applies.** Do
not open one to record that there was nothing to correct: a lane's own
`pack_corrections: - none` is already that record, in the artifact whose head
the count came from. A file written to say "nothing here" makes the gate
accountable for nothing, and the reason written beside `skipped` is then a claim
about the file's contents that no one re-reads — `2026-09-12` closed with
`protocol-lint skipped (pack-corrections.md is empty)` against a file of eleven
lines. The gate was right to skip. The ledger's reason for skipping it was
false, and that is the part a later reader would have believed.

Record this in the ledger and not only in your close-out report. The report is
prose said once to a human and gone by the next run; the ledger line is read
back by `check_report.py <run_dir>/ --require-heads`, which matches it against
the Artifacts rows and against `pack-corrections.md` and fails close-out on a
gate that quietly did not run.

### `next:` is what makes a run resumable

`status: DISPATCHING` says a run is mid-flight. It does not say *what to
dispatch*, so a session that ends at dispatch twelve leaves its successor
reconstructing intent from twelve artifact rows.

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

Marking a row resolved and leaving it in place is the tempting alternative, and
it costs you the table: `Open` is re-read on every ledger update, so rows that
are done but still present are paid for again at every dispatch. Nothing is lost
by moving them — `Closed` keeps the trail, and the artifact `ref` points at
holds the detail.

**A row can also leave by being dismissed.** Not everything that lands in
`Open` needs a dispatch: a note about the run's own transient artifacts, a
finding a later lane showed to be wrong, an item the user waves off. Move it to
`## Closed` with `absorbed by` reading `dismissed — <reason>`. `CARRIED` means
the human is owed something after the run ends; a row nobody is owed anything
for is finished, and leaving it in `Open` to satisfy the close-out checklist
puts noise in the one table close-out is supposed to make readable.

**One fact, one row.** The same finding reaches you twice — from the lane that
hit it, and from a later pass that notices it again. Before adding a row, check
whether `ref` already appears; if it does, update that row rather than appending
a second account of the same fact.

### Why `Open` and `Rounds` are tables

Because prose bullets grow and typed rows do not. Everything in this network
that holds its size holds it by having a schema: the report block has one and
lane reports stay between 25 and 81 lines. Structure, not discipline, is what
keeps an artifact small.

So: **one row per item, five columns, `one-line` under 120 characters.** If an
item needs more than that, the detail is already in the artifact `ref` points
at — the row is a pointer, not a record. `state` is `OPEN` or `CARRIED`
(surfaced to the human at close-out); an absorbed row is not a state, it is a
row that has moved to `## Closed`.

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

## 2. Phases, not a route

A run is a set of **phases**. Each answers one question, is filled by a lane the
project names, and fires only when its trigger is true of *this* request.

| Phase | The question it answers | Fires when |
|---|---|---|
| `intake` | what was asked, and against which project | always |
| `ground-truth` | what is actually true in the repo right now | the run would otherwise build on an unchecked claim about the repo — a bug report, a findings document, an unfamiliar area |
| `framing` | should this happen at all, and where does it belong | the request changes what the product does |
| `specification` | what would make it done, in checkable terms | framing produced scope no approved statement of done covers |
| `design` | what contract does it commit to | the change crosses a contract boundary, or more than one build lane touches it |
| `build` | the change itself | anything that edits the repo |
| `verify` | is it right, by each gate's own criterion | per gate — the project declares each gate's trigger |
| `close` | reconcile, sweep the ledger, hand back | always |

**The phases are protocol; the lanes that fill them are not.** This file does not
know what your project calls its lanes, whether it has a mathematics gate, or
whether its unit of approved scope is a story, a ticket or an issue. Read
`projects/<project>/project.md` § Phases at intake: it binds each phase to a
lane, in order, with the clause that decides whether that lane fires.

### A phase that does not fire is recorded, not skipped

Copy the project's table into the ledger's `## Phases` and put a verdict beside
every row — `satisfied — <nn>`, or `not triggered (<the clause that was false>)`.

That record is what a route name could not give you. `route: express` says a
short run happened. `framing — not triggered (defect in shipped behaviour, no
new user-visible scope)` says *which* question went unasked and on what grounds,
so a later reader can tell a decision from an omission — and so can you, three
dispatches later, when a lane returns something that makes the clause false.

It also removes the need for a route menu. A run where only `build` and its own
`verify` fire **is** the short route: nothing has to be named, claimed or
defended, and nothing has to void itself, because the clause that was false is
written down and is re-read every turn.

### The order is a dependency, not a schedule

A phase may not run before the phases it reads from are satisfied or ruled out —
`design` reads `specification`'s output, `verify` judges `build`'s. That is the
whole of the ordering rule. Within it, a phase runs when its inputs exist, not
when its number comes up, and a run that revisits `design` because a build lane
contradicted it is re-planning rather than going backwards.

---

## 3. The control loop

You are not executing a plan. You are running a loop whose state is the ledger —
and the ledger, not your memory of what you intended, is what each turn reads.

Every turn:

1. **Read `run.md`.** `## Phases`, `## Artifacts`, `## Open`, `spent`.
2. **Take the earliest phase whose trigger is true and whose state is not
   `satisfied`.** Earliest by the dependency order in § 2, not by which one you
   find most interesting.
3. **If there is none, the phase is `close`.**
4. **If that phase carries a human stop the human has not given, stop and ask.**
   Do not dispatch past an unanswered decision; proceeding is deciding.
5. **Write the ledger before you spend** — `phase:`, `next:`, and the dispatch
   you are about to make.
6. **Dispatch exactly one order.**
7. **Record the head and absorb its output** — § 1 for the row, § 4 for what to
   open.
8. **Test the result against the plan**, and re-plan if it disagrees (below).

Then read `run.md` again. The re-read is not ceremony: it is what makes a
compacted, resumed or restarted session identical to a continuing one. Anything
you carry between turns that is not in the ledger will not survive the run, so
put it there or accept losing it.

### Serial by default, and the exception is narrow

One order at a time, and you read its head before you write the next one. The
relay — naming an upstream artifact as a downstream lane's `inputs` — is the
highest-value thing you do, and it is only possible when the upstream head
landed before the downstream order was written. Two orders in flight against a
ledger that describes neither is how a contract note goes unrouted.

Two dispatches may overlap only when **all three** hold:

- neither reads a file the other writes;
- neither's `inputs` names an artifact the other produces;
- both are read-only, **or** the contract they both depend on is already settled
  and on disk.

In practice that is the read-only lanes early in a run. Everything downstream of
a contract is serial for the reason the contract exists. If you are arguing with
one of the three clauses, the answer is serial: the wall-clock saved is worth
less than one mismatch found at the integration gate.

### The budget is derived, and it is what ends an open-ended run

At intake, once `## Phases` is filled in, the budget falls out of it:

```
budget:       7 — 5 triggered phases (build is 3 lanes) + 2 gates
spent:        0
```

**Derive it, do not pad it.** A budget with slack in it is one a run can only
come in under, which makes the number unfalsifiable in exactly the direction
that matters — `2026-09-12` budgeted `4 + 1 slack` and spent 4, and the ledger
cannot say whether the model was calibrated or the padding absorbed the miss.
One dispatch over an honest estimate costs a `## Replans` row, and that row is
the measurement. Buying it off in advance is paying to learn nothing.

Increment `spent` on every dispatch. **At `spent == budget` you do not dispatch
again until you have written a `## Replans` row** saying what the estimate missed
and what the new budget is. At twice the original budget, stop and hand back to
the human regardless of how close the work feels.

A route name was chosen before the run knew anything, from a menu of guesses
about shape. A budget is derived from which triggers actually fired, which is
evidence, and it is falsifiable at close-out: `spent` against `budget` measures
the estimate, and it is the only number in the ledger that says whether the
phase model is calibrated for this project yet.

### Re-plan on evidence, and version it

Four things a plan cannot absorb silently. Any one of them is a re-plan:

- a head returns `BLOCKED` for a reason that is not a missing input;
- a lane's result **contradicts** something the plan or an earlier artifact
  asserted — contradicts, not merely adds to;
- a phase recorded as `not triggered` turns out to be triggered;
- `spent` reaches `budget`.

Re-planning is three actions in one edit: bump `plan:` to the next version,
append a `## Replans` row (`plan | because | change`), and say what changed to
the user before the next dispatch. An unversioned re-plan is indistinguishable
from drift — the ledger shows a run that did something other than what it said,
with nothing recording the moment anyone chose that.

### A resumed session is the same session, or the ledger failed

Compaction is not an exception the loop handles; it is the case the loop was
designed around. A session that restarts mid-run reads five fields and two
tables and is where it left off:

`status` says whether the run is mid-flight. `blocked_on` says what would
restart it. `next` says the one action to take. `spent` says what has been paid.
`## Phases` says what is left, and `## Artifacts` says what already ran.

Two consequences worth writing down because both are silent when broken. A
`pending` row for a lane that already ran means a resume dispatches it twice —
which is why the row is written when the head returns, not at the end. And
`next:` on a `CLOSED` run must read `none — CLOSED`; a closed ledger still
naming a dispatch is an instruction to a session that has no other way to know
the run is over. Both are checked at close-out.

### The loop ends when every phase is accounted for

Not when the work feels finished. `close` is reachable when every `## Phases` row
reads `satisfied` or `not triggered (<clause>)`, every gate in `gates:` carries a
verdict or a reason, and every remaining `Open` row is deliberately `CARRIED`.
Those three are the termination condition; the skill's close-out checklist is how
you discharge it.

---

## 4. Reading discipline: heads, briefs, and named sections

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

**Planning artifacts are read by their brief.** `product`, `design`, `story` and
`quant` RESEARCH produce artifacts far longer than the report block — a plan and
its stories run to hundreds of lines, and perhaps thirty of them are routing
decisions you act on. Every such artifact opens with a `## Orchestrator brief`
of at most 15 lines. Read the brief. Read the sections the brief names, if you
need them. Do not read the document.

**This is safe because the brief is checked for completeness, not just length.**
`check_report.py` fails an artifact whose brief does not name every section
below it. Reading every line is what would otherwise guarantee you saw every
story; the check is what guarantees it instead, so routing from a brief the
validator has not passed gives you neither guarantee.

The sections you skip are not lost — they reach the lane that needs them as an
`inputs` path with a `§ section` suffix, which is the entire point of the relay
rule: you can name a section of a plan you have not read yourself, and the
engineer who needs it reads the specialist's own words rather than your summary.

### Validate every artifact, derive every head

**Every artifact gets checked before you route from it. Every dispatch, every
lane, whether or not that lane has `Bash`.** Where the head comes from is the
only thing that varies:

- **A lane returned a head** — transcribe it verbatim into `<run_dir>/<nn>-head.txt`
  and validate it against the artifact with `--head`. Transcribing is not
  deriving: the file is a copy of
  a claim until the script has measured it against the document.
- **A lane returned no head, or the check rejects the one it did** — derive it:

  ```bash
  python <agenticRoot>/scripts/check_report.py <run_dir>/<nn>-<lane>.md --emit-head > <run_dir>/<nn>-head.txt
  ```

  Then paste the lane's `headline` over the placeholder the script leaves in
  angle brackets — it is the one line the script cannot produce and the lane
  can. Everything else comes from the artifact.

**The head is a file, not a paragraph in your ledger.** A run whose `<nn>-head.txt`
is missing has an Artifacts row backed by nothing: the row says `DONE` and the
evidence for it was never written down. Close-out cannot audit what is not on
disk, and `close`'s `--require-heads` sweep will fail on it.

**The check is not scoped to the shell-less lanes.** It is tempting to read it
that way — a lane with `Bash` was told to validate its own artifact, so its head
looks already-earned — but "the lane was supposed to" is not a measurement. A
lane that skipped its own check returns a head indistinguishable from one that
passed, and a head you transcribed into a file is still that lane's claim about
its own work. One command per dispatch is the entire cost of not having to trust
it. Writing `<nn>-head.txt` and moving on without running the validator is the
same omission as not writing the file at all — you have recorded the claim and
skipped the measurement.

Checking a head by eye is the alternative, and it does not work: it asks a model
to count list items and slice a string to an exact length. A mismatch costs a
full artifact read — the read the head exists to avoid — where deriving one
costs a single Bash call. That arithmetic does not change for a lane that has a
shell, which is why this applies to all of them.

**If a head is missing, malformed, or its counts disagree with the artifact**,
that lane is not closed. From a shell-less lane, derive it as above and carry
on — a mismatch there is expected and is not a finding. From a lane that has
`Bash`, it is: that lane was told to derive its head and typed one instead, so
re-dispatch it, or read the artifact in full and say in the ledger that you did.
Do not infer the head in either case.

**A `detail` mismatch is never cosmetic.** `verification.detail` is the evidence
behind a `PASS`, and the head must carry it verbatim. When the two disagree, the
validator names the character they diverge at — read that, then decide. The
reading to distrust is "a dash or encoding quirk, cosmetic": both sides open
identically in that case *and* in the case where a lane abridged its own
evidence line, which is precisely what putting `detail` in the head exists to
catch. The diverging character tells you which one you have. Nothing else does.

---

## 5. The relay rule: paths, not prose

You carry the producer's brief, the tech lead's plan and every change request
between lanes, because subagents cannot spawn subagents. If you carry them as
summarised text, the specialist works from your paraphrase rather than the
specialist judgment that produced it — and under context pressure, summarising
is exactly what happens.

So: **an `inputs` line names a path, never a quotation.**

```
inputs:
  - projects/portfolio/runs/2026-08-20-sector-drawdown/03-technical-plan.md   § contract
  - projects/portfolio/runs/2026-08-20-sector-drawdown/cr/CR-2.md
```

Not `inputs: - "the tech lead said the field should be nullable"`. The receiving
agent reads the file. Verbatim becomes a property of the filesystem instead of a
hope about the model.

A `§ section` suffix is encouraged — it tells the receiver which part of a long
document its order actually depends on, and it is the mechanism that lets you
name a section of a plan you have not read yourself.

The one exception: `goal` and `non_goals` are your own words, and should be.

### The human's ruling is a path too

Every judgment in a run reaches the lane that needs it as a file — except the
most consequential one. A human stop produces a decision in the chat, and the
chat is not a path, so it reaches the next lane the one way the relay rule
forbids: as your restatement of it.

`2026-09-11` is what that costs. The story lane's own `risks` block: *"this
story assumes the work order's framing of the human's ruling is accurate — I did
not see a separate signed ruling document, only the work order's own restatement
of the producer's brief's two open items as resolved."* The lane was right to
flag it, had no way to check it, and drafted against a paraphrase anyway.

So **write the ruling down before the next dispatch**, in
`<run_dir>/decisions.md`:

```markdown
# Decisions — <run-id>

## D-1 · framing · 2026-09-11
open decision:  epic placement — new Risk-tab epic, or Backlog sibling?
raised by:      02-delivery-brief.md § Open decisions (a)
ruling:         "no epic, keep it a one-off toggle"
by:             the human, in session
```

One entry per decision the human actually resolved, the ruling in **their
words**, and the artifact and section that raised it. Then every downstream
order names `decisions.md § D-1` in `inputs`, the same as any other input.

This costs a paragraph per stop and closes the last place where a lane works
from your summary of someone else's judgment. It is also the only record that
survives the session: a run resumed after a compaction has the ledger, the
artifacts and — without this — no idea what the human said.

---

## 6. Writing a work order

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
- **Every factual claim in the order is sourced.** An order asserts things about
  the repo — this file has that shape, this spec covers that path, this module
  already does X. Each one is either something you read this turn, or something
  a path in `inputs` says, or it does not go in the order. Write what you do not
  know as a question for the lane, not as a premise for it.

**If you need a claim and have neither, that is the `ground-truth` trigger.**
The phase exists for this and nothing else. `2026-09-12` skipped it on the
strength of an intake grep and then told the frontend lane that a spec file
"still asserts the old DOM shape" — the file did not exist. The lane repeated
the claim in its handoff, the test lane spent its `risks` block establishing
that no such file had ever been in git history, and the run carried an `Open`
row about its own work order to close-out. Nothing shipped wrong; three lanes
paid for one sentence. An unverified claim reads exactly like a verified one,
which is why it has to be sourced where it is written rather than caught where
it hurts.

---

## 7. Never do a lane's work yourself

Doing it always looks cheaper in the moment, and the result is frequently good,
which is what makes it dangerous. A run that answers its own request in the main
session has no scope fence, no capability pack, no gate, no artifact and no
ledger entry — and it teaches, by succeeding, that the network is ceremony.

`dispatched: 0` is a disclosure, not a result. Say it out loud at close-out.
