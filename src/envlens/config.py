from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    tomllib = None


@dataclass
class EnvLensConfig:
    env_paths: list[str] | None = None
    example_path: str | None = None
    schema_path: str | None = None
    presets: list[str] = field(default_factory=list)
    ignore_keys: list[str] = field(default_factory=list)
    output_format: str | None = None
    strict: bool | None = None
    no_scan: bool | None = None
    summary: bool | None = None


def load_config(project_root: str | Path, config_path: str | Path | None = None) -> EnvLensConfig:
    root = Path(project_root).resolve()
    path = Path(config_path) if config_path else root / "pyproject.toml"
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    if not path.exists():
        return EnvLensConfig()

    data = _load_toml(path)
    raw = data.get("tool", {}).get("envlens", {})
    if not isinstance(raw, dict):
        return EnvLensConfig()

    env_paths = _string_list(raw.get("env_paths", raw.get("env")))
    presets = _string_list(raw.get("presets", raw.get("preset"))) or []
    ignore_keys = _string_list(raw.get("ignore_keys", raw.get("ignore"))) or []

    return EnvLensConfig(
        env_paths=env_paths,
        example_path=_optional_string(raw.get("example", raw.get("example_path"))),
        schema_path=_optional_string(raw.get("schema", raw.get("schema_path"))),
        presets=presets,
        ignore_keys=ignore_keys,
        output_format=_optional_string(raw.get("format", raw.get("output_format"))),
        strict=_optional_bool(raw.get("strict")),
        no_scan=_optional_bool(raw.get("no_scan")),
        summary=_optional_bool(raw.get("summary")),
    )


def _load_toml(path: Path) -> dict[str, Any]:
    if tomllib is not None:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    return _parse_minimal_toml(path.read_text(encoding="utf-8-sig"))


def _parse_minimal_toml(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current: dict[str, Any] = data
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = data
            for part in line[1:-1].split("."):
                current = current.setdefault(part.strip(), {})
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        current[key.strip()] = _parse_toml_scalar(value.strip())
    return data


def _parse_toml_scalar(value: str) -> Any:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_toml_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _string_list(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]

