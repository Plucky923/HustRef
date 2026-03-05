"""Minimal BibTeX parser for the HustRef pipeline."""

from __future__ import annotations

import re

from hustref.models import Author, ReferenceRecord

_ENTRY_START_RE = re.compile(r"@(?P<entry_type>\w+)\s*\{", re.IGNORECASE)

_TYPE_MAP = {
    "article": "journal",
    "book": "book",
    "inproceedings": "conference",
    "conference": "conference",
    "proceedings": "conference",
    "patent": "patent",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
    "thesis": "thesis",
}


def parse_bibtex(text: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    for entry_type, body in _iter_entries(text):
        citation_key, fields_part = _split_key_and_fields(body)
        fields = _parse_fields(fields_part)
        mapped_type = _TYPE_MAP.get(entry_type.lower(), "journal")
        records.append(_map_fields_to_record(mapped_type, citation_key, fields, body))
    return records


def _iter_entries(text: str):
    index = 0
    while True:
        match = _ENTRY_START_RE.search(text, index)
        if not match:
            return

        entry_type = match.group("entry_type")
        brace_start = match.end() - 1
        brace_depth = 0
        end = brace_start
        while end < len(text):
            char = text[end]
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    break
            end += 1
        body = text[brace_start + 1 : end].strip()
        yield entry_type, body
        index = end + 1


def _split_key_and_fields(body: str) -> tuple[str, str]:
    depth = 0
    in_quotes = False
    for idx, char in enumerate(body):
        if char == '"' and (idx == 0 or body[idx - 1] != "\\"):
            in_quotes = not in_quotes
        if in_quotes:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == "," and depth == 0:
            return body[:idx].strip(), body[idx + 1 :]
    return "", body


def _parse_fields(field_blob: str) -> dict[str, str]:
    segments = _split_top_level_commas(field_blob)
    data: dict[str, str] = {}
    for segment in segments:
        if "=" not in segment:
            continue
        key, value = segment.split("=", 1)
        clean_key = key.strip().lower()
        clean_value = _strip_wrappers(value.strip())
        data[clean_key] = clean_value
    return data


def _split_top_level_commas(text: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0
    in_quotes = False
    for idx, char in enumerate(text):
        if char == '"' and (idx == 0 or text[idx - 1] != "\\"):
            in_quotes = not in_quotes
        if not in_quotes:
            if char == "{":
                depth += 1
            elif char == "}":
                depth = max(depth - 1, 0)
            elif char == "," and depth == 0:
                token = "".join(current).strip()
                if token:
                    items.append(token)
                current = []
                continue
        current.append(char)

    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    return items


def _strip_wrappers(raw: str) -> str:
    value = raw.rstrip(",").strip()
    if len(value) >= 2 and ((value.startswith("{") and value.endswith("}")) or (value.startswith('"') and value.endswith('"'))):
        return value[1:-1].strip()
    return value


def _map_fields_to_record(
    record_type: str,
    source_key: str,
    fields: dict[str, str],
    raw_source: str,
) -> ReferenceRecord:
    author_field = fields.get("author", "")
    authors = [
        Author(raw=item.strip())
        for item in re.split(r"\s+and\s+", author_field)
        if item.strip()
    ]

    patent_number = fields.get("patentnumber", "")
    if record_type == "patent" and not patent_number:
        patent_number = fields.get("number", "")

    patent_kind = fields.get("patentkind", "")
    if record_type == "patent" and not patent_kind:
        patent_kind = fields.get("type", "")

    degree = ""
    if record_type == "thesis":
        degree = fields.get("type", "")

    pages = fields.get("pages", "")
    if not pages and fields.get("articleno", "").strip():
        article_no = fields.get("articleno", "").strip()
        if article_no.lower().startswith("article "):
            pages = article_no
        else:
            pages = f"Article {article_no}"

    return ReferenceRecord(
        type=record_type,
        authors=authors,
        title=fields.get("title", ""),
        journal_name=fields.get("journal", ""),
        conference_name=fields.get("booktitle", ""),
        year=fields.get("year", ""),
        volume=fields.get("volume", ""),
        issue=fields.get("number", ""),
        pages=pages,
        publisher=fields.get("publisher", ""),
        edition=fields.get("edition", ""),
        translator=fields.get("translator", ""),
        location=fields.get("address", ""),
        country=fields.get("country", ""),
        event_date=fields.get("date", ""),
        patent_country=fields.get("country", ""),
        patent_kind=patent_kind,
        patent_number=patent_number,
        degree=degree,
        institution=fields.get("school", fields.get("institution", "")),
        source_key=source_key,
        raw_source=raw_source,
    )
