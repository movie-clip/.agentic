# `.agentic` — agent network architecture

Version 0.4. Lives at `C:\projects\investments\.agentic`, one level above the
repos it drives. First bound project: `portfolio` (quant-research-lab).

---

## 1. The problem this solves

Today `portfolio/.claude/skills/` holds a **linear pipeline**:

```
quant-research → write-story → build-story → write-tests → verify-story → update-docs
```

It works, but everything runs in one context. `build-story` carries the whole
project in its head — backend conventions, UI design system, pytest fixtures,
FMP caching, doc contracts — and hands the model 2,500 lines of skill text for a
change that might touch three files. Two consequences:

- **Context dilution.** The test conventions compete for attention with the
  Recharts shim and the trust-ladder rules, even on a backend-only ticket.
- **No isolation.** A wrong turn in the UI slice pollutes the reasoning of the
  backend slice, because they share one transcript.

The fix is not more skills. It is **separating who decides from who does.**

## 2. The model

```
   you (chat) ── "add a per-sector drawdown breakdown to the Risk tab"
        │
        ▼
  ┌──────────────┐   1. PRODUCER — where does this belong?
  │              │──────► roadmap · epic · story shape · dependencies
  │              │◄────── delivery brief          ── you approve ──┐
  │              │                                                  │
  │              │   [story authoring — human gate, repo skill] ◄───┘
  │ ORCHESTRATOR │
  │              │   2. SCOUT — read-only map of the area
  │  main session│
  │  plans       │   3. TECH LEAD (design) — the contract, reuse, lane split
  │  dispatches  │──────► technical plan  ── you approve the lane plan ──┐
  │  relays      │                                                        │
  │              │   4. ENGINEERS, one order at a time ◄──────────────────┘
  │              │──────► backend → frontend → test → docs
  │              │◄────── reports · contract_notes · handoff
  │              │
  │              │   5. TECH LEAD (integration) — engineering gate
  │              │◄────── PASS │ CHANGES_REQUESTED ──┐
  │              │                                    │ relayed verbatim
  │              │──────► back to the owning lane ────┘
  │              │
  │              │   6. REVIEWER — acceptance gate vs the story
  └──────┬───────┘◄────── PASS │ FAIL
         ▼
   you run the suite and commit
```

Each specialist runs in its own context with its own tools and its own
capability pack. The orchestrator sees only their reports.

Three layers, deliberately separated:

| Layer | Lives in | Changes when |
|---|---|---|
| **Roles** — what a test engineer *is*, how it reports | `plugins/agentic-core/agents/` | never (project-agnostic) |
| **Protocol** — message shapes, run ledger, gate rules | `PROTOCOL.md` — one copy, pointed at from everywhere | rarely |
| **Context packs** — how *this* repo does testing | `projects/<name>/capabilities/` | every time the repo evolves |

That split is the whole point of putting `.agentic` outside the repo. Point it
at a second project later and only the `projects/<name>/` folder is new.

## 3. Binding a repo to the network

The repo declares its own binding. `portfolio/.agentic.json`:

```json
{ "agenticRoot": "../.agentic", "project": "portfolio" }
```

Every agent's first action is: find `.agentic.json` by walking **up** from the
working directory (a session started in a subdirectory is normal), resolve
`agenticRoot` against the directory holding it, then load `PROTOCOL.md`,
`projects/<project>/project.md` and its own capability pack. Nothing else in the
network hardcodes a path, so moving `.agentic` or adding a second repo is a
one-line edit.

## 4. Roster (v0.3)

