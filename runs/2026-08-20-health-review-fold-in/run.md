# RUN 2026-08-20-health-review-fold-in
request:   I ran a project health review and produced docs/product/review-2026-08-20-findings.md with 8 findings (F-R1 to F-R8). Fold these into the roadmap properly — dedupe against what's already known and open, and tell me whether this is one epic or several.
story:     NONE
status:    CLOSED
story:     .agentic/runs/2026-08-20-health-review-fold-in/04-stories.md (US-36.1/36.2/36.3, human-approved 2026-08-20)
express:   no

## Artifacts
| # | lane | mode | agent | artifact | status | verdict |
|---|------|------|-------|----------|--------|---------|
| 01 | recon | — | scout | 01-scout.md | DONE | — |
| 02 | product | — | producer | 02-delivery-brief.md | DONE | — |
| 03 | docs | — | docs-engineer | 03-docs.md | DONE | — |
| 04 | story | — | story-author | 04-stories.md | DONE | — |
| 05 | design | DESIGN | tech-lead | 05-technical-plan.md | DONE | — |
| 06 | backend | — | backend-engineer | 06-backend-T36.1.1.md | DONE | — |
| 07 | backend | — | backend-engineer | 07-backend-T36.2.1a.md | DONE | — |
| 08 | docs | — | docs-engineer | 08-docs-US36.3.md | DONE | — |
| 09 | test | — | test-engineer | 09-test-T36.3.2b.md | DONE | — |
| 10 | test | — | test-engineer | 10-test-T36.2.1b.md | DONE | — |
| 12 | test | — | test-engineer | 12-test-T36.1.2.md | DONE | — |
| 13 | docs | — | docs-engineer | 13-docs-T36.1.3.md | DONE | — |
| 14 | integration | INTEGRATION | tech-lead | 14-integration.md | DONE | PASS |
| 15 | review | — | reviewer | 15-review.md | DONE | PASS |
| 16 | docs (close-out) | — | docs-engineer | 16-docs-closeout.md | DONE | — |
| 11 | backend | — | backend-engineer | 11-backend-T36.2.2.md | DONE | — |

## Open
- Working-state check done in main session (not a lane order, read-only): `python scripts/run_all_tests.py` green — 331 frontend, backend pytest, tsc, dead-code gate all passed.
- **Alarming finding from scout, not yet dispatched to a fix lane:** CLAUDE.md currently asserts F-R1 was "fixed 2026-08-20" via a git-level `scripts/githooks/pre-commit` hook — that hook, and `scripts/hooks/git_pre_commit.py`, do not exist anywhere in the repo (confirmed via Glob/Grep). The findings doc's own "corrected" Disposition table also claims CLAUDE.md was corrected to stop making this claim — that correction did not happen either. Second-order false-claim, same failure mode the review doc was trying to catch. Surfaced to producer for placement, not fixed by orchestrator.
- pack_correction against `.agentic/projects/portfolio/project.md` "Mechanical gates" section — DONE (order 03), applied urgently pre-epic per human approval, not deferred to close-out.
- CLAUDE.md correction — DONE (order 03), same urgent pre-epic fix.
- Both corrected files now cite "Epic 36 (F-R1)" — Epic 36 does not exist in the roadmap/tech-debt-register yet. Must be created at docs close-out so the citation resolves.
- Open decision still unresolved (human, not yet asked): what to do with `docs/product/review-2026-08-20-findings.md`'s own second error (false claim that 6 findings are logged in tech-debt-register.md). Recommend marking superseded/historical at close-out, not deleting.
- **Lane-routing correction applied by orchestrator to tech-lead's plan**: the plan bundles `test_commit_gate.py` (T-36.1.2) and `test_audit_dependencies.py` (part of T-36.2.1) into the "backend-engineer" track, but both are new files under `app/tests/**`, which `project.md`'s routing table assigns exclusively to `test-engineer` ("the only lane that should be editing test files"). Splitting those into separate test-engineer orders when dispatching — no technical redesign needed, pure lane assignment.
- T-36.3.5 (retire findings doc) and Epic 36 PRD creation both deferred to the close-out docs dispatch (Step 10), per delivery-model convention that the docs lane reconciles roadmap/PRD/story index only after engineering + gates pass — resolves the plan's step 8/9 dependency naturally.
- **Real finding surfaced by order 07's design-verification run (out of scope for this epic, flagging for the human):** a live `pip-audit`/`npm audit` run (done locally to verify the classifier's marker list, not part of the network-free gate) found genuine advisories against currently-pinned backend packages (`starlette==0.48.0`, `pypdf==6.9.1`, `python-multipart==0.0.20`, `pydantic-settings==2.13.1`, `python-dotenv==1.1.1`) and one low-severity transitive frontend package (`@babel/core`). Untouched per this ticket's non_goals — this is exactly what US-36.2's scheduled workflow (T-36.2.2, now built) will surface for real once it runs, but the human should know now rather than wait for the first scheduled run.
- **Integration gate PASSED (order 14).** No BLOCKING findings, no CRs filed. 3 SHOULD_FIX carried to close-out: (1) `audit_dependencies.py`'s `main()` cross-ecosystem priority rule untested; (2) `_commit_gate.changed_files()`'s rename-entry parsing untested; (3) npm-network-error marker text unverified against a real failure (only documented conventions). Plus an operational note: concurrent lanes sharing `.claude/.last-test-pass` during this run is a real race risk for future concurrent dispatches, not an actual defect this run (all PASS claims independently re-verified).
- **Acceptance gate PASSED (order 15).** All 20 in-scope ACs verified by direct inspection, 23 new tests re-run independently green.
- **Close-out done (order 16).** Epic 36 PRD + 3 story files created; roadmap/story index updated; findings doc marked superseded (preserving its own second self-authored error as audit trail); backend.md pack corrected. Judgment call: the 4 SHOULD_FIX/risk items logged in epic-roadmap.md's "Open items" rather than tech-debt-register.md (out of that file's file-scope this order, and its stated convention is narrower than these items) — flagged for the human to redirect if desired.
- **New findings surfaced by docs-engineer during close-out, not fixed (same F-R7 class this epic just closed for Epic 24):** Epic 32's and Epic 35's PRDs still say "Status: Active" despite being Completed; `docs/product/stories/README.md` labels 5 completed epics "(active)". Candidate for a small future hygiene story.
- **RUN CLOSED.** 16 dispatches total. Nothing left blocking.
- Ground truth vs. findings doc's own "corrected" Disposition table: F-R1, F-R3, F-R5, F-R6, F-R7, F-R8 are claimed "logged in docs/tech-debt-register.md" but grep for "F-R" across `docs/` finds zero matches outside the findings doc itself — the correction pass fabricated the same class of claim it was created to fix, just smaller. Only F-R2 (dup of US-26.3) and now-suspect F-R4 (dashboard-fields.md already contains the entry it claims is missing — needs re-verification, git-history-blind) are not straightforwardly "still open, nowhere recorded."

## Rounds
- (none yet)
