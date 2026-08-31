REPORT 2026-08-31-probe-engine-hardening/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only order; no verification command specified

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - verdict: new epic, findings-first, sibling to Epic 36 / Epic 21 — see § Placement
  - 2 stories proposed for the new epic — see § Stories
  - open decision: owner opens the epic and assigns its number (43 is next free) — see § Open decisions
  - open decision: fix-1 carries 3 sub-behaviours; whether it stays one story is a tech-lead DESIGN call — see § Open decisions
  - dedupe: no product doc, story, roadmap item or git history covers the MCP server / probe_engine — see § Already covered
  - docs for these stories land in the .agentic capability packs, not docs/contracts/ — see § Stories

risks:
  - The 5 findings are taken as measured and correct per the order's non-goals; I did not reproduce any number (drawdown probe 34,135 chars, "14 engine routes", shape taxonomy).
  - I read server.py / probing.py / testing.py to confirm the fix seams and the _impl split; I did not independently enumerate the 14 engine routes finding 1 spans (16 route modules exist under app/api/routes/).
  - Placing this on the product roadmap rather than treating the MCP server as .agentic-internal is a judgment call; precedent (Epics 21/32/36 are pure infra epics on the product roadmap) supports it, but the owner may prefer otherwise — flagged as an open decision.

## Orchestrator brief
- verdict: NEW EPIC, findings-first, explicit sibling to Epic 36 (Findings-First Doc & Gate Hygiene) and Epic 21 (Testing Strategy & Architecture Hardening).
- epic: PROPOSED — next free number is 43; owner opens it and assigns the number. Active epics 41 and 42 do not fit.
- audit story: NOT needed. The review is already done and its findings are measured; the new PRD transcribes them as F-1..F-5. This mirrors Epic 42's shape, not the US-x.1 audit-story shape.
- 2 stories, both PROPOSED:
  - probe_engine stops confirming probes that answered nothing — F-1, F-2, F-3, all in tools/probing.py
  - the suite-runner tools fail safe — F-4, F-5, all in tools/testing.py
- lanes: backend + test only. No frontend. quant-audit correctly SKIPPED (no formula/weighting/trust-classification — the tool reports trust strings, it does not compute them).
- docs: the return-shape and new-arg changes are documented in the .agentic backend/quant/testing packs (already at v0.5.5 for the route-to-shape table), NOT in docs/contracts/. Route docs work is a pack reconciliation, not a product-contract change.
- blocks dispatch: two owner decisions (open the epic + number; confirm product-roadmap placement is wanted). Neither blocks tech-lead DESIGN starting on the story shapes once the epic exists.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**Nearest precedent: Epic 36 — Findings-First Doc & Gate Hygiene**, itself an
explicit sibling of Epic 32 and adjacent to Epic 21. All three are infrastructure
epics with **no user-visible deliverable** — "make green mean green" (21), route
inventory and commit-gate reachability (36), agent-facing doc accuracy (32). This
request is the same class: a measured correctness defect in agent-facing tooling
that "hands lanes confidently wrong answers," surfaced by a review, with a ranked
findings list. Epic 36 was created exactly this way — from
`docs/product/review-2026-08-20-findings.md`, an 8-finding between-epic health
review.

