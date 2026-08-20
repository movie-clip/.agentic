# Project profile: `portfolio`

Repo: `C:\projects\investments\portfolio` (quant-research-lab)
Bound via `portfolio/.agentic.json`.

Read this in full before any lane work. `CLAUDE.md` at the repo root is the
richer onboarding document and remains authoritative — this profile is the
*agent-facing* summary plus the routing table. When they disagree, `CLAUDE.md`
wins and this file needs updating.

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
  product/prd/            one PRD per epic
  product/stories/        one file per story
  product/epic-roadmap.md            epic snapshot + slice log
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
| Which epic is current? | `docs/product/epic-roadmap.md` — **the authority**; PRD pointers in CLAUDE.md go stale |
| Where does this field come from? | `docs/contracts/<area>-fields.md` |
| What are the backend seams? | `docs/architecture/system-architecture.md` |
| How does testing actually work? | `docs/architecture/testing-architecture.md` + `capabilities/testing.md` |

## Delivery model

**PRD → User Story → Ticket.** A story is a vertical slice delivering
user-visible value, carrying acceptance criteria, a test plan, and
`T-<epic>.<story>.<n>` tickets. Vertical slice with no ticketed story → the
orchestrator dispatches `story-author` for a draft, then stops for the human to
approve it. The human approves; the network never self-approves a story.

## Lane routing

| Lane | Agent | Pack | Owns |
|---|---|---|---|
| product | `producer` | `product.md` | roadmap placement, epic/story shaping, sequencing. **Entry point.** |
| quant | `quant-analyst` (RESEARCH) | `quant.md` | research brief: formulas, grounding, trust-class analysis |
| story | `story-author` | `story.md` | drafts the ticketed story. **Human approves before dispatch.** |
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
that count). Three gates, each checking something the others cannot see:
`quant-analyst` gates the mathematics, `tech-lead` gates engineering coherence,
`reviewer` gates acceptance against the story.

**Any change touching `analytics/`, a formula, a weighting, a return basis, or a
trust classification must go through the quant lane** — in research mode before,
audit mode after. That is guardrail one made operational. It is also the
hardest express-lane disqualifier: mathematics never takes the short route.

### The express lane in this repo

`orchestrate-feature` § "The express lane" defines the gate. What it means here:

**Eligible.** A failing or flaky test (`test` lane). A doc reconciliation the
reviewer or a contract note already identified (`docs` lane). A rename or a
dead-code removal that `detect_deadcode.py` flags. A defect in shipped behaviour
whose fix is inside one lane and changes no schema.

**Not eligible, no matter how small it looks.** Anything under
`services/quant-engine/app/schemas/` — that is the contract source of truth and
the schema hook exists because changes there never stay in one lane. Anything
under `analytics/`. Anything that adds or removes a field visible in
`docs/contracts/<area>-fields.md`. Anything a user would see as new.

Express still ends the same way: `python scripts/run_all_tests.py`, green, then
the human commits. The short route skips planning, never verification.

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

Its description still triggers on *"build US-X.Y"*, *"pick up ticket T-..."*,
*"implement the next story"* — the same phrasing that should reach
`orchestrate-feature`. Until its description is narrowed in the repo, two
architectures compete for the same request and which one answers is a coin flip.

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
- **Commit gate hook** — today, only the **Claude Code**
  `scripts/hooks/pre_commit_gate.py` exists (PreToolUse, matched on `Bash`
  only). It checks that `.claude/.last-test-pass` exists and is fresher than
  every changed non-`.md` file, written only by a fully green suite run. It
  does not fire for a `git commit` issued through a non-Bash tool (e.g.
  PowerShell) — there is no equivalent enforcement at the git level in this
  repo. That gap is **open**, tracked under Epic 36 (F-R1). **A blocked commit
  means re-run the suite — never work around the hook.**
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
