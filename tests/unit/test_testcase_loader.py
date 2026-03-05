import unittest

from hustref.testcase_loader import parse_markdown_cases


class TestcaseLoaderTests(unittest.TestCase):
    def test_parse_markdown_cases_with_expected_block(self) -> None:
        text = """# Test A
## BibTex
@article{a,
  author = {John Smith},
  title = {T},
  journal = {J},
  year = {2024}
}

## Expected
J. Smith. T. J, 2024
"""
        cases = parse_markdown_cases(text)
        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertEqual(case.name, "Test A")
        self.assertIn("bibtex", case.inputs)
        self.assertEqual(case.expected, "J. Smith. T. J, 2024")


if __name__ == "__main__":
    unittest.main()

