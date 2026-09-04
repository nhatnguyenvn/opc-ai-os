# Change control

Material changes: feature/<scope> or fix/<scope> → Change Request → analysis → tests → review → approval → merge → deploy → verify.

States: DRAFT, ANALYSIS, TESTING, REVIEW, APPROVAL, APPROVED, DEPLOYED, VERIFIED, REJECTED, ROLLED_BACK.

No direct Production configuration edits. Founder task instructions do not silently amend effective policy. Material changes invalidate approval. P0 failures block merge/release. Runtime/go-live approval is separate from specification approval.

Each P0 change identifies affected controls and regression tests. Breaking schema changes require a migration and rollback/recovery plan. Retain exact commit, approval and verification evidence.
