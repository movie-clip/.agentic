# RUN 2026-10-07-s2-animation-bridge-contract
request:      okay, Take next slice and start working step by step, first planning how to address the slice
agentic_root: C:\projects\investments\.agentic
project:      projects/impact/project.md
story:        runs/2026-10-07-s2-animation-bridge-contract/01-story.md
status:       CLOSED
phase:        close
plan:         v3
budget:       14 — v2 12 + CR-3 docs fix 1 + protocol-lint re-run 1
spent:        14
next:         none — CLOSED
gates:        integration PASS (06 CHANGES_REQUESTED, re-run 09 PASS) · review PASS (10) · protocol-lint PASS (12 FAIL, re-run 14 PASS on CR-3)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing system/behaviour | not triggered (prior artifacts cover the area: runs/2026-10-07-ecs-animation-approach/01-recon.md, 02-recon.md, 03-recon.md; S1's bridge changes in 07-backend.md, 09-backend.md) |
| framing | product | new gameplay system / feature surface, or changes what one is for | not triggered (S2 already framed in runs/2026-10-07-ecs-animation-approach/04-delivery-brief.md § Stories S2, under D-2..D-6) |
| specification | story | framing scope no approved brief covers, and crosses >1 lane contract | satisfied — 01 (D-2..D-5) |
| design | design | crosses a package-boundary contract | satisfied — 02 |
| build | backend, test, docs | anything that edits Impact/Packages, Assets, Tools or docs | satisfied — 03, 04, 05 |
| verify | integration | any build lane was dispatched | satisfied — 06, 09 |
| verify | review | the run carries a story | satisfied — 10 |
| close | docs | always | satisfied — 11 |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|
| 01 | story | — | story-author | sonnet | 01-story.md | DONE | — |
| 02 | design | DESIGN | tech-lead | sonnet | 02-technical-plan.md | DONE | — |
| 03 | test | — | test-engineer | sonnet | 03-test.md | DONE | — |
| 04 | backend | — | backend-engineer | sonnet | 04-backend.md | DONE | — |
| 05 | test | — | test-engineer | sonnet | 05-test.md | DONE | — |
| 06 | integration | INTEGRATION | tech-lead | sonnet | 06-integration.md | DONE | CHANGES_REQUESTED |
| 07 | backend | — | backend-engineer | sonnet | 07-backend.md | DONE | — |
| 08 | test | — | test-engineer | sonnet | 08-test.md | DONE | — |
| 09 | integration | INTEGRATION | tech-lead | sonnet | 09-integration.md | DONE | PASS |
| 10 | review | — | reviewer | sonnet | 10-review.md | DONE | PASS |
| 11 | docs | — | docs-engineer | sonnet | 11-docs.md | DONE | — |
| 12 | protocol-lint | — | protocol-linter | opus | 12-protocol-lint.md | DONE | FAIL |
| 13 | docs | — | docs-engineer | sonnet | 13-docs.md | DONE | — |
| 14 | protocol-lint | — | protocol-linter | opus | 14-protocol-lint.md | DONE | PASS |

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|
| handoff | 02-design | 02-technical-plan.md § handoff | human git rm of CharacterAnimationAuthoring stub + later retired-field cleanup | CARRIED |
| risk | 02-design | 02-technical-plan.md § risks | AC-7 has no real-prefab bake test (BakingUtility internal); evidence by construction | CARRIED |
| risk | 03-test | 03-test.md § risks | 150-char figures understate Animator work (CullUpdateTransforms, no renderers in batchmode) | CARRIED |
| scope | orchestrator | git status (2026-10-12) | human WIP in tree, not S2: athena.contentmanagement edits/deletes, GameAssetLoad.cs, packages-lock.json (dated 10-09) | CARRIED |
| risk | 05-test | 05-test.md § risks (AC-10) | with-camera path unreachable while isStrafing hard-coded false; untested until S4 | CARRIED |
| risk | 05-test | 05-test.md § risks (AC-8) | sort test red-on-old-code shown by reasoning, not run | CARRIED |
| should_fix | 06-integration | 06-integration.md § risks | OnEnable resets adapter cache without telling presentation gate (latent; nothing toggles sync) | CARRIED |
| should_fix | CR-2 | cr/CR-2.md | fixed (07) + regression test (08); CR-2 red-on-old-code by reasoning only | CARRIED |
| should_fix | CR-1 | cr/CR-1.md | tdd call recorded in 08-test.md, not 05-test.md; 05 read alone still shows the contradiction | CARRIED |
| risk | 10-review | 10-review.md § Findings per AC | AC-12 bookkeeping release unobservable by log count (Entity version) — S3/S4 seam | CARRIED |
| handoff | 10-review | 10-review.md § handoff | TestResults-*.xml tracked and rewritten by runs — revert or commit deliberately | CARRIED |
| contract_note | 11-docs | 11-docs.md § contract_notes | setup doc still partly stale (S9); PLAYER_SESSION_CHARACTER_FLOW.md, PACKAGE_ARCHITECTURE.md unchecked | CARRIED |
| should_fix | 12-protocol-lint | 12-protocol-lint.md § risks | Git Bash forward-slash fact only in backend.md; testing.md:61-74 still shows .\Tools\ | CARRIED |
| should_fix | prior run 12-protocol-lint | testing.md:91-94 (SF-1) | References table mixes Unity refs; should list Unity.Entities for TimeData | CARRIED |
| should_fix | 14-protocol-lint | 14-protocol-lint.md § findings (SF-5) | testing.md:34-37 bullet 274 chars; drop the because-clause | CARRIED |
| should_fix | CR-3 | cr/CR-3.md | F-1 fixed (13) and confirmed (14); batchmode compile check at AGENTS.md:48 not covered by :40 | CARRIED |

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|
| contract_note | 02-design | 03-test (asmdefs gained CharacterController.Runtime, Unity.CharacterController, Unity.Physics) | test asmdefs need Athena.CharacterController.Runtime + Unity.CharacterController refs — for 03 test |
| contract_note | 02-design | 04-backend (implemented; test-side adaptation routed to 05 via 04-backend.md § contract_notes) | ICharacterAnimationBackend, link fields, state IEquatable/field map, Sync becomes passive — for 04 backend, 05 test |
| contract_note | 02-design | 04-backend (CharacterAnimationSpeedReference + AnimationMaxSpeed 7) | CharacterAnimationSpeedReference (default 7) — for 04 backend, 05 test |
| contract_note | 03-test | 05-test (SetBridgeEnabled disables presentation system) | extend SetBridgeEnabled to disable new presentation system — for 05 test |
| should_fix | CR-2 | 07-backend (settling recomputed in Apply) | settle Update can freeze Animator MoveSpeed when Apply lands on the snap frame (one-line fix) |
| should_fix | CR-2 | 08-test (regression test) + 09-integration PASS | fixed in 07; regression test for the snap-frame sequence routed to 08 test |
| contract_note | 02-design | 11-docs (three repo docs + TESTING.md updated) | setup doc, PACKAGE_DOCUMENTATION, ARCHITECTURE_REVIEW lag push model / one baker — for close docs |
| pack_correction | 03-test | 11-docs (5 applied; state APPLIED) | two testing.md corrections (TimeData; Run-UnityTests exit behaviour) — for close docs |
| risk | 04-backend | 06-integration (settle-only Update ruled accepted; CR-2 fixed its defect) | deviation: CharacterAnimatorSync keeps settle-only Update for MoveSpeed smoothing — for 06 integration |
| risk | 04-backend | 06-integration (accepted as documented limitation; documented by 11-docs) | controller assigned later gets no write until state changes — for 06 integration |
| risk | 03-test | dismissed — did not recur in 5 later full PlayMode -CoreOnly runs (03 x2, 05, 07, 08, 09) | StartupReproPlayModeTests 10 s timeout once after recompile |
| should_fix | 12-protocol-lint | 13-docs (SF-2..SF-4 applied; confirmed by 14) | SF-2..SF-4 bullet splits in testing.md:34-45 — routed with CR-3 to 13 docs |

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|
| CR-1 | test | 1 | 2 | — |
| CR-2 | backend | 1 | 2 | — |
| CR-3 | docs | 1 | 2 | — |

## Replans
| plan | because | change |
|---|---|---|
| v2 | 06-integration CHANGES_REQUESTED (CR-1 blocking, CR-2 fix per D-7); protocol-lint owed (pack-corrections.md non-empty), missed at intake | CR-1 test fix + CR-2 backend fix + integration re-run + protocol-lint; budget 8 → 12 |
| v3 | 12-protocol-lint FAIL (F-1 BLOCKING, testing.md:39 contradicts project.md:187-188 / AGENTS.md) | CR-3 docs fix + protocol-lint re-run; budget 12 → 14 |
