from __future__ import annotations

import json
import sys
from .analyzer import display_path, is_secret_name
from .models import Analysis, EnvSpec
from .presets import PRESETS


def render_text(analysis: Analysis, use_color: bool | None = None) -> str:
    if use_color is None:
        use_color = sys.stdout.isatty()

    if not analysis.issues:
        return "No environment contract issues found."

    lines: list[str] = []
    for issue in analysis.issues:
        location = ""
        if issue.path:
            location = display_path(analysis.project_root, issue.path)
            if issue.line:
                location += f":{issue.line}"

        severity = colorize(issue.severity.upper(), issue.severity, use_color)
        key = issue.key or "-"
        suffix = f" ({location})" if location else ""
        lines.append(f"{severity:<15} {key:<24} {issue.code:<22} {issue.message}{suffix}")
        if issue.hint:
            lines.append(f"{'':15} {'':24} {'hint':<22} {issue.hint}")

    lines.append("")
    lines.append(
        f"{len(analysis.issues)} issues found: "
        f"{analysis.error_count} errors, {analysis.warning_count} warnings, {analysis.info_count} info"
    )
    return "\n".join(lines)


def render_json(analysis: Analysis) -> str:
    payload = {
        "summary": {
            "issues": len(analysis.issues),
            "errors": analysis.error_count,
            "warnings": analysis.warning_count,
            "info": analysis.info_count,
            "usages": len(analysis.usages),
        },
        "issues": [issue.to_dict() for issue in analysis.issues],
        "usages": [
            {
                "key": usage.key,
                "path": str(usage.path),
                "line": usage.line,
                "language": usage.language,
                "expression": usage.expression,
            }
            for usage in analysis.usages
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_sarif(analysis: Analysis) -> str:
    rules = {}
    results = []
    for issue in analysis.issues:
        rules.setdefault(
            issue.code,
            {
                "id": issue.code,
                "name": issue.code,
                "shortDescription": {"text": issue.code.replace("-", " ").title()},
                "help": {"text": issue.hint or issue.message},
            },
        )
        result = {
            "ruleId": issue.code,
            "level": {"error": "error", "warning": "warning", "info": "note"}.get(issue.severity, "note"),
            "message": {"text": issue.message},
        }
        if issue.path:
            result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": display_path(analysis.project_root, issue.path).replace("\\", "/")},
                        "region": {"startLine": issue.line or 1},
                    }
                }
            ]
        results.append(result)

    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "envlens",
                        "informationUri": "https://github.com/Luckymeyo/envlens",
                        "rules": sorted(rules.values(), key=lambda rule: rule["id"]),
                    }
                },
                "results": results,
            }
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def render_github(analysis: Analysis) -> str:
    if not analysis.issues:
        return "No environment contract issues found."

    lines: list[str] = []
    for issue in analysis.issues:
        command = "error" if issue.severity == "error" else "warning" if issue.severity == "warning" else "notice"
        props = []
        if issue.path:
            props.append(f"file={display_path(analysis.project_root, issue.path)}")
        if issue.line:
            props.append(f"line={issue.line}")
        props.append(f"title={escape_github(issue.code)}")
        message = issue.message
        if issue.hint:
            message += f" Hint: {issue.hint}"
        lines.append(f"::{command} {','.join(props)}::{escape_github(message)}")
    return "\n".join(lines)


def render_docs(analysis: Analysis) -> str:
    specs: dict[str, EnvSpec] = analysis.schema.specs if analysis.schema and analysis.schema.exists else {}
    example_entries = analysis.example_file.entries if analysis.example_file and analysis.example_file.exists else {}
    usage_keys = {usage.key for usage in analysis.usages}
    keys = sorted(set(specs) | set(example_entries) | usage_keys)

    rows = ["| Variable | Required | Type | Default | Description |", "| --- | --- | --- | --- | --- |"]
    for key in keys:
        spec = specs.get(key)
        required = spec.required if spec else key in example_entries
        type_name = spec.type if spec else infer_type_name(key)
        default = spec.default if spec and spec.default is not None else ""
        description = spec.description if spec else ""
        rows.append(
            "| {key} | {required} | {type_name} | {default} | {description} |".format(
                key=escape_markdown(key),
                required="yes" if required else "no",
                type_name=escape_markdown(type_name),
                default=escape_markdown(default),
                description=escape_markdown(description),
            )
        )
    return "\n".join(rows)


def render_summary(analysis: Analysis) -> str:
    lines = [
        "## envlens",
        "",
        "| Result | Count |",
        "| --- | ---: |",
        f"| Errors | {analysis.error_count} |",
        f"| Warnings | {analysis.warning_count} |",
        f"| Info | {analysis.info_count} |",
        f"| Env usages found | {len(analysis.usages)} |",
    ]
    if analysis.issues:
        lines.extend(["", "### Findings", "", "| Severity | Key | Code | Location |", "| --- | --- | --- | --- |"])
        for issue in analysis.issues[:25]:
            location = ""
            if issue.path:
                location = display_path(analysis.project_root, issue.path)
                if issue.line:
                    location += f":{issue.line}"
            lines.append(
                f"| {escape_markdown(issue.severity)} | {escape_markdown(issue.key or '-')} | "
                f"{escape_markdown(issue.code)} | {escape_markdown(location)} |"
            )
    else:
        lines.extend(["", "No environment contract issues found."])
    return "\n".join(lines) + "\n"


