REPORT 2026-10-22-runs-gitignored/02
status:      DONE
verdict:     PASS
changed:
  - none

verification:
  command:   claude plugin validate ./plugins/agentic-core; git diff HEAD and --cached of the 5 scoped files; grep of PROTOCOL.md, protocol/**, agents, skills, scripts, ARCHITECTURE.md, README.md
  result:    PASS
  detail:    validate passed (license/icon directory notices only); F1 resolved at designer.md:120-123; P1-P5 PASS; 0 new hits in network-wide search; anchor: authoring.md + orchestrator.md § 1/§ 8 + 01's findings; 3 UNVERIFIED

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - F1 RESOLVED — designer.md:120-123 no longer says images are not committed nor cites orchestrator.md § 1; it cites § "Closed runs are pruned" by name, as 01's fix asked.
  - P5 PASS (rule 2) — designer.md:121-123 states the consequence for its own lane (report stands without screenshots) and cites the home of the rule rather than restating it.
  - P5 PASS (rule 9) — "stays in the local run dir and is deleted when the run is pruned" agrees with orchestrator.md:251-258 ("Runs are local and never committed", "Pruning deletes it for good").
  - P5 citation check — orchestrator.md:249 heading reads exactly "### Closed runs are pruned"; the cited name resolves.
  - P1 PASS — orchestrator.md:243-244 unchanged since 01; "drop it" cites § "Closed runs are pruned", no git-history claim.
  - P2 PASS — orchestrator.md:249-263 unchanged since 01; agrees with § 8 hard limits (orchestrator.md:803-805, stage only lane paths) and SKILL.md:219-220.
  - P3 PASS — authoring.md:402-408 unchanged since 01; places the .gitignore step and cites orchestrator.md § "Closed runs are pruned" for the reason.
  - P4 PASS — ARCHITECTURE.md:162-165 and README.md:57 unchanged since 01 and agree with P2; human docs outside the four layers.
  - Search PASS — no remaining text in PROTOCOL.md, protocol/**, agents, skills or scripts assumes project runs are committed or that images are excluded by any rule other than P2.
  - Search detail — orchestrator.md has no image/png/screenshot text left; no hit for runs/README.md, git history of runs, or `.ignore`; § 1 citations elsewhere (packs.md:16, authoring.md:384, grill-plan:53) are about the ledger, not images.

skill_calls:
  - none

risks:
  - UNVERIFIED: that each project's ux pack screenshot command writes into the run dir, as designer.md:121-122 asserts; no ux.md pack was opened.
  - UNVERIFIED: that each bound repo's .gitignore holds agentic/runs/; no bound repo was opened (carried from 01).
  - UNVERIFIED: runs already tracked in a bound repo stay tracked despite .gitignore until git rm --cached; P2 assumes none were committed (carried from 01).
  - Outside scope per non_goals: P2's unqualified "Runs are local and never committed" reads broader than its agentic/runs/ clause, while .agentic/runs/ lint runs are committed (.gitignore ignores only runs/**/*.png).
