# CR-PHASE-B-005 — Governance supporting objects

State: TESTING. Additive migration 0006; previous migrations remain immutable.
Sources: OPC-BUILD-002 B1.9–B1.12 and Module 4 sections 18–20, 50, 52.

Adds Evidence, Assumption, Risk, Exception, ChangeRequest; typed join tables for
Decision/Evidence, Decision/Assumption, Decision/Risk, Assumption/Evidence,
Approval/Evidence, Exception/Evidence and ChangeRequest/Risk. Composite business
FKs prevent cross-business joins. ChangeRequest required tests are child references.

Assumption states are exactly UNTESTED, SUPPORTED, WEAKENING, INVALIDATED,
REPLACED, with UNTESTED default. ChangeRequest vocabulary follows CHANGE_CONTROL.md.
Evidence verification labels UNVERIFIED/VERIFIED/DISPUTED are implementation choices
for review; a VERIFIED label alone does not qualify source truth or approve actions.

Evidence stores external document references, not attachments. Confidence and
probability are constrained to 0–1; risk scores nonnegative. Impact remains text
rather than inventing a scoring scale. Owners/reviewers are scoped business members.
Identity snapshots and typed relationship changes retain database-actor history.
No new runtime role, authority policy or production action is enabled.

Open work: actor-attributed audit, lifecycle transition enforcement, Risk-to-Control
links, other domain object relationships, end-to-end approval-version validation
for ChangeRequest, and role/RLS qualification. Reference fields do not validate
external systems. The schema does not treat a stored approval or status as permission
to deploy. The shared status vocabulary for Risk/Exception still needs lifecycle review.

Validation: default/allowed Assumption status and history, cross-business evidence
rejection, probability bounds, orphan approval rejection and Exception insertion.
All fixtures roll back. No business rows are seeded by the migration.

Recovery: atomic rollback on failure, fix forward after successful application;
retain histories and do not edit applied migrations. No destructive downgrade.
Exact-candidate review and merge approval remain required; Phase B is not PASS.
