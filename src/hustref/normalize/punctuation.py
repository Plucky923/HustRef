"""Output punctuation and spacing cleanup."""

from __future__ import annotations

import re

from hustref.constants import TRAILING_PUNCTUATION


def post_process_output(text: str) -> str:
    value = _normalize_spacing(text)
    return _strip_trailing_punctuation(value)


def _normalize_spacing(text: str) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    value = re.sub(r"\s+,", ",", value)
    value = re.sub(r"\s+\.", ".", value)
    value = re.sub(r"\s+:(?!/)", ":", value)
    value = re.sub(r",\s*", ", ", value)
    value = re.sub(r":(?!/)\s*", ": ", value)
    value = re.sub(r"(?i)\barxiv:\s+(\d)", r"arXiv:\1", value)
    return re.sub(r"\s+", " ", value).strip()


def _strip_trailing_punctuation(text: str) -> str:
    return text.rstrip().rstrip(TRAILING_PUNCTUATION + " ").rstrip()
