# `.agentic` — agent network architecture

Lives at `C:\projects\investments\.agentic`, one level above the repos it
drives. Six projects are bound: `portfolio`, `budget`, `impact`,
`tradingview`, `datoro` and `los-tres`. `plugins/agentic-core/.claude-plugin/plugin.json`
is the authority on the version. Examples below use `portfolio`.

**This file is the current design and the reasoning behind it.** How each rule
was discovered is in `git log`. Installation and the
directory tree are in [`README.md`](./README.md). What is wrong or missing is
in [`TECH-DEBT.md`](./TECH-DEBT.md); what comes next is in
[`ROADMAP.md`](./ROADMAP.md).

---

## 1. The problem this solves

Before the network, `portfolio/.claude/skills/` ran a linear pipeline in one
context:

```
quant-research → write-story → build-story → write-tests → verify-story → update-docs
```

It worked. But `build-story` carried the whole project in its head — backend
conventions, the UI design system, pytest fixtures, FMP caching, doc contracts —
for a change that might touch three files, and it self-invoked `write-tests`,
`verify-story` and `update-docs`, so roughly 1,200 lines of skill text sat in
one transcript before a repo file was read. Two consequences:

- **Context dilution.** The test conventions competed for attention with the
  Recharts shim and the trust-ladder rules, even on a backend-only ticket.
- **No isolation.** A wrong turn in the UI slice polluted the reasoning of the
  backend slice, because they shared one transcript.

The fix is not more skills. It is **separating who decides from who does.**
Each specialist runs in its own context, with its own tools and its own
capability pack. The orchestrator sees only their reports.

**The repo skills were not replaced.** All eight still live in
`portfolio/.claude/skills/` and the specialists reach for them as reference —
except `build-story`, which is superseded and must not run: a slice built
through it has no ledger, no gate verdicts, no contract notes, and ends with an
agent commit. `portfolio/agentic/project.md` § "Repo skills agents may invoke"
says which lane reaches for which.

## 2. The model: phases, not a route

A run is a set of **phases**. Each answers one question, is filled by a lane the
project names, and fires only when its trigger is true of *this* request.

| Phase | The question it answers | Fires when |
|---|---|---|
| `intake` | what was asked, and against which project | always |
| `ground-truth` | what is actually true in the repo right now | the run would otherwise build on an unchecked claim about the repo |
| `framing` | should this happen at all, and where does it belong | the request changes what the product does |
| `specification` | what would make it done, in checkable terms | framing produced scope no approved statement of done covers |
| `design` | what contract does it commit to | the change crosses a contract boundary, or more than one build lane touches it |
| `build` | the change itself | anything that edits the repo |
| `verify` | is it right, by each gate's own criterion | per gate — the project declares each gate's trigger |
| `close` | reconcile, sweep the ledger, hand back | always |

**The phases are protocol; the lanes that fill them are not.** `PROTOCOL.md`
knows nothing about what a project calls its lanes, whether it has a mathematics
gate, or whether its unit of approved scope is a story or an issue. The binding
lives in the project's `agentic/phases.md`: which lane fills each phase, in what
order, and the clause that decides whether it fires. The orchestrator reads it
at intake; no specialist lane needs it, which is why it is a file beside
`project.md` rather than a section inside it.

**A phase that does not fire is recorded, not skipped.** Every row gets a
verdict in the ledger — `satisfied — <nn>`, or `not triggered (<the clause that
was false>)`. That record is what a route name could not give: `route: express`
says a short run happened; `framing — not triggered (defect in shipped
behaviour, no new user-visible scope)` says *which* question went unasked and on
what grounds. A later reader can tell a decision from an omission — and so can
the orchestrator three dispatches later, when a lane returns something that
makes the clause false.

**So there is no route menu, and a short run needs no name.** A run where only
`build` and its `verify` gates fire *is* the short run. Nothing has to be
claimed or defended, and nothing has to void itself, because the false clause is
on disk and is re-read every turn.

**The order is a dependency, not a schedule.** A phase may not run before the
phases it reads from are satisfied or ruled out — `design` reads
`specification`'s output, `verify` judges `build`'s. Within that, a phase runs
when its inputs exist. A run that revisits `design` because a build lane
contradicted it is re-planning, not going backwards.

### The run is the ledger

State lives in `runs/<id>/run.md`, not in the orchestrator's context. Every
turn:

1. **Read `run.md`** — `## Phases`, `## Artifacts`, `## Open`, `spent`.
2. **Take the earliest phase** whose trigger is true and whose state is not
   `satisfied`. Earliest by dependency order, not by interest.
