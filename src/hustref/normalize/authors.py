"""Author normalization and formatting utilities."""

from __future__ import annotations

import re

from hustref.constants import CHINESE_ET_AL, ENGLISH_ET_AL, MAX_VISIBLE_AUTHORS
from hustref.models import Author


def normalize_author(author: Author, language: str) -> Author:
    raw = (author.raw or _join_name(author.first_name, author.last_name)).strip()
    if not raw:
        return Author()

    if language == "zh":
        return Author(raw=re.sub(r"\s+", "", raw))

    first_name, last_name = _split_english_name(raw)
    return Author(first_name=first_name, last_name=last_name, raw=raw)


def format_author(author: Author, language: str) -> str:
    if language == "zh":
        return re.sub(r"\s+", "", author.raw)

    if author.first_name or author.last_name:
        first_name = author.first_name
        last_name = author.last_name
    else:
        first_name, last_name = _split_english_name(author.raw)

    initials = _to_initials(first_name)
    if initials and last_name:
        return f"{initials} {last_name}".strip()
    return (author.raw or f"{first_name} {last_name}").strip()


def format_author_list(authors: list[Author], language: str) -> str:
    if not authors:
        return ""

    formatted = []
    for author in authors:
        value = format_author(author, language)
        if value:
            formatted.append(value)
    if len(formatted) <= MAX_VISIBLE_AUTHORS:
        return ", ".join(formatted)

    suffix = CHINESE_ET_AL if language == "zh" else ENGLISH_ET_AL
    return ", ".join(formatted[:MAX_VISIBLE_AUTHORS] + [suffix])


def _split_english_name(raw: str) -> tuple[str, str]:
    name = re.sub(r"\s+", " ", raw.strip())
    if not name:
        return "", ""

    if "," in name:
        last_name, first_name = [item.strip() for item in name.split(",", 1)]
        return first_name, last_name

    tokens = name.split(" ")
    if len(tokens) == 1:
        return "", tokens[0]
    return " ".join(tokens[:-1]), tokens[-1]


def _to_initials(given_names: str) -> str:
    if not given_names:
        return ""
    words = [token for token in given_names.split(" ") if token]
    initials: list[str] = []
    for word in words:
        if "-" in word:
            parts = [item for item in word.split("-") if item]
            initials.append("-".join(f"{part[0].upper()}." for part in parts))
        else:
            initials.append(f"{word[0].upper()}.")
    return " ".join(initials)


def _join_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}".strip()
