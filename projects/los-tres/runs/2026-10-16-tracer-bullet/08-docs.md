REPORT 2026-10-16-tracer-bullet/08
status:      DONE
verdict:     NONE

changed:
  - capabilities/backend.md — applied 03 corrections 1-6 (stack line, Layout, delivery and pins, .env.example rule, import side effects, Next 16 env and port note); intro and Layout index row updated
  - capabilities/frontend.md — applied 04 corrections 1-5 (stack line, Layout, next-intl no-middleware, force-dynamic, plugin wrapper); intro and Layout index row updated
  - capabilities/testing.md — applied 05 corrections 1-6 including configs-never-import-tests/; intro and Running tests index row updated
  - docs/decisions/0010-slice-a-tooling-calls.md — new; records D-3 (npm, Node 22, test database, plain CSS) and nothing else

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only docs order, verification NONE; premises checked against the lane reports and the repo's decisions directory

contract_notes:
  - docs/decisions/0010 states the D-3 calls; CLAUDE.md § Stack was not touched (owner's), so it does not list npm, Node 22 or the plain-CSS interim.
  - 02-design § Pack corrections owed was fully covered by the lane corrections; the lanes' wording was used where both existed, so the design's "(confirm O-1 and O-2 answers)" aside was dropped.

pack_corrections:
  - none

handoff:
  - Open rows for the ledger (from 07-integration): Vite configLoader native warning, init-env and entrypoint exit 64 untested, TD-10 lint ban has no regression test, base URL rule held twice. Not written into any pack.
  - Slice B owner call still owed: styling system (O-4), recorded in docs/decisions/0010 as undecided.
  - The decisions directory skips 0003 and 0005; 0010 numbers after the highest existing, 0009.

skill_calls:
  - none

risks:
  - Removed the "No pack exists yet" intros in backend.md, frontend.md and testing.md, and reworded three index rows. Not in any correction, but left as written they would be false after the edits.
  - Dropped the sentence "No test calls a live network" from 05 correction 3 because testing.md § What must always be covered already says it; the fact now lives once.
  - Added a pointer line in testing.md § Running tests that CLAUDE.md § Commands is the authority for the command list; this is the old text's intent kept, not a new convention.
  - Did not verify premises against code with a shell; relied on 07-integration's gate PASS and the reports' stated verification.
