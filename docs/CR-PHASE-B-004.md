# CR-PHASE-B-004 — Initial Decision, Approval and Delegation records

State: TESTING. Source: OPC-BUILD-002 B1.6–B1.8 and Module 4 objects 14,15,62.

Migration 0005 creates typed Decision, Approval and Delegation tables, decision
options, and an effective_delegation view. Approval binds object type/ID/version,
nonempty scope, authority, recipient and terms hash. Issued approval bindings are
immutable; approved records may be revoked but cannot be reactivated. A new approval
is needed for changed bindings. Delegation references Approval within its business.

The view checks the exact delegation ID/version/scope/authority/terms hash,
authority actor and recipient, DELEGATE action, statuses, start/end windows and
revocation. It evaluates time on every statement; it does not rely on a stale
boolean. Linking an approval increments delegation version; approval binds that
resulting version. No runtime grants, authority changes or production activation.

Implementation vocabularies DRAFT/ACTIVE/APPROVED/REJECTED/REVOKED/ARCHIVED are
initial database states, not new approved authority policy. A valid row or view
result is NOT sufficient permission to act: the Control Engine must still verify
Founder authority, signature/provenance, terms hash construction, amount limits,
conditions and effective policies. No executor consumes this view yet.

Deliberate limits: polymorphic approval targets outside Delegation are recorded
but do not yet have object-specific FK validation. Exact hash is supplied and must
be computed/verified by the later approval service. Scope equality is exact text,
not scope-subset inference. Evidence/Assumption/Risk links, complete lifecycle
transitions, role isolation, and end-user actor attribution remain pending.
Shared snapshot history records database changes; it is not full audit_event.

Tests: no approval means no effective delegation; invalid approval FK rejection;
valid exact binding; expired/revoked approval exclusion; issued terms immutable;
changed delegation scope/version invalidates the old binding; confidence bounds.
Fixtures and all snapshots are rolled back. Existing applied migrations are unchanged.

Recovery: failed migration is atomic; after successful application preserve
history and fix forward. Exact-candidate Founder review/approval remains required
before merge; no approval for runtime authority is inferred from implementation.
