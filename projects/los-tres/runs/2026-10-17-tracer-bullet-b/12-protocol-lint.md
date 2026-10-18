REPORT 2026-10-17-tracer-bullet-b/12
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate <agenticRoot>/plugins/agentic-core; python <agenticRoot>/scripts/check_network_edit.py --verbose
  result:    PASS
  detail:    validate: passed. check_network_edit: 4 UNLINTED (warning, exit 0). Anchor: protocol/authoring.md. CR-1 and CR-2 resolved; 0 BLOCKING; 0 new SHOULD_FIX; 8 SHOULD_FIX carried from 08/10; 5 UNVERIFIED premise groups.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Verdict: testing.md PASS. Four-pack outcome for this run: backend.md PASS (08), frontend.md PASS (08), architecture.md PASS (08), testing.md PASS (12).
  - The three 08 passes stand: backend.md, frontend.md, architecture.md mtimes are 15:16-15:17, before 08 was written at 15:20; not re-judged (non_goals).
  - CR-1 RESOLVED (rule 9): testing.md l.65 scopes assertTestDatabase() to integration tests and helpers and carries the e2e exception in the same bullet; "development database" appears nowhere in testing.md.
  - CR-2 RESOLVED (rule 5): l.33 now ends "The e2e write rule is in § What must always be covered."; the restated rule is gone. The e2e write rule now lives only at l.65.
  - CR-2 fix caused no new finding: the l.33 pointer targets an always-read section, and l.65's "(§ Running tests)" points back only for where globalSetup is described.
  - Rule 9 re-read: no always-read section of testing.md or project.md now directs a different action from l.33 or l.65.
  - Rule 7: every command in testing.md is npm, docker compose or Playwright under Bash; test-engineer.md l.4 tools: "Read, Write, Edit, Glob, Grep, Bash, Skill, mcp__project__..." includes Bash.
  - SHOULD_FIX carried from 08/10, rule 8: testing.md § Running tests l.27 is still a ~1,100-char multi-fact paragraph; the commands-to-needs part belongs in a table.
  - SHOULD_FIX carried from 08/10, rule 8: the e2e base-URL rule is still stated twice, l.27 (E2E_BASE_URL default) and l.35 (never a literal base URL); keep it once.
  - SHOULD_FIX carried from 08/10, rule 8: testing.md l.35 "(`appBaseUrl()` is gone)" is still change history; delete the parenthesis.
  - SHOULD_FIX carried from 08, rule 8: frontend.md § Next.js and i18n l.52-55 bullets exceed 200 chars and carry several facts each.
  - SHOULD_FIX carried from 08, rule 8: "no literal site name" is in frontend.md l.46 and l.52; keep it in the always-read one.
  - SHOULD_FIX carried from 08, rule 8: backend.md § Layout l.28-36 are multi-fact paragraphs (l.28 ~900 chars); split into bullets, pinned versions as a table.
  - SHOULD_FIX carried from 08, rule 8: backend.md l.22 and frontend.md l.26 heading "Before the stack is recorded" sits over text saying it is recorded; rename.
  - SHOULD_FIX carried from 08, rule 8: architecture.md § The seams l.34-43 bullets now exceed 200 chars; move the paths into a seam-to-file table.

skill_calls:
  - none

risks:
  - This verdict certifies authoring only; no path, export or behaviour in the bound repo was opened.
  - UNVERIFIED: testing.md test-support file names and exports (global-setup.ts, db.ts resetDatabase/closeDb/assertTestDatabase, catalogue.ts, feeds.ts, network-off.ts, messages.ts).
  - UNVERIFIED: that assertTestDatabase() restricts writes to ${DB_NAME}_test (l.65).
  - UNVERIFIED: that tests/e2e/global-setup.ts runs import-feeds via docker compose run and is the only e2e database write (l.33, l.65).
  - UNVERIFIED: testing.md Vitest 5, vitest.config.mts, E2E_BASE_URL default and the Umami 307 at / claim.
  - UNVERIFIED: testing.md tests/unit/seams.test.ts scan list and the ESLint-in-Vitest 60 s timeout.
  - Carried, different lanes so not rule 9: testing.md l.89 says multi-line Edit fails on CRLF; backend.md l.36 and frontend.md l.36 prescribe Edit.
  - Out of scope, carried: project.md l.143 "There is no gate command yet" and l.17-22 "greenfield" are stale against CLAUDE.md npm run gate.
  - Ledger run.md § Closed marks the prior run's base-URL dedupe as absorbed by 04-test, yet testing.md l.27/l.35 still duplicate it (carried SHOULD_FIX above).
  - The 10-to-11 diff could not be isolated in git (capability edits uncommitted); 11 § changed before/after was checked against the current l.33 text.
  - check_network_edit.py still lists the 4 packs UNLINTED; this PASS artifact is what should clear testing.md, and 08 the other three.
