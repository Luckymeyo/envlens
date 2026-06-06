# Roadmap

## Shipped in 0.5

- Risk Radar view for contract, schema, secrets, profiles, and source risk.
- Secret Exposure view with public-prefix and placeholder-strength review.
- CI Policy view with configurable error, warning, and score thresholds.
- Scan Timeline with local history and restore.
- Share Card view for polished Markdown summaries.
- Web UI/UX overhaul with animated panels, richer insight cards, responsive layouts, and refined dark mode.

## Shipped in 0.4

- CLI profile comparison with `envlens compare BASE TARGET`.
- Web profile comparison for `.env` and `.env.production`.
- Secret-aware drift output that masks secret-looking values.

## Shipped in 0.3

- Static browser workbench for paste-and-check env contract reviews.
- Issues, variables, profile comparison, explain, fix-plan, generated-schema, docs, export, and CLI views.
- Share links, downloads, ignored-key filters, and light/dark themes.
- Browser-side support for text, JSON, GitHub annotation, and SARIF-style exports.
- GitHub Pages deployment workflow.

## Shipped in 0.2

- SARIF output for GitHub Code Scanning.
- GitHub Action packaging and step summaries.
- Framework presets for common stacks.
- `envlens doctor`, `envlens explain`, `envlens list-presets`, and `envlens schema`.
- Published JSON Schema for editor integration.
- Project docs, examples, contribution guide, security policy, maintainer guide, and release process.

## Near Term

- Publish to PyPI.
- Add more framework presets.
- Add typed schema examples for popular stacks.
- Add richer dynamic-source detection where safe.
- Add package manager installation docs.

## Medium Term

- Add optional runtime validators for Python and Node.js.
- Add Docker Compose and Kubernetes environment matrix checks.
- Add interactive fix mode for `envlens doctor`.
- Add a generated demo GIF for the README.

## Long Term

- Support workspace-level reports for monorepos.
- Support plugin-style scanners.
- Support schema import/export for popular validator libraries.
