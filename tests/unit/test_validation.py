import unittest
import json

from hustref.pipeline import convert_report_to_json, convert_with_diagnostics
from hustref.validate import has_errors


class ValidationTests(unittest.TestCase):
    def test_missing_year_reports_error(self) -> None:
        text = """@article{no_year,
          author = {John Smith},
          title = {A title without year},
          journal = {Journal of Missing Metadata},
          volume = {10},
          number = {2},
          pages = {1--9}
        }"""
        report = convert_with_diagnostics(text, source_format="bibtex", strict=False)
        self.assertEqual(len(report.entries), 1)
        entry = report.entries[0]
        self.assertTrue(has_errors(entry.issues))
        self.assertTrue(any(issue.field == "year" for issue in entry.issues))
        self.assertFalse(entry.skipped)
        self.assertTrue(entry.output)

    def test_strict_mode_skips_invalid_record(self) -> None:
        text = """@article{no_year,
          author = {John Smith},
          title = {A title without year},
          journal = {Journal of Missing Metadata}
        }"""
        report = convert_with_diagnostics(text, source_format="bibtex", strict=True)
        self.assertEqual(len(report.entries), 1)
        entry = report.entries[0]
        self.assertTrue(entry.skipped)
        self.assertEqual(entry.output, "")
        self.assertTrue(report.has_errors)

    def test_strict_mode_keeps_valid_record(self) -> None:
        text = """@article{ok,
          author = {John Smith},
          title = {A valid title},
          journal = {Journal of Tests},
          year = {2022},
          volume = {1},
          number = {1},
          pages = {10--20}
        }"""
        report = convert_with_diagnostics(text, source_format="bibtex", strict=True)
        self.assertEqual(len(report.entries), 1)
        entry = report.entries[0]
        self.assertFalse(entry.skipped)
        self.assertFalse(has_errors(entry.issues))
        self.assertIn("Journal of Tests, 2022, 1(1): 10-20", entry.output)

    def test_convert_report_to_json_includes_issues(self) -> None:
        text = """@article{no_year,
          author = {John Smith},
          title = {A title without year},
          journal = {Journal of Missing Metadata}
        }"""
        payload = json.loads(
            convert_report_to_json(text, source_format="bibtex", strict=True)
        )
        self.assertTrue(payload["has_errors"])
        self.assertTrue(payload["entries"][0]["skipped"])
        self.assertEqual(payload["entries"][0]["issues"][0]["field"], "year")

    def test_arxiv_misc_has_no_journal_missing_error(self) -> None:
        text = """@misc{stolet2025virtuoso,
          title={Virtuoso: High Resource Utilization and {\\mu}s-scale Performance Isolation in a Shared Virtual Machine TCP Network Stack},
          author={Matheus Stolet and Liam Arzola and Simon Peter and Antoine Kaufmann},
          year={2025},
          eprint={2309.14016},
          archivePrefix={arXiv},
          primaryClass={cs.NI},
          url={https://arxiv.org/abs/2309.14016}
        }"""
        report = convert_with_diagnostics(text, source_format="bibtex", strict=True)
        self.assertFalse(report.has_errors)
        self.assertEqual(len(report.entries), 1)
        entry = report.entries[0]
        self.assertEqual(entry.record.journal_name, "arXiv:2309.14016")
        self.assertEqual(entry.record.year, "2025")
        self.assertEqual(entry.issues, [])
        self.assertIn("arXiv:2309.14016, 2025", entry.output)
        self.assertIn("us-scale", entry.output)


if __name__ == "__main__":
    unittest.main()
