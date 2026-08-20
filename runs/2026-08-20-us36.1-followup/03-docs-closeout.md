REPORT 2026-08-20-us36.1-followup/03
status:      DONE
verdict:     NONE

changed:
  - docs/product/stories/US-36.1-blocked-commit-stays-blocked.md — Test plan: "10 tests" → "14 tests" plus 2 new bullets describing the AC7 (real `git commit` subprocess) and AC8 (tracked-executable index check) tests. Tickets: added checked T-36.1.4 describing the interpreter-discovery hardening, `ensure_git_hooks_wired()`'s existence check, and the 4 new tests, referencing both gate PASS verdicts. Outcome: appended (did not replace) a new "Post-close follow-up (2026-08-20)" sub-entry recording why AC6 as originally written proved logic-not-reachability, what T-36.1.4 fixed, both gates' PASS verdicts, and the reviewer's two non-blocking notes (test-precision asymmetry, nothing on HEAD yet). Did not touch Story/Context/Design decision/Acceptance criteria sections.
  - docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md — added a "Post-close addendum (2026-08-20)" section (before "Success signals") recording that post-close review found AC6 under-specified, what was corrected (AC6 narrowed, AC7/AC8 added, T-36.1.4), and both gate PASS verdicts, pointing back at US-36.1's Outcome section for detail rather than duplicating it.
  - docs/product/epic-roadmap.md — added a new slice-log entry, "US-36.1 follow-up (2026-08-20)", at the top of Epic 36's slice log (most-recent-first ordering, ahead of the existing US-36.3 entry), in the established narrative style: what AC6 got wrong, why it matched F-R1's own failure mode, what AC7/AC8/T-36.1.4 added, both gates' independent verification detail, and the test-count delta (10 → 14).

verification:
  command: |
    grep -n "14 tests\|T-36.1.4" docs/product/stories/US-36.1-blocked-commit-stays-blocked.md
    grep -n "AC7\|AC8" docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md
    grep -n "T-36.1.4\|AC6" docs/product/epic-roadmap.md
  result:    PASS
  detail: |
    (1) story file — both terms present:
      102: `services/quant-engine/app/tests/test_commit_gate.py` (**14 tests** — 10
      159: [x] **T-36.1.4 — Prove the gate actually fires.** Post-close follow-up
      210: ### Post-close follow-up (2026-08-20) — AC6 was under-specified; T-36.1.4 closes the gap
      240: **T-36.1.4** implemented the fix this gap-closing found was actually needed

    (2) PRD — addendum present, both AC7 and AC8 named:
      157: (pre-existing line, unmodified — "(6/6), US-36.2 (5/5) and US-36.3 (9/9, AC8 ...")
      170: ("fails if the staleness logic regresses"), and AC7 (a real-`git commit`
      171: regression test) and AC8 (a tracked-and-executable check on

    (3) roadmap — new slice-log entry present:
      108-129: new "US-36.1 follow-up (2026-08-20)" entry (AC6/AC7/AC8/T-36.1.4
      all present in the new text); line 740 is a pre-existing, unrelated Epic-32
      "AC6" match from a different story, not touched by this order.

contract_notes:
  - none. No schema, TS type, or contracts doc is touched by this docs-only close-out.

pack_corrections:
  - none. `capabilities/docs.md` held up throughout — the "Auto vs flag-for-human"
    split, the slice-log narrative-style expectation, and "append, don't replace"
    guidance all matched what the order needed.

handoff:
  - The Epic 36 PRD's existing "Gate verdicts" section (line ~157) still reads
    "US-36.1 (6/6)" from the original pre-follow-up gate pass — now stale
    since the story has 8 ACs (AC6 corrected, AC7/AC8 added). I deliberately
    did not touch that line: the work order scoped this lane to "add a short
    dated addendum," not to edit the existing Gate verdicts section, and
    non_goals said not to touch anything beyond what's named. The new
    addendum section states the corrected picture in prose immediately above
    it, so the two sections are adjacent and mutually legible, but a future
    docs pass touching that PRD should update "(6/6)" to "(8/8)" (or similar)
    for exactness if this file is edited again.
  - Both new gate reports (`01-integration.md`, `02-review.md` in this run
    dir) are PASS with no BLOCKING findings and no contract notes — nothing
    else in the codebase needs reconciling from this follow-up.
  - The one still-open SHOULD_FIX item that touches this same area
    (`_commit_gate.changed_files()`'s rename-entry parsing has no dedicated
    test) was already recorded in `epic-roadmap.md`'s "Open items" section
    from the original integration gate; I did not duplicate it in the new
    slice-log entry, since it wasn't part of this follow-up's own change set.

risks:
  - none. Both gates in this follow-up passed cleanly (tech-lead INTEGRATION
    PASS, reviewer acceptance PASS) with no unresolved BLOCKING items, so
    there was no ambiguity about whether the story's boxes were safe to
    describe as satisfied. The one judgment call I made — leaving the PRD's
    pre-existing "(6/6)" gate-verdict count untouched rather than correcting
    it to match the now-8-AC story — is recorded above in `handoff`, not
    here, since it's a scope decision rather than something uncertain.