3. **If that phase carries a human stop the human has not given, stop and ask.**
   Proceeding is deciding. Only an order that asks (a fact check, or a
   question back to the lane that wrote the artifact) may go out at the stop,
   so the human is asked about decisions rather than facts (`grill-plan`).
4. **Write the ledger before you spend** — `phase:`, `next:`, and the dispatch
   about to be made.
5. **Dispatch exactly one order.**
6. **Record the head and absorb its output.**
7. **Test the result against the plan**, and re-plan if it disagrees.

Then read `run.md` again. The re-read is not ceremony: it is what makes a
compacted, resumed or restarted session identical to a continuing one. Anything
carried between turns that is not in the ledger will not survive the run.

**The budget is derived, and it is what ends an open-ended run.** Once
`## Phases` is filled in at intake, the budget falls out of it — triggered
phases plus gates — and is not padded. At `spent == budget` the orchestrator
writes a `## Replans` row saying what the estimate missed before dispatching
again; at twice the **original** budget it stops and hands back to the human,
and the ruling that lets it go on is written to `decisions.md` — a ceiling read
off the re-planned budget rises with every re-plan and can never be reached. A
route name was chosen before the run knew anything. A budget is derived from
which triggers actually fired, so `spent` against `budget` at close-out measures
whether the model is calibrated for this project.

**Two phases stop for the human** in `portfolio`: `framing`, where the delivery
brief's verdict is the human's, and the `story` row of `specification`, which is
the one hard stop. Each stop ends by writing the ruling to
`<run_dir>/decisions.md` in the human's own words; downstream orders name
`decisions.md § D-<n>` in `inputs`. The human's judgment is a path like every
other judgment in a run — it was the one exception the relay rule never named,
and a lane drafting against the orchestrator's paraphrase of it is the failure
that closed.

## 3. Four layers, deliberately separated

| Layer | Lives in | Contains | Changes when |
|---|---|---|---|
| **Protocol** | `PROTOCOL.md` + `protocol/*.md` | message shapes, binding, gate rules | rarely |
| **Role** | `plugins/agentic-core/agents/<name>.md` | what a lane judges, tool discipline | never for project reasons |
| **Capability** | `<repo>/agentic/capabilities/<lane>.md`, `project.md`, `phases.md` — in the project's own repo | paths, frameworks, fixtures, commands, gotchas, phase bindings | every time the repo evolves |
| **Skill** | `plugins/agentic-core/skills/<name>/SKILL.md` | **sequence** — how a run is opened, what happens between a head returning and the next dispatch, how one is closed | rarely |

`protocol/authoring.md` is the authority on this split and on what each layer
must *not* contain. Two rules do most of the work:

**One rule, one home.** The protocol partition is disjoint — no rule appears in
two of `PROTOCOL.md`, `orchestrator.md`, `gates.md`, `packs.md` and
`authoring.md`. Placement is decided by who needs it: every lane → core; only
the dispatcher → `orchestrator.md`; only a gate → `gates.md`; only the docs lane
at close-out → `packs.md`; only someone writing network files → `authoring.md`.
A rule that seems to belong in two places is usually two rules stated at the
wrong level of abstraction.

**A skill is not a fifth place to put a rule.** It is the one layer that can
restate a rule without reading as a second definition, because a step reads as
"here is what to do now". The test: would the text still be true if the run
happened in a different order? If yes, it is a rule, it belongs in the protocol,
and the step cites it.

That split is the whole point of putting `.agentic` outside the repo. Point it
at a second project and only that repo's `agentic/` folder is new.

**The capability layer lives in the project's repo, not here.** Its profile
and packs sit in `<repo>/agentic/`, committed with the code they describe. Its
runs sit beside them in `agentic/runs/`, gitignored: they are for analysing
the network, not part of the product.
A pack correction then lands on the same branch as the change that made the old
wording false, and is reviewed in the same pull request. This follows Claude
Code's own split: project instructions are shared through the project's version
control, and a long-running agent's progress log lives in the project it
tracks. Runs that lint edits to the network itself sit in `.agentic/runs/`,
the repo their changes land in. `.agentic` is not a project: its
`.agentic.json` names only `agenticRoot`, so the linter can bind there.

## 4. Binding a repo to the network

The repo declares its own binding. `portfolio/.agentic.json`:

```json
{ "agenticRoot": "../.agentic", "project": "portfolio", "projectDir": "agentic" }
```

