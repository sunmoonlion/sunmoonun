"""Synthetic evidence check against the actual compiled author step; no API/data writes."""
import asyncio
import copy
import json
import sys
from unittest.mock import AsyncMock

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import judge_numbers
from app.domain.workbench.packs import AcceptanceRule


async def main():
    step = json.loads(sys.argv[1])["compiled_step"]
    rules = tuple(AcceptanceRule.model_validate(r) for r in step["acceptance"])
    source = "测试合成材料：管理层讨论指出收入增长来自销售增长。"
    conclusions = ["测试结论一", "测试结论二"]
    repo = AsyncMock()
    repo.list_task_events.return_value = []
    repo.list_artifacts_with_content.return_value = [
        {"name": "indicators", "kind": "step", "content": {"indicators": conclusions}}
    ]
    reader = AsyncMock()
    async def quotes(_repo, _task, refs):
        return [{"found": q["material_id"] == "synthetic" and q["page"] == 7 and q["text"] in source} for q in refs]
    reader.quotes.side_effect = quotes
    good = {"comparisons": [
        {"conclusion": conclusions[0], "verdict": "支持", "reason": "合成材料明确提及", "quotes": [{"material_id": "synthetic", "page": 7, "text": "收入增长来自销售增长"}]},
        {"conclusion": conclusions[1], "verdict": "不支持", "reason": "管理层讨论未提及", "quotes": []},
    ]}
    cases = [("supported_quote_and_unmentioned", good, True)]
    for name, field, value in [
        ("missing_quote", "quotes", []),
        ("fabricated_quote", "quotes", [{"material_id": "synthetic", "page": 7, "text": "伪造引文"}]),
        ("wrong_page", "quotes", [{"material_id": "synthetic", "page": 8, "text": "收入增长来自销售增长"}]),
        ("invalid_verdict", "verdict", "未知"),
        ("empty_reason", "reason", " "),
    ]:
        changed = copy.deepcopy(good)
        changed["comparisons"][0][field] = value
        cases.append((name, changed, False))
    cases.extend([
        ("missing_conclusion", {"comparisons": good["comparisons"][:1]}, False),
        ("duplicate_conclusion", {"comparisons": good["comparisons"] * 2}, False),
        ("missing_section_disclosed", {"comparisons": [
            {"conclusion": c, "verdict": "不支持", "reason": "未找到管理层讨论章节", "quotes": []}
            for c in conclusions
        ]}, True),
        ("empty_comparisons", {"comparisons": []}, False),
    ])
    results = []
    for name, output, expected in cases:
        verdict = await judge_numbers(judge(json.dumps(output, ensure_ascii=False), rules), rules, repo=repo, task={"id": "synthetic-only"}, reader=reader)
        results.append({"case": name, "expected": expected, "accepted": verdict.ok, "failures": verdict.failures})
        assert verdict.ok == expected, results[-1]
    print(json.dumps({"synthetic": True, "cases": results, "passed": len(results)}, ensure_ascii=False))

asyncio.run(main())
