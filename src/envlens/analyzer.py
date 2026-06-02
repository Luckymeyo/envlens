from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

from .envfile import parse_env_file
from .models import Analysis, EnvEntry, EnvFile, EnvSpec, EnvUsage, Issue, Schema
from .presets import PRESET_SOURCE, get_preset_specs
from .scanner import scan_project
from .schema import load_schema

SECRET_WORDS = ("SECRET", "TOKEN", "PASSWORD", "PASS", "PRIVATE", "API_KEY", "ACCESS_KEY")
PUBLIC_PREFIXES = ("PUBLIC_", "NEXT_PUBLIC_", "VITE_", "REACT_APP_", "NUXT_PUBLIC_")
PLACEHOLDER_VALUES = {
    "",
    "changeme",
    "change_me",
    "change-me",
    "example",
    "example-value",
    "replace-me",
    "replace_me",
    "todo",
    "none",
    "null",
    "password",
    "password123",
    "secret",
    "token",
    "your-api-key",
    "your_api_key",
}
SECRET_VALUE_RE = re.compile(
    r"(?i)(sk_live_|ghp_|gho_|github_pat_|xox[baprs]-|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]+PRIVATE KEY-----)"
)


def analyze_project(
    project_root: str | Path,
    env_paths: list[str | Path] | None = None,
    example_path: str | Path | None = ".env.example",
    schema_path: str | Path | None = "env.schema.yml",
    scan_code: bool = True,
    preset_names: list[str] | None = None,
    ignore_keys: list[str] | None = None,
) -> Analysis:
    root = Path(project_root).resolve()
    ignored = set(ignore_keys or [])
    env_files = [parse_env_file(resolve_path(root, path)) for path in (env_paths or [".env"])]
    example_file = parse_env_file(resolve_path(root, example_path)) if example_path else None
    schema = merge_preset_specs(load_schema(resolve_path(root, schema_path)) if schema_path else None, preset_names)
    usages = [usage for usage in (scan_project(root) if scan_code else []) if usage.key not in ignored]

    issues: list[Issue] = []
    issues.extend(file_parse_issues(env_files, example_file, schema))
    issues.extend(contract_issues(root, env_files, example_file, schema, usages))
    issues = [issue for issue in issues if issue.key not in ignored]

    return Analysis(
        project_root=root,
        env_files=env_files,
        example_file=example_file,
        schema=schema,
        usages=usages,
        issues=sorted(issues, key=issue_sort_key),
    )


def resolve_path(root: Path, path: str | Path | None) -> Path | None:
    if path is None:
        return None
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    root_candidate = root / candidate
    cwd_candidate = Path.cwd() / candidate
    if root_candidate.exists() or not cwd_candidate.exists():
        return root_candidate
    try:
        cwd_candidate.resolve().relative_to(root.resolve())
        return cwd_candidate
    except ValueError:
        return root_candidate


def merge_preset_specs(schema: Schema | None, preset_names: list[str] | None) -> Schema | None:
    preset_specs = get_preset_specs(preset_names)
    if not preset_specs:
        return schema

    merged = schema or Schema(path=None, exists=True)
    merged.exists = True
    for key, spec in preset_specs.items():
        merged.specs.setdefault(key, spec)
    return merged
    return cwd_candidate


def file_parse_issues(env_files: list[EnvFile], example_file: EnvFile | None, schema) -> list[Issue]:
    issues: list[Issue] = []
    for env_file in [*env_files, *([example_file] if example_file else [])]:
        if env_file is None:
            continue
        for problem in env_file.problems:
            issues.append(
                Issue(
                    severity="error",
                    code="parse-error",
                    message=problem.message,
                    path=problem.path,
                    line=problem.line,
                )
            )
        for duplicate in env_file.duplicates:
            issues.append(
                Issue(
                    severity="warning",
                    code="duplicate-key",
                    key=duplicate.key,
                    message=f"{duplicate.key} is declared more than once",
                    path=duplicate.path,
                    line=duplicate.duplicate_line,
                    hint=f"first declaration is on line {duplicate.first_line}",
                )
            )

    if schema:
        for problem in schema.problems:
            issues.append(
                Issue(
                    severity="error",
                    code="schema-parse-error",
                    message=problem.message,
                    path=problem.path,
                    line=problem.line,
                )
            )
    return issues


