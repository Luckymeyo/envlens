# Presets

Presets add optional schema entries for framework-provided variables. They prevent false positives for variables that are expected but not usually listed in `.env.example`.

List presets:

```console
envlens list-presets
```

Use a preset:

```console
envlens check --preset nextjs
```

Available presets:

- `nextjs`
- `vite`
- `django`
- `fastapi`
- `docker-compose`

Project schemas override preset entries.

