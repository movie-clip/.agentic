# Project profile: `portfolio`

Repo: `C:\projects\investments\portfolio` (quant-research-lab)
Bound via `portfolio/.agentic.json`.

Read this in full before any lane work. `CLAUDE.md` at the repo root is the
richer onboarding document and remains authoritative — this profile is the
*agent-facing* summary plus the routing table. When they disagree, `CLAUDE.md`
wins and this file needs updating.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Hard guardrails — no plan or lane may violate these** · **Stack** · **Layout** · **Sources of truth (check before assuming)** · **Mechanical gates — never bypass**

| Section | Read it when |
|---|---|
| What the product is | this is your first order in this repo |
| Delivery model | you are the orchestrator or the producer |
| Phases | you are the orchestrator, at intake |
| Lane routing | you are choosing which lane owns a piece of work |
| Repo skills agents may invoke | your order names a repo skill, or you are the orchestrator |
| Commands | your order names a `verification` command |
| PR convention | your order asks you to open or describe a PR |

---

## What the product is

A local-first, deterministic, auditable decision-support platform for systematic
personal investing. Imports broker portfolios, computes deterministic analytics,
presents holdings analysis under explicit financial guardrails. It is a research
workbench, not a prediction engine — every displayed number must be explainable,
traceable and reproducible.

Three tabs: **Dashboard** (performance), **Exposure** (composition), **Risk**
(pre-decision risk-budget views).

## Hard guardrails — no plan or lane may violate these

1. **Financial accuracy first.** If the math or methodology is wrong, nothing
   else matters. Any change to analytics, a factor formula or trust-state logic
   requires reading `docs/finance/financial-methodology.md` first, and updating
   its tests in the same pass.
2. **Methodology traceability.** Every UI metric maps to one engine formula and
   one code path. Untraceable → do not ship.
3. **Truth-class separation.** Broker truth, snapshot analytics, synthetic
   history and persisted imports are distinct classes. Never mixed in one
   response.
4. **Trust semantics over fabrication.** `verified > degraded > withheld >
   unavailable`. Surface the level; never fill a plausible value; never collapse
   `withheld` into `unavailable`.
5. **No execution.** The system never places trades or moves money.

An order that requires breaking one of these gets `status: REFUSED` naming the
guardrail.

## Stack

| Layer | Tech |
|---|---|
| Desktop | React 18 + TypeScript + Vite, Tauri 2 (Rust shell) |
| Engine | Python FastAPI + Uvicorn + Pydantic |
| Market data | FMP via local cache |
| Tests | Pytest (backend), Vitest (frontend) |

## Layout

```
apps/desktop/src/
  app/                    core state, storage, App shell, primitives
  features/portfolio/     holdings, exposure, diagnostics, dashboard cards
  features/market-data/   market data integration
services/quant-engine/app/
  schemas/                Pydantic models — CONTRACT SOURCE OF TRUTH
  api/routes/             FastAPI routes
  services/               business logic
  analytics/              returns, drawdown, distribution, exposure, risk,
                          attribution, correlation
  clients/                FMP client (with caching)
  domain/                 ledger + accounting model
  importers/              broker parsers (IBKR, Freedom24, ESPP)
  tests/                  pytest suite
docs/
  product/planning.md     how stories/epics/roadmap work - read first
  product/stories/        one file per story (frontmatter carries status)
  product/epics/          optional grouping, one file per epic
  product/ROADMAP.md                 GENERATED index - never hand-edited
  product/current-product-state.md   shipped-state inventory
  finance/financial-methodology.md   formula source of truth
  architecture/                       seams, routes, truth classes
  contracts/<area>-fields.md          backend ↔ TS ↔ UI traceability
```

## Sources of truth (check before assuming)

| Question | Doc |
|---|---|
| How is this computed? | `docs/finance/financial-methodology.md` |
| What is shipped today? | `docs/product/current-product-state.md` |
| What work exists, and what state is it in? | `docs/product/ROADMAP.md` — **generated** from story frontmatter by `scripts/build_roadmap.py`, so it cannot be stale. The rules are in `docs/product/planning.md`. Epics are optional; most stories have none. |
| Where does this field come from? | `docs/contracts/<area>-fields.md` |
| What are the backend seams? | `docs/architecture/system-architecture.md` |
| How does testing actually work? | `docs/architecture/testing-architecture.md` + `capabilities/testing.md` |

