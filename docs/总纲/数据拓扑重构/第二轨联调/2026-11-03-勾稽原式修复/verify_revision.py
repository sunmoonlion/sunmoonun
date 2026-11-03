"""Exercise compiled author rules through the real runtime judge with synthetic facts.

No model, database or data-provider call. Supply a preview/published manifest path.
"""

import asyncio
import copy
import json
import sys
from pathlib import Path

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import judge_numbers
from app.domain.workbench.packs import AcceptanceRule

FORMULAS = {
    "balance": ("A-(L+E)", {"A": 10, "L": 3, "E": 7}),
    "profit": ("NP-(P+M)", {"NP": 10, "P": 8, "M": 2}),
    "cash": ("END-(BEGIN+CHANGE)", {"END": 10, "BEGIN": 7, "CHANGE": 3}),
    "continuity": ("OPEN-PREV_CLOSE", {"OPEN": 10, "PREV_CLOSE": 10}),
}


async def main():
    manifest = json.loads(Path(sys.argv[1]).read_text())
    if "manifest" in manifest:
        manifest = manifest["manifest"]
    workflow = {s["step_id"]: s for s in manifest["pack"]["workflow"]}
    rules = tuple(
        AcceptanceRule.model_validate(r) for r in workflow["reconcile"]["acceptance"]
    )
    inventory_rules = tuple(
        AcceptanceRule.model_validate(r) for r in workflow["inventory"]["acceptance"]
    )
    inventory = {"periods": ["Synthetic report scope"]}
    content = {"checks": ["Synthetic balanced result"]}
    records = []
    for n, (kind, (formula, operands)) in enumerate(FORMULAS.items(), 1):
        key = f"{kind}/2024-12-31/synthetic-v1"
        inventory[f"{kind}_plan"] = [{"key": key}]
        content[f"{kind}_checks"] = [
            {"key": key, "compute_id": f"c{n}", "value": 0, **operands}
        ]
        content[f"{kind}_missing"] = []
        records.append(
            {
                "cursor": n,
                "payload": {
                    "expression": formula,
                    "value": "0",
                    "inputs": [
                        {"name": k, "value": str(v), "ref": f"fact:synthetic-{k}"}
                        for k, v in operands.items()
                    ],
                },
            }
        )

    class Repo:
        def __init__(self, data):
            self.data = data

        async def list_task_events(self, task_id, *, types):
            return self.data

        async def list_artifacts_with_content(self, task_id):
            return [{"kind": "step", "name": "inventory", "content": inventory}]

    results = []

    async def verify(name, body, data, expected):
        verdict = judge(json.dumps(body), rules)
        verdict = await judge_numbers(
            verdict, rules, repo=Repo(data), task={"id": "synthetic"}
        )
        assert verdict.ok == expected, (name, verdict.failures, verdict.checks)
        results.append({"case": name, "accepted": verdict.ok})

    assert judge(json.dumps(inventory), inventory_rules).ok
    empty = {k: [] for k in inventory}
    assert not judge(json.dumps(empty), inventory_rules).ok
    results.append({"case": "empty_inventory_rejected", "accepted": False})
    await verify("four_original_formulas", content, records, True)
    for n, kind in enumerate(FORMULAS):
        altered = copy.deepcopy(records)
        altered[n]["payload"]["expression"] = "A-TLE"
        await verify(f"{kind}_substitute_formula", content, altered, False)
        altered = copy.deepcopy(records)
        altered[n]["payload"]["value"] = "2"
        await verify(f"{kind}_nonzero_reported_as_zero", content, altered, False)
        altered = copy.deepcopy(content)
        altered[f"{kind}_checks"][0][next(iter(FORMULAS[kind][1]))] += 1
        await verify(f"{kind}_operand_changed", altered, records, False)
        altered = copy.deepcopy(content)
        altered[f"{kind}_checks"] = []
        await verify(f"{kind}_period_omitted", altered, records, False)
        altered = copy.deepcopy(content)
        altered[f"{kind}_checks"] *= 2
        await verify(f"{kind}_period_duplicated", altered, records, False)
        altered = copy.deepcopy(content)
        row = altered[f"{kind}_checks"].pop()
        altered[f"{kind}_missing"] = [
            {"key": row["key"], "reason": "input missing; not verified"}
        ]
        await verify(f"{kind}_missing_explicitly_recorded", altered, records, True)
        altered[f"{kind}_checks"] = [row]
        await verify(f"{kind}_both_computed_and_missing", altered, records, False)
    # A real imbalance is evidence, not a platform error; the author excludes it
    # from forecasts rather than forcing every source report to balance.
    imbalance, rec = copy.deepcopy(content), copy.deepcopy(records)
    imbalance["balance_checks"][0].update(A=12, value=2)
    rec[0]["payload"]["value"] = "2"
    rec[0]["payload"]["inputs"][0]["value"] = "12"
    await verify("genuine_imbalance_retained_not_forged_zero", imbalance, rec, True)
    # Reproduce the identified live calculation shape without using report data.
    live_shape = copy.deepcopy(records)
    live_shape[0]["payload"] = {
        "expression": "A-TLE",
        "value": "0",
        "inputs": [{"name": "A", "value": "10"}, {"name": "TLE", "value": "10"}],
    }
    await verify("test10_c263_c287_c339_shape_rejected", content, live_shape, False)
    print(
        json.dumps(
            {
                "synthetic": True,
                "checks": len(results),
                "results": results,
                "limits": "Formula/value/input/coverage verification; not a live financial test or semantic validation of report sources.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )


asyncio.run(main())
