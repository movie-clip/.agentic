REPORT 2026-10-18-s1-1-go-redirect/08
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   python C:\projects\investments\.agentic\scripts\check_report.py C:\projects\investments\.agentic\projects\los-tres\runs\2026-10-18-s1-1-go-redirect\ --require-heads
  result:    PASS
  detail:    exit 0, run.md and 01-07 ok; plugin validate passed; 4 BLOCKING, 4 SHOULD_FIX; 4 UNVERIFIED premises; anchor authoring.md (read in full) against the 6 files and their git diff; no "not chosen" left outside runs/

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1 (authoring.md § Two instructions may not disagree): testing.md:69, always-read, says a browser visit asserts no request leaves the app origin; testing.md:35 says the /go click-through asserts a request to the `.example` host. Fix: state the /go click-through exception in the :69 bullet, and move :35 into § Shared scaffolding and gotchas.
  - BLOCKING F2 (§ Two instructions may not disagree): frontend.md:62 makes each offer row's href `goPath(offerId)`, but frontend.md:32 bars components from `src/server` and lets a page import only read functions and `formatEuroCents`. Fix: add `goPath` (`src/server/clicks/go-path.ts`) to the page carve-out at :32 and say at :62 that the page maps it.
  - BLOCKING F3 (§ Two instructions may not disagree): phases.md:30 no longer fires design for a choice no decision covers and :31 holds build until it is recorded, yet project.md:102-103 and architecture.md:22 route that case to tech-lead DESIGN. Fix: add to phases.md:30 "or the request needs a choice no recorded decision covers (project.md § Building before the stack exists)".
  - BLOCKING F4 (§ Two instructions may not disagree): backend.md:24 and frontend.md:28 say report BLOCKED "only if" the plan names no directory or file; project.md:104-106 also requires BLOCKED for an uncovered framework or package-manager choice. Fix: drop "only" and cite project.md § Building before the stack exists. Predates this run's diff.
  - SHOULD_FIX (§ Writing for the reader you actually have): testing.md:81 joins two unrelated facts, the vi.mock failure-forcing recipe and the Python `\b` gotcha. Split into two bullets.
  - SHOULD_FIX (§ Writing for the reader you actually have): backend.md:57, the (5) bullet, now carries five facts in one bullet. Split one fact per bullet.
  - SHOULD_FIX (§ Writing for the reader you actually have): architecture.md:48, the Click log seam, packs five file roles into one parenthetical. Use sub-bullets or a table.
  - SHOULD_FIX (§ Writing for the reader you actually have): frontend.md:62 and testing.md:54 each add three facts to one bullet. Split one fact per bullet.

skill_calls:
  - none

risks:
  - UNVERIFIED: backend.md:28 and architecture.md:48 name `src/server/clicks/*` files and their roles; only go-path.ts and its import in page.tsx were opened.
  - UNVERIFIED: testing.md:80 `tests/support/go.ts` helper names and signatures were not opened.
  - UNVERIFIED: testing.md:35 claim that Playwright page.route does not intercept a navigation's redirect target.
  - UNVERIFIED: testing.md:81 claim that vi.mock with importOriginal and a vi.hoisted switch forces a failure in the real route.
  - Outside scope: capabilities/docs.md:5 still says "stack run that the owner approved", a procedure phases.md no longer defines.
  - project.md:94 heading "Building before the stack exists" now heads text saying the stack is recorded; it is always-read and cited by name at architecture.md:52, so not judged unfindable.
  - check_report printed over-400-char warnings (~) for pack_corrections bullets in 02-backend and 03-frontend yet exited 0; those artifacts are outside this verdict.
