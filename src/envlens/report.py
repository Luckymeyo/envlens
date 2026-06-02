from __future__ import annotations

import json
import sys
from .analyzer import display_path, is_secret_name
from .models import Analysis, EnvSpec


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

