from unittest import TestCase, main

from forecast import calculate as predict
from history_metrics import calculate as history
from report import calculate
from test_forecast import example as forecast_example
from test_history_metrics import example as history_example


class ReportTest(TestCase):
    def test_only_requested_section_and_evidence(self):
        result = calculate(
            {
                "sections": ["history"],
                "history": history({**history_example(), "metric": "gross_margin"}),
            }
        )
        self.assertIn("25%", result["markdown"])
        self.assertIn("历史指标", result["markdown"])
        self.assertNotIn("管理层讨论", result["markdown"])
        self.assertEqual(result["gaps"], [])
        self.assertTrue(all(row["页"] for row in result["evidence"]))

    def test_real_upstream_contracts_and_missing_section(self):
        result = calculate(
            {
                "sections": ["history", "prediction", "discussion"],
                "history": history(history_example()),
                "prediction": predict(forecast_example(loss=True)),
            }
        )
        for text in (
            "减亏5元",
            "百分比：不适用",
            "2025Q2 点值 100 元",
            "2024Q4 同比",
            "回测起点 2024Q3",
        ):
            self.assertIn(text, result["markdown"])
        self.assertIn("管理层讨论核对缺少上游交付", result["gaps"])

    def test_passage(self):
        excerpt = "本期国内销量增长。"
        check = dict(
            status="已核对",
            items=[
                dict(
                    claim_id="x",
                    claim=excerpt,
                    status="支持",
                    reason="范围吻合",
                    quote=excerpt,
                    page=8,
                    report="合成年报",
                )
            ],
        )
        result = calculate(dict(sections=["discussion"], discussion=check))
        self.assertIn("合成年报 第 8 页", result["markdown"])
        self.assertEqual(
            result["evidence"], [dict(quote=excerpt, report="合成年报", page=8)]
        )


if __name__ == "__main__":
    main()
