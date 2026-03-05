"""Record-level normalization orchestrator."""

from __future__ import annotations

from dataclasses import replace

from hustref.models import ReferenceRecord
from hustref.normalize.authors import normalize_author
from hustref.normalize.fields import detect_language, normalize_fields


def normalize_record(record: ReferenceRecord) -> ReferenceRecord:
    language = record.language or detect_language(record)
    with_lang = replace(record, language=language)
    with_fields = normalize_fields(with_lang)
    normalized_authors = [
        normalize_author(author, language=with_fields.language)
        for author in with_fields.authors
    ]
    return replace(with_fields, authors=normalized_authors)

