Chuyển sang **Build & Deploy Plan v1.0**. Giai đoạn này không còn là thiết kế governance nữa mà là biến kiến trúc đã khóa thành **backlog kỹ thuật có dependency, acceptance criteria và test gate rõ ràng**.

Bắt đầu với **Phase A — Repository & Configuration Foundation**.

:::writing{variant="document" id="48137"}
# OPC AI OPERATING SYSTEM v1.0
## BUILD & DEPLOY PLAN
### PHASE A — REPOSITORY & CONFIGURATION FOUNDATION

**Document ID:** OPC-BUILD-001  
**Version:** 1.0  
**Status:** Draft for Founder Approval  
**Phase Objective:** Establish the controlled technical foundation required for all subsequent OPC AI OS implementation work.

---

# 1. PHASE OBJECTIVE

Phase A creates the repository, versioning, configuration hierarchy, release structure, environment conventions, and change-control foundation for OPC AI OS.

No database schema, Agent runtime, workflow, or connector SHOULD be treated as production implementation until this foundation exists.

Primary output:

> **A reproducible, version-controlled OPC AI OS source repository with clear configuration ownership and release discipline.**

---

# 2. PHASE SUCCESS CRITERIA

Phase A is complete only when:

1. A canonical source repository exists.
2. Main/production branches are protected.
3. OPC AI OS package structure is created.
4. Approved v1.0 specifications are represented as versioned configuration artifacts.
5. Environment configuration is separated.
6. Secrets are excluded from repository content.
7. Release manifests can be generated.
8. Change-control workflow is defined.
9. Basic validation can detect missing/invalid package configuration.
10. Phase A regression checks pass.

---

# 3. IMPLEMENTATION PRINCIPLE

Repository structure SHOULD separate:

- stable governance;
- runtime configuration;
- business-specific configuration;
- secrets;
- generated artifacts;
- test fixtures.

Core principle:

`Specification → Machine-Readable Configuration → Test → Release`

Do NOT make free-form prompt files the only source of implementation truth.

---

# 4. TARGET REPOSITORY STRUCTURE

Recommended structure:

```text
opc-ai-os/
│
├── README.md
├── CHANGELOG.md
├── VERSION
│
├── constitution/
│   └── v1.0/
│
├── runtime/
│   ├── shared/
│   └── hard-controls/
│
├── agents/
│   ├── chief-of-staff/
│   ├── product/
│   ├── sales/
│   ├── finance/
│   ├── operations/
│   └── strategy/
│
├── permissions/
│
├── policies/
│   ├── enterprise/
│   └── domain/
│
├── schemas/
│
├── decision-tables/
│
├── workflows/
│
├── connectors/
│
├── knowledge/
│   └── manifests/
│
├── tests/
│   ├── golden/
│   ├── agents/
│   ├── permissions/
│   ├── connectors/
│   ├── schemas/
│   ├── decisions/
│   ├── workflows/
│   └── e2e/
│
├── migrations/
│
├── fixtures/
│
├── observability/
│
├── release/
│   ├── manifests/
│   └── reports/
│
├── scripts/
│
└── docs/
```

---

# 5. WORKSTREAM A1 — REPOSITORY INITIALIZATION

## Task A1.1 — Create Canonical Repository

Create private canonical repository:

`opc-ai-os`

The repository SHOULD become the controlled implementation source for:

- runtime packages;
- Agent packages;
- schemas;
- permissions;
- policies;
- workflows;
- tests;
- release configuration.

### Acceptance Criteria

- Repository exists.
- Repository is private.
- Repository ownership is clearly defined.
- Default branch exists.
- README identifies repository purpose.
- Repository contains no production secrets.

### Dependency

None.

### Gate

`A1-GATE-01`

Repository can be cloned and validated from a clean environment.

---

# 6. TASK A1.2 — BRANCH STRATEGY

Recommended branches:

### `main`

Approved production-ready source.

### `develop`

Optional integration branch if implementation complexity justifies it.

### Feature branches

Format:

`feature/<scope>`

### Fix branches

`fix/<scope>`

### Release branches

Optional:

`release/v1.0.0`

Do NOT create unnecessary Git-flow complexity for a one-person company unless deployment needs justify it.

Preferred simple model:

`feature branch → PR → main`

---

