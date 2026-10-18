REPORT 2026-10-16-tracer-bullet/09
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   git -C C:\projects\investments\.agentic diff --stat -- projects/los-tres/capabilities/ ; claude plugin validate <agenticRoot>/plugins/agentic-core
  result:    PASS
  detail:    diff --stat: 3 files, 41 insertions, 24 deletions; plugin validate passed. Anchor: protocol/authoring.md (not self-referential). 4 BLOCKING (rule 6), 5 SHOULD_FIX (rule 8), 9 UNVERIFIED premises.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING F1 rule 6 (authoring.md § Indexing a pack or profile) backend.md § Layout l.35: port-collision rule "never stop another project's container" sits in a section read only when adding a file, port, variable or pin.
  - F1 cont.: a lane hits a taken port while running the gate, a situation its index condition cannot predict. Satisfied by moving l.35 into an always-read section or adding Layout to Always read.
  - BLOCKING F2 rule 6 backend.md § Layout l.33 + l.35: "Compose binds ports to 127.0.0.1" and "Next 16 loads .env itself, no env loader" are hazards in a conditional section; fix as F1 (same move satisfies both).
  - BLOCKING F3 rule 6 frontend.md § Layout l.33: "A component never imports src/db, src/server or src/config" is a guardrail-type hazard, but its row says read only when adding a file or component; editing an existing one skips it.
  - F3 fix: add Layout to frontend.md Always read, or move the import ban into § Guardrails, in code terms.
  - BLOCKING F4 rule 6 + rule 5.1 frontend.md § Spanish market conventions l.45-46: no-middleware (guardrail 5) and force-dynamic / no env at module load are hazards filed under a copy/prices/dates condition.
  - F4 cont.: a lane adding middleware or a data page without new copy skips them, and none searches "Spanish market" for Next.js rendering. Fix: move l.45-47 to an always-read section, e.g. a new "Next.js and i18n" listed under Always read.
  - SHOULD_FIX rule 8 testing.md § Running tests l.27: one ~900-char paragraph carrying runners, databases, e2e target and commands; the command-to-needs mapping is a table.
  - SHOULD_FIX rule 8 testing.md § Running tests l.27 and l.33: the e2e base URL from APP_PORT is stated twice in one section (also 07-integration's Open row).
  - SHOULD_FIX rule 8 frontend.md § Spanish market conventions l.45-47: each bullet exceeds 200 characters and carries 2-3 facts.
  - SHOULD_FIX rule 8 frontend.md l.42 and l.45: "no literal site name" stated twice in one section, the second broader; keep one.
  - SHOULD_FIX rule 8 backend.md § Layout l.31-33: multi-fact paragraphs; the pinned versions are a mapping and read better as a table.

skill_calls:
  - none

risks:
  - Counted F1 and F2 as separate findings on one section; one edit (Layout to Always read) clears both.
  - testing.md § Running tests also holds hazards (Umami 307, configs never import tests/), but its condition is true on every test-engineer build order, so not filed.
  - testing.md l.59 "no request leaves the app origin" may conflict with frontend.md l.59 cookieless Umami once a tracker script loads from the Umami port; two lanes, so not a rule-9 finding.
  - testing.md l.27 restates CLAUDE.md § Commands; l.29 states CLAUDE.md wins, so no rule-9 conflict, but the copy can drift.
  - "Before the stack is recorded" sections in backend.md and frontend.md now hold a post-stack rule; both are always-read, so the name misleads no lane.
  - Packs carry no YAML frontmatter, so plugin validate covers the agent files only, not these three packs.
  - UNVERIFIED: the src/config, src/db, src/server, src/cli, src/i18n, src/components and docker/db-init paths exist as described.
  - UNVERIFIED: pinned versions (TypeScript 5.9, ESLint 9, Next 16, Postgres 17, Umami postgresql-v2.20.2, Vitest 5).
  - UNVERIFIED: next-intl API names (createNextIntlPlugin, getTranslations, getLocale) and that its middleware sets a cookie.
  - UNVERIFIED: Next 16 loads .env itself; process.loadEnvFile is how tests get env.
  - UNVERIFIED: assertTestDatabase lives in tests/support/db.ts; global-setup.ts and test-database-env.ts exist.
  - UNVERIFIED: Umami answers 307 at / and 200 at /api/heartbeat.
  - UNVERIFIED: .dockerignore removes tests/ and tsconfig includes both test configs.
  - UNVERIFIED: docker compose up -d picks up a changed SITE_NAME without rebuild.
  - UNVERIFIED: .gitattributes keeps *.sh LF and the app image sets HOSTNAME=0.0.0.0. (npm script names were confirmed in package.json.)
