REPORT 2026-10-22-admin-sign-in/07
status:      DONE
verdict:     NONE

changed:
  - agentic/runs/2026-10-22-admin-sign-in/07-recon.md — independent verdicts on C1–C14 for better-auth 1.7.12

verification:
  command:   node scratchpad/ba-check/scripts/t.mjs (better-auth 1.7.12, memoryAdapter, design's exact options) + source reading of the package and next 16.4.2
  result:    PASS
  detail:    12 CONFIRMED (C1 C2 C3 C4 C6 C7 C8 C9 C10 C11 C12 C14), 1 REFUTED in part (C5: expired/signed-out cookie gets Max-Age=0 clears), 1 CONFIRMED with caveat (C13: missing Origin is allowed)

contract_notes:
  - none

pack_corrections:
  - none

handoff:
  - C1 CONFIRMED — wrong password and unknown email both throw 401 code INVALID_EMAIL_OR_PASSWORD, no Set-Cookie (script output "C1 wrong pw"/"C1 unknown", headers: []).
  - C2 CONFIRMED for the cookie part — no CSRF cookie anywhere in 1.7.12; sign-in CSRF is formCsrfMiddleware (Origin + Sec-Fetch-*, dist/api/middlewares/origin-check.mjs:123-150), which sets no cookie.
  - C2 caveat — that middleware returns early when ctx.request is absent (origin-check.mjs:124); auth.api.signInEmail with Origin http://evil.example succeeded in the script, so in library-only use CSRF rests entirely on Next (C13).
  - C3 CONFIRMED — successful sign-in emits exactly one Set-Cookie, __Secure-admin.session_token (script "C3 ok"); no session_data or dont_remember.
  - C4 CONFIRMED — "Max-Age=28800; Path=/; HttpOnly; Secure; SameSite=Strict", value "<32-char token>.<base64 HMAC>" (script "C3 ok"); note the __Secure- prefix is added when useSecureCookies is true, so the name is not literally admin.session_token on https.
  - C5 CONFIRMED for missing, forged-signature and malformed cookies — null, no Set-Cookie (script "C5 none/forged/malformed").
  - C5 REFUTED for expired and signed-out cookies — getSession calls deleteSessionCookie (dist/api/routes/session.mjs:156) and emits three Max-Age=0 clears (session_token, session_data, dont_remember); script "C5 expired", "C5 signed-out cookie".
  - C5 context — in a Server Component nextCookies' cookieHelper.set throws and is swallowed (dist/integrations/next-js.mjs:91-95), so no clear reaches the browser; from a server action (requireAdminAction) the clears do reach it. see § C5 and AC 12
  - C6 CONFIRMED — expiresAt = sign-in + 8.0 h; after backdating updatedAt 5 h and calling getSession, expiresAt unchanged (script "C6 expiresAt unchanged true"); refresh path at session.mjs:200 is gated by needsRefresh.
  - C7 CONFIRMED — signOut deleted the row (rows 1→0) and emitted Max-Age=0 clears; nextCookies' after-hook forwards them via cookies().set in a server action (next-js.mjs:77-96).
  - C8 CONFIRMED — an account row with password from better-auth/crypto hashPassword('abcdef') signed in through signInEmail (script "C3 ok").
  - C9 CONFIRMED — with disableIpTracking the stored ipAddress is "" (empty string, not null; dist/db/internal-adapter.mjs:275); userAgent IS stored by default ("UA-test"), so the design's databaseHooks null-out is required.
  - C10 CONFIRMED — logger.disabled: zero console lines captured; with logger on, failures log only "Invalid password" / "User not found" (no email) plus a secret-entropy warning.
  - C11 CONFIRMED — telemetry off by default in 1.7.12: enabled only if options.telemetry.enabled or env BETTER_AUTH_TELEMETRY true (@better-auth/telemetry/dist/index.mjs:360-361); explicit false is belt-and-braces.
  - C12 CONFIRMED — auth.api.signUpEmail returns 400 EMAIL_PASSWORD_SIGN_UP_DISABLED; better-auth registers no Next route itself, routes exist only via toNextJsHandler mounted by the app.
  - C13 CONFIRMED with caveat — next 16.4.2 aborts an action whose Origin host ≠ Host/x-forwarded-host unless in serverActions.allowedOrigins (next/dist/server/app-render/action-handler.js:436-456); a request with NO Origin is let through with a warning (line 436-441).
  - C14 CONFIRMED — sign-in lowercases before lookup (dist/api/routes/sign-in.mjs:317; "A@B.es" signed in); a 6-char password signs in; a 5-char one got INVALID_EMAIL_OR_PASSWORD (generic).
  - AC 12 escalation line: C1, C2, C3 hold; C5 fails as worded for expired/signed-out cookies (deletion clears only, never a new cookie) — the human must rule whether a Max-Age=0 clear on a refused request breaks AC 12 (D-13).

skill_calls:
  - none

risks:
  - Docs pages were not fetched; every verdict rests on 1.7.12 source and script output, which is stronger evidence for this version.
  - Script used memoryAdapter, not drizzle/pg; cookie, session and origin logic is adapter-independent, but adapter field mapping was not exercised.
  - Missing-Origin action POSTs pass Next's check; with SameSite=Strict the session cookie is not sent cross-site, which is the remaining CSRF defence.
  - Guardrail 5: sessions store user agent by default and ipAddress as "" — only the design's databaseHooks keep both empty; a test should pin this.

## Orchestrator brief
- 12 of 14 claims hold outright; C13 holds with a missing-Origin caveat.
- C5 is the only AC-12 claim that fails, and only as Max-Age=0 deletion of an existing cookie for expired/signed-out sessions. § C5 and AC 12
- C2 note: Better Auth's own origin check does not run on auth.api calls; CSRF = Next action check + SameSite=Strict.
- Escalate C5 to the human per D-13.

## C5 and AC 12
A browser presenting an expired or signed-out (but correctly signed) session cookie, when the guard runs getSession inside a server action, receives `Set-Cookie: __Secure-admin.session_token=; Max-Age=0` plus the same for `session_data` and `dont_remember`. These only delete; nothing is stored. In a Server Component (requireAdminPage) Next forbids cookie writes and better-auth swallows the error, so nothing is sent. Options the design could take without changing framework: have checkAdminSession strip Set-Cookie (call getSession with returnHeaders and drop them, and do not rely on nextCookies for get-session), or accept clears as not "setting" a cookie. The ruling is the human's.
