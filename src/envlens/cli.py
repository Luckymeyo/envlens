from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .analyzer import analyze_project
from .config import EnvLensConfig, load_config
from .report import (
    render_docs,
    render_doctor,
    render_github,
    render_inferred_schema,
    render_json,
    render_sarif,
    render_summary,
    render_text,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envlens",
        description="Find missing, stale, unsafe, and mistyped environment variables.",
    )
    parser.add_argument("--version", action="version", version=f"envlens {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    add_check_parser(subparsers)
    add_docs_parser(subparsers)
    add_doctor_parser(subparsers)
    add_init_schema_parser(subparsers)
    return parser


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", default=".", help="Project path to inspect.")
    parser.add_argument("--config", help="Path to pyproject.toml or another TOML config file.")
    parser.add_argument("--env", action="append", dest="env_paths", help="Env file to validate. Can be repeated.")
    parser.add_argument("--example", help="Example env file.")
    parser.add_argument("--schema", help="Typed env schema file.")
    parser.add_argument("--preset", action="append", dest="presets", help="Framework preset to apply. Can be repeated.")
    parser.add_argument("--ignore", action="append", dest="ignore_keys", help="Env key to ignore. Can be repeated.")
    parser.add_argument("--no-scan", action="store_true", default=None, help="Skip source code scanning.")


def add_check_parser(subparsers) -> None:
    parser = subparsers.add_parser("check", help="Validate the environment contract.")
    add_common_args(parser)
    parser.add_argument("--format", choices=["text", "json", "github", "sarif"], help="Output format.")
    parser.add_argument("--strict", action="store_true", default=None, help="Treat warnings as failures.")
    parser.add_argument("--summary", action="store_true", default=None, help="Write a GitHub step summary when possible.")
    parser.add_argument("--summary-file", help="Markdown summary file path. Defaults to GITHUB_STEP_SUMMARY.")


def add_docs_parser(subparsers) -> None:
    parser = subparsers.add_parser("docs", help="Generate a Markdown env variable table.")
    add_common_args(parser)


def add_doctor_parser(subparsers) -> None:
    parser = subparsers.add_parser("doctor", help="Print a remediation plan for environment drift.")
    add_common_args(parser)


def add_init_schema_parser(subparsers) -> None:
    parser = subparsers.add_parser("init-schema", help="Infer a starter env.schema.yml from code and .env.example.")
    add_common_args(parser)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    commands = {"check", "docs", "doctor", "init-schema"}
    if not argv or (argv[0] not in commands and argv[0] not in {"-h", "--help", "--version"}):
        argv = ["check", *argv]

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        config = load_runtime_config(args)
        analysis = load_analysis(args, config)
        output_format = args.format or config.output_format or "text"
        if output_format == "json":
            print(render_json(analysis))
        elif output_format == "github":
            print(render_github(analysis))
        elif output_format == "sarif":
            print(render_sarif(analysis))
        else:
            print(render_text(analysis))

        if should_write_summary(args, config):
            write_summary(args.summary_file or os.environ.get("GITHUB_STEP_SUMMARY"), render_summary(analysis))

        if analysis.error_count:
            return 1
        strict = args.strict if args.strict is not None else bool(config.strict)
        if strict and analysis.warning_count:
            return 1
        return 0

    if args.command == "docs":
        print(render_docs(load_analysis(args, load_runtime_config(args))))
        return 0

    if args.command == "doctor":
        print(render_doctor(load_analysis(args, load_runtime_config(args))))
        return 0

    if args.command == "init-schema":
        print(render_inferred_schema(load_analysis(args, load_runtime_config(args))), end="")
        return 0

    parser.print_help()
    return 2


def load_runtime_config(args) -> EnvLensConfig:
    return load_config(Path(args.path), args.config)


def load_analysis(args, config: EnvLensConfig):
    root = Path(args.path)
    env_paths = args.env_paths if args.env_paths is not None else config.env_paths
    example_path = args.example if args.example is not None else (config.example_path or ".env.example")
    schema_path = args.schema if args.schema is not None else (config.schema_path or "env.schema.yml")
    no_scan = args.no_scan if args.no_scan is not None else bool(config.no_scan)
    presets = [*(config.presets or []), *(args.presets or [])]
    ignore_keys = [*(config.ignore_keys or []), *(args.ignore_keys or [])]
    return analyze_project(
        root,
        env_paths=env_paths,
        example_path=example_path,
        schema_path=schema_path,
        scan_code=not no_scan,
        preset_names=presets,
        ignore_keys=ignore_keys,
    )


def should_write_summary(args, config: EnvLensConfig) -> bool:
    if getattr(args, "summary", None) is not None:
        return bool(args.summary)
    return bool(config.summary)


def write_summary(path: str | None, content: str) -> None:
    if not path:
        return
    with Path(path).open("a", encoding="utf-8") as handle:
        handle.write(content)
        if not content.endswith("\n"):
            handle.write("\n")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
