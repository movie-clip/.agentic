REPORT 2026-08-31-probe-engine-hardening/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only reference + draft artifact; work order verification field is NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - draft path: C:\projects\investments\.agentic\runs\2026-08-31-probe-engine-hardening\02-stories.md — two story drafts for human approval, NOT approved stories
  - US-43.1 (F-1/F-2/F-3, tools/probing.py) tickets: T-43.1.1 shape-aware envelope · T-43.1.2 bounded body + fields= · T-43.1.3 allow_unmocked gating · T-43.1.4 tests · T-43.1.5 capability-pack docs (close-out)
  - US-43.2 (F-4/F-5, tools/testing.py) tickets: T-43.2.1 per-scope subprocess timeouts · T-43.2.2 reset_goldens records discard · T-43.2.3 tests · T-43.2.4 capability-pack docs (close-out)
  - open decision, NOT human-blocking: F-1 ticket breakdown and the source of the "matched request-model name" (route introspection vs maintained table) is a tech-lead DESIGN call; T-43.1.1 may split there — flagged in both § Open decisions and the story body
  - resolved context: no docs/product/ artifact — tracked as .agentic-internal tech debt per owner; no PRD, roadmap entry, docs/product/stories file or story-index edit; drafts live only in this file
  - both stories state the MCP transport/handshake CANNOT be verified this run (needs a fresh interactive session) and is out of scope
  - verification for both stories: `SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q` from services/quant-engine; the full `run_all_tests.py` run and the commit stay with the human, not a ticket

risks:
  - The "~14 engine routes" count and the three-shape taxonomy (flat / snapshot-wrapped / bare-snapshot) are taken verbatim from run.md § request; I did not enumerate the routes under app/api/routes/ or verify the count.
  - The drawdown probe measurement (34,135 chars / ~8,500 tokens, mostly the underwater series) is taken as current; the F-2 ACs reference it as prior context, not as a target number to hit.
  - The F-1 "matched request-model name" AC describes observable output, but whether a request model can be recovered by route introspection at all is a tech-lead DESIGN question; if it needs a hand-maintained table, that AC may need softening. Flagged to DESIGN.
  - F-1 bundles three behaviours into US-43.1 on the producer's confirmed two-story split; if DESIGN finds the request-model mapping heavy enough to stand alone, US-43.1 may split. Expected, not a defect.
  - Capability-pack documentation (T-43.1.5 / T-43.2.4) is written as a close-out docs-lane task because the work order's non-goal forbids me touching the packs now while its DoD requires the new args be pack-documented. If the owner wants that reconciled differently, those tickets are where to say so.

## Orchestrator brief
- Draft only. Two stories for human approval before any DESIGN dispatch; nothing here is an approved story.
- Decision: two-story split kept exactly as the producer confirmed — US-43.1 (F-1/F-2/F-3, tools/probing.py), US-43.2 (F-4/F-5, tools/testing.py). Not merged, not split further.
- Decision: no docs/product/ artifact — tracked as .agentic-internal tech debt per owner; no PRD, roadmap, story-index or docs/product/stories file. Drafts live only in this file.
- Carried forward (not human-blocking): F-1 ticket breakdown and the source of the "matched request-model name" is a tech-lead DESIGN call; US-43.1's ticket list may be revised there.
- Both stories state the MCP transport/handshake cannot be verified this run (needs a fresh interactive session) and is out of scope.
- Lane split per story: backend (probing.py / testing.py) then test; capability-pack docs at close-out by the docs lane. No frontend, no schema change, no quant lane.
- Verification for both: `SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q` from services/quant-engine.
- Sequence: US-43.1 first (risk-carrier — shape taxonomy across the engine routes is where the plan is most likely to prove wrong); US-43.2 parallel or second, hard-independent.
- Sections below: § US-43.1 (story, ACs by finding, test plan, tickets) · § US-43.2 (same) · § Open decisions · § Assumptions carried.
- Blocks dispatch: none beyond human approval of the drafts.

