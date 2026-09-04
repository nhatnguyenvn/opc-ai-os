# Changelog

## [1.0.0-dev] — Unreleased

### Added
- Phase A repository foundation, six disabled Agent skeletons, environment references, config contracts, local validation, negative tests and CI.
### Changed
- Document A2 semantic version meanings and development-to-release progression in docs/VERSIONING.md.
### Fixed
- Disable automatic Git maintenance in disposable test repositories to prevent a background writer racing fixture cleanup on CI; exclude temporary clones from fixture copies.
### Deprecated
- None.
### Removed
- None.
### Security
- Secrets excluded; execution disabled. Native branch protection skipped by explicit user instruction because the repository is private on GitHub Free; direct mutation risk remains.
### Governance
- Record the scoped A1.3 platform exception and continuation authority in docs/PHASE-A-HANDOFF.md; no protection PASS, merge approval or deployment approval is inferred.
- Preserved 14 constitutional controls, shared runtime sections, 30 hard controls and approved source references. Materialization is not runtime enforcement or production release.
