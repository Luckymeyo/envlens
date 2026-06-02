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

## Data Flow

1. Load config.
2. Parse env files.
3. Load schema and presets.
4. Scan source files.
5. Compare the contract.
6. Render output.

The core package avoids required third-party runtime dependencies.

