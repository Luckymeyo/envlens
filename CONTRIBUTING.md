# Contributing to envlens

Thanks for helping improve `envlens`. The project is meant to stay small, predictable, and useful in local development and CI.

## Good First Contributions

- Add a source scanner pattern for a language or framework.
- Add a framework preset.
- Improve schema inference.
- Add a regression test for a real env drift edge case.
- Improve docs, examples, or GitHub Action usage.

## Development Setup

```console
git clone https://github.com/Luckymeyo/envlens.git
cd envlens
python -m pip install -e .
python -m unittest discover -s tests
```

Run the CLI locally:

```console
envlens check examples --env examples/.env.example --example examples/.env.example --schema examples/env.schema.yml
```

## Pull Request Checklist

- Tests pass with `python -m unittest discover -s tests`.
- New behavior has a focused test.
- README or docs are updated when public behavior changes.
- Fixtures do not contain provider-shaped fake secrets.
- The change keeps the CLI dependency-light unless there is a strong reason.

## Design Notes

`envlens` is intentionally conservative. It should explain what it found and avoid guessing when source code uses dynamic env access.

When in doubt, prefer:

- clear errors over clever inference
- small helpers over broad abstractions
- deterministic output over flashy formatting
- docs and tests over silent behavior

