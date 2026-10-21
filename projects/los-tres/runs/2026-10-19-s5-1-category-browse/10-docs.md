REPORT 2026-10-19-s5-1-category-browse/10
status:      DONE
verdict:     NONE

changed:
  - C:\projects\investments\los-tres\docs\product\stories\US-5.1-category-browse.md — status now approved (shipped, PR #215); Open decisions records OD-A..OD-J ruled to default under D-1
  - C:\projects\investments\los-tres\docs\design\system.md — created from 02-ux.md § Design system and § Tokens, with the seven additive tokens
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\backend.md — 4 corrections: catalogue files, isWellFormedSlug, category condition in scope, seed mappings, importer category_id rule
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\frontend.md — 4 corrections: listing components, .page p rule, card single link, listing page conventions
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\testing.md — 5 corrections: insert helper defaults, null-category coverage, category fixtures, e2e selection, heredoc gotcha
  - C:\projects\investments\.agentic\projects\los-tres\capabilities\ux.md — 2 corrections: category states rows, Tab focus via node script

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    order verification was NONE; premises spot-checked by reading code (catalogue files, helper names, category fixtures, globals.css tokens and .page p rule all exist)

contract_notes:
  - 04 and 05 contract_notes are test-lane or code facts already landed (07-integration gate exit 0); the design-system note is absorbed in docs/design/system.md
  - Other 04 notes (migration 0002, SeedReport, C-11, C-18) are shipped-contract facts held in the code; no doc in scope states them, dismissed
  - mvp.md not edited: its category and unmapped-feed statements already match shipped behaviour
  - CLAUDE.md not edited: demo steps still hold (demo product oc-1234 has a mapped feed category, public after import-feeds)

pack_corrections:
  - none

handoff:
  - CARRIED SHOULD_FIX for the human, unfixed: src/cli/seed.ts does not print SeedReport.categoryMappings
  - CARRIED SHOULD_FIX for the human, unfixed: header focus ring, pagination indicator spacing at 390 px, no live card showing the title clamp
  - project.md guardrail 1 wording does not name the unmapped state; owner's call, left as is
  - AC 11 ties within equal prices order by products.id (stable, arbitrary); review noted, no action taken

skill_calls:
  - none

risks:
  - ux.md intro still says the site has no design system yet and the first UX order sets it; now stale since docs/design/system.md exists. Not in the corrections, so left; suggested wording: "The design system is recorded in docs/design/system.md."
  - testing.md now holds two heredoc/apostrophe bullets in Shared scaffolding; the new one extends the older one and could be merged by a later pass
  - Story file per-entry OD text still says "Default assumed"; the section preamble records the ruling for all ten rather than each entry being rewritten
  - Review risk: a real feed with a category column named other than category imports unmapped and non-public until a header alias exists
