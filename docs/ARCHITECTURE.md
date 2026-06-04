# Architecture

`envlens` is intentionally small and split into focused modules.

| Module | Responsibility |
| --- | --- |
| `cli.py` | Argument parsing and command routing |
| `config.py` | `pyproject.toml` config loading |
| `envfile.py` | Dotenv parsing |
| `schema.py` | Schema loading and normalization |
| `scanner.py` | Source-code env usage detection |
| `presets.py` | Framework preset definitions |
| `analyzer.py` | Contract comparison and issue generation |
| `report.py` | Text, JSON, GitHub, SARIF, docs, doctor, and explain output |
| `web/` | Static browser workbench for quick env contract reviews |

## Data Flow

1. Load config.
2. Parse env files.
3. Load schema and presets.
4. Scan source files.
5. Compare the contract.
6. Render output.

The core package avoids required third-party runtime dependencies.

## Web Workbench

The web app is intentionally static: `web/index.html`, `web/styles.css`, and `web/app.js`.

It mirrors the CLI's common parsing, scanning, comparison, and export behavior in browser JavaScript so contributors can try envlens without installing Python. The CLI remains the source of truth for CI and release testing.
