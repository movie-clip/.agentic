REPORT 2026-08-20-health-review-fold-in/03
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\portfolio\CLAUDE.md — "Mechanical gates (CI + hooks)" section, "Commit gate hook" bullet: removed the false claim that a git-level `scripts/githooks/pre-commit` hook (calling `scripts/hooks/git_pre_commit.py`) is the "actual enforcement boundary" and was "fixed 2026-08-20" (with citation to the findings doc's F-R1). Replaced with accurate text: only `scripts/hooks/pre_commit_gate.py` (Claude Code PreToolUse, matched on `Bash` only) exists; it does not fire for `git commit` via a non-Bash tool (e.g. PowerShell); no git-level enforcement exists; the gap is open, tracked under Epic 36 (F-R1).
  - C:\projects\investments\.agentic\projects\portfolio\project.md — "Mechanical gates — never bypass" section, "Commit gate hook" bullet: same correction applied verbatim in substance (only the Claude Code PreToolUse hook exists; no git-level hook; gap open, tracked under Epic 36 F-R1).

verification:
  command:   grep -rn "githooks\|git_pre_commit\|fixed 2026-08-20" "C:\projects\investments\portfolio\CLAUDE.md" "C:\projects\investments\.agentic\projects\portfolio\project.md"
  result:    PASS
  detail:    Ran as two separate ripgrep invocations (one per file) with pattern `githooks|git_pre_commit|fixed 2026-08-20`. Both returned "No matches found" after the edit. (Before the first-pass edit, the same grep matched both files — I initially wrote replacement prose that named `scripts/githooks/` and `git_pre_commit.py` explicitly, as *proof of absence*, which re-triggered the pattern; the final wording drops those literal path strings entirely and states the gap functionally instead — "no equivalent enforcement at the git level in this repo" — which is both accurate and grep-clean.)

contract_notes:
  - none — this is a doc-only correction to two onboarding files; no schema, type, or field-level artifact changed.

pack_corrections:
  - none — the pack correction this order exists to apply is fully reflected in `changed` above (project.md's own text was the pack correction target). No further pack file needs updating.

handoff:
  - The corrected text in both files states the gap is "tracked under Epic 36 (F-R1)" per the work order's instruction. Epic 36 does not yet exist in `docs/product/epic-roadmap.md` or `docs/tech-debt-register.md` as of this order — per this order's non_goals, I did not create it (that's out of scope: "epic/story creation happens via story-author next, not this order"). Whoever creates Epic 36 should confirm the citation `(F-R1)` in both corrected files still resolves once the epic/register entry exists, and should note that `docs/product/review-2026-08-20-findings.md` still contains a separate, second self-authored error (its own "Correction"/Disposition table falsely claims 6 findings are "logged in docs/tech-debt-register.md") — untouched here per this order's explicit non_goal, and named in 02-delivery-brief.md's open_decisions as a human call.
  - Only the "Commit gate hook" bullet was touched in each file. The surrounding bullets (CI, schema hook, dead-code gate, PR template) were read and left untouched — no other false claim was found nearby during this pass.

risks:
  - none — this was a narrow, mechanically-verified doc correction with an exact grep gate; no ambiguity encountered in either target file.
