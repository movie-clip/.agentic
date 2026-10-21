REPORT 2026-10-21-s6-1-leftovers/01
status:      DONE
verdict:     NONE

changed:
  - tests/unit/product-jsonld.test.ts — 4 raw U+2028/U+2029 chars (line 107 hostile name, lines 122-123 not.toContain args) written as \u2028 and \u2029 escapes

verification:
  command:   cd C:\projects\investments\los-tres && npm run gate
  result:    PASS
  detail:    gate exit 0; vitest 46 files 770 tests passed; playwright 70 passed. Raw-char grep -c for the UTF-8 bytes of U+2028/U+2029 returned 0 (was 3 lines); cat -A of lines 107,122,123 shows plain \u2028 backslash text; git diff --stat 1 file, 3 lines

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - Runtime unchanged: line 107 is a normal string literal so \u2028 still yields the real char; the escaped-output assertions at lines 124-125 (String.raw) are untouched
  - Change is uncommitted on branch 38-product-jsonld for the orchestrator to commit

skill_calls:
  - none

risks:
  - The pack warned about escapes turning raw; the real trap here was the reverse in tooling: bash double-quoted python -c and a heredoc lost the backslash, so the first edit silently did nothing. Wrote the fix with chr(92) in a scratchpad script; worth a pack line
  - grep -P fails in this Git Bash locale (unibyte); use grep with $'\xe2\x80\xa8' bytes to count the characters