Every agent's first action is: find `.agentic.json` by walking **up** from the
working directory (a session started in a subdirectory is normal), resolve
`agenticRoot` against the directory holding it — not against cwd — then read
`PROTOCOL.md`, its one protocol extension if it has one, and the indexed
sections of `<projectDir>/project.md` and its own capability pack. No
`.agentic.json` above cwd means `BLOCKED`, not a guess at the layout.

Nothing else in the network hardcodes a path, so moving `.agentic` or adding a
second repo is a one-line edit.

**The repo's `CLAUDE.md` is free.** Claude Code loads it into every dispatched
lane at startup, so the product surface, stack, layout and command list arrive
without a tool call. The profile carries what `CLAUDE.md` does not — the lane
map, the numbered guardrails a lane may refuse an order over, and the friction
the repo docs do not record.

## 5. Roster — 12 agents, 15 lanes

The lane is the unit of dispatch; four agents fill two lanes each, because a
design pass and an integration gate are different jobs with different inputs
even when the same role does them.

| Lane | Agent | Pack | Owns |
|---|---|---|---|
| `recon` | `scout`; `reviewer` (CHECK) | — | read-only exploration: where does this live, what already exists, what will this touch. `reviewer` in CHECK mode when a claim can only be settled by running something |
| `product` | `producer` | `product.md` | **the front door.** Roadmap placement, epic/story shaping, sequencing — and where "no" lives |
| `quant` | `quantitative-researcher` (RESEARCH) | `quant.md` | formulas, academic grounding, trust-class analysis, metrics inventory, before a story exists |
| `story` | `story-author` | `story.md` | drafts the ticketed story. Decides nothing — not placement, not the contract |
| `ux` | `designer` (UX) | `ux.md` | the flow, screens, states, copy and design system, settled before the tech lead plans the contract |
| `design` | `tech-lead` (DESIGN) | `architecture.md` | the contract, reuse, and the lane split, settled before anyone codes |
| `backend` | `backend-engineer` | `backend.md` | `services/quant-engine/app/**` (non-test). Owns the contract source of truth |
| `frontend` | `frontend-engineer` | `frontend.md` | `apps/desktop/src/**` (non-test). Mirrors server schemas exactly |
| `test` | `test-engineer` | `testing.md` | everything under a test file — fixtures, goldens, the network guard |
| `docs` | `docs-engineer` | `docs.md` | `docs/**`, and at close-out only, applying `pack-corrections.md` back into the project's packs |
| `quant-audit` | `quantitative-researcher` (AUDIT) | `quant.md` | **mathematics gate.** Independently recomputes published numbers, checks trust labels |
| `integration` | `tech-lead` (INTEGRATION) | `architecture.md` | **engineering gate.** PASS / CHANGES_REQUESTED, per lane |
| `ux-review` | `designer` (UX-REVIEW) | `ux.md` | **design gate.** Screenshots the running app at phone and desktop widths against the UX spec. PASS / FAIL |
| `review` | `reviewer` | — | **acceptance gate.** ACs one by one, test-plan fidelity. PASS / FAIL |
| `protocol-lint` | `protocol-linter` | — | **authoring gate.** The network's own files against `authoring.md` |

`plugins/agentic-core/agents/` is the authority on the roster and
`scripts/check_report.py` (`LANES`) on the lane names. The two have disagreed
before, and a lane name the validator does not know is a report it cannot check.

**Every agent holds `Write`, for exactly one file: its own artifact in the run
dir.** "Read-only" was never quite true. What actually bounds the planning and
gate lanes is that they hold no `Edit` — though `Bash` remains a write primitive
for the lanes that have it, and that is a real gap, not a rounding error.

**Six of the twelve agents reach the bound repo's `project` MCP server** — `run_tests`,
`probe_engine`, `build_snapshot`, `check_gates`, `reset_goldens` — granted
narrowly, with the verifying gates (`reviewer`, `tech-lead`) getting nothing
that mutates. It exists because lanes
were otherwise hand-writing throwaway probe scripts to answer "what does this
route actually return?". Each agent file's `tools:` line is the authority on its
own grants.

**`tools:`, `model:` and `effort:` hold only while the block around them
parses.**
Frontmatter that fails to parse still loads the agent — name taken from the
filename, every other field dropped — so the lane silently takes the session's
default model and effort and the parent's entire tool roster in place of its
allowlist, `mcp__*` grants included. `claude plugin validate
plugins/agentic-core` reports it by file and reason; `protocol-linter` runs that
before it reads anything, and `authoring.md` § "The frontmatter has to parse, or
none of it applies" is the rule it cites.