## Delivery model

**PRD → User Story → Ticket.** A story is a vertical slice delivering
user-visible value, carrying acceptance criteria, a test plan, and
`T-<epic>.<story>.<n>` tickets. Vertical slice with no ticketed story → the
orchestrator dispatches `story-author` for a draft, then stops for the human to
approve it. The human approves; the network never self-approves a story.

## Phases

`protocol/orchestrator.md` § 2 defines the phases and § 3 the loop that walks
them. This table is the binding: which lane fills each phase **here**, in what
order, and the clause that decides whether it fires at all. The orchestrator
copies it into the run ledger at intake and records a verdict beside every row.

| Phase | # | Lane | Fires when | Human stop |
|---|---|---|---|---|
| ground-truth | 1 | recon | the area is unfamiliar, or the run would otherwise build on an unverified claim — a bug report, a findings doc, a "this number looks wrong" | — |
| framing | 1 | product | the request changes what the product does: a new capability, new scope, or a re-prioritisation | **yes** — the brief is relayed and the verdict is the human's |
| specification | 1 | quant (RESEARCH) | the work introduces or changes a metric, formula, weighting, return basis or trust classification | — |
| specification | 2 | story | framing produced scope that no approved, ticketed story covers, **and** the slice needs ticketing — more than one build lane, a contract crossing, or mathematics | **yes** — the one hard stop |
| design | 1 | design | the change crosses a contract boundary, or more than one build lane touches it | — |
| build | 1..n | backend, frontend, test | anything that edits the repo. One order per lane: contracts before consumers, implementation before tests | — |
| verify | 1 | quant-audit | any lane touched `analytics/`, a formula, a weighting, a return basis or a trust label | — |
| verify | 2 | integration | any build lane was dispatched | — |
| verify | 3 | review | the run carries a story whose acceptance criteria someone must accept | — |
| close | 1 | docs | always — contract notes against `docs/`, and `pack-corrections.md` against `capabilities/` **when a lane emitted one** | — |

### Four orderings that are not negotiable

**`ground-truth` before `framing`.** When both fire, recon's artifact is an
`inputs` on the producer's order. Run the other way round, the producer
establishes the facts itself and recon re-derives them — which is what happened
on `2026-09-09`: the brief's own `risks` block conceded *"'Already covered'
rests on claims I opened myself"*, the scout ran two dispatches later over the
same territory, and it **contradicted the brief** (the Dashboard volatility path
has no 20-observation floor; the brief said it did). Two dispatches, one of them
wrong, and the correction surfaced only because a third lane read both.

**`quant` RESEARCH before `story`.** The research brief is what makes acceptance
criteria groundable. Written the other way round, the story states an outcome
nobody has established is computable, and the contradiction surfaces during
implementation — when three lanes have already built toward it.

**`quant-audit` before `integration`.** A wrong formula can be engineered
flawlessly and satisfy every acceptance criterion, so the other two gates would
both pass it. If the mathematics is wrong, the rest of the review is measuring
the wrong thing. Read its `verification.detail` for **which anchor it checked
against**: an audit that recomputed from the same methodology doc the
implementation was built from is a consistency check, not an independent one.

**`review` last.** It judges the story, not the code, and only once engineering
coherence has passed — so a `FAIL` there is about acceptance rather than
something `integration` would have caught anyway.

### When the brief is the specification

The `story` row's trigger is narrower than `framing`'s on purpose. A slice that
is one build lane, crosses no contract and touches no mathematics does not need
a ticketed story: the delivery brief already states the outcome, the slice
boundary and what is out of scope, and the human approved it at the framing
stop. Record the row as `not triggered (single-lane slice; the delivery brief in
<nn> is the specification)`, and `review` does not fire either — its own clause
asks for a story to accept, and there is none.

The evidence is `2026-09-11`: a story of 28 lines and two tickets, carrying no
contract notes, restating a brief the human had already approved. It was not
wrong. It was a dispatch and a human stop spent re-stating a decision already
made, and the `review` gate that followed judged acceptance criteria written
from that restatement.

