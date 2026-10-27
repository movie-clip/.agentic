REPORT 2026-10-24-merge-engineer-producer/01
status:      DONE
verdict:     FAIL

changed:
  - none

verification:
  command:   claude plugin validate C:\projects\investments\.agentic\plugins\agentic-core
  result:    PASS
  detail:    validate passed, 0 errors; 2 BLOCKING (rule 9), 2 SHOULD_FIX (rule 8); 3 UNVERIFIED. Anchor for authoring.md: the other agent files in plugins/agentic-core/agents/ (10 listed). Scope judged: C:\projects\investments\.agentic\plugins\agentic-core\agents\engineer.md, C:\projects\investments\.agentic\plugins\agentic-core\agents\producer.md, C:\projects\investments\.agentic\PROTOCOL.md, C:\projects\investments\.agentic\protocol\authoring.md, C:\projects\investments\.agentic\protocol\orchestrator.md, deleted backend-engineer.md, frontend-engineer.md, story-author.md (git show HEAD). Frontmatter model/effort/tools of all 10 agents match authoring.md model and effort tables and the no-Bash lists; no network file outside scripts/ names a deleted agent.

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - BLOCKING rule 9 — producer.md:12-15 says "Your output is a delivery brief" unconditionally; STORY mode (:24, :256) outputs a story file — see § F1
  - BLOCKING rule 9 — authoring.md:329 rule 7 test (runnable per `tools:`) passes a frontend pack calling probe_engine that authoring.md:363-367 and engineer.md:53 forbid — see § F2
  - SHOULD_FIX rule 8 — authoring.md:155 high-effort Why cell says "the two that write the code"; `engineer` is now one agent — reword to "both lanes of engineer"
  - SHOULD_FIX rule 8 — authoring.md:157 medium Why cell lists "Drafting", but story drafting now runs in producer at `high`; drop "Drafting" or name what still drafts at medium

skill_calls:
  - none

risks:
  - scripts/check_network_edit.py:14 docstring still names `frontend-engineer`; scripts/** is outside scope and outside the linter's subject
  - README.md, ARCHITECTURE.md, scripts/hooks/*, scripts/test_ledger.py and plugins/agentic-core/evals/ changed but are outside scope; not judged
  - Bound-repo grep for deleted agent names covered budget, datoro, los-tres, portfolio, tradingview (0 hits); impact was not searched
  - UNVERIFIED: bound profiles' lane tables name `capabilities/story.md` only where it exists, as producer.md:48-50 assumes
  - UNVERIFIED: every bound repo with backend/frontend lanes has `capabilities/backend.md` and `capabilities/frontend.md`, which engineer.md:25 reads by `<lane>`
  - UNVERIFIED: check_report.py accepts a `--lane story` artifact whose Orchestrator brief names no sections below it, as producer.md:266-268 implies

## Orchestrator brief
- verdict: FAIL on two rule-9 findings; two rule-8 SHOULD_FIX go to Open
- sections below: F1 (producer.md intro vs STORY mode) · F2 (authoring.md rule 7 vs engineer frontend rule)
- both fixes are one-sentence rewordings in the authoring main session; re-lint only those two files

## F1

- **Rule:** authoring.md § "Two instructions may not disagree" — a rule and its exception are one fact.
- **Where:** plugins/agentic-core/agents/producer.md:12-15: "Your output is a **delivery brief** that a human approves and the orchestrator then executes." It sits above `## Two modes`, so it binds both modes; the table at :21-24 lists the sections each mode applies but not the intro.
- **Conflict:** in STORY mode (:24 "one story file, from an approved brief"; :256 "You draft the story. Nothing else.") the lane reads two statements of what its output is.
- **Satisfied by:** scoping :12 to FRAMING ("In FRAMING mode your output is a delivery brief…"), or rewording it to cover both outputs (brief in FRAMING, story draft in STORY).

## F2

- **Rule:** authoring.md § "Two instructions may not disagree" — an exception split from its rule must say which cases it covers. This is the self-anchored case: judged against engineer.md, the rule no longer describes what the agent files do.
- **Where:** protocol/authoring.md:311-330 defines the rule-7 test as "open the agent file and read its `tools:` line" and closes "every command in a pack must be runnable by the lane that pack belongs to". engineer.md:4 `tools:` holds `mcp__project__probe_engine` and `mcp__project__build_snapshot`; engineer.md:53-55 and authoring.md:365-367 say the frontend lane must not call them.
- **Conflict:** a linter applying :329 to a frontend pack that tells the lane to call `probe_engine` finds it on the `tools:` line and passes it; the agent file then forbids it. Before the merge the `tools:` line was the whole answer (frontend-engineer lacked both); the edit moved the restriction into the body without telling the rule.
- **Satisfied by:** one sentence in § "A pack may not instruct a tool the lane does not have", e.g. "Where one agent serves several lanes, its per-lane working rules narrow its `tools:` line: a pack may not instruct a tool its agent forbids for that lane (`engineer` on `frontend`: `probe_engine`, `build_snapshot`)."