**Model and effort are pinned in frontmatter on all twelve, never `inherit`.**
The policy is in `authoring.md`; the rationale is one test: *would a wrong
answer from this lane be caught by anything downstream — a test, a gate, a
validator, the human approval step?* If yes, Sonnet. If no, Opus. Only
`quantitative-researcher` and `protocol-linter` fail it. A wrong formula is
engineered perfectly, tested thoroughly, satisfies every acceptance criterion
and passes every other gate; a wrong `model:` line in an agent file bills wrong
on every dispatch forever and shows up as nothing at all. `tech-lead` is also on
Opus, by the owner's ruling rather than the test. `effort` is the second dial
and is not the model — `high` for the five lanes that decide something, `low`
for `tech-lead`, `medium` for the rest, because the implicit default is `xhigh` and an omission is a silent
escalation rather than a neutral one.

## 6. Why five gates

| Gate | Judges | Fails on |
|---|---|---|
| `quantitative-researcher` AUDIT | the **mathematics** | a wrong formula, a mislabelled trust class, a number that does not reproduce |
| `tech-lead` INTEGRATION | the **engineering** | contracts misaligned across lanes, the design not followed |
| `designer` UX-REVIEW | the **rendered UI** | a failed spec check, a missing state, a broken phone layout, an accessibility-floor breach, copy that contradicts the spec |
| `reviewer` | **acceptance** | the story's criteria not satisfied |
| `protocol-linter` | the **network's own files** | an agent, skill, pack or protocol section that breaks `authoring.md` |

None subsumes another. A wrong formula can be engineered flawlessly, tested
thoroughly, and satisfy every acceptance criterion — the engineering and
acceptance gates would both pass it, because neither is looking at the arithmetic. That is why
the quant gate runs first where analytics changed: if the mathematics is wrong,
the others are measuring the wrong thing. The converse holds too — correct math
can be wired into the wrong lane, or ship a feature nobody asked for. One gate
holding every standard in one context is exactly the dilution this network
exists to avoid.

The first four gate a **delivery** run and are the ones the close-out sweep
checks. `protocol-lint` gates the lint runs in `.agentic/runs/`, over edits
to the network's own files; a delivery ledger never mentions it. A project's packs are
project docs, reviewed in the pull request with the code, so a pack correction
owes no lint. The linter judges a project's profile and packs once at
onboarding, and again whenever an order asks for an audit.

**A gate that reads only the source the work was built from is not a gate.** It
catches slips, not wrong premises, and the failure is invisible: every gate
passes, loudly and correctly, and the defect ships. Where a pack names an
external anchor — a reference implementation, a textbook definition,
hand-computed values, a second data source — the gate must use it and say in
`verification.detail` which one. "Recomputed from the methodology doc" is a
consistency check, and a methodology doc that is itself wrong will agree with
you every time.

### Why the producer is the front door

A request that arrives as "add X" is a request to change the plan. Without a
producer, the orchestrator either changes the plan implicitly — producing work
with no place in the roadmap — or the human does it manually every time.

The producer is also where **"no" lives**: already shipped, already storied,
deliberately left open with a recorded reason, or out of scope. It is the
cheapest place in the flow to kill work, which is why it runs before anything
that costs a build lane.

## 7. Design rules

**The orchestrator does not write code, and does not make specialist calls.** It
plans, dispatches and relays. If it starts editing files you have lost the
isolation you paid for; if it starts deciding scope or contracts, you have lost
the specialists. Doing a lane's work always looks cheaper in the moment and the
result is frequently good, which is what makes it dangerous: a run that answers
its own request has no scope fence, no pack, no gate, no artifact and no ledger
entry — and it teaches, by succeeding, that the network is ceremony.
`dispatched: 0` is a disclosure, not a result.

**The orchestrator stays in the main session.** Fan-out is one level deep,
driven from the top, by choice: Claude Code lets subagents nest, but no lane
holds the `Agent` tool, because coordinating through a lane that cannot see the
ledger is the failure the ledger exists to prevent. Anthropic's own
multi-agent write-up says the same of coding work: few of its tasks
parallelise cleanly, and agents are not yet good at delegating to each other in
real time. The producer
cannot commission a story and the tech lead cannot dispatch an engineer — they
emit briefs, plans and change requests, and the orchestrator carries them. A
paraphrased change request is the orchestrator's judgment wearing the tech
lead's authority.

**So relay by path, not by quotation.** Asking the orchestrator to carry text
verbatim is an instruction, not a mechanism — and the moment context gets tight,
summarising is exactly what a model does. Every agent writes its own artifact
into `runs/<id>/` and a work order's `inputs` names files. The receiving
specialist reads the original. Verbatim became a property of the filesystem.

