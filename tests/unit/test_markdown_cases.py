from pathlib import Path
import unittest

from hustref.pipeline import convert_with_diagnostics
from hustref.testcase_loader import load_markdown_cases


class MarkdownCaseTests(unittest.TestCase):
    def test_test_md_cases_can_be_loaded_and_converted(self) -> None:
        test_file = Path("test.md")
        if not test_file.exists():
            self.skipTest("test.md not found")

        cases = load_markdown_cases(test_file)
        self.assertGreaterEqual(len(cases), 1)

        for case in cases:
            for source, payload in case.inputs.items():
                with self.subTest(case=case.name, source=source):
                    report = convert_with_diagnostics(
                        payload,
                        source_format=source,
                        strict=True,
                    )
                    self.assertGreaterEqual(len(report.entries), 1)
                    self.assertFalse(report.has_errors)
                    self.assertGreaterEqual(len(report.formatted_lines()), 1)
                    for line in report.formatted_lines():
                        self.assertNotIn(line[-1], ".,，。;；:：")
                    if case.expected:
                        self.assertEqual("\n".join(report.formatted_lines()), case.expected)


if __name__ == "__main__":
    unittest.main()
