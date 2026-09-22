# Project profile: `datoro`

Repo: `C:\projects\investments\datoro` (Datoro)
Bound via `datoro/.agentic.json`.

**`CLAUDE.md` is already in your context.** Claude Code loads the repo's
`CLAUDE.md` into every dispatched lane at startup, so the product surface, the
stack, the directory layout, the canonical-doc map and the command list reach
you without a read. Treat it as read, and go to it for anything about the code
this file does not carry. (If it is genuinely not in your context, read it —
that is the one case where it is worth a tool call.)

`datoro/AGENTS.md` is a second, deeper source on house style — imports, naming,
error handling, CI caveats — written before this network existed. It is not
superseded; `CLAUDE.md` points to it and this pack does not repeat it.

This file carries what `CLAUDE.md` does not: the lane map, the **numbering** a
`REFUSED` cites, and the friction the repo docs do not record. Phase bindings
live in `phases.md`, which the orchestrator reads at intake and no specialist
lane needs.

**This profile is new.** It is grounded in what `AGENTS.md`, the README and the
repo layout actually establish — not in hard-won incident history the way
`portfolio`'s packs are, because none has accumulated here yet. Expect thinner
gotcha sections than a mature project's packs, and expect `pack_corrections`
to do real work over the first several runs. `protocol/packs.md` is the loop
that closes that gap; use it rather than treating the current thinness as a
finding.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **Hard guardrails — no plan or lane may violate these** · **Mechanical gates — never bypass**

| Section | Read it when |
|---|---|
| Delivery model | you are the producer, or shaping a request into work |
| Lane routing | you are choosing which lane owns a piece of work |
| Why `quant` is not bound | you are about to propose a mathematics gate, or a request touches DCF/health-score correctness |
| Reference | you are a recon or product order checking whether something was already flagged |

Elsewhere: **`phases.md`** — which lane fills each phase and the clause that
fires it (orchestrator, at intake). **`CLAUDE.md`** — product, stack, layout,
canonical docs, commands (already in your context).

---

## Hard guardrails — no plan or lane may violate these

1. **Auth boundary.** Protected routes use `authenticate()` /
   `requireAuth`-style middleware from `server/middleware/auth.ts`. Never
   weaken or bypass it to unblock a feature.
2. **Stripe webhook integrity.** Subscription and payment state changes only
   follow a webhook whose signature `constructWebhookEvent`
   (`server/services/stripeService.ts`) has verified. Never process an
   unverified event body.
3. **No secrets or PII in logs.** Backend logging goes through
   `server/services/logger.ts`, never `console.log`. Never log tokens, JWTs,
   card data, or emails in plaintext.
4. **Prisma is the DB access layer.** No raw SQL without a documented existing
   exception. Schema changes go through `prisma/migrations`.
5. **External data is validated and degrades honestly.** FMP/market responses
   are validated at the boundary (Zod/Joi) before use. Missing or partial
   financial data is surfaced as missing — never fabricated, never silently
   zeroed.

An order that requires breaking one of these gets `status: REFUSED` naming the
guardrail. **This is the system's only numbered copy** — `CLAUDE.md` restates
the same five unnumbered, so a session working the repo outside the network
still sees them and a cited number still resolves to exactly one rule.

## Delivery model

**Request → change.** There is no PRD or epic tree in this repo (no
`docs/product/` corpus) — the backlog is whatever the human asks for next, plus
what `docs/PROJECT_REVIEW_PLAYBOOK.md` and `docs/reviews/` surface.

A ticketed story is the exception, not the rule, the same way it is in
`tradingview`. One endpoint, one component, one behaviour change — the delivery
brief is the specification and `story` does not fire. What earns a story: a
change that crosses more than one lane's contract **and** has no approved brief
already covering it, or a change to a route or a Prisma model already relied on
by shipped frontend code, where "what breaks for existing users" is a question
the brief did not answer. `phases.md` § "When the brief is the specification"
carries the exact clause.

## Lane routing

| Lane | Agent | Pack | Owns |
|---|---|---|---|
| recon | `scout` | — | read-only exploration: which route/component/service already does this |
| product | `producer` | `product.md` | which change this is, whether it is already covered, where "no" lives |
| story | `story-author` | — | drafts a ticketed story on the rare slice that needs one |
| design | `tech-lead` (DESIGN) | `architecture.md` | the frontend/backend contract, reuse, the lane split |
| backend | `backend-engineer` | `backend.md` | `server/**`, `prisma/**` (non-test) |
| frontend | `frontend-engineer` | `frontend.md` | `src/**` (non-test) |
| test | `test-engineer` | `testing.md` | `tests/**` |
| docs | `docs-engineer` | `docs.md` | `docs/**`, and — at close-out only — `<agenticRoot>/projects/datoro/capabilities/**` when applying `pack-corrections.md` |
| integration | `tech-lead` (INTEGRATION) | `architecture.md` | engineering gate: PASS / CHANGES_REQUESTED |
| review | `reviewer` | — | acceptance gate: PASS / FAIL — only where a story exists |
| protocol-lint | `protocol-linter` | — | **authoring gate**: network files under `<agenticRoot>` against `protocol/authoring.md`. Not a delivery phase — see below |

**No project tool server.** `datoro/.mcp.json` does not exist, so no
`mcp__project__*` tools are granted here. Every lane runs the plain `npm`/`npx`
commands `CLAUDE.md` and the capability packs name, under `Bash`. If this repo
grows one later, `protocol/authoring.md` § "The project tool server" and §
"Adding a project" are what to read before wiring it.

## Why `quant` is not bound

`src/services/dcf/**` and `src/services/health/**` compute real financial
outputs (DCF valuation, a health score) shown to users, which is the kind of
substance the `quantitative-researcher` lane exists to gate elsewhere in this
network. It is not bound here because, unlike `portfolio`, this repo has no
methodology doc, no trust-class taxonomy and no formula-traceability
convention for the lane to gate *against* — binding the lane today would mean
inventing that apparatus from the `.agentic` side, which is a producer/domain
decision for a human working the repo, not network wiring.

**Treat this as deferred, not decided.** If DCF or health-score correctness
becomes a live concern, the right first step is a `quant` RESEARCH brief that
proposes the methodology doc this project does not yet have — not silently
trusting `dcfCalculator.ts` / `healthIndicatorService.ts`, and not a lane
inventing a formula on its own authority. Until then, changes to those services
route through `backend`/`frontend` like any other service, and their tests are
the only check.

Three gates, not four, therefore apply here: `integration`, `review` when a
story exists, and `protocol-lint` on an authoring order. `phases.md`'s `verify`
rows are the authority `check_report.py` reads.

## Mechanical gates — never bypass

- **`npm run validate:quick`** (`lint:check` + `test`) is the fast local gate;
  `npm run validate` (+ `security:audit` + `build`) is the fuller one. Neither
  is CI, and `AGENTS.md` § "CI And Verification Caveats" documents real drift
  between what CI runs and what these scripts run — read it before treating a
  green CI run as equivalent to a local one.
- **`prepush` runs `validate:quick`** via a git hook path already wired in this
  repo (`package.json`'s `prepush` script) — a lane does not need to invoke it
  separately, but must not rely on it silently catching what its own
  `verification` command should have caught.
- **No agent commits.** The human commits.

## Reference

`datoro/docs/PROJECT_REVIEW_PLAYBOOK.md` and `datoro/docs/reviews/` hold this
project's own recurring-review history, predating this network. A `recon` or
`product` order investigating whether something was already flagged should
check there before treating a finding as new.
