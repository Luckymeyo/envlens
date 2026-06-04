# Web Demo

The envlens web demo is a static browser workbench for quick environment-contract checks.

Open it locally:

```console
python -m http.server 8765 --directory web
```

Then visit:

```text
http://localhost:8765
```

When GitHub Pages is enabled for the repository, the public demo URL is:

```text
https://luckymeyo.github.io/envlens/
```

## Included Views

| View | Purpose |
| --- | --- |
| Issues | Filter findings by severity |
| Variables | Review detected keys, sources, schema types, and status |
| Explain | Inspect one variable across env files, schema, source, and findings |
| Fix Plan | Group findings into a remediation checklist |
| Schema | Generate a starter `env.schema.yml` from detected variables |
| Docs | Generate a Markdown environment table |
| Export | Copy text, JSON, GitHub annotation, or SARIF output |
| CLI | Generate local CLI commands and a GitHub Actions snippet |

## Features

- Paste `.env`, `.env.example`, schema, and source snippets.
- Drag files into the workbench.
- Apply framework presets.
- Ignore exact keys or wildcard prefixes such as `DYNAMIC_*`.
- Copy a shareable URL for the current workbench state.
- Toggle light and dark themes.
- Download generated docs, schema, reports, and command snippets.

## Notes

- The demo runs in the browser.
- It mirrors the CLI's common checks, but the CLI remains the source of truth for CI.
- It has no build step and no runtime dependencies.
