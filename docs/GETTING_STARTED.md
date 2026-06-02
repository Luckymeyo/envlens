# Getting Started

`envlens` checks whether your environment-variable contract matches the code that uses it.

## Install

```console
python -m pip install -e .
```

## First Run

```console
envlens check
```

If your project has no `.env`, pass an explicit env file:

```console
envlens check --env .env.local
```

## Add a Schema

```yaml
DATABASE_URL:
  type: url
  required: true
  description: Database connection string.

PORT:
  type: integer
  default: 3000
  description: Local server port.
```

Run:

```console
envlens check --schema env.schema.yml
```

## Explain One Key

```console
envlens explain DATABASE_URL
```

This shows schema metadata, env file presence, source usage, and findings for one key.

## Editor Validation

Print the JSON Schema used for `env.schema.yml`:

```console
envlens schema
```

For editor setup, see [Editor Integration](EDITOR_INTEGRATION.md).
