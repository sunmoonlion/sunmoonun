from copy import deepcopy
from unittest import TestCase, main

from history_metrics import calculate
from test_forecast import receipt


def example():
    history = {}
    for year, profit, revenue in [(2023, -10, 100), (2024, -5, 200)]:
        row, checks = receipt(year, 4, profit)
        rows = {}
        for k, name, table, value in [
            ("revenue", "营业收入", "利润表", revenue),
            ("profit", "归属于母公司股东的净利润", "利润表", profit),
            ("cost", "营业成本", "利润表", 150),
            ("cash", "经营活动产生的现金流量净额", "现金流量表", 25),
            ("equity_open", "归母净资产", "资产负债表", 90),
            ("equity_close", "归母净资产", "资产负债表", 110),
        ]:
            rows[k] = {
                **row,
                "行名": name,
                "表名": table,
                "原始金额": str(value),
                "证据编号": f"{year}-{k}",
            }
            if k == "profit":
                rows[k] = checks["明细"][2]["证据"][1]
            elif k.startswith("equity_"):
                rows[k].update(
                    {
                        "起始日期": "",
                        "截止日期": f"{year - int(k == 'equity_open')}-12-31",
                    }
                )
        history[str(year)] = dict(rows=rows, checks=checks)
    return dict(
        annual=deepcopy(history),
        subject=row["主体"],
        scope=row["范围"],
        metric="yoy",
        account="profit",
        end_year=2024,
        comparable_versions=[
            history[y]["rows"]["revenue"]["报告版本"] for y in ("2023", "2024")
        ],
    )


class HistoryTest(TestCase):
    def test_negative_comparison_and_evidence(self):
        result = calculate(example())
        self.assertEqual(
            (result["change_yuan"], result["description"], result["percent"]),
            ("5", "减亏5元", None),
        )
        self.assertEqual(
            [(r["截止日期"], r["原始金额"]) for r in result["evidence"]],
            [("2024-12-31", "-5"), ("2023-12-31", "-10")],
        )

    def test_ratios(self):
        for metric, expected in [
            ("gross_margin", "25"),
            ("net_margin", "-2.5"),
            ("roe", "-5"),
            ("cash_to_profit", "-500"),
        ]:
            self.assertEqual(
                calculate({**example(), "metric": metric})["percent"], expected
            )

    def test_missing_and_bad_rows(self):
        args = example()
        args["annual"]["2024"]["rows"]["revenue"]["原始金额"] = "0"
        self.assertEqual(
            calculate({**args, "metric": "gross_margin"})["status"], "分母不成立"
        )
        args["annual"]["2024"]["rows"]["profit"]["范围"] = "母公司"
        self.assertEqual(calculate(args)["status"], "原行科目、口径或期间不符")

    def test_growth(self):
        args = {**example(), "account": "revenue"}
        self.assertEqual(calculate(args)["percent"], "100")
        self.assertEqual(
            calculate({**args, "metric": "cagr", "start_year": 2023})["percent"], "100"
        )
        self.assertEqual(
            calculate({**args, "comparable_versions": []})["status"], "需确认可比版本链"
        )


if __name__ == "__main__":
    main()
