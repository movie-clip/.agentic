REPORT 2026-10-22-admin-sign-in/02
status:      DONE
verdict:     NONE

changed:
  - none

verification:
  command:   NONE
  result:    NOT_RUN
  detail:    read-only framing; sources opened: mvp.md, decisions 0001/0006/0009/0010, issues #22 and #23, product pack, project profile, repo grep for existing auth code

contract_notes:
  - docs/decisions needs a new record for the auth approach (OD1), already ticket #74; it should also name the TOTP direction so S2.2 inherits it
  - CLAUDE.md § Commands gains the create-admin verb (ticket #74); the Compose entrypoint currently exits 64 on any other verb
  - messages/es-ES.json gains a separate admin section if OD8 is ruled as recommended
  - the public privacy text (messages/es-ES.json, adminsBody) already promises an admin-only session cookie; S2.1 must keep that sentence true

pack_corrections:
  - none

handoff:
  - 1 story confirmed for E2 (#10): S2.1 #22 — see § Stories
  - open decision: OD1 approach, recommend the small purpose-built module — see § Open decisions
  - open decision: OD7 TOTP-library part, recommend S2.1 adds no dependency and the TOTP choice is made at S2.2 design — see § Open decisions
  - open decision: OD8 admin language, recommend Spanish in a separate admin message section — see § Open decisions
  - open decision: password-only login has no lockout until S2.2; confirm S2.1 is never deployed to the VPS alone — see § Open decisions
  - story file is warranted (specification clause: crosses backend, frontend and test, and changes the data model) — see § Stories

skill_calls:
  - none

risks:
  - Took on trust, from issue #22: that the guardrail-3 tests deferred from slice A are a recorded deferral. I opened tests/support/routes.ts, which has a classifyRoute helper treating a first directory named admin as an admin route, and decision 0006 line 35 ("admin routes reject anonymous requests on the server"). I did not open the deferral record itself.
  - Took on trust, from issue #22: slice number (11 of 39), sizes, and that OD1, OD7 and OD8 are unruled. I found no ruling in docs/decisions. The OD ids exist only in issue bodies, not in repo docs.
  - Did not open epic #10 or issues #24 to #26 (S2.3, S2.4); the S2.1/S2.2 boundary rests on #22 and #23 only.
  - OD8 touches settled scope. mvp.md § Out of MVP already says "Any language other than Spanish", and CLAUDE.md puts all copy in es-ES message files. My recommendation follows those; the only real open point is how the admin copy is organised.
  - No code sets any admin cookie today. grep over src and package.json finds no users, sessions, hashing or TOTP code, so S2.1 starts from nothing.
  - I did not check any package registry; no TOTP library is named or vetted.

## Orchestrator brief
- verdict: New story, existing epic. S2.1 (#22) is correctly placed and is in the approved MVP; nothing is already covered and no recorded decision is overruled.
- epic: E2 (#10), Backlog; S2.1 is slice 11 of 39, size L, P0, no dependencies.
- 1 story: #22 S2.1 an admin signs in with email and password and reaches an admin area that no anonymous request can reach.
- scope edge: S2.1 is password only. TOTP, enrolment output and lockout are S2.2 (#23), which depends on #22.
- story file: warranted. The specification clause fires: three lanes, a data-model change, a security-critical surface.
- OD1: recommend the small purpose-built module (three users, no OAuth), recorded as a decision (ticket #74).
- OD7, TOTP part: recommend S2.1 adds no runtime dependency, since TOTP belongs to S2.2. Choose the TOTP library at S2.2 design.
- OD8: recommend Spanish, in a separate admin section of the message files; already implied by mvp.md and decision 0001.
- gap: password-only login has no brute-force limit until S2.2, so S2.1 must not be deployed to the VPS alone. Human to confirm.
- blocks dispatch: OD1 and OD8 must be ruled before design (per #22). The TOTP-library question does not block S2.1.
- sections below: Placement · Stories · Sequence · Open decisions · Already covered

## Placement
mvp.md § Admin area says: "Accounts for the three team members only, created by a command. There is no sign-up. Login is email + password + authenticator-app code (TOTP). Every admin route and action checks the role on the server." Everything else in that section (feeds, imports, categories, matching, hiding) needs this first. So E2 comes before every S3.x admin story and S9.4, as #22 says.

The nearest precedent is E2's own split. #22 is the password half and #23 (S2.2) adds the second factor, so they are siblings and not one story. The split lets the guard and session contract land first, and S2.2 then only extends it. S2.1 is a thin vertical slice in that an admin can really sign in and reach a shell. It is the first story that sets a cookie, and the foundation for guardrail 3.

Guardrail check:
- Guardrail 3 is the story's whole purpose.
- Guardrail 5 applies: no email, password or token in logs.
- Decision 0009 already allows an admin-only strictly-necessary session cookie, and the privacy page already says so. Public pages must still set no cookie.
- Guardrail 1 is untouched; S2.1 adds no way to publish data.

## Stories

### #22 S2.1 Admin signs in with email and password
Outcome: an admin signs in with email and password and reaches the admin area, and no one else can reach any admin route or action.

value: the three team members get a protected place to work, and every later admin story gets one server-side check to use. Until this exists none of the admin list in mvp.md can be built safely.

slice, in:
- Accounts created only by a command; no sign-up route.
- Login and logout.
- An admin shell with navigation, in Spanish.
- A session in a cookie set for admins only.
- A server-side check on every admin route and action that refuses an anonymous request.
- Passwords stored hashed; email, password and token never logged.
- Admin pages not indexed.
- The guardrail-3 test suite.
- The decision record, and the command documented.

slice, out (the S2.2 boundary, explicit):
- Authenticator code, TOTP secret storage and enrolment output: S2.2 (#23).
- Failed-attempt lockout: S2.2.
- Any admin feature beyond the shell: S2.3, S2.4 and the S3.x stories.
- Password reset by email, public accounts and "remember me": not in the MVP. mvp.md § Out of MVP excludes public accounts, and no owner call on admin password recovery is recorded. The story file should state how recovery works (see Open decisions).

depends_on: none.

invest:
- Small is weak. The size is L and there are seven tickets. I accept it because the session contract, the guard and the shell cannot be accepted apart from each other. If the tech lead finds the guard and sessions can be accepted alone, the fallback split is "sign-in and guard" first, "shell and navigation" second.
- Valuable is met for the team and not for visitors, which is right for a prerequisite.

Story file: warranted. The issue says yes and I agree. It crosses backend, frontend and test lanes and changes the data model, so the specification clause in phases.md fires. Acceptance outline the story file must carry (topics for the story lane, not criteria):
1. No sign-up path. Accounts come from the command only. The command must not leave the password in shell history or logs (the story lane fixes how it is entered).
2. Correct credentials reach the admin area. A wrong email and a wrong password give the same message, which does not reveal which was wrong. S2.2 already requires this of the factors, and it is cheap to keep from the start.
3. Logout ends the session on the server. The story file must state the session lifetime and expiry. The #22 outline is silent, and a limit is a product call.
4. The cookie is set for admins only. Public pages and the `/go/<offer>` redirect still set no cookie, and a test checks it.
5. Every admin route and action refuses an anonymous request on the server, and a new admin route that forgets the check is caught by the suite. tests/support/routes.ts already classifies routes by first directory, which the suite can build on.
6. Passwords are stored hashed. No email, password or token reaches any log, and a test checks it.
7. Admin pages carry a noindex signal and are absent from the sitemap.
8. The admin shell is in Spanish (OD8), with copy in message files.
9. The decision record exists, and create-admin is in CLAUDE.md § Commands.
10. The story file states plainly that S2.1 ships a password-only login that is not deployable (see Open decisions).

## Sequence
1. Rule OD1 and OD8 (human). Hard dependency: #22 says both are settled before design.
2. Story lane writes the story file; then ux and design run, per the run plan. OD7's TOTP part is not needed here.
3. Build in the ticket order #68 to #74: tables, hashing, command, sessions and guard, login and shell, the test suite, docs. The decision record (#74) is drafted from the OD1 ruling.
4. S2.2 (#23) follows, with its TOTP library chosen at its design. Hard dependency: #23 depends on #22, and no admin route is deployed to the VPS before #23.

Risk-first note: the guard contract is the thing that could invalidate later stories, so the guard (#71) and the guardrail-3 suite (#73) are the first things for the tech lead to settle, before the login screen.

## Open decisions

- **OD1. How is admin authentication built?**
  - A. A small purpose-built module: Node's built-in password hashing, server-stored opaque sessions in an HttpOnly cookie, and (in S2.2) one TOTP library. It fits three users with no OAuth. The cost is that we own security-critical code, so the suite in #73 is essential.
  - B. An off-the-shelf auth framework. Less code to own, but it brings a dependency tree and defaults aimed at OAuth and public sign-up, which this product excludes. It is also harder to hold to "no cookie for anyone but admins".
  - Recommendation: A, recorded as a decision (ticket #74). I agree with the issue's reasoning.
  - Blocks: S2.1 design, and through it S2.2 to S2.4, the S3.x admin stories and S9.4.

- **OD7, TOTP-library part only. Does S2.1 need a new dependency, and which TOTP library?**
  - Does S2.1 need one? No. Hashing and session tokens use what Node already provides, and TOTP is S2.2. Nothing in the #22 outline requires a package. Recommend S2.1 adds no runtime dependency. If the tech lead's design finds one is needed, that is a new decision record and not a quiet addition.
  - The library itself. Options: (A) one maintained TOTP library; (B) a small in-repo RFC 6238 module on Node's crypto, which adds no dependency but adds security code to own and test. Recommend A, chosen at S2.2 design on maintenance, licence and size, with a decision record then. I have not checked any registry and name no library.
  - Blocks: S2.2 design only, not S2.1. #22 lists the TOTP library under S2.1, but the work that uses it is in #23. The orchestrator can lift it out of S2.1's blockers.

- **OD8. What language is the admin interface?**
  - A. Spanish, in message files under a separate admin section, same rule as the public site.
  - B. English for the admin only.
  - Recommendation: A. mvp.md § Out of MVP lists "Any language other than Spanish", and CLAUDE.md § Conventions puts all user-facing copy in es-ES message files. B would need a second message set and goes against a settled scope item. The only remaining point is that admin copy sits in its own section so it does not mix with public copy.
  - Blocks: S2.1 design, trivially.

- **Is it acceptable that S2.1 is a password-only login that is never deployed on its own?** (Human to confirm; not one of the three ODs.)
  - Why it matters: mvp.md says login is email + password + TOTP, and lockout arrives only with S2.2. S2.1 alone leaves guessing unlimited and has no second factor. #23 already says S2.2 "must be done before any admin route is deployed to the VPS".
  - Recommendation: yes. Keep S2.1 local-only, and have the story file state it as a standing constraint.
  - Blocks: nothing in S2.1. It affects the order of the deploy work.

- **Admin password recovery and session lifetime.** (The story lane may propose defaults for the human to approve.)
  - Neither is in mvp.md or #22. Recovery by email would add outgoing mail, which is not in the stack. Recommend recovery by re-running the command, and a limited session lifetime stated in the story file.

## Already covered
- Nothing in the repo implements this. grep over src and package.json for users, sessions, hashing and TOTP finds nothing, and src/app has only the public route group. S2.1 is not covered by existing code.
- Existing pieces S2.1 builds on, which are not duplicates:
  - tests/support/routes.ts, which classifies a route as public or admin by its first directory.
  - Decision 0001: the admin role check runs in server code (route handlers, server actions, data access) and never in components alone.
  - Decision 0006: "admin routes reject anonymous requests on the server" is a gate test.
  - Decision 0009: an admin-only session cookie needs no consent.
  - The privacy page text (messages/es-ES.json, adminsBody), which already tells visitors this.
- No recorded decision on the auth approach, the admin language or the TOTP library exists in docs/decisions, so none is being overruled.
- S2.1 and S2.2 (#23) do not overlap: #23 depends on #22 and extends its contract.
