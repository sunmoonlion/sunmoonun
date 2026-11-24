"""Reproduce a private frozen script and verify its digest before writing to stdout."""

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).parent
TITLES = {
    "F1": "历史财报指标与走势计算",
    "F2": "单季流量还原与原行追溯",
    "F4": "固定季节性两季预测与历史回测",
    "report": "财务分析报告成稿与证据索引",
}


def source(tool):
    def read(name):
        return (ROOT / name).read_text(encoding="utf-8")

    if tool == "F1":
        return "\n".join(
            (
                read("quarter.py").split('if __name__ == "__main__":')[0],
                read("seasonal_rates.py"),
                read("history_metrics.py")
                .replace("from quarter import amount, verified", "")
                .replace("from seasonal_rates import year_on_year, yuan", ""),
            )
        )
    if tool == "F4":
        return (
            read("seasonal_rates.py")
            + "\n"
            + read("forecast.py").replace(
                "from seasonal_rates import forecast_windows, quarter_label, yuan", ""
            )
        )
    return read({"F2": "quarter.py", "report": "report.py"}[tool])


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in TITLES:
        raise SystemExit("用法：python3 registered_source.py F1|F2|F4|report")
    tool = sys.argv[1]
    receipts = json.loads((ROOT / "正式试跑回执.json").read_text(encoding="utf-8"))
    expected = next(
        x["source_digest"] for x in receipts["tools"] if x["title"] == TITLES[tool]
    )
    content = source(tool).encode("utf-8")
    if "sha256:" + hashlib.sha256(content).hexdigest() != expected:
        raise SystemExit("本地实现与冻结来源摘要不同")
    sys.stdout.buffer.write(content)
