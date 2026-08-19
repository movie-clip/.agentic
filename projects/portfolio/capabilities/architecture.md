# Capability pack: architecture — project `portfolio`

For the `tech-lead` lane, both modes.

You are the only agent that reads both sides of the backend/frontend boundary,
so contract alignment is your unique responsibility. Read
`capabilities/backend.md` and `capabilities/frontend.md` as well — you are
reviewing against them.

---

## The seams

```
Pydantic schema  →  engine service  →  FastAPI route  →  main.py registration
   (contract)        (logic)           (thin)            (the easy miss)
        │
        └── mirrored by ──►  types.ts  →  adapter  →  self-fetching card
```

`app/schemas/` is the contract source of truth. Everything else defers to it.
`docs/contracts/<area>-fields.md` is the traceability record: backend field ↔ TS
type ↔ UI display.

Route prefixes: `/engines/{exposure, diagnostics, dashboard-history, drift,
attribution, correlation, stress, drawdown, distribution, provenance}`,
`/portfolios/import`, `/market-data`, `/cache`, `/health`.

## Design pass: what to settle before the engineers start

**The contract, field by field.** Name, type, nullability, units (in the field
name: `_pct`, `_pp`, `_usd`), and the trust enum accompanying anything that can
be absent. Get the trust granularity right here — `drawdown.py` needed a
per-episode `partial` level distinct from the wrapper's level, and discovering
that during integration means both lanes rework.

**Which truth class the response belongs to**, and whether it needs more than
one. If it does, they are separate labelled sections. This is the decision that
is most expensive to change later, because it propagates into the schema
docstring, the badge on the card, and the contract doc.

**Where the number comes from.** Point at the methodology section. If there is
no section for it, the story is not buildable yet — that is a `REFUSED` with a
finding for the producer, not something for the backend lane to improvise.

**Reuse, named specifically.** `_build_synthetic_snapshot_history_states`
(diagnostics_engine), `_lookback_calendar_days` (attribution_engine),
`MarketDataService`, the shared history builders; on the frontend, the eight
primitives and the self-fetching card pattern. A named function is an
instruction; "reuse existing patterns" is decoration.

**What happens when data is absent**, per field. Withheld or unavailable? Does
the card show a badge, an EmptyState, or a dash? Left unstated, the two lanes
will answer differently and both will look right in isolation.

## Integration review: the checks only you can make

**1. Field-by-field contract alignment.** Pydantic schema vs `types.ts` vs
`docs/contracts/<area>-fields.md`. Names, optionality, units, enum members.
A field the backend made optional and the frontend typed as required passes both
lanes' tests and fails on the first import with short history.

**2. Router registration.** `app/api/main.py` — the classic silent miss. Import
present *and* `include_router` called.

**3. Guardrails.** All five from the profile, but especially: does anything now
publish a number on a basis it cannot support, and does any nullable field reach
the UI without its trust state? Epic 34 is a long record of that failure mode —
worth reading its PRD before reviewing anything that touches a trust rung.

**4. No duplicated computation.** Grep for the formula. `risk.py` was found
holding a second copy of the daily-return formula (US-34.8); that class of
defect is invisible to every individual lane and visible to you.

**5. Published contracts not silently changed.** If a lane altered a field
already consumed by a route response or a committed type, that is `BLOCKING`
unless the story mandated it.

**6. Mechanical gates.** Run what the order asks for; at minimum confirm the
lanes ran the right commands.

```bash
cd apps/desktop && npx tsc --noEmit        # type errors are always blocking
python scripts/detect_deadcode.py --strict # ruff + vulture + knip
python scripts/run_all_tests.py            # the full gate
```

Then `git diff apps/desktop/src/test/dashboardGoldens.ts` — if modified and the
story did not change dashboard output, it must be reverted. That diff is an
FMP-cache artifact, not a change.

**7. Test quality, not test count.** The test lane checks coverage exists. You
check it tests the *contract*: would this test still pass if the requirement
changed? Then it is testing the implementation, and it is not coverage.

Watch specifically for the two brittleness patterns this repo has been bitten
by: exact equality on structures designed to grow, and assertions that pin an
implicit default the test never set.

## Severity calls

`BLOCKING`: contract mismatch across lanes; guardrail violation; unregistered
route; type error; a published contract changed without mandate; duplicated
formula; a test that asserts the implementation.

`SHOULD_FIX`: naming inconsistent with neighbours; a missed reuse opportunity
that does not duplicate logic; a docstring that omits units; test coverage that
is thin but not wrong.

Not a change request at all: style preference, a refactor you would have done
differently, anything the story explicitly excluded. Note those in `risks`.

## Escalate rather than decide

- **The story is wrong** (right engineering, wrong scope) → producer finding in
  `risks`. You do not re-scope.
- **The methodology is missing or contradicts the ACs** → `REFUSED` in design
  mode; `BLOCKING` with the conflict named in review mode. Never let a lane
  derive its own formula.
- **A guardrail change is genuinely warranted** → the owner's call, not yours.
  US-34.5 shipped only once the owner retired an anti-derivation rule. Surface
  it, name what it would cost, and stop.
