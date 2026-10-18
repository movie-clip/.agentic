REPORT 2026-10-16-tracer-bullet/11
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   git -C C:\projects\investments\.agentic diff --stat -- projects/los-tres/capabilities/
  result:    PASS
  detail:    diff --stat: 3 files, 45 insertions, 28 deletions (testing.md unchanged since 09). Anchor: protocol/authoring.md. F1-F4 resolved; 1 new BLOCKING (rule 5); 5 SHOULD_FIX carried from 09.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F1 resolved: backend.md § Index l.17 lists Layout under Always read, so the port rule at § Layout l.33 is always read.
  - F2 resolved: the same edit makes backend.md § Layout l.31 and l.33 always read.
  - F3 resolved: frontend.md § Index l.18 lists Layout under Always read; the component import ban at § Layout l.32 is always read.
  - F4 resolved: frontend.md § Next.js and i18n (l.45-49) holds the three moved bullets, is listed under Always read at l.18, and can be found by name.
  - BLOCKING F5 rule 5 (authoring.md § Indexing a pack or profile) backend.md l.11-19: file is now read in full yet opens with ## Index and l.13-15 "read what your order touches", a claim skipping is safe.
  - F5 cont.: authoring.md says a full-read file opens with ## Contents, and an index is made only where skipping is safe. Caused by the F1/F2 fix, so it continues that count (round 2).
  - F5 fix: replace l.11-19 with "## Contents", one line saying the file is read in full, and the four section names; drop the skip sentence at l.13-15.
  - SHOULD_FIX rule 8 carried: testing.md § Running tests l.27 is a ~900-char multi-fact paragraph; command-to-needs belongs in a table.
  - SHOULD_FIX rule 8 carried: testing.md § Running tests l.27 and l.33 state the e2e base-URL rule twice.
  - SHOULD_FIX rule 8 carried: frontend.md § Next.js and i18n l.47-49 bullets each exceed 200 characters and carry several facts.
  - SHOULD_FIX rule 8 carried: "no literal site name" is in frontend.md l.41 (Spanish market conventions) and l.47 (Next.js and i18n); keep it once.
  - SHOULD_FIX rule 8 carried: backend.md § Layout l.29-31 are multi-fact paragraphs; the pinned versions would read better as a table.

skill_calls:
  - none

risks:
  - The site-name duplicate now spans two sections, which also meets the letter of rule 5.2; carried as SHOULD_FIX because the order says 09's rule-8 items are not re-raised.
  - The duplicate misleads no lane: l.47 is always read and broader than the conditional l.41.
  - F5 does not change what the lane reads today, since l.17 lists every section; it is filed because the rule names the form and l.13-15 contradicts l.19.
  - UNVERIFIED: every code premise listed in 09 § risks still stands; the moved text was not checked against the bound repo.
