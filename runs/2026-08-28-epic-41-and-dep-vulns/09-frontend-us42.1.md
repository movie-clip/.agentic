REPORT 2026-08-28-epic-41-and-dep-vulns/09
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   cd apps/desktop && npx vitest run && npx tsc --noEmit
  result:    PASS
  detail:    vitest 40 files / 359 tests passed; tsc --noEmit exit 0 clean; run against the unchanged repo, manifests byte-identical

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - draft finding F-6 (@babel/core) is ready for order 10 to transcribe into the findings doc verbatim — see § Draft finding F-6
  - F-6 row values for the Epic 36 findings table: package @babel/core | ids GHSA-4x5r-pxfx-6jf8 / CVE-2026-49356 | source GitHub Advisory DB REST API + npm audit, both live 2026-08-28 | severity low (CVSS 3.2) | reachable build-time only, vulnerable path not reached, no shipped runtime surface | min safe 7.29.6 | impact none (not a backend dep, does not touch dashboardGoldens.ts) | bucket (a) safe
  - remediation story must bump lockfile-only with a SCOPED command (`npm install @babel/core@7.29.7 --package-lock-only` or `npm update @babel/core`), NOT bare `npm audit fix` — see § Draft finding F-6, "Lockfile-only resolution"
  - test lane / remediation CI check after any future bump: `npx vitest run` + `npx tsc --noEmit` + the designSystem.audit.test.ts run stay green; no quant audit needed for this dep