---

# Draft for human review

Neither story below is approved. They are drafts produced from
`01-delivery-brief.md` and `run.md` for a human approval pass and a subsequent
tech-lead DESIGN pass. They are deliberately **not** filed under
`docs/product/` — per the owner decision recorded in `run.md`, the
`probe_engine` / suite-runner hardening bundle is tracked as `.agentic`-internal
tech debt, not a product epic. No PRD, no roadmap entry, no
`docs/product/stories/` file, no story-index edit. The `US-43.x` / `T-43.x.n`
identifiers are used for internal reference only; final register placement is
the docs lane's call at close-out (`docs/tech-debt-register.md`).

The ACs describe observable tool behaviour. They do **not** specify return-dict
keys, helper-function names, the shape-taxonomy mechanism, or any schema — those
are the tech-lead DESIGN pass. Argument names that already appear in `run.md`
as required (`allow_unmocked`, `fields`, `timeout`) are named because they are
the tool's caller-facing interface, not internal structure.

---

## US-43.1 — `probe_engine` stops confirming a probe that answered nothing

**Scope of code:** `services/quant-engine/app/mcp_server/tools/probing.py`
(`probe_engine_impl`, `engine_module_for`, and helpers they call). `server.py`
stays a thin wrapper.
**Status:** Backlog (draft — not filed under `docs/product/`).
**Closes:** F-1, F-2, F-3 (`run.md` § request).
**Verification:** `SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q` from `services/quant-engine`.

### Story

As a **lane using `probe_engine` to check an engine route in-process**, I want
the tool's success signal to mean "the route actually answered" — not merely
"an HTTP response came back" — so that I can act on the probe result without
re-reading every body by hand to find out whether the probe was real.

### Context

`probe_engine_impl` today returns `ok = status_code < 400` and nothing else
about whether the response carried an answer. Three measured ways it hands a
lane a confidently wrong result:

- **F-1 — `ok: true` on a probe that answered nothing.** The tool never inspects
  the payload it sent against the shape the route expects (across the engine
  routes there are three request-body shapes: a flat body, a snapshot-wrapped
  body, and a bare snapshot). A mismatched payload can still yield a 2xx with an
  empty or default body. A body carrying `trust: "unavailable"` is likewise
  reported `ok: true`.
- **F-2 — unbounded response.** A drawdown probe over a ~750-day history was
  measured at 34,135 characters / ~8,500 tokens, almost all of it the underwater
  series. The whole body lands in the calling lane's context window.
- **F-3 — non-engine routes run live and unmocked.** `engine_module_for` returns
  `None` for non-`/engines/` routes (imports, cache, market-data, health); the
  probe then uses `nullcontext()` and runs the route with **no market-data
  mock** — against a live FMP client, with no pytest `--disable-socket` guard in
  effect. A typo in an explicitly-passed engine name falls into the same path.

The `.agentic` capability packs (backend / quant / testing) already carry, as of
v0.5.5, the route-to-shape table, the "read trust before believing a 200" rule
and the context-cost warning. This story makes the tool's behaviour match that
guidance.

### Acceptance criteria

**F-1 — the success signal means the route answered**

- [ ] AC-F1.1 — For a probe against an engine route, the result reports which of
  the recognised request-body shapes the route expected (flat body /
  snapshot-wrapped body / bare snapshot) and the request model that shape
  corresponds to.
- [ ] AC-F1.2 — When the payload the caller supplied does not match the shape
  the route expects, the result carries a warning that names the mismatch
  (shape expected vs shape supplied). The probe still returns the route's actual
  HTTP response — a mismatch warns, it does not raise and does not suppress the
  body.
- [ ] AC-F1.3 — A route whose expected request shape matches none of the three
  recognised forms is disclosed in the result as unclassified, so the caller can
  tell the tool did not categorise it rather than assuming it silently picked
  one.