| Agent | Tools | Job |
|---|---|---|
| `quant-analyst` | read + bash + run-dir write | **Owns guardrail one.** Research mode: formulas, grounding, trust-class analysis before a story exists. Audit mode: independently *recomputes* published numbers and checks trust labels against the basis they rest on. |
| `producer` | read + run-dir write | **The front door.** Owns the roadmap: does this already exist, does it fit the active epic, is it a new epic, should it be declined. Shapes stories as vertical slices, sequences them, names dependencies. |
| `scout` | read + run-dir write | Recon. "Where does this live, what already exists, what will this touch" — compressed to the two hundred words that matter. |
| `tech-lead` | read + bash + run-dir write | **Manages the engineers.** Design mode: settles the contract and reuse before anyone codes. Integration mode: the engineering gate, returning change requests per lane. |
| `backend-engineer` | read/write/bash | Schemas → service → route → registration. Owns the contract source of truth. |
| `frontend-engineer` | read/write/bash | TS types mirroring schemas; cards built on the design-system primitives. |
| `test-engineer` | read/write/bash | Everything under a test file. Knows the network guard, shared fixtures, goldens, the assertion-brittleness rules. |
| `docs-engineer` | read/write | Contracts, methodology, slice log, shipped-state inventory — and, at close-out only, applying `pack_corrections` back into the capability packs. |
| `story-author` | read/write | Drafts the ticketed story from the producer's brief. Decides nothing: not epic placement, not the contract, not the producer's open decisions. The human approves. |
| `reviewer` | read + bash + run-dir write | The acceptance gate: ACs one by one, test-plan fidelity, trust-state spot checks. PASS / FAIL. |

All ten are live, each with a capability pack for `portfolio`.
(`plugins/agentic-core/agents/` is the authority on that count — this table and
the READMEs have disagreed before.)

**"read-only" was never quite true, and v0.3 stopped pretending.** Every agent
now holds `Write`, for exactly one file: its own artifact in the run dir. The
gate and planning lanes hold no `Edit` tool, which is the part that actually
bounds them — though `Bash` remains a write primitive for the four lanes that
have it, and that is a real gap, not a rounding error.

### Why three gates

| Gate | Question | Runs |
|---|---|---|
| `quant-analyst` | Are the numbers correct and honestly labelled? | first, when analytics changed |
| `tech-lead` | Do the lanes cohere — contracts, reuse, design followed? | second |
| `reviewer` | Does this satisfy the story? | last |

None subsumes another, and the order matters. A wrong formula can be engineered
flawlessly, tested thoroughly, and satisfy every acceptance criterion — the
second and third gates would both pass it, because neither is looking at the
arithmetic. That is why the quant gate runs first: if the mathematics is wrong,
the other two are measuring the wrong thing.

The converse holds too. Correct math can be wired into the wrong lane, or ship
a feature nobody asked for. One gate holding all three standards in one context
is exactly the dilution this network exists to avoid.

### Why the producer is the entry point

A request that arrives as "add X" is a request to change the plan. Without a
producer, the orchestrator either changes the plan implicitly — producing work
with no place in the roadmap — or the human does it manually every time.

The producer is also where **"no" lives**: already shipped, already storied,
deliberately left open with a recorded reason, or out of scope. In a repo with
131 stories across 35 epics, that check is the highest-leverage thing in the
flow.

## 5. Design rules

**The orchestrator does not write code, and does not make specialist calls.** It
plans, dispatches and relays. If it starts editing files you have lost the
isolation you paid for; if it starts deciding scope or contracts, you have lost
the specialists.

**The orchestrator stays in the main session.** Assume a subagent cannot spawn
another subagent. Fan-out is one level deep, driven from the top. So the
producer cannot commission a story and the tech lead cannot dispatch an
engineer — they emit briefs, plans and change requests, and the orchestrator
carries them. A paraphrased change request is the orchestrator's judgment
wearing the tech lead's authority.

**So relay by path, not by quotation.** v0.2 asked the orchestrator to carry
text verbatim, which is an instruction, not a mechanism — and the moment context
gets tight, summarising is exactly what a model does. In v0.3 every agent writes
its own artifact into `runs/<id>/` and a work order's `inputs` names files. The
receiving specialist reads the original. Verbatim became a property of the
filesystem.

**Managing is relaying, and that is enough.** "The tech lead can request changes
from any engineer" works, mechanically, as: tech lead emits a change request →
orchestrator opens a new work order on the owning lane, scope fenced to that
finding, request text quoted → engineer fixes exactly that → integration review
re-runs. Two rounds on the same finding, then escalate to the human.

