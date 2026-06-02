# Editor Integration

`envlens` publishes a JSON Schema for `env.schema.yml` and `env.schema.json`.

Use this URL in editors that support schema associations:

```text
https://raw.githubusercontent.com/Luckymeyo/envlens/main/schemas/env.schema.json
```

You can also print the schema from the CLI:

```console
envlens schema
```

## VS Code

Add this to workspace settings:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/Luckymeyo/envlens/main/schemas/env.schema.json": [
      "env.schema.yml",
      "env.schema.yaml"
    ]
  },
  "json.schemas": [
    {
      "fileMatch": ["env.schema.json"],
      "url": "https://raw.githubusercontent.com/Luckymeyo/envlens/main/schemas/env.schema.json"
    }
  ]
}
```

## What It Validates

The schema validates the supported contract fields:

- `type`
- `required`
- `default`
- `values`
- `description`
- `secret`
- `public`

It also supports the short form:

```yaml
DATABASE_URL: url
PORT: integer
```
