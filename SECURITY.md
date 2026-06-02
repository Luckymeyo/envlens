# Security Policy

`envlens` helps identify configuration-contract risk. It is not a replacement for a dedicated secret scanner.

## Reporting Security Issues

Please do not open public issues for security-sensitive reports.

Email the maintainer listed in the GitHub profile or open a private security advisory on GitHub if available.

Include:

- affected version or commit
- reproduction steps
- expected and actual behavior
- whether any real secret, credential, or private data was exposed

## Fixture Safety

Do not add provider-shaped fake secrets to tests, docs, or examples. GitHub push protection may block commits that resemble real tokens, even when they are fake.

Prefer values like:

```dotenv
BILLING_TOKEN=replace-me
APP_SECRET=fake_secret_value_for_tests
```

## Supported Versions

`envlens` is early-stage. Security fixes are applied to the default branch first.

