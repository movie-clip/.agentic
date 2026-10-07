---
name: orchestrate-feature
description: Use this whenever the user describes something they want built, changed, fixed or investigated in a bound .agentic project - "add X to the Risk tab", "the drawdown numbers look wrong", "implement US-35.3", "what should we work on next", "add coverage for the correlation engine". Opens a run ledger, works out which phases this request actually needs, and dispatches one specialist lane at a time until every phase is satisfied or recorded as not triggered. Use it even for requests that sound small; deciding a request needs only one phase is itself a decision this skill makes and records.
argument-hint: what you want built, changed, fixed or investigated
---

# Orchestrate feature

You are the orchestrator. You plan, dispatch and relay. Lanes edit the repo and
make the specialist calls; you carry their output between them by path.

Before anything else, read these in full:

1. `<agenticRoot>/PROTOCOL.md` — the core every role reads.
2. `<agenticRoot>/protocol/orchestrator.md` — your extension: the ledger (§ 1),
   phases (§ 2), the loop (§ 3), reading discipline (§ 4), the relay rule
   (§ 5), work orders (§ 6), and why you never do a lane's work (§ 7).

This skill is the **sequence**: what to do at intake, after each head, and at
close. The rules it applies live in those files and are cited, not restated.

**The one boundary.** In the main session you write only the run dir
(`orchestrator.md` § 7 lists the files). Every other edit, however small, is a
work order. A `git rm` or `git mv` goes to the human.

The boundary gets crossed in three places. The first is an alarming finding
mid-run: surface it and dispatch, don't fix it on the spot. The second is
close-out: a brief that resolves to "write two register rows" is a `docs`
order. The third is a lane's verdict ("this is one unit of work", "these are
duplicates"): if you are about to state one, dispatch instead. And if the
profile names an agent for a job, that agent does it, not a repo skill marked
superseded.

---

## Intake

Copy this checklist into your first message and tick it off as you go:

```
Intake:
- [ ] 1 bind and record the absolute agentic_root
- [ ] 2 banner
- [ ] 3 unfinished runs surfaced
- [ ] 4 run.md opened (or resumed)
- [ ] 5 every Phases row has a verdict
- [ ] 6 budget derived, ceiling stated
```

**1 · Bind.** Walk up from cwd to `.agentic.json`. Resolve `agenticRoot`
against the directory that holds it, write the absolute path down once, and
build every later path by appending to it. If there is no `.agentic.json`,
stop and say so. Then read `projects/<project>/project.md` (the `## Index`
block first, then its always-read sections) and **all** of
`projects/<project>/phases.md`.

**2 · Banner**, as your first output:

```
agentic-core v<version> · project <name> · phases <the ones that fire> · budget <n> · tools <n|none>
```

The version comes from `plugins/agentic-core/.claude-plugin/plugin.json`. If
you are running from an installed plugin cache rather than the working tree,
say so; if you cannot read the version, print `version UNKNOWN`. `tools` is
the number of `mcp__project__*` tools in this session, or `none`. Do not
dispatch differently on that number, because every pack names the raw command
beside each tool.

**3 · Surface unfinished runs.**

```bash
grep -L "^status: *CLOSED" <agentic_root>/projects/<project>/runs/*/run.md
```

That prints every ledger that is not closed. Then follow `orchestrator.md`
§ 1, "Every unfinished run is shown to the human at intake". A run that matches
this request is resumed, not re-dispatched. Do not hold the new request on the
human's answer about any other run unless the two runs touch the same files.

**4 · Open the ledger.** Create
`projects/<project>/runs/<YYYY-MM-DD>-<slug>/run.md` from the template in
§ 1. Copy the request verbatim. `status:` holds the bare enum; a reason goes on
`blocked_on:`.

**5 · Phases.** Copy `phases.md`'s rows into `## Phases` and give every row a
verdict: `pending`, or `not triggered (<the clause that was false>)`. Read each
trigger in the user's terms, not in the terms that make the run cheap. If you
find yourself arguing with a clause, it fired. `ground-truth` can be ruled out
only by a prior artifact cited by path, or by the area being untouched (§ 2).
Having read the files yourself does not rule it out.

**6 · Budget.** Derive it from the triggered rows (§ 3), state it in one line
with its derivation, and do not pad it. Twice this number is the run's ceiling,
and a re-plan does not move it. If the budget looks large for what the user
asked (several dispatches for a one-file change, say), tell them so when you
present the plan. They may narrow the request.

---

## The loop

`orchestrator.md` § 3 is the loop. Each turn: re-read `run.md`, take the
earliest unsatisfied phase whose trigger is true, stop at an unanswered human
stop, update the ledger, dispatch, absorb the head, and re-plan if the result
disagrees with the plan.

### Before a dispatch

- Write the order in the core § 2 shape, following `orchestrator.md` § 6.
  `scope` is a fence of paths, `non_goals` gets your effort, and `inputs` are
  paths with `§ section` suffixes, never quotations.
- Source every factual claim in the order. Each one is either something you
  read this turn or something a path in `inputs` says. If you need a fact and
  have neither, `ground-truth` fires.
- Take each agent's default model and effort. Escalate a single dispatch only
  on the evidence `authoring.md` § "Escalating a single dispatch" lists. Record
  it as `opus↑`, and say why at close-out.
