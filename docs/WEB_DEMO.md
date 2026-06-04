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
| Docs | Generate a Markdown environment table |
| Export | Copy text, JSON, GitHub annotation, or SARIF output |

## Notes

- The demo runs in the browser.
- It mirrors the CLI's common checks, but the CLI remains the source of truth for CI.
- It has no build step and no runtime dependencies.
