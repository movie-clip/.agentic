# RUN 2026-09-22-session-start-diagnostic
request:      Add a small diagnostic ECS system that logs a one-line message once, on world
              initialization, with the current Unity Editor version and a timestamp
              (something like "[Impact] Session started — Unity 6000.4.0f1, <timestamp>").
              Pick the package it belongs in yourself, using the dependency-chain guardrail
              in the project profile, and add an EditMode test that proves it fires exactly
              once. This should be a short run — no design phase, no story — since it adds
              no cross-package contract; if you find it needs one, say why instead of just
              proceeding. While implementing, use the Unity CLI + Pipeline fast-iteration
              loop (the `unity-cli` skill, `unity command eval` against the already-open
              Editor) instead of a cold batchmode boot for each iteration. Note in the report
              whether that actually worked, and fall back to batchmode explicitly if it
              didn't, saying why.
agentic_root: C:\projects\investments\.agentic
project:      impact
story:        NONE
status:       PLANNING
phase:        intake
plan:         v1
budget:       5 — ground-truth(1, scout) + build(2: backend, test) + verify(1: integration) + close(1: docs); framing/specification/design/review not triggered
spent:        0
next:         dispatch ground-truth (scout) — confirm how a new ISystem in athena.core actually gets scheduled (Application World vs Local World split in WorldBootstrap.cs) before backend order is written
gates:        integration pending · review skipped (no story) · protocol-lint skipped (no pack-corrections.md yet)

## Phases
| phase | lane | fires when | state |
|---|---|---|---|
| ground-truth | recon | the request names an existing system/behaviour, or rests on an unverified claim about current behaviour | pending |
| framing | product | the request is a new gameplay system or feature surface, or changes what an existing one is for | not triggered (a one-off diagnostic log system is not a feature surface and changes no existing system's purpose) |
| specification | story | framing produced scope no approved brief covers, and the slice crosses more than one lane's contract | not triggered (single lane — backend — no cross-package contract; the user's own request is the specification per delivery model) |
| design | tech-lead (DESIGN) | the change crosses a package-boundary contract — a shared singleton/component shape, the crate/content pipeline, a new cross-package .asmdef reference | pending — provisionally not triggered (self-contained system, no shared singleton touched), to be confirmed once ground-truth reports how scheduling actually works |
| build | backend, test | anything that edits Impact/Packages/**, Impact/Assets/**, Impact/Tools/**, or Impact/*.md | pending |
| verify | integration | any build lane was dispatched | pending |
| verify | review | the run carries a story whose acceptance criteria someone must accept | not triggered (no story) |
| close | docs | always | pending |

## Artifacts
| # | lane | mode | agent | model | artifact | status | verdict |
|---|------|------|-------|-------|----------|--------|---------|

## Open
| kind | from | ref | one-line | state |
|---|---|---|---|---|

## Closed
| kind | from | absorbed by | one-line |
|---|---|---|---|

## Rounds
| finding | lane | round | of | caused by |
|---|---|---|---|---|

## Replans
| plan | because | change |
|---|---|---|
