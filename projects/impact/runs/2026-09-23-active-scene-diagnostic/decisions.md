# Decisions — 2026-09-23-active-scene-diagnostic

## D-1 · verify (test rerun) · 2026-09-23
open decision:  02-test.md's verification is blocked: Unity Editor PID 19804 open
                (blocks batchmode) and its Pipeline server unreachable (blocks
                unity-cli) at the same time — the lane could not proceed on either
                path without closing the human's open Editor, which is outside its
                authority.
raised by:      02-test.md § verification, § risks (bullet 3)
ruling:         "Close the Editor yourself" — the human closes Unity Editor PID
                19804 themselves rather than authorizing the orchestrator/lane to
                kill it, and rather than debugging the Pipeline server.
by:             the human, in session
confirmed:      PID 19804 verified no longer in the process list immediately after
                the ruling — orchestrator check via `tasklist`, not the human's own
                report.
