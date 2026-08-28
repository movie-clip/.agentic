REPORT 2026-08-28-epic-41-and-dep-vulns/01
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only producer order, no verification command named

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Epic 41 — Documentation & Roadmap Accuracy Reconciliation: open it as the ACTIVE epic, sibling to Epic 32 / Epic 36 — see § Placement
  - docs-lane close-out: write the Epic 41 PRD folding run 2026-08-27 02-scout.md § A-I as F-1..F-n; migrate US-41.2's shipped record from the roadmap "between-epic work" narrative into an Epic 41 section — see § Stories (Epic 41 setup)
  - docs-lane close-out: reslot US-41.1 (Backlog) and US-41.2 (Done) from the "Unassigned / Backlog (no epic)" index group into a new "### Epic 41" group; flip both files' "Epic:" header field — no file rename needed — see § Stories
  - Story A PROPOSED (US-41.3, Epic 41): doc-reconciliation bundle for the 5 carried follow-ups — see § Stories
  - Story B PROPOSED: dependency-vulnerability remediation, findings-first, its own epic — audit story first — see § Stories
  - open decision: Story B's epic — new epic (number is the owner's call) vs Backlog — see § Open decisions
  - open decision: US-41.1 is a Dashboard-trust chart feature, not doc-accuracy work — confirm it belongs under Epic 41 or send it back to Backlog — see § Open decisions
  - open decision: does Story A ship a re-drift guard test, or is it documentation-only like US-32.3 — see § Open decisions
  - sequencing across Epic 41 setup + Story A + Story B in § Sequence

risks:
  - live pip-audit / npm audit could not be re-run offline; Story B's 6 advisories are taken from run 2026-08-27 03-delivery-brief.md, US-36.2 § Out of scope and the roadmap open-items bullet — all three agree, none re-verified against a current vulnerability DB this run
  - two of the 5 carried Story A items are already partly closed: docs/contracts/currency-risk-fields.md now exists (I ran `ls docs/contracts/`), and current-product-state.md:3 header date is already bumped to 2026-08-27 with a detailed parenthetical (I read it) — the live residue is narrower than the CARRIED rows read; § Already covered has the item-by-item state
  - the exhaustive 12-contract x 20-schema field diff was completed in run 2026-08-27 (run.md Closed table: 11 docs diffed, correlation-fields.md + diagnostics-fields.md corrected) — only the "verify correlation-fields.md TS-type columns against types.ts" residual is carried; the full sweep is NOT Epic 41 scope
  - I did not read run 2026-08-27 artifacts 04/05/08/12 line by line — the exact carried-item wording is taken from run.md § Open (the CARRIED rows) and the work order, which agree

## Orchestrator brief

- verdict: **new epic + two proposed stories.** Open Epic 41 (doc/roadmap accuracy), propose Story A under it, propose Story B (dep vulns) under its own separate epic.
- epic: **Epic 41 — Documentation & Roadmap Accuracy Reconciliation** — PROPOSED as ACTIVE, explicit sibling to Epic 32 and Epic 36 (both between-epics doc-hygiene epics, both shipped a re-drift guard). Owner already decided to open it (work order); this brief makes it concrete.
- Epic 41 already has content: **US-41.2** (system-architecture doc + guard, Done 2026-08-27) and **US-41.1** (inline withheld-return annotation, Backlog). Both keep their numbers and files — no rename. Story A takes **US-41.3**.
- Story A (US-41.3): doc-reconciliation bundle — 6 carried follow-ups from run 2026-08-27, same shape as US-32.3 / US-36.3. Weak on user-visible value (agent-facing); precedent accepts that. Quant not needed up front; the current-product-state.md re-audit item may spawn a quant referral if it surfaces a stale trust claim.
- Story B: dependency-vulnerability remediation for 5 pinned backend advisories + 1 transitive frontend one, deferred by US-36.2. **Findings-first**: first story audits which advisories are reachable and which bumps are golden-safe (US-36.2 records goldens are sensitive to FastAPI/Pydantic internals), then remediation stories apply the safe bumps. Backend and frontend split.
- Story B's epic is **not Epic 41** — different domain. New epic recommended (findings-first, sibling to Epic 21 / Epic 36); the number is the owner's call. Backlog is the fallback.
- blocks dispatch: three owner decisions in § Open decisions — Story B's epic identity, US-41.1's fit under Epic 41, and whether Story A ships a guard. None block the Epic 41 PRD/setup docs work.
- dedupe: no existing story covers Story A's 6 items or Story B's advisories; US-36.2's deferral reason is unchanged (§ Already covered).
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement

