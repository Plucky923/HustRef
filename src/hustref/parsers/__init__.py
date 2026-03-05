"""Input parsers."""

from hustref.models import ReferenceRecord
from hustref.parsers.acm_ref import parse_acm_ref
from hustref.parsers.bibtex import parse_bibtex
from hustref.parsers.endnote import parse_endnote


def parse_input(text: str, source_format: str = "auto") -> list[ReferenceRecord]:
    source = source_format.strip().lower()
    if source == "auto":
        source = detect_source(text)

    if source == "bibtex":
        return parse_bibtex(text)
    if source in {"endnote", "ris"}:
        return parse_endnote(text)
    if source in {"acm_ref", "plain", "text"}:
        return parse_acm_ref(text)
    raise ValueError(f"Unsupported source format: {source_format}")


def detect_source(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("@"):
        return "bibtex"
    if stripped.startswith("%0") or stripped.startswith("%A"):
        return "endnote"
    if "TY  -" in stripped and "ER  -" in stripped:
        return "endnote"
    return "acm_ref"