# 7. TASK A1.3 — BRANCH PROTECTION

Protect `main`.

Require where platform supports:

- pull request before merge;
- status checks;
- no force push;
- no direct destructive history rewrite;
- resolved review comments;
- successful required tests.

Founder MAY remain final administrative authority.

### Acceptance Criteria

Direct accidental mutation of Production source is materially reduced.

---

# 8. WORKSTREAM A2 — VERSIONING FOUNDATION

## Task A2.1 — Establish Semantic Versioning

Use:

`MAJOR.MINOR.PATCH`

Examples:

- `1.0.0`
- `1.0.1`
- `1.1.0`
- `2.0.0`

### Meaning

**MAJOR**
breaking runtime/governance change.

**MINOR**
compatible feature/capability expansion.

**PATCH**
fix, clarification, non-breaking correction.

---

# 9. TASK A2.2 — VERSION FILE

Create root:

`VERSION`

Initial target:

`1.0.0-dev`

Progression:

`1.0.0-dev`
→ `1.0.0-rc1`
→ `1.0.0`

Release version MUST NOT be inferred from repository date alone.

---

# 10. TASK A2.3 — CHANGELOG

Create:

`CHANGELOG.md`

Minimum sections:

- Added
- Changed
- Fixed
- Deprecated
- Removed
- Security
- Governance

Governance changes SHOULD be especially explicit.

---

# 11. WORKSTREAM A3 — GOVERNANCE PACKAGE MATERIALIZATION

## Task A3.1 — Constitution Package

Create:

`constitution/v1.0/constitution.yaml`

Recommended structure:

```text
id
version
status
effective_date
controls[]
```

Each control includes:

```text
control_id
title
severity
rule
```

Avoid storing only one large prose prompt.

---

# 12. TASK A3.2 — Shared Runtime Package

Create machine-readable/runtime-readable representation of:

`Shared Agent Runtime Contract v1.0`

Recommended separation:

- authority
- evidence
- confidence
- execution
- communication
- data
- change
- audit
- failure
- output

Large explanatory text MAY remain in documentation, while enforceable rules SHOULD exist structurally.

---

# 13. TASK A3.3 — Hard-Control Registry

Create:

`runtime/hard-controls/v1.0/controls.yaml`

Each entry SHOULD contain:

- Control ID
- Name
- Severity
- Trigger
- Required Behavior
- Prohibited Behavior
- Enforcement Type
- Decision Table
- Tests

Example:

```text
HC-FIN-001
Financial Commitment Approval
P0
```

---

# 14. WORKSTREAM A4 — AGENT PACKAGE STRUCTURE

For each Executive Agent create:

```text
agents/<agent>/
├── manifest.yaml
├── identity.md
├── domain-controls.yaml
├── boundaries.yaml
├── outputs.yaml
└── tests.yaml
```

Do NOT initially copy all Shared Runtime rules into each Agent folder.

---

# 15. TASK A4.1 — AGENT MANIFEST

Each Agent Manifest SHOULD include:

- Agent ID
- Name
- Version
- Runtime dependency
- Domain
- Permission profile ID
- Domain control registry
- Supported workflow classes
- Output contract
- Status

Example dependency:

`requires_runtime: >=1.0.0,<2.0.0`

---

# 16. TASK A4.2 — INITIAL AGENT PACKAGES

Create packages for:

- AI Chief of Staff
- Product & Offer
- Sales & Growth
- Finance & Control
- Operations & Workflow
- Strategy & Compliance

Initial status:

`CONFIGURED_NOT_DEPLOYED`

until later technical gates pass.

---

# 17. WORKSTREAM A5 — ENVIRONMENT MODEL

Define at minimum:

- LOCAL / DEVELOPMENT
- TEST
- STAGING
- PRODUCTION

Optional:

- SANDBOX

Each environment SHOULD have independent:

- database references;
- credentials;
- connector configuration;
- execution limits;
- release state.

---

# 18. TASK A5.1 — ENVIRONMENT CONFIGURATION

Recommended structure:

```text
config/
├── development/
├── test/
├── staging/
└── production/
```

But confidential values MUST NOT be stored directly.

Use configuration references.

---

# 19. TASK A5.2 — ENVIRONMENT SAFETY

Production MUST differ visibly from test environments.

Examples:

