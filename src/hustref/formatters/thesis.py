"""Thesis formatter."""

from __future__ import annotations

from hustref.models import ReferenceRecord
from hustref.normalize.authors import format_author_list


def format_thesis(record: ReferenceRecord) -> str:
    authors = format_author_list(record.authors, record.language)
    degree = record.degree or _default_degree(record.language)
    title_block = f"{record.title}: [{degree}]" if degree else record.title

    if record.location and record.institution:
        org_block = f"{record.location}: {record.institution}"
    else:
        org_block = record.institution or record.location

    if record.year:
        org_block = ", ".join(part for part in [org_block, record.year] if part)

    return ". ".join(part for part in [authors, title_block, org_block] if part)


def _default_degree(language: str) -> str:
    if language == "zh":
        return "硕士学位论文"
    return "Master thesis"

