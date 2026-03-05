"""Top-level conversion pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import json

from hustref.formatters import format_reference
from hustref.models import ReferenceRecord
from hustref.normalize import normalize_record
from hustref.normalize.punctuation import post_process_output
from hustref.parsers import parse_input
from hustref.validate import ValidationIssue, has_errors, validate_record


@dataclass(frozen=True)
class ConversionEntry:
    index: int
    record: ReferenceRecord
    output: str
    issues: list[ValidationIssue]
    skipped: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "record": self.record.to_dict(),
            "output": self.output,
            "skipped": self.skipped,
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class ConversionReport:
    entries: list[ConversionEntry]
    strict: bool = False

    @property
    def has_errors(self) -> bool:
        return any(has_errors(entry.issues) for entry in self.entries)

    def formatted_lines(self) -> list[str]:
        return [entry.output for entry in self.entries if entry.output]

    def to_dict(self) -> dict[str, object]:
        return {
            "strict": self.strict,
            "has_errors": self.has_errors,
            "entries": [entry.to_dict() for entry in self.entries],
        }


def convert_text(text: str, source_format: str = "auto") -> list[str]:
    report = convert_with_diagnostics(text, source_format=source_format, strict=False)
    return report.formatted_lines()


def convert_to_json(text: str, source_format: str = "auto") -> str:
    records = parse_input(text, source_format=source_format)
    normalized = [normalize_record(record).to_dict() for record in records]
    return json.dumps(normalized, ensure_ascii=False, indent=2)


def convert_with_diagnostics(
    text: str,
    source_format: str = "auto",
    strict: bool = False,
) -> ConversionReport:
    records = parse_input(text, source_format=source_format)
    entries: list[ConversionEntry] = []

    for index, record in enumerate(records):
        normalized = normalize_record(record)
        issues = validate_record(normalized)
        skip_output = strict and has_errors(issues)

        output = ""
        if not skip_output:
            formatted = format_reference(normalized)
            output = post_process_output(formatted)

        entries.append(
            ConversionEntry(
                index=index,
                record=normalized,
                output=output,
                issues=issues,
                skipped=skip_output,
            )
        )

    return ConversionReport(entries=entries, strict=strict)


def convert_report_to_json(
    text: str,
    source_format: str = "auto",
    strict: bool = False,
) -> str:
    report = convert_with_diagnostics(text, source_format=source_format, strict=strict)
    return json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
