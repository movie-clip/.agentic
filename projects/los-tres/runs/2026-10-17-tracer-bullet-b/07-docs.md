REPORT 2026-10-17-tracer-bullet-b/07
status:      DONE
verdict:     NONE

changed:
  - los-tres/docs/decisions/0011-css-modules.md — new; records CSS Modules as the owner's choice (D-1 ruling quoted), 0010 format, notes it replaces 0010's styling line
  - los-tres/CLAUDE.md § Stack — one line: Styling, CSS Modules, globals.css keeps variables and reset (0011)
  - los-tres/CLAUDE.md § Commands — F-2 only: the e2e failure text now quotes the shipped sentence from tests/e2e/global-setup.ts exactly, on one line
  - capabilities/backend.md — Layout (server dirs, relative imports, ES2023 lib, verbs, identity ids, CRLF); Guardrails 1, 2, 4, Migrations, new Feed URLs and lint bullet; Definition of done; header sentence
  - capabilities/frontend.md — Layout (CSS Modules, component/page import rule, hashed classes, CRLF); Spanish market conventions (price); Next.js and i18n (timezone, dates, route); Guardrails 2
  - capabilities/testing.md — Index; Running tests (config .mts, global setup, resetDatabase, e2e data, baseURL); What must always be covered (matching, U+00A0 and seams); new section Shared scaffolding and gotchas
  - capabilities/architecture.md — The seams the product forces (paths in the four seam bullets); Design pass (CLI-in-image item)

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    Edited by Edit/Write only. Pack files edited: backend.md (Layout, Guardrails, DoD), frontend.md (Layout, Spanish market conventions, Next.js and i18n, Guardrails), testing.md (Index, Running tests, What must always be covered, Shared scaffolding and gotchas), architecture.md (seams, Design pass).

contract_notes:
  - CLAUDE.md § Stack now cites 0011; docs/decisions/0010 still says no styling system is chosen and was left unedited (out of scope); 0011 states it replaces that line.
  - CLAUDE.md § Commands quotes the e2e failure sentence; if tests/e2e/global-setup.ts NO_FEED_MESSAGE changes, that quote must change with it.
  - testing.md and frontend.md now name tests/support/messages.ts normaliseSpaces and src/server/money.ts formatEuroCents; renaming either makes both packs stale.
  - phases.md and project.md were not touched; project.md says lanes read capabilities by index, and testing.md's index gained a new always-read section.

pack_corrections:
  - none

handoff:
  - Outcomes by source. 01-design backend.md: bullet 1 (Layout server-only sentence) APPLIED merged with 02 #1; bullet 2 (Layout migrations) APPLIED into the existing Migrations guardrail bullet, merged with 02 #2.
  - 01-design backend.md bullet 3 (Guardrails 1 seed) APPLIED using 02 #3 wording (adds "and the demo shops"); bullet 4 (visibility, money, source.ts, URLs, eslint) APPLIED merged with 02 #4, with the file names folded into Guardrails 1, 2 and 4 rather than a duplicate bullet.
  - 02-backend: #1 to #4 as above; #5 (CRLF and ES2023 lib) APPLIED into Layout; #6 (identity ids) APPLIED into Layout; #7 as listed in pack-corrections.md (Definition of done, no URL in logs) APPLIED. 02-backend.md lists six bullets though the index says seven.
  - 01-design frontend.md bullets 1 to 4 (CSS Modules, page import rule, price example, timezone and route) APPLIED merged with 03 #1 to #4; the CSS line cites 0011.
  - 03-frontend: #5 (no link until /go) APPLIED into Guardrails 2; #6 (hashed class names) APPLIED to Layout; #7 (CRLF and heredoc) APPLIED to Layout, shortened.
  - 01-design testing.md bullets 1 to 4 APPLIED merged with 04 #1 to #5: global setup and resetDatabase, .mts and baseURL, matching line, U+00A0 and seams. 04 #1 also added closeDb in afterAll.
  - 04-test #6 (scaffolding) APPLIED as new section Shared scaffolding and gotchas; #7 ESLint timeout, #8 malformed slug, #9 stubEnv, #10 renderToStaticMarkup, #11 Windows and Python APPLIED in the same section.
  - 01-design architecture.md bullets 1 (seam paths) and 2 (CLI in image) APPLIED; paths folded into the four seam bullets, the CLI item into Design pass. Nothing rejected.
  - The Windows CRLF note exists in backend, frontend and testing packs with a different failure each (scripted replace, heredoc, multi-line Edit); kept per lane because each lane reads only its own pack.
  - Next pack-maintenance order should re-run protocol-lint on the four packs; bullets in the new testing section are under 200 characters, but backend Layout is one long paragraph.

skill_calls:
  - none

risks:
  - Premises were not re-verified against code by this lane: no shell, and the entries agree across 01-design and three build lanes whose gate passed; I did read global-setup.ts for the exact sentence.
  - 04 #1 and the TD-38 reference: packs cannot cite TD-38 (a plan id), so testing.md says "a named message (quoted in CLAUDE.md § Commands)" instead of the correction's wording.
  - backend.md Guardrails 2 still says the importer parses "CSV or XML"; slice B is CSV only. No lane emitted a correction, so I left it.
  - backend.md Layout is now a single long paragraph; split it into bullets at the next pack pass if protocol-lint flags length.
  - 02-backend.md lists six pack_corrections bullets while pack-corrections.md says seven; I applied all six present and found no seventh.
  - SHOULD_FIX F-1 and F-3 were not touched, per the order.
  - 03 #7 and 04 #11 are tool-environment tips, not facts about the code; applied because the lanes emitted them, but they may be pruned later.
