"""Assemble only the requested sections from the author's exact upstream deliveries."""

from html import escape
import json
import os
from pathlib import Path

TITLES = {
    "history": "历史指标",
    "quarter": "单季还原",
    "discussion": "管理层讨论核对",
    "prediction": "预测与回测",
}


def plain(value):
    text = escape(" ".join(str(value).splitlines()), quote=False)
    for char in ("\\", "[", "]", "*", "_", "`", "|"):
        text = text.replace(char, "\\" + char)
    return text


def reference_text(item):
    if "报告版本" in item:
        return (
            " · ".join(
                plain(item[k])
                for k in (
                    "主体",
                    "范围",
                    "报告版本",
                    "截止日期",
                    "页",
                    "表名",
                    "行名",
                    "证据编号",
                )
            )
            + " · "
            + plain(item["原始金额"])
            + plain(item["原单位"])
        )
    if "quote" in item:
        return f"{plain(item['report'])} 第 {plain(item['page'])} 页「{plain(item['quote'])}」"
    if "evidence" in item:
        origin = "、".join(
            f"{plain(r['version'])} 第 {plain(r['page'])} 页 {plain(r['row'])}"
            for r in item["evidence"]
        )
        return f"{plain(item.get('period', '实际值'))} · {plain(item['yuan'])} 元 · {plain(item['available_on'])} 可得 · {origin}"
    raise ValueError("无法定位证据")


def calculate(args):
    output = ["# 财务分析报告"]
    evidence = []
    gaps = []
    index = {}

    def cite(item):
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key not in index:
            index[key] = len(evidence) + 1
            evidence.append(item)
        return f"[{index[key]}]"

    def refs(items):
        return " ".join(cite(item) for item in items)

    def note(text):
        gaps.append(text)
        output.append(f"- 待核对：{plain(text)}")

    def money(value):
        return "缺项" if value is None else f"{plain(value)} 元"

    def projected(target):
        bounds = target["interval_yuan"]
        interval = "缺项" if bounds is None else " 至 ".join(money(v) for v in bounds)
        return f"{plain(target['period'])} 点值 {money(target['point_yuan'])}，区间 {interval}"

    for section in args["sections"]:
        title = TITLES[section]
        output.extend(["", f"## {title}"])
        data = args.get(section)
        if data is None:
            note(f"{title}缺少上游交付")
            continue
        output.append(f"- 状态：{plain(data['status'])}")
        if section in ("history", "quarter"):
            if section == "quarter":
                output.append(f"- 金额：{money(data['yuan'])}")
            else:
                if "percent_status" in data:
                    pct = data.get("percent")
                    output.append(
                        f"- 百分比：{plain(pct)}%"
                        if pct is not None
                        else f"- 百分比：{plain(data['percent_status'])}"
                    )
                for key, label in [
                    ("current_yuan", "本期"),
                    ("prior_yuan", "同期"),
                    ("amount_yuan", "金额"),
                    ("change_yuan", "变动额"),
                ]:
                    if key in data:
                        output.append(f"- {label}：{money(data[key])}")
                for key in ("description", "reason"):
                    if data.get(key):
                        output.append(f"- {plain(data[key])}")
            if data.get("formula"):
                output.append(f"- 算式：{plain(data['formula'])}")
            output.append("- 原行：" + refs(data["evidence"]))
            if data["status"] not in ("已计算", "已列示", "已还原", "时点值"):
                note(f"{title}：{data['status']}")
        elif section == "discussion":
            for item in data["items"]:
                output.append(
                    f"- {plain(item['claim'])}　{plain(item['status'])}。{plain(item['reason'])}"
                )
                if item["status"] == "支持":
                    if item["quote"] and item["page"] and item["report"]:
                        output.append(
                            f"  引文「{plain(item['quote'])}」 "
                            + cite({k: item[k] for k in ("report", "page", "quote")})
                        )
                    else:
                        note(f"{item['claim_id']} 缺少支持项引文或页码")
            if data["status"] == "缺资料":
                note("管理层讨论核对缺资料")
        else:
            if "forecast" not in data:
                note(data.get("reason", data["status"]))
                continue
            output.append(
                "点值按上年同季金额乘以一加近四季同比中位数计算。区间取近八季同比的最小值与最大值；区间反映历史变动范围。"
            )
            for metric, label in (("revenue", "营业收入"), ("profit", "归母净利润")):
                part = data["forecast"][metric]
                output.append(
                    f"- {label}：" + "；".join(projected(t) for t in part["targets"])
                )
                for missing in part["missing_ratios"]:
                    note(f"{label} {missing['period']} 同比：{missing['reason']}")
                for target in part["targets"]:
                    if target["base_missing"]:
                        note(f"{label} 缺{target['base_period']}基准金额")
                output.append("  预测依据：" + refs(part["sources"]))
            for test in data["backtests"]:
                output.append(
                    f"- 回测起点 {plain(test['origin'])}，可用资料截至 {plain(test['cutoff'])}"
                )
                for metric, label in (
                    ("revenue", "营业收入"),
                    ("profit", "归母净利润"),
                ):
                    part = test["metrics"][metric]
                    actual = part["actual"]
                    output.append(
                        f"  {label}：{projected(part['prediction'])}，实际 {money(actual['yuan'] if actual else None)}。"
                        + refs(part["sources"])
                        + (" " + cite(actual) if actual else "")
                    )
                    if not actual:
                        note(f"{test['origin']} 回测缺少{label}实际值")
                    for missing in part["missing_ratios"]:
                        note(
                            f"{test['origin']} 回测，{label} {missing['period']} 同比：{missing['reason']}"
                        )
            if data["status"] != "已计算" and not gaps:
                note(f"预测与回测：{data['status']}")
    output.extend(["", "## 证据索引"])
    for n, item in enumerate(evidence, 1):
        output.append(f"- [{n}] " + reference_text(item))
    return dict(markdown="\n".join(output), evidence=evidence, gaps=gaps)


if __name__ == "__main__":
    args = json.loads(
        (Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text()
    )
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps({"result": calculate(args)}, ensure_ascii=False), encoding="utf-8"
    )