def contract_issues(
    root: Path,
    env_files: list[EnvFile],
    example_file: EnvFile | None,
    schema,
    usages: list[EnvUsage],
) -> list[Issue]:
    issues: list[Issue] = []
    usage_by_key = group_usages(usages)
    used_keys = set(usage_by_key)
    example_keys = set(example_file.entries) if example_file and example_file.exists else set()
    schema_specs: dict[str, EnvSpec] = schema.specs if schema and schema.exists else {}
    schema_keys = set(schema_specs)

    contract_keys = example_keys | schema_keys | used_keys

    for env_file in env_files:
        env_keys = set(env_file.entries)
        is_example_env = bool(
            example_file
            and example_file.exists
            and env_file.path.resolve() == example_file.path.resolve()
        )
        if not env_file.exists:
            issues.append(
                Issue(
                    severity="warning",
                    code="env-file-missing",
                    message=f"{display_path(root, env_file.path)} does not exist",
                    path=env_file.path,
                    hint="create it locally or pass --env to validate another file",
                )
            )
            continue

        for key in sorted(contract_keys):
            spec = schema_specs.get(key)
            required = spec.required if spec else key in example_keys
            if required and key not in env_keys:
                issues.append(
                    Issue(
                        severity="error",
                        code="missing-in-env",
                        key=key,
                        message=f"{key} is required but missing from {display_path(root, env_file.path)}",
                        path=env_file.path,
                        hint="add the variable or mark it required: false in env.schema.yml",
                    )
                )

        for key in sorted(env_keys - example_keys - schema_keys):
            entry = env_file.entries[key]
            issues.append(
                Issue(
                    severity="warning",
                    code="undocumented-env",
                    key=key,
                    message=f"{key} exists in {display_path(root, env_file.path)} but is not documented",
                    path=entry.path,
                    line=entry.line,
                    hint="add it to .env.example or env.schema.yml",
                )
            )

        for key, entry in sorted(env_file.entries.items()):
            spec = schema_specs.get(key)
            issues.extend(validate_entry(entry, spec, in_example=is_example_env))

    if example_file and example_file.exists:
        for key in sorted(used_keys - example_keys - schema_keys):
            usage = usage_by_key[key][0]
            issues.append(
                Issue(
                    severity="error",
                    code="missing-in-example",
                    key=key,
                    message=f"{key} is used in {display_path(root, usage.path)} but missing from .env.example",
                    path=usage.path,
                    line=usage.line,
                    hint="add it to .env.example so other developers know it exists",
                )
            )

        for key in sorted(example_keys - used_keys - schema_keys):
            entry = example_file.entries[key]
            issues.append(
                Issue(
                    severity="warning",
                    code="unused-example",
                    key=key,
                    message=f"{key} is listed in .env.example but was not found in scanned code",
                    path=entry.path,
                    line=entry.line,
                    hint="remove it if stale or add it to env.schema.yml if external",
                )
            )

        for key, entry in sorted(example_file.entries.items()):
            spec = schema_specs.get(key)
            issues.extend(validate_entry(entry, spec, in_example=True))

    if schema and schema.exists:
        for key in sorted(used_keys - schema_keys):
            usage = usage_by_key[key][0]
            issues.append(
                Issue(
                    severity="info",
                    code="schema-missing-used",
                    key=key,
                    message=f"{key} is used in code but has no schema entry",
                    path=usage.path,
                    line=usage.line,
                    hint="add type and description metadata to env.schema.yml",
                )
            )

        for key in sorted(schema_keys - used_keys - example_keys):
            spec = schema_specs[key]
            if spec.source == PRESET_SOURCE:
                continue
            issues.append(
                Issue(
                    severity="info",
                    code="schema-unused",
                    key=key,
                    message=f"{key} is in env.schema.yml but was not found in code or .env.example",
                    path=spec.source,
                    hint="keep it if it is consumed outside source scanning",
                )
            )

    issues.extend(case_collision_issues(root, env_files, example_file))
    return issues


def validate_entry(entry: EnvEntry, spec: EnvSpec | None, in_example: bool) -> list[Issue]:
    issues: list[Issue] = []
    secret_like = is_secret_name(entry.key, spec)
    public_like = is_public_name(entry.key, spec)

    if spec and spec.required and entry.value == "":
        issues.append(
            Issue(
                severity="error",
                code="empty-required",
                key=entry.key,
                message=f"{entry.key} is required but has an empty value",
                path=entry.path,
                line=entry.line,
            )
        )

    if spec and entry.value != "":
        type_issue = validate_type(entry, spec)
        if type_issue:
            issues.append(type_issue)

    if public_like and secret_like:
        issues.append(
            Issue(
                severity="warning",
                code="public-secret-name",
                key=entry.key,
                message=f"{entry.key} looks public and secret at the same time",
                path=entry.path,
                line=entry.line,
                hint="public client-side variables should not contain secrets",
            )
        )

    if in_example and secret_like and looks_like_real_secret(entry.value):
        issues.append(
            Issue(
                severity="warning",
                code="secret-in-example",
                key=entry.key,
                message=f"{entry.key} in sample env appears to contain a real secret",
                path=entry.path,
                line=entry.line,
                hint="replace it with a clear placeholder",
            )
        )

    if not in_example and secret_like and weak_secret_value(entry.value):
        issues.append(
            Issue(
                severity="warning",
                code="weak-secret",
                key=entry.key,
                message=f"{entry.key} has a weak placeholder-like value",
                path=entry.path,
                line=entry.line,
            )
        )

    return issues


