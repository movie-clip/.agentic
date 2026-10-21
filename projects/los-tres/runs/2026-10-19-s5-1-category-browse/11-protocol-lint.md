REPORT 2026-10-19-s5-1-category-browse/11
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate <agenticRoot>/plugins/agentic-core; git diff -- projects/los-tres/capabilities; tools: lines of designer, test-engineer, frontend-engineer, backend-engineer
  result:    PASS
  detail:    validate passed (1 icon warning, out of scope); 4 packs judged against authoring.md (external anchor: agent tools: lines + repo files for 12 premises); 1 BLOCKING (rule 9), 4 SHOULD_FIX (rule 8); 7 premises UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 (Two instructions may not disagree), capabilities/ux.md:115 vs :118 — see § Finding 1
  - SHOULD_FIX rule 8 (Writing for the reader), testing.md:105-106 — two bullets for one heredoc gotcha; merge into one ("Bash heredocs with apostrophes fail to parse: write files with Write, run edit scripts from the scratchpad").
  - SHOULD_FIX rule 8, testing.md:77-79 and :49 — bullets over 200 characters carrying several facts (insert defaults, defaultCategoryId, null categoryId, helper names); split one fact per bullet.
  - SHOULD_FIX rule 8, backend.md:40-49 — Guardrail (1) bullet now holds scope, seeds, mappings, importer rule and SEED_DEMO_DATA; move the importer category_id rule to its own bullet.
  - SHOULD_FIX rule 8, ux.md:97 — one paragraph carries the CLI limit, the node-script method and the fallback; split the node-script method into its own line.

skill_calls:
  - none

risks:
  - ux.md:7-10 intro still says the site has no design system and the first UX order sets it; docs/design/system.md now exists. Stale fact, not an authoring rule; :51-53 already handles both cases. Docs lane flagged it in 10-docs risks.
  - ux.md:97 does not say where the node script lives; designer has Write only for its artifact (core § 3), so the script must run via Bash (node -e or stdin), not a file. Not a rule 7 break: designer tools include Bash.
  - UNVERIFIED: ux.md:112-116 state URLs and counts (/categoria/filtros 26 products, 2 pages; escobillas-y-bombillas one card; aceites-y-lubricantes empty).
  - UNVERIFIED: ux.md:97 that a node script with createRequire from the repo package.json can press Tab and screenshot.
  - UNVERIFIED: backend.md:47-48 importer sets products.category_id only from null and never clears it.
  - UNVERIFIED: backend.md:44-46 seeds insert demo feed_category_mappings on conflict do nothing.
  - UNVERIFIED: frontend.md:71 product card link stretched by ::after on the title anchor.
  - UNVERIFIED: frontend.md:60 listing pages link page 1 with no ?pagina=1 and use plain <a> for card and pagination links.
  - UNVERIFIED: testing.md:106 heredoc parse failure (exit 2) as described.

## Orchestrator brief

- Verdict FAIL: one BLOCKING finding, rule 9, owner docs-engineer, file capabilities/ux.md. See § Finding 1.
- Four SHOULD_FIX rule 8 findings, listed in handoff. They go to the Open table and do not hold the slice.
- No rule 1, 3-7 findings. Every command added to a pack is runnable by the lane that owns the pack.

## Finding 1

- **Rule:** authoring.md § "Two instructions may not disagree".
- **File and line:** `projects/los-tres/capabilities/ux.md:115` vs `:118`, § Producing the states.
- **Claim:** the close-out added row 115, `category, empty (200)` → `/categoria/aceites-y-lubricantes`, which produces an empty product list. Line 118, unchanged, still names "an empty list" as a state "this table cannot produce", to be reported `not checked`.
- **Impact:** a UX-REVIEW lane checking an empty listing reads one instruction to bring it up live and another to mark it `not checked`. Nothing records which one it followed.
- **What would satisfy it:** reword line 118's example so it names a state the table still cannot produce. For example, replace "an empty list" with "a product with no offers", or delete it. Leave rows 112-116 unchanged.
