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
orchestrator stops and asks for `write-story` first.

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
| docs | `docs-engineer` | `docs.md` | `docs/**` |
| quant-audit | `quant-analyst` (AUDIT) | `quant.md` | **financial gate**: independently recomputes, checks trust honesty |
| integration | `tech-lead` (INTEGRATION) | `architecture.md` | engineering gate: PASS / CHANGES_REQUESTED |
| review | `reviewer` | — | acceptance gate: PASS / FAIL |

All ten roles are live. Three gates, each checking something the others cannot
see: `quant-analyst` gates the mathematics, `tech-lead` gates engineering
coherence, `reviewer` gates acceptance against the story.

**Any change touching `analytics/`, a formula, a weighting, a return basis, or a
trust classification must go through the quant lane** — in research mode before,
audit mode after. That is guardrail one made operational.

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
- **Commit gate hook** (`scripts/hooks/pre_commit_gate.py`, PreToolUse) blocks
  `git commit` unless `.claude/.last-test-pass` exists and is fresher than every
  changed non-`.md` file. Only a fully green suite writes that marker. **A
  blocked commit means re-run the suite — never work around the hook.**
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
