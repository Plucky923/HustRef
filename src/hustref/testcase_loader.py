"""Load markdown test cases for regression testing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

SOURCE_ALIASES = {
    "bibtex": "bibtex",
    "bib tex": "bibtex",
    "endnote": "endnote",
    "acmref": "acm_ref",
    "acm ref": "acm_ref",
    "acm_ref": "acm_ref",
    "expected": "__expected__",
    "expect": "__expected__",
    "output": "__expected__",
}


@dataclass(frozen=True)
class MarkdownCase:
    name: str
    inputs: dict[str, str]
    expected: str = ""


def load_markdown_cases(path: str | Path) -> list[MarkdownCase]:
    case_file = Path(path)
    text = case_file.read_text(encoding="utf-8")
    return parse_markdown_cases(text)


def parse_markdown_cases(text: str) -> list[MarkdownCase]:
    heading_re = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
    cases: list[MarkdownCase] = []

    current_name = ""
    current_source = ""
    buffers: dict[str, list[str]] = {}

    def flush_case() -> None:
        nonlocal current_name, current_source, buffers
        if not current_name:
            return

        payload: dict[str, str] = {}
        for source, lines in buffers.items():
            value = "\n".join(lines).strip()
            if value:
                payload[source] = value
        expected = payload.pop("__expected__", "")
        if payload:
            cases.append(MarkdownCase(name=current_name, inputs=payload, expected=expected))

        current_name = ""
        current_source = ""
        buffers = {}

    for line in text.splitlines():
        heading_match = heading_re.match(line)
        if heading_match:
            heading = heading_match.group(1).strip()
            normalized = _normalize_heading(heading)
            source = SOURCE_ALIASES.get(normalized, "")

            if source:
                if current_name:
                    current_source = source
                    buffers.setdefault(source, [])
                continue

            if normalized.startswith("test"):
                flush_case()
                current_name = heading
                current_source = ""
                buffers = {}
                continue

        if current_name and current_source:
            buffers.setdefault(current_source, []).append(line)

    flush_case()
    return cases


def _normalize_heading(value: str) -> str:
    lowered = value.strip().lower()
    lowered = lowered.replace("_", " ")
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered
