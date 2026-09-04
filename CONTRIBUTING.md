# Contributing

1. Never commit secrets; .env.example contains names only.
2. Never modify Production configuration directly.
3. Every material change uses feature/<scope> or fix/<scope> and a PR.
4. Every P0-impacting change identifies affected controls and tests in a Change Request.
5. Run `python scripts/validate.py` and `python -m unittest discover -s tests -v`.
6. Breaking schema changes require a migration and rollback/recovery plan.
7. VERSION and release manifest must match; all components must be pinned.
8. Founder/governance owner reviews authority changes. Do not infer approval from tool access or previous approvals.

See docs/CHANGE_CONTROL.md and docs/REPOSITORY_ADMIN.md. No deployment is included in foundation CI.
