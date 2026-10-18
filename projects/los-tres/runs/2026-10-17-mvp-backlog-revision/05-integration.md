REPORT 2026-10-17-mvp-backlog-revision/05
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   cd C:\projects\investments\los-tres && git diff --stat cca91f4..a7d77b6
  result:    PASS
  detail:    1 file changed (docs/product/mvp.md), 4 insertions, 4 deletions; only the CR-1 bullet. Full gate not re-run: change is one prose bullet in Markdown that no code or test reads (grep for mvp.md in ts/tsx/json/mjs/js: no hits). Gate last exited 0 at cca91f4 (report 03).

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

skill_calls:
  - none

risks:
  - docs/product/mvp.md § Search and browsing still says product pages carry schema.org Product/AggregateOffer data without the no-offers exception. The bullet in § Product and offers now states the exception, so a reader of both can reconcile them. Not blocking; a cross-reference there is the owner's call.

## Orchestrator brief
Verdict PASS: CR-1 is satisfied; no new finding is blocking.
- Diff cca91f4..a7d77b6 touches only docs/product/mvp.md, the "When a product loses all its offers" bullet (4+, 4-).
- The bullet now names both changes: the offer list shows "No offers right now" with the last known lowest price and date, and the structured data is omitted. "Only" and "exactly" are gone, so the contradiction is removed.
- The ruled meaning is kept: page, text, image, price history and indexing stay.
- Full gate not re-run: the only change is one Markdown prose bullet, and grep finds no code or test that reads mvp.md. Gate was exit 0 at cca91f4.
- Sections below: CR-1 recheck.

## CR-1 recheck
Current text, mvp.md lines 66-69: "its page stays as it is (text, image, price history, still indexed), with two changes. The offer list shows "No offers right now" with the last known lowest price and its date, and the structured data is omitted while the product has no offers."

CR-1 "What satisfies it" asked that the bullet name both changes, or state the structured-data omission as an exception. It does the first: "with two changes" followed by both. A story author reading only this bullet can tell that S8.4 must drop the JSON-LD when offers are zero.

Scope fence held: git diff --name-only shows only docs/product/mvp.md, and the hunk is limited to that bullet. The working tree was clean at the start (git status).

Gate not re-run. The only change since the exit-0 run at cca91f4 is that one bullet. A grep of ts, tsx, json, mjs and js files outside node_modules, .next and dist for "mvp.md" returns nothing. The only other mentions are prose in CLAUDE.md and docs/decisions/0007. No test or build step reads the file.
