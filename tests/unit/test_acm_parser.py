import unittest

from hustref.pipeline import convert_with_diagnostics


class AcmParserTests(unittest.TestCase):
    def test_parse_acm_dl_style_reference(self) -> None:
        text = (
            "Masanori Misono, Dimitrios Stavrakakis, Nuno Santos, and Pramod Bhatotia. "
            "2024. Confidential VMs Explained: An Empirical Analysis of AMD SEV-SNP and Intel TDX. "
            "Proc. ACM Meas. Anal. Comput. Syst. 8, 3, Article 36 (December 2024), 42 pages. "
            "https://doi.org/10.1145/3700418"
        )
        report = convert_with_diagnostics(text, source_format="acm_ref", strict=True)
        self.assertEqual(len(report.entries), 1)
        self.assertFalse(report.has_errors)

        line = report.formatted_lines()[0]
        self.assertIn("Proc. ACM Meas. Anal. Comput. Syst., 2024, 8(3): Article 36", line)
        self.assertNotIn("https: //", line)
        self.assertNotIn("doi. org", line)


if __name__ == "__main__":
    unittest.main()

