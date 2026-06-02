# Configuration

`envlens` reads `[tool.envlens]` from `pyproject.toml`.

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

## Fields

| Field | Meaning |
| --- | --- |
| `env` | Env files to validate |
| `example` | Example env contract file |
| `schema` | Typed schema file |
| `preset` | Built-in presets to apply |
| `ignore` | Env keys to ignore |
| `format` | Default output format |
| `strict` | Treat warnings as failures |
| `summary` | Write GitHub step summary when possible |

CLI flags override config values.

## Schema Validation

Use the published JSON Schema to get editor validation for `env.schema.yml`:

```text
https://raw.githubusercontent.com/Luckymeyo/envlens/main/schemas/env.schema.json
```

The same schema is available from the CLI:

```console
envlens schema
```

See [Editor Integration](EDITOR_INTEGRATION.md) for VS Code configuration.
