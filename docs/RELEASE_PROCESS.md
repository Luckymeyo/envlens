# Release Process

## Pre-release Checklist

```console
python -m unittest discover -s tests
envlens check examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
envlens docs examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
envlens doctor examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
envlens list-presets
```

## Steps

1. Update `CHANGELOG.md`.
2. Update `src/envlens/__init__.py` and `pyproject.toml` version.
3. Commit release changes.
4. Create a signed tag if available.
5. Push tag and branch.
6. Publish package artifacts when packaging is ready.