**Vertical slice is the unit of work, lane is the unit of dispatch.** One story
= one vertical slice = several work orders across lanes (schema, engine, UI,
tests, docs). Never dispatch a lane that does not trace to a story ticket.

**Every dispatch is a contract.** A work order names goal, scope, inputs,
definition of done, and explicit non-goals. An agent that has to guess its
boundary will expand it.

**Reports are structured, not prose.** The orchestrator only sees the report —
if it is chatty, integration is guesswork. See `agentic-protocol`.

**Gates stay mechanical.** `run_all_tests.py`, the pre-commit hook and CI remain
the actual authority. The reviewer agent is a *pre-*check that catches problems
cheaply; it never replaces a green suite.

**Skills stay in the repo, agents stay in `.agentic`.** A skill is procedural
knowledge the repo owns and versions with its code (`ui-polish`, `fmp-data`).
An agent is a worker with a context budget. Agents *invoke* repo skills — the
existing eight are not replaced, they become tools the specialists reach for.

## 6. Relationship to the existing skills

| Existing skill | Fate |
|---|---|
| `quant-research` | unchanged — a research lane the orchestrator can route to |
| `write-story` | unchanged — still authors the story before any dispatch |
| `build-story` | **thins out.** Its per-lane knowledge migrates to capability packs; what remains is ticket sequencing, which the orchestrator absorbs |
| `write-tests` | becomes the body of `capabilities/testing.md`, invoked by `test-engineer` |
| `verify-story` | becomes the `reviewer` agent's checklist |
| `update-docs` | becomes `docs-engineer`'s capability pack |
| `ui-polish`, `fmp-data` | stay as-is — reference skills the specialists load on demand |

Nothing is deleted in v0.1. The network reads the existing skills; migration is
incremental and reversible.

## 7. Roadmap

- **v0.1** — protocol, orchestrator, `scout` + `test-engineer`, portfolio profile.
- **v0.2** — `producer` and `tech-lead` added; nine roles live; backend / frontend / docs / product / architecture packs written; two-gate model; change-request relay.
- **v0.2.1** — `quant-analyst` added, owning guardrail one; three-gate model. `story-author` brings the roster to ten.
- **v0.3 (this)** — the design review's structural fixes, pulled forward because they change what the first real run would be testing:
  - **run ledger** under `runs/<id>/`. A slice's state is on disk, not in the orchestrator's context. Resumable after a compaction or a restart; round counters and unabsorbed contract notes are written down rather than remembered. (Was v0.5.)
  - **relay by path.** Every agent writes its own artifact; `inputs` names files, never quotations. "Verbatim" becomes a filesystem property instead of an instruction the model is asked to honour under context pressure.
  - **one copy of the protocol.** `PROTOCOL.md` is the only definition of the shapes; the skill and all ten agent files point at it. v0.2 had eleven copies and two had already drifted.
  - **the express lane.** A defined cheap route for one-lane work that crosses no contract and touches no mathematics — with a self-voiding rule, so it escalates rather than quietly building a slice sideways.
  - **`status` / `verdict` / `verification.result` separated.** Gate outcomes were previously unrepresentable.
  - **`pack_corrections` + a close-out order that applies them.** The packs finally have an owner.
  - **`build-story` marked superseded** in the repo, ending the trigger collision with `orchestrate-feature`. (Was v0.4.)
  - **binding walks up** from cwd instead of assuming the repo root.
- **v0.3.1** — first real invocation, and it exposed two things no amount of protocol design would have:
  - **the network could not say which version of itself was running.** The run executed `v0.2.3` from a stale git-sourced marketplace clone while `v0.3.0` sat uncommitted in the working directory, and nothing in the output revealed it. The orchestrator now announces `agentic-core v<version> · project · route` as its first line, and repeats it with `dispatched: <n>` at close-out.
  - **the orchestrator's real failure mode is a no-op, not a bad plan.** It answered the request itself in the main session — zero dispatches, four files edited directly, no ledger, no gates, the producer's verdict issued in its own voice — and produced a genuinely good answer. A no-op that succeeds is the most dangerous outcome available, because it teaches that the network is ceremony. `commands/feature.md` now loads the skill imperatively and carries the non-negotiables inline as a safety net; the skill leads with the no-op self-checks; and `dispatched: 0` must be disclosed rather than presented as a network result.
