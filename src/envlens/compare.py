from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .analyzer import is_secret_name, validate_type
from .envfile import parse_env_file
from .models import EnvEntry, EnvFile, EnvSpec, Issue, Schema
from .schema import load_schema


@dataclass
class EnvComparison:
    base: EnvFile
    target: EnvFile
    schema: Schema | None = None
    findings: list[Issue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "info")


def compare_env_files(
    base_path: str | Path,
    target_path: str | Path,
    schema_path: str | Path | None = None,
    show_values: bool = False,
) -> EnvComparison:
    base = parse_env_file(base_path)
    target = parse_env_file(target_path)
    schema = load_schema(schema_path) if schema_path else None
    specs = schema.specs if schema and schema.exists else {}

    comparison = EnvComparison(base=base, target=target, schema=schema)
    findings = comparison.findings
    findings.extend(file_findings(base, "base"))
    findings.extend(file_findings(target, "target"))
    if schema:
        for problem in schema.problems:
            findings.append(
                Issue(
                    severity="error",
                    code="schema-parse-error",
                    message=problem.message,
                    path=problem.path,
                    line=problem.line,
                )
            )

    keys = sorted(set(base.entries) | set(target.entries) | set(specs))
    for key in keys:
        spec = specs.get(key)
        base_entry = base.entries.get(key)
        target_entry = target.entries.get(key)
        required = spec.required if spec else False
        missing_base_required = required and not base_entry
        missing_target_required = required and not target_entry

        if missing_base_required:
            findings.append(missing_required(key, base.path, "base"))
        if missing_target_required:
            findings.append(missing_required(key, target.path, "target"))

        if base_entry and not target_entry:
            if not missing_target_required:
                findings.append(
                    Issue(
                        severity="warning" if required else "info",
                        code="missing-in-target",
                        key=key,
                        message=f"{key} exists in {base.path} but is missing from {target.path}",
                        path=target.path,
                        hint="add it to the target profile or mark it optional in the schema",
                    )
                )
            continue

        if target_entry and not base_entry:
            if not missing_base_required:
                findings.append(
                    Issue(
                        severity="info",
                        code="extra-in-target",
                        key=key,
                        message=f"{key} exists in {target.path} but is missing from {base.path}",
                        path=target.path,
                        line=target_entry.line,
                        hint="keep it if the target profile needs an environment-specific override",
                    )
                )
            continue

        if base_entry and target_entry:
            if spec:
                for entry in (base_entry, target_entry):
                    type_issue = validate_type(entry, spec)
                    if type_issue:
                        findings.append(type_issue)
            if base_entry.value != target_entry.value:
                findings.append(value_drift(base_entry, target_entry, spec, show_values))

    findings.sort(key=finding_sort_key)
    return comparison


def file_findings(env_file: EnvFile, role: str) -> list[Issue]:
    findings: list[Issue] = []
    if not env_file.exists:
        findings.append(
            Issue(
                severity="error",
                code=f"{role}-file-missing",
                message=f"{role} env file does not exist: {env_file.path}",
                path=env_file.path,
            )
        )
        return findings

    for problem in env_file.problems:
        findings.append(
            Issue(
                severity="error",
                code="parse-error",
                message=problem.message,
                path=problem.path,
                line=problem.line,
            )
        )
    for duplicate in env_file.duplicates:
        findings.append(
            Issue(
                severity="warning",
                code="duplicate-key",
                key=duplicate.key,
                message=f"{duplicate.key} is declared more than once in the {role} env file",
                path=duplicate.path,
                line=duplicate.duplicate_line,
                hint=f"first declaration is on line {duplicate.first_line}",
            )
        )
    return findings


def missing_required(key: str, path: Path, role: str) -> Issue:
    return Issue(
        severity="error",
        code=f"missing-required-{role}",
        key=key,
        message=f"{key} is required by schema but missing from the {role} env file",
        path=path,
    )


def value_drift(base_entry: EnvEntry, target_entry: EnvEntry, spec: EnvSpec | None, show_values: bool) -> Issue:
    if show_values and not is_secret_name(base_entry.key, spec):
        detail = f"{base_entry.path.name}={base_entry.value!r}, {target_entry.path.name}={target_entry.value!r}"
    else:
        detail = "values differ"
    return Issue(
        severity="warning",
        code="value-drift",
        key=base_entry.key,
        message=f"{base_entry.key} differs between profiles: {detail}",
        path=target_entry.path,
        line=target_entry.line,
        hint="review whether the difference is intentional for this environment",
    )


def render_compare_text(comparison: EnvComparison) -> str:
    if not comparison.findings:
        return f"No profile drift found between {comparison.base.path.name} and {comparison.target.path.name}."

    lines = [f"envlens compare {comparison.base.path.name} -> {comparison.target.path.name}", ""]
    for finding in comparison.findings:
        location = ""
        if finding.path:
            location = str(finding.path)
            if finding.line:
                location += f":{finding.line}"
        suffix = f" ({location})" if location else ""
        lines.append(f"{finding.severity.upper():<8} {finding.key or '-':<24} {finding.code:<24} {finding.message}{suffix}")
        if finding.hint:
            lines.append(f"{'':8} {'':24} {'hint':<24} {finding.hint}")
    lines.append("")
    lines.append(
        f"{len(comparison.findings)} findings: "
        f"{comparison.error_count} errors, {comparison.warning_count} warnings, {comparison.info_count} info"
    )
    return "\n".join(lines)


def render_compare_json(comparison: EnvComparison) -> str:
    payload = {
        "summary": {
            "findings": len(comparison.findings),
            "errors": comparison.error_count,
            "warnings": comparison.warning_count,
            "info": comparison.info_count,
            "base": str(comparison.base.path),
            "target": str(comparison.target.path),
        },
        "findings": [finding.to_dict() for finding in comparison.findings],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def finding_sort_key(finding: Issue):
    severity_order = {"error": 0, "warning": 1, "info": 2}
    return (
        severity_order.get(finding.severity, 9),
        finding.code,
        finding.key or "",
        str(finding.path or ""),
        finding.line or 0,
    )
