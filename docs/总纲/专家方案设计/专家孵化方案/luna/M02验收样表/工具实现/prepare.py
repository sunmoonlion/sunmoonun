"""Build the four private implementation sources and independently authored suites."""

import argparse
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from author_cases import M, fixtures, labels, target


def source(kind):
    implementation = (
        Path(__file__).with_name("reconcile.py").read_text(encoding="utf-8")
    )
    return (
        implementation
        + f'''

if __name__ == "__main__":
    import json
    import os
    from pathlib import Path

    data = json.loads((Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text())
    result = reconcile("{kind}", data["target"], data["rows"])
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps({{"check": result}}, ensure_ascii=False), encoding="utf-8"
    )
'''
    )


def local_call(executable, values):
    with TemporaryDirectory() as wd:
        folder = Path(wd)
        (folder / "arguments.json").write_text(json.dumps(values), encoding="utf-8")
        subprocess.run(
            [sys.executable, "-I", str(executable)],
            cwd=wd,
            check=True,
            env={**os.environ, "SUNMOON_INPUT_DIR": wd, "SUNMOON_OUTPUT_DIR": wd},
        )
        return json.loads((folder / "result.json").read_text(encoding="utf-8"))


def verify(folder):
    count = 0
    for kind in labels:
        suite = json.loads((folder / f"{kind}-suite.json").read_text())
        for case in suite["cases"]:
            result = local_call(folder / f"{kind}.py", case["input"]["values"])
            for rule in case["expected"]["assertions"]:
                value = result
                for segment in rule["pointer"].split("/")[1:]:
                    value = (
                        value[int(segment)]
                        if isinstance(value, list)
                        else value[segment]
                    )
                if value != rule["value"]:
                    raise ValueError((kind, case["case_id"], rule["pointer"], value))
            check = result["check"]
            if bool(check["待补"]) != (check["状态"] == "未核验"):
                raise ValueError((kind, case["case_id"], "待补"))
            count += 1
    with (M / "披露行.csv").open() as f:
        facts = list(csv.DictReader(f))
    with (M / "独立期望.csv").open() as f:
        expected = list(csv.DictReader(f))
    checks = {}
    for row in expected:
        kind = row["工具"]
        item = {**target(kind), "项目键": row["清单项"]}
        if kind == "Q01":
            item["时点"] = row["清单项"].split("-")[-1]
        check = local_call(folder / f"{kind}.py", {"target": item, "rows": facts})[
            "check"
        ]
        checks[row["清单项"]] = check
        ids = [fact["证据编号"] for fact in check["证据"]]
        if (
            check["状态"] != row["状态"]
            or (check["差额元"] or "") != row["差额元"]
            or ids != row["操作数证据（算式顺序）"].replace(" 缺项", "").split()
        ):
            raise ValueError((row["清单项"], check))
    collector_inputs = {
        "opening_balance": checks["资产平表-期初"],
        "closing_balance": checks["资产平表-期末"],
        "profit": checks["利润归属-全年"],
        "cash": checks["现金滚动-全年"],
        "inventory": checks["存货连续性-期初"],
    }
    report = local_call(Path(__file__).with_name("collect_checks.py").resolve(), collector_inputs)["report"]
    counts = {key: report[key] for key in ("应核", "实核", "阈值内", "不平", "未核验")}
    if counts != {"应核": 5, "实核": 4, "阈值内": 3, "不平": 1, "未核验": 1}:
        raise ValueError(("汇总", counts))
    if report["明细"] != list(collector_inputs.values()) or report["待补清单"] != [
        {"项目键": "利润归属-全年", "待补": checks["利润归属-全年"]["待补"]}
    ]:
        raise ValueError("汇总丢失明细或待补项目")
    print(f"单工具 {count} 例、混合样表 {len(expected)} 项及最终汇总本地核对通过")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    folder = parser.parse_args().directory.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    for key in labels:
        (folder / f"{key}.py").write_text(source(key), encoding="utf-8")
        (folder / f"{key}-suite.json").write_text(
            json.dumps(fixtures(key), ensure_ascii=False, indent=2), encoding="utf-8"
        )
    verify(folder)
