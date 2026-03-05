"""Book formatter."""

from __future__ import annotations

from hustref.models import ReferenceRecord
from hustref.normalize.authors import format_author_list


def format_book(record: ReferenceRecord) -> str:
    authors = format_author_list(record.authors, record.language)
    chunks: list[str] = [authors, record.title]

    if record.edition:
        chunks.append(record.edition)
    if record.translator:
        chunks.append(record.translator)

    publication = _book_publication(record)
    if publication:
        chunks.append(publication)
    if record.pages:
        chunks.append(record.pages)

    return ". ".join(chunk for chunk in chunks if chunk)


def _book_publication(record: ReferenceRecord) -> str:
    if record.location and record.publisher and record.year:
        return f"{record.location}: {record.publisher}, {record.year}"
    if record.publisher and record.year:
        return f"{record.publisher}, {record.year}"
    if record.year:
        return record.year
    return ""