risks:
  - bare `npm audit fix` (non-dry-run) also rewrites unrelated lockfile subtrees (postcss, nanoid, ws, browserslist data, adds knip's transitive tree) — those are other advisories; folding them into a "babel bump" PR would smuggle five unrelated fixes past review
  - GitHub Advisory DB names first_patched_version 7.29.6 for the 7.x line; npm's fixer prefers 7.29.7 (latest 7-line patch). Minimum-safe recorded as 7.29.6; the exact adopt version is the remediation story's call (non-goal here)
  - the US-42.1 seed named only @babel/core, but the live `npm audit` this order ran shows the frontend tree also carries moderate/high advisories on vite, esbuild, postcss, nanoid, @vitest/mocker, vite-node — out of scope for this order and F-6, flagged so the wider frontend exposure is not lost when Epic 42 is scoped

## Orchestrator brief

- One section below the report block: **§ Draft finding F-6** — the full draft finding for `@babel/core` (T-42.1.2), for order 10 (docs) to consolidate into `docs/product/dependency-advisory-assessment-2026-08.md`. Nothing in it is a decision; it is a finding.
- Verdict on the order: DONE. No repo file changed. `git status --porcelain apps/desktop/package.json apps/desktop/package-lock.json` is empty — confirmed after `npm audit` and `npm audit fix --dry-run` (both read-only). Verification green (vitest + tsc) against the unchanged tree.
- Bucket call for F-6: **(a) safe** — build-time-only dev dependency, lockfile-only patch bump, no analytic or runtime surface.
- Network was available this session; no field in F-6 is unverified.

## Draft finding F-6

### Package and dependency path

- **Package:** `@babel/core`
- **Installed version:** `7.29.0` (`apps/desktop/package-lock.json` → `node_modules/@babel/core`, `"version": "7.29.0"`, `"dev": true`; single install, one lockfile node, no duplicate copies).
- **Transitive — confirmed.** Not present in `apps/desktop/package.json` (neither `dependencies` nor `devDependencies`). Dependency path:
  - `apps/desktop` (root) → `devDependencies` → `@vitejs/plugin-react` `^4.3.4` (resolved `4.7.0`)
  - `@vitejs/plugin-react@4.7.0` → `dependencies` → `@babel/core` `^7.28.0` (resolved `7.29.0`)
- `@vitejs/plugin-react` is the only package that declares `@babel/core` as a real dependency. Three sibling `@babel/*` packages declare it as a *peer* only — `@babel/helper-module-transforms` (`^7.0.0`), `@babel/plugin-transform-react-jsx-self` (`^7.0.0-0`), `@babel/plugin-transform-react-jsx-source` (`^7.0.0-0`) — all pulled by the same `@vitejs/plugin-react`.
- `vite.config.ts` uses `react()` as its sole plugin (the Babel-based `@vitejs/plugin-react`, not `@vitejs/plugin-react-swc`), and vitest reuses the same `vite.config.ts` via its `test` key.

### AC2 — Advisory id and severity

- **Advisory:** `GHSA-4x5r-pxfx-6jf8` — CVE `CVE-2026-49356`
- **Title:** "@babel/core: Arbitrary File Read via sourceMappingURL Comment"
- **Severity:** low. CVSS 3.1 base score **3.2**, vector `CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N`. CWE-22 (path traversal), CWE-200 (information exposure).
- **Published:** 2026-06-15.
- **Affected / patched ranges (from the GitHub Advisory DB):**
  - 7.x line: vulnerable `<= 7.29.0`; **first patched version `7.29.6`**.
  - 8.x pre-release line: vulnerable `>= 8.0.0-alpha.0, < 8.0.0-rc.5`; patched `8.0.0-rc.6` (not relevant — this repo is on the 7.x line).
- The installed `7.29.0` is inside the affected range.

### AC3 / AC10 — Reachability

**Build-time execution: yes.** `@vitejs/plugin-react` invokes `@babel/core` on this repo's own first-party `apps/desktop/src/**` `.ts`/`.tsx` source during `vite dev`, `vite build`, and `vitest run` (React Fast Refresh transform + automatic JSX runtime). So `@babel/core` code does execute inside this repo's Node toolchain.

**Vulnerable-path reachability: not reached from normal usage — reasoning, not a bare "no".** The CVE triggers when Babel compiles source *text* that contains a crafted `//# sourceMappingURL=<path>` comment while input-source-map reading is active; Babel then reads that referenced file from disk and can leak its bytes into the generated source map (arbitrary file read). In this repo Babel is fed only version-controlled, developer-authored source; `@vitejs/plugin-react` excludes `node_modules`, so no third-party or attacker-controlled source text is compiled. Exploitation additionally requires local access (`AV:L`), has high attack complexity (`AC:H`), and needs a malicious `sourceMappingURL` comment introduced into the source tree — which already implies commit or build-host access, a strictly larger capability than the file read it would grant. The trusted-input boundary plus the local-only, high-complexity vector is why the path is not considered reachable here.

**Shipped runtime surface: none.** `@babel/core` is a Node build-time tool. The compiled browser bundle (`apps/desktop/dist/`) contains no Babel code (`grep -rc "@babel/core\|sourceMappingURL" dist/` → no matches), and the Tauri desktop app ships that bundle. Nothing Babel touches reaches an end user's machine at runtime.

### AC4 — Minimum safe version and lockfile-only resolution

- **Minimum non-vulnerable version:** `7.29.6` (GitHub Advisory DB `first_patched_version` for the 7.x line). `npm audit fix` targets `7.29.7` (the latest 7.x patch; versions available after 7.29.0 are 7.29.6, 7.29.7, then 8.x). Either resolves the advisory.
- **A lockfile-only resolution exists — confirmed.** Both `7.29.6` and `7.29.7` satisfy `@vitejs/plugin-react@4.7.0`'s `@babel/core: ^7.28.0` range, so re-resolving the transitive dependency needs **no `package.json` change, no `overrides` entry, and no toolchain (Vite / `@vitejs/plugin-react`) bump**.
  - `npm audit --json` reports `"fixAvailable": true` (boolean, not an object) for `@babel/core` — npm classifies it as a non-breaking, in-range fix.
  - `npm audit fix --dry-run --json` (run read-only this session) reports `change @babel/core 7.29.0 => 7.29.7` (plus its `@babel/*` sub-tree), i.e. `package-lock.json`-only.
  - **Scoped command for the remediation story:** `npm install @babel/core@7.29.7 --package-lock-only` (or `npm update @babel/core`) keeps the lockfile diff to the `@babel/*` subtree. A bare `npm audit fix` would additionally rewrite unrelated subtrees (postcss, nanoid, ws, browserslist data) and add knip's transitive tree — those belong to other advisories, not F-6.

### AC6 — Advisory-data provenance

- Advisory id, CVE, title, severity, CVSS vector/score, publish date, and affected/patched ranges: **live query of the GitHub Advisory Database REST API** (`GET https://api.github.com/advisories/GHSA-4x5r-pxfx-6jf8`) on 2026-08-28.
- Cross-checked against **`npm audit --json`** run in `apps/desktop` the same session — npm registry advisory source `1123528`, same `GHSA-4x5r-pxfx-6jf8`, same `<= 7.29.0` range, severity `low`, CVSS 3.2. The two sources agree.
- Installed version and dependency path: read directly from `apps/desktop/package-lock.json` at HEAD.
- Network was available; **no field in this finding is unverified.**
- `npm audit` and `npm audit fix --dry-run` were run read-only. `git status --porcelain apps/desktop/package.json apps/desktop/package-lock.json` is empty afterwards — manifests byte-identical (AC9).

### AC7 — Draft bucket assignment

**Bucket (a) — safe.** Build-time-only dev dependency with no analytic and no shipped-runtime surface. The fix is a lockfile-only patch bump (`7.29.0` → `7.29.6`/`7.29.7`) inside the existing `^7.28.0` range. It is not a backend dependency, so it cannot move a backend golden; it does not touch `apps/desktop/src/**` or `apps/desktop/src/test/dashboardGoldens.ts`, so it cannot move a frontend golden. The only post-bump check is that `npx vitest run`, `npx tsc --noEmit`, and `designSystem.audit.test.ts` stay green — a plain CI check, not a quant audit. Not bucket (b) (no analytic output — Babel is a JSX/TS transform, not finance math). Not bucket (c) (a fixed version exists and is reachable without a coordinated toolchain bump).
