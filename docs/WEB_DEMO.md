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
| Radar | Review contract, schema, secrets, profiles, and source risk areas |
| Secrets | Audit secret-shaped keys, public prefixes, and placeholder strength |
| Variables | Review detected keys, sources, schema types, and status |
| Profiles | Compare `.env` with `.env.production` |
| Policy | Configure CI gate thresholds and copy enforcement snippets |
| Timeline | Review local scan history and restore prior states |
| Explain | Inspect one variable across env files, schema, source, and findings |
| Fix Plan | Group findings into a remediation checklist |
| Schema | Generate a starter `env.schema.yml` from detected variables |
| Share | Generate a polished Markdown scan card |
| Docs | Generate a Markdown environment table |
| Export | Copy text, JSON, GitHub annotation, or SARIF output |
| CLI | Generate local CLI commands and a GitHub Actions snippet |

## Features

- Paste `.env`, `.env.example`, schema, and source snippets.
- Compare local and production/staging profile files.
- Drag files into the workbench.
- Apply framework presets.
- Ignore exact keys or wildcard prefixes such as `DYNAMIC_*`.
- Review risk radar, secret exposure, and CI policy gates.
- Keep a local scan timeline and restore previous states.
- Copy or download a share card for demos and reports.
- Copy a shareable URL for the current workbench state.
- Toggle light and dark themes.
- Download generated docs, schema, reports, and command snippets.

## Notes

- The demo runs in the browser.
- It mirrors the CLI's common checks, but the CLI remains the source of truth for CI.
- It has no build step and no runtime dependencies.