def render_doctor(analysis: Analysis) -> str:
    if not analysis.issues:
        return "envlens doctor\n\nNo environment contract issues found."

    buckets = {
        "missing-in-env": "Add missing required values to the target env file, or mark them `required: false` in `env.schema.yml`.",
        "missing-in-example": "Add used keys to `.env.example`, or document external keys in `env.schema.yml`.",
        "type-mismatch": "Update the env value or change the schema type if the schema is wrong.",
        "unused-example": "Remove stale sample keys, or keep them documented in `env.schema.yml` if consumed externally.",
        "undocumented-env": "Add local-only keys to `.env.example` or `env.schema.yml`.",
        "public-secret-name": "Rename public client-side variables so secret-looking keys are never exposed to the browser.",
        "secret-in-example": "Replace real-looking sample secrets with clear placeholders.",
    }
    lines = ["envlens doctor", "", "Recommended fixes:"]
    for code, advice in buckets.items():
        matches = [issue for issue in analysis.issues if issue.code == code]
        if not matches:
            continue
        lines.append("")
        lines.append(f"- {code}: {advice}")
        for issue in matches[:8]:
            key = f" {issue.key}" if issue.key else ""
            lines.append(f"  -{key}: {issue.message}")
    return "\n".join(lines)


def render_explain(analysis: Analysis, key: str) -> str:
    lines = [f"envlens explain {key}", ""]

    issues = [issue for issue in analysis.issues if issue.key == key]
    usages = [usage for usage in analysis.usages if usage.key == key]
    spec = analysis.schema.specs.get(key) if analysis.schema and analysis.schema.exists else None
    example = analysis.example_file.entries.get(key) if analysis.example_file and analysis.example_file.exists else None
    env_entries = [env_file.entries[key] for env_file in analysis.env_files if key in env_file.entries]

    if not any([issues, usages, spec, example, env_entries]):
        return f"envlens explain {key}\n\nNo contract, env file entry, or source usage found for {key}."

    if spec:
        lines.append("Schema")
        lines.append(f"- type: {spec.type}")
        lines.append(f"- required: {'yes' if spec.required else 'no'}")
        if spec.default is not None:
            lines.append(f"- default: {spec.default}")
        if spec.values:
            lines.append(f"- values: {', '.join(spec.values)}")
        if spec.description:
            lines.append(f"- description: {spec.description}")
        if spec.secret is not None:
            lines.append(f"- secret: {spec.secret}")
        if spec.public is not None:
            lines.append(f"- public: {spec.public}")
        lines.append("")

    if example:
        lines.append("Example")
        lines.append(f"- {display_path(analysis.project_root, example.path)}:{example.line}")
        lines.append("")

    if env_entries:
        lines.append("Env Files")
        for entry in env_entries:
            lines.append(f"- {display_path(analysis.project_root, entry.path)}:{entry.line}")
        lines.append("")

    if usages:
        lines.append("Source Usage")
        for usage in usages:
            lines.append(f"- {display_path(analysis.project_root, usage.path)}:{usage.line} `{usage.expression}`")
        lines.append("")

    if issues:
        lines.append("Findings")
        for issue in issues:
            location = ""
            if issue.path:
                location = f" ({display_path(analysis.project_root, issue.path)}"
                if issue.line:
                    location += f":{issue.line}"
                location += ")"
            lines.append(f"- {issue.severity}: {issue.code}: {issue.message}{location}")
            if issue.hint:
                lines.append(f"  hint: {issue.hint}")
    else:
        lines.append("Findings")
        lines.append("- no issues for this key")

    return "\n".join(lines)


def render_presets(format: str = "text") -> str:
    if format == "json":
        payload = {
            name: {
                key: {
                    "type": spec.type,
                    "required": spec.required,
                    "default": spec.default,
                    "values": spec.values,
                    "description": spec.description,
                    "secret": spec.secret,
                    "public": spec.public,
                }
                for key, spec in specs.items()
            }
            for name, specs in PRESETS.items()
        }
        return json.dumps(payload, indent=2, sort_keys=True)

    lines = ["Available presets:"]
    for name, specs in sorted(PRESETS.items()):
        lines.append(f"- {name}: {', '.join(sorted(specs))}")
    return "\n".join(lines)


def render_inferred_schema(analysis: Analysis) -> str:
    keys = sorted({usage.key for usage in analysis.usages} | (set(analysis.example_file.entries) if analysis.example_file else set()))
    blocks: list[str] = []
    for key in keys:
        example = analysis.example_file.entries.get(key).value if analysis.example_file and key in analysis.example_file.entries else ""
        type_name = infer_type_from_value(key, example)
        blocks.append(f"{key}:")
        blocks.append(f"  type: {type_name}")
        blocks.append("  required: true")
        if example and not is_secret_name(key):
            blocks.append(f"  default: {example}")
        blocks.append("  description: ''")
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def infer_type_name(key: str) -> str:
    upper = key.upper()
    if upper.endswith("URL") or upper.endswith("_URL"):
        return "url"
    if upper in {"PORT"} or upper.endswith("_PORT"):
        return "integer"
    if upper.startswith("IS_") or upper.startswith("HAS_") or upper.endswith("_ENABLED"):
        return "boolean"
    return "string"


def infer_type_from_value(key: str, value: str) -> str:
    if value.lower() in {"true", "false", "yes", "no", "on", "off", "1", "0"}:
        return "boolean"
    if value.isdigit():
        return "integer"
    if key.upper().endswith("URL") or key.upper().endswith("_URL"):
        return "url"
    return infer_type_name(key)


def colorize(text: str, severity: str, enabled: bool) -> str:
    if not enabled:
        return text
    color = {"error": "31", "warning": "33", "info": "36"}.get(severity)
    return f"\033[{color}m{text}\033[0m" if color else text


def escape_github(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A").replace(",", "%2C").replace(":", "%3A")


def escape_markdown(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
