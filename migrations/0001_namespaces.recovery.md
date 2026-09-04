# Recovery for 0001_namespaces

If any CREATE SCHEMA fails, the transaction must be rolled back by the migration executor. Do not continue on an aborted transaction.

After successful application, inspect ownership and contents before any removal. In a disposable qualification database only, empty schemas may be dropped with RESTRICT under the migration role. Never use CASCADE to undo this migration. If later migrations created objects, recover those migrations in reverse dependency order or restore a verified backup under an approved recovery plan. No automatic Production rollback is supplied.

The planner also creates audit.schema_migration inside the same transaction. After successful application audit is not empty. Do not attempt a schema-only rollback or remove its ledger independently. A recovery procedure must account for both migration objects and history; no automated reverse migration is supplied.