**What still fires it, however small the change looks:** anything under
`schemas/`, anything under `analytics/`, anything that adds or removes a field
in `docs/contracts/<area>-fields.md`, and anything two build lanes touch. Those
are the cases where "what does done mean" is a question the brief did not
answer.

### What the gates run

**`integration` runs `python scripts/run_all_tests.py`.** Not the subset the
run happened to touch — the whole suite, every time, whatever the lanes changed.
Write that command into the gate's order, and nothing narrower.

Two reasons, and the second is the one that bites. It is this project's declared
acceptance command, so a gate running something smaller is gating against a
weaker standard than the repo itself applies. And it is the only command that
writes `.claude/.last-test-pass`, which the commit hook checks against every
changed file — so a run whose gate ran `vitest` + `tsc` + `detect_deadcode.py`
ends with three green results, a `PASS` verdict, and work the human cannot
commit until they run the suite themselves. `2026-09-12` ended exactly there.

A build lane's own `verification` is properly narrower: it is checking its own
change, not the run. The gate is where the project's standard applies.

**`quant-audit` runs whatever recomputes the number independently** — named in
its order, and its `verification.detail` says which anchor it checked against.
**`review`** verifies the story's test plan actually ran; the suite is the
evidence, not the claim.

### The short run — what used to be the express route

There is no express route and none is needed: a run where `framing`,
`specification` and `design` all fail their triggers **is** the short run. What
matters is that each false clause is written into the ledger with its reason.

**What makes them false here.** A failing or flaky test (`test` lane). A doc
reconciliation a gate or a contract note already identified (`docs` lane). A
rename or a dead-code removal that `detect_deadcode.py` flags. A defect in
shipped behaviour whose fix sits inside one lane and changes no schema.

**What makes them true, no matter how small it looks.** Anything under
`services/quant-engine/app/schemas/` — that is the contract source of truth, and
the schema hook exists because changes there never stay in one lane, so `design`
fires. Anything under `analytics/` — the quant rows in `specification` and
`verify` both fire, always; mathematics never takes the short route, and that is
guardrail one made operational. Anything that adds or removes a field visible in
`docs/contracts/<area>-fields.md`. Anything a user would describe as a new
capability — `framing` fires and the verdict is the producer's.

**A false clause is re-read every turn, which is what replaces the old
self-voiding rule.** When a build lane returns a contract note, `design`'s
clause has stopped being false: that is a re-plan (`orchestrator.md` § 3), with
a `## Replans` row and a bumped `plan:`, not a route quietly discovering it was
the wrong one.

The short run ends the same way as the long one: `python scripts/run_all_tests.py`,
green, then the human commits. Skipping phases never skips verification.

## Lane routing

| Lane | Agent | Pack | Owns |
|---|---|---|---|
| product | `producer` | `product.md` | roadmap placement, epic/story shaping, sequencing |
| quant | `quant-analyst` (RESEARCH) | `quant.md` | research brief: formulas, grounding, trust-class analysis |
| story | `story-author` | `story.md` | drafts the ticketed story |
| recon | `scout` | — | read-only exploration |
| design | `tech-lead` (DESIGN) | `architecture.md` | the contract, reuse, lane split |
| backend | `backend-engineer` | `backend.md` | `services/quant-engine/app/**` (non-test) |
| frontend | `frontend-engineer` | `frontend.md` | `apps/desktop/src/**` (non-test) |
| test | `test-engineer` | `testing.md` | `app/tests/**`, `src/**/*.test.{ts,tsx}`, `src/test/**` |
| docs | `docs-engineer` | `docs.md` | `docs/**`, and — at close-out only — `<agenticRoot>/projects/portfolio/capabilities/**` when applying `pack-corrections.md` |
| quant-audit | `quant-analyst` (AUDIT) | `quant.md` | **financial gate**: independently recomputes, checks trust honesty |
| integration | `tech-lead` (INTEGRATION) | `architecture.md` | engineering gate: PASS / CHANGES_REQUESTED |
| review | `reviewer` | — | acceptance gate: PASS / FAIL |

All **ten** roles are live (`plugins/agentic-core/agents/` is the authority on
that count). This table says what each lane **owns**; § Phases says when it
fires. Three gates, each checking something the others cannot see:
`quant-analyst` gates the mathematics, `tech-lead` gates engineering coherence,
`reviewer` gates acceptance against the story.

