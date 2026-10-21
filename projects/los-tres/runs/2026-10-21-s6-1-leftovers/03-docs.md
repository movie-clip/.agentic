REPORT 2026-10-21-s6-1-leftovers/03
status:      DONE
verdict:     NONE

changed:
  - capabilities/testing.md § Shared scaffolding and gotchas — the Python `\b` bullet (:93) now also covers heredocs and regex literals in e2e specs
  - capabilities/testing.md § Shared scaffolding and gotchas — the old :95 bullet is split into two: the U+2028/U+2029 escape plus `String.raw`, and a separate `cat -A` check bullet
  - capabilities/backend.md § Layout — the product-jsonld.ts note now gives the reason (JsonLd.tsx imports it, D-2) and forbids server-only, src/db and src/config imports

verification:
  command:   Grep for U+2028 and U+2029 over the capabilities directory
  result:    PASS
  detail:    0 matches in capabilities/; the order's verification was NONE

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - none

skill_calls:
  - none

risks:
  - The raw U+2028 byte could not be matched by Edit, so testing.md was rewritten whole with Write (it is LF, so no line-ending change); the escape is described in words, never typed, and a Grep for the two characters finds none
