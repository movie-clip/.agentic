REPORT 2026-09-07-new-epic-perf-benchmark-trust/04
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-44.1-monthly-returns-honour-withholding-gate.md — new draft story (P1); 8 ACs, 4 tickets
  - docs/product/stories/US-44.2-withheld-days-warning-direction.md — new draft story (P2); 7 ACs, 3 tickets
  - docs/product/stories/US-44.3-benchmark-outage-preserves-portfolio-performance.md — new draft story (P3); 9 ACs, 5 tickets
  - docs/product/stories/US-44.4-selectable-comparison-benchmark.md — new draft story (P4); 8 ACs, 5 tickets

verification:
  command:   NONE (drafting order; verification field was NONE)
  result:    NOT_RUN
  detail:    Four draft stories written from 03-delivery-brief § Stories/Sequence/Open decisions, 02-quant-research §§ P1-P3, and 01-recon § Blast radius. ACs are grounded and cited; not approved — human review pending.

contract_notes:
  - US-44.4 adds a caller-chosen benchmark symbol to the /run-imported request — a change under services/quant-engine/app/schemas/ (or the route signature); schema hook fires, TS types + docs/contracts/dashboard-fields.md move in the same pass. Not express-eligible.
  - US-44.3 changes section_trust.benchmark_path / source_status.benchmark_history semantics and makes docs/contracts/dashboard-fields.md:105 reachable; TS types + that contract doc move even if no schema model changes.
  - US-44.1 reconciles docs/contracts/dashboard-fields.md:98-101 (source_status.monthly_returns) at close-out; a per-month disclosure marker (Open decision 2, out of scope) would additionally pull the schema hook if ever adopted.

pack_corrections:
  - capabilities/story.md § Files lists docs/product/stories/_TEMPLATE.md ("the shape to follow"), docs/product/stories/README.md ("read for numbering") and docs/product/epic-roadmap.md as present; all were deleted in repo commit ce9c97d and are absent from the working tree. Replacement wording: "No story template or index exists in-tree (removed in ce9c97d). Follow the two most recent sibling stories for house format; numbering is US-<epic>.<n>-<slug>.md with tickets T-<epic>.<story>.<n>." House format for this run was taken from ref/story-format-US-43.3.md and ref/story-format-US-43.4.md.

handoff:
  - Four draft story files in docs/product/stories/ (US-44.1 .. US-44.4), house format per the ref/ examples; each opens with a "draft for human review" banner and a ## Open decisions block.
  - Ticket inventory: US-44.1 → T-44.1.1..4; US-44.2 → T-44.2.1..3; US-44.3 → T-44.3.1..5 (T-44.3.1 is a tech-lead DESIGN pass and blocks T-44.3.2/T-44.3.3); US-44.4 → T-44.4.1..5. No ticket instructs a commit or a self-gate.
  - BLOCKS dispatch: Epic 44 PRD (epic-44-performance-benchmark-trust.md) and its roadmap entry do not exist — the docs lane creates them at 05 after human approval; the stories reference that PRD path as "to be created".
  - BLOCKS dispatch: all four stories are drafts; the human approves before any ticket is dispatched (the network never self-approves a story).
  - Open decisions carried, none resolved by this lane: #2 (US-44.1 — per-cell marker; scoped out, candidate successor US-44.5), #5 (US-44.1 — methodology wording, close-out), #6 (US-44.2 — methodology wording, close-out), #3 (US-44.3 — valuation calendar; resolved into DESIGN ticket T-44.3.1, algorithm still open), #7 (US-44.3 — benchmark-outage rule unwritten).
  - US-44.4 T-44.4.2 (return basis of a non-verified benchmark) may need a focused quant RESEARCH pass first — 02-quant-research explicitly scoped P4 out.

