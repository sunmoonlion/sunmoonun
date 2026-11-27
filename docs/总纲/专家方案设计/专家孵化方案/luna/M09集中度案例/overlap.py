"""仅用披露证据明确标注的主体键，交叉核对两份排名回执。"""

import json
import os
from pathlib import Path


def compare(customer, supplier):
    if customer["side"] != "customer" or supplier["side"] != "supplier":
        raise ValueError("需要一份客户及一份供应商回执")
    if customer["context"] != supplier["context"] or customer["n"] != supplier["n"]:
        raise ValueError("主体、期间、范围、版本、单位或排名范围不一致")
    if customer["n"] != 5:
        raise ValueError("M09 报告需要前五名口径")
    indexes = []
    unresolved = {}
    for receipt in (customer, supplier):
        known = {}
        anonymous = []
        for row in receipt["selected"]:
            identity = row["identity"]
            if identity is None:
                anonymous.append(row["ref"])
                continue
            key = identity["id"]
            if not key.strip() or not identity["ref"].strip() or key in known:
                raise ValueError("身份标注重复或缺少出处")
            known[key] = {"row_ref": row["ref"], "identity_ref": identity["ref"]}
        indexes.append(known)
        unresolved[receipt["side"]] = anonymous
    customers, suppliers = indexes
    matches = [
        {"id": key, "customer": customers[key], "supplier": suppliers[key]}
        for key in customers
        if key in suppliers
    ]
    complete = all(r["status"] == "complete" for r in (customer, supplier))
    return {
        "customer": customer,
        "supplier": supplier,
        "risk_rating": "待定",
        "context": customer["context"],
        "matches": matches,
        "anonymous_refs": unresolved,
        "coverage": "complete"
        if complete and not any(unresolved.values())
        else "partial",
    }


if __name__ == "__main__":
    args = json.loads(
        (Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text()
    )
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(
        json.dumps(
            {"overlap": compare(args["customer"], args["supplier"])}, ensure_ascii=False
        )
    )
