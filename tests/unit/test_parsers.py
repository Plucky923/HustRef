from pathlib import Path
import unittest

from hustref.parsers import detect_source, parse_input
from hustref.parsers.bibtex import parse_bibtex
from hustref.parsers.endnote import parse_endnote
from hustref.parsers.endnote import parse_ris


class ParserTests(unittest.TestCase):
    def test_parse_bibtex_article_to_journal(self) -> None:
        bib_text = Path("tests/fixtures/sample.bib").read_text(encoding="utf-8")
        records = parse_bibtex(bib_text)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.type, "journal")
        self.assertTrue(record.title.startswith("Genome-wide atlas"))
        self.assertEqual(len(record.authors), 7)
        self.assertEqual(record.pages, "168--176")
        self.assertEqual(record.issue, "7124")
        self.assertEqual(record.patent_number, "")

    def test_parse_ris_to_journal(self) -> None:
        ris_text = Path("tests/fixtures/sample.ris").read_text(encoding="utf-8")
        records = parse_ris(ris_text)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.type, "journal")
        self.assertEqual(record.year, "2019")
        self.assertEqual(record.pages, "1361-1364")

    def test_parse_endnote_tagged_to_journal(self) -> None:
        tagged_text = Path("tests/fixtures/sample.endnote.txt").read_text(encoding="utf-8")
        records = parse_endnote(tagged_text)

        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.type, "journal")
        self.assertEqual(record.year, "2024")
        self.assertEqual(record.volume, "8")
        self.assertEqual(record.issue, "3")
        self.assertEqual(record.pages, "Article 36")
        self.assertEqual(len(record.authors), 4)

    def test_auto_detect_source(self) -> None:
        bib_text = Path("tests/fixtures/sample.bib").read_text(encoding="utf-8")
        ris_text = Path("tests/fixtures/sample.ris").read_text(encoding="utf-8")
        tagged_text = Path("tests/fixtures/sample.endnote.txt").read_text(encoding="utf-8")
        acm_text = (
            "T. Yao, J. Wan. Building efficient key-value stores. "
            "ACM Transactions on Storage, 2017, 13(4): 1-28"
        )

        self.assertEqual(detect_source(bib_text), "bibtex")
        self.assertEqual(detect_source(ris_text), "endnote")
        self.assertEqual(detect_source(tagged_text), "endnote")
        self.assertEqual(detect_source(acm_text), "acm_ref")

        self.assertEqual(len(parse_input(bib_text, source_format="auto")), 1)
        self.assertEqual(len(parse_input(ris_text, source_format="auto")), 1)
        self.assertEqual(len(parse_input(tagged_text, source_format="auto")), 1)
        self.assertEqual(len(parse_input(acm_text, source_format="auto")), 1)

    def test_parse_bibtex_articleno_as_pages(self) -> None:
        bib_text = """@article{article_no_case,
          author = {John Smith},
          title = {Article number field},
          journal = {Journal of Tests},
          year = {2024},
          volume = {8},
          number = {3},
          articleno = {36}
        }"""
        record = parse_bibtex(bib_text)[0]
        self.assertEqual(record.pages, "Article 36")


if __name__ == "__main__":
    unittest.main()
