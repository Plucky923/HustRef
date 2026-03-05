"""Project-wide constants."""

import re

SUPPORTED_TYPES = {"book", "journal", "conference", "patent", "thesis"}
MAX_VISIBLE_AUTHORS = 6
CHINESE_ET_AL = "等"
ENGLISH_ET_AL = "et al"
TRAILING_PUNCTUATION = ".,，。;；:："
CHINESE_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")
PAGE_RANGE_RE = re.compile(r"\s*[-–—]{1,2}\s*")

