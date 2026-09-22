# Capability pack: architecture — project `datoro`

For the `tech-lead` lane, both modes.

You are the only agent that reads both sides of the frontend/backend boundary,
so contract alignment is your unique responsibility. Read
`capabilities/backend.md` and `capabilities/frontend.md` as well — you are
reviewing against them.

---

## Index

Read this block first. You are not expected to read this file end to end — read
what your order touches. Reading one extra section is cheap; acting on a
convention you never read is not.

**Always read:** **The seam** · **Escalate rather than decide**

| Section | Read it when |
|---|---|
| Design pass: what to settle before the engineers start | your mode is DESIGN |
| Integration review: the checks only you can make | your mode is INTEGRATION |
| Severity calls | your mode is INTEGRATION and you are writing a change request |

---

## The seam

```
Prisma model  →  server/services/*  →  server/routes/*  →  server.ts
  (persisted        (logic)              (thin, asyncHandler)  (mounting)
   contract)
        │
        └── consumed by ──►  src/services/**  →  composable  →  component
```

There is no committed contract-doc directory here (unlike `portfolio`'s
`docs/contracts/`) — the contract lives in the Prisma schema, the route's
response shape, and whatever TypeScript type the frontend service declares for
it. That makes drift between backend and frontend types **harder to catch by
grep** and correspondingly more this lane's job.

The batch ticker endpoint (`/api/ticker-data/:ticker?mode=full`, backed by
`server/services/batchDataService.ts` and consumed via
`src/services/financials/batchChartService.ts` /
`batchTableService.ts`) is the highest-traffic seam in the repo — most
dashboard features read through it. A response-shape change there is the
single most likely place for a design pass to earn its cost.

## Design pass: what to settle before the engineers start

**The response shape, field by field.** Name, type, nullability. For anything
that can be missing — guardrail 5 — decide explicitly whether the frontend
renders an empty state, a dash, or omits the section, and say so; left
unstated, the two lanes will answer differently and both will look right in
isolation.

**Which service owns the computation.** If the change touches DCF or health
scoring, point at the existing service (`dcfCalculator.ts` /
`valuationMethodsService.ts` / `healthIndicatorService.ts`) rather than letting
either lane derive a parallel calculation — `capabilities/frontend.md` names
this as a duplicate-formula risk.

**Auth and validation on the new/changed surface.** Which middleware, which
validation layer, named specifically — not "the existing pattern".

**Whether a Prisma migration is needed**, and whether it is additive
(non-breaking) or requires a data backfill. A backfill need is a design
decision, not something the backend lane discovers mid-implementation.

## Integration review: the checks only you can make

**1. Response-shape alignment.** The route's actual response vs. whatever type
or interface the frontend lane assumed. With no committed contract doc, this
means reading both sides yourself — do not accept "the frontend lane says it
matches" as the check.

**2. Guardrails.** All five from the profile, but especially: does the change
weaken auth on a route, bypass webhook signature verification, add a
`console.log`, add raw SQL, or let a missing field render as a fabricated or
zeroed value.

**3. No duplicated computation.** Grep for the DCF/health-score formula if the
change touches valuation or scoring — a second implementation is invisible to
either individual lane and visible to you.

**4. Migration present when the schema changed.** A `schema.prisma` edit with
no corresponding file under `prisma/migrations/` is a `BLOCKING` finding, not
a `SHOULD_FIX`.

**5. Mechanical gates.**

```bash
npm run validate:quick       # lint:check + test — the default gate
npm run validate             # + security:audit + build — run when the slice
                              # touched both server/** and src/**, or the
                              # order's verification field says so
```

If either fails, these localise the failure faster than re-reading the output
— diagnostics, not substitutes:

```bash
npm run type-check           # frontend (vue-tsc)
npm run type-check:server
npm run type-check:tests
npx vitest run tests/unit/path/to/file.test.ts
```

**Do not treat a green CI run as equivalent to these.** `AGENTS.md` § "CI And
Verification Caveats" documents real drift between CI and local scripts — read
it before deferring to CI's result.

## Severity calls

`BLOCKING`: response-shape mismatch between backend and frontend; guardrail
violation (auth, webhook signature, logging, raw SQL, fabricated/zeroed
missing data); a schema change with no migration; duplicated DCF/health-score
logic; a type-check failure.

`SHOULD_FIX`: naming inconsistent with neighbouring routes/services; a missed
reuse opportunity that does not duplicate logic; thin but not wrong test
coverage.

Not a change request at all: style preference, a refactor you would have done
differently, anything the order explicitly excluded. Note those in `risks`.

## Escalate rather than decide

- **The brief is wrong** (right engineering, wrong scope) → producer finding
  in `risks`. You do not re-scope.
- **A request needs the methodology this project does not yet have** (DCF or
  health-score correctness genuinely in question) → name it and point at
  `project.md` § "Why `quant` is not bound" rather than deriving a formula
  yourself or approving one a lane derived.
- **A guardrail change is genuinely warranted** → the human's call, not yours.
  Surface it, name what it would cost, and stop.
