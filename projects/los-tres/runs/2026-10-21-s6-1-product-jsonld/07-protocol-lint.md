REPORT 2026-10-21-s6-1-product-jsonld/07
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   claude plugin validate .agentic/plugins/agentic-core; check_report.py --lane protocol-lint
  result:    PASS
  detail:    validate: passed (LICENSE/icon directory checks only, out of scope); 5 edits across 3 packs checked, 0 BLOCKING, 3 SHOULD_FIX (rule 8); anchor authoring.md + D-2 + JsonLd.tsx imports; 2 premises UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SHOULD_FIX (rule 8) testing.md:95 holds a literal U+2028 byte (cat -A shows M-bM-^@M-() where the text ` ` was meant; the gotcha's subject is unreadable and ungreppable. Fix: type ` ` with Edit, confirm with cat -A.
  - SHOULD_FIX (rule 8) testing.md:95 carries four facts (heredoc, regex literals, U+2028 escapes, String.raw/cat -A) and restates the Python `\b` trap of testing.md:93. Fix: fold the Python part into :93, one bullet per remaining trap.
  - SHOULD_FIX (rule 8, keep the why) backend.md:28 notes product-jsonld.ts has no server-only but not why: JsonLd.tsx imports it (frontend.md:32, D-2). Fix: add that it must stay free of server-only, src/db and src/config imports.

skill_calls:
  - none

risks:
  - UNVERIFIED: testing.md:95 claim that ` `-style escapes typed in a test string arrive as the raw character, and that String.raw avoids it; not reproduced.
  - UNVERIFIED: testing.md:41 e2e method (regex over script tags, one match, then openRawHtml price comparison) not read in tests/e2e/product.spec.ts; only that the file references product-jsonld.
  - plugin validate reports LICENSE_MISSING and ICON_MISSING for plugins/agentic-core (directory-submission checks, outside this order's scope; YAML parse passed).
