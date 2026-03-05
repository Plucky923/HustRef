import unittest

from hustref.webapp import BadRequestError, convert_payload_to_response


class WebAppApiTests(unittest.TestCase):
    def test_convert_payload_success(self) -> None:
        payload = {
            "source": "bibtex",
            "strict": False,
            "text": """@article{ok,
              author = {John Smith},
              title = {A valid title},
              journal = {Journal of Tests},
              year = {2022},
              volume = {1},
              number = {1},
              pages = {10--20}
            }""",
        }
        result = convert_payload_to_response(payload)
        self.assertTrue(result["ok"])
        self.assertEqual(result["summary"]["error_count"], 0)
        self.assertEqual(result["summary"]["record_count"], 1)
        self.assertEqual(len(result["lines"]), 1)

    def test_convert_payload_strict_failure(self) -> None:
        payload = {
            "source": "bibtex",
            "strict": True,
            "text": """@article{missing_year,
              author = {John Smith},
              title = {Missing year},
              journal = {Journal of Tests}
            }""",
        }
        result = convert_payload_to_response(payload)
        self.assertFalse(result["ok"])
        self.assertEqual(result["summary"]["error_count"], 1)
        self.assertTrue(result["entries"][0]["skipped"])

    def test_convert_payload_invalid_source(self) -> None:
        with self.assertRaises(BadRequestError):
            convert_payload_to_response(
                {
                    "source": "unknown",
                    "strict": False,
                    "text": "x",
                }
            )

    def test_convert_payload_requires_text(self) -> None:
        with self.assertRaises(BadRequestError):
            convert_payload_to_response(
                {
                    "source": "auto",
                    "strict": False,
                    "text": "  ",
                }
            )


if __name__ == "__main__":
    unittest.main()

