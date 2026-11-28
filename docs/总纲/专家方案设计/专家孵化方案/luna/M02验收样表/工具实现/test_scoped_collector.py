import json
import unittest
from itertools import combinations
from pathlib import Path

from collect_scoped_checks import collect

SAMPLES = Path(__file__).resolve().parents[1]
REFERENCE = json.loads((SAMPLES / "五粮液普通委托交付.json").read_text())["delivery"][
    "report"
]
PROJECTS = {
    "opening_balance": "资产平表-期初",
    "closing_balance": "资产平表-期末",
    "profit": "利润归属-全年",
    "cash": "现金滚动-全年",
    "inventory": "存货连续性-期初",
}
BY_KEY = {row["项目键"]: row for row in REFERENCE["明细"]}
RECEIPTS = {port: BY_KEY[key] for port, key in PROJECTS.items()}


class ScopedCollectorTest(unittest.TestCase):
    def test_every_nonempty_subset(self):
        for n in range(1, len(PROJECTS) + 1):
            for ports in combinations(PROJECTS, n):
                with self.subTest(ports=ports):
                    scope = {port: PROJECTS[port] for port in reversed(ports)}
                    rows = {port: RECEIPTS[port] for port in ports}
                    out = collect({"scope": scope, **rows})
                    self.assertEqual(
                        {k: v for k, v in out.items() if k != "report"}, rows
                    )
                    self.assertEqual(
                        out["report"],
                        {
                            "应核": n,
                            "实核": n,
                            "阈值内": n,
                            "不平": 0,
                            "未核验": 0,
                            "明细": list(rows.values()),
                            "待补清单": [],
                        },
                    )

    def test_missing_receipt_and_missing_disclosure_are_distinct(self):
        supplied = dict(RECEIPTS)
        del supplied["profit"]
        supplied["cash"] = dict(
            supplied["cash"], 状态="未核验", 差额元=None, 待补=["现金期末行"]
        )
        out = collect({"scope": PROJECTS, **supplied})
        report = out["report"]
        self.assertEqual(
            [report[k] for k in ("应核", "实核", "阈值内", "不平", "未核验")],
            [5, 3, 3, 0, 2],
        )
        self.assertNotIn("profit", out)
        self.assertEqual(out["cash"], supplied["cash"])
        self.assertEqual(report["明细"][2]["缺失回执"], "profit")
        self.assertEqual(
            report["待补清单"],
            [
                {"项目键": PROJECTS["profit"], "待补": ["未收到核验回执"]},
                {"项目键": PROJECTS["cash"], "待补": ["现金期末行"]},
            ],
        )

    def test_pair_keeps_differences_and_evidence_independent(self):
        scope = {k: PROJECTS[k] for k in ("opening_balance", "cash")}
        cash = dict(RECEIPTS["cash"], 差额元="17.00", 状态="不平")
        out = collect(
            {
                "scope": scope,
                "cash": cash,
                "opening_balance": RECEIPTS["opening_balance"],
            }
        )
        self.assertEqual(out["opening_balance"], RECEIPTS["opening_balance"])
        self.assertEqual(out["cash"], cash)
        self.assertEqual(out["report"]["不平"], 1)
        self.assertEqual(out["report"]["应核"], 2)

    def test_five_selected_one_absent(self):
        out = collect(
            {"scope": PROJECTS, **{k: v for k, v in RECEIPTS.items() if k != "cash"}}
        )
        self.assertEqual(
            [out["report"][k] for k in ("应核", "实核", "未核验")], [5, 4, 1]
        )
        self.assertNotIn("cash", out)
        self.assertIsNone(out["report"]["明细"][3]["差额元"])

    def test_rejects_invalid_scope_and_misrouted_receipts(self):
        for arguments in [
            {"scope": {}},
            {"scope": {"unknown": "x"}},
            {"scope": {"profit": ""}},
            {"scope": {"profit": "x", "cash": "x"}},
            {"scope": {"cash": PROJECTS["cash"]}, "profit": RECEIPTS["profit"]},
            {"scope": PROJECTS, "opening_balance": RECEIPTS["closing_balance"]},
            {"scope": PROJECTS, "cash": dict(RECEIPTS["cash"], 工具="Q01")},
            {"scope": PROJECTS, "cash": dict(RECEIPTS["cash"], 差额元=None)},
        ]:
            with self.subTest(keys=list(arguments)), self.assertRaises(ValueError):
                collect(arguments)


if __name__ == "__main__":
    unittest.main()