**Why a new epic and not a fold-in.** The two active epics are 41 (Documentation
& Roadmap Accuracy Reconciliation) and 42 (Dependency Vulnerability Remediation).
Neither owns MCP tool correctness. Epics 21, 32 and 36 are all Closed; this
project's house pattern is to open a fresh findings-first epic for a new review
rather than reopen a closed one (Epic 36 did this against Epic 32's domain).

**Why the product roadmap at all.** The MCP server lives in the repo
(`services/quant-engine/app/mcp_server/`), is covered by the repo suite
(`app/tests/test_mcp_tools.py`), is subject to the repo gates, and the order
routes it through the full orchestrator route with integration + review gates.
That makes it repo work in the same sense Epics 21/32/36 were. The `.agentic`
side of the review (route-to-shape table, "read trust before believing a 200",
context-cost warning) is already folded into the packs at v0.5.5 — that is the
network-config half and it is done; the repo-code half is what needs stories.

**Why no audit story.** The findings-first pattern makes US-x.1 audit-only *when
the cause is not yet named*. Here it is named five times over with reproducible
measurements, and the order's non-goals forbid re-litigating them. So the new
PRD records the five ranked fixes as F-1..F-5 directly (the order's `run.md`
`request:` line is the findings source — do not let it persist as a standalone
file with its own numbering), and the epic goes straight to remediation stories.
This is Epic 42's shape (US-42.1 assessment → grouped remediation), not the
US-34.1 / US-33.1 audit-story shape.

## Stories

### US-43.1 — probe_engine stops confirming a probe that answered nothing

Closes **F-1, F-2, F-3**. A lane that calls `probe_engine` today can get
`ok: true` on a response that carried no answer — a payload-shape mismatch the
tool never inspected, a `trust: "unavailable"` body, or a non-engine route that
silently ran live and unmocked. This story makes the tool's success signal mean
"the route actually answered."

  value:      An agent lane can trust `probe_engine`'s `ok` / result envelope
              instead of re-reading every body by hand to find out whether the
              probe was real. Directly removes the "confidently wrong answers"
              failure the review measured.
  slice:      In — payload-shape detection across the engine routes
              (flat / snapshot-wrapped / bare-snapshot), reporting the matched
              request-model name, a warning on shape mismatch, `ok` no longer
              true when the body carries `trust: "unavailable"` (F-1);
              head/tail truncation of long arrays with the original count
              preserved plus a `fields=` argument (F-2); `allow_unmocked: bool
              = False` refusing non-engine / underivable routes by default and
              naming the flag, while a typo'd engine name still fails loudly
              (F-3). Deliberately out — any change to the engine routes
              themselves; any new schema under `app/schemas/`; the MCP
              transport/handshake (cannot be verified this run).
  depends_on: none. All three findings are in `tools/probing.py`
              (`probe_engine_impl` / `engine_module_for`) and share one return
              envelope, so the tech lead designs that envelope once.
  invest:     Weak on "small" — F-1 alone is three behaviours (shape
              classification across ~14 routes; request-model-name reporting;
              trust-string → not-ok). Acceptable because they are one contract
              change on one function with one review surface, and splitting F-1
              from F-2/F-3 would mean two designs of the same envelope. The
              tech-lead DESIGN pass should confirm this (see Open decisions).
  docs:       New args and envelope fields are documented in the .agentic
              capability packs (backend / quant / testing), NOT in a repo
              docstring — `server.py` tool docstrings are capped at 2 lines —
              and NOT in `docs/contracts/`.

### US-43.2 — the suite-runner tools fail safe

Closes **F-4, F-5**. Two ways the `tools/testing.py` wrappers can hurt the
caller: a subprocess in `_run` with no `timeout=` can hang a lane indefinitely,
and `reset_goldens` runs `git checkout --` with no record of what it discarded.

  value:      A lane running `run_tests` / `check_gates` gets a structured
              timeout result instead of a hang, and `reset_goldens` returns the
              `git diff --stat` (plus a bounded diff) of what it threw away, so
              destroyed uncommitted work is at least visible after the fact.
  slice:      In — a per-scope `timeout=` on every `subprocess.run` in `_run`,
              returning a structured timeout result rather than raising (F-4);
              `reset_goldens_impl` capturing `git diff --stat` and a bounded
              diff of `dashboardGoldens.ts` before the checkout and returning it
              (F-5). Out — any change to what `scripts/run_all_tests.py` owns;
              `tools/testing.py` keeps importing its path constants from that
              runner.
  depends_on: none. Separate file, separate tool surfaces (`run_tests`,
              `check_gates`, `reset_goldens`) from US-43.1. Can run in parallel.
  invest:     Weak on "valuable" in the user-facing sense — no researcher sees
              this. Acceptable on the Epic 21 / 36 precedent: agent-tool
              safety is exactly what those epics shipped, and F-5 is a
              data-loss guard, not a refactor.

**Not folded into one story:** two files, two independent tool contracts, and
F-4/F-5 have nothing to do with "the probe answered nothing." One AC set across
all five would be incoherent. **Not split into five:** each fix is small, and
F-1..F-3 share one return envelope the tech lead should design once.

## Sequence

1. **US-43.1 first.** It is the risk-carrier — the shape-taxonomy work across
   ~14 routes is where the plan is most likely to prove wrong (a route whose
   real shape fits none of the three buckets, or a request-model name that
   can't be recovered without route introspection). Learn that before US-43.2
   is ticketed.
2. **US-43.2 second, or in parallel.** No shared code with US-43.1; the only
   reason not to run them concurrently is review bandwidth. Hard-independent,
   so a soft edge only.

Neither story depends on the other's artifact. Both depend on the epic existing.

## Open decisions

- **The owner opens the epic and assigns its number.** 43 is the next free
  number (41 and 42 are active). Epic placement is the owner's call; this brief
  proposes, it does not create.

- **Confirm the MCP server belongs on the product roadmap.** The alternative
  view is that it is `.agentic`-network-internal tooling and its repo code
  should be tracked as tech debt rather than a product epic. Precedent (Epics
  21/32/36 are pure-infra epics on the product roadmap; the code is repo code
  under the repo's gates) points to a product epic, but this is a framing call
  only the owner should make.

- **Does F-1 stay one story?** F-1 bundles shape classification, request-model
  reporting, and trust-string handling. This brief keeps them together with
  F-2/F-3 in US-43.1 because they are one return envelope. If the tech-lead
  DESIGN pass finds the request-model-name mapping needs route introspection
  heavy enough to stand alone, US-43.1 may split — expect this and do not treat
  the two-story plan as fixed.

- **Where does the "matched request-model name" come from?** FastAPI route
  introspection vs a maintained table. This is a tech-lead DESIGN question, not
  a product one — named here only so it is not discovered mid-implementation.

## Already covered

Nothing covers this. Searched, all with zero product-doc hits:

- `grep -rn -i "probe_engine|mcp_server|mcp tool|probe engine|reset_goldens|mcp_tools|MCP"` over
  `docs/product/` (roadmap, all PRDs, all stories, `current-product-state.md`)
  and `docs/tech-debt-register.md` — no matches.
- `git log -- services/quant-engine/app/mcp_server/` — two commits only,
  `b998c9a add mcp` and `07535f8 fixes`, both 2026-08-27, neither tied to a
  story. The MCP server was added outside the PRD→Story→Ticket structure.
- The roadmap's "Open items" list carries no MCP / probe_engine entry, so there
  is no deliberately-left-open decision this brief would reverse.

The `.agentic` capability packs (backend / quant / testing) were updated to
v0.5.5 with the route-to-shape table, the "read trust before believing a 200"
rule and the context-cost warning. That is the network-guidance layer and it is
done; it does not change the tool's behaviour, which is what these two stories
do. Keep the implemented behaviour consistent with those packs (the order's
constraint).
