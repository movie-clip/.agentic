REPORT 2026-10-18-s1-1-go-redirect/07
status:      DONE
verdict:     NONE

changed:
  - los-tres/docs/decisions/0009-click-log-and-analytics.md — D-2 addendum under Consequences, as one bullet carrying the two approved sentences verbatim
  - .agentic/projects/los-tres/capabilities/backend.md — Layout: error-code.ts, clicks/ files, /go route rule; Guardrails (5): click-row rule and the demo-feed rule
  - .agentic/projects/los-tres/capabilities/frontend.md — Guardrails (2): "until /go ships" sentence replaced by the sponsored-anchor rule
  - .agentic/projects/los-tres/capabilities/testing.md — guardrail 5 bullet counting-rules note; go.ts helpers; vi.mock and `\b` gotchas; page.route redirect gotcha under Running tests
  - .agentic/projects/los-tres/capabilities/architecture.md — Click log seam names its files; routing row for Proposing a stack reworded off "not chosen"
  - .agentic/projects/los-tres/phases.md — removed the Contents bullet, the design row's stack clause and the whole § The stack run (pure-scope sentence included)
  - .agentic/projects/los-tres/project.md — lines 12-13 reworded to match § Building before the stack exists

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    docs order, verification NONE; grep for "not chosen" in the profile and packs finds only run artifacts

contract_notes:
  - docs/product/mvp.md § Outgoing clicks already states the counting rules and the limit; read, no edit needed.
  - CLAUDE.md § Commands is unchanged by S1.1 (no new command or variable); not edited.
  - No other file under docs/ makes a statement S1.1 turned false (grep for /go, click and no link across docs/); nothing else changed there.

pack_corrections:
  - none

handoff:
  - Protocol-lint (pending in run.md) should check phases.md, project.md and architecture.md, which this order edited.
  - project.md:119 Lane routing row for design still says "stack proposals"; not in the named lines, left for a later order.
  - capabilities/docs.md:5 still mentions "stack run that the owner approved"; outside scope, left.
  - phases.md build row still says "only once the stack it needs is recorded"; not keyed on "not chosen", left as written.

skill_calls:
  - none

risks:
  - architecture.md: pack-corrections said delete the Proposing a stack row; I reworded it instead (a choice no recorded decision covers) so the section stays findable by index. DoD allows either.
  - 0009 addendum is one bullet of two sentences, as written in 01-design; the stated limit (an unlisted bot still counts, best effort) is absent from 0009 per D-2. 06-review notes the gap; mvp.md:156-157 and counting.ts carry it.
  - Where 01-design and a later lane word the same change, the later lane's wording was used: backend.md Layout route sentence follows 02-backend, which reads the same as 01-design.
  - The 0009 edit matched a multi-line old string on a CRLF working copy and succeeded; the appended lines may carry LF endings. Check git diff for mixed endings.
  - Premise check: each correction was verified against the run's lane artifacts (02, 03, 04, 05) rather than re-read from src/, which is outside this order's scope.
