REPORT 2026-08-27-next-epic-or-story/03
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
  - projects/portfolio/project.md § "`build-story` is superseded and must not run" — false premise: the claim that build-story's description "still triggers on *build US-X.Y*" and that "two architectures compete". The repo skill IS narrowed — `.claude/skills/build-story/SKILL.md` frontmatter opens "SUPERSEDED - do not use for implementation". Exact replacement wording in § Pack correction detail.

handoff:
  - verdict: multi-unit cleanup — a docs-lane reconciliation pass (no story) for the stale-label/pointer/date cluster, plus ONE proposed story for the system-architecture.md rewrite + its mechanical guard — see § Orchestrator brief
  - the roadmap itself is NOT the problem — epic-roadmap.md snapshot is accurate and consistent with git + current-product-state body; the rot is in stories/README.md, prd/README.md and system-architecture.md — see § Already covered
  - docs-lane pass Part A (no human decision needed): 6 stale epic labels in stories/README.md, 3-4 "Epic 40 PRD: none" pointers, current-product-state.md header date, prd/README.md § Index, US-34.3 clerical number, build-story prose in repo docs — see § Stories
  - docs-lane pass Part B (blocked on the human's numbering call): story-index restructure — missing Epic 30 heading, and where the orphan US-41.1 file is indexed — see § Open decisions
  - PROPOSED story (Unit 2): rewrite system-architecture.md's seam/route/data-flow inventory to the 15 shipped routes + extend test_route_inventory.py to guard that file — not docs-lane-only because it needs architecture judgement and ships a test — see § Stories
  - recommend a new findings-first Epic 41 — Documentation & Roadmap Accuracy Reconciliation (explicit sibling to Epic 32 and Epic 36) to house both units; opening it is the owner's call — see § Placement
  - § F number mismatch (-$53.13 vs -$58.11 / -$19.98) is clerical, NOT a quant question — US-34.3 lines 133-134 already record -$53.13 as a superseded first estimate and the methodology reconciles -$58.11 / -$19.98 explicitly — see § Stories
  - § H exhaustive 12-contract x 20-schema diff: recommend OUT of scope for this baseline — two mechanical guards already exist, scout's sample was clean, no drift evidence — a separate follow-up if the owner wants exhaustive certainty — see § Open decisions
  - not-a-finding / do not schedule: methodology withholding rule (§ F, internally consistent — verified), roadmap snapshot (§ I), CLAUDE.md Epic-34 pointer (§ G, stale-but-hedged by US-32.3 design) — see § Already covered

risks:
  - system-architecture.md's "Data Flow" section (02-scout.md § A, lines ~267-345) is scout's claim; I confirmed the stale seam/route inventory myself (lines 1-120; app/api/routes/ + api/main.py show 15 real routers, none of the removed routes exist) but did not read the Data Flow section line by line
  - § H "sample is clean" (dashboard-fields.md in sync with schema) is taken on trust from 02-scout.md § H — I did not re-run any contract-vs-schema field diff
  - opening Epic 41 for doc-hygiene reverses nothing recorded, but the human's 2026-08-26 "no new epic now" call was specifically about the withheld-return-annotation story (US-41.1 orphan) — a new epic for doc-hygiene is a different question and still the owner's
  - the build-story SKILL.md frontmatter is already narrowed (I verified — contra project.md); the residual conflict is only repo prose in stories/README.md and prd/README.md

## Orchestrator brief

- verdict: **more than one unit.** Not a single cleanup story; not pure docs-lane either. Split: (1) a docs-lane reconciliation pass with no story file, (2) one proposed story for system-architecture.md.
- epic: PROPOSED — **Epic 41 — Documentation & Roadmap Accuracy Reconciliation**, findings-first, explicit sibling to Epic 32 and Epic 36. Owner decides whether to open it; the work can also run as standalone Backlog stories if not.
- unit 1 — **docs-lane reconciliation, no story** (dispatch `docs-engineer` with a close-out-style order): stale epic-status labels, "Epic 40 PRD: none" pointers, current-product-state.md header date, prd/README.md § Index, US-34.3 clerical number, build-story prose. Every fix has one unambiguous correct value; no code, no test, no design call.
- unit 2 — **PROPOSED story**: "The architecture doc an agent is told to trust for backend seams actually matches the repo" — rewrite system-architecture.md's route/seam/data-flow inventory (currently describes the /backtests//construction//optimizer product deleted in Epic 8, ~30 epics stale) + extend `test_route_inventory.py` to guard it. Needs architecture judgement + a test → a story, not a docs edit. Direct analogue of US-36.3.
- blocks dispatch: **one human decision** — the story-index numbering / orphan-US-41.1 question (§ Open decisions). Unit 1 Part A and unit 2 do not wait on it; unit 1 Part B (index restructure) does.
- § F is clerical not quant; § H is out of scope; methodology + roadmap snapshot + CLAUDE.md pointer are not findings.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered · Pack correction detail

## Placement

**The roadmap is not what is broken.** `docs/product/epic-roadmap.md`'s live
snapshot (lines 1-77) is accurate: every epic `## Completed Epic`, "No epic is
active", "next epic is unscoped" — consistent with git (`07535f8` latest, Epic
40 the highest shipped) and with `current-product-state.md`'s body. 02-scout.md
§ I confirms it, and I re-checked the snapshot and the epic-heading grep myself.
Cosmetic-only roadmap nits (Epic 33 heading style at line 780; "Epic 8 — Reset
to Portfolio Analysis Core" vs the PRD filename's "...to Analysis Core") are
real but trivial.

The drift is concentrated in three satellite docs:

- `docs/architecture/system-architecture.md` — its "Current Implemented Backend
  Seams" / "Important implementation reality" sections (lines 28-107) describe
  `/backtests/portfolio-allocation*`, `/construction/run`,
  `/strategy-lab/etf-ranking*`, `/optimizer/preview` and services
  `portfolio_backtest_engine.py`, `strategy_lab.py`, `optimizer_preview_service.py`
  — **none of which exist** (verified: `app/api/routes/` has 15 modules,
  `api/main.py` registers 15 routers, `ls app/services/` finds none of the named
  files). Pre-Epic-8. CLAUDE.md and project.md both name this file the source of
  truth for "backend seams".
- `docs/product/stories/README.md` — 6 stale epic-status labels, a structural
  bug (no Epic 30 heading), an unindexed orphan story, stale build-story prose.
- `docs/product/prd/README.md` — its § Index still lists Epic 5 as "**Active**"
  and references PRD files `epic-5-...md` / `epic-3-...md` that do not exist;
  last touched at commit `bfacf7b` (~Epic 5), ~35 epics ago; no pointer to the
  roadmap as the real index.

**Precedent epic:** Epic 36 — Findings-First Doc & Gate Hygiene, itself
described in its roadmap section as an "explicit sibling to Epic 32 — Project
Hygiene & Agent-Facing Doc Accuracy". Both were seeded from a between-epics
health-review findings document, folded the findings into a PRD as F-n
(deduplicated against the tech-debt register and prior open findings), and each
closing story shipped a mechanical guard against re-drift
(`test_docs_paths.py`, `test_route_inventory.py`). This request is the same
shape: 02-scout.md is the health review; unit 2 is the guard-shipping story.
That makes **Epic 41, sibling to 32/36**, the precedent-consistent home — not
epic inflation, because the precedent is "new epic every time" for this class
(Epic 36's own section: "new epic, every time, never a reopen"). Whether to
open it is the owner's call (§ Open decisions).

## Stories

### Unit 1 — docs-lane reconciliation pass (NO story file)

Dispatch `docs-engineer` with a close-out-style order. This is reconciliation,
not a vertical slice: no user-visible behaviour, no code, every edit has a
single correct value. Splits into two parts by whether it needs the human's
numbering decision.

**Part A — no decision needed, can dispatch immediately:**

    scope:  docs/product/stories/README.md, docs/product/prd/README.md,
            docs/product/current-product-state.md, docs/product/epic-roadmap.md,
            docs/product/stories/US-34.3-*.md
    - stories/README.md: 6 stale epic-status labels -> "(complete)". Lines 82
      (Epic 35), 92 (Epic 34), 125 (Epic 32), 221 (Epic 26), 232 (Epic 24) read
      "(active)"; line 162 (Epic 28) reads "(backlog)". epic-roadmap.md has all
      six as "## Completed Epic". Also normalise "(completed)" -> "(complete)"
      (lines 270/281/297/311) and the non-monotonic 25-before-26 ordering.
    - "Epic 40 PRD: none" is wrong in 3-4 places -> point at
      docs/product/prd/epic-40-snapshot-trust-and-fidelity-follow-through.md
      (which exists, Status: Completed, a retrospective close-out PRD): 
      epic-roadmap.md:83-88, stories/README.md:23, and the **PRD:** headers of
      US-40.1 / US-40.2.
    - current-product-state.md:3 — header "Updated: 2026-08-19 (after Epic 34 ...)"
      lags its own body (covers US-35.1, a 2026-08-26 audit, US-37.1/38.1/39.1,
      US-40.1/40.2). Bump the date and the parenthetical; body spot-checks
      accurate, do not rewrite it.
    - prd/README.md § Index (lines 41-49) — rewrite: Epic 5 is not "Active" (it
      is "complete — superseded by Epic 8 pivot" per stories/README.md:487),
      Epic 3 is cancelled, the referenced epic-5-*.md / epic-3-*.md PRD files do
      not exist, and there is no pointer to epic-roadmap.md as the authoritative
      epic index. Add that pointer.
    - US-34.3 clerical: lines 132 and 185 still say "-$53.13"; the story's own
      AC7/AC8 (lines 40, 96-97) and lines 133-134 ("the story's first estimate
      of -$53.13 omitted day-one trade cash. Measured: -$58.11") say -$58.11.
      Make lines 132/185 read -$58.11. This is NOT a quant question — see the
      note after Unit 2.
    - build-story prose: stories/README.md:16 and :504-505, prd/README.md:29-30
      still tell agents to "invoke the build-story skill". Replace with the
      orchestrate-feature / write-story routing. (The SKILL.md frontmatter is
      already narrowed; only this prose lags.)
    - roadmap cosmetic: Epic 33 heading style (line 780), Epic 8 name vs PRD
      filename (line 1866) — fix if trivial, not load-bearing.

    value:      an agent or the owner reading stories/README.md, prd/README.md
                or current-product-state.md gets a status that matches the
                roadmap and git, instead of "Epic 34 active" 6 epics after it
                closed. Same value class as US-32.3 / US-36.3.
    slice:      label / pointer / date / prose corrections only. Out: anything
                needing a numbering decision (Part B), and system-architecture.md
                (Unit 2).
    depends_on: none.
    invest:     not a story by design — no vertical value slice. Runs as a
                docs-lane close-out order. Acceptable because every edit is
                mechanical with one correct answer.

**Part B — blocked on the human's numbering decision (§ Open decisions):**

    - stories/README.md has no "### Epic 30" heading; US-30.1..30.6 (lines
      166-175) sit under the "### Epic 28 ... (backlog)" heading, though
      epic-roadmap.md:1036 has a real "## Completed Epic: Epic 30 — Exposure
      Improvements" section and docs/product/prd/epic-30-exposure-improvements.md
      exists. Create the heading, move the rows.
    - the orphan file docs/product/stories/US-41.1-inline-withheld-return-
      annotation.md exists but is indexed nowhere (grep "41" in stories/README.md
      returns nothing). Its own header says "the docs lane must renumber/reslot
      the file if a different epic number is assigned". Where it lands depends on
      the Epic 41 numbering call.

### Unit 2 — PROPOSED story: system-architecture.md accuracy + guard

**Outcome:** an agent told (by CLAUDE.md and project.md § Sources of truth) to
trust `docs/architecture/system-architecture.md` for "what the backend seams
are" reads an inventory that matches `app/api/routes/`, and a mechanical test
fails if it drifts again.

    value:      today that doc's seam/route inventory describes a
                ranking/construction/optimizer product removed in Epic 8 (~30
                epics / ~2 months ago) and names 8 service files that do not
                exist. An agent planning backend work from it is planning
                against a deleted architecture. This is the same failure
                US-36.3 fixed for current-product-state.md's 3-module
                undercount — one notch larger and in the doc CLAUDE.md points
                at first for seams.
    slice:      IN — rewrite "Current Implemented Backend Seams",
                "Important implementation reality", the "Data Flow" section
                (~267-345) and the truth-class list entries that name
                "persisted construction artifacts" / "optimizer previews and
                handoffs" / "replay-derived hypothetical outputs", to the 15
                shipped routers (exposure, dashboard_history, diagnostics,
                drift, attribution, correlation, stress, drawdown, distribution,
                provenance, cache, currency_risk, imports, market_data, health)
                and their real services. Extend
                app/tests/test_route_inventory.py (or a sibling) to assert
                system-architecture.md's route list == app/api/routes/, the way
                it already does for current-product-state.md.
                OUT — the sections 02-scout.md § A confirms are already current
                (market-data providers lines 131-239, truth-semantics 109-129,
                the US-36.3 unauthenticated-file-read tradeoff 252-265); leave
                them untouched.
    depends_on: none hard. Soft: cheaper after Unit 1 so the roadmap/index it
                cross-references are themselves clean.
    invest:     weak on "vertical user-visible value" in the literal sense —
                the beneficiary is an agent/developer, not the researcher. This
                project has already accepted that framing twice (US-32.3,
                US-36.3), and the test deliverable is the concrete, checkable
                part. Estimable: medium — the rewrite scope of the "Data Flow"
                section is not yet confirmed line by line (see risks), so the
                honest first ticket is the tech-lead reading the current seams
                and drafting the replacement structure.

**Why Unit 2 is a story and not more docs-lane work:** (a) it is authorship,
not label-correction — ~250 lines describing a different product; (b)
characterising the *current* seams is `architecture.md`-pack territory
(tech-lead), not reconciliation from a contract note; (c) it ships a test,
which is a `test`-lane change with a test plan. That is a story shape.

**On § F (the number mismatch) — clerical, do NOT route to quant.** I opened
US-34.3 and financial-methodology.md:2410-2456 myself. The methodology
reconciles both live figures explicitly: "-$58.11" is "the figure this rule
produced when it shipped, kept because it is what the 96% is measured against";
"-$19.98" is "the 2026-08-17 capture ... US-34.9 supplied real terminal-day
quotes". US-34.3 itself (lines 133-134) records "-$53.13" as a superseded first
estimate that "omitted day-one trade cash". The math is settled and documented;
the only defect is two stale "-$53.13" strings in US-34.3's own prose that
contradict its own acceptance criteria. One docs-lane edit (in Part A).

## Sequence

1. **Human decides the numbering question** (§ Open decisions). Cheap; unblocks
   Unit 1 Part B. Does not block Part A or Unit 2.
2. **Unit 1 Part A** — docs-lane close-out order. Fast, zero-risk, produces a
   clean baseline immediately. Independent of everything.
3. **Unit 1 Part B** — same docs lane, once (1) is answered. Small.
4. **Unit 2** — the system-architecture.md story. Sequenced last of the doc
   work because it is the one with unconfirmed scope (risk-first says surface
   that early *within the story*: ticket 1 is the tech-lead scoping pass), and
   because it benefits from the index/roadmap it cross-references already being
   clean.
5. If Epic 41 is opened: its PRD folds 02-scout.md's § A-I into F-1..F-n with
   the "examined-and-correct" list (§ I is that list already), deduped against
   `docs/tech-debt-register.md` and Epic 34's open findings. Unit 1 = the
   findings + mechanical fixes (US-41.x), Unit 2 = US-41.x + its guard.

If the owner wants only ONE unit done: do Unit 1 (pure win, no risk, no
decision beyond the numbering line). Unit 2 is the part that genuinely needs
shaping and a story file.

## Open decisions

- **Open Epic 41 for this work, or run it as standalone Backlog stories under
  the existing hygiene precedent?** Recommendation: open it — Epic 32 and Epic
  36 both set the precedent that between-epics doc-hygiene reviews get their own
  epic ("new epic, every time"). Epic placement is the owner's call per the
  product pack; a brief that presents it as settled removes the owner from it.

- **The US-41.1 numbering collision.** The file
  `docs/product/stories/US-41.1-inline-withheld-return-annotation.md` already
  occupies "US-41.1" as a self-declared placeholder, and its header instructs
  the docs lane to renumber it if an epic number is assigned elsewhere. If the
  doc-hygiene epic becomes Epic 41, its audit/fix story wants to be US-41.1 too.
  Options: (a) doc-hygiene = Epic 41; the annotation story is renumbered and
  the story index gains a new "## Unassigned / Backlog (no epic)" section to
  hold it — recommended, because the index needs an orphan-story home
  regardless; (b) doc-hygiene = Epic 42, leaving 41 nominally reserved for the
  annotation story; (c) the annotation story moves to
  `docs/tech-debt-register.md` — not recommended, it is a genuine vertical
  slice, fully planned in run 2026-08-26-missing-chart-data-0414. Agents cannot
  rename cleanly (create + `git rm` handoff), so whichever option, the docs
  lane writes the new file and reports the `git rm` for the human to run. This
  is the one decision that blocks Unit 1 Part B.

- **Carve `.claude/skills/build-story/SKILL.md` out or leave it alone?** It is
  already narrowed (frontmatter opens "SUPERSEDED - do not use"). No change
  needed there; the residual build-story prose is in `docs/**` and handled by
  Unit 1 Part A. Confirming so the orchestrator does not schedule a repo-skill
  edit that is not required.

- **Is the exhaustive 12-contract x 20-schema field diff (§ H) wanted?**
  Recommendation: no, not for this baseline. Two mechanical guards already run
  (`schema_edit_reminder.py` PostToolUse hook on `app/schemas/`,
  `test_docs_paths.py`), 02-scout.md's sample (`dashboard-fields.md`) showed no
  drift, and there is no drift evidence to justify the sweep. If the owner
  wants exhaustive certainty it is a separate follow-up story in the mould of
  US-23.5 (contract/schema/type/docs drift), not part of reaching known-good.

## Already covered

Deliberate state — do NOT schedule work that re-litigates these:

- **financial-methodology.md withholding / terminal-day rule (02-scout.md § F).**
  Verified myself at lines 2410-2456: the US-34.8 supersession ("the reconciled
  terminal day is CORRECTED, not withheld ... via `market_derived_terminal_value`")
  is stated coherently, `return_is_publishable` is scoped to the *other* cause
  (material `unbacked_cash_flow`), and no residual live "terminal day is
  withheld" framing survives. This was fixed by run
  2026-08-26-missing-chart-data-0414/04-docs.md and is internally consistent
  now. Nothing to do.

- **epic-roadmap.md snapshot (02-scout.md § I).** Consistent with git and with
  current-product-state.md's body. No repeat of the pre-US-32.3 "Epic 31 active
  four epics later" failure. The roadmap does not need a cleanup pass; its
  satellites do.

- **CLAUDE.md's Epic-34 "most-recently shipped" pointer (02-scout.md § G).**
  Stale in the literal number (Epic 40 is current) but **hedged by design** —
  US-32.3 deliberately made both sites (CLAUDE.md:41 and :203) defer to
  `epic-roadmap.md` as the authority precisely so the number going stale
  degrades gracefully. Surfacing per the pack rule on recorded decisions: this
  was decided with more context than this brief has. If the docs lane wants to
  bump the illustrative number while it is in CLAUDE.md for other reasons that
  is harmless, but it is not a finding and not a scheduled task.

- **CLAUDE.md's repo-layout route list.** Checked by US-36.3 and by 02-scout.md
  § G — accurate (matches the 15 modules). No edit.

Dropped / re-scoped scout items:

- **02-scout.md § C's implication that a prior run flagged "Epic 40 shipped
  with no PRD"** — that flag is now stale; the retrospective PRD landed
  (`epic-40-snapshot-trust-and-fidelity-follow-through.md`, verified present,
  Status: Completed). The live drift is 3-4 "PRD: none" pointers, folded into
  Unit 1 Part A.

- **02-scout.md § D (prd/README.md is ~35 epics stale)** — real, folded into
  Unit 1 Part A as a rewrite of its § Index. Not its own story: it is a
  single-file reconciliation with an unambiguous target (point at the roadmap).

- **§ H contract-vs-schema exhaustive diff** — explicitly out of scope for this
  cleanup (see § Open decisions). Not dropped as false; deferred as
  unjustified-for-now.

## Pack correction detail

`projects/portfolio/project.md` § "`build-story` is superseded and must not
run". Its second paragraph currently ends:

> Its description still triggers on *"build US-X.Y"*, *"pick up ticket
> T-..."*, *"implement the next story"* — the same phrasing that should reach
> `orchestrate-feature`. Until its description is narrowed in the repo, two
> architectures compete for the same request and which one answers is a coin
> flip.

That is no longer true. `.claude/skills/build-story/SKILL.md` frontmatter now
reads: "SUPERSEDED - do not use for implementation. Story implementation is
owned by the .agentic network's orchestrate-feature skill ... Requests like
'build US-X.Y', 'pick up ticket T-...', or 'implement the next story' belong to
orchestrate-feature."

Suggested replacement for those two sentences:

> The repo skill's own description (`.claude/skills/build-story/SKILL.md`
> frontmatter) now opens "SUPERSEDED - do not use for implementation" and
> explicitly routes "build US-X.Y" / "pick up ticket T-..." / "implement the
> next story" to `orchestrate-feature`, so the trigger collision is closed at
> the skill itself. Residual prose telling agents to run `build-story` survives
> only in `docs/product/stories/README.md` and `docs/product/prd/README.md` — a
> docs-lane reconciliation, tracked under Epic 41.

This is a `docs-engineer` close-out edit per project.md's lane-routing note
that the docs lane may touch `capabilities/**` / the pack when applying
`pack-corrections.md`.
