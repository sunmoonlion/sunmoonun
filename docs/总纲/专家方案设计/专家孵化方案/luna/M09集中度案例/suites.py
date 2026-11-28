"""导出三套 KnowLab 宿主试跑用例，期望值取自手算样表。"""

import argparse
import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from verify import sample


def case(key, inputs, expectations):
    return {
        "case_id": key,
        "input": {"values": inputs},
        "repetitions": 1,
        "minimum_passes": 1,
        "expected": {
            "outcome": "succeeded",
            "assertions": [
                {"kind": "equals", "pointer": path, "value": value}
                for path, value in expectations.items()
            ],
        },
    }


def suites():
    c = sample("customer", [20, 12, 8, 6, 4], 200)
    s = sample("supplier", [20, 10, 8, 4, 3], 100)
    partial = sample("customer", [20, 12], 200)

    # 汇总工具单独试跑时，使用手算的上游回执，避免用待验实现生成自己的期望。
    def receipt(data, total_sum, ratio, related_ratio):
        return {
            "context": {
                k: data[k] for k in ("issuer", "period", "scope", "unit", "report")
            },
            "side": data["side"],
            "n": 5,
            "count": 5,
            "metric": data["total"]["metric"],
            "sum": total_sum,
            "total": data["total"],
            "selected": data["ranked_rows"],
            "status": "complete",
            "disclosed_share": ratio,
            "top_n_share": ratio,
            "related_amount": "20",
            "unknown_related_refs": [row["ref"] for row in data["ranked_rows"][1:]],
            "disclosed_related_share": related_ratio,
        }

    compare = {
        "customer": receipt(c, "50", "1/4", "1/10"),
        "supplier": receipt(s, "45", "9/20", "1/5"),
    }
    checks = {
        "/risk_rating": "待定",
        "/coverage": "partial",
        "/matches/0/id": "甲",
        "/customer/top_n_share": "1/4",
        "/supplier/top_n_share": "9/20",
        "/supplier/disclosed_related_share": "1/5",
        "/matches/0/customer/identity_ref": "C实名注",
        "/anonymous_refs/supplier": ["S2", "S3", "S4", "S5"],
    }
    return {
        "concentration": [
            case(
                "sales",
                {"table": c},
                {"/receipt/top_n_share": "1/4", "/receipt/related_amount": "20"},
            ),
            case(
                "purchases",
                {"table": s},
                {"/receipt/top_n_share": "9/20", "/receipt/metric": "purchases"},
            ),
            case(
                "partial",
                {"table": partial},
                {
                    "/receipt/count": 2,
                    "/receipt/top_n_share": None,
                    "/receipt/disclosed_share": "4/25",
                },
            ),
        ],
        "overlap": [
            case("evidence", compare, {"/overlap" + k: v for k, v in checks.items()})
        ],
        "parent": [
            case(
                "delivery",
                {"customers": c, "suppliers": s},
                {"/report" + k: v for k, v in checks.items()},
            )
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    directory = parser.parse_args().directory
    directory.mkdir(parents=True, exist_ok=True)
    for name, cases in suites().items():
        payload = {
            "suite_id": str(uuid5(NAMESPACE_URL, "sunmoon/luna/m09/v1/" + name)),
            "version": 1,
            "cases": cases,
        }
        (directory / (name + "-suite.json")).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        )
