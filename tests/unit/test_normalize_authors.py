import unittest

from hustref.models import Author
from hustref.normalize.authors import format_author, format_author_list, normalize_author


class AuthorNormalizeTests(unittest.TestCase):
    def test_hyphenated_english_name_initials(self) -> None:
        author = normalize_author(Author(raw="Jean-Baptiste Poquelin"), language="en")
        self.assertEqual(format_author(author, language="en"), "J.-B. Poquelin")

    def test_english_more_than_six_authors_use_et_al(self) -> None:
        authors = [
            normalize_author(Author(raw=name), language="en")
            for name in [
                "Alice Smith",
                "Bob Jones",
                "Carol White",
                "David Black",
                "Eve Brown",
                "Frank Green",
                "Grace Hall",
            ]
        ]
        result = format_author_list(authors, language="en")
        self.assertTrue(result.endswith("et al"))
        self.assertEqual(result.count(","), 6)

    def test_english_exactly_six_authors_no_et_al(self) -> None:
        authors = [
            normalize_author(Author(raw=name), language="en")
            for name in [
                "Alice Smith",
                "Bob Jones",
                "Carol White",
                "David Black",
                "Eve Brown",
                "Frank Green",
            ]
        ]
        result = format_author_list(authors, language="en")
        self.assertNotIn("et al", result)
        self.assertEqual(result.count(","), 5)

    def test_chinese_more_than_six_authors_use_deng(self) -> None:
        authors = [
            normalize_author(Author(raw=name), language="zh")
            for name in ["张三", "李四", "王五", "赵六", "孙七", "周八", "吴九"]
        ]
        result = format_author_list(authors, language="zh")
        self.assertTrue(result.endswith("等"))
        self.assertEqual(result.count(","), 6)


if __name__ == "__main__":
    unittest.main()
