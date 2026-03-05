"""Patent formatter."""

from __future__ import annotations

from hustref.models import ReferenceRecord
from hustref.normalize.authors import format_author_list


def format_patent(record: ReferenceRecord) -> str:
    authors = format_author_list(record.authors, record.language)
    tail = ", ".join(
        part
        for part in [
            record.patent_country or record.country,
            record.patent_kind,
            record.patent_number,
            record.year,
        ]
        if part
    )
    return ". ".join(part for part in [authors, record.title, tail] if part)

