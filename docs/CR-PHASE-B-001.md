# CR-PHASE-B-001 — Non-production migration foundation

State: TESTING. Implementation of approved Phase B; not a policy amendment.

Problem: namespace bootstrap could not represent later migration versions and
there was no PostgreSQL CI qualification. Add an ordered transaction planner,
extend history through a new migration, and exercise it on disposable PostgreSQL.

Scope: migrations 0001 and 0002, planners, offline tests, PostgreSQL CI. The existing
bootstrap is preserved byte-for-byte. audit.migration_history copies its historical
row and accepts later versions; audit.schema_migration remains intact.

Governance: no change to authority, P0 controls, runtime execution flags, production
configuration or Founder approval requirements. Review and exact-commit approval
remain required before merging. No production deployment is included.

Validation: offline history/order/checksum tests; PostgreSQL clean bootstrap,
previous-to-latest upgrade, fault rollback, repeat no-op, changed-checksum rejection,
and database-side predecessor guard. Full physical drift and domain DB gates are
outside this change and remain open. CI credentials are ephemeral local-service
values derived from the workflow run ID; no cloud credentials are needed.

Recovery: a failed migration rolls back its own transaction. After successful
0002, leave history intact and fix forward; do not remove ledger rows to permit
replay. No automatic downgrade or destructive reset is supplied. In an approved
disposable environment, recreation is an explicit separate operation.

Operational limitation: this is a trusted migration-code runner, not a sandbox for
arbitrary SQL. Each JSON entry must be one statement, with no transaction control;
review migration payloads before execution. A CLI invocation emits a plan only.