**Epic 41 — Documentation & Roadmap Accuracy Reconciliation.**

*Problem it owns.* Between Epic 32 (closed 2026-08-19) and now, the navigation
layer around the code drifted again: run 2026-08-27's health review
(`02-scout.md` § A-I) found `system-architecture.md` ~30 epics stale, six stale
epic-status labels and a missing Epic 30 heading in `stories/README.md`, a
~35-epic-stale `prd/README.md` index, and assorted pointer/date/citation nits.
US-41.2 already closed the largest item (the architecture doc) as a standalone
Backlog story. What remains is a bundle of smaller reconciliations with no epic
home, plus the housekeeping of recording US-41.2 itself in the roadmap
structure rather than in a "between-epic work" narrative paragraph.

*Goal.* Every agent-facing status/navigation doc — `stories/README.md`,
`prd/README.md`, `current-product-state.md`, `epic-roadmap.md`, `CLAUDE.md`'s
doc map, the contract-doc citation headers — reads a state that matches the
roadmap, git and the shipped code; and the run 2026-08-27 findings are folded
into a discoverable PRD finding list (`F-1`..`F-n`) instead of living only in a
run artifact.

*Non-goals.*
- The exhaustive 12-contract x 20-schema field diff — completed in run
  2026-08-27 (`run.md` Closed table).
- Any behaviour, schema, analytics or trust-classification change. If the
  `current-product-state.md` re-audit surfaces a stale methodology/trust claim,
  that is a finding routed to quant — not a doc edit made in this epic.
- Re-opening `financial-methodology.md`'s withholding rule — confirmed
  internally consistent in run 2026-08-26 and re-confirmed by 02-scout.md § F.
- `CLAUDE.md`'s Epic-34 "most-recently shipped" pointer — stale in the literal
  number but hedged by design (US-32.3); surfacing it, not scheduling it.

*Precedent it is a sibling of.* **Epic 36 — Findings-First Doc & Gate Hygiene**,
which its own roadmap section calls an "explicit sibling to Epic 32 — Project
Hygiene & Agent-Facing Doc Accuracy". Both were seeded from a between-epics
health-review findings document, folded the findings into a PRD as `F-n`
(deduplicated against the tech-debt register and prior open findings), and each
shipped a mechanical guard against re-drift (`test_docs_paths.py`,
`test_route_inventory.py`). Run 2026-08-27 is the health review; US-41.2 already
shipped the guard (`test_architecture_doc_route_inventory.py`). This is the
same epic shape, third instance. The project's own convention for this class is
"new epic, every time, never a reopen" (Epic 36 roadmap section), so this is
precedent-consistent, not epic inflation. **Opening it is the owner's call** —
the work order records that call as already made; this brief makes it concrete.

