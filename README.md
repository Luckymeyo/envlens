# envlens

[![CI](https://github.com/Luckymeyo/envlens/actions/workflows/ci.yml/badge.svg)](https://github.com/Luckymeyo/envlens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](pyproject.toml)
[![Web Demo](https://img.shields.io/badge/web-demo-0f766e.svg)](https://luckymeyo.github.io/envlens/)

Find missing, stale, unsafe, and mistyped environment variables before they break production.

`envlens` treats environment variables like a contract. It scans your source code for env usage, compares that usage against `.env`, `.env.example`, and an optional typed schema, then reports drift in formats that work locally and in CI.

Try the static web workbench: [luckymeyo.github.io/envlens](https://luckymeyo.github.io/envlens/).

The web workbench now includes a larger product-style review surface:

- Risk Radar for contract, schema, secrets, profile, and source risk areas
- Secret Exposure audit with strength scoring and public-prefix warnings
- CI Policy builder with configurable error, warning, and score gates
- Scan Timeline with local history and restore
- Share Card for clean scan summaries

```console
$ envlens check

ERROR           DATABASE_URL             missing-in-env         DATABASE_URL is required but missing from .env
ERROR           BILLING_TOKEN            missing-in-example     BILLING_TOKEN is used in src/billing.ts but missing from .env.example
WARNING         OLD_FEATURE_FLAG         unused-example         OLD_FEATURE_FLAG is listed in .env.example but was not found in scanned code
WARNING         PUBLIC_SECRET_KEY        public-secret-name     PUBLIC_SECRET_KEY looks public and secret at the same time
INFO            CACHE_TTL                schema-missing-used    CACHE_TTL is used in code but has no schema entry

5 issues found: 2 errors, 2 warnings, 1 info
```

## The Pitch

Every growing codebase eventually develops environment drift:

- code reads a variable that nobody documented
- `.env.example` keeps variables from features that were deleted months ago
- deploys fail because a URL, port, boolean, or enum is malformed
- public frontend env names accidentally look like private secret names
- teammates waste time asking which keys are required for local setup

`envlens` gives the project a single source of truth for configuration, without forcing a heavy framework or runtime dependency.

## Who It Is For

`envlens` is useful when configuration has become bigger than a few obvious variables.

| Team or project | How envlens helps |
| --- | --- |
| Solo projects | Keeps `.env.example` honest as features change |
| Open-source repos | Makes local setup clearer for contributors |
| Frontend teams | Catches public/private env naming mistakes |
| Backend teams | Validates URLs, ports, booleans, and required secrets before deploys |
| Platform teams | Adds a small CI gate without introducing a new service |
| Monorepos | Lets each app validate its own schema and env files |

## Why Another Env Tool

Many tools validate env values at application startup. That is useful, but it is late. By the time startup validation fails, somebody has already pulled the code, run the app, or shipped a deploy.

`envlens` works earlier:

- during local development
- during pull requests
- before a deploy pipeline reaches runtime
- while updating docs for contributors

It is not trying to replace framework-specific runtime validation. It is the layer that checks whether the repo's configuration contract is documented, typed, and in sync with the code that uses it.

## What It Checks

| Check | Example | Severity |
| --- | --- | --- |
| Missing local env | `DATABASE_URL` is required but absent from `.env` | error |
| Used but undocumented | `process.env.BILLING_TOKEN` is missing from `.env.example` | error |
| Empty required value | `DATABASE_URL=` with `required: true` | error |
| Type mismatch | `PORT=abc` with `type: integer` | error |
| Invalid enum | `NODE_ENV=staging` outside allowed values | error |
| Duplicate key | `PORT` appears twice in the same env file | warning |
| Undocumented local key | `.env` contains a key not in schema or example | warning |
| Unused example key | `.env.example` lists a key not found in scanned code | warning |
| Public secret name | `NEXT_PUBLIC_SECRET_KEY` | warning |
| Schema gap | scanned key has no `env.schema.yml` entry | info |

## Adoption Modes

You can adopt `envlens` gradually.

### 0. Browser Workbench

Paste env files, schema, and source snippets into the web workbench:

```text
https://luckymeyo.github.io/envlens/
```

Use this for quick reviews, screenshots, and demos before installing the CLI.

### 1. Documentation Mode

Start by generating docs without failing builds:

```console
envlens docs --schema env.schema.yml > ENVIRONMENT.md
```

Use this when the project needs clearer onboarding but you are not ready to enforce rules.

### 2. Local Doctor Mode

Run checks locally:

```console
envlens check
```

This is good for catching drift while adding new features.

### 3. Pull Request Mode

Use GitHub annotations:

```console
envlens check --format github
```

This points contributors to the exact file and line where an env key was discovered.

### 4. CI Gate Mode

Treat warnings as failures:

```console
envlens check --format github --strict
```

Use this once the schema is mature and the team agrees on the contract.

## Install

From source:

```console
git clone https://github.com/Luckymeyo/envlens.git
cd envlens
python -m pip install -e .
envlens check
```

Run directly from a checkout:

```console
PYTHONPATH=src python -m envlens check examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m envlens check examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
```

Windows cmd:

```cmd
set PYTHONPATH=src
python -m envlens check examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
```

## Quick Start

Create a sample contract:

```dotenv
# .env.example
DATABASE_URL=postgres://localhost:5432/app
PORT=3000
NODE_ENV=development
PUBLIC_API_URL=https://api.example.com
BILLING_TOKEN=replace-me
```

Create a typed schema:

```yaml
# env.schema.yml
DATABASE_URL:
  type: url
  required: true
  description: Database connection string.

PORT:
  type: integer
  required: true
  default: 3000
  description: Local web server port.

NODE_ENV:
  type: enum
  values: [development, test, production]
  default: development
  description: Runtime environment.

PUBLIC_API_URL:
  type: url
  required: true
  public: true
  description: Public API base URL used by the frontend.

BILLING_TOKEN:
  type: string
  required: true
  secret: true
  description: Server-side billing provider token.
```

Run the analyzer:

```console
envlens check --schema env.schema.yml
```

Generate docs:

```console
envlens docs --schema env.schema.yml > ENVIRONMENT.md
```

## Commands

### `envlens check`

Validate a project environment contract.

```console
envlens check [PROJECT_PATH]
```

Common options:

```console
--env .env                  Env file to validate. Can be repeated.
--example .env.example      Example env contract file.
--schema env.schema.yml     Typed schema file.
--format text               Output format: text, json, github, or sarif.
--strict                    Treat warnings as failures.
--no-scan                   Skip source code scanning.
```

Examples:

```console
envlens check
envlens check apps/web --env apps/web/.env.local --schema apps/web/env.schema.yml
envlens check --format json
envlens check --format github --strict
envlens check --format sarif > envlens.sarif
envlens check --preset nextjs --summary
envlens compare .env .env.production --schema env.schema.yml
envlens explain DATABASE_URL
envlens list-presets
envlens schema
```

### `envlens compare`

Compare two env profiles, such as local and production.

```console
envlens compare .env .env.production --schema env.schema.yml
envlens compare .env .env.staging --format json
envlens compare .env .env.production --show-values
```

Secret-looking values remain masked even when `--show-values` is used.

### `envlens docs`

Generate a Markdown table from the detected contract.

```console
envlens docs --schema env.schema.yml
```

Example output:

| Variable | Required | Type | Default | Description |
| --- | --- | --- | --- | --- |
| DATABASE_URL | yes | url |  | Database connection string. |
| NODE_ENV | no | enum | development | Runtime environment. |
| PORT | yes | integer | 3000 | Local web server port. |

### `envlens init-schema`

Infer a starter schema from source code and `.env.example`.

```console
envlens init-schema > env.schema.yml
```

This is intentionally conservative. It gives you a first draft, then you add descriptions, enum values, and optional flags.

### `envlens doctor`

Print a remediation plan grouped by issue type.

```console
envlens doctor
```

This is useful after a noisy first run because it turns findings into a practical cleanup checklist.

### `envlens explain`

Explain one variable across schema, env files, source usage, and findings.

```console
envlens explain DATABASE_URL
```

This is useful when a single variable is confusing or appears in multiple places.

### `envlens list-presets`

List the built-in framework presets.

```console
envlens list-presets
envlens list-presets --format json
```

### `envlens schema`

Print the JSON Schema for `env.schema.yml` files.

```console
envlens schema
```

Use this to wire editor validation into VS Code, YAML Language Server, or custom automation.

## Output Formats

### Text

Default output for humans:

```console
envlens check
```

### JSON

Structured output for scripts:

```console
envlens check --format json
```

The JSON payload includes:

- summary counts
- normalized issues
- source usages with file, line, language, and expression

### GitHub

Annotation output for GitHub Actions:

```console
envlens check --format github
```

Errors become workflow errors, warnings become workflow warnings, and info items become notices.

### SARIF

SARIF output for GitHub Code Scanning or other SARIF-compatible tools:

```console
envlens check --format sarif > envlens.sarif
```

In GitHub Actions, upload it with `github/codeql-action/upload-sarif`:

```yaml
- run: envlens check --format sarif > envlens.sarif
- uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: envlens.sarif
```

### GitHub Step Summary

Add a Markdown summary to the Actions run:

```console
envlens check --format github --summary
```

## Severity Model

`envlens` uses three severities so teams can tune enforcement over time.

| Severity | Meaning | Default exit behavior |
| --- | --- | --- |
| error | The environment contract is likely broken | non-zero exit |
| warning | The contract may be stale, risky, or confusing | zero exit unless `--strict` |
| info | Useful cleanup or schema completeness signal | zero exit |

This lets you start with visibility, then move to enforcement once the contract is clean.

## Configuration

`envlens` reads `[tool.envlens]` from `pyproject.toml` in the project root.

```toml
[tool.envlens]
env = [".env.local", ".env.test"]
example = ".env.example"
schema = "env.schema.yml"
preset = ["nextjs"]
ignore = ["EXTERNAL_PLATFORM_KEY"]
format = "github"
strict = true
summary = true
```

CLI flags override config values.

## Schema Reference

`env.schema.yml` is a small YAML-like file where each top-level key is an environment variable.

For editor validation, use the published JSON Schema:

```text
https://raw.githubusercontent.com/Luckymeyo/envlens/main/schemas/env.schema.json
```

```yaml
VARIABLE_NAME:
  type: string
  required: true
  default: ""
  values: []
  description: Human-readable documentation.
  secret: false
  public: false
```

Supported fields:

| Field | Type | Purpose |
| --- | --- | --- |
| `type` | string | `string`, `number`, `integer`, `boolean`, `url`, `email`, or `enum` |
| `required` | boolean | Whether the key must appear in validated env files |
| `default` | string | Documented default value |
| `values` | list | Allowed values for `type: enum` |
| `description` | string | Documentation used by `envlens docs` |
| `secret` | boolean | Override secret-name inference |
| `public` | boolean | Override public-client-name inference |

## Source Scanning

`envlens` scans common source patterns and records file and line information for each key.

| Language | Patterns |
| --- | --- |
| JavaScript and TypeScript | `process.env.NAME`, `process.env["NAME"]`, `import.meta.env.NAME` |
| Python | `os.getenv("NAME")`, `os.environ["NAME"]`, `os.environ.get("NAME")` |
| Go | `os.Getenv("NAME")`, `os.LookupEnv("NAME")` |
| Ruby | `ENV["NAME"]`, `ENV.fetch("NAME")` |
| PHP | `getenv("NAME")`, `$_ENV["NAME"]`, `$_SERVER["NAME"]` |

Skipped directories include `.git`, `node_modules`, `.venv`, `vendor`, `dist`, `build`, `.next`, and cache folders.

## Framework Presets

Presets document common framework-provided keys so they do not need to appear in `.env.example`.

```console
envlens check --preset nextjs
envlens check --preset vite
envlens check --preset django
envlens check --preset fastapi
envlens check --preset docker-compose
```

Preset keys are optional by default and can still be overridden in `env.schema.yml`.

## Capability Matrix

| Capability | CLI | Web | GitHub Action | JSON | SARIF | Docs |
| --- | --- | --- | --- | --- | --- | --- |
| Detect env usage in source | yes | yes | yes | yes | yes | yes |
| Compare code with `.env.example` | yes | yes | yes | yes | yes | yes |
| Compare env profiles | yes | yes | no | yes | no | no |
| Review risk radar | no | yes | no | yes | no | no |
| Audit secret exposure | partial | yes | no | yes | no | no |
| Build CI policy gate | yes | yes | yes | yes | no | no |
| Restore scan history | no | yes | no | no | no | no |
| Generate share card | no | yes | no | no | no | no |
| Validate typed values | yes | yes | yes | yes | yes | yes |
| Explain one variable | yes | yes | no | no | no | no |
| Generate Markdown docs | yes | yes | no | no | no | yes |
| Publish Code Scanning results | no | copy/export | yes | no | yes | no |
| Editor schema support | yes | no | no | yes | no | yes |

## Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Configuration](docs/CONFIGURATION.md)
- [GitHub Action](docs/GITHUB_ACTION.md)
- [SARIF Output](docs/SARIF.md)
- [Editor Integration](docs/EDITOR_INTEGRATION.md)
- [Web Demo](docs/WEB_DEMO.md)
- [Presets](docs/PRESETS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Release Process](docs/RELEASE_PROCESS.md)
- [Roadmap](docs/ROADMAP.md)

## Examples

- [General mixed-language example](examples)
- [Next.js example](examples/nextjs)
- [FastAPI example](examples/fastapi)
- [Monorepo example](examples/monorepo)

## Monorepo Examples

Validate one app inside a monorepo:

```console
envlens check apps/web --env apps/web/.env.local --example apps/web/.env.example --schema apps/web/env.schema.yml
```

Validate multiple apps in CI:

```yaml
strategy:
  matrix:
    app: [apps/web, apps/api, apps/admin]

steps:
  - uses: actions/checkout@v5
  - uses: actions/setup-python@v6
    with:
      python-version: "3.12"
  - run: python -m pip install .
  - run: envlens check ${{ matrix.app }} --schema ${{ matrix.app }}/env.schema.yml --format github --strict
```

## Security Posture

`envlens` is not a replacement for a dedicated secrets scanner. It focuses on environment contract risk:

- secret-like names in public frontend prefixes
- real-looking values in sample env files
- weak placeholder values in local secret keys
- accidental documentation of sensitive values

Use it alongside GitHub secret scanning, pre-commit hooks, or dedicated scanners if your project handles sensitive credentials.

## CI

Use the GitHub Action:

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
      - uses: Luckymeyo/envlens@main
        with:
          path: .
          format: github
          strict: "true"
          summary: "true"
```

Use GitHub Actions annotations:

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

Use JSON for custom pipelines:

```console
envlens check --format json
```

The JSON output contains a summary, issue list, and detected source usages.

## How It Works

`envlens` has four small stages:

1. Parse env files
   `.env`, `.env.example`, and any repeated `--env` files are parsed into key/value entries with line numbers.

2. Load schema
   `env.schema.yml` or JSON schema input is normalized into a typed contract.

3. Scan source
   Supported source files are searched for common env access patterns.

4. Compare contracts
   The analyzer combines env files, schema metadata, and source usage into deterministic findings.

The implementation has no required third-party runtime dependencies, which keeps installs small and CI behavior predictable.

## Example Workflows

### Adding a New Environment Variable

1. Add the variable where the app reads it.
2. Add it to `.env.example`.
3. Add type and description metadata to `env.schema.yml`.
4. Run `envlens check`.
5. Regenerate docs with `envlens docs` if your README or `ENVIRONMENT.md` includes an env table.

### Cleaning Up an Old Feature

1. Remove the old code path.
2. Run `envlens check`.
3. Review `unused-example` and `schema-unused` findings.
4. Remove stale keys from `.env.example` and `env.schema.yml`.

### Preparing a Repo for Contributors

1. Create `.env.example`.
2. Run `envlens init-schema > env.schema.yml`.
3. Add descriptions to the generated schema.
4. Run `envlens docs > ENVIRONMENT.md`.
5. Add a CI check in non-strict mode.

### Publishing Code Scanning Results

1. Run `envlens check --format sarif > envlens.sarif`.
2. Upload the SARIF file in CI.
3. Review env contract drift in the repository security/code scanning views.

## Design Principles

- Local first: useful on a laptop before it becomes a CI gate.
- Contract driven: `.env.example` and `env.schema.yml` should describe what the project needs.
- Explainable output: every finding should include a key, a reason, and usually a file or line.
- Conservative security checks: flag suspicious patterns without pretending to be a full secrets scanner.
- Small surface area: one CLI that does a focused job well.

## Limitations

`envlens` is intentionally lightweight. It does not evaluate arbitrary code, expand shell scripts, execute framework config, or parse every possible dynamic env lookup.

These patterns are not reliably detectable yet:

```python
name = "DATABASE_URL"
os.getenv(name)
```

```ts
const key = "DATABASE_" + "URL";
process.env[key];
```

When a variable is intentionally dynamic or provided outside the source tree, add it to `env.schema.yml` so it remains documented.

## Comparison

| Need | envlens | Runtime env validators | Secrets scanners |
| --- | --- | --- | --- |
| Find env usage in source | yes | usually no | no |
| Compare code usage to `.env.example` | yes | no | no |
| Validate typed env values | yes | yes | no |
| Generate env documentation | yes | sometimes | no |
| Run before app startup | yes | no | yes |
| Detect provider credentials | limited | no | yes |
| Enforce runtime safety | no | yes | no |

The sweet spot for `envlens` is configuration contract drift. It pairs well with runtime validators and secrets scanners rather than competing with them.

## Project Layout

```text
envlens/
  src/envlens/
    analyzer.py     contract comparison engine
    cli.py          command-line interface
    compare.py      env profile comparison
    envfile.py      dotenv parser
    models.py       dataclasses used across the project
    report.py       text, JSON, GitHub, and docs renderers
    scanner.py      source-code env usage scanner
    schema.py       schema loader and normalizer
    schema_json.py  published JSON Schema renderer
  examples/         sample app and schema
  schemas/          editor and automation schema files
  web/              static browser workbench
  tests/            unit tests
```

## Roadmap

Shipped in 0.5:

- Risk Radar, Secret Exposure, CI Policy, Scan Timeline, and Share Card web views
- Local scan history with restore support
- Configurable web CI policy thresholds
- UI/UX overhaul with animated panels, responsive insight cards, and richer dark mode polish

Shipped in 0.4:

- CLI profile comparison with `envlens compare BASE TARGET`
- Web profile comparison for `.env` and `.env.production`
- Secret-aware drift output that masks secret-looking values

Shipped in 0.3:

- Static web workbench
- Browser-side issue, variable, profile comparison, explain, fix plan, schema, docs, export, and CLI views
- Share links, downloads, ignored-key filters, and light/dark themes
- GitHub Pages deployment workflow

Shipped in 0.2:

- SARIF output for GitHub Code Scanning
- GitHub Action packaging and step summaries
- Framework presets for common stacks
- `envlens doctor`, `envlens explain`, and `envlens list-presets`
- Published JSON Schema/editor integration for `env.schema.yml`
- Expanded docs, examples, and maintainer files

Near term:

- Support multiple environment profiles, such as `.env.local`, `.env.test`, and `.env.production`
- Add richer duplicate and case-collision reporting
- Publish to PyPI
- Add package manager installation docs

Future:

- Interactive `envlens doctor` fix wizard
- Runtime validators for Python and Node.js
- Kubernetes ConfigMap and Secret checks
- Docker Compose environment matrix checks
- Package releases for PyPI and Homebrew

## FAQ

### Does envlens read my real secrets?

It parses the env files you pass to it and reports only key names, locations, and validation problems. Avoid committing real `.env` files, and prefer validating `.env.example` or local files in trusted environments.

### Can I use it without a schema?

Yes. Without `env.schema.yml`, `envlens` still compares scanned usage with `.env.example` and env files. The schema adds stronger typing, descriptions, defaults, and public/secret overrides.

### Why does it report variables that are intentionally unused?

Some env variables are consumed by hosting platforms, CLIs, containers, or external tools instead of source code. Add those variables to `env.schema.yml` with a description so they remain documented.

### Does it support YAML fully?

The current schema parser supports the small YAML subset needed for simple env contracts. JSON schema files are also supported. Full YAML parsing is planned once the project introduces optional dependencies.

### Will dynamic env access be supported?

Some dynamic patterns may be added, but `envlens` will stay conservative. Guessing dynamic keys incorrectly is worse than asking maintainers to document them in the schema.

## Contributing

Contributions are welcome. Good first issues include:

- adding a new source scanning pattern
- improving schema inference
- adding framework-specific presets
- expanding CI output formats
- tightening tests around edge cases

Run tests locally:

```console
python -m unittest discover -s tests
```

Please keep fixtures free of provider-shaped fake secrets. GitHub push protection may block commits that resemble real API keys, even when they are only test data.

## License

MIT. See [LICENSE](LICENSE).