def validate_type(entry: EnvEntry, spec: EnvSpec) -> Issue | None:
    value = entry.value
    type_name = spec.type

    if type_name in {"string", "str"}:
        return None
    if type_name in {"number", "float"}:
        try:
            float(value)
            return None
        except ValueError:
            return type_mismatch(entry, spec, "expected a number")
    if type_name in {"integer", "int"}:
        try:
            int(value)
            return None
        except ValueError:
            return type_mismatch(entry, spec, "expected an integer")
    if type_name in {"boolean", "bool"}:
        if value.lower() in {"1", "0", "true", "false", "yes", "no", "on", "off"}:
            return None
        return type_mismatch(entry, spec, "expected a boolean")
    if type_name == "url":
        parsed = urlparse(value)
        if parsed.scheme and parsed.netloc:
            return None
        return type_mismatch(entry, spec, "expected a URL with scheme and host")
    if type_name == "email":
        if re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value):
            return None
        return type_mismatch(entry, spec, "expected an email address")
    if type_name == "enum":
        if value in spec.values:
            return None
        return Issue(
            severity="error",
            code="invalid-enum",
            key=entry.key,
            message=f"{entry.key} must be one of: {', '.join(spec.values)}",
            path=entry.path,
            line=entry.line,
        )
    return Issue(
        severity="warning",
        code="unknown-type",
        key=entry.key,
        message=f"{entry.key} uses unknown schema type {type_name!r}",
        path=entry.path,
        line=entry.line,
    )


def type_mismatch(entry: EnvEntry, spec: EnvSpec, detail: str) -> Issue:
    return Issue(
        severity="error",
        code="type-mismatch",
        key=entry.key,
        message=f"{entry.key} has value {entry.value!r}: {detail}",
        path=entry.path,
        line=entry.line,
    )


def group_usages(usages: list[EnvUsage]) -> dict[str, list[EnvUsage]]:
    grouped: dict[str, list[EnvUsage]] = {}
    for usage in usages:
        grouped.setdefault(usage.key, []).append(usage)
    return grouped


def is_secret_name(key: str, spec: EnvSpec | None = None) -> bool:
    if spec and spec.secret is not None:
        return spec.secret
    upper = key.upper()
    return any(word in upper for word in SECRET_WORDS)


def is_public_name(key: str, spec: EnvSpec | None = None) -> bool:
    if spec and spec.public is not None:
        return spec.public
    upper = key.upper()
    return upper.startswith(PUBLIC_PREFIXES)


def weak_secret_value(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered in PLACEHOLDER_VALUES or (0 < len(value) < 12)


def looks_like_real_secret(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False
    if stripped.lower() in PLACEHOLDER_VALUES:
        return False
    if SECRET_VALUE_RE.search(stripped):
        return True
    has_letters = bool(re.search(r"[A-Za-z]", stripped))
    has_numbers = bool(re.search(r"\d", stripped))
    return len(stripped) >= 24 and has_letters and has_numbers


def case_collision_issues(root: Path, env_files: list[EnvFile], example_file: EnvFile | None) -> list[Issue]:
    issues: list[Issue] = []
    files = [*env_files, *([example_file] if example_file else [])]
    for env_file in files:
        if not env_file or not env_file.exists:
            continue
        by_lower: dict[str, list[EnvEntry]] = {}
        for entry in env_file.entries.values():
            by_lower.setdefault(entry.key.lower(), []).append(entry)
        for entries in by_lower.values():
            unique_names = {entry.key for entry in entries}
            if len(unique_names) > 1:
                first = entries[0]
                issues.append(
                    Issue(
                        severity="warning",
                        code="case-collision",
                        key=first.key,
                        message=f"{display_path(root, first.path)} contains keys that differ only by case: {', '.join(sorted(unique_names))}",
                        path=first.path,
                        line=first.line,
                    )
                )
    return issues


def display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def issue_sort_key(issue: Issue):
    severity_order = {"error": 0, "warning": 1, "info": 2}
    return (
        severity_order.get(issue.severity, 9),
        issue.code,
        issue.key or "",
        str(issue.path or ""),
        issue.line or 0,
    )