*Why Story B does not go here.* Dependency-vulnerability remediation is not
documentation accuracy — it changes pinned versions and can move engine
behaviour. Its precedent is Epic 21 (Testing Strategy & Architecture Hardening)
and Epic 36 (which built the scan and deferred acting on it), not Epic 32.
Folding it into Epic 41 would mix a doc-hygiene epic with a
dependency-and-goldens epic — two different gate profiles (Epic 41 needs no
quant-audit; Story B's remediation stories may).

## Stories

### Epic 41 setup (docs-lane close-out, not a story)

Driven by this brief; the docs lane writes these at close-out after the owner
approves Epic 41.

- **Write `docs/product/prd/epic-41-<slug>.md`.** Fold run 2026-08-27
  `02-scout.md` § A-I into `F-1`..`F-n`, carrying its "examined-and-correct"
  list (§ I) as the epic's examined-and-correct record. Deduplicate against
  `docs/tech-debt-register.md` and Epic 34's deliberately-open findings.
  Mark which findings US-41.2 closed, which Story A (US-41.3) closes, and which
  stay open with a reason.
- **Migrate US-41.2's shipped record.** The roadmap's "Between-epic work
  shipped 2026-08-27 (no epic)" narrative paragraph
  (`epic-roadmap.md`, in the live snapshot) moves into a new
  `## Epic 41 — Documentation & Roadmap Accuracy Reconciliation` section with
  US-41.2 recorded as its first shipped story. The snapshot line "No epic is
  active" becomes "Epic 41 active".
- **Reslot the story index.** `stories/README.md`'s "Unassigned / Backlog
  (no epic)" group loses US-41.1 and US-41.2; a new "### Epic 41" group gains
  both (US-41.1 Backlog, US-41.2 Done). Flip the `**Epic:**` header field in
  both story files from "Unassigned — Backlog" to "Epic 41". **No file rename
  is required** — US-41.1 and US-41.2 keep their numbers; the "reserve US-41.1"
  language in both files' headers is satisfied by US-41.1 simply keeping its
  own number under the new epic.

### Story A — US-41.3: the agent-facing status and navigation docs match the roadmap, git and the shipped code

*User-visible outcome.* An agent or the owner reading `stories/README.md`,
`prd/README.md`, `current-product-state.md`, `CLAUDE.md`'s doc map or a
contract-doc citation header gets a statement that matches the roadmap, git and
the shipped types — not a stale pointer, date or citation.

    value:      same class as US-32.3 / US-36.3 — the beneficiary is an
                agent/developer navigating the repo, not the researcher. The
                concrete, checkable deliverables are the specific doc states in
                the ACs (and optionally one guard test — see Open decisions).
    slice:      IN — the 6 carried reconciliation items:
                (1) verify correlation-fields.md's DriftWindow-table + relocated
                    `coverage`-row TS-type columns against
                    apps/desktop/src/features/portfolio/types.ts (a
                    frontend/test-lane check; types.ts has DriftWindow at
                    ~L1519 and coverage fields present — the doc columns need
                    confirming, not assuming);
                (2) the "**Backend schema:**" header-citation nuance in
                    correlation-fields.md (L84 cites analytics/risk.py's
                    build_rolling_risk_series; the Pydantic class RollingRiskPoint
                    lives in reconciliation.py) and the analogous line in
                    factor-drift-fields.md;
                (3) re-audit current-product-state.md's *body* against shipped
                    code — the header now asserts "body current through Epic 40"
                    but that rests on run 2026-08-27 spot-checks, not a fresh
                    line-by-line audit;
                (4) epic-roadmap.md's non-monotonic per-epic section ordering
                    (Epic 25 at L1250, Epic 23 at L1291, Epic 24 at L1343);
                (5) CLAUDE.md "Where to find what" doc map has no row for
                    docs/contracts/currency-risk-fields.md (the file exists;
                    only the map row is missing);
                (6) any other pointer/label residue 02-scout.md § B-G caught
                    that US-41.2 and run 2026-08-27's docs passes did not
                    already fix — the docs lane confirms the live list at
                    ticketing time (see risks — some sub-items are already
                    partly closed).
                nearest thing OUT — the exhaustive contract x schema field
                diff (done, run 2026-08-27); system-architecture.md (US-41.2,
                shipped); financial-methodology.md's withholding rule
                (confirmed consistent); any behaviour/schema/trust change.
    acceptance-criteria shape:
                one AC per item, each stating the observable end state
                ("correlation-fields.md L84's citation names the class's real
                module" / "CLAUDE.md doc map lists currency-risk-fields.md" /
                "epic-roadmap.md epic sections are in descending order"), plus
                a final AC that `python scripts/run_all_tests.py` is green.
                Item (3) additionally: "the re-audit either confirms the body
                or lists each discrepancy; any discrepancy that is a
                methodology/trust claim is recorded as a finding for quant, not
                edited here."
    needs quant?  not up front. Item (3)'s body re-audit *may* surface a stale
                 methodology/trust statement in current-product-state.md — if it
                 does, that specific claim routes to the quant lane as a
                 finding; the rest of Story A proceeds without it.
    depends_on:  Epic 41 PRD exists (soft — Story A can be ticketed from this
                 brief alone, but its finding references (F-n) resolve against
                 the PRD). No hard dependency on US-41.2 or Story B.
    invest:      weak on Valuable in the literal user-visible sense — accepted
                twice before (US-32.3, US-36.3). Estimable: high — every item
                has one unambiguous correct value except (3), whose size is
                "read the body once"; (3) is the honest reason this is a
                reconciliation bundle and not six one-line edits.

### Story B — dependency-vulnerability remediation (its own epic; audit story first)

*Operator-visible outcome.* The scheduled `dependency-audit.yml` run stops
reporting known advisories against this repo's pinned dependency set — because
each advisory has been assessed and every safe bump applied — instead of
producing a red run every week that everyone learns to ignore.

    epic home:  NOT Epic 41. Recommended: a new findings-first epic —
                "Dependency Vulnerability Remediation" (or similar) — sibling to
                Epic 21 (architecture hardening) and Epic 36 (which built the
                scan, US-36.2, and explicitly deferred acting on findings). The
                epic number is the owner's call (do not fix it here). Backlog is
                the fallback if the owner would rather not open an epic — but
                there are already 6 concrete advisories and a weekly workflow
                that will keep surfacing them, so "Backlog until it has
                siblings" is a weak fit; it has siblings now.
    why findings-first:
                US-36.2's own context records that backend deps are pinned
                exact *because goldens are sensitive to FastAPI/Pydantic
                internals*. Three of the five backend advisories
                (starlette, pydantic-settings, python-dotenv) sit on that
                sensitive path. Scoping a bump before knowing whether it moves a
                golden is exactly the "fix before the cause is named" failure
                the audit-first pattern exists for. So US-<epic>.1 is
                audit-only: for each of the 6 advisories, record severity,
                whether the vulnerable code path is reachable from this repo's
                usage, the minimum non-vulnerable version, and whether that
                version bump moves any golden or shifts any analytic output.
                Findings recorded as F-n. No version change in the audit story.
    subsequent stories:
                one (or a small number) that apply the bumps the audit found
                safe, re-capture goldens only where the audit predicted a
                move and a quant-audit confirms the move is
                serialization/formatting and not a methodology shift, and leave
                as recorded-open any advisory whose safe bump is blocked (with
                the reason).
    backend / frontend split:
                yes. The 5 backend advisories (starlette==0.48.0, pypdf==6.9.1,
                python-multipart==0.0.20, pydantic-settings==2.13.1,
                python-dotenv==1.1.1) are the substantive work and carry the
                golden risk. The 1 transitive frontend advisory (@babel/core,
                low-severity, dev/build-time) is a separate, much smaller
                ticket — likely a lockfile bump with no runtime surface —
                and should not gate the backend work.
    risk profile:
                a dependency bump can change behaviour. The audit story is the
                risk-first move — it surfaces which bumps are safe before any
                are attempted. Remediation stories that touch a golden or any
                analytic output route through quant-audit (guardrail 1 /
                project.md "any change touching a return basis goes through the
                quant lane"); a bump that only moves serialization does not, but
                the tech lead makes that call at DESIGN.
    depends_on: none on Epic 41. The audit story depends on nothing; each
                remediation story depends_on the audit story (it needs the
                per-advisory safe-bump determination).
    invest:     Valuable — operator/security value, checkable against the
                `dependency-audit.yml` run going green. Estimable: the audit
                story is estimable; the remediation stories are deliberately
                not sized until the audit lands (that is the point of
                audit-first).

## Sequence

1. **Owner opens Epic 41** and decides Story B's epic identity + number (or
   Backlog). Cheap. Blocks the Epic 41 index/PRD naming and Story B ticketing;
   blocks nothing else.
2. **Epic 41 setup (docs lane)** — write the PRD folding 02-scout.md § A-I,
   migrate US-41.2's roadmap record into an Epic 41 section, reslot US-41.1 /
   US-41.2 in the story index, flip both files' Epic field. No renames.
   Independent of Story A and Story B. Fast, zero-risk.
3. **Story-author tickets Story A (US-41.3)** from this brief. Can run in
   parallel with step 2; its F-n references firm up once the PRD exists.
4. **Story-author tickets Story B's audit story** from this brief.
5. **Story B audit story runs** — risk-first: it determines which bumps are
   safe and which move a golden, reshaping the remediation stories. Do this
   before any remediation ticket is written.
6. **Story A runs** and **Story B remediation stories run** — independent of
   each other, parallelisable.

Edge reasons: step 1 before 2 because the epic name/number is an input to the
PRD and index. Step 2 before/with 3 because Story A cites F-n. Step 5 before any
remediation because the audit's safe-bump table is the remediation stories'
scope. Story A and Story B never block each other — different docs, different
code, different gates.

If capacity forces a single track first: **Story B's audit story**, because the
`dependency-audit.yml` weekly run will produce a red result until the advisories
are addressed or explicitly accepted, and an ignored red gate erodes every
other gate. Story A is pure-win but not time-sensitive.

## Open decisions

- **Story B's epic identity and number.** New findings-first epic
  ("Dependency Vulnerability Remediation", sibling to Epic 21 / Epic 36) vs a
  Backlog story. Recommendation: new epic — 6 concrete advisories + a weekly
  workflow is past the "Backlog until it has siblings" threshold. If a new
  epic, the number is explicitly the owner's call and is not set in this brief.

- **US-41.1's fit under Epic 41.** US-41.1 (inline withheld-return annotation
  on the Performance & Benchmark chart) is a Dashboard trust-surfacing feature —
  its natural lineage is Epic 34 (An Answerable Dashboard), not a
  documentation-accuracy epic. The work order directs it under Epic 41, and it
  can sit there as a carried story (no rename, keeps US-41.1). But the owner
  should confirm that placement knowingly, or choose to (a) leave US-41.1 as a
  Backlog orphan keeping its number until a Dashboard epic reopens, or (b)
  widen Epic 41's charter line to "Documentation & Roadmap Accuracy
  Reconciliation, plus one carried Dashboard-trust story" so the mismatch is
  explicit in the record. Recommendation: (b) — cheapest, keeps the owner's
  stated placement, and stops a future reader wondering why a chart feature is
  in a doc epic.

