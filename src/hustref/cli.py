"""Command-line interface for HustRef."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from hustref.pipeline import convert_report_to_json, convert_text, convert_to_json, convert_with_diagnostics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert references to HUST style.")
    parser.add_argument(
        "--source",
        default="auto",
        choices=["auto", "bibtex", "endnote", "ris", "acm_ref", "plain", "text"],
        help="Input source format.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Path to input file. If omitted, read from stdin.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output normalized JSON instead of formatted text.",
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Output validation diagnostics (missing required fields, warnings).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Skip references with validation errors and return non-zero exit code.",
    )
    return parser


def _read_text(input_path: Path | None) -> str:
    if input_path:
        return input_path.read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    text = _read_text(args.input)

    if args.diagnostics:
        if args.json:
            print(
                convert_report_to_json(
                    text,
                    source_format=args.source,
                    strict=args.strict,
                )
            )
        else:
            report = convert_with_diagnostics(
                text,
                source_format=args.source,
                strict=args.strict,
            )
            if report.formatted_lines():
                print("\n".join(report.formatted_lines()))
            for entry in report.entries:
                for issue in entry.issues:
                    print(
                        f"[{issue.level}] record#{entry.index + 1} field={issue.field}: {issue.message}",
                        file=sys.stderr,
                    )
            if args.strict and report.has_errors:
                return 1
        return 0

    if args.strict:
        report = convert_with_diagnostics(
            text,
            source_format=args.source,
            strict=True,
        )
        if report.formatted_lines():
            print("\n".join(report.formatted_lines()))
        if report.has_errors:
            for entry in report.entries:
                for issue in entry.issues:
                    if issue.level == "error":
                        print(
                            f"[error] record#{entry.index + 1} field={issue.field}: {issue.message}",
                            file=sys.stderr,
                        )
            return 1
        return 0

    if args.json:
        print(convert_to_json(text, source_format=args.source))
        return 0

    lines = convert_text(text, source_format=args.source)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
