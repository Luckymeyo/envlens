from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EnvEntry:
    key: str
    value: str
    path: Path
    line: int
    raw: str


@dataclass(frozen=True)
class DuplicateKey:
    key: str
    path: Path
    first_line: int
    duplicate_line: int


@dataclass(frozen=True)
class ParseProblem:
    path: Path
    line: int
    message: str


@dataclass
class EnvFile:
    path: Path
    entries: dict[str, EnvEntry] = field(default_factory=dict)
    duplicates: list[DuplicateKey] = field(default_factory=list)
    problems: list[ParseProblem] = field(default_factory=list)
    exists: bool = True


@dataclass(frozen=True)
class EnvUsage:
    key: str
    path: Path
    line: int
    language: str
    expression: str


@dataclass
class EnvSpec:
    key: str
    type: str = "string"
    required: bool = True
    default: str | None = None
    values: list[str] = field(default_factory=list)
    description: str = ""
    secret: bool | None = None
    public: bool | None = None
    source: Path | None = None


@dataclass
class Schema:
    path: Path | None = None
    specs: dict[str, EnvSpec] = field(default_factory=dict)
    problems: list[ParseProblem] = field(default_factory=list)
    exists: bool = True


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    message: str
    key: str | None = None
    path: Path | None = None
    line: int | None = None
    hint: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "key": self.key,
            "path": str(self.path) if self.path else None,
            "line": self.line,
            "hint": self.hint,
        }


@dataclass
class Analysis:
    project_root: Path
    env_files: list[EnvFile]
    example_file: EnvFile | None
    schema: Schema | None
    usages: list[EnvUsage]
    issues: list[Issue]

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "info")

