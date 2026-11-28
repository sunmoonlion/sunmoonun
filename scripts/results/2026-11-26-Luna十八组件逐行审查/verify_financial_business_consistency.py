"""Run in the KnowBench app venv with the financial fixture directory as argv[1]."""
import asyncio
import json
import runpy
import sys
from pathlib import Path

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import judge_numbers


async def main():
    fixtures = Path(sys.argv[1])
    sys.argv[1] = str(fixtures / "fixtures/financial-expert-manifest.json")
    probe = runpy.run_path(str(fixtures / "financial_runtime_probe.py"))
    evidence = probe["Evidence"]()
    outputs = probe["outputs"](evidence)
    for method, changes in [
        ("M05", {"solvency_risk_level": "低", "altman_z_score": 0.5}),
        ("M14", {"sensitivity_table": []}),
        ("M18", {"kam_topics_count": 0}),
        ("M13", {}),
    ]:
        key = probe[method]
        result = outputs[key] | changes
        rules = probe["units"][key].acceptance
        verdict = await judge_numbers(judge(json.dumps(result, ensure_ascii=False), rules),
                                      rules, repo=evidence, task={"id": "synthetic"}, reader=evidence)
        print(method, "accepted", verdict.ok)
        if method == "M13":
            print("first scenario and interval", result["forecast_income_statement"][0],
                  result["forecast_intervals"][0])


if __name__ == "__main__":
    asyncio.run(main())
