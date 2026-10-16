# RUN 2026-10-07-ecs-animation-approach
request:      Review how animations systems, I believe right now in the project I don't have clear approch how to work with animations and ECS. I'm using 3d models and animations from Polygon, and it is perfect for me, so investigate and research how to work with animations, how Polygon models are configured, you can update packages if needed to latest version or remove them if needed. It is very big Epic task, first do research -> then clarify what you have found -> plan how to address issues or implement features
agentic_root: C:\projects\investments\.agentic
project:      projects/impact/project.md
story:        NONE
status:       CLOSED
phase:        close
plan:         v3
budget:       12 — CR-1 fix + integration re-run (D-11) on top of v2: ground-truth 3 recon (code, assets, web research per D-1) + framing 1 + specification 1 + design 1 + build 1 (backend, minimum; re-planned after design) + verify integration 1 + review 1 + close 1
spent:        12
next:         none — CLOSED
gates:        integration PASS (08, re-run 10 on CR-1) · review skipped (no story — S1 brief is the specification) · protocol-lint PASS (12)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing system/behaviour | satisfied — 01, 02, 03 |
| framing | product | new gameplay system / feature surface, or changes what one is for | satisfied — 04 (D-6..D-9) |
| specification | story | framing scope no approved brief covers, and crosses >1 lane contract | not triggered (S1 does not cross more than one lane's contract; 04-delivery-brief.md is the specification per D-6) |
| design | design | crosses a package-boundary contract | satisfied — 05 |
| build | backend, test, docs | anything that edits Impact/Packages, Assets, Tools or docs | satisfied — 06, 07 |
| verify | integration | any build lane was dispatched | satisfied — 08 |
| verify | review | the run carries a story | not triggered (no story to accept) |
| close | docs | always | satisfied — 11 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | recon | — | scout | sonnet | 01-recon.md | DONE | — |
| 02 | recon | — | scout | sonnet | 02-recon.md | DONE | — |
| 03 | recon | unbound general-purpose (D-1) | — | opus | 03-recon.md | DONE | — |
| 04 | product | — | producer | sonnet | 04-delivery-brief.md | DONE | — |
| 05 | design | DESIGN | tech-lead | sonnet | 05-technical-plan.md | DONE | — |
| 06 | test | — | test-engineer | sonnet | 06-test.md | DONE | — |
| 07 | backend | — | backend-engineer | sonnet | 07-backend.md | DONE | — |
| 08 | integration | INTEGRATION | tech-lead | sonnet | 08-integration.md | DONE | PASS |
| 09 | backend | — | backend-engineer | sonnet | 09-backend.md | DONE | — |
| 10 | integration | INTEGRATION | tech-lead | sonnet | 10-integration.md | DONE | PASS |
| 11 | docs | — | docs-engineer | sonnet | 11-docs.md | DONE | — |
| 12 | protocol-lint | — | protocol-linter | opus | 12-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| finding | 02-recon | 02-recon.md § Configuration problems | Samurai pack prefabs reference missing controller GUID d62af11c — slice S7 | CARRIED |
| doc_drift | 01-recon | 01-recon.md § Doc claims verified | CHARACTER_ANIMATION_SETUP.md contradicted by code (params, order, steps) — S9 rewrite | CARRIED |
| finding | 01-recon | 01-recon.md § Packages | entities.graphics, animation.rigging, cinemachine, timeline installed but unused by code — S8 (Timeline kept, D-8) | CARRIED |
| protocol_gap | 03-recon | decisions.md § D-1 | no lane has web access; unbound agent cannot be named in Artifacts agent column | CARRIED |
| human | 07-backend | ProjectSettings/ProjectSettings.asset | Unity line-ending churn in ProjectSettings.asset, not lane work; human decides to commit or revert | CARRIED |
| risk | 07-backend | 07-backend.md § risks (item 2) | bridge pass-2 per-frame cost at 150 chars unmeasured; belongs to S2 (O5 budget) | CARRIED |
| should_fix | 10-integration | cr/CR-1.md (fixed 09, verified 10) | CR-1 warn-once path has no test; add one in S2 test slice | CARRIED |
| should_fix | 12-protocol-lint | 12-protocol-lint.md § SF-1 | testing.md:76-79 References (Athena) column now lists Unity.Transforms, omits other Unity refs | CARRIED |
| pack_gap | 12-protocol-lint | 06-test.md § handoff | Run-UnityTests.ps1 returns before Unity.exe exits; not in testing.md Gotchas | CARRIED |
| pack_gap | 12-protocol-lint | 12-protocol-lint.md § risks | test-engineer declares mcp__project__* tools; impact has no tool server | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 05-design | 06-test | test asmdefs need Unity.Transforms reference; route to test 06 |
| contract_note | 05-design | 07-backend | BridgeInitialized -> managed cleanup class w/ LinkedInstance; route to backend 07 |
| contract_note | 05-design | 07-backend | HybridGameObject.Prefab never written after bake; route to backend 07 |
| contract_note | 05-design | 07-backend | new CharacterAnimationBridgeCleanupSystem in PostEntityLifecycleGroup; route to backend 07 |
| risk | 07-backend | dismissed — superseded by CR-1 | TryLink LogWarning fires every frame for Animator-less instance; integration to judge |
| finding | 01-recon | 07-backend (S1, verified 08) | CharacterAnimationBridgeInitialized never cleared: skin swap loses animation, ghost entities leak |
| should_fix | CR-1 | 09-backend (verified 10) | Animator-less LogWarning every frame; warn once per instance (bridge system only) |
| contract_note | 05-design | 11-docs | athena.shared docs + CHARACTER_ANIMATION_SETUP.md lag S1; route to close docs 09 |
| pack_correction | 06-test | 11-docs | testing.md package-visibility table lacks Unity.Transforms; apply at close |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| CR-1 | backend | 1 | 2 | — |

## Replans
| plan | because | change |
|---|---|---|
| v2 | no lane has web access; human ruled D-1 (general-purpose web research agent) | ground-truth +1 recon (03, unbound); budget 9 → 10 |
| v3 | specification and review did not fire (-2), protocol-lint became accountable via pack-corrections.md (+1), human ruled D-11 to fix CR-1 now (+2: backend round 1, integration re-run) | budget 10 → 12 |
