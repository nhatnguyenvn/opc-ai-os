# OPC AI Operating System

Canonical implementation repository foundation for OPC AI OS v1.0: governance, runtime packages, six Agent packages, configuration, schemas, workflows, tests and releases.

**Owner:** Founder. **Version:** 1.0.0-dev. **State:** LOCAL FOUNDATION; NOT RELEASED. Private remote and main protection are pending.

## Validate

Python 3.11+ and Git; no Python third-party dependencies.

```text
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/release_manifest.py --output release/manifests/local-build.json
```

Manifest generation requires a clean committed checkout. The generated manifest remains BUILD_ONLY_NOT_DEPLOYABLE; no approval is fabricated.

## Layout

constitution, runtime, agents, permissions, policies, schemas, decision-tables, workflows, connectors, knowledge, tests, migrations, fixtures, observability, config, release, scripts, docs.

Machine-readable YAML artifacts use the JSON subset (see docs/CONFIGURATION.md). Package versions are exact pins. Domain packages and all external execution remain disabled. Constitution/runtime rules are preserved from the approved reference; control enforcement and full domain transcription are later work.

See docs/reference/phase-a.md for the approved plan, docs/PROVENANCE.md for authority evidence, docs/REPOSITORY_ADMIN.md for remote setup, and release/reports/phase-a-acceptance.md for verified results and blockers.
