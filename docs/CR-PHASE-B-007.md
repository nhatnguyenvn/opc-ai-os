# CR-PHASE-B-007 — Dependency graph and relationship audit

State: TESTING. Migration 0008. No previously applied migration is edited.

Fix: Task dependencies accepted directed cycles. New trigger checks reachability
before INSERT/UPDATE, serializes participating writers on the Business row, and
requires READ COMMITTED. Cycles fail with TASK_DEPENDENCY_CYCLE. Existing unrelated
businesses remain independent. Self links retain the earlier CHECK constraint.

Add history and TRUNCATE rejection to Task dependencies, Event/Run joins, Decision
options and ChangeRequest test references. The shared relationship log preserves
old/new values and database actor. It does not replace end-user audit attribution.

Validation: red three-node cycle accepted; green saved SQL test rejects the cycle
and verifies dependency history. Concurrent stress remains pending. No runtime
permissions or production changes. Detailed remaining source/control gaps are in
PHASE-B-WAVE-1-COVERAGE.md; Wave 1/Phase B remain incomplete.

Recovery: transaction rollback on failure; fix forward after success. Do not delete
history, disable triggers or rewrite applied migrations. Review and exact-commit
merge approval remain required.
