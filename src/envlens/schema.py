from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import EnvSpec, ParseProblem, Schema


def load_schema(path: str | Path | None) -> Schema | None:
    if path is None:
        return None

    schema_path = Path(path)
    schema = Schema(path=schema_path, exists=schema_path.exists())
    if not schema_path.exists():
        return schema

    try:
        text = schema_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        schema.problems.append(ParseProblem(schema_path, 1, f"could not read schema: {exc}"))
        return schema

    try:
        data = json.loads(text) if schema_path.suffix.lower() == ".json" else parse_simple_yaml(text)
    except ValueError as exc:
        schema.problems.append(ParseProblem(schema_path, 1, str(exc)))
        return schema

    if not isinstance(data, dict):
        schema.problems.append(ParseProblem(schema_path, 1, "schema root must be an object"))
        return schema

    for key, raw_spec in data.items():
        if not isinstance(key, str):
            schema.problems.append(ParseProblem(schema_path, 1, "schema keys must be strings"))
            continue
        schema.specs[key] = normalize_spec(key, raw_spec, schema_path)

    return schema


def parse_simple_yaml(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_key: str | None = None

    for line_no, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        line = raw.strip()

        if indent == 0:
            if ":" not in line:
                raise ValueError(f"line {line_no}: expected KEY:")
            key, value = line.split(":", 1)
            current_key = key.strip()
            if not current_key:
                raise ValueError(f"line {line_no}: empty schema key")
            value = value.strip()
            result[current_key] = parse_scalar(value) if value else {}
            continue

        if current_key is None:
            raise ValueError(f"line {line_no}: property without a parent key")
        if indent < 2:
            raise ValueError(f"line {line_no}: nested properties need at least two spaces")
        if ":" not in line:
            raise ValueError(f"line {line_no}: expected property: value")

        prop, value = line.split(":", 1)
        parent = result.setdefault(current_key, {})
        if not isinstance(parent, dict):
            raise ValueError(f"line {line_no}: cannot add properties to scalar {current_key}")
        parent[prop.strip()] = parse_scalar(value.strip())

    return result


def parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "none"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def normalize_spec(key: str, raw_spec: Any, source: Path) -> EnvSpec:
    if raw_spec is None:
        return EnvSpec(key=key, source=source)
    if isinstance(raw_spec, str):
        return EnvSpec(key=key, type=raw_spec, source=source)
    if not isinstance(raw_spec, dict):
        return EnvSpec(key=key, source=source)

    values = raw_spec.get("values", [])
    if isinstance(values, str):
        values = [values]
    values = [str(value) for value in values]

    default = raw_spec.get("default")
    return EnvSpec(
        key=key,
        type=str(raw_spec.get("type", "string")).lower(),
        required=bool(raw_spec.get("required", default is None)),
        default=None if default is None else str(default),
        values=values,
        description=str(raw_spec.get("description", "")),
        secret=_optional_bool(raw_spec.get("secret")),
        public=_optional_bool(raw_spec.get("public")),
        source=source,
    )


def _optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

