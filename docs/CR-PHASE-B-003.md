# CR-PHASE-B-003 — Organization integrity hardening

State: TESTING. Additive migration 0004; migrations 0001–0003 remain immutable.

Agent now requires an AI_AGENT Actor through a composite FK. Changing the linked
Actor type is rejected. Identity INSERT stamps version=1 and database provenance.
TRUNCATE is rejected on identity and relationship tables. Relationship changes
are recorded with prior/new values and database actor in append-only history.

This enforces structural integrity, not new execution authority. No application
role grants, production activation or lifecycle approval changes are included.
Existing incompatible Agent rows would cause migration failure and rollback rather
than silent conversion. Initial provenance stamping affects new rows only.

Tests: non-AI rejection, valid Agent insertion, Actor-type change rejection,
initial provenance spoof rejection, relationship insertion/deletion history,
and TRUNCATE rejection. Fixture changes roll back in an explicit subtransaction.

Limits: ownership can disable triggers; these are not owner-proof audit controls.
End-user attribution, least-privilege role/RLS qualification, lifecycle transitions,
and complete governance/domain relationships remain open. Runtime authority is
still determined by the locked controls, not the membership tables.

Recovery: failed migration rolls back; successful changes use fix-forward recovery.
Do not remove history or disable triggers to replay tests. No destructive downgrade
is supplied. Exact-commit review/approval remains required before merge.