- **v0.3.2** — first clean run (`review` route), and the fixes it earned:
  - **`scripts/check_report.py`.** The report contract stopped being prose. The orchestrator validates every artifact before routing from it; agents can check their own first. It caught its own first bug (matching keys at column 0, when `command`/`result` are indented under `verification`). It checks routability, never truth.
  - **`review` is its own route.** The run announced `route audit`, which is the quant lane's single-dispatch route. Health reviews and findings fold-ins now have a name and a stated shape: verify state → `scout` for ground truth → `producer` for placement.
  - **Findings are claims.** A findings document — including one this network wrote, including its own "already fixed" section — is an input to verify, never a premise. The first run found a doc asserting six items were logged in a register that contained none of them, and one finding that was simply false.
  - **`status` takes the bare enum**, with `blocked_on:` for the reason. Free text in an enum field is unreadable by the next session.
  - **`agentic_root` resolved once, absolute.** Repeated relative-path arithmetic produced `C:\projects\investments.agentic\...` in dispatched orders — one separator from correct, and silent.
- **v0.4 (this)** — two compounding context fixes, measured against the first full run rather than asserted:
  - **the protocol is partitioned by audience.** `PROTOCOL.md` is a 245-line core every agent reads; `protocol/orchestrator.md`, `gates.md`, `packs.md` and `authoring.md` are read by exactly the roles that need them. This is a partition, not a copy — no rule appears in two files, so the v0.3 single-copy rule still holds. Binding tells each agent which one extension is its own.
  - **provenance moved out of the agent-facing files.** Everything under `PROTOCOL.md`, `protocol/`, `projects/` and `agents/` is read only by models, once per dispatch, many dispatches per run. The *why* that changes behaviour stays; the story of how a rule was discovered lives here instead, where its reader is a human deciding whether to trust the design. Four artifacts remain human-facing and are still written for a person: the delivery brief's recommendation, the story's acceptance criteria, the gate verdicts, and the close-out report.
  - **packs and profiles are read by index.** Each opens with `## Index` naming its always-read sections and a "read it when" row for the rest. Binding no longer says "in full" — a backend order stopped paying for the frontend primitives and the quant trust ladder.
  - **the duplicated tails are gone.** All ten agent files carried a byte-identical 38-line "Required output format" section. It is 20 lines now, and it no longer contradicts the protocol.
  - **`REPORT HEAD` — the artifact pattern, finished.** v0.3 had agents write a full report to disk *and* return it in full, so the orchestrator paid for every body twice and mostly routed none of it. A lane now returns an 11-line head — status, verdict, verification, and a count per routable section — and the orchestrator opens a section only when a count says there is something in it. `check_report.py --emit-head` derives the head from the artifact, because a count typed by hand can be wrong in the one direction that matters: too low, silently dropping work.
  - **planning artifacts carry a `## Orchestrator brief`**, 15 lines, enforced. `04-stories.md` and `05-technical-plan.md` were 546 and 454 lines — half of all artifact volume in the first full run — read end to end to extract about thirty lines of routing decisions. The sections skipped are not lost: they reach the lane that needs them as an `inputs` path, which is what the relay rule was always for.
  - **the ledger got a schema.** `Open` and `Rounds` are typed tables now. The evidence was already in the data: the report block has a schema and lane reports stayed between 25 and 81 lines; `run.md`'s `Open` section had none and reached 705 words with single bullets over 700 characters. Structure, not discipline, is what keeps an artifact small.
  - **bullets are capped** at 400 characters hard, 200 as the target. Measured across the 186 bullets of the first full run: median 336, longest 1,517. The median is the habit the cap is changing.
  - **measured, not claimed.** Mandatory per-dispatch reading fell **26%** on average (896 → 586 lines for a backend order; 13,824 → 10,224 across sixteen dispatches). Replaying the first full run's sixteen artifacts under the head rule puts **527 lines** into the orchestrator instead of 1,935 — **73% less** — and the two planning artifacts go from 1,000 lines to 72. The first pass measured 30%/74%; the review pass gave 4 points back to buy correctness fixes, which is the right trade.
  - **reviewed, and it was not clean.** A change-by-change pass found six bugs in `check_report.py` and three regressions in the design. The validator ones: code fences were parsed as document structure (a `## ` in a quoted diff read as a section; a `key:` in a quoted YAML truncated the section it sat in, making the head's counts wrong while every check passed); the head's `detail` was checked as a *prefix*, so an agent could stop just before "4 skipped"; an unedited `--emit-head` placeholder passed; `US-36.10` satisfied a `US-36.1` section by substring. All fixed, and `scripts/test_check_report.py` now pins all of them — the validator had no tests of its own, which was its own gap.
  - **the review also corrupted nine capability packs and had to undo it.** A regex written to rebuild the index table matched every two-column table in each file, duplicating Doc/Module/Primitive rows into the index; the repair script for *that* used `re.S`, so `\|.*\|` ran across newlines and deleted real content — `project.md` fell from 216 lines to 87. Restored from HEAD and redone as pure insertion, with an assertion that every section appears in the index exactly once and a check that no original line is lost. The lesson is in `authoring.md`: a script that rewrites a pack must be scoped to a heading, never to a pattern that also matches the pack's own content.
  - **still unvalidated:** every number above is a replay against v0.3 artifacts, not a v0.4 run. The head, the brief and the bullet cap have never been produced by a live agent. That is what the next run tests.
- **v0.4.1** — cost. A usage report showed 42% of spend coming from subagent-heavy sessions, which is the documented shape of this pattern (multi-agent runs cost roughly 15x a chat session, and token usage explains ~80% of performance variance) — but the documented discipline has two halves and only one was implemented. The route table was already the scaling heuristic; model selection did not exist.
  - **every agent pins a model explicitly.** All ten were `model: inherit`, so all sixteen of the first full run's dispatches billed at the main session's tier and nothing in the run said so. `inherit` is now banned in `authoring.md`, along with `fable`.
  - **Sonnet is the ceiling, Opus is the exception.** The test is stated rather than listed: *would a wrong answer from this lane be caught by anything downstream — a test, a gate, a validator, the human approval step?* If yes, Sonnet. If no, Opus. Only `quant-analyst` fails that test: a wrong formula is engineered perfectly, tested thoroughly, satisfies every acceptance criterion and passes every other gate. It is also the rarest lane, so highest-consequence x lowest-frequency is what earns the premium. `scout` runs on Haiku — read-only retrieval whose every claim is cheap to verify by opening the file it cites.
  - **the gates went to Sonnet, deliberately.** v0.4 moved their load-bearing checks off the model and onto mechanisms: `check_report.py` for the report shape, head counts and brief completeness; falsifiable acceptance criteria; the external-anchor rule. A gate leaning on structure is far less tier-sensitive than one leaning on the model noticing something. If gate quality drops, `tech-lead` INTEGRATION moves back first — on ledger evidence, not on a hunch.
  - **cost is recorded, not felt.** The ledger's Artifacts table gains a `model` column and the ledger gains a `Cost` block (dispatches, rounds, model spread, escalations). `scripts/run_cost.py` derives all of it from the rows and fails when the tally disagrees or a dispatch recorded no model — a tally written from memory at close-out drifts exactly like a report nobody validates. `scripts/test_run_cost.py` pins 17 cases, including the happy path no real ledger exercises yet.
  - **escalation is evidence-driven.** The frontmatter is a default, not a ceiling: the orchestrator may raise one dispatch to Opus when a lane returns `BLOCKED` on something that is not a missing input, or a finding reaches its second change-request round. Marked `opus↑` in the ledger so the pattern is reviewable.
  - **the number that decides whether this worked** is change-request rounds. A cheaper engineer that produces two extra rounds costs more than the model it replaced, because a round is a re-dispatch plus a re-run of the integration gate. That is why the Cost block records rounds beside model spread, and why the first Sonnet run is a measurement rather than a conclusion.
  - **still unmeasured:** no run has yet executed under these settings. On the first full run's shape (11 of 16 dispatches were execution lanes, and `quant` never ran at all) the same work would now be 15 Sonnet and 1 Haiku — but the round count is the term that could undo it, and only a real run can supply it.
- **v0.4.2 — the producer, reviewed against its own output.** The only lane with a real artifact to grade (`02-delivery-brief.md`, the run that became Epic 36).
  - **it did the hard part well.** It dropped F-R4 as a false finding, spotted F-R2 as an exact duplicate of `US-26.3`, proposed a sibling to Epic 32 rather than inventing a pattern, and routed the F-R1 design choice to the tech lead instead of deciding it. The judgment was not the problem.
  - **the brief was in the wrong field.** Step 5 said to put the delivery brief in `handoff`, so a 40-line document went into a list field and was shredded into **9 bullets, longest 608 characters**, split wherever a nested `-` happened to fall. The orchestrator could not route "the open decisions" separately from "the sequence" because both were fragments of one bullet. v0.4 had already added a `## Orchestrator brief` section to this agent — so the file contradicted itself, and that contradiction was mine. The brief is now a document below the block; `handoff` carries one-line pointers with `see § <section>`. Same content, 5 bullets, longest 96 characters, and every one routable on its own.
  - **it treated recon as ground truth, and recon is now Haiku.** Its own `risks` said so: *"I did not independently re-verify any of scout's file:line claims."* F-R4 was **dropped** on one unverified claim — and dropping a finding is a verdict. Now: *any claim that changes a verdict, you open yourself*. Narrow enough to stay cheap (one `Read`), and it is `gates.md`'s independence rule applied one level up. Without it, v0.4.1's model split would have run the cheapest lane's unchecked claims straight into the brief a human approves.
  - **it had git and did not know to use it.** `tools:` grants `Bash`, yet the brief twice recorded that history was not checked. `git log -S` is the definitive answer to Step 1's "does this already exist?" — a doc can be stale about the code, a commit cannot. Now named with the commands.
  - **it navigated a 1,721-line roadmap by instinct.** It read lines 1–180 plus two epic sections, which was exactly right and written nowhere. The pack now documents the roadmap's actual shape (snapshot in the first ~70 lines, epics newest-first below) and the `grep -n "^## .*Epic "` that shortlists precedents — because placement here is precedent-driven, and an epic proposed with no stated precedent is usually epic inflation.
  - **`- none (read-only; report is this file)` counted as one changed file**, so the head advertised work that never happened. Real instance of the ambiguity the review pass flagged; the fix is guidance to write a bare `- none`.
- **v0.4.3 — the first real story, end to end.** `2026-08-21-dynamic-sector-classification`: 12 dispatches, 1 change-request round, sonnet 10 · opus 2, stopped by a session limit at dispatch 12 with the implementation merged and the suite green. **All 12 artifacts validate.** The v0.4 contract survived first contact.
  - **the Opus gate earned its keep on its first run.** 840 backend tests, 331 frontend, tsc clean, dead-code clean — all green — and `quant-analyst` AUDIT returned `FAIL` on a MATERIAL finding every one of those checks missed: an untouched catch-all in `registry.py` still hardcoded `sector="Other"`, so a position with no matching broker record violated the story's own AC9. That is the exact profile the model policy reserves Opus for: a lane with no downstream check, catching what the downstream checks could not.
  - **the producer disconfirmed the request's premise.** The user reported SBIO landing in "Other"; the producer ran the importer and found SBIO already classified correctly, then found the *larger* real gap behind it (equities never get dynamic classification at all). The verdict changed on evidence it opened itself — the behaviour v0.4.2 turned into a rule.
  - **`Open` grew without bound.** The v0.4.1 rule — "nothing leaves the table by being deleted; it changes state" — kept the audit trail and let the working table reach **57 rows, 20 already ABSORBED**, re-read on every update. Fixed the length problem, missed the growth problem. Absorbed rows now move to a `## Closed` table; `Open` holds only what is open. The same run also recorded one tombstone twice, so: one fact, one row — check `ref` before appending.
  - **`status: DISPATCHING` does not say what to dispatch.** The run ended mid-flight and resuming meant reconstructing intent from twelve rows. The ledger gains `next:` — one line, the single next action, rewritten on every update.
  - **an order and a capability pack disagreed, and the lane silently obeyed the order.** `docs.md` says a brand-new methodology section is flag-for-human; the order said write it; the lane wrote it, flagged the conflict in `risks`, and reported `DONE` — so nothing downstream treated the doc as provisional. Now: a numbered project guardrail always wins (`REFUSED`); a pack *convention* does not block the order but forces `PARTIAL` plus the conflict named.
  - **no lane can delete a file**, so a story renumber left a tombstone nothing in the network could clean up. Deliberate — deletion is the one repo edit with no diff to review — but previously unstated. A lane now does the half it can and reports the other half as a `should_fix` naming the exact command.
  - **`--lane quant` on a `quant-audit` artifact** produced "this report is wrong" when the fault was the argument. The validator now infers the lane from the filename and says *"did you mean --lane quant-audit?"*.
  - **two things that looked like bugs were not**: the doubled producer dispatch and the `C:\projects\investments.agentic` path in the transcript are display artifacts — artifact count, ledger rows and cost all reconcile at 12, and no stray directory exists.
- **v0.4.4 — effort, the dial that was never set.** `model` decides which model runs; `effort` decides how hard it works. They are independent frontmatter fields, and v0.4.1 pinned only one of them.
  - **the default was not neutral.** Claude Code's implicit `effort` is `xhigh` — the second-highest of five — so all ten lanes had been running near the top of the range on every dispatch since the network existed. Nine of them now run lower: `high` for the judgment and implementation lanes, `medium` for drafting and applying, `low` for `scout`'s pure retrieval.
  - **the settled split (v0.4.5) is two levels, not four.** `high` for the five lanes that *decide* something — `producer`, `tech-lead`, `reviewer`, `backend-engineer`, `frontend-engineer`; `medium` for everything else, which drafts, applies, tests or retrieves against something another lane already fixed. `low` and `max` are defaults nowhere; `max` remains the escalation on the same evidence rule as a model escalation.
  - **`quant-analyst` runs Opus at `medium` — the tier does the work, not the dial.** A deliberate trade, and the one to watch: it found the first real run's MATERIAL defect at `xhigh`, and the gate with no downstream check is the worst place for a silent regression. If an audit ever passes something a later gate catches, that is the signal to raise it.
  - **`scout` runs at `medium` rather than `low`.** Retrieval is the canonical `low` task, so this is the single lane deliberately above the cheapest setting that would do; judge it on whether `file:line` citations stay complete, not on cost.
  - **lower effort is different, not merely cheaper.** Fewer and more-consolidated tool calls, less preamble, terser confirmations. Usually an improvement for lanes whose output is a structured report — but it is why `scout` at `low` must be judged on whether its `file:line` citations stay complete, not only on what it costs.
  - **two things effort does not control, now written down.** Extended thinking is inherited from the main session with no per-agent override, so it is a property of how the human runs the orchestrator, not something a lane can set. `maxTurns` is a separate ceiling on turns rather than depth, deliberately left unset — a turn cap that fires mid-task yields a truncated report, which is worse than an expensive one.
  - **the ledger records effort overrides** alongside model ones (`sonnet/max↑`), so an escalation on either dial is visible after the fact.
- **v0.4.6 — the first story closed end to end.** `US-37.1`, 17 dispatches, 1 change-request round, sonnet 14 · opus 3, all three gates PASS, story `Done`, epic 37 Completed. **All 17 artifacts validate and the cost tally reconciles.** The run executed on v0.4.1, so 0.4.2–0.4.5's fixes were not in effect — most of what it exposed was already closed, and only three things were new.
  - **three lanes were told to run a script they cannot run.** `scout`, `story-author` and `docs-engineer` have no `Bash` by design, yet every agent file instructed them to self-check with `check_report.py`. They spent a `risks` bullet apologising for it three separate times in this run. The instruction is now conditional, and says plainly that the orchestrator's own validation — which is mandatory — is what actually checks the artifact.
  - **the docs pack instructed `git diff` for a lane with no shell**, and `"read the diff, not the story"` is load-bearing for that lane. It substituted reading the code and mentioned it in `risks`. Replaced with the right source: the upstream lanes' `changed:` sections, which arrive as `inputs` paths and are a *better* diff — one line per file, written by the lane that touched it, and unable to include an unrelated working-tree edit.
  - **`pack_corrections` does not catch this class of false premise.** The loop is aimed at facts about the *code*; a lane that cannot run a command substitutes something and files a `risk`, not a correction. So the check moved to authoring time: **every command in a pack must be runnable by the lane that pack belongs to** — open the agent file's `tools:` line before writing one.
  - **`- none` must be bare.** `- none — because X` counts as one real entry, so the head advertises work that does not exist. The v0.4.3 warning fired five times in this run; the rule it was warning about is now written down.
  - **the Opus quant gate earned its keep twice.** It returned `FAIL` on a MATERIAL finding — a pre-existing catch-all in `registry.py` still hardcoding `"Other"`, reachable in practice and invisible to 840 green tests — then `PASS` on the re-check after CR-1. One gate, one round, one real defect caught.
  - **a failed dispatch is invisible to the cost tally.** Dispatch 12 died on a session limit before writing an artifact and was re-dispatched; `run_cost.py` derives dispatches from artifact rows, so the run cost one more attempt than the ledger says. The orchestrator did record it under `Open` as an `infra` row. Left as-is — the tally measures work produced, and a retry after an API failure is not a lane problem worth a schema change.
- **v0.4.7 — the ledger stopped tracking a run it was in the middle of.** In `2026-08-21-epic38-followups-and-etf` the producer returned, its head validated, and the orchestrator read the brief and reported it to the human — while the Artifacts table still showed one row and `next:` still said `awaiting 02-delivery-brief.md from producer`. The artifacts were fine; only the record was wrong.
  - **the rule was implied, never stated.** `orchestrator.md` showed the Artifacts table's shape and insisted the `model` column be accurate, but never said *when* a row gets written. Now it does: the row and `next:` are written **when the head returns, before you read the artifact** — because the two natural stopping points, "I know what to do next so I will go do it" and "I told the human and the turn ended", both come after the head and both feel like completion. A pre-dispatch ledger edit does not discharge it; that records intent, and intent is what a stale ledger already has too much of.
  - **`run_cost.py` crashed on the path a human would type.** Given `runs/<id>/run.md` it fell through its directory branch to `iterdir()` and raised `NotADirectoryError`. It now accepts the ledger, the run dir, or the parent of many runs; anything else exits 2 with a message. Four cases pin it.
  - **an unfilled Cost block said `0`, not `—`.** `0` is a claim that no dispatch happened, so the validator correctly reported a mismatch on every mid-flight run. The placeholder is now `—`, which the tally already skips.
  - **the producer corrected the record it was handed, and was right.** US-37.2 recorded the `cached: True` bug shape as "4 other methods" including `get_quote`. The producer re-opened the source and reported five methods across six call sites, and that `get_quote` does not exist — the method is `get_latest_quotes`. Verified against `market_data.py`: six hardcoded sites, five distinct methods, no `get_quote` anywhere. This is v0.4.2's **"any claim that changes a verdict, you open yourself"** firing on real work and catching a wrong method name before it reached a ticket.
- **v0.3.3 — still not done: run one real story end to end.** The work-order, report and change-request shapes remain guesses until something real passes through them, and nothing above changes that. Deliberately a *small* story, so the cost model in `orchestrate-feature` § Step 1 gets measured rather than asserted.
- **v0.4** — thin `build-story`'s body down now that its per-lane knowledge lives in packs; delete rather than deprecate, once a run has proven the packs carry it.
- **v0.5** — enforce the scope fence mechanically (a `PreToolUse` hook checking writes against the current order's `scope`), rather than by asking agents nicely.
- **v0.6** — second project bound, to test whether the agnostic/specific split actually holds.
