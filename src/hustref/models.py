"""Core data models for the parse -> normalize -> format pipeline."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Author:
    first_name: str = ""
    last_name: str = ""
    raw: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ReferenceRecord:
    type: str
    language: str = ""
    authors: list[Author] = field(default_factory=list)
    title: str = ""
    journal_name: str = ""
    conference_name: str = ""
    year: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    publisher: str = ""
    edition: str = ""
    translator: str = ""
    location: str = ""
    country: str = ""
    event_date: str = ""
    patent_country: str = ""
    patent_kind: str = ""
    patent_number: str = ""
    degree: str = ""
    institution: str = ""
    source_key: str = ""
    raw_source: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["authors"] = [author.to_dict() for author in self.authors]
        return payload

