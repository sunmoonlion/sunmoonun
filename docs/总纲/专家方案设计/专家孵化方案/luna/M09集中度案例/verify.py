"""以临时目录和独立脚本进程复验合成披露样表。"""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import validate

from drafts import tools


def run(name, args, reject=False):
    _, _, inputs, output, result_slot, _ = tools[name]
    for key, slot in inputs.items():
        validate(args[key], slot["schema"])
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        (folder / "arguments.json").write_text(json.dumps(args))
        proc = subprocess.run(
            [sys.executable, Path(__file__).with_name(name + ".py")],
            capture_output=True,
            check=False,
            env={**os.environ, "SUNMOON_INPUT_DIR": tmp, "SUNMOON_OUTPUT_DIR": tmp},
        )
        if reject:
            assert proc.returncode and not (folder / "result.json").exists(), (
                proc.stderr
            )
            return
        proc.check_returncode()
        result = json.loads((folder / "result.json").read_text())[output]
        validate(result, result_slot["schema"])
        return result


def sample(side, values, total):
    prefix, metric = ("C", "sales") if side == "customer" else ("S", "purchases")
    rows = [
        {
            "rank": i,
            "amount": str(value),
            "ref": prefix + str(i),
            "related": {"confirmed": True, "ref": prefix + "关联注"}
            if i == 1
            else None,
            "identity": {"id": "甲", "ref": prefix + "实名注"} if i == 1 else None,
        }
        for i, value in enumerate(values, 1)
    ]
    return {
        "issuer": "合成甲公司",
        "report": "合成年度披露v1",
        "period": "2025年度",
        "scope": "合并",
        "unit": "人民币元",
        "side": side,
        "n": 5,
        "total": {"metric": metric, "amount": str(total), "ref": prefix + "总额"},
        "ranked_rows": rows,
    }


def verify():
    c = sample("customer", [20, 12, 8, 6, 4], 200)
    s = sample("supplier", [20, 10, 8, 4, 3], 100)
    customer = run("concentration", {"table": c})
    supplier = run("concentration", {"table": s})
    assert (
        customer["sum"],
        customer["top_n_share"],
        supplier["sum"],
        supplier["top_n_share"],
    ) == ("50", "1/4", "45", "9/20")
    assert (
        customer["disclosed_related_share"] == "1/10"
        and supplier["disclosed_related_share"] == "1/5"
    )
    assert customer["unknown_related_refs"] == ["C2", "C3", "C4", "C5"]
    both = run("overlap", {"customer": customer, "supplier": supplier})
    assert (
        both["risk_rating"] == "待定"
        and both["customer"] == customer
        and both["supplier"] == supplier
    )
    assert both["matches"] == [
        {
            "id": "甲",
            "customer": {"row_ref": "C1", "identity_ref": "C实名注"},
            "supplier": {"row_ref": "S1", "identity_ref": "S实名注"},
        }
    ]
    assert both["coverage"] == "partial" and both["anonymous_refs"] == {
        "customer": ["C2", "C3", "C4", "C5"],
        "supplier": ["S2", "S3", "S4", "S5"],
    }
    partial = run("concentration", {"table": sample("customer", [20, 12], 200)})
    assert (partial["count"], partial["top_n_share"], partial["disclosed_share"]) == (
        2,
        None,
        "4/25",
    )
    zero = run("concentration", {"table": sample("customer", [], 0)})
    assert zero["top_n_share"] is None and zero["disclosed_share"] is None
    cutoff = run("concentration", {"table": {**c, "n": 2}})
    assert cutoff["top_n_share"] == "4/25" and len(cutoff["selected"]) == 2
    for field, value in (
        ("rank", 3),
        ("ref", "C1"),
        ("amount", "80"),
        ("identity", c["ranked_rows"][0]["identity"]),
    ):
        bad = copy.deepcopy(c)
        bad["ranked_rows"][1][field] = value
        run("concentration", {"table": bad}, reject=True)
    for update in ({"metric": "purchases"}, {"amount": "49"}):
        run(
            "concentration",
            {"table": {**c, "total": {**c["total"], **update}}},
            reject=True,
        )
    run("overlap", {"customer": customer, "supplier": customer}, reject=True)
    run(
        "overlap",
        {
            "customer": customer,
            "supplier": {
                **supplier,
                "context": {**supplier["context"], "period": "2024年度"},
            },
        },
        reject=True,
    )
    run("overlap", {"customer": cutoff, "supplier": {**supplier, "n": 5}}, reject=True)
    assert (
        run("overlap", {"customer": partial, "supplier": supplier})["coverage"]
        == "partial"
    )
    named = sample("supplier", [20, 10, 8, 4, 3], 100)
    named_buyers = copy.deepcopy(c)
    for label, data in (("采购", named), ("销售", named_buyers)):
        for row in data["ranked_rows"]:
            row["identity"] = {"id": label + str(row["rank"]), "ref": row["ref"] + "注"}
            row["related"] = {"confirmed": False, "ref": row["ref"] + "关联披露"}
    a = run("concentration", {"table": named_buyers})
    b = run("concentration", {"table": named})
    assert b["disclosed_related_share"] == "0/1" and not b["unknown_related_refs"]
    disjoint = run("overlap", {"customer": a, "supplier": b})
    assert disjoint["matches"] == [] and disjoint["coverage"] == "complete"
    anonymous = copy.deepcopy(c)
    for row in anonymous["ranked_rows"]:
        row["related"] = None
    unclassified = run("concentration", {"table": anonymous})
    assert (
        unclassified["disclosed_related_share"] is None
        and len(unclassified["unknown_related_refs"]) == 5
    )
    return {"report": both}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
