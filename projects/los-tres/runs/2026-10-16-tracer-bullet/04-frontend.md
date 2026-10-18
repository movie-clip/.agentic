REPORT 2026-10-16-tracer-bullet/04
status:      DONE
verdict:     NONE

changed:
  - src/app/layout.tsx — overwrites stub; lang from getLocale(), generateMetadata from Metadata.*, SiteHeader, imports globals.css, force-dynamic
  - src/app/(public)/page.tsx — overwrites stub; main, one h1 (Home.heading with siteName), one p (Home.tagline), force-dynamic
  - src/app/not-found.tsx — new; Spanish 404 from NotFound.* with a link back to /
  - src/app/globals.css — new; plain CSS with variables, no styling system (D-3 O-4)
  - src/components/SiteHeader.tsx — new; header with site name received as a prop, link to /
  - src/i18n/locale.ts — new; constant LOCALE = 'es-ES'
  - src/i18n/request.ts — new; getRequestConfig returns the fixed locale and messages/es-ES.json, no middleware or routing
  - messages/es-ES.json — new; Metadata, Home, NotFound namespaces per C-8, no literal site name
  - next.config.ts — only change is wrapping the config in createNextIntlPlugin('./src/i18n/request.ts')

verification:
  command:   npm run lint && npm run typecheck && npm run build; docker compose up -d --build --wait; curl / and curl -I / on port 3010; SITE_NAME change with docker compose up -d (no --build); restore; docker compose down
  result:    PASS
  detail:    lint, typecheck, build exit 0. GET / 200: lang="es-ES", one h1 "Los Tres", no Set-Cookie (also on 404). SITE_NAME="Nombre Prueba" gave h1 and title "Nombre Prueba" without rebuild. .env restored, stack down.

contract_notes:
  - C-7 holds on GET /: one main, one h1 equal to getSiteName(), one p equal to Home.tagline, title contains the site name, only same-origin scripts, one on-site link (header, href="/").
  - C-8 keys exist with the specified names and placeholders; the header link text is not a message key because it is the siteName prop.
  - Header site name is not an h1 and not in messages; the layout passes getSiteName() to SiteHeader as a prop, since components may not import src/config.
  - Unknown URLs return 404 with the Spanish not-found page rendered inside the root layout (header included).
  - Lane 05 e2e must use APP_PORT 3010 from the local .env; the h1 and title expected values derive from SITE_NAME, never a literal.

pack_corrections:
  - frontend.md — § Before the stack is recorded: replace the body with "The stack is recorded in `CLAUDE.md` § Stack. Report `BLOCKED` only if the tech-lead plan names no directory or file for what you are asked to build."
  - frontend.md — § Layout: replace "*Not yet established.*" with "UI under `src/app` (pages), `src/components`, `src/i18n` (`locale.ts`, `request.ts`), `messages/es-ES.json`, `src/app/globals.css` (plain CSS with variables until the owner picks a styling system, O-4). Public pages under `src/app/(public)/`, admin under `src/app/admin/`. A component never imports `src/db`, `src/server` or `src/config`: the layout or page reads configuration and passes it down as a prop."
  - frontend.md — § Spanish market conventions, add: "next-intl runs without middleware and without i18n routing: locale is the constant `es-ES` in `src/i18n/request.ts`, because next-intl's middleware sets a locale cookie (guardrail 5). Messages are namespaced in one file; the site name enters a message only as the `{siteName}` placeholder filled from `getSiteName()`. No literal site name anywhere in `src/` or `messages/`."
  - frontend.md — § Spanish market conventions, add: "Pages and the root layout that show configuration or data export `dynamic = 'force-dynamic'`; never read `SITE_NAME` or any env at module load. A changed `SITE_NAME` takes a container restart (`docker compose up -d`), not a rebuild."
  - frontend.md — § Spanish market conventions, add: "`next.config.ts` is wrapped with `createNextIntlPlugin('./src/i18n/request.ts')`; server components use `getTranslations(namespace)` and `getLocale()` from `next-intl/server`. Add `NextIntlClientProvider` only when the first client component needs messages."

handoff:
  - lane 05: assert on GET /: 200, text/html, no Set-Cookie, html lang es-ES, exactly one h1 and one main, h1 text equals SITE_NAME, p text equals Home.tagline from messages/es-ES.json, title contains SITE_NAME.
  - lane 05: assert no cookie and a 404 status on an unknown path (for example /no-existe) with the h1 from NotFound.heading.
  - lane 05: assert no off-site anchors and no script whose src is not same-origin on GET /.
  - lane 05 (unit): messages/es-ES.json has the C-8 keys with the placeholder contract, and no case-insensitive "Los Tres" appears under src/ or messages/.
  - lane 06: CLAUDE.md § Commands needs nothing new from this lane; no script was added.

skill_calls:
  - none

risks:
  - The home page has the site name twice (header link and h1), as the order's "header showing the site name" plus C-7 h1 require; a test counting text matches of SITE_NAME would see two.
  - The Spanish copy (title, description, tagline, 404 text) is my own wording; the owner may want to review it.
  - The "Los Tres" check was done by grep over src/ and messages/ only; local .env and .env.example legitimately hold the value.
  - The pack said nothing about components being barred from src/config; I followed the design's layout rule (components never import src/config) by passing siteName as a prop.