**Managing is relaying, and that is enough.** "The tech lead can request changes
from any engineer" works, mechanically, as: tech lead writes the request to
`<run_dir>/cr/CR-<n>.md` → orchestrator opens a new work order on the owning
lane, scope fenced to that finding, the file named in `inputs` → engineer fixes
exactly that → the integration gate re-runs. **Every other gate routes the
same way**, with the orchestrator writing the request on the failing gate's
behalf, since none of them can dispatch either; the body then points at the
gate's own report rather than restating it, because a relayed finding restated
is the orchestrator's judgment wearing the gate's authority. **Two rounds maximum on the same
finding**, counted in the ledger's `Rounds` table rather than in anyone's
memory; a third means the request is unclear or the design is wrong, and that
goes to the human. A finding caused by a previous round's fix is that finding
renumbered, so the row names its ancestor in `caused by` and the count
continues across it — otherwise the cap is defeated by renaming.

**Serial by default.** One order at a time, and its head is read before the next
is written. Parallel dispatch carries conflicting implicit decisions that only
surface at the gate.

**Vertical slice is the unit of work, lane is the unit of dispatch.** One story
= one vertical slice = several work orders across lanes. Never dispatch a lane
that does not trace to approved scope.

**Every dispatch is a contract.** A work order names goal, scope, inputs,
definition of done, and explicit non-goals. `scope` is a fence written as paths,
not intentions; `non_goals` is the field that prevents scope creep and the one
people skip. An agent that has to guess its boundary will expand it.

**Every factual claim in an order is sourced** — something the orchestrator read
this turn, or something a path in `inputs` says. What it does not know goes in
as a question for the lane, never as a premise. Needing a claim with neither
*is* the `ground-truth` trigger, and it is what that phase exists for: an
unverified claim reads exactly like a verified one, which is why it has to be
sourced where it is written rather than caught where it hurts.

**Reports are structured, not prose, and a lane returns a head rather than a
body.** The artifact goes to disk in full; what comes back is a short head —
status, verdict, verification, and a count per routable section — and the
orchestrator opens a section only when a count says there is something in it.
The head is *derived* by `check_report.py --emit-head`, never typed, because a
count written by hand is wrong in the one direction that matters: too low,
silently dropping work.

**The ledger is written by a script for the same reason.** `scripts/ledger.py`
applies a head's Artifacts row, `next:`, phase state and `Open` rows in one
call, derives `spent:` from the rows rather than taking it as an argument, and
hands the result to `check_report.py`'s ledger battery — so an inconsistency is
reported at the dispatch that caused it instead of at close-out. `Rounds` and
`Replans` are prose rows written a few times a run and stay hand-edited.

**Gates stay mechanical.** `run_all_tests.py`, the commit hook and CI remain the
actual authority, and the integration gate runs the project's whole acceptance
command rather than the subset the run happened to touch. The reviewer agent is
a *pre-*check that catches problems cheaply; it never replaces a green suite.
No lane commits, and no agent merges; a project that declares a tracker lets
the orchestrator commit to the run's branch (`protocol/orchestrator.md` § 8).

**A lane cannot delete or rename a file.** Deliberate — deletion is the one repo
edit with no diff to review. A lane does the half it can and reports the other
half as a `should_fix` naming the exact command.

**Skills stay in the repo, agents stay in `.agentic`.** A repo skill is
procedural knowledge the repo owns and versions with its code (`ui-polish`,
`fmp-data`). An agent is a worker with a context budget. Agents *invoke* repo
skills; the network's own two skills carry sequence, not rules.

**Third-party technique skills are enabled per repo and fired by a pack.**
`mattpocock-skills` is on in `budget`, `impact` and `portfolio`, through each
repo's `.claude/settings.json`. It supplies technique (`diagnosing-bugs`,
`tdd`, `codebase-design`), never house style. A lane calls one only where its
capability pack names the trigger and adapts the skill to the lane's fences.
The profile's skills section lists every allowed call. A skill with
`disable-model-invocation` (`to-spec`, `to-tickets`, `handoff`) cannot be
wired to a lane at all. Every call, made or skipped, lands in the report's
`skill_calls:` field, which the tech lead's INTEGRATION pass checks against
the rest of each report.

## 8. Gaps and plans

What is wrong or missing is in [`TECH-DEBT.md`](./TECH-DEBT.md), with the map of
which rules a script enforces and which rest on an agent's judgment. What comes
next is in [`ROADMAP.md`](./ROADMAP.md).
