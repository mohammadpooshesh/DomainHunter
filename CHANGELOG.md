# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-22

### Fixed

- **Critical:** every scanner module built request URLs with doubled-brace
  f-strings (e.g. `f"{{https://{domain}}}"`), producing a literal
  `{https://example.com}` that no HTTP client could fetch. All URLs are now
  assembled with string concatenation or httpx `params=`, so every network
  module actually works.
- GitHub module now sends the authorization header on every request.
- Removed dead code and unused variables flagged by the linter.

### Added

- Packaging via `pyproject.toml` with a `domainhunter` console entry point.
- Full offline test suite (`pytest`) covering utils, config, cache, report,
  scanner, threads and the scanner modules, plus a regression test that guards
  against the URL bug.
- GitHub Actions CI (lint, multi-OS/multi-version tests, type-check, coverage),
  Docker image publishing, CodeQL scanning and an automated release workflow.
- Comprehensive English documentation (`README.md` and `docs/`).
- Contributor tooling: `Makefile`, pre-commit config, Dependabot, issue and PR
  templates, `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE` and `.env.example`.

## [0.1.0] - Initial prototype

- First implementation of the multi-module domain OSINT scanner and CLI.
