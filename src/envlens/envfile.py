from __future__ import annotations

import re
from pathlib import Path

from .models import DuplicateKey, EnvEntry, EnvFile, ParseProblem

KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def parse_env_file(path: str | Path) -> EnvFile:
    env_path = Path(path)
    parsed = EnvFile(path=env_path, exists=env_path.exists())
    if not env_path.exists():
        return parsed

    seen: dict[str, int] = {}
    for line_no, raw_line in enumerate(env_path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("export "):
            stripped = stripped[7:].strip()

        if "=" not in stripped:
            parsed.problems.append(ParseProblem(env_path, line_no, "expected KEY=value"))
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        if not KEY_RE.match(key):
            parsed.problems.append(ParseProblem(env_path, line_no, f"invalid key name {key!r}"))
            continue

        cleaned_value = clean_value(value.strip())
        if key in seen:
            parsed.duplicates.append(DuplicateKey(key, env_path, seen[key], line_no))
        seen.setdefault(key, line_no)
        parsed.entries[key] = EnvEntry(key=key, value=cleaned_value, path=env_path, line=line_no, raw=raw_line)

    return parsed


def clean_value(value: str) -> str:
    if not value:
        return ""

    quote = value[0]
    if quote in {"'", '"'}:
        end = _find_closing_quote(value, quote)
        if end is not None:
            inner = value[1:end]
            if quote == '"':
                return _unescape_double_quoted(inner)
            return inner
        return value[1:]

    return _strip_inline_comment(value).strip()


def _find_closing_quote(value: str, quote: str) -> int | None:
    escaped = False
    for index, char in enumerate(value[1:], start=1):
        if quote == '"' and char == "\\" and not escaped:
            escaped = True
            continue
        if char == quote and not escaped:
            return index
        escaped = False
    return None


def _unescape_double_quoted(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\r", "\r")
        .replace("\\t", "\t")
        .replace('\\"', '"')
        .replace("\\\\", "\\")
    )


def _strip_inline_comment(value: str) -> str:
    for index, char in enumerate(value):
        if char == "#" and (index == 0 or value[index - 1].isspace()):
            return value[:index]
    return value
