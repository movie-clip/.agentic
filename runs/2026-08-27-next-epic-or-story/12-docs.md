REPORT 2026-08-27-next-epic-or-story/12
status:      DONE
verdict:     NONE

changed:
  - .agentic/projects/portfolio/capabilities/architecture.md — pack correction (pack-corrections.md item 2): added `currency-risk` to the `/engines/{...}` route-prefix brace list in § "The seams". Verified against code: `POST /engines/currency-risk/run` is registered (`app/api/routes/currency_risk.py:6,9`, `app/api/main.py:21`). Index unchanged (no section moved).
  - .agentic/projects/portfolio/project.md — tightened § "`build-story` is superseded and must not run": the residual-prose sentence order 04 applied verbatim (claiming build-story prose "survives only in docs/product/stories/README.md and docs/product/prd/README.md") now states that prose has been reconciled to `orchestrate-feature` / `write-story`, so the collision reads as closed both at the skill and across the repo docs.
  - docs/product/stories/US-41.2-system-architecture-doc-accuracy-and-route-guard.md — Status `Backlog` → `Done`; added a "Close-out (2026-08-27)" block (integration + acceptance PASS, all 13 ACs SATISFIED, suite green: backend 947 / frontend 359 / tsc + dead-code clean, the two shipped artifacts); ticked all 13 ACs (`- [ ]` → `- [x]`) and all 3 tickets T-41.2.1/.2/.3; rewrote the stale trailing "story draft for human review … no gate has accepted it" line to a shipped/gate-accepted note that keeps the unresolved epic-placement flag.
  - docs/product/stories/README.md — added a `US-41.2` row (Status `Done`) to the "### Unassigned / Backlog (no epic)" section order 04 created; extended that section's preamble to note US-41.2 shipped standalone and that epic placement (open "Epic 41" or leave standalone) is still the owner's call and would renumber both files.
  - docs/product/epic-roadmap.md — snapshot header `Updated: **2026-08-25**` → `**2026-08-27**`; added a "**Between-epic work shipped 2026-08-27 (no epic).**" paragraph after "The next epic is unscoped." recording US-41.2 (the system-architecture.md rewrite + the new guard, gate PASSes, suite counts, the open Epic-41 placement question), explicitly stating it is not entered in a slice log because the slice log below is strictly epic-partitioned. No new epic or slice-log section invented.
  - docs/product/current-product-state.md — header parenthetical extended: "… plus the 2026-08-27 US-41.2 architecture-doc seam-accuracy pass"; new "**Architecture-doc seam accuracy (US-41.2, 2026-08-27):**" paragraph in § "## Backend" describing the system-architecture.md backend-seams / service-layer / data-flow / API-boundary rewrite to the 15 registered routers and the new `test_architecture_doc_route_inventory.py` guard (bidirectional drift check, names the offending module), noting the three protected sections stayed byte-identical.
  - docs/contracts/currency-risk-fields.md — NEW field-inventory contract doc for `services/quant-engine/app/schemas/currency_risk.py` (`CurrencyRiskRequest`, `CurrencyRiskResult`, `CurrencyLegContribution`), in the `correlation-fields.md` format: header block, trust-class preamble, per-type field tables (name / Python type / TS type / UI label / trust class / nullability / notes), null-display rules. Every row grounded in the schema's actual annotations + defaults and the `types.ts` / `runCurrencyRiskEngine` mirror; no trust level fabricated (schema carries only `Literal["synthetic","unavailable"]`).
  - docs/contracts/exposure-fields.md — one line: the existing `CurrencyRiskResult` prose paragraph now points at both `financial-methodology.md` §Currency Risk Contribution (formulas) and the new `docs/contracts/currency-risk-fields.md` (field-level inventory). No other change to this file.

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Order's verification field is NONE; docs lane has no Bash. The orchestrator runs `python scripts/run_all_tests.py` after this order lands, as the final gate before the human commits.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - `<run_dir>/pack-corrections.md` is now fully applied: item 1 (project.md build-story paragraph) by order 04, item 2 (`capabilities/architecture.md` § "The seams" `/engines/{...}` list missing `currency-risk`) by this order. Nothing left open in that file.
  - correlation-fields.md TS-type columns for the `DriftWindow` table and the relocated `coverage` row (both added by order 05) are still unverified against `apps/desktop/src/features/portfolio/types.ts` — outside this order's contract-doc scope (currency-risk only). Route to a frontend or test lane. Carried from 05-docs.md § handoff.
  - correlation-fields.md § US-9.2 and factor-drift-fields.md cite `analytics/risk.py` / component types on their "**Backend schema:**" line where the actual Pydantic class `RollingRiskPoint` lives in `app/schemas/reconciliation.py` — header-citation nuance, not field drift, still open. Carried from 05-docs.md § handoff; a future doc pass.
  - epic-roadmap.md has non-monotonic per-epic section ordering (the Epic 23 section precedes Epic 24) — noticed by order 04, still unaddressed, out of scope here.
  - US-41.1 / US-41.2 epic placement and numbering is unresolved and is the owner's call: opening "Epic 41 — Documentation & Roadmap Accuracy Reconciliation" would renumber/reslot both story files. Agents cannot rename — the docs lane would write the new file and report the `git rm` of the old path for a human to run.
  - CLAUDE.md's "Where to find what" doc map does not list the new `docs/contracts/currency-risk-fields.md` (it lists `risk-fields.md` specially); a one-row add when CLAUDE.md is next touched. Out of scope here (CLAUDE.md not in this order's fence).

risks:
  - epic-roadmap.md's slice log is strictly epic-partitioned and has no row format for a no-epic story. Per the order's DoD I recorded US-41.2 as a narrative paragraph in the top "living execution snapshot" section instead of forcing a slice-log row or inventing an "Epic 41" section, and flagged that inline in the paragraph. A human should confirm this is the right home, or open Epic 41.
  - current-product-state.md body below the header line was not re-audited against shipped code in this order (scope was the US-41.2 addition + header parenthetical only). The "body current through Epic 40 …" claim is carried forward from order 04, which rested it on 02-scout / 03-delivery-brief spot-checks, not a fresh audit.
  - The new currency-risk-fields.md TS-type column was grounded in a read-only pass over `apps/desktop/src/features/portfolio/types.ts` and the `runCurrencyRiskEngine` adapter. `CurrencyRiskRequest` has no dedicated TS type — the request body is the inline object `{ snapshot, window }` with `window` typed `60 | 252` at the call site — and the doc says so rather than inventing a TS type name.
