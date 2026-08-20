# RUN 2026-08-20-health-review-fold-in
request:   I ran a project health review and produced docs/product/review-2026-08-20-findings.md with 8 findings (F-R1 to F-R8). Fold these into the roadmap properly — dedupe against what's already known and open, and tell me whether this is one epic or several.
story:     NONE
status:    DISPATCHING
express:   no

## Artifacts
| # | lane | mode | agent | artifact | status | verdict |
|---|------|------|-------|----------|--------|---------|
| 01 | recon | — | scout | 01-scout.md | DONE | — |
| 02 | product | — | producer | 02-delivery-brief.md | DONE | — |
| 03 | docs | — | docs-engineer | 03-docs.md | DONE | — |
| 04 | story | — | story-author | 04-stories.md | DISPATCHED | — |

## Open
- Working-state check done in main session (not a lane order, read-only): `python scripts/run_all_tests.py` green — 331 frontend, backend pytest, tsc, dead-code gate all passed.
- **Alarming finding from scout, not yet dispatched to a fix lane:** CLAUDE.md currently asserts F-R1 was "fixed 2026-08-20" via a git-level `scripts/githooks/pre-commit` hook — that hook, and `scripts/hooks/git_pre_commit.py`, do not exist anywhere in the repo (confirmed via Glob/Grep). The findings doc's own "corrected" Disposition table also claims CLAUDE.md was corrected to stop making this claim — that correction did not happen either. Second-order false-claim, same failure mode the review doc was trying to catch. Surfaced to producer for placement, not fixed by orchestrator.
- pack_correction against `.agentic/projects/portfolio/project.md` "Mechanical gates" section — DONE (order 03), applied urgently pre-epic per human approval, not deferred to close-out.
- CLAUDE.md correction — DONE (order 03), same urgent pre-epic fix.
- Both corrected files now cite "Epic 36 (F-R1)" — Epic 36 does not exist in the roadmap/tech-debt-register yet. Must be created at docs close-out so the citation resolves.
- Open decision still unresolved (human, not yet asked): what to do with `docs/product/review-2026-08-20-findings.md`'s own second error (false claim that 6 findings are logged in tech-debt-register.md). Recommend marking superseded/historical at close-out, not deleting.
- Ground truth vs. findings doc's own "corrected" Disposition table: F-R1, F-R3, F-R5, F-R6, F-R7, F-R8 are claimed "logged in docs/tech-debt-register.md" but grep for "F-R" across `docs/` finds zero matches outside the findings doc itself — the correction pass fabricated the same class of claim it was created to fix, just smaller. Only F-R2 (dup of US-26.3) and now-suspect F-R4 (dashboard-fields.md already contains the entry it claims is missing — needs re-verification, git-history-blind) are not straightforwardly "still open, nowhere recorded."

## Rounds
- (none yet)