- [ ] AC-F1.4 — A probe whose response body carries a trust level of
  `"unavailable"` is **not** reported as `ok`, even when the HTTP status is
  `< 400`. The result makes the reason discoverable (the trust value that
  downgraded it).
- [ ] AC-F1.5 — A probe whose body carries a trust level of `verified` or
  `degraded` and whose HTTP status is `< 400` is still reported as `ok` —
  the change narrows `ok`, it does not collapse `degraded`/`withheld` into
  not-ok.
- [ ] AC-F1.6 — Each of the three recognised request shapes is exercised by at
  least one real engine route in the result: a flat-body route, a
  snapshot-wrapped route, and a bare-snapshot route each get their shape
  correctly identified.

**F-2 — the response is bounded**

- [ ] AC-F2.1 — When the response body contains a long array, the result
  truncates it to a bounded number of head and tail elements, preserving their
  original order (first N, last N).
- [ ] AC-F2.2 — A truncated array reports its original element count and carries
  a self-describing marker in place of the elided middle: a reader can tell
  truncation happened, how many elements were dropped, and that the `probe_engine`
  tool did it rather than the route.
- [ ] AC-F2.3 — An array short enough not to need truncation is returned whole,
  with no marker. An empty array and a `null` body are returned as empty / null,
  not as a truncation marker.
- [ ] AC-F2.4 — `probe_engine` accepts a `fields=` argument naming which
  response fields to keep; when supplied, the result carries only those fields
  plus enough of the envelope to stay interpretable. When omitted, the result is
  the bounded-but-otherwise-complete body.
- [ ] AC-F2.5 — A drawdown probe over a multi-year synthetic history (the case
  measured at ~34k characters, dominated by the underwater series) returns a
  result whose underwater series is truncated head/tail per AC-F2.1–F2.2, so the
  result is materially smaller than the untruncated body.

**F-3 — non-derivable routes fail safe, not live**

- [ ] AC-F3.1 — A probe against a route whose engine module cannot be derived
  (non-`/engines/` routes) with no explicit `engine_module` given is **refused
  by default**: the route is not run, nothing goes live/unmocked, and the
  refusal message names the `allow_unmocked` argument as the override.
- [ ] AC-F3.2 — With `allow_unmocked=True`, the same probe proceeds and runs
  without a market-data mock; the result discloses that it ran unmocked.
