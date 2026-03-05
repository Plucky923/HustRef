"""Field-level normalization."""

from __future__ import annotations

import re
from dataclasses import replace

from hustref.constants import CHINESE_CHAR_RE, PAGE_RANGE_RE
from hustref.models import ReferenceRecord


def detect_language(record: ReferenceRecord) -> str:
    probes = [record.title, " ".join(author.raw for author in record.authors)]
    if any(CHINESE_CHAR_RE.search(text or "") for text in probes):
        return "zh"
    return "en"


def normalize_fields(record: ReferenceRecord) -> ReferenceRecord:
    data = record.to_dict()
    cleaned: dict[str, object] = {}
    for key, value in data.items():
        if key == "authors":
            cleaned[key] = record.authors
            continue
        if isinstance(value, str):
            cleaned[key] = _collapse_whitespace(_normalize_markup(value))
        else:
            cleaned[key] = value

    year = cleaned.get("year", "")
    if isinstance(year, str):
        year_match = re.search(r"(19|20)\d{2}", year)
        cleaned["year"] = year_match.group(0) if year_match else year

    pages = cleaned.get("pages", "")
    if isinstance(pages, str):
        cleaned["pages"] = PAGE_RANGE_RE.sub("-", pages).strip("- ")

    return replace(record, **cleaned)


def _collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_markup(value: str) -> str:
    normalized = value
    normalized = re.sub(r"\{\\mu\}\s*s", "us", normalized)
    normalized = re.sub(r"\\mu\s*s", "us", normalized)
    normalized = re.sub(r"\{\\mu\}", "mu", normalized)
    normalized = re.sub(r"\\mu\b", "mu", normalized)
    normalized = normalized.replace("{", "").replace("}", "")
    return normalized
