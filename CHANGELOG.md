# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Project scaffold: `src/` layout, packaging, ruff, mypy and pytest configuration.
- CI workflow (lint, type check, tests) and pull request template.
- Apache-2.0 license and NOTICE.
- Project conventions in `CLAUDE.md`.
- Architecture, glossary, draft model format and sources skeleton in `docs/`.
- ADR-0001: common-mode failure is modeled with node tags and scenario selectors.
- `CLAUDE.md`: checklist items are ticked only after verification, and checks run locally before push.
- Model schema (nodes with tags, four edge types, capabilities, break-glass paths, redundancy groups) and exported JSON Schema.
- YAML loader with semantic lint and readable errors that name the model, item and field.
- Vendor-neutral reference model (`models/reference-dc`) with 46 nodes and its description in `docs/reference-model.md`.
- Typed dependency graph with dependency queries and explanatory chains (`lockout.graph`).
- Analyzers: bootstrap cycles and start order, lockout simulation, break-glass validity (`lockout.analyzers`).
- Scenario format with name list and tag selector (ADR-0001), example scenarios in `scenarios/`.
- CLI commands `lockout analyze` and `lockout simulate`.

### Changed
- Reference model: removed the on-site engineer's dependency on access control, added the `administer-fleet` capability.
