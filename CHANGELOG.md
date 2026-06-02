# Changelog

All notable changes to `envlens` will be documented in this file.

## 0.2.0 - Unreleased

- Added GitHub Action metadata with `action.yml`.
- Added SARIF output for code-scanning workflows.
- Added GitHub step summary support.
- Added `envlens doctor`.
- Added `envlens explain KEY`.
- Added `envlens list-presets`.
- Added framework presets for Next.js, Vite, Django, FastAPI, and Docker Compose.
- Added `[tool.envlens]` config loading from `pyproject.toml`.
- Fixed Windows UTF-8 BOM parsing for env files.
- Fixed relative env path resolution for nested project checks.
- Improved Python and Ruby scanner expression capture.
- Expanded tests and documentation.

## 0.1.0 - 2026-06-02

- Initial public release.
- Added env file parsing.
- Added source scanning for JavaScript, TypeScript, Python, Go, Ruby, and PHP patterns.
- Added schema loading and validation.
- Added text, JSON, and GitHub annotation output.
- Added docs generation and schema inference.