- explicit environment variable;
- database-name distinction;
- production action guard;
- connector endpoint separation.

Runtime MUST NOT accidentally treat Test as Production or vice versa.

---

# 20. WORKSTREAM A6 — SECRET MANAGEMENT FOUNDATION

## Task A6.1 — Secret Exclusion

Repository MUST exclude:

- `.env`
- API keys
- passwords
- OAuth secrets
- private certificates
- service-account credentials
- database passwords

Provide:

`.env.example`

with names only.

---

# 21. TASK A6.2 — GITIGNORE

Minimum exclusions:

```text
.env
.env.*
*.pem
*.key
secrets/
credentials/
local-data/
tmp/
```

Actual implementation SHOULD be adapted to technologies selected later.

---

# 22. TASK A6.3 — SECRET REFERENCES

Configuration SHOULD reference secrets logically.

Example:

```text
database_credential_ref:
  OPC_PROD_DATABASE
```

not actual password.

---

# 23. WORKSTREAM A7 — CONFIGURATION SCHEMA

Configuration files themselves SHOULD be validated.

Define schemas for:

- Agent Manifest
- Permission Profile
- Policy
- Hard Control
- Decision Table
- Workflow
- Connector
- Release Manifest

---

# 24. TASK A7.1 — CONFIG VALIDATOR

Create validation mechanism capable of detecting:

- missing required fields;
- invalid enums;
- duplicate IDs;
- invalid references;
- wrong versions;
- malformed configurations.

Initial implementation MAY be simple.

The key requirement is deterministic validation.

---

# 25. WORKSTREAM A8 — ID & NAMING CONVENTIONS

Use stable IDs.

Recommended prefixes:

```text
AGENT-
HC-
PC-
SC-
FC-
OC-
SCG-
POL-
PERM-
DT-
WF-
OBJ-
TEST-
REL-
CR-
```

Do NOT use display name as primary identifier.

---

# 26. NAMING RULE

IDs SHOULD be:

- unique;
- immutable;
- machine-safe;
- human-readable where practical.

Changing title/name SHOULD NOT require changing ID.

---

# 27. WORKSTREAM A9 — RELEASE MANIFEST FOUNDATION

Create template:

`release/manifest.schema.yaml`

Release Manifest SHOULD include:

- Release ID
- System Version
- Constitution
- Runtime
- Hard Controls
- Agent Versions
- Permission Profiles
- Policies
- Schema Version
- Decision Tables
- Workflow Versions
- Connector Configurations
- Regression Version
- Deployment Environment
- Approval Reference
- Build Hash / Commit

---

# 28. TASK A9.1 — BUILD IDENTIFIER

Every candidate SHOULD reference exact source commit.

Example:

```text
release:
OPC-AIOS-v1.0.0-rc1

commit:
<git commit SHA>
```

This enables reproducibility.

---

# 29. WORKSTREAM A10 — CHANGE CONTROL FOUNDATION

Create Change Request template:

```text
Change ID
Requested By
Component
Current Version
Proposed Change
Reason
Risk
Affected Controls
Affected Tests
Rollback
Approval
Status
```

---

# 30. CHANGE STATES

Recommended:

- DRAFT
- ANALYSIS
- TESTING
- REVIEW
- APPROVAL
- APPROVED
- DEPLOYED
- VERIFIED
- REJECTED
- ROLLED_BACK

---

# 31. WORKSTREAM A11 — CONTRIBUTION / IMPLEMENTATION RULES

Create:

`CONTRIBUTING.md`

Minimum implementation rules:

1. Never commit secrets.
2. Never modify Production configuration directly.
3. Every material change uses a branch.
4. Every P0-impacting change identifies affected tests.
5. Machine-readable artifacts must validate.
6. Breaking schema changes require migration.
7. Release version and manifest must match.

---

# 32. WORKSTREAM A12 — CODEOWNERS / REVIEW OWNERSHIP

Where supported, define ownership.

Conceptually:

- Runtime → Chief of Staff / Founder
- Product package → Product domain
- Finance package → Finance domain
- Workflow → Operations
- Policy → Strategy
- Permissions → Founder/governance owner

In a one-person company, Founder may be technical reviewer, but domain ownership SHOULD still remain explicit for Agent reasoning and future team growth.

---

