# Decisions — 2026-10-22-admin-sign-in

## D-1 · framing · 2026-10-22
open decision:  OD1 — how admin authentication is built: purpose-built module or off-the-shelf auth framework
raised by:      02-delivery-brief.md § Open decisions (OD1)
ruling:         "use auth framework"
by:             the human, in session (against the brief's recommendation A)

## D-2 · framing · 2026-10-22
open decision:  OD8 — admin interface language
raised by:      02-delivery-brief.md § Open decisions (OD8)
ruling:         "use english"
by:             the human, in session (against the brief's recommendation A)

## D-3 · framing · 2026-10-22
open decision:  OD7 (TOTP part) — S2.1 adds no new runtime library; TOTP library chosen at S2.2
raised by:      02-delivery-brief.md § Open decisions (OD7)
ruling:         "Yes"
by:             the human, in session
note:           conflicts with D-1 (a framework is a runtime dependency) — follow-up Q6 pending

## D-4 · framing · 2026-10-22
open decision:  S2.1 is password-only and is never deployed on its own before S2.2
raised by:      02-delivery-brief.md § Open decisions (password-only login)
ruling:         "recommendation"
by:             the human, in session

## D-5 · framing · 2026-10-22
open decision:  password recovery and session lifetime
raised by:      02-delivery-brief.md § Open decisions (recovery and session lifetime)
ruling:         "follow recommendation" — recovery by re-running the command; limited session lifetime, value proposed by the story lane
by:             the human, in session

## D-6 · framing · 2026-10-22
open decision:  Q6 — D-1 (framework) vs D-3 (no new runtime library)
raised by:      decisions.md § D-1, § D-3
ruling:         "you can add needed library or framework"
by:             the human, in session — supersedes D-3's "no new library"; each new dependency still gets a decision record

## D-7 · framing · 2026-10-22
open decision:  Q7 — who chooses the auth framework
raised by:      decisions.md § D-1; agentic/project.md § Building before the stack exists
ruling:         "tech lead, but double check his pick"
by:             the human, in session — design (tech-lead DESIGN) picks; the pick is independently checked before the build go

## D-8 · framing · 2026-10-22
open decision:  Q8 — English admin (D-2) vs mvp.md / CLAUDE.md Spanish-only rule
raised by:      decisions.md § D-2; docs/product/mvp.md § Out of MVP; CLAUDE.md § Conventions
ruling:         "Okay, make it Spanish to follow the rule"
by:             the human, in session — supersedes D-2: admin copy is es-ES, in its own admin section of the message files

## D-9 · specification · 2026-10-22
open decision:  Q9 — session lifetime
raised by:      US-2.1-admin-sign-in.md § Open decisions 1
ruling:         "Yes, 8 hours, no idle timeout"
by:             the human, in session

## D-10 · specification · 2026-10-22
open decision:  Q10 — what an anonymous request to an admin URL sees
raised by:      US-2.1-admin-sign-in.md § Open decisions 2
ruling:         "Yes, send them to sign-in"
by:             the human, in session

## D-11 · specification · 2026-10-22
open decision:  Q11 — minimum password length (proposal was 12)
raised by:      US-2.1-admin-sign-in.md § Open decisions 3
ruling:         "make it shorter, I do not need anything super secure right now, 6 character should be fine"
by:             the human, in session — minimum 6 characters, no composition rule

## D-12 · specification · 2026-10-22
open decision:  Q12 — re-running create-admin ends that admin's sessions
raised by:      US-2.1-admin-sign-in.md § Open decisions 4
ruling:         "Yes, follow your recommendation"
by:             the human, in session

## D-13 · specification · 2026-10-22
open decision:  Q13 — no cookie before successful sign-in (AC 12), even if it narrows the framework choice
raised by:      US-2.1-admin-sign-in.md § Open decisions 6
ruling:         "Yes. That keeps the promise the privacy page already makes"
by:             the human, in session

## D-14 · specification · 2026-10-22
open decision:  Q14 — approve the US-2.1 draft with D-9..D-13
raised by:      03-story.md § Orchestrator brief
ruling:         "approve"
by:             the human, in session — the story lane applies D-9..D-13 and marks the story approved

## D-15 · design · 2026-10-22
open decision:  Q15 — Better Auth sends Max-Age=0 cookie deletions on expired/signed-out sessions; does that break AC 12?
raised by:      07-recon.md § C5 and AC 12
ruling:         "yes, strip the header"
by:             the human, in session — the guard strips Set-Cookie headers from getSession so no admin response carries a cookie header unless sign-in succeeded

## D-16 · design · 2026-10-22
open decision:  Q16 — CSRF: Better Auth's Origin check is skipped via auth.api; Next lets a missing Origin through
raised by:      07-recon.md § C2, § C13
ruling:         "Yes"
by:             the human, in session — sign-in and sign-out actions refuse a missing or mismatched Origin

## D-17 · build · 2026-10-22
open decision:  Q17 — go on the build plan (06-design.md + D-15, D-16; backend, frontend, test, docs)
raised by:      06-design.md § Lanes; 07-recon.md
ruling:         "Yes, go"
by:             the human, in session

## D-18 · verify · 2026-10-22
open decision:  resume after blocked_on; dropped lane risks; close-time housekeeping
raised by:      run.md blocked_on; 08-backend.md, 09-frontend.md, 10-test.md § risks
ruling:         ".env now has AUTH_SECRET and SITE_URL and the stack is up, so clear blocked_on." Add the five dropped risk rows to Open; close both "CLAUDE.md § Commands" and both "docs/design/system.md" rows as landed by 11-docs. "dispatch 12 integration with every Open risk row in its inputs, so the tech lead rules on each one and writes change requests for the blocking ones." "At close, also: add AGENTS.md to .gitignore, remove the e2e-admin@example.test row from the dev DB, and recreate the app container with the new .env."
by:             the human, in session

## D-19 · verify · 2026-10-22
open decision:  anonymous unmatched /admin/* — redirect to sign-in (18-frontend) or ordinary 404 (story AC 1)?
raised by:      18-frontend.md § handoff (AC 1 bullet), § Anonymous behaviour
ruling:         "Redirect; amend AC 1" — keep 18's behaviour: anonymous /admin/* → 307 to sign-in; story lane revises AC 1; test lane updates the two e2e tests.
by:             the human, in session

## D-20 · close · 2026-10-22
open decision:  close sweep fails only on Artifacts row 07 (agent general-purpose has no network definition); mark the PR ready anyway?
raised by:      check_report.py <run_dir>/ --require-heads at close
ruling:         "Accept; mark PR ready"
by:             the human, in session
