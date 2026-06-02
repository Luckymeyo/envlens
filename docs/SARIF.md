# SARIF Output

Generate SARIF:

```console
envlens check --format sarif > envlens.sarif
```

Upload it in GitHub Actions:

```yaml
- run: envlens check --format sarif > envlens.sarif
- uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: envlens.sarif
```

SARIF is useful when teams want env contract drift to appear in code-scanning workflows.

