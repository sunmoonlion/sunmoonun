"""Offline composition checks for the accepted financial assembly.

Run with knowbench-backend/app on PYTHONPATH. By default inspect the accepted
preview; --stdin inspects the manifest emitted by real freeze/bind/publish in an
isolated knowlab database. Plans and requirements are synthetic test inputs, not
AI matching results or proof of financial correctness. Never writes assets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

from app.domain.workbench.execution_plan import project_plan
from app.domain.workbench.knowbots import V2_TOOLS
from app.domain.workbench.method_catalog import CapabilityMethodCatalog, parse_catalog
from app.domain.workbench.method_plan import (
    AcceptedMethodPlan,
    parse_plan,
    validate_plan,
)

HERE = Path(__file__).resolve().parent


def verify(manifest):
    catalog = parse_catalog(manifest["pack"])
    if not isinstance(catalog, CapabilityMethodCatalog):
        raise ValueError("expected the accepted capability catalog")
    units = {unit.contract.step_id: unit for unit in catalog.method_units}
    if set(units) != {
        "scope",
        "inventory",
        "reconcile",
        "series",
        "indicators",
        "official",
        "forecast",
        "writeup",
    }:
        raise ValueError("unexpected financial method assembly")
    checks = {}

    def proposal(capabilities, selected):
        return {
            "contract": "knowbench/method-plan/v2",
            "parent_version": 0,
            "reason": "合成工程计划：只验证已接受装配的依赖和投影，不代替模型规划或财务验收",
            "requirement_coverage": {
                f"r{i}": cap for i, cap in enumerate(capabilities)
            },
            "steps": [
                {
                    "instance_id": f"run_{alias}",
                    "method_id": alias,
                    "inputs": [
                        {"slot": slot, "instance_id": f"run_{spec.method_id}"}
                        for slot, spec in unit.contract.input_slots.items()
                        if spec.method_id in selected
                    ],
                    "omitted_inputs": {
                        slot: "not_selected"
                        for slot, spec in unit.contract.input_slots.items()
                        if spec.method_id not in selected
                    },
                    "tools": list(unit.contract.tools),
                    "reason": unit.selection.applies_when,
                }
                for alias, unit in units.items()
                if alias in selected
            ],
            "unselected_methods": {
                alias: "本题未要求此项能力" for alias in units if alias not in selected
            },
            "final_outputs": {"writeup": "run_writeup"},
        }

    def validate(document, requirements):
        plan = parse_plan(document)
        validate_plan(
            catalog,
            plan,
            previous=None,
            protected_prefix=0,
            completed_prefix=0,
            results={},
            available_tools=V2_TOOLS,
            requirement_capabilities=requirements,
        )
        return plan

    def expect_rejected(name, document, requirements):
        try:
            validate(document, requirements)
        except ValueError as exc:
            checks[name] = {"passed": True, "reason": str(exc)}
        else:
            raise AssertionError(f"invalid plan accepted: {name}")

    cases = {}
    for name, capabilities, optional in (
        ("annual_trend", ["annual_analysis"], []),
        ("employee_revenue", ["employee_revenue"], []),
        ("quarter_trend", ["quarter_analysis"], ["series"]),
        (
            "annual_with_forecast",
            ["annual_analysis", "seasonal_forecast"],
            ["series", "forecast"],
        ),
    ):
        selected = {
            "scope",
            "inventory",
            "reconcile",
            "indicators",
            "official",
            "writeup",
            *optional,
        }
        document = proposal(capabilities, selected)
        requirements = {
            key: {cap} for key, cap in document["requirement_coverage"].items()
        }
        plan = validate(document, requirements)
        receipt = AcceptedMethodPlan(
            task_id="synthetic-task",
            attempt_id="synthetic-attempt",
            pack_digest="sha256:" + "0" * 64,
            version=1,
            proposal=plan,
        )
        projected = project_plan(catalog, receipt, profile_id="synthetic-financial")
        assert len(projected.pack.workflow) == len(selected)
        author_steps = {
            step.instance_id: units[step.method_id].contract for step in plan.steps
        }
        planned_steps = {step.instance_id: step for step in plan.steps}
        for step in projected.pack.workflow:
            original = author_steps[step.step_id]
            bound = {item.slot for item in planned_steps[step.step_id].inputs}
            # Only frozen optional-input guards may remove acceptance checks.
            assert len(step.acceptance) == sum(
                check.when_input_present is None or check.when_input_present in bound
                for check in original.acceptance
            )
            assert step.output_file == original.output_file
        assert projected.pack.workflow[-1].output_file is not None
        cases[name] = {
            "methods": [step.method_id for step in plan.steps],
            "plan": document,
            "projected_checks": {
                s.step_id: len(s.acceptance) for s in projected.pack.workflow
            },
        }
        checks[f"accepted:{name}"] = {"passed": True}

    full = cases["annual_with_forecast"]["plan"]
    requirements = {key: {cap} for key, cap in full["requirement_coverage"].items()}
    bad = deepcopy(cases["annual_trend"]["plan"])
    expect_rejected("missing_requested_forecast", bad, requirements)
    bad = deepcopy(full)
    bad["requirement_coverage"]["r1"] = "employee_revenue"
    expect_rejected("substituted_capability", bad, requirements)
    bad = deepcopy(full)
    final = bad["steps"][-1]
    forecast_slot = next(
        i["slot"] for i in final["inputs"] if i["instance_id"] == "run_forecast"
    )
    final["inputs"] = [i for i in final["inputs"] if i["slot"] != forecast_slot]
    final["omitted_inputs"][forecast_slot] = "not_selected"
    expect_rejected("hidden_selected_forecast", bad, requirements)
    bad = deepcopy(full)
    bad["steps"] = [s for s in bad["steps"] if s["method_id"] != "reconcile"]
    expect_rejected("skipped_reconciliation", bad, requirements)
    bad = deepcopy(full)
    bad["steps"][0]["tools"].append("arbitrary_external_tool")
    expect_rejected("undeclared_tool", bad, requirements)
    bad = deepcopy(full)
    bad["steps"][-1]["inputs"][0]["version"] = 99
    expect_rejected("fabricated_artifact_version", bad, requirements)
    return {
        "synthetic_plans": True,
        "real_model_calls": 0,
        "financial_semantics_verified": False,
        "manifest_sha256": hashlib.sha256(
            json.dumps(
                manifest, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode()
        ).hexdigest(),
        "independent_methods": len(catalog.method_sources),
        "checks": checks,
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()
    manifest = (
        json.load(sys.stdin)
        if args.stdin
        else json.loads((HERE / "financial-manifest-preview.json").read_text())
    )
    print(json.dumps(verify(manifest), ensure_ascii=False, indent=2))
