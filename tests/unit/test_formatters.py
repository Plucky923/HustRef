import unittest

from hustref.formatters import format_reference
from hustref.models import Author, ReferenceRecord
from hustref.normalize.punctuation import post_process_output
from hustref.normalize.record import normalize_record
from hustref.pipeline import convert_text


def _assert_no_trailing_punctuation(testcase: unittest.TestCase, text: str) -> None:
    testcase.assertTrue(text)
    testcase.assertNotIn(text[-1], ".,，。;；:：")


class FormatterTests(unittest.TestCase):
    def test_format_journal_english_example(self) -> None:
        text = """@article{yao2017,
          author = {Tao Yao and Jie Wan and Peilin Huang and Xin He and Feifei Wu and Chao Xie},
          title = {Building efficient key-value stores via a lightweight compaction tree},
          journal = {ACM Transactions on Storage},
          year = {2017},
          volume = {13},
          number = {4},
          pages = {1--28}
        }"""
        output = convert_text(text, source_format="bibtex")[0]
        self.assertIn("ACM Transactions on Storage, 2017, 13(4): 1-28", output)
        _assert_no_trailing_punctuation(self, output)

    def test_format_journal_chinese_example(self) -> None:
        output = convert_text(
            "詹向红, 李德新. 中医药防治阿尔茨海默病实验研究述要. 中华中医药学刊, 2004, 22(11): 2094-2096",
            source_format="acm_ref",
        )[0]
        _assert_no_trailing_punctuation(self, output)
        self.assertIn("中华中医药学刊", output)

    def test_format_book_conference_patent_thesis_no_trailing_punctuation(self) -> None:
        records = [
            ReferenceRecord(
                type="book",
                language="zh",
                authors=[Author(raw="闫明礼"), Author(raw="张东刚")],
                title="CFG桩复合地基技术及工程实践（第二版）",
                location="北京",
                publisher="中国水利水电出版社",
                year="2006",
            ),
            ReferenceRecord(
                type="conference",
                language="en",
                authors=[
                    Author(raw="Y. Shunsuke"),
                    Author(raw="A. Masahide"),
                    Author(raw="K. Masayuki"),
                    Author(raw="M. Yoshizawa"),
                ],
                title="Performance evaluation of phase-only correlation functions",
                conference_name="APSIPA ASC",
                location="Honolulu, HI",
                country="USA",
                event_date="12-15 Nov. 2018",
                publisher="Proceedings of the IEEE",
                year="2019",
                pages="1361-1364",
            ),
            ReferenceRecord(
                type="patent",
                language="zh",
                authors=[Author(raw="刘加林")],
                title="多功能一次性压舌板",
                patent_country="中国",
                patent_kind="[P]",
                patent_number="ZL92214985.2",
                year="1993",
            ),
            ReferenceRecord(
                type="thesis",
                language="zh",
                authors=[Author(raw="李清泉")],
                title="基于混合数据结构的三维GIS数据模型与空间分析研究",
                degree="博士学位论文",
                location="武汉",
                institution="武汉测绘科技大学",
                year="1998",
            ),
        ]

        for record in records:
            output = post_process_output(format_reference(normalize_record(record)))
            _assert_no_trailing_punctuation(self, output)


if __name__ == "__main__":
    unittest.main()

