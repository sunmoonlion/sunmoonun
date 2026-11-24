from decimal import Decimal
from unittest import TestCase, main

from seasonal_rates import forecast_windows, year_on_year


class NegativeProfitBase(TestCase):
    origin = 2024 * 4 + 3

    def test_loss_reduction(self):
        result = year_on_year(Decimal("-5"), Decimal("-10"), parent_profit=True)
        self.assertEqual(result["change_yuan"], "5")
        self.assertEqual(result["description"], "减亏5元")
        self.assertEqual(result["percent_status"], "不适用")
        self.assertIsNone(result["rate"])

    def test_other_levels_and_zero(self):
        for current, prior, rate in [
            (-12, -10, None),
            (5, -10, None),
            (0, -10, None),
            (5, 0, None),
            (-5, 10, Decimal("-1.5")),
        ]:
            with self.subTest(current=current, prior=prior):
                result = year_on_year(
                    Decimal(current), Decimal(prior), parent_profit=True
                )
                self.assertEqual(result["rate"], rate)

    def test_two_metrics_are_independent(self):
        history = {i: Decimal(10) for i in range(self.origin - 19, self.origin + 1)}
        history.update({self.origin - 4: Decimal(-10), self.origin: Decimal(-5)})
        profit = forecast_windows(history, self.origin, parent_profit=True)
        self.assertEqual(
            profit["missing_ratios"],
            [{"period": "2024Q4", "reason": "同期归母净利润为负"}],
        )
        self.assertEqual(
            (profit["point_status"], profit["interval_status"]),
            ("窗口缺项", "窗口缺项"),
        )
        self.assertEqual(
            [(t["point_yuan"], t["interval_yuan"]) for t in profit["targets"]],
            [(None, None), (None, None)],
        )
        revenue = forecast_windows(
            dict.fromkeys(history, Decimal(100)), self.origin, parent_profit=False
        )
        self.assertEqual(
            [
                (t["period"], t["point_yuan"], t["interval_yuan"])
                for t in revenue["targets"]
            ],
            [("2025Q1", "100", ["100", "100"]), ("2025Q2", "100", ["100", "100"])],
        )

    def test_only_eight_quarter_window_needs_old_ratio(self):
        history = {i: Decimal(10) for i in range(self.origin - 11, self.origin + 1)}
        history[self.origin - 11] = Decimal(-2)
        result = forecast_windows(history, self.origin, parent_profit=True)
        self.assertEqual(result["missing_ratios"][0]["period"], "2023Q1")
        self.assertEqual(result["point_status"], "可算")
        self.assertEqual(result["targets"][0]["point_yuan"], "10")
        self.assertIsNone(result["targets"][0]["interval_yuan"])

    def test_missing_quarter_stays_missing(self):
        history = {i: Decimal(10) for i in range(self.origin - 20, self.origin + 3)}
        del history[self.origin]
        result = forecast_windows(history, self.origin, parent_profit=True)
        self.assertEqual(
            result["missing_ratios"], [{"period": "2024Q4", "reason": "比较期金额缺失"}]
        )
        self.assertIsNone(result["targets"][1]["point_yuan"])


if __name__ == "__main__":
    main()
