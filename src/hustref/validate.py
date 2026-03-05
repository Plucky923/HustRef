"""Validation rules for normalized references."""

from __future__ import annotations

from dataclasses import dataclass

from hustref.models import ReferenceRecord

REQUIRED_FIELDS_BY_TYPE: dict[str, tuple[str, ...]] = {
    "book": ("authors", "title", "year"),
    "journal": ("authors", "title", "journal_name", "year"),
    "conference": ("authors", "title", "conference_name", "year"),
    "patent": ("authors", "title", "patent_number", "year"),
    "thesis": ("authors", "title", "institution", "year"),
}


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    code: str
    field: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "level": self.level,
            "code": self.code,
            "field": self.field,
            "message": self.message,
        }


def validate_record(record: ReferenceRecord) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    required_fields = REQUIRED_FIELDS_BY_TYPE.get(record.type)
    if required_fields is None:
        issues.append(
            ValidationIssue(
                level="error",
                code="unsupported_type",
                field="type",
                message=f"Unsupported reference type: {record.type}",
            )
        )
        return issues

    for field in required_fields:
        if not _has_field_value(record, field):
            issues.append(
                ValidationIssue(
                    level="error",
                    code="missing_required_field",
                    field=field,
                    message=f"Missing required field '{field}' for type '{record.type}'",
                )
            )

    if record.type == "patent" and not (record.patent_country or record.country):
        issues.append(
            ValidationIssue(
                level="warning",
                code="missing_patent_country",
                field="patent_country",
                message="Patent country is missing; output may not satisfy HUST format",
            )
        )

    if (
        record.type == "journal"
        and not _is_preprint_journal(record)
        and not record.volume
        and not record.issue
    ):
        issues.append(
            ValidationIssue(
                level="warning",
                code="missing_volume_issue",
                field="volume",
                message="Journal volume/issue is missing; check source completeness",
            )
        )

    return issues


def has_errors(issues: list[ValidationIssue]) -> bool:
    return any(issue.level == "error" for issue in issues)


def _has_field_value(record: ReferenceRecord, field: str) -> bool:
    value = getattr(record, field)
    if field == "authors":
        return bool(value)
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def _is_preprint_journal(record: ReferenceRecord) -> bool:
    name = record.journal_name.strip().lower()
    return name.startswith("arxiv:")
