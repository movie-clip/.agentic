REPORT 2026-10-22-runs-gitignored/01
status:      DONE
verdict:     FAIL
changed:
  - none

verification:
  command:   claude plugin validate ./plugins/agentic-core; git diff of the 4 scoped files; grep of PROTOCOL.md, protocol/**, agents, skills, scripts
  result:    PASS
  detail:    validate passed (license/icon warnings only); P1-P4 PASS; 1 BLOCKING finding (designer.md:121, orphaned by P2); 0 script git dependencies; anchor: authoring.md + orchestrator.md § 8 + orchestrate-feature SKILL; 2 UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - P1 PASS — orchestrator.md:243-244 "drop it" no longer cites git history; consistent with P2 "Pruning deletes it for good".
  - P2 PASS on its own text (orchestrator.md:249-262) — agrees with § 7, § 8 hard limits (stage only paths lane artifacts name) and the skill's Tracker/Close rows, which commit lane paths only.
  - P3 PASS — authoring.md:402-408 places the .gitignore step and cites orchestrator.md § "Closed runs are pruned" for the reason rather than restating it (rule 2).
  - P4 PASS — ARCHITECTURE.md:162-165 and README.md:57 agree with P2; both are human docs outside the four layers, so no rule-2 duplication.
  - BLOCKING (rule 2, one rule one home): designer.md:121-122 says "images are not committed with the run (`orchestrator.md` § 1)"; P2 removed that rule from its home, so designer.md is now its only copy, and it implies runs are committed.
  - Fix for designer.md:121-122: reword so it neither restates an image rule nor implies the run is committed, e.g. cite `orchestrator.md` § "Closed runs are pruned" by name; keep "your report has to stand without them".
  - After the fix, re-lint with plugins/agentic-core/agents/designer.md added to scope, so check_network_edit.py --strict sees a PASS for it.
  - Scripts PASS: check_report.py, ledger.py and the hooks make no git calls; check_network_edit.py runs git on .agentic only and excludes runs/**.
  - No hit for agentic/runs/README.md, `.ignore`, or runs in a pull request anywhere in PROTOCOL.md, protocol/**, agents, skills or scripts.

skill_calls:
  - none

risks:
  - UNVERIFIED: that each bound repo's .gitignore now holds agentic/runs/ — no bound repo was opened.
  - UNVERIFIED: a run already tracked in a bound repo stays tracked despite .gitignore (needs git rm --cached); P2's "no commit carries one" assumes none were committed.
