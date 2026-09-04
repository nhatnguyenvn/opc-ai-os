# CR-PHASE-B-006 — Workflow core persistence

State: TESTING. Sources: Phase B sections 26–31 and Module 4 objects 10–13.
Migration 0007 adds Workflow, immutable WorkflowVersion, WorkflowRun, Task, Action,
Event, Handoff and typed Event/Run and Task-dependency relationships.

Each Run references one immutable version through a business-scoped FK. The version
stores an external definition reference and SHA256; it does not embed or activate
an executor. Run version and Task parent cannot be rebound. Action identity fields
and Event source/payload identity cannot be rewritten after insertion.

Action idempotency is unique per Business; Event idempotency is unique per
Business/source. Nonempty keys and nonnegative retry counts are required. This is
record deduplication, not a guarantee of exactly-once external side effects.
Permission/policy defaults are NOT_EVALUATED. No worker, role grants or runtime
activation is supplied, and ALLOW values are not trusted authorization proofs.

Implementation state vocabulary DRAFT/PENDING/RUNNING/SUCCEEDED/FAILED/CANCELLED/
ARCHIVED is for review. Valid state transitions, status-specific invariants and
control-engine decisions remain to be implemented. End-user attribution and RLS
remain open. The immutable package reference is the home of versioned definition
content for now; normalized steps, policies, approvals, tools, SLA, retry/rollback
rules, completion criteria and KPI traceability still require reconciliation.
Task dependency cycles, Handoff acceptance rules and history for join rows are
also not yet qualified. This increment does not close all B1.13–B1.17 gates.

Tests: immutable workflow version; Run version cannot change; duplicate Action and
Event keys rejected; negative retries rejected. Fixtures and snapshots roll back.
Reference/risk/approval/actor links are typed and scoped; external capabilities and
version-package hashes still require runtime verification.

Recovery: failure rolls back migration; after application retain history and fix
forward. No automatic destructive downgrade. Prior migrations unchanged. Exact
commit review/merge approval remains required; no Production action included.
