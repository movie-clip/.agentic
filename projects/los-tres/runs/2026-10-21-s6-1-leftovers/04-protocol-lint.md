REPORT 2026-10-21-s6-1-leftovers/04
status:      DONE
verdict:     PASS

changed:
  - none

verification:
  command:   check_report.py --lane protocol-lint; claude plugin validate plugins/agentic-core; python U+2028/U+2029 and control-char count over testing.md, backend.md, frontend.md
  result:    PASS
  detail:    3 of 3 S6.1 rule-8 findings resolved; 0 BLOCKING, 1 SHOULD_FIX (rule 8); 0 raw U+2028/U+2029/control chars in the 3 packs; plugin validate passed; anchor: authoring.md + frontend.md:32 + agent tools: lines; 2 UNVERIFIED
contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - RESOLVED finding 1: testing.md:95 now spells the escape in words; python count of U+2028/U+2029 and other control chars in testing.md is 0.
  - RESOLVED finding 2: Python/heredoc/regex `\b` trap folded into testing.md:93; :95 (escape + String.raw) and :96 (cat -A) are one trap each, both under 200 chars.
  - RESOLVED finding 3: backend.md:28 now gives the reason (JsonLd.tsx imports it, D-2) and bans server-only, src/db, src/config; agrees with frontend.md:32's narrow JsonLd.tsx exception (rule 9).
  - Rule 7 PASS: testing.md:96 `cat -A` is runnable by test-engineer (agents/test-engineer.md:4 `tools: Read, Write, Edit, Glob, Grep, Bash, ...`).
  - SHOULD_FIX (rule 8) testing.md:93 lists "a regex literal" as a cause, then says write regexes with Write; name the writer (Python string or heredoc) as the cause so the cure does not read as the hazard.

skill_calls:
  - none

risks:
  - UNVERIFIED: testing.md:95 claim that a typed U+2028 escape in a test string arrives as the raw character and String.raw avoids it; not reproduced.
  - UNVERIFIED: testing.md:93 claim that a regex literal in an e2e spec gets `\b` turned into a backspace; not reproduced.
  - plugin validate warns ICON_MISSING for plugins/agentic-core (directory-submission check, outside scope; YAML parse passed).
