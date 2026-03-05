"""Parser for ACM-style plain text references."""

from __future__ import annotations

import re

from hustref.models import Author, ReferenceRecord

_MAIN_RE = re.compile(r"^(?P<authors>.+?)\.\s+(?P<title>.+?)\.\s+(?P<rest>.+)$")
_ACM_DL_RE = re.compile(
    r"^(?P<authors>.+?)\.\s+(?P<year>(19|20)\d{2})\.\s+(?P<title>.+?)\.\s+"
    r"(?P<rest>.+)$"
)
_JOURNAL_RE = re.compile(
    r"^(?P<journal>.+?),\s*(?P<year>(19|20)\d{2}),\s*"
    r"(?P<volume>\d+)(?:\((?P<issue>[^)]+)\))?\s*:\s*(?P<pages>.+)$"
)
_CONFERENCE_RE = re.compile(
    r"^in:\s*(?P<conference>.+?),\s*(?P<location>.+?),\s*(?P<event_date>[^,]+),\s*"
    r"(?P<publisher>[^,]+),\s*(?P<year>(19|20)\d{2})\s*:\s*(?P<pages>.+)$",
    re.IGNORECASE,
)
_YEAR_RE = re.compile(r"(19|20)\d{2}")
_VOLUME_ISSUE_RE = re.compile(r"^(?P<volume>\d+)\s*,\s*(?P<issue>\d+)\s*,\s*(?P<rest>.+)$")
_ARTICLE_RE = re.compile(r"\bArticle\s+([A-Za-z0-9._-]+)\b", re.IGNORECASE)
_PAGE_RANGE_RE = re.compile(r"\b(\d+\s*[-–—]\s*\d+)\b")
_PAGE_COUNT_RE = re.compile(r"\b(\d+)\s+pages?\b", re.IGNORECASE)


def parse_acm_ref(text: str) -> list[ReferenceRecord]:
    records: list[ReferenceRecord] = []
    for line in [item.strip() for item in text.splitlines() if item.strip()]:
        record = _parse_line(line)
        if record:
            records.append(record)
    return records


def _parse_line(line: str) -> ReferenceRecord | None:
    acm_dl_record = _parse_acm_dl_style(line)
    if acm_dl_record is not None:
        return acm_dl_record

    match = _MAIN_RE.match(line)
    if not match:
        return None

    authors_part = match.group("authors")
    title = match.group("title").strip()
    rest = match.group("rest").strip()

    authors = _parse_authors(authors_part)
    lower_rest = rest.lower()

    if "in:" in lower_rest:
        in_index = lower_rest.index("in:")
        conference_slice = rest[in_index:]
        conference_match = _CONFERENCE_RE.match(conference_slice)
        if conference_match:
            return ReferenceRecord(
                type="conference",
                authors=authors,
                title=title,
                conference_name=conference_match.group("conference").strip(),
                location=conference_match.group("location").strip(),
                event_date=conference_match.group("event_date").strip(),
                publisher=conference_match.group("publisher").strip(),
                year=conference_match.group("year").strip(),
                pages=conference_match.group("pages").strip(),
                raw_source=line,
            )

    journal_match = _JOURNAL_RE.match(rest)
    if journal_match:
        return ReferenceRecord(
            type="journal",
            authors=authors,
            title=title,
            journal_name=journal_match.group("journal").strip(),
            year=journal_match.group("year").strip(),
            volume=journal_match.group("volume").strip(),
            issue=(journal_match.group("issue") or "").strip(),
            pages=journal_match.group("pages").strip(),
            raw_source=line,
        )

    year_match = _YEAR_RE.search(rest)
    return ReferenceRecord(
        type="journal",
        authors=authors,
        title=title,
        journal_name=rest,
        year=year_match.group(0) if year_match else "",
        raw_source=line,
    )


def _parse_authors(authors_part: str) -> list[Author]:
    cleaned = authors_part.replace(" and ", ", ")
    cleaned = cleaned.replace(", and ", ", ")
    parts = [item.strip() for item in cleaned.split(",") if item.strip()]
    return [Author(raw=item) for item in parts]


def _parse_acm_dl_style(line: str) -> ReferenceRecord | None:
    match = _ACM_DL_RE.match(line)
    if not match:
        return None

    authors = _parse_authors(match.group("authors"))
    year = match.group("year").strip()
    title = match.group("title").strip()
    rest = _strip_url(match.group("rest").strip())

    volume = ""
    issue = ""
    pages = ""
    journal_name = ""

    volume_issue_search = re.search(
        r"\b(?P<volume>\d+)\s*,\s*(?P<issue>\d+)\s*,\s*(?P<tail>.+)$",
        rest,
    )
    if volume_issue_search:
        prefix = rest[: volume_issue_search.start()].strip()
        journal_name = _clean_journal_prefix(prefix)
        volume = volume_issue_search.group("volume").strip()
        issue = volume_issue_search.group("issue").strip()
        pages = _extract_pages(volume_issue_search.group("tail").strip())
    else:
        dot_split = rest.split(". ", 1)
        journal_name = _clean_journal_prefix(dot_split[0].strip())
        tail = dot_split[1].strip() if len(dot_split) > 1 else ""
        volume_issue_match = _VOLUME_ISSUE_RE.match(tail)
        if volume_issue_match:
            volume = volume_issue_match.group("volume").strip()
            issue = volume_issue_match.group("issue").strip()
            pages = _extract_pages(volume_issue_match.group("rest").strip())
        else:
            pages = _extract_pages(tail)

    return ReferenceRecord(
        type="journal",
        authors=authors,
        title=title,
        journal_name=journal_name,
        year=year,
        volume=volume,
        issue=issue,
        pages=pages,
        raw_source=line,
    )


def _strip_url(text: str) -> str:
    return re.sub(r"\s+https?://\S+\s*$", "", text).strip().rstrip(".")


def _extract_pages(text: str) -> str:
    article_match = _ARTICLE_RE.search(text)
    if article_match:
        return f"Article {article_match.group(1)}"

    page_range_match = _PAGE_RANGE_RE.search(text)
    if page_range_match:
        return re.sub(r"\s*[-–—]\s*", "-", page_range_match.group(1))

    page_count_match = _PAGE_COUNT_RE.search(text)
    if page_count_match:
        return f"{page_count_match.group(1)} pages"

    return ""


def _clean_journal_prefix(value: str) -> str:
    journal = value.strip()
    if journal.endswith(".") and journal[:-1].count(".") == 0:
        return journal[:-1].strip()
    return journal
