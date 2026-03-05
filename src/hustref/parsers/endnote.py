"""EndNote RIS parser."""

from __future__ import annotations

import re

from hustref.models import Author, ReferenceRecord

_TYPE_MAP = {
    "JOUR": "journal",
    "JFULL": "journal",
    "BOOK": "book",
    "CHAP": "book",
    "CONF": "conference",
    "CPAPER": "conference",
    "PAT": "patent",
    "THES": "thesis",
}

_TAGGED_TYPE_MAP = {
    "journal article": "journal",
    "book": "book",
    "book section": "book",
    "conference paper": "conference",
    "conference proceedings": "conference",
    "patent": "patent",
    "thesis": "thesis",
    "doctoral dissertation": "thesis",
    "masters thesis": "thesis",
    "master's thesis": "thesis",
}

_TAGGED_LINE_RE = re.compile(r"^%([A-Za-z0-9])\s*(.*)$")


def parse_endnote(text: str) -> list[ReferenceRecord]:
    if _looks_like_tagged_format(text):
        return parse_endnote_tagged(text)
    return parse_ris(text)


def parse_ris(text: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    current: dict[str, list[str]] = {}

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        if re.match(r"^[A-Z0-9]{2}\s{2}-\s", line):
            tag = line[:2]
            value = line[6:].strip()
            current.setdefault(tag, []).append(value)
            if tag == "ER":
                records.append(_map_ris_record(current))
                current = {}
            continue

        # Continuation line, append to the last active field if any.
        if current:
            last_tag = next(reversed(current))
            if current[last_tag]:
                current[last_tag][-1] = f"{current[last_tag][-1]} {line.strip()}".strip()

    if current:
        records.append(_map_ris_record(current))
    return records


def parse_endnote_tagged(text: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    current: dict[str, list[str]] = {}

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue

        match = _TAGGED_LINE_RE.match(line)
        if not match:
            if current:
                last_tag = next(reversed(current))
                if current[last_tag]:
                    current[last_tag][-1] = f"{current[last_tag][-1]} {line.strip()}".strip()
            continue

        tag = match.group(1)
        value = match.group(2).strip()

        # A new %0 record starts a new entry.
        if tag == "0" and current:
            records.append(_map_endnote_tagged_record(current))
            current = {}

        current.setdefault(tag, []).append(value)

    if current:
        records.append(_map_endnote_tagged_record(current))
    return records


def _first(data: dict[str, list[str]], *keys: str) -> str:
    for key in keys:
        values = data.get(key)
        if values:
            return values[0]
    return ""


def _first_tagged(data: dict[str, list[str]], *keys: str) -> str:
    for key in keys:
        values = data.get(key)
        if values:
            return values[0]
    return ""


def _map_ris_record(data: dict[str, list[str]]) -> ReferenceRecord:
    ris_type = _first(data, "TY").upper()
    mapped_type = _TYPE_MAP.get(ris_type, "journal")

    authors_raw = data.get("AU", []) + data.get("A1", [])
    authors = [Author(raw=raw.strip()) for raw in authors_raw if raw.strip()]

    start_page = _first(data, "SP")
    end_page = _first(data, "EP")
    pages = ""
    if start_page and end_page:
        pages = f"{start_page}-{end_page}"
    elif start_page:
        pages = start_page

    year_text = _first(data, "PY", "Y1")
    year_match = re.search(r"(19|20)\d{2}", year_text)

    return ReferenceRecord(
        type=mapped_type,
        authors=authors,
        title=_first(data, "TI", "T1"),
        journal_name=_first(data, "JO", "JF"),
        conference_name=_first(data, "T2", "BT"),
        year=year_match.group(0) if year_match else year_text,
        volume=_first(data, "VL"),
        issue=_first(data, "IS"),
        pages=pages,
        publisher=_first(data, "PB"),
        edition=_first(data, "ET"),
        location=_first(data, "CY"),
        country=_first(data, "PP"),
        patent_country=_first(data, "CY", "PP"),
        patent_kind=_first(data, "M3"),
        patent_number=_first(data, "CN"),
        degree=_first(data, "M3"),
        institution=_first(data, "PB", "IN"),
        raw_source="\n".join(
            f"{tag}  - {value}" for tag, values in data.items() for value in values
        ),
    )


def _map_endnote_tagged_record(data: dict[str, list[str]]) -> ReferenceRecord:
    record_type_raw = _first_tagged(data, "0")
    mapped_type = _TAGGED_TYPE_MAP.get(record_type_raw.lower(), "journal")

    authors = [Author(raw=raw.strip()) for raw in data.get("A", []) if raw.strip()]
    year_text = _first_tagged(data, "D")
    year_match = re.search(r"(19|20)\d{2}", year_text)
    year = year_match.group(0) if year_match else year_text

    degree = ""
    if mapped_type == "thesis":
        lowered = record_type_raw.lower()
        if "doctoral" in lowered or "phd" in lowered:
            degree = "博士学位论文"
        elif "master" in lowered:
            degree = "硕士学位论文"

    return ReferenceRecord(
        type=mapped_type,
        authors=authors,
        title=_first_tagged(data, "T"),
        journal_name=_first_tagged(data, "J"),
        conference_name=_first_tagged(data, "B"),
        year=year,
        volume=_first_tagged(data, "V"),
        issue=_first_tagged(data, "N"),
        pages=_first_tagged(data, "P"),
        publisher=_first_tagged(data, "I"),
        location=_first_tagged(data, "C"),
        patent_number=_first_tagged(data, "M"),
        degree=degree,
        institution=_first_tagged(data, "I"),
        raw_source="\n".join(
            f"%{tag} {value}" for tag, values in data.items() for value in values
        ),
    )


def _looks_like_tagged_format(text: str) -> bool:
    return bool(re.search(r"(?m)^%[A-Za-z0-9]\s", text))