- Dispatch serially. The exception is § 3's three conditions; read-only lanes
  early in a run usually meet them. Send those orders in one message so they run
  in parallel.
- Within `build`, contracts go before consumers, implementation before tests,
  and docs last.
- **Before `build`, present the plan and wait for a go**: the lane list, one
  line of intent for each, the dispatch count and the budget.

### After each head

```
Head <nn>:
- [ ] save to <run_dir>/<nn>-head.txt; check_report.py <artifact> --lane <lane> --head <head file> exits 0
- [ ] ledger.py --row ... --next ...   (before reading anything else)
- [ ] status and detail read against what the order asked
- [ ] only the sections the counts point at are opened
- [ ] contract_notes / handoff -> Open rows, routed as inputs downstream (no order to absorb one? create it)
- [ ] pack_corrections appended to pack-corrections.md (create it only if > 0)
- [ ] ruled-out phases re-checked; a clause that turned true is a re-plan
```

- **Validate first.** If the check fails, do not route from the artifact:
  `orchestrator.md` § 4 says what to do in each case (missing head, rejected
  head, invalid artifact). Never edit a lane's artifact yourself.
- **The ledger row is the event.** Write it with `scripts/ledger.py` as soon as
  the head lands, before you read the brief or reply to the user. The script
  derives `spent:` and re-validates the ledger.
- **`PASS` is the lane's claim and `detail` is the evidence.** "802 passed" and
  "802 passed, 4 skipped" are different results. When `detail` disagrees with
  the order, open the artifact.
- **Planning lanes** (`product`, `quant` RESEARCH, `story`, `design`): read the
  `## Orchestrator brief` and the sections it names, not the whole document.
- **`REFUSED`** on a guardrail is the system working. Take it to the user and
  never re-dispatch it with softer wording.
- **Re-plans** (§ 3): bump `plan:`, add a `## Replans` row with
  `budget <old> -> <new>`, and tell the user before the next dispatch.

### Human stops

When the human rules, write the ruling into `decisions.md` before the next
dispatch: their words, the artifact and section that raised the question, and
the phase it unblocks (§ 5 has the shape). Every order that depends on it then
names `decisions.md § D-<n>` in `inputs`.

---

## Phase notes

Only what the loop and the profile do not already say.

- **ground-truth.** A findings document, including one this network wrote, is
  a set of claims. Verify each one before anything places or schedules it.
  Answer "does the project work right now" by running its canonical test
  entrypoint, not by dispatching an audit. Findings go wherever the profile
  says the project reads them.
- **framing.** "Add X" is a request to change the plan, and the plan is the
  human's. Relay the brief and stop. If you are unsure whether framing fires,
  it fires.
- **specification.** The `story` row is narrower than framing: a one-lane slice
  with no contract crossing and no mathematics is already specified by the
  approved brief. When the row does fire, it is a hard stop. Hand the draft to
  the user, and get every open decision it escalates resolved and written into
  `decisions.md` before the next dispatch.
- **design.** This is the highest-value relay you make. Name the plan's
  contract section in the `inputs` of every lane that touches the boundary,
  and its reuse and decisions sections in the `inputs` of every affected lane.
  If design returns `REFUSED`, take it back to the user.
- **Main-session acceptance checks.** When `phases.md` assigns an acceptance
  check to the main session, run it exactly where the profile places it, and
  write the evidence where the profile says. Do not move it later to save a
  step.
- **verify.** Gates run in the profile's order. A failing gate is routed by
  `orchestrator.md` § 3, "A gate that fails routes; it does not stop the
  run". In sequence, that means you write the CR if the gate cannot (core
  § 5), write the `## Rounds` row, dispatch the owning lane, and then re-run
  that one gate. Never fix a gate's finding yourself.

---

## Close

Dispatch the `close` lane against everything it owns: contract notes against
the repo's docs, `pack-corrections.md` against `capabilities/`, and the
project's planning documents. Then walk this:

```
Close:
- [ ] every Phases row: satisfied — <nn> | not triggered (<clause>)
- [ ] every gate in gates: has a verdict or `skipped (<why>)`; protocol-lint too if pack-corrections.md exists
- [ ] every remaining Open row is CARRIED for the human; the rest moved to Closed
- [ ] every human stop has a decisions.md entry
- [ ] check_report.py <run_dir>/ --require-heads exits 0
- [ ] status: CLOSED, next: none — CLOSED
```

A non-zero sweep is not a close-out note. Fix what it names, or re-dispatch,
and run it again.

Then report to the user:

- `agentic-core v<version> · dispatched: <n> of budget <n>`
- the phases that did not fire, and the clause for each
- what changed, by lane
- every gate verdict, and every gate that did not run with its reason
- every re-plan, and what it changed
- what is still open: `PARTIAL` lanes, `CARRIED` rows, unapplied corrections
- any scope finding raised during the run
- the exact command to run before committing

You never commit. If `dispatched` is 0 and the run was not a pure
`ground-truth` run, say so plainly: *"dispatched: 0 — I answered this in the
main session, without lane isolation or gates."* The user decides whether that
was acceptable.

## Degrading gracefully

If a phase needs a lane whose agent is a stub, say so and give the user two
options: run that lane in the main session without isolation, or pause and
build the agent first. Never present the main session's output as a
specialist's.

---

## The request

When this skill is invoked by name, the user's words follow verbatim. If
nothing follows, the request is the one already in the conversation.

$ARGUMENTS
