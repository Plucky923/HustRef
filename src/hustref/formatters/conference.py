"""Conference formatter."""

from __future__ import annotations

from hustref.models import ReferenceRecord
from hustref.normalize.authors import format_author_list


def format_conference(record: ReferenceRecord) -> str:
    authors = format_author_list(record.authors, record.language)
    head = ". ".join(part for part in [authors, record.title] if part)

    venue = record.conference_name
    if venue:
        head = f"{head}. in: {venue}"

    location_time = ", ".join(
        part for part in [record.location, record.country, record.event_date] if part
    )
    tail_parts = [location_time, record.publisher, record.year]
    tail = ", ".join(part for part in tail_parts if part)

    if tail:
        head = f"{head}. {tail}"
    if record.pages:
        head = f"{head}: {record.pages}"
    return head

