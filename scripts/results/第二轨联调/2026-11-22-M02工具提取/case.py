"""Build one fixed script and one independent test suite per M02 rule."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parent
TOOLS = {
    "Q01": (
        "fin_check_balance_sheet",
        "资产负债表平衡",
        ("assets", "liabilities", "equity"),
    ),
    "Q02": (
        "fin_check_profit_attr",
        "净利润归属",
        ("net_profit", "parent_profit", "minority_profit"),
    ),
    "Q03": (
        "fin_check_cash_roll",
        "现金及等价物滚动",
        ("closing_cash", "opening_cash", "net_change"),
    ),
    "Q04": (
        "fin_check_opening_cont",
        "存量期初连续性",
        ("opening_balance", "previous_close"),
    ),
}


def identifier(check, kind):
    return str(uuid5(NAMESPACE_URL, f"sunmoonai/luna/sig-am/M02/v1/{check}/{kind}"))


def source(check):
    roles = TOOLS[check][2]
    return (
        f"CHECK = {check!r}\nROLES = {roles!r}\n" + (ROOT / "reconcile.py").read_text()
    )


def definition(check, registration, destination):
    name, title, roles = TOOLS[check]

    def slot(description, schema):
        return {
            "description": description,
            "schema": schema,
            "meaning": {},
            "required": True,
            "on_missing": "fail",
        }

    impl = {
        k: registration[k] for k in ("kind", "source", "version", "digest", "entry")
    }
    impl["requirement_ids"] = ["run-script"]
    fact_fields = "role、amount（整数分）、currency=CNY、unit=fen、precision_fen、direct、entity、scope、basis、end、material_version、locator"
    return {
        "contract": "knowlab/formal-method/v1",
        "capability_declaration": {
            "title": f"M02 {check} {title}",
            "purpose": f"核对{title}并保留有符号差额",
            "applies_when": ["提供人民币报表行事实及其可比口径"],
            "excludes": ["取数、原文鉴真与预测准入"],
            "promises": {
                "reconcile": "依据作者一元阈值返回平衡、不平或未核验，并交回原因及已核到的行引用"
            },
        },
        "access_requirements": [
            {
                "requirement_id": "run-script",
                "capability_ref": "isolated-script",
                "version": "1",
                "operations": ["execute"],
                "resources": [],
                "required_when": "always",
                "on_unavailable": "pause",
                "data_transfer": {
                    "destination": destination,
                    "argument_fields": ["facts"],
                    "purpose": "在隔离脚本中核对本次传入的事实",
                },
            }
        ],
        "procedure": {
            "kind": "direct",
            "implementation": impl,
            "inputs": {
                "facts": slot(
                    "按 " + ", ".join(roles) + " 键入报表行，字段为 " + fact_fields,
                    {
                        "type": "object",
                        "properties": {r: {"type": "object"} for r in roles},
                    },
                )
            },
            "outputs": {
                "result": slot(
                    "判断状态、带符号差额（分）、原因、来源行",
                    {
                        "type": "object",
                        "required": [
                            "status",
                            "difference_fen",
                            "reason",
                            "references",
                        ],
                        "properties": {
                            "status": {
                                "enum": ["balanced", "unbalanced", "unverified"]
                            },
                            "difference_fen": {"type": ["integer", "null"]},
                            "reason": {"type": "string"},
                            "references": {"type": "array"},
                        },
                    },
                )
            },
            "instructions": f"运行钉版的 {name}.py。按给定顺序用首项减去其余项，绝对差额超过 100 分判不平。",
            "stop_conditions": ["完成一次计算或交回未核验原因"],
            "max_model_turns": 0,
        },
        "how_to_validate": [
            {
                "promise_id": "reconcile",
                "outputs": ["result"],
                "check": "核对独立预期的状态、差额、原因及行引用",
                "evidence": "隔离脚本 result.json",
                "on_failure": "fail",
            }
        ],
        "what_requires_approval": [],
    }


def cases(check):
    roles = TOOLS[check][2]
    facts = {}
    for i, role in enumerate(roles):
        row = {
            "role": role,
            "amount": ([7000, 6000, 1000] if len(roles) == 3 else [7000, 7000])[i],
            "currency": "CNY",
            "unit": "fen",
            "precision_fen": 1,
            "entity": "sample-A",
            "scope": "consolidated",
            "basis": "as-filed",
            "end": "2025-12-31",
            "material_version": "fixture/v1",
            "locator": role,
            "direct": True,
        }
        if check in ("Q02", "Q03"):
            row["start"] = "2025-01-01"
        if check == "Q03":
            row["cash_scope"] = "cash_and_cash_equivalents"
        if check == "Q04":
            row.update(account="inventory", measure="stock")
        facts[role] = row
    refs = [
        {"material_version": row["material_version"], "locator": row["locator"]}
        for row in facts.values()
    ]

    def case(label, supplied, status, diff, reason, seen):
        expected = {
            "status": status,
            "difference_fen": diff,
            "reason": reason,
            "references": seen,
        }
        return {
            "case_id": label,
            "input": {"values": {"facts": supplied}},
            "repetitions": 1,
            "minimum_passes": 1,
            "covers_promises": ["reconcile"],
            "expected": {
                "outcome": "succeeded",
                "assertions": [
                    {"kind": "equals", "pointer": "/result", "value": expected}
                ],
            },
        }

    def edit(index, **fields):
        copy = deepcopy(facts)
        copy[roles[index]].update(fields)
        return copy

    yield case("equal", facts, "balanced", 0, "computed", refs)
    for label, amount, delta, status in (
        ("plus-one", 7100, 100, "balanced"),
        ("minus-one", 6900, -100, "balanced"),
        ("above-one", 7101, 101, "unbalanced"),
        ("below-minus-one", 6899, -101, "unbalanced"),
    ):
        yield case(label, edit(0, amount=amount), status, delta, "computed", refs)
    yield case(
        "missing",
        {roles[0]: facts[roles[0]]},
        "unverified",
        None,
        "missing_or_unexpected_fact",
        [],
    )
    yield case(
        "coarse",
        edit(0, precision_fen=10000),
        "unverified",
        None,
        "precision_insufficient",
        refs[:1],
    )
    yield case(
        "mixed-scope",
        edit(0, scope="standalone"),
        "unverified",
        None,
        "context_mismatch",
        refs,
    )
    yield case(
        "derived",
        edit(1, direct=False),
        "unverified",
        None,
        "substitute_or_duplicate_fact",
        refs[:1],
    )
    field, reason = {
        "Q01": ({"end": "2024-12-31"}, "context_mismatch"),
        "Q02": ({"start": "2025-07-01"}, "period_mismatch"),
        "Q03": ({"cash_scope": "bank_deposits"}, "cash_scope_mismatch"),
        "Q04": ({"measure": "flow"}, "stock_account_mismatch"),
    }[check]
    yield case("specific-scope", edit(1, **field), "unverified", None, reason, refs)


def suite(check):
    return {
        "suite_id": identifier(check, "suite"),
        "version": 1,
        "cases": list(cases(check)),
    }


def verify():
    for check in TOOLS:
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            entry = folder / (TOOLS[check][0] + ".py")
            entry.write_text(source(check))
            for sample in cases(check):
                output = folder / "result.json"
                output.unlink(missing_ok=True)
                (folder / "arguments.json").write_text(
                    json.dumps(sample["input"]["values"])
                )
                subprocess.run(
                    [sys.executable, "-I", str(entry)],
                    env={
                        **os.environ,
                        "SUNMOON_INPUT_DIR": directory,
                        "SUNMOON_OUTPUT_DIR": directory,
                    },
                    check=True,
                )
                assert json.loads(output.read_text()) == {
                    "result": sample["expected"]["assertions"][0]["value"]
                }, sample["case_id"]
            print(
                check,
                len(suite(check)["cases"]),
                hashlib.sha256(entry.read_bytes()).hexdigest(),
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite", choices=TOOLS, help="write the selected FormalTestSuiteDraft as JSON"
    )
    args = parser.parse_args()
    if args.suite:
        print(json.dumps(suite(args.suite), ensure_ascii=False, indent=2))
    else:
        verify()
