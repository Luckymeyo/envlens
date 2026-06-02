# GitHub Action

Use `envlens` directly in GitHub Actions:

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

## Inputs

| Input | Default | Meaning |
| --- | --- | --- |
| `path` | `.` | Project path |
| `env` | empty | Env file to validate |
| `example` | `.env.example` | Example env file |
| `schema` | `env.schema.yml` | Typed schema file |
| `preset` | empty | Framework preset |
| `format` | `github` | Output format |
| `strict` | `false` | Treat warnings as failures |
| `summary` | `true` | Write job summary |

