# Changelog

All notable changes to `envlens` will be documented in this file.

## 0.3.0 - Unreleased

- Added a static web workbench under `web/`.
- Added browser-side env, schema, source scanning, issue filtering, variable review, explain view, docs generation, and export views.
- Added fix-plan, generated-schema, CLI/CI snippet, share-link, ignored-key, download, and theme features to the web workbench.
- Added GitHub Pages deployment workflow.
- Added web demo documentation and static asset tests.

## 0.2.0 - 2026-06-02

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