## Repo skills agents may invoke

These live in `portfolio/.claude/skills/` and stay there. Agents read them as
reference; they are not replaced by this network.

| Skill | Who reaches for it |
|---|---|
| `write-tests` | `test-engineer` (its content is mirrored into `capabilities/testing.md`) |
| `ui-polish` | `frontend-engineer` — mandatory for any card work; a design-system audit test enforces it |
| `fmp-data` | any lane touching market data, symbol resolution or the cache |
| `quant-research` | `quant-analyst` in RESEARCH mode (its brief template is mirrored into `capabilities/quant.md`) |
| `write-story` | `story-author` — for its drafting conventions only; its workflow (roadmap edits, epic placement, `build-story` handoff) is superseded by this network |
| `verify-story` | `reviewer` (its checklist becomes the gate) |
| `update-docs` | `docs-engineer` |
| `build-story` | **nobody. Superseded — do not invoke.** See below. |

### `build-story` is superseded and must not run

`build-story` implements the old linear pipeline: it works tickets in order in
one context, self-invokes `write-tests` / `verify-story` / `update-docs`, and
**commits**. Every one of those is now owned by a lane or by the human.

The repo skill's own description (`.claude/skills/build-story/SKILL.md`
frontmatter) now opens "SUPERSEDED - do not use for implementation" and
explicitly routes "build US-X.Y" / "pick up ticket T-..." / "implement the
next story" to `orchestrate-feature`, so the trigger collision is closed at
the skill itself. The residual prose that once told agents to run `build-story`
lived in `docs/product/stories/README.md` and `docs/product/prd/README.md`,
both deleted at commit `ce9c97d`, so the collision is now closed both at the
skill and across the repo docs.

**If `build-story` loads for a request that belongs to this network, stop and
route to `orchestrate-feature` instead.** A slice built through it has no run
ledger, no gate verdicts, no contract notes, and ends with an agent commit.

## Commands

```bash
python scripts/run_dev.py           # both dev servers (:8000 / :5173)
python scripts/run_all_tests.py     # canonical full suite — the gate
cd services/quant-engine && pytest  # backend only
cd apps/desktop && npx vitest run   # frontend only
cd apps/desktop && npx tsc --noEmit # type-check
python scripts/detect_deadcode.py --strict   # dead-code gate
python scripts/manage_cache.py      # FMP cache
```

## Mechanical gates — never bypass

- **CI** runs `run_all_tests.py` on every PR and push to `main`. Network-free.
- **Commit gate hook** — enforced at two layers, both checking the same
  thing (`.claude/.last-test-pass` exists and is fresher than every changed
  non-`.md` file, written only by a fully green suite run). The **git-level**
  `scripts/githooks/pre-commit` (wired via `git config core.hooksPath
  scripts/githooks`, execing `scripts/hooks/git_pre_commit.py`) is the actual
  enforcement boundary — it fires on every `git commit` regardless of which
  tool or terminal invoked git, since it runs inside git itself rather than
  inside a tool's interception layer. `core.hooksPath` is local git config,
  not committed; `scripts/run_all_tests.py` idempotently sets it early in
  every run, so a dev/agent session that has run the suite at least once has
  it wired — a clone that has never run the suite yet does not. The
  **Claude Code** `scripts/hooks/pre_commit_gate.py` (PreToolUse, matched on
  `Bash` only) remains as a faster-feedback duplicate inside agent sessions,
  not the boundary itself. **A blocked commit means re-run the suite — never
  work around either hook.**
- **Schema hook** (`schema_edit_reminder.py`, PostToolUse) fires after edits
  under `app/schemas/`, reminding that TS types and
  `docs/contracts/<area>-fields.md` must change in the same pass.
- **Dead-code gate** is enforced inside `run_all_tests.py` (ruff + vulture +
  knip, zero findings, plus `tsc --noEmit`). New dead code fails the suite.
- **No agent commits.** The human runs the suite and commits.

## PR convention

`.github/PULL_REQUEST_TEMPLATE.md` structures PRs around the story: story ID, AC
checklist, contracts/methodology checklist, verify verdict. GitHub only
auto-fills it in the web UI — with `gh pr create`, pass it explicitly via
`--body-file`.
