# A1.3 — Compensating controls for GitHub Free private

Document: OPC-A1-3-ALT-001, version 1.0-draft
Change request: CR-FOUNDATION-003
Status: implementation authorized by Founder continuation; TESTING; amended gate not yet effective.
Owner and final approver: Founder.

## Purpose and boundary

Keep nhatnguyenvn/opc-ai-os private on GitHub Free. Replace the requirement for native branch protection with a measured combination of local prevention, a controlled merge procedure, CI evidence and recovery readiness. This is a scoped amendment to Phase A, not equivalent server-side enforcement. The original approved specification in docs/reference/phase-a.md remains unchanged.

No Constitution rule, P0 severity, Production approval, secrets restriction or runtime permission changes. System version remains 1.0.0-dev. This procedure does not authorize deploying or enabling Agents.

## Proposed replacement for A1.3

Protect main against accidental changes through verified compensating controls. Every normal update must use a feature/fix branch and a PR; validation must pass on the exact candidate and current base; the Founder must approve the candidate, base and intended merge. Local safeguards must reject direct pushes and deletion of main. Changes to these safeguards use the same review process. Native protection remains unavailable and bypass risk must be explicitly accepted.

## Controls and required evidence

| ID | Control to implement | Acceptance evidence |
|---|---|---|
| ALT-01 | Versioned pre-push hook and explicit installer for each authorized local checkout. Reject every ref update/deletion targeting refs/heads/main, including force updates. Verify installed core.hooksPath and hook contents. | Local bare-remote fixture proves rejected operations leave main unchanged; approved feature push succeeds. Record installation on the execution checkout. |
| ALT-02 | Read-only pre-merge verifier for the fixed repository and PR. Resolve current head and base SHAs; require open non-draft PR, expected base main, no conflicts, successful Foundation check from GitHub Actions on current PR merge candidate, and zero unresolved review threads. Unknown, stale, cancelled, skipped, missing or failed evidence means HOLD. | Saved verdict ties repository, PR, head SHA, base SHA, check run IDs and review-thread result. Fail-closed fixtures cover unavailable API/auth and all negative states. No credentials in evidence. |
| ALT-03 | Founder approval record bound to PR, head SHA, base SHA, scope, A1.3 exception and merge method. Agent may retain the user's actual approval; it must not manufacture one. Any changed head/base or material scope requires refreshed verification and approval. | Approval record and exact-candidate comparison immediately before merge. Self-approval through a fabricated GitHub review is not used. |
| ALT-04 | Merge through the approved PR only. Run verifier immediately before submission; use expected-head constraint where the merge interface supports it. Limit main writers to the declared workflow during the short verification/merge window. Re-read resulting commit and parents. | Merge result contains the approved head and expected base. A mismatch is an incident/HOLD for subsequent work. Local snapshots cannot make verification and merge atomic; this residual race is accepted explicitly. |
| ALT-05 | Preserve read-only contents permission for Foundation CI and retain real validation/tests. Remove or rename the echo-only Gatekeeper so it cannot be presented as enforcement. | Fixture demonstrates validator/test failure; real candidate CI passes. Gatekeeper success is not accepted as evidence for this gate. |
| ALT-06 | Inventory authorized write paths and local checkouts without storing secrets. Founder attests to the inventory; document that browser edits, API writes, another clone and --no-verify bypass local hooks. Review every known main update during an active execution session. | Inventory plus successful trace from latest main update to approved PR/candidate. This is session-based review, not continuous monitoring. Unexplained updates trigger HOLD and investigation. |
| ALT-07 | Retain a clean Git bundle of the approved baseline, source-bound manifest and review evidence in a Founder-controlled location. Verify recovery in a separate disposable repository. | Bundle verification and restored commit/hash equality. Do not test recovery by rewriting live main. Later recovery uses an approved corrective/revert PR. |

ALT-01 is local accident prevention. ALT-02 through ALT-06 are procedural checks and detection. None prevents the account owner or a valid write credential from bypassing the process. CI failure after a direct push does not undo that push. No auto-revert, automatic force push or repository exposure is proposed.

## Proposed Phase A exit-gate amendment

Replace only the original item "Branch protection configured" with:

> Native branch protection is configured and verified, OR the Founder-approved OPC-A1-3-ALT-001 alternative is effective, ALT-01 through ALT-07 have passed, all required evidence identifies the evaluated baseline, and residual bypass risk has been explicitly accepted.

All other Phase A exit criteria remain unchanged. No missing or failing mandatory alternative test may be treated as PASS. While this proposal is unapproved or any required control is incomplete, the alternative gate is NOT PASS.

After approval and verification, report: "Phase A PASS — amended baseline CR-FOUNDATION-003; A1.3 satisfied by verified compensating controls; native protection absent." Never report PASS against the unchanged original native-protection item.

## Verification plan

- ALT-T01: direct main push rejected and remote SHA unchanged.
- ALT-T02: force update and deletion of main rejected; feature update allowed.
- ALT-T03: missing hook installation or wrong hook content detected.
- ALT-T04: failing, pending, skipped, cancelled, missing or wrong-source CI yields HOLD.
- ALT-T05: changed candidate/base, absent approval, unresolved review thread or API uncertainty yields HOLD.
- ALT-T06: one approved candidate produces a complete read-only preflight result; no side effect from the verifier.
- ALT-T07: secret scanning still rejects a synthetic token in additional workflow YAML; full foundation suite passes.
- ALT-T08: baseline bundle restores to the recorded commit and content hashes in an isolated repository.
- ALT-T09: post-merge audit detects an unapproved parent/candidate in a fixture and yields HOLD.

Tests use disposable repositories and synthetic API responses for negative cases. Live read-only evidence is also required for the real PR; fixtures alone cannot qualify the real merge workflow. No unsafe write to main is needed to test rejection logic.

## Execution and approval sequence

1. Founder reviews and approves this exact proposal and residual risk. This approval authorizes implementing the alternative, not declaring it passed.
2. Implement hooks, installer, read-only verifier and focused tests on a feature branch. Replace misleading Gatekeeper naming/behavior within the same reviewed change.
3. Run tests, demonstrate live read-only preflight, record writer inventory, verify recovery and collect all seven control results.
4. Founder reviews evidence and approves the exact implementation candidate. The existing explicit exception permits this bootstrap PR; record that bootstrap qualification separately rather than assuming the new gate already applies.
5. Merge approved implementation, verify resulting baseline and installed safeguards, then make the amended gate effective and evaluate Phase A.

## Residual risk and rollback

Owner/browser/API access, credential compromise, uninstrumented clones and deliberate hook bypass remain outside local prevention. Approval records rely on Founder identity and retained conversation evidence, not cryptographic signing. CI and metadata checks may race a base update; verify parents after merge and stop on mismatch. Inventory/review is not a background monitoring service.

If these controls are bypassed or fail, stop normal main changes, preserve evidence and seek Founder recovery approval. Revert this amendment through a reviewed Change Request or migrate to verified native protection if later supported. Removing the alternative does not automatically restore Phase A PASS; revert status to NOT COMPLETE or an explicit exception pending qualification.
