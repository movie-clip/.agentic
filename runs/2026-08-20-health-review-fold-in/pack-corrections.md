# Pack corrections — run 2026-08-20-health-review-fold-in

- **`<agenticRoot>/projects/portfolio/project.md`**, "Mechanical gates — never bypass" section
  (confirmed independently by both scout/01-scout.md and producer/02-delivery-brief.md):
  The text "The git-level `scripts/githooks/pre-commit` (wired via `core.hooksPath`, calling
  `scripts/hooks/git_pre_commit.py`) is the actual boundary — fires on every `git commit`
  regardless of invoking tool... a commit through another tool used to walk past it (fixed
  2026-08-20)" is FALSE. `scripts/githooks/` and `scripts/hooks/git_pre_commit.py` do not exist
  anywhere in the repo (confirmed via Glob + repo-wide Grep, both agents, independently).
  **Replacement wording:** state that only the Claude Code PreToolUse hook
  (`scripts/hooks/pre_commit_gate.py`, matched on `Bash` only) exists today; that it does not
  fire for `git commit` issued through a non-Bash tool (e.g. the PowerShell tool available in
  this environment); and that this gap is open, tracked as F-R1 under the newly-approved epic
  (Epic 36), not fixed.

- **Repo root `CLAUDE.md`**, "Mechanical gates (CI + hooks)" section: carries the identical
  false "fixed 2026-08-20" claim, with an added false citation to
  `docs/product/review-2026-08-20-findings.md` F-R1 (which itself, per that doc's own
  "Disposition" table, makes the same false claim). Same replacement as above, applied to this
  file.

**Scope note:** neither file is under `docs/**` or `capabilities/**`, the docs lane's normal
routing scope — this correction is dispatched as an explicit, human-approved exception due to
urgency (both files are live misinformation read by every future agent/human session that binds
to this project), not a routing change. See run.md for the approval record.

- **New learning (not a false-premise correction, but worth adding to `capabilities/backend.md`
  or `project.md`), from order 06 (T-36.1.1):** this checkout has `core.filemode=false`. A plain
  `git add` on a newly-created executable script (e.g. a `.sh`/POSIX hook wrapper) silently
  records it in the git index as mode `100644` (non-executable) even though the file has `chmod
  +x` on disk — verified directly via `git ls-files --stage`. Since git checkout applies the
  *stored* index mode on every clone regardless of that clone's own `core.filemode` setting, this
  silently ships a non-executable script that Linux's git hook runner (no `sh`-fallback the way
  Git-for-Windows has) skips without error — the exact "wiring exists but is inert" failure class
  Epic 36 exists to close, just at the file-mode layer. Fix: stage with
  `git add --chmod=+x <path>` for any new executable file added from a Windows dev box in this
  repo. Recommend adding this as a standing gotcha in the backend capability pack, not just this
  run's ledger, since it will recur the next time any script needs the executable bit.
