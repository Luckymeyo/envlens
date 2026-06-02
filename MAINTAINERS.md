# Maintainers

## Current Maintainer

- `Luckymeyo`

## Maintainer Responsibilities

- Review issues and pull requests.
- Keep tests and examples current.
- Cut releases and update the changelog.
- Review new scanner patterns for false positives.
- Keep fixtures free of provider-shaped fake secrets.
- Maintain GitHub Action and CI compatibility.

## Release Expectations

Before release:

- run the test suite
- smoke test `check`, `docs`, `doctor`, `explain`, `list-presets`, and SARIF output
- update `CHANGELOG.md`
- tag the release
- publish package artifacts when packaging is ready

