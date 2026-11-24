from calendar import monthrange
from datetime import date, timedelta
from functools import lru_cache
from unittest import TestCase, main

from forecast import calculate
from quarter import calculate as single_quarter
from quarter_cases import period


def shift_years(value, offset):
    if isinstance(value, dict):
        return {k: shift_years(v, offset) for k, v in value.items()}
    if isinstance(value, list):
        return [shift_years(v, offset) for v in value]
    if isinstance(value, str):
        for year in (2024, 2025):
            value = value.replace(str(year), "year_" + str(year - 2023))
        return value.replace("year_1", str(2024 + offset)).replace(
            "year_2", str(2025 + offset)
        )
    return value


@lru_cache
def receipt(year, quarter, cumulative_profit=None):
    row, report = period(quarter, cumulative_profit)
    return shift_years(row, year - 2025), shift_years(report, year - 2025)


def example(*, loss):
    facts = []
    dates = []
    for year in range(2020, 2025):
        for metric, regular in [("营业收入", 100), ("归母净利润", 10)]:
            previous = None
            total = 0
            for q in range(1, 5):
                single = regular
                if loss and metric == "归母净利润" and q == 4:
                    single = {2023: -10, 2024: -5}.get(year, regular)
                total += single
                reported_profit = 10 * q + (
                    {2023: -20, 2024: -15}.get(year, 0) if loss and q == 4 else 0
                )
                template, checks = receipt(year, q, reported_profit)
                if metric == "归母净利润":
                    template = checks["明细"][2]["证据"][1]
                row = {
                    **template,
                    "行名": metric,
                    "原始金额": str(total),
                    "证据编号": f"{year}-{q}-{metric}",
                }
                args = dict(current=row, current_checks=checks)
                if previous:
                    prior, prior_checks = previous
                    args.update(
                        previous=prior,
                        previous_checks=prior_checks,
                        comparable_versions=[prior["报告版本"], row["报告版本"]],
                    )
                result = single_quarter(args)
                assert result["status"] == "已还原" and result["yuan"] == str(single)
                end = date(year, 3 * q, monthrange(year, 3 * q)[1])
                publication = (end + timedelta(days=21)).isoformat()
                if metric == "营业收入":
                    dates.append(publication)
                facts.append(dict(available_on=publication, delivery=result))
                if metric == "归母净利润":
                    assert row["原始金额"] == template["原始金额"]
                previous = row, checks
    return dict(
        origin="2024Q4",
        as_of=dates[-1],
        backtest_cutoffs=dates[-5:-1],
        subject=row["主体"],
        scope=row["范围"],
        facts=facts,
    )


class ForecastTest(TestCase):
    def test_negative_window_and_four_backtests(self):
        result = calculate(example(loss=True))
        self.assertEqual(result["missing_profit_periods"], ["2024Q4"])
        self.assertEqual(
            (result["profit_point_status"], result["profit_interval_status"]),
            ("窗口缺项", "窗口缺项"),
        )
        self.assertEqual(result["revenue_point_yuan"], "100")
        self.assertEqual(len(result["backtests"]), 4)
        self.assertEqual(
            result["backtests"][-1]["metrics"]["profit"]["actual"]["yuan"], "-5"
        )

    def test_complete_history(self):
        result = calculate(example(loss=False))
        self.assertEqual(result["status"], "已计算")
        self.assertEqual(
            [v["point_yuan"] for v in result["forecast"]["profit"]["targets"]],
            ["10", "10"],
        )

    def test_late_restatement_stays_out_of_earlier_forecast(self):
        args = example(loss=False)
        old = args["facts"][0]
        revised = {**old["delivery"], "yuan": "999"}
        args["facts"].append(dict(available_on=args["as_of"], delivery=revised))
        result = calculate(args)
        self.assertEqual(result["forecast"]["revenue"]["sources"][0]["yuan"], "999")
        for backtest in result["backtests"]:
            self.assertEqual(
                backtest["metrics"]["revenue"]["sources"][0]["yuan"], "100"
            )

    def test_cutoff_that_can_see_actual_is_invalid(self):
        args = example(loss=False)
        args["backtest_cutoffs"][0] = args["backtest_cutoffs"][1]
        with self.assertRaisesRegex(ValueError, "已能看到"):
            calculate(args)


if __name__ == "__main__":
    main()