- **Does Story A ship a re-drift guard test?** US-32.3 was documentation-only
  (goldens byte-identical, no new test); US-36.3 shipped
  `test_route_inventory.py`. Of Story A's items, only the epic-roadmap.md
  section-ordering item is mechanically guardable (assert epic headings are in
  descending order). Recommendation: leave it to the tech lead / story-author —
  a one-item guard is thin, and US-41.2 already added the architecture-doc
  guard this epic's precedent calls for. Not a blocker either way.

- **Quant-audit involvement in Story B remediation.** A starlette /
  pydantic-settings bump could shift a golden. Whether a given bump needs
  quant-audit (analytic output moved) or only tech-lead sign-off
  (serialization moved) is a DESIGN-time call per remediation story, flagged
  here so it is not discovered mid-implementation.

## Already covered

Item-by-item state of the 5 carried Story A follow-ups (verified this run where
it changed a verdict):

- **currency-risk-fields.md** — the *file* exists (`ls docs/contracts/` this
  run lists it). The live gap is only the missing **row in CLAUDE.md's doc
  map** (`grep` this run: CLAUDE.md names `risk-fields.md` explicitly and
  otherwise uses the generic `<area>-fields.md` form — currency-risk has no
  dedicated row). Narrower than the CARRIED row reads. Still a real item.