- [ ] AC-F3.3 — A probe given an explicit `engine_module` that does not resolve
  (a typo'd engine name) still fails loudly, with an error naming the module
  that could not be imported. It is not silently downgraded to an unmocked run.
- [ ] AC-F3.4 — A probe against a normal `/engines/<name>/` route is unaffected:
  no flag needed, the market-data mock is installed from the derived module as
  before, and the existing `TestProbeEngine` / `TestEngineModuleDerivation`
  behaviour still holds.

**Guardrail guards (this story creates specific new ways to trip these)**

- [ ] AC-G1 — All new logic lives in the `*_impl` / helper functions in
  `tools/probing.py`. `server.py`'s `probe_engine` wrapper stays a single
  delegating call with no branching; its docstring stays ≤ 2 lines. New
  arguments (`fields`, `allow_unmocked`) are added to the wrapper signature
  only.
- [ ] AC-G2 — No new Pydantic model under `app/schemas/`; no change to any
  engine route or service. The `mcp` pin is not bumped and `starlette` is not
  lifted past `==0.48.0`.

### Test plan

All cases live in `services/quant-engine/app/tests/test_mcp_tools.py` and call
the `*_impl` functions directly — no MCP transport, no server process.

- **Shape classification** — one probe per recognised request shape (a
  flat-body engine route, a snapshot-wrapped route, a bare-snapshot route),
  asserting the result names the matched shape and request model (AC-F1.1,
  AC-F1.6).
- **Shape mismatch** — a probe with a deliberately wrong-shaped payload:
  assert the mismatch warning is present and the route's real HTTP response is
  still returned (AC-F1.2).
- **Unclassified route** — a route whose shape matches none of the three:
  assert the result discloses it as unclassified rather than guessing (AC-F1.3).
- **Trust gating** — a probe whose body carries `trust: "unavailable"` (via a
  route+payload or a mocked response that yields it) is reported not-`ok`
  despite a `< 400` status, with the downgrade reason discoverable; a
  `verified` / `degraded` body of the same status stays `ok` (AC-F1.4,
  AC-F1.5).
- **Truncation** — a body with a long array: head/tail elements kept in order,
  original count preserved, self-describing marker present (AC-F2.1, AC-F2.2);
  a short array untouched, an empty array and a `null` body pass through
  (AC-F2.3); a drawdown probe over a long synthetic history returns a bounded
  result (AC-F2.5).
- **`fields=`** — with `fields` set, only those fields (plus envelope) are
  present; omitted, the bounded full body is returned (AC-F2.4).
- **`allow_unmocked`** — a non-derivable route refused by default with the
  message naming the flag (AC-F3.1); `allow_unmocked=True` proceeds and the
  result is marked unmocked (AC-F3.2); a typo'd explicit `engine_module` raises
  / errors loudly naming the module (AC-F3.3); a normal engine route is
  unaffected (AC-F3.4).
- **Wrapper thinness** — a check that `server.py`'s `probe_engine` still
  delegates in one call and its docstring is ≤ 2 lines (AC-G1); the existing
  five-tool registration check still passes.
- **Regression** — the current `TestProbeEngine`, `TestEngineModuleDerivation`
  and `TestBuildSnapshot` cases continue to pass unchanged.

Cover the absent / degraded cases named above explicitly — empty array, null
body, unclassified route, missing engine module — not just the happy path.

### Tickets

Ordered; the envelope contract lands first, its consumers build on it, tests
are their own ticket. **The F-1 breakdown and where the "matched request-model
name" comes from (FastAPI route introspection vs a hand-maintained table) is a
tech-lead DESIGN call — this ticket list may be revised in the DESIGN pass, and
T-43.1.1 in particular may split.**

- [ ] **T-43.1.1 — Shape-aware probe envelope (F-1).** In `tools/probing.py`:
  classify the request shape a route expects (flat / snapshot-wrapped / bare
  snapshot), report the matched shape and request model, warn on a payload
  shape mismatch without raising, disclose an unclassified route, and gate `ok`
  on the body not carrying `trust: "unavailable"`. `server.py` wrapper
  unchanged. Traces AC-F1.1–F1.6, AC-G1, AC-G2.
- [ ] **T-43.1.2 — Bounded response body + `fields=` (F-2).** Head/tail array
  truncation with original count preserved and a self-describing truncation
  marker; pass-through for short / empty / null; new `fields=` argument. Add
  `fields` to the `server.py` wrapper signature only. Traces AC-F2.1–F2.5,
  AC-G1.
- [ ] **T-43.1.3 — Fail-safe route gating (F-3).** `allow_unmocked: bool =
  False`; default refusal of non-derivable routes with a message naming the
  flag; loud failure on an unresolved explicit `engine_module`; normal engine
  routes untouched. Add `allow_unmocked` to the `server.py` wrapper signature
  only. Traces AC-F3.1–F3.4, AC-G1.
- [ ] **T-43.1.4 — Test coverage.** All cases in the test plan above, in
  `app/tests/test_mcp_tools.py`, calling `*_impl` directly. Own ticket.
- [ ] **T-43.1.5 — Capability-pack documentation (close-out, docs lane).**
  Document the new arguments (`fields=`, `allow_unmocked=`) and the enriched
  result (shape / request-model reporting, mismatch warning, trust-gated `ok`,
  truncation marker) in the `.agentic` backend / quant / testing capability
  packs, consistent with the v0.5.5 route-to-shape / trust / context-cost
  guidance already there. **Not** in `server.py` docstrings (2-line cap),
  **not** in `docs/contracts/`. This is a close-out documentation task owned by
  the docs lane, not part of the implementation tickets.

### Out of scope

- Any change to the engine routes or services themselves, or to
  `app/tests/fixtures.py`.
- Any new schema under `app/schemas/`.
- Bumping the `mcp` pin or letting `starlette` move past `==0.48.0` (broke
  944-test collection once; the trap is documented in `requirements-dev.txt`).
- The MCP transport / handshake itself — it cannot be verified in this run
  (an MCP server is connected at session start; verifying it needs a fresh
  interactive session). Explicitly out of scope for this story.

### Notes / decisions

- Kept as one story with F-2 and F-3 on the producer's confirmed two-story
  split: F-1/F-2/F-3 are all in `probe_engine_impl` and share one result
  envelope, which the tech lead should design once.
- The "matched request-model name" AC states observable output only. If the
  DESIGN pass finds request models cannot be recovered without a maintained
  table, that AC may be softened — flagged in § Open decisions.
- No formula, weighting, return basis or trust-classification change: the tool
  reports trust strings, it does not compute them. quant-audit is correctly
  skipped for this bundle.

---

## US-43.2 — the suite-runner tools fail safe

**Scope of code:** `services/quant-engine/app/mcp_server/tools/testing.py`
(`_run`, `run_tests_impl`, `check_gates_impl`, `reset_goldens_impl`).
`server.py` stays a thin wrapper.
**Status:** Backlog (draft — not filed under `docs/product/`).
**Closes:** F-4, F-5 (`run.md` § request).
**Verification:** `SKIP_GOLDEN_FRESHNESS_CHECK=1 python -m pytest app/tests/test_mcp_tools.py -q` from `services/quant-engine`.

### Story

As a **lane running `run_tests`, `check_gates` or `reset_goldens`**, I want a
subprocess that hangs to come back as a structured timeout result rather than
stalling my run, and `reset_goldens` to tell me what it discarded, so that
neither tool can quietly cost me a working session or uncommitted work.

### Context

Two measured hazards in `tools/testing.py`:

- **F-4 — no subprocess timeout.** Every `subprocess.run` call goes through
  `_run`, which omits `timeout=`. A wedged pytest / vitest / tsc / git
  invocation hangs the calling lane indefinitely with no signal.
- **F-5 — `reset_goldens` destroys uncommitted work with no record.**
  `reset_goldens_impl` runs `git checkout -- apps/desktop/src/test/dashboardGoldens.ts`
  and returns only `ok` / `path` / `stderr`. Whatever was in that file is gone
  with no way to see what it was.

`tools/testing.py` imports its path constants (`BACKEND_DIR`, `FRONTEND_DIR`,
`TEST_PASS_MARKER`, `npx_command`) from `scripts/run_all_tests.py` and must keep
doing so — this story restates no path and no step list that runner owns.

### Acceptance criteria

**F-4 — a hanging subprocess returns, it does not hang**

- [ ] AC-F4.1 — Every subprocess the suite-runner tools spawn is launched with a
  timeout; a subprocess that exceeds it is terminated rather than left running.
- [ ] AC-F4.2 — The timeout budget differs by scope — a `full`-suite run gets a
  larger budget than a single-file `backend` iteration, and `check_gates`'s
  individual gate subprocesses get their own. The budgets are defined in
  `tools/testing.py`, not restated from anything `scripts/run_all_tests.py`
  owns.
- [ ] AC-F4.3 — When a subprocess times out, the tool returns a structured
  result identifying it as a timeout (which scope / command, the limit that was
  hit). It does **not** raise or propagate an exception to the caller.
- [ ] AC-F4.4 — A timed-out `run_tests` result is distinguishable from both a
  passing run and a run with parsed failures: a caller can branch on "timed
  out" vs "failed" vs "passed" without guessing.
- [ ] AC-F4.5 — `check_gates` reports a per-gate timeout for whichever of
  dead-code / type-check / goldens-status subprocesses timed out, and still
  returns results for the gates that completed.
- [ ] AC-F4.6 — A subprocess that finishes under its limit is reported exactly
  as it is today — bounded parsed failures plus a short tail — with no timeout
  marker. The existing `TestRunTestsParsing` and `TestGates` behaviour holds.

**F-5 — `reset_goldens` records what it discarded**

- [ ] AC-F5.1 — Before it runs `git checkout --`, `reset_goldens` captures
  `git diff --stat` for `dashboardGoldens.ts` and returns that summary in its
  result.
- [ ] AC-F5.2 — `reset_goldens` also returns a bounded diff (head/tail capped,
  like other tool output) of the changes it is about to discard.
- [ ] AC-F5.3 — The capture happens strictly before the checkout. If the
  checkout then fails, the result still carries the pre-checkout stat and diff
  and reports the checkout failure.
- [ ] AC-F5.4 — When `dashboardGoldens.ts` has no drift, `reset_goldens`
  reports that nothing was discarded (empty stat, empty diff) rather than a
  bare successful checkout with no signal.

**Guardrail guards**

- [ ] AC-G1 — All new logic lives in `tools/testing.py`'s `*_impl` / helper
  functions. `server.py`'s `run_tests` / `check_gates` / `reset_goldens`
  wrappers stay single delegating calls; their docstrings stay ≤ 2 lines. No
  wrapper signature changes.
- [ ] AC-G2 — `tools/testing.py` still imports `BACKEND_DIR`, `FRONTEND_DIR`,
  `TEST_PASS_MARKER` and `npx_command` from `scripts/run_all_tests.py`; no path
  or step list that runner owns is copied into this module. No new schema; no
  `mcp` pin bump; no `starlette` past `==0.48.0`.

### Test plan

All cases in `services/quant-engine/app/tests/test_mcp_tools.py`, calling
`*_impl` directly and mocking `_run` / the subprocess boundary.

- **Timeout is passed** — mock the subprocess call and assert `_run` is invoked
  with a `timeout=` value, and that the value for `scope="full"` differs from
  `scope="backend"` and from the `check_gates` subprocesses (AC-F4.1, AC-F4.2).
- **Timeout is handled** — simulate `subprocess.TimeoutExpired`: assert
  `run_tests_impl` returns a structured timeout result and does not raise
  (AC-F4.3), and that the result is distinguishable from a pass and from a
  parsed-failure run (AC-F4.4).
- **`check_gates` partial timeout** — one gate subprocess times out, the others
  complete: assert a per-gate timeout is reported and the completed gates still
  have results (AC-F4.5).
- **Normal completion unchanged** — a fast subprocess still yields the existing
  bounded parsed result with no timeout marker (AC-F4.6); the current
  `TestRunTestsParsing` / `TestGates` cases still pass.
- **`reset_goldens` capture order** — mock the git calls and assert
  `git diff --stat` and a bounded `git diff` are invoked *before*
  `git checkout --`, and both appear in the result (AC-F5.1, AC-F5.2).
- **`reset_goldens` checkout failure** — checkout returns non-zero: the result
  still carries the captured stat and diff and reports the failure (AC-F5.3).
- **`reset_goldens` no drift** — `git diff --stat` is empty: the result says
  nothing was discarded (AC-F5.4).
- **Import guard** — a check that `tools/testing.py`'s path constants still
  resolve from `run_all_tests` (AC-G2).

### Tickets

- [ ] **T-43.2.1 — Per-scope subprocess timeouts (F-4).** In `tools/testing.py`:
  give every `subprocess.run` (through `_run`) a scope-appropriate `timeout=`;
  catch `TimeoutExpired` and turn it into a structured timeout result across
  `run_tests_impl` and `check_gates_impl`, distinguishable from pass and from
  parsed failures. No wrapper or import changes. Traces AC-F4.1–F4.6, AC-G1,
  AC-G2.
- [ ] **T-43.2.2 — `reset_goldens` records what it discards (F-5).** Capture
  `git diff --stat` and a bounded `git diff` for `dashboardGoldens.ts` before
  `git checkout --`; return both; handle the checkout-failure and no-drift
  cases. Traces AC-F5.1–F5.4, AC-G1.
- [ ] **T-43.2.3 — Test coverage.** All cases in the test plan above, in
  `app/tests/test_mcp_tools.py`, calling `*_impl` directly. Own ticket.
- [ ] **T-43.2.4 — Capability-pack documentation (close-out, docs lane).**
  Document the structured timeout result and its per-scope budgets, and the
  `reset_goldens` stat/diff return, in the `.agentic` testing capability pack.
  **Not** in `server.py` docstrings, **not** in `docs/contracts/`. Close-out
  task owned by the docs lane.

### Out of scope

- Any change to what `scripts/run_all_tests.py` or `scripts/detect_deadcode.py`
  own — step lists, path constants, the golden-freshness gate. `tools/testing.py`
  keeps importing from that runner.
- Any new schema under `app/schemas/`.
- Bumping the `mcp` pin or moving `starlette` past `==0.48.0`.
- The MCP transport / handshake — cannot be verified in this run, needs a fresh
  interactive session. Out of scope for this story.

### Notes / decisions

- Separate story from US-43.1 on the producer's confirmed split: different file,
  different tool surfaces, and F-4/F-5 have nothing to do with "the probe
  answered nothing". No shared code — the two stories can run in parallel.
- F-5 is a data-loss guard, not a refactor: the point is that discarded work is
  visible after the fact, not that `reset_goldens` stops discarding.
- No formula / methodology change; quant-audit correctly skipped.

---

## Open decisions

- **F-1 ticket breakdown and the source of the "matched request-model name".**
  Whether the matched request model is recovered by FastAPI route introspection
  or from a hand-maintained route→model table is a **tech-lead DESIGN** call,
  not a human product decision. It is surfaced here so it is not discovered
  mid-implementation. Consequence: **T-43.1.1 may split** in the DESIGN pass and
  US-43.1's ticket list may be revised. This does not block human approval of
  these drafts.

- **Epic / register placement — resolved, recorded for traceability.** Per the
  owner decision in `run.md`, this bundle is tracked as `.agentic`-internal tech
  debt, not a product epic: no PRD, no roadmap entry, no
  `docs/product/stories/` file, no story-index edit. The drafts live only in
  this file. Final placement in `docs/tech-debt-register.md` is the docs lane's
  call at close-out. Not reopened here.

- **MCP transport / handshake verification — not a decision, a stated limit.**
  Both stories record that the MCP server's startup and handshake cannot be
  verified in this run (the server is connected at session start); it needs a
  fresh interactive session and is out of scope for both stories. The
  `*_impl`-direct test suite is the entire verifiable surface.

No other producer open decision remains. `01-delivery-brief.md` § Open
decisions raised the epic-number question (resolved above) and this F-1
sub-scoping question (deferred to DESIGN above).

## Assumptions carried

Stated here because the briefs did not settle them and the ACs depend on them:

- The three request-body shapes (flat / snapshot-wrapped / bare snapshot) and
  the "~14 engine routes" span are taken verbatim from `run.md`; the routes were
  not enumerated against `app/api/routes/` in this pass.
- The drawdown probe size (34,135 chars / ~8,500 tokens, mostly the underwater
  series) is taken as current and used only as context in AC-F2.5, not as a
  target.
- "Report the matched request-model name" is assumed feasible as observable
  output; if DESIGN finds it needs a maintained table, AC-F1.1 may be softened.
- Capability-pack documentation (T-43.1.5 / T-43.2.4) is placed as a close-out
  docs-lane task to reconcile the work order's non-goal ("do not touch the
  capability packs") with its DoD ("new args documented in the capability
  packs"). If the owner wants this handled differently, those tickets are the
  place to say so.
