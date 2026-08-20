# RUN 2026-08-20-us36.1-followup
request:   Fold the post-close US-36.1 follow-up into Epic 36. AC6 was under-specified — it was marked satisfied by a test suite that never issued a git commit, so it proved the staleness logic but not that the gate fires. Code fix is already landed and green in the working tree (githooks wrapper interpreter discovery, ensure_git_hooks_wired target check, 4 new tests in test_commit_gate.py, hook staged 100755). US-36.1's acceptance-criteria block is ALREADY updated with the corrected AC6 plus new AC7/AC8 — do not redo it. Remaining: test plan count 10 to 14, a T-36.1.4 ticket, the Outcome section, the Epic 36 PRD record, and the roadmap slice log.
story:     docs/product/stories/US-36.1-blocked-commit-stays-blocked.md (already amended by human/prior session with corrected AC6 + new AC7/AC8 — confirmed present, not redone here)
status:    CLOSED
express:   no

## Artifacts
| # | lane | mode | agent | artifact | status | verdict |
|---|------|------|-------|----------|--------|---------|
| 01 | integration | INTEGRATION | tech-lead | 01-integration.md | DONE | PASS |
| 02 | review | — | reviewer | 02-review.md | DONE | PASS |
| 03 | docs (close-out) | — | docs-engineer | 03-docs-closeout.md | DONE | — |

## Open
- Orchestrator independently verified (not trusted blindly, given this project's own history of false "already fixed" claims): `test_commit_gate.py` has 14 `def test_` functions (confirmed via grep); `scripts/githooks/pre-commit` contains interpreter-discovery logic (tries `python` then `python3`, comment explaining Windows Python-Store-stub and bare-python-absence gotchas); `scripts/run_all_tests.py`'s `ensure_git_hooks_wired()` has a target-existence-check comment ("Never set the config without verifying the target exists"); `git ls-files --stage scripts/githooks/pre-commit` shows mode `100755`; `python scripts/run_all_tests.py` passed clean (dead-code gate clean, "All tests passed.").
- Prior run `2026-08-20-health-review-fold-in` is CLOSED — this is a genuinely new post-close amendment, not a resume.

## Rounds
- (none yet)

## Open (carried to close-out human-visibility)
- Nothing from this follow-up is on `HEAD` yet — `scripts/githooks/pre-commit` is staged (A), `_commit_gate.py`/`git_pre_commit.py`/`test_commit_gate.py` are untracked, `pre_commit_gate.py`/`run_all_tests.py` are modified-unstaged. Expected under "no agent commits," but the story's "Done"/Outcome wording could read as already-shipped to a human who doesn't check git status. Flag at final report.
- Minor test-precision asymmetry (reviewer, non-blocking): `test_real_git_commit_is_blocked_when_marker_missing` checks only the generic "COMMIT BLOCKED" prefix, not the specific marker-missing substring its sibling stale-file test checks. Property still covered by other tests. Candidate for a small follow-up ticket, not urgent.
- Docs close-out left the Epic 36 PRD's "Gate verdicts" line reading "US-36.1 (6/6)" — now stale since the story carries 8 ACs. Deliberate scope decision (order named only "add an addendum," not "edit that line") — flag for a future small pass.
- RUN CLOSED. 3 dispatches total.
