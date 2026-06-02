from __future__ import annotations

import re
from pathlib import Path

from .models import EnvUsage

ENV_KEY = r"([A-Za-z_][A-Za-z0-9_]*)"

PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "javascript": [
        re.compile(rf"\bprocess\.env\.{ENV_KEY}\b"),
        re.compile(rf"\bprocess\.env\[['\"]{ENV_KEY}['\"]\]"),
        re.compile(rf"\bimport\.meta\.env\.{ENV_KEY}\b"),
        re.compile(rf"\bimport\.meta\.env\[['\"]{ENV_KEY}['\"]\]"),
    ],
    "python": [
        re.compile(rf"\bos\.getenv\(['\"]{ENV_KEY}['\"]"),
        re.compile(rf"\bos\.environ\[['\"]{ENV_KEY}['\"]\]"),
        re.compile(rf"\bos\.environ\.get\(['\"]{ENV_KEY}['\"]"),
    ],
    "go": [
        re.compile(rf"\bos\.Getenv\(['\"]{ENV_KEY}['\"]\)"),
        re.compile(rf"\bos\.LookupEnv\(['\"]{ENV_KEY}['\"]\)"),
    ],
    "ruby": [
        re.compile(rf"\bENV\[['\"]{ENV_KEY}['\"]\]"),
        re.compile(rf"\bENV\.fetch\(['\"]{ENV_KEY}['\"]"),
    ],
    "php": [
        re.compile(rf"\bgetenv\(['\"]{ENV_KEY}['\"]\)"),
        re.compile(rf"\$_ENV\[['\"]{ENV_KEY}['\"]\]"),
        re.compile(rf"\$_SERVER\[['\"]{ENV_KEY}['\"]\]"),
    ],
}

EXTENSIONS: dict[str, str] = {
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".py": "python",
    ".go": "go",
    ".rb": "ruby",
    ".php": "php",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".next",
    ".nuxt",
    ".turbo",
    ".pytest_cache",
}


def scan_project(root: str | Path) -> list[EnvUsage]:
    project_root = Path(root)
    usages: list[EnvUsage] = []
    if not project_root.exists():
        return usages

    for path in _iter_source_files(project_root):
        language = EXTENSIONS.get(path.suffix.lower())
        if not language:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        patterns = PATTERNS[language]
        for line_no, line in enumerate(lines, start=1):
            for pattern in patterns:
                for match in pattern.finditer(line):
                    usages.append(
                        EnvUsage(
                            key=match.group(1),
                            path=path,
                            line=line_no,
                            language=language,
                            expression=match.group(0),
                        )
                    )
    return _dedupe_usages(usages)


def _iter_source_files(root: Path):
    stack = [root]
    while stack:
        current = stack.pop()
        for child in current.iterdir():
            if child.is_dir():
                if child.name not in SKIP_DIRS:
                    stack.append(child)
                continue
            if child.suffix.lower() in EXTENSIONS:
                yield child


def _dedupe_usages(usages: list[EnvUsage]) -> list[EnvUsage]:
    seen: set[tuple[str, Path, int, str]] = set()
    deduped: list[EnvUsage] = []
    for usage in usages:
        fingerprint = (usage.key, usage.path, usage.line, usage.expression)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduped.append(usage)
    return deduped

