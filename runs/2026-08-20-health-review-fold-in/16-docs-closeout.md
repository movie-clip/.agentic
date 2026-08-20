REPORT 2026-08-20-health-review-fold-in/16
status:      DONE
verdict:     NONE

changed:
  - docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md — NEW. Epic PRD: the 8 findings and their disposition (F-R1/F-R3/F-R5/F-R6/F-R7/F-R8 folded into US-36.1-3, F-R2 deduplicated against US-26.3, F-R4 dropped as false-as-written), the tech lead's design decisions, both gate verdicts (PASS/PASS), and a dedicated "meta-finding" section recording the false "fixed 2026-08-20" claim and its two corrections during this run.
  - docs/product/stories/US-36.1-blocked-commit-stays-blocked.md — NEW. Status: Done. ACs/tickets ticked against what the gates confirmed shipped (git-level hook, not a matcher mirror); Outcome section names the 2 carried SHOULD_FIX items.
  - docs/product/stories/US-36.2-dependency-vulnerability-scan.md — NEW. Status: Done. ACs/tickets ticked; Outcome section names the untested `main()` priority rule and the unverified npm-failure marker text.
  - docs/product/stories/US-36.3-docs-match-the-repo.md — NEW. Status: Done. ACs/tickets ticked including AC8 (findings-doc supersession, landed in this same pass) and AC9 (the new mechanical route-inventory test).
  - docs/product/stories/README.md — added an "Epic 36 — Findings-First Doc & Gate Hygiene (complete)" section with all 3 stories, inserted above the Epic 35 section (most recent first, matching existing order).
  - docs/product/epic-roadmap.md — added "## Completed Epic: Epic 36" section (PRD link, story snapshot, slice log, 3 entries) above the Epic 35 section; flipped the top summary ("Updated: 2026-08-20", most-recently-shipped now names Epic 36, "No epic is active" paragraph rewritten around Epic 36); added two new "Open items" bullets (the 4 SHOULD_FIX/risk items from the integration gate, and the real dependency-vulnerability findings surfaced by US-36.2's design-verification runs) — see `risks` for why these landed in "Open items" rather than `docs/tech-debt-register.md`.
  - docs/product/review-2026-08-20-findings.md — added a "Superseded (2026-08-20)" blockquote at the top, pointing at the new Epic 36 PRD as the live record. File otherwise untouched — its own "Correction" section (including its second, self-authored tech-debt-register error) preserved exactly as-is, per the work order's explicit instruction.
  - <agenticRoot>/projects/portfolio/capabilities/backend.md — added a new "## Gotchas that will bite you" section (mirroring `capabilities/testing.md`'s existing heading of the same name — backend.md had no such section before) containing the queued `core.filemode=false` / `git add --chmod=+x` pack correction, verified against the code before applying (see `pack_corrections` below).

verification:
  command:   Grep-based checks named in the work order (4 checks, run via the Grep tool against each target file)
  result:    PASS
  detail: |
    (1) `grep -rn "F-R1|F-R3|F-R5|F-R6|F-R7|F-R8" docs/product/epic-roadmap.md`
        → 6 matches (lines 54-56, 87, 108, 131, 149), all inside the new Epic
        36 top-summary paragraph and slice-log entries.
    (2) `grep -n "superseded|Epic 36" docs/product/review-2026-08-20-findings.md`
        → 2 matches: line 8 ("superseded — preserved as the audit trail...")
        and line 12 ("**Epic 36 — Findings-First Doc & Gate Hygiene**,
        specifically..."). Note: my first pass used "SUPERSEDED" (uppercase)
        and only the file path (not the literal words "Epic 36"), which the
        case-sensitive grep this AC names would have missed — caught by
        running the check myself before reporting, not assumed; fixed by
        lower-casing "superseded" in the running prose and adding an explicit
        "Epic 36 — Findings-First Doc & Gate Hygiene" mention.
    (3) `grep -n "core.filemode" <agenticRoot>/projects/portfolio/capabilities/backend.md`
        → 2 matches (lines 140, 146), inside the new "Gotchas that will bite
        you" section.
    (4) Directory listing (`Glob`) confirms all four new files exist:
        `docs/product/prd/epic-36-findings-first-doc-and-gate-hygiene.md`,
        `docs/product/stories/US-36.1-blocked-commit-stays-blocked.md`,
        `docs/product/stories/US-36.2-dependency-vulnerability-scan.md`,
        `docs/product/stories/US-36.3-docs-match-the-repo.md`.

    Not run: `python scripts/run_all_tests.py` and
    `<agenticRoot>/scripts/check_report.py` — neither is available as a tool
    in this session (no Bash/execute tool granted to this lane's dispatch),
    and the work order's own `verification` field named only the grep-based
    checks above, consistent with this being a documentation-only close-out
    order that changes no test-affecting file.

contract_notes:
  - none. No `app/schemas/`, TS type, or production code file was touched by
    this order — every change is under `docs/**` or the capabilities pack.

pack_corrections:
  - APPLIED — `<agenticRoot>/projects/portfolio/capabilities/backend.md`: the
    queued `core.filemode=false` / `git add --chmod=+x` entry from
    `pack-corrections.md` (filed by order 06). Verified before applying, not
    just copied: cross-checked against the tech-lead integration gate's own
    independent confirmation (`git ls-files --stage scripts/githooks/pre-commit`
    → index mode `100755`) that the workaround was applied correctly in
    practice. Applied as a new "Gotchas that will bite you" section (backend.md
    had none; `capabilities/testing.md` already uses this exact heading, so
    reused it rather than inventing a new one) — the replacement wording is
    the queued entry's own text, lightly reformatted to fit prose rather than
    verbatim-pasted, per the pack's instruction to apply the replacement
    wording, not a paraphrase of the *substance* (paths, mechanism, fix all
    unchanged from the queued entry).
  - ALREADY APPLIED (not by me) — the other two `pack-corrections.md` entries
    (`<agenticRoot>/projects/portfolio/project.md` and repo-root `CLAUDE.md`,
    both "Mechanical gates" sections) were dispatched urgently pre-epic
    (order 03) and corrected a second time once the real fix landed
    (T-36.1.3, order 13) — confirmed still correctly applied by direct read
    during this pass; nothing further needed from this order.

handoff:
  - "**Judgment call, not in this order's file scope: the 4 SHOULD_FIX/risk
    items from the integration gate were NOT logged in
    `docs/tech-debt-register.md`.** That file was not in this work order's
    `scope` list (only `backend.md` was named for pack corrections), and its
    own stated convention ('A single living catalog of (a) dead/unused code
    to remove and (b) hardcodes/anti-patterns to improve') is narrower than
    what these 4 items are — untested code paths and process/operational
    notes, not dead code or a hardcode/anti-pattern (only one precedent row
    in that file, a `missing-coverage` category item, is close). I recorded
    all 4 directly in `epic-roadmap.md`'s 'Open items' section instead,
    which is where this project already records epic-scoped deliberately-left-
    open items (Epic 34's F-1a/F-10/F-12 precedent) and is unambiguously in
    scope. If the human wants these formally registered in
    `docs/tech-debt-register.md` as well, that's a small follow-up, not done
    here."
  - "AC8 (US-36.3) is satisfied: `docs/product/review-2026-08-20-findings.md`
    now reads explicitly superseded, pointing at the new Epic 36 PRD."
  - "**Two pre-existing, out-of-scope staleness findings noticed while
    building the PRD/roadmap precedent, not fixed:** (1) both
    `docs/product/prd/epic-32-project-hygiene-and-agent-docs.md:3` and
    `docs/product/prd/epic-35-market-data-cache-resilience.md:3` still read
    `**Status:** Active` even though both epics are Completed per
    `epic-roadmap.md` — the exact F-R7 class of gap this very epic fixed for
    Epic 24, still live on two other closed epics' own PRDs. (2)
    `docs/product/stories/README.md`'s section headers for Epic 35, Epic 34,
    Epic 32, Epic 26 and Epic 24 all still read `(active)` despite every one
    being Completed. Neither was in this order's scope (`README.md`'s DoD was
    'add the three new stories to the index,' not 'fix every stale label in
    the file'), so neither was touched — flagging for a future small
    doc-accuracy story rather than silently tidying it in this pass."
  - "Epic 36's own PRD status header was set to `Completed (closed
    2026-08-20)` at creation time (not `Active`, then flipped later) — since
    the epic was already closed by the time this order created the file,
    deliberately not repeating the F-R7 staleness pattern the two PRDs above
    show."

risks:
  - "I could not run `python <agenticRoot>/scripts/check_report.py` or
    `python scripts/run_all_tests.py` myself — this lane's dispatch granted
    only Read/Write/Edit/Glob/Grep, no shell-execution tool. The work order's
    own `verification` field named only grep-based checks (all 4 run and
    reported above), consistent with a docs-only close-out order, so this is
    not a gap against what was asked — but the orchestrator's own
    `check_report.py` pass on this artifact is the first independent
    structural check of this report's shape."
  - "The 'superseded' grep check initially failed on my first draft (case
    mismatch + missing literal 'Epic 36' text) — caught and fixed by actually
    running the check before reporting PASS, not assumed from having written
    prose that read as satisfying it. Recording this because it's exactly the
    class of self-check discipline this epic's own subject matter (a claimed
    fix that wasn't verified) argues for."
  - "The two out-of-scope stale-PRD-status findings and the stories/README.md
    '(active)' labels (see `handoff`) are real drift of the same class Epic
    36 exists to close, on files this specific order was not scoped to touch.
    Not fixed here; not silently ignored either — recorded for whoever scopes
    the next small hygiene pass."
