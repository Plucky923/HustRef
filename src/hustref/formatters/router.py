"""Formatter router by reference type."""

from __future__ import annotations

from hustref.formatters.book import format_book
from hustref.formatters.conference import format_conference
from hustref.formatters.journal import format_journal
from hustref.formatters.patent import format_patent
from hustref.formatters.thesis import format_thesis
from hustref.models import ReferenceRecord


def format_reference(record: ReferenceRecord) -> str:
    if record.type == "book":
        return format_book(record)
    if record.type == "journal":
        return format_journal(record)
    if record.type == "conference":
        return format_conference(record)
    if record.type == "patent":
        return format_patent(record)
    if record.type == "thesis":
        return format_thesis(record)
    raise ValueError(f"Unsupported reference type: {record.type}")

