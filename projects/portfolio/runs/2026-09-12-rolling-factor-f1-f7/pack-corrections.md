# Pack corrections — 2026-09-12-rolling-factor-f1-f7

- `capabilities/frontend.md` § The eight primitives — table states `TrustBadge` accepts `{type: 'synthetic'|'unavailable'}`; `TrustBadge.tsx:14` already has a `'degraded'` member in the union and in production use (added by 03-frontend.md in this run). Replace the table entry with `{type: 'synthetic'|'unavailable'|'degraded'}`.
  — from 06-frontend.md § pack_corrections.
