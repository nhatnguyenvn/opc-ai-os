# CR-PHASE-B-002 — Organization schema, Wave 1 first increment

State: TESTING. Builds on CR-PHASE-B-001 without modifying applied migrations.

Migration 0003 adds Business, Actor, LegalEntity, Venture and Agent identities,
explicit Actor/Agent business scopes, market and bank-reference child tables,
and organization snapshot history. Business founder membership is deferred until
transaction commit so bootstrap is possible without a permanently unowned row.
Membership is a relationship, not an authorization grant.

Implementation choices for review: DRAFT/ACTIVE/DISABLED/ARCHIVED form the initial
organization status lookup; UNSPECIFIED is the only seeded Venture stage. These
are implementation seeds, not source-defined lifecycle approval. All identities
default to DRAFT. Actor types follow the Phase B examples. Agent permissions and
authority levels remain references to the existing configuration, not DB grants.

Reference scope: Business/Actor/Agent global; LegalEntity/Venture per Business.
Founder and Venture owner must have matching business membership. Bank references
must match their LegalEntity business. Currency is three uppercase letters, not
yet an ISO currency registry validation. Capital is exact numeric and nonnegative.

Audit: identity-table UPDATE automatically advances version and records a JSONB
snapshot; DELETE is rejected. Database actor provenance is retained. This is not
yet end-user actor attribution or a complete audit-event implementation. Snapshot
JSON supplements typed domain fields; canonical relationships are relational.

Open qualification: full lifecycle transitions, controlled strategic-status values,
Agent actor-type restriction, application roles/RLS, owner-resistant enforcement,
TRUNCATE safeguards, relationship-row history, external permission reference checks,
and future Product/Offer, Risk/Assumption, license/obligation and Tool links. No claim
that all B1.1-B1.5 or DB-001–DB-012 acceptance gates are closed.

Tests exercise duplicate references, orphan business, cross-business owner,
negative capital, invalid status, version history, and identity hard-delete denial.
Fixtures are rolled back. No business production records are seeded.

Recovery: atomic rollback on failure; after success preserve schema and history and
fix forward. No automatic destructive downgrade is supplied. Runtime and production
configuration and authority policies remain unchanged. Exact-candidate merge review
and approval remain required.
