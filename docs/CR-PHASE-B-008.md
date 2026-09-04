# CR-PHASE-B-008 — Workflow definitions and Venture governance links

State: TESTING. Migration 0009; approved source scope: Module 4 Workflow fields
and Venture Assumption/Risk relationships. Existing applied migrations unchanged.

Workflow versions previously carried only an external reference/hash. Add a
normalized definition header, ordered steps, step dependencies, typed requirement
items (INPUT, DECISION_POINT, POLICY, APPROVAL, TOOL, KPI), and an immutable seal.
The header snapshots name, owner, trigger, SLA, expected output, exception/retry/
rollback rules, completion criteria and status. Workflow identity/version remain
on their existing tables. Empty item groups mean no declared requirements.

Assembly: insert a new version, header and children, then insert its seal, preferably
in one transaction. Header and child rows are append-only even before sealing;
correct an error by creating a new version. Sealing requires a header and at least
one step and rejects dependency cycles. After sealing no additional definition
rows can be inserted. Run creation requires the exact business/version seal.
The seal is structural completeness, not Founder approval or permission to execute.

Writers lock the version row and require READ COMMITTED, including sealing.
Other isolation levels fail closed. Concurrent-writer qualification remains open.
All new definition inserts have relationship audit records. Seal timestamps and
database actor are stamped server-side. End-user identity remains a separate gate.

Policy/tool/KPI/approval requirement references are declared references, not
validated registry FKs or issued approvals. definition_hash continues to describe
the external artifact; this increment does not prove its equality to normalized
rows. Content digest verification and runtime semantics remain open coverage gates.
Implementation vocabulary/requiredness is documented here, not retroactively
attributed to the source specification.

Venture–Assumption and Venture–Risk use business-scoped composite foreign keys,
relationship history and TRUNCATE rejection. No destructive cascade is added.

Upgrade precondition: no existing WorkflowRun rows. If runs exist, fail atomically
with WORKFLOW_DEFINITION_BACKFILL_REQUIRED; prepare a reviewed backfill path rather
than inventing definitions for historical runs. The current nonproduction test
target has no business fixtures. No production deployment or runtime activation.

Validation: saved workflow_definition.sql plus adapted earlier workflow fixtures,
full offline suite and PostgreSQL qualification. Failure recovery is transaction
rollback; after successful application use a new migration. Keep draft PR review
and exact-commit Founder approval before merge.
