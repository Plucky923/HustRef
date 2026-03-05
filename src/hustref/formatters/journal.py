"""Journal formatter."""

from __future__ import annotations

from hustref.models import ReferenceRecord
from hustref.normalize.authors import format_author_list


def format_journal(record: ReferenceRecord) -> str:
    authors = format_author_list(record.authors, record.language)
    journal_line = ", ".join(part for part in [record.journal_name, record.year] if part)

    volume_issue = record.volume
    if record.issue:
        volume_issue = f"{volume_issue}({record.issue})" if volume_issue else f"({record.issue})"

    if volume_issue:
        journal_line = ", ".join(part for part in [journal_line, volume_issue] if part)

    output = ". ".join(part for part in [authors, record.title, journal_line] if part)
    if record.pages:
        output = f"{output}: {record.pages}"
    return output