risks:
  - Assumed story home is docs/product/stories/ because the work order directs file creation there; this resolves the producer's Open decision 1 only for story files. The PRD/roadmap surface deleted in ce9c97d is still unreplaced and the .agentic product/project packs still point at deleted paths — unresolved for the human.
  - Assumed Epic number 44 and one-epic grouping of all four points (producer's Open decision 8), and status Backlog (order did not say Epic 44 was pulled into the active phase).
  - The reported "+100% monthly return" repro is taken on trust from 01-recon (no runtime repro built). US-44.1 ACs are written to the confirmed code-path defect, not to that magnitude.
  - US-44.4 spans a schema/route contract change and a new UI selector interaction model — my capability pack flags that shape for a possible backend-contract / UI split. The producer scoped it as one story (INVEST: medium, Independent, Valuable); I did not split it. Producer's call if T-44.4.1's schema surface grows.
  - US-44.4 AC5 requires an "honest, non-verified return basis" for a non-allowlisted benchmark but no brief names which basis that is; left for the design/quant pass. 01-recon only establishes it cannot be verified_total_return.
  - No disagreement with either brief on substance. Minor: 02-quant-research lists dashboard max-drawdown as benchmark-independent while also separately gated by its own withholding policy — US-44.3 AC3 keeps it conditional on that existing policy to avoid overstating what the story delivers.

---

## Orchestrator brief

Four draft stories for the proposed **Epic 44 — Performance & Benchmark Trust**, one per reported point. Drafts for human review; not approved, not dispatchable.

- Numbering / status / sequence: US-44.1 (P1), US-44.2 (P2), US-44.3 (P3), US-44.4 (P4); all `Backlog`; sequence US-44.1 → [US-44.2 in parallel] → US-44.3 → US-44.4.
- **US-44.1** `docs/product/stories/US-44.1-monthly-returns-honour-withholding-gate.md` — 8 ACs, 4 tickets, quant-gated. Carries Open decision 2 (per-cell marker — scoped out, candidate successor US-44.5) and 5 (methodology wording, close-out).
- **US-44.2** `docs/product/stories/US-44.2-withheld-days-warning-direction.md` — 7 ACs, 3 tickets, quant-gated (full route: trust-disclosure change). Carries Open decision 6 (methodology wording, close-out).
- **US-44.3** `docs/product/stories/US-44.3-benchmark-outage-preserves-portfolio-performance.md` — 9 ACs, 5 tickets, quant-gated. T-44.3.1 is a tech-lead DESIGN pass and blocks the implementation tickets. Carries Open decision 3 (valuation calendar → T-44.3.1) and 7 (outage rule unwritten).
- **US-44.4** `docs/product/stories/US-44.4-selectable-comparison-benchmark.md` — 8 ACs, 5 tickets, quant-touched, NOT express-eligible (schema hook). No blocking decision; T-44.4.2 may need a focused quant RESEARCH pass first.
- Blocks dispatch: (a) all four are drafts pending human approval; (b) Epic 44 PRD + roadmap entry do not exist — docs lane creates them at 05.
- Pack correction: `capabilities/story.md` § Files points at three files deleted in ce9c97d; house format taken from `ref/` US-43.3 / US-43.4 instead.
- Sections below: **Draft status** · **Decisions this lane took** · **The four stories** · **Open decisions carried into the stories** · **Assumptions and risks**.

---

## Draft status

These four files are **drafts for human review**. Per the project delivery model
("The human approves; the network never self-approves a story") and the story
lane's definition of done, nothing here is dispatchable until the human approves
the epic and the stories. Each file opens with a banner saying so and a
`## Open decisions` block.

Two things must happen before any ticket is dispatched, both owned elsewhere:

1. **Human approval** of proposed Epic 44 and the four stories.
2. **The docs lane (step 05)** creates
   `docs/product/prd/epic-44-performance-benchmark-trust.md` and the
   epic-roadmap entry — the story files reference that PRD path as "to be
   created". This lane did not touch the roadmap, any PRD, or a stories index
   (per the order's scope fence and the story pack).

The `docs/product/stories/` directory did not exist (deleted in `ce9c97d`);
writing the four files created it.

## Decisions this lane took

- **AC grounding.** Every AC traces to `02-quant-research.md` (§§ P1-P3) or
  `01-recon.md` (§ Blast radius / § P1-P4) and cites it. No rule was invented.
- **US-44.1 = exclude-the-day.** The monthly grid omits exactly the days the
  published TWR chain omits, honouring `return_is_publishable` and the
  market-derived terminal-value correction; an all-withheld month emits no row;
  the month inherits its range's TWR trust level and the run-level withheld-days
  disclosure. The per-cell "partial month" marker is **out of scope** (Open
  decision 2) and recorded as candidate successor story **US-44.5**.
- **US-44.2 = copy selection by sign.** Understates iff impact > 0, overstates
  iff impact < 0, no directional claim at 0.00 or null; magnitude shown as
  `abs(impact)`. Frontend-only; no engine change. Full route + quant-audit gate
  (human decision 2026-09-07) because it is a trust-disclosure change.
- **US-44.3 = split the two fail-closed gates.** Benchmark-independent outputs
  (portfolio TWR, MWR, net contributions, monthly returns, dashboard
  max-drawdown) publish at their own trust when benchmark history is absent; only
  benchmark-derived fields go `unavailable`; excess return null, never 0. The
  fully-empty case stays fully unavailable. **T-44.3.1 is a tech-lead DESIGN
  pass** for a benchmark-independent valuation calendar and the gate split; it
  blocks the implementation tickets. The calendar algorithm is not specified in
  the story.
- **US-44.4 = thread a chosen symbol end to end.** Card selector
  (workspace-persisted, App-level, US-25.2 pattern) → adapter → `/run-imported`
  route → `run_imported_dashboard_history(..., benchmark_symbol=...)`. A
  non-allowlisted symbol gets an honest, non-verified return basis; a
  history-less symbol yields an unavailable benchmark section with a reason, not
  a silent fallback. Schema/route change → schema hook, not express-eligible.
  Sequenced last (risk-ordering behind US-44.3).
- **No commit / self-gate tickets.** Quant-audit, integration and review gates
  are dispatched by the orchestrator; the human commits. Docs close-out tickets
  cover methodology and contract-doc wording only; story/epic status records are
  the docs lane's at close-out.
- **Not specified (left to the tech-lead design pass):** whether the gated
  per-day return is a shared helper or a call into the existing one; the exact
  schema shape for US-44.4; the benchmark-independent calendar algorithm; the
  precise non-verified return-basis label.

## The four stories

| Story | File | Point / finding | ACs | Tickets | Quant | Sequence | Unresolved decisions carried |
|---|---|---|---|---|---|---|---|
| US-44.1 | `docs/product/stories/US-44.1-monthly-returns-honour-withholding-gate.md` | P1 / F-1 | 8 | T-44.1.1..4 | gated (RESEARCH done; audit after) | 1st (risk-first) | #2 (per-cell marker — scoped out → candidate US-44.5); #5 (methodology wording at close-out) |
| US-44.2 | `docs/product/stories/US-44.2-withheld-days-warning-direction.md` | P2 / F-2 | 7 | T-44.2.1..3 | gated (full route, trust disclosure; human decision 2026-09-07) | parallel with US-44.1 | #6 (methodology wording at close-out) |
| US-44.3 | `docs/product/stories/US-44.3-benchmark-outage-preserves-portfolio-performance.md` | P3 / F-3 | 9 | T-44.3.1..5 (T-44.3.1 DESIGN, blocks impl) | gated (RESEARCH done; audit after) | after US-44.1, before US-44.4 | #3 (valuation calendar → T-44.3.1; algorithm open); #7 (benchmark-outage rule unwritten) |
| US-44.4 | `docs/product/stories/US-44.4-selectable-comparison-benchmark.md` | P4 / F-4 | 8 | T-44.4.1..5 | touched; NOT express-eligible (schema hook) | last (risk-ordered behind US-44.3) | none blocking; T-44.4.2 may need a focused quant RESEARCH pass |

Ticket ordering within each story is contracts-before-consumers, with tests as
their own ticket and a docs close-out ticket last:

- **US-44.1:** T-44.1.1 backend gate → T-44.1.2 frontend grid tolerance →
  T-44.1.3 tests → T-44.1.4 docs/methodology.
- **US-44.2:** T-44.2.1 frontend copy → T-44.2.2 tests → T-44.2.3 docs.
- **US-44.3:** T-44.3.1 DESIGN (blocks) → T-44.3.2 backend split → T-44.3.3
  frontend tolerance → T-44.3.4 tests → T-44.3.5 docs/methodology.
- **US-44.4:** T-44.4.1 schema+route → T-44.4.2 backend trust/return-basis →
  T-44.4.3 frontend selector → T-44.4.4 tests → T-44.4.5 docs.

## Open decisions carried into the stories

Reproduced from `03-delivery-brief.md` § Open decisions. This lane resolved none
of them. Decisions 1, 4 and 8 were already settled by the work order / a recorded
human decision and are noted where they bear on a story.

- **#2 — P1 disclosure shape (US-44.1).** Does a month that dropped a withheld
  interior day need its own visible marker (a per-cell flag, a footnote), or does
  inheriting the run-level withheld-return disclosure suffice? A schema flag
  would pull the schema hook into US-44.1 and may split it. US-44.1 is drafted on
  "run-level disclosure suffices" and puts the marker out of scope; a visible
  marker is candidate successor **US-44.5**. (`02-quant-research.md` § Methodology
  gaps (b).)
- **#3 — P3 valuation calendar (US-44.3).** `valuation_dates` is derived from
  `benchmark_rows` (`dashboard_history_engine.py:313`); a benchmark-independent
  trading calendar must be designed before the line-304 collapse can be removed.
  Resolved into **T-44.3.1** (tech-lead DESIGN pass, confirmed by human decision
  2026-09-07); the algorithm choice remains open for that pass.
  (`01-recon.md` § risks; `02-quant-research.md` § P3.)
- **#5 — P1 methodology resolution (US-44.1).** Confirm the fix is "exclude the
  withheld day from the month's product" (preserves the chaining identity) rather
  than "withhold the whole month". `02-quant-research.md` § P1 is confident;
  US-44.1's ACs are written to it; the human ratifies at close-out because it is
  a `financial-methodology.md` § "Monthly Returns (Dashboard)" change.
  (`02-quant-research.md` § Methodology gaps (a).)
- **#6 — P2 signed-interpretation doc wording (US-44.2).**
  `financial-methodology.md` § "Publication rungs" documents the withheld-return
  impact only through an understatement example; the general signed reading needs
  a one-sentence addition. Docs lane at US-44.2 close-out; human confirms the
  wording. (`02-quant-research.md` § Methodology gaps (c).)
- **#7 — P3 methodology rule (US-44.3).** No section states that a total
  benchmark-history outage must still publish portfolio-economics on the imported
  dashboard path. Guardrails 3 and 4 imply it; the operative rule is unwritten.
  The human decides the rule before or during US-44.3; the docs lane writes it at
  close-out. (`02-quant-research.md` § Methodology gaps (d).)

## Assumptions and risks

- **Story home.** The work order directs file creation at
  `docs/product/stories/`, so this lane treats that as the story home. That
  resolves the producer's **Open decision 1** only for the story files; the
  PRD/roadmap surface deleted in `ce9c97d` is unreplaced and the `.agentic`
  product/project packs still point at deleted paths — those remain for the human
  and the docs lane.
- **Epic number and grouping.** Assumed Epic 44 and one epic for all four points
  (producer's Open decision 8; producer recommended it, Epic 34 precedent).
  Status assumed `Backlog` — the order did not say Epic 44 was pulled into the
  active phase.
- **P1 repro on trust.** The "+100% monthly return" figure comes from the
  reporter via `01-recon.md`, which confirmed the code path but built no runtime
  repro. US-44.1's ACs target the confirmed defect (the monthly path ignores
  `return_is_publishable` and the terminal correction), not the magnitude.
- **US-44.4 shape.** It spans a schema/route contract change and a new UI
  selector interaction model. The story pack flags that shape for a possible
  backend-contract / UI split; the producer scoped it as one story and this lane
  did not split it. If T-44.4.1's schema surface grows, the split is the
  producer's call.
- **US-44.4 AC5.** "Honest, non-verified return basis" for a non-allowlisted
  benchmark — no brief names the specific basis; `01-recon.md` only establishes
  it cannot be `verified_total_return`. Left for the design / quant pass.
- **No substantive disagreement with either brief.** One point of care: US-44.3
  AC3 keeps dashboard max-drawdown conditional on its own existing withholding
  policy, because `02-quant-research.md` § P3 lists it as benchmark-independent
  *and* separately gated — the story should not overstate what it delivers there.
- **House format.** `capabilities/story.md` § Files names `_TEMPLATE.md`,
  `README.md` and `epic-roadmap.md`, all deleted in `ce9c97d`. Format and
  register were taken from `ref/story-format-US-43.3.md` and
  `ref/story-format-US-43.4.md`. See `pack_corrections`.
