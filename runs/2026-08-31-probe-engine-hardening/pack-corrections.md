# Pack corrections — run 2026-08-31-probe-engine-hardening

Source: contract_notes from 04-technical-plan, 05-backend-probing, 06-backend-testing.
All concern `.agentic/projects/portfolio/capabilities/` packs going stale against the
landed `probe_engine` / suite-runner changes. Apply at close-out (tickets T-43.1.5, T-43.2.4).

## 1. backend.md — "response is not truncated" is now false
- **File / anchor:** `capabilities/backend.md` (~line 166, the probe_engine description).
- **False premise:** states the probe response "is not truncated".
- **Replacement wording:** the probe response now bounds long arrays head/tail
  (`PROBE_ARRAY_HEAD`/`PROBE_ARRAY_TAIL` = 5, bound only when `len > 11`), replacing
  the elided middle with a single `{"__probe_truncated__": {original_count, dropped,
  kept_head, kept_tail, note}}` sentinel; `truncation` in the envelope lists the dotted
  paths bounded. A `fields=` arg filters to named top-level body keys (trust keys always
  retained) and is applied *before* truncation.

## 2. quant.md — same "not truncated" claim
- **File / anchor:** `capabilities/quant.md` (~lines 166–169).
- **False premise / replacement:** identical to item 1 — reword the "not truncated"
  statement to the bounded-head/tail + sentinel behaviour.

## 3. testing.md — "does not validate the payload shape"
- **File / anchor:** `capabilities/testing.md` (~lines 154–156).
- **False premise:** states probe_engine "does not validate the payload shape".
- **Replacement wording:** probe_engine now classifies the route's expected request-body
  shape (`flat` / `snapshot-wrapped` / `bare-snapshot` / `unclassified`) via live FastAPI
  route introspection, reports `request_shape` + `request_model`, and emits a warn-only
  `shape_mismatch` when the supplied payload has/omits a top-level `snapshot` key against
  what the route expects. It still never returns 422 and never raises on a mismatch — the
  probe still POSTs and returns the real response.

## 4. backend.md + testing.md — suite-runner tool descriptions lag
- **File / anchor:** `capabilities/backend.md` and `capabilities/testing.md`, the
  `run_tests` / `check_gates` / `reset_goldens` descriptions.
- **Additions needed:**
  - `run_tests` / `check_gates` now return a **structured timeout result** (identifies
    scope / command / limit; does not raise) when a subprocess exceeds its per-scope
    budget (`TIMEOUTS` dict local to `tools/testing.py`: full 1800 / backend 600 /
    frontend 600 / typecheck 300 / gate 300 / git 30 s). `check_gates` isolates each gate
    subprocess, so a per-gate timeout is reported while completed gates still return
    results; its result dict gains a top-level `timeouts` key.
  - `reset_goldens` now captures `git diff --stat` and a bounded `git diff` of
    `dashboardGoldens.ts` **before** the `git checkout --`, and returns both
    (`diff_stat` / `diff`); the capture survives a failed checkout; a no-drift reset
    reports nothing discarded.

## 5. No repo-doc change (confirm only)
- No `docs/contracts/` or `docs/finance/` file is affected — the tool passes engine trust
  strings through verbatim and defines no contract field. No TS type, no `app/schemas/`
  model, no dependency-pin change. Verify and record "none".

## 6. Head-derivation drift (pack-process note, not a code fact)
- Every Bash-enabled lane in this run (05, 06, 07, 08, 09) returned a `REPORT HEAD` with
  the `headline:` line missing — they ran `check_report.py --emit-head` but returned the
  template without filling `<outcome ...>`. Consider tightening the head-return step in
  the affected agent files / packs so `headline` is always filled before the head is
  returned. Orchestrator read each artifact directly to compensate.