- **current-product-state.md header date** — already bumped: line 3 reads
  "Updated: 2026-08-27 (body current through Epic 40 ... plus Epics 35-39, the
  2026-08-26 chart-data audit, and the 2026-08-27 US-41.2 ... pass)" (read this
  run). The date-bump CARRIED sub-item is **done**. What remains is that the
  header now *asserts* body-currency that was never established by a
  line-by-line audit — item (3) in Story A's slice.

- **correlation-fields.md / factor-drift-fields.md citation nuance** — still
  live. `grep` this run: correlation-fields.md L84 "**Backend schema:**
  `.../analytics/risk.py` — `build_rolling_risk_series`" cites the builder
  function, not the Pydantic class's module. A citation-precision fix, no
  behaviour impact.

- **epic-roadmap.md non-monotonic section ordering** — confirmed this run via
  the epic-heading `grep`: Epic 25 (L1250) precedes Epic 23 (L1291) precedes
  Epic 24 (L1343). Real, cosmetic.

- **correlation-fields.md TS-type columns vs types.ts** — `grep` this run
  confirms `types.ts` has `DriftWindow` (~L1519) and `coverage?:
  SyntheticHistoryCoverage | null` entries; the doc's TS column *text* still
  needs a column-by-column check. A frontend/test-lane verification task, small.

Dedupe confirmations:

- **No existing story covers Story A.** US-41.2 covered `system-architecture.md`
  only. The exhaustive contract x schema sweep (run 2026-08-27) corrected
  `correlation-fields.md` + `diagnostics-fields.md` for *field* drift; the
  carried items here are citation-header form, TS-column verification, doc-map
  rows, roadmap ordering and a body re-audit — none of them in that sweep's
  scope. Confirmed against the story directory listing and `run.md` Closed
  table this run.

- **No existing story covers Story B, and US-36.2's deferral reason is
  unchanged.** US-36.2 § Out of scope: "acting on any vulnerability the scan
  finds ... is a follow-up, not part of this slice"; the roadmap open-items
  bullet: "addressing them is a follow-up, not part of Epic 36." No story has
  been written since; the advisories are not in `docs/tech-debt-register.md`
  (`grep` this run: nothing). The scheduled `dependency-audit.yml` still runs
  weekly and will keep surfacing them. Nothing about the deferral has changed —
  it was always "do this later", and this is later.

- **financial-methodology.md withholding rule** — confirmed internally
  consistent by run 2026-08-26 and re-confirmed by run 2026-08-27 02-scout.md
  § F. Not a finding, not in Epic 41 scope.
