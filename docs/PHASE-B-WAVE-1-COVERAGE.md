# Wave 1 coverage review

Status: INCOMPLETE. Review of source requirements against migrations 0001–0009,
not a declaration of object/task acceptance. All implementation is on test and
PR #2; no runtime deployment or merge approval is implied.

| Task / object | Present | Remaining work before full qualification |
| --- | --- | --- |
| B1.1 Business | Identity, founder membership, market refs, snapshots | Strategic-status governance; Product/Offer relationships in later waves |
| B1.2 LegalEntity | Business FK, legal fields, bank refs | License/obligation links and complete source traceability |
| B1.3 Venture | Owner scope, capital constraints, criteria, scoped Assumption/Risk links and history | Stage lifecycle |
| B1.4 Actor | Identity/type, membership, database provenance | End-user identity attribution; controlled authority references |
| B1.5 Agent | AI actor FK, business scopes, package refs | Tool/permission registry validation; lifecycle |
| B1.6 Delegation | Approval FK and exact-version/time/scope view | Authority proof, conditions evaluation and service lifecycle |
| B1.7 Decision | Typed fields, options and Evidence/Assumption/Risk joins | Complete requiredness and decision transition rules |
| B1.8 Approval | Scope/version/hash binding, issued-binding immutability | Actual object targets beyond Delegation; signing/authority provenance |
| B1.9 Evidence | Source refs, freshness, verification vocabulary | Related objects beyond existing joins; freshness policy enforcement |
| B1.10 Assumption | Exact canonical status vocabulary, evidence links/history | Allowed transitions and review service behavior |
| B1.11 Risk | Probability/score bounds and fields | Control links and controlled risk lifecycle |
| B1.12 ChangeRequest | Approval/reviewer refs, tests/risk links and statuses | Exact target approval integrity; deployment/verification semantics |
| Exception | Owner, decision/evidence links, SLA and expiry fields | Expiry/state semantics and remaining related objects |
| B1.13 Workflow | Identity/version, definition header, steps/dependencies, requirement items, immutable seal | Registry validation of external references; normalized-content digest binding; lifecycle and concurrent-writer qualification |
| B1.14 WorkflowRun | Exact sealed version pin, scope/risk/approval | Trigger linkage semantics and state transitions |
| B1.15 Task | Run/owner/approval/evidence links, dependencies | Lifecycle and full source coverage |
| B1.16 Action | Actor/task binding, idempotency, retry bounds | Real permission/policy/approval decisions and side-effect verification |
| B1.17 Event | Business/source idempotency, immutable event identity, Run joins | Event taxonomy, processing lifecycle |
| Handoff | Run and actor links, acceptance fields | Acceptance and rejection semantics |

## Controls checked in this increment

Task dependency insertion accepted a three-node cycle before migration 0008.
The same saved SQL test rejects it after migration and verifies insert/delete
history. Dependency mutations take a business-row lock and require READ COMMITTED;
other isolation levels fail closed. Concurrent-writer stress is still untested.
Audit/anti-TRUNCATE triggers now also cover Task dependencies, Event/Run links,
Decision options and ChangeRequest test references.

## Cross-cutting gates still open

- Real non-owner application/read/audit/reporting roles and cross-business RLS.
- Physical schema drift validation against a clean migration result.
- Full source-to-column/relationship registry, including later-wave dependencies.
- Controlled lifecycle transitions and end-user attribution.
- Backup/restore rehearsal, all remaining DB acceptance tests and release evidence.

Do not mark Wave 1 PASS because every primary table exists. Retain the rows above
until their semantic and regression criteria are independently satisfied.
Migration 0009 adds normalized definition content and Venture governance links.
Sealing rejects missing headers/steps and dependency cycles, and prevents later
inserts into the definition. Runs require a sealed business/version. The seal
does not grant runtime authority. External requirement references and artifact
hash equality to normalized content remain unverified; see CR-PHASE-B-008.

Next bounded increment: isolate application roles and qualify their actual
privileges and cross-business access, keeping the remaining gates above open.
