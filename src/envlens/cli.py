from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .analyzer import analyze_project
from .report import render_docs, render_github, render_inferred_schema, render_json, render_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envlens",
        description="Find missing, stale, unsafe, and mistyped environment variables.",
    )
    parser.add_argument("--version", action="version", version=f"envlens {__version__}")

    subparsers = parser.add_subparsers(dest="command")
    add_check_parser(subparsers)
    add_docs_parser(subparsers)
    add_init_schema_parser(subparsers)
    return parser


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", default=".", help="Project path to inspect.")
    parser.add_argument("--env", action="append", dest="env_paths", help="Env file to validate. Can be repeated.")
    parser.add_argument("--example", default=".env.example", help="Example env file.")
    parser.add_argument("--schema", default="env.schema.yml", help="Typed env schema file.")
    parser.add_argument("--no-scan", action="store_true", help="Skip source code scanning.")


def add_check_parser(subparsers) -> None:
    parser = subparsers.add_parser("check", help="Validate the environment contract.")
    add_common_args(parser)
    parser.add_argument("--format", choices=["text", "json", "github"], default="text", help="Output format.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")


def add_docs_parser(subparsers) -> None:
    parser = subparsers.add_parser("docs", help="Generate a Markdown env variable table.")
    add_common_args(parser)


def add_init_schema_parser(subparsers) -> None:
    parser = subparsers.add_parser("init-schema", help="Infer a starter env.schema.yml from code and .env.example.")
    add_common_args(parser)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    commands = {"check", "docs", "init-schema"}
    if not argv or (argv[0] not in commands and argv[0] not in {"-h", "--help", "--version"}):
        argv = ["check", *argv]

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        analysis = load_analysis(args)
        if args.format == "json":
            print(render_json(analysis))
        elif args.format == "github":
            print(render_github(analysis))
        else:
            print(render_text(analysis))

        if analysis.error_count:
            return 1
        if args.strict and analysis.warning_count:
            return 1
        return 0

    if args.command == "docs":
        print(render_docs(load_analysis(args)))
        return 0

    if args.command == "init-schema":
        print(render_inferred_schema(load_analysis(args)), end="")
        return 0

    parser.print_help()
    return 2


def load_analysis(args):
    root = Path(args.path)
    return analyze_project(
        root,
        env_paths=args.env_paths,
        example_path=args.example,
        schema_path=args.schema,
        scan_code=not args.no_scan,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
