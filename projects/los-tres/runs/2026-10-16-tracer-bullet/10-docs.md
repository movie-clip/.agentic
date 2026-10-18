REPORT 2026-10-16-tracer-bullet/10
status:      DONE
verdict:     NONE

changed:
  - capabilities/backend.md — F1 and F2 satisfied by adding Layout to the Always read line; the now-empty conditional table is replaced by one line saying every section is always-read
  - capabilities/frontend.md — F3 satisfied by adding Layout to the Always read line
  - capabilities/frontend.md — F4 satisfied by moving the three next-intl, force-dynamic and plugin bullets, wording unchanged, from Spanish market conventions into a new always-read section Next.js and i18n, added to the index

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only docs order, verification NONE; protocol-lint re-runs

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - SHOULD_FIX rule-8 findings from 09 are untouched and still carried for the human, including the long frontend bullets now under Next.js and i18n.

skill_calls:
  - none

risks:
  - The backend index now has no conditional table; if protocol-lint wants a table block present, re-add one row rather than an empty table.
