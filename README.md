# envlens

Find missing, stale, unsafe, and mistyped environment variables before they break production.

`envlens` is a small CLI for treating environment variables like a contract. It scans your code for env usage, compares that against `.env`, `.env.example`, and an optional typed schema, then reports drift in a CI-friendly format.

```console
$ envlens check

ERROR  DATABASE_URL  missing-in-env       required in .env.example but missing from .env
ERROR  STRIPE_KEY    missing-in-example   used in src/billing.ts but missing from .env.example
WARN   API_SECRET    secret-in-example    .env.example appears to contain a real secret
WARN   OLD_FLAG      unused-example       listed in .env.example but not used in scanned code

4 issues found: 2 errors, 2 warnings
```

## Why

Most projects discover env drift too late:

- a variable is used in code but missing from `.env.example`
- production has a stale variable nobody uses
- a secret leaks into a sample file
- a port, URL, or enum value has the wrong type
- CI passes while a deploy fails at boot

`envlens` catches those problems close to the commit.

## Features

- Scan source code for environment variable usage
- Compare `.env`, `.env.example`, and `env.schema.yml`
- Detect missing, extra, unused, empty, duplicate, and undocumented keys
- Validate types: `string`, `number`, `integer`, `boolean`, `url`, `email`, and `enum`
- Flag suspicious secret values and public secret names
- Output human-readable text, JSON, or GitHub Actions annotations
- Generate Markdown env documentation tables
- No required third-party runtime dependencies

## Quick Start

From source:

```console
git clone https://github.com/Luckymeyo/envlens.git
cd envlens
python -m pip install -e .
envlens check
```

Or run without installing:

```console
PYTHONPATH=src python -m envlens check examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
```

## Example Schema

Create `env.schema.yml`:

```yaml
DATABASE_URL:
  type: url
  required: true
  description: Database connection string.

PORT:
  type: integer
  default: 3000
  description: Local web server port.

NODE_ENV:
  type: enum
  values: [development, test, production]
  default: development
  description: Runtime environment.
```

Then run:

```console
envlens check --schema env.schema.yml
```

## CLI

```console
envlens check [PROJECT_PATH]
envlens docs [PROJECT_PATH]
envlens init-schema [PROJECT_PATH]
```

Useful options:

```console
--env .env                  Env file to validate. Can be repeated.
--example .env.example      Example contract file.
--schema env.schema.yml     Typed schema file.
--format text               text, json, or github.
--strict                    Treat warnings as failures.
--no-scan                   Skip code usage scanning.
```

## GitHub Actions

```yaml
name: envlens

on:
  pull_request:
  push:
    branches: [main]

jobs:
  envlens:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m pip install .
      - run: envlens check --format github --strict
```

## Documentation Table

Generate a README-ready table:

```console
envlens docs --schema env.schema.yml > ENVIRONMENT.md
```

Output:

| Variable | Required | Type | Default | Description |
| --- | --- | --- | --- | --- |
| DATABASE_URL | yes | url |  | Database connection string. |
| NODE_ENV | no | enum | development | Runtime environment. |

## Supported Code Patterns

`envlens` currently scans these common patterns:

- JavaScript/TypeScript: `process.env.NAME`, `process.env["NAME"]`, `import.meta.env.NAME`
- Python: `os.getenv("NAME")`, `os.environ["NAME"]`, `os.environ.get("NAME")`
- Go: `os.Getenv("NAME")`, `os.LookupEnv("NAME")`
- Ruby: `ENV["NAME"]`, `ENV.fetch("NAME")`
- PHP: `getenv("NAME")`, `$_ENV["NAME"]`, `$_SERVER["NAME"]`

## Roadmap

- Framework presets for Next.js, Vite, FastAPI, Django, Laravel, and Docker Compose
- SARIF output for GitHub code scanning
- Runtime validators for Python and Node.js
- Interactive fix wizard
- Kubernetes and Docker Compose environment matrix checks

## License

MIT