# 33. WORKSTREAM A13 — BASE CI VALIDATION

Initial CI SHOULD NOT attempt the whole AI OS.

Phase A CI only needs to verify repository integrity.

Recommended checks:

1. YAML/JSON syntax
2. Required files exist
3. Duplicate IDs
4. Broken references
5. Secret scanning
6. Version consistency
7. Configuration schema validation

---

# 34. CI FAILURE POLICY

Any failure in:

- secret scan;
- invalid P0 control registry;
- invalid Agent manifest;
- version inconsistency;

SHOULD block merge.

---

# 35. PHASE A TEST SUITE

## A-TEST-001 — Missing Constitution

Delete/omit Constitution package.

Expected:

`FAIL`

---

## A-TEST-002 — Duplicate Control ID

Two hard controls share same ID.

Expected:

`FAIL`

---

## A-TEST-003 — Invalid Agent Runtime Dependency

Agent requires nonexistent runtime version.

Expected:

`FAIL`

---

## A-TEST-004 — Secret Committed

Fixture includes API token pattern.

Expected:

`FAIL`

---

## A-TEST-005 — Broken Permission Reference

Agent manifest references nonexistent permission profile.

Expected:

`FAIL`

---

## A-TEST-006 — Invalid Environment

Production config declares environment=test.

Expected:

`FAIL`

---

## A-TEST-007 — Release Manifest Version Mismatch

Manifest says Agent v1.0, repository package is v1.1.

Expected:

`FAIL`

---

## A-TEST-008 — Missing Required Package

Finance Agent package absent from v1.0 release configuration.

Expected:

`FAIL`

---

# 36. PHASE A DELIVERABLES

At completion, expected artifacts:

### Repository

`opc-ai-os`

### Governance

- Constitution package
- Shared Runtime package
- Hard-Control Registry

### Agent Structure

6 Agent manifests/packages.

### Configuration

- environment model
- base config schema
- naming rules

### Governance Operations

- Change Request template
- CONTRIBUTING
- Release Manifest schema

### Validation

- base configuration validator
- Phase A tests
- CI configuration

---

# 37. DEPENDENCY GRAPH

```text
A1 Repository
   ↓
A2 Versioning
   ↓
A3 Governance Packages
   ↓
A4 Agent Package Skeletons
   ↓
A5 Environment Model
   ↓
A6 Secret Foundation
   ↓
A7 Config Schemas
   ↓
A8 ID Conventions
   ↓
A9 Release Manifest
   ↓
A10 Change Control
   ↓
A13 CI Validation
   ↓
PHASE A GATE
```

Some tasks MAY run in parallel after A1.

---

# 38. PHASE A EXIT GATE

Phase A is `PASS` only if:

- [ ] Canonical repository exists
- [ ] Branch protection configured
- [ ] Versioning established
- [ ] Constitution materialized
- [ ] Shared Runtime materialized
- [ ] Hard-Control Registry materialized
- [ ] Six Agent package skeletons exist
- [ ] Environment model exists
- [ ] Secrets excluded
- [ ] Config validation exists
- [ ] Release Manifest template exists
- [ ] Change Control template exists
- [ ] Base CI succeeds
- [ ] Phase A tests pass

Any missing mandatory item:

`PHASE A NOT COMPLETE`

---

# 39. PHASE A → PHASE B HANDOFF

Phase B may begin after repository/configuration contracts are stable enough to support migrations.

Required handoff:

- Repository Commit
- Release Baseline
- Schema Configuration Convention
- ID Convention
- Environment Convention
- Change Control Procedure

---

# 40. NEXT PHASE

After Phase A approval and technical completion:

> **PHASE B — DATABASE & CANONICAL SCHEMA BUILD**

Phase B will convert the approved Canonical Object Schemas into:

- PostgreSQL schemas;
- tables;
- enums;
- relationships;
- constraints;
- indexes;
- audit fields;
- soft-delete/versioning rules;
- migrations;
- seed/reference data;
- database regression tests.

---

# END — PHASE A
## Repository & Configuration Foundation
:::

Nếu phê duyệt **Phase A**, mình sẽ tiếp tục sang **Phase B — Database & Canonical Schema Build**, trong đó chúng ta sẽ chia canonical model thành các migration waves để không tạo một database khổng lồ ngay từ đầu.
