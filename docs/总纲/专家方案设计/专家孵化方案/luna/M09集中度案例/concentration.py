"""计算一张已标注的客户或供应商排名表，使用固定金额与证据口径。"""

import json
import os
import re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


def label(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError("缺少有效的披露标识或证据定位")
    return value


def amount(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"(0|[1-9][0-9]{0,19})(\.[0-9]{1,6})?", value
    ):
        raise ValueError("金额须为非负十进制定点字符串")
    return Decimal(value)


def calculate(table):
    side = table["side"]
    metric = {"customer": "sales", "supplier": "purchases"}[side]
    context = {
        key: label(table[key])
        for key in ("issuer", "period", "scope", "unit", "report")
    }
    n = table["n"]
    if type(n) is not int or n < 1:
        raise ValueError("N 必须是正整数")
    total = table["total"]
    if total["metric"] != metric:
        raise ValueError("分母必须是同表销售总额或采购总额")
    denominator = amount(total["amount"])
    total_ref = label(total["ref"])
    rows = table["ranked_rows"]
    if not isinstance(rows, list):
        raise TypeError("需要披露的排名明细")
    seen_refs = {total_ref}
    identities = set()
    previous = None
    disclosed_sum = Decimal(0)
    selected_sum = Decimal(0)
    related_sum = Decimal(0)
    unclassified = []
    selected = []
    for rank, row in enumerate(rows, 1):
        value = amount(row["amount"])
        ref = label(row["ref"])
        if (
            type(row["rank"]) is not int
            or row["rank"] != rank
            or ref in seen_refs
            or (previous is not None and value > previous)
        ):
            raise ValueError("排名必须从第一名连续降序排列，证据不能重复")
        seen_refs.add(ref)
        identity = row.get("identity")
        if identity is not None:
            key = label(identity["id"])
            label(identity["ref"])
            if key in identities:
                raise ValueError("同一主体重复列入排名")
            identities.add(key)
        relation = row["related"]
        if relation is not None:
            if type(relation["confirmed"]) is not bool:
                raise ValueError("关联标注必须取自明确披露")
            label(relation["ref"])
        previous = value
        disclosed_sum += value
        if rank <= n:
            selected_sum += value
            if relation is None:
                unclassified.append(ref)
            elif relation["confirmed"]:
                related_sum += value
            selected.append(
                {
                    "rank": rank,
                    "amount": row["amount"],
                    "ref": ref,
                    "identity": identity,
                    "related": relation,
                }
            )
    if disclosed_sum > denominator:
        raise ValueError("明细超过同口径总额")
    # 精确分数保留原始计算，显示百分比时由展示层舍入。
    share = (
        Fraction(selected_sum) / Fraction(denominator)
        if denominator and selected
        else None
    )
    fraction = None if share is None else f"{share.numerator}/{share.denominator}"
    complete = len(selected) == n and fraction is not None
    related_fraction = (
        Fraction(related_sum) / Fraction(denominator)
        if denominator and len(selected) > len(unclassified)
        else None
    )
    return {
        "related_amount": str(related_sum),
        "unknown_related_refs": unclassified,
        "disclosed_related_share": f"{related_fraction.numerator}/{related_fraction.denominator}"
        if related_fraction is not None
        else None,
        "context": context,
        "side": side,
        "n": n,
        "metric": metric,
        "count": len(selected),
        "status": "complete" if complete else "incomplete",
        "sum": str(selected_sum),
        "total": dict(total),
        "selected": selected,
        "disclosed_share": fraction,
        "top_n_share": fraction if complete else None,
    }


if __name__ == "__main__":
    args = json.loads(
        (Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text()
    )
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps({"receipt": calculate(args["table"])}, ensure_ascii=False)
    )
