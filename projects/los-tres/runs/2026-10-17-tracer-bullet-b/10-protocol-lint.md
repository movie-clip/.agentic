REPORT 2026-10-17-tracer-bullet-b/10
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate <agenticRoot>/plugins/agentic-core; python <agenticRoot>/scripts/check_network_edit.py --verbose
  result:    PASS
  detail:    validate: passed. check_network_edit: 4 UNLINTED (warning, exit 0). Anchor: protocol/authoring.md. CR-1 rule 9 resolved; 1 BLOCKING new (testing.md rule 5, caused by the CR-1 fix); 3 SHOULD_FIX carried, 0 new; 5 UNVERIFIED premise groups.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Verdict: testing.md FAIL. backend.md, frontend.md, architecture.md not re-judged (non_goals); 08's PASS on them stands.
  - CR-1 RESOLVED (rule 9): l.65 now scopes assertTestDatabase() to integration tests and helpers and carries the e2e exception in the same bullet; "development database" no longer appears in testing.md.
  - CR-1 cont.: l.33 now agrees with l.65; no always-read section of testing.md or project.md directs a different action. Rule 9 is clear.
  - BLOCKING new, rule 5 (authoring.md § Indexing a pack or profile, rule 2 "Every fact lives in exactly one section"): the e2e write rule is now in two sections.
  - BLOCKING cont.: testing.md l.33 (§ Running tests) "this `import-feeds` run is the only e2e write"; l.65 (§ What must always be covered) "e2e writes only through `import-feeds` in `globalSetup`". Same fact.
  - BLOCKING cause: the CR-1 fix, specifically 09's l.33 edit (09 risks flags it as beyond the fix wording). CR-1's own defect was two copies of this rule drifting; this rebuilds two copies.
  - BLOCKING lineage: per gates.md § 4 this is CR-1 renumbered, caused by CR-1. Record it as round 2 of 2, not a new round 1.
  - BLOCKING fix (docs lane): end l.33 after the feeds=0 sentence with "The e2e write rule is in § What must always be covered." Delete "e2e tests and their helpers never write ... the only e2e write". Leave l.65 as is.
  - SHOULD_FIX carried from 08, rule 8: testing.md § Running tests l.27 is still a ~1,100-char multi-fact paragraph; the commands-to-needs part belongs in a table.
  - SHOULD_FIX carried from 08, rule 8: the e2e base-URL rule is still stated twice, l.27 (E2E_BASE_URL default) and l.35 (never a literal base URL); keep it once.
  - SHOULD_FIX carried from 08, rule 8: testing.md l.35 "(`appBaseUrl()` is gone)" is still change history; delete the parenthesis.

skill_calls:
  - none

risks:
  - This verdict certifies authoring only; no path, export or behaviour in the bound repo was opened.
  - UNVERIFIED: testing.md test-support file names and exports (global-setup.ts, db.ts resetDatabase/closeDb/assertTestDatabase, catalogue.ts, feeds.ts, network-off.ts, messages.ts).
  - UNVERIFIED: that assertTestDatabase() restricts writes to ${DB_NAME}_test, the new l.65 claim.
  - UNVERIFIED: that tests/e2e/global-setup.ts runs import-feeds via docker compose run and is the only e2e database write (l.33, l.65).
  - UNVERIFIED: testing.md Vitest 5, vitest.config.mts, E2E_BASE_URL default and the Umami 307 at / claim.
  - UNVERIFIED: testing.md tests/unit/seams.test.ts scan list and the ESLint-in-Vitest 60 s timeout.
  - 08's own fix wording left l.33's "e2e tests never write the development database themselves" alongside the new l.65, which would also have duplicated it; 08 missed that.
  - The second round is an escalation trigger (authoring.md § Escalating a single dispatch); the orchestrator decides.
  - Carried from 08, different lanes so not rule 9: testing.md l.89 says multi-line Edit fails on CRLF, backend.md l.36 and frontend.md l.36 prescribe Edit.
  - Out of scope, carried from 08: project.md § Mechanical gates still says "There is no gate command yet", stale against CLAUDE.md npm run gate.
  - The 08-to-09 diff could not be isolated in git (changes uncommitted since bbd9772); 09 § changed before/after text was trusted for what moved.
  - check_network_edit.py keeps warning until a PASS lint names these 4 packs; this FAIL does not clear it.
