"""Runtime body shared at build time. Each registered entry has one fixed specification."""

import json
import os
from datetime import date
from pathlib import Path


def valid_date(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def reconcile(facts):
    references = []

    def unchecked(reason):
        return {"result": {"status": "unverified", "difference_fen": None,
                           "reason": reason, "references": references}}

    if not isinstance(facts, dict) or set(facts) != set(ROLES):
        return unchecked("missing_or_unexpected_fact")
    rows = [facts[key] for key in ROLES]
    for role, row in zip(ROLES, rows):
        if not isinstance(row, dict) or row.get("role") != role:
            return unchecked("wrong_role")
        for field in ("material_version", "locator", "entity", "scope", "basis"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                return unchecked("missing_context")
        ref = {key: row[key] for key in ("material_version", "locator")}
        if ref in references or row.get("direct") is not True:
            return unchecked("substitute_or_duplicate_fact")
        references.append(ref)
        if row.get("currency") != "CNY" or row.get("unit") != "fen":
            return unchecked("currency_or_unit")
        if type(row.get("amount")) is not int:
            return unchecked("amount_unavailable")
        if type(row.get("precision_fen")) is not int or not 1 <= row["precision_fen"] <= 100:
            return unchecked("precision_insufficient")
        if not valid_date(row.get("end")):
            return unchecked("invalid_period")
    for key in ("entity", "scope", "basis", "end"):
        if any(row[key] != rows[0][key] for row in rows[1:]):
            return unchecked("context_mismatch")
    if CHECK in ("Q02", "Q03"):
        start = rows[0].get("start")
        if not valid_date(start) or start > rows[0]["end"] or any(row.get("start") != start for row in rows):
            return unchecked("period_mismatch")
    if CHECK == "Q02" and rows[0]["scope"] != "consolidated":
        return unchecked("consolidated_required")
    if CHECK == "Q03" and any(row.get("cash_scope") != "cash_and_cash_equivalents" for row in rows):
        return unchecked("cash_scope_mismatch")
    if CHECK == "Q04":
        account = rows[0].get("account")
        if not isinstance(account, str) or not account.strip() or any(
            row.get("account") != account or row.get("measure") != "stock" for row in rows
        ):
            return unchecked("stock_account_mismatch")
    difference = rows[0]["amount"] - sum(row["amount"] for row in rows[1:])
    return {"result": {"status": "unbalanced" if abs(difference) > 100 else "balanced",
                       "difference_fen": difference, "reason": "computed", "references": references}}


if __name__ == "__main__":
    arguments = json.loads((Path(os.environ["SUNMOON_INPUT_DIR"]) / "arguments.json").read_text())
    output = reconcile(arguments.get("facts"))
    (Path(os.environ["SUNMOON_OUTPUT_DIR"]) / "result.json").write_text(json.dumps(output))
