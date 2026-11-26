"""在 KnowBench 后端测试环境运行，使用同一组方法版本核对两种入口的宿主判断。"""

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

workspace = Path(__file__).resolve().parents[4]
backend = workspace / "knowbench-app/knowbench-backend/app"
sys.path[:0] = [str(backend), str(backend / "tests")]

from test_hierarchical_planning import decision, inspect, setup

from app.application.workbench.temporary_planning import compile_choice
from app.domain.workbench.hierarchical_planning import HierarchicalPlanner
from app.domain.workbench.temporary_plan import read_choice


async def main():
    goal = "用我给的两份独立输入，分别交回标准明细和费用核对回执，两份分开交。"
    steps = [
        dict(id="detail", task="提取标准明细", method="first",
             inputs={"value": {"source": "caller", "name": "rows"}},
             deliver_as={"receipt": "detail"}),
        dict(id="fee", task="核对费用", method="a",
             inputs={"value": {"source": "caller", "name": "fees"},
                     "kind": {"source": "caller", "name": "kind"}},
             deliver_as={"receipt": "check"}),
    ]
    task, definitions = setup()
    context = task["original_input"]["input"]
    context["text"] = goal
    context["catalog"]["entries"] = [
        row for row in context["catalog"]["entries"] if row["alias"] in {"a", "first"}
    ]
    selection = dict(status="ready", reason=goal, routing_required=False, steps=steps)
    choice = read_choice(task, selection, check_graph=True)

    async def lookup(owner, refs):
        return {ref: definitions[ref] for ref in refs}

    service = SimpleNamespace(formal_registry=SimpleNamespace(planning_definitions=lookup))
    _, root = await compile_choice(
        service, "fixture", str(uuid4()), goal, choice, context["runtime"], ["join"]
    )
    assert set(root.procedure.exports) == {"detail", "check"}
    assert all(not s.depends_on for s in root.procedure.steps)
    print("平图保留两个独立导出", sorted(root.procedure.exports))

    market = {}
    for row in context["catalog"]["entries"]:
        slots = {
            side: {name: view["slot"] for name, view in ports.items()}
            for side, ports in row["interfaces"].items()
        }
        market[row["alias"]] = {**row, **slots}
    author = {
        "seed": {"text": goal},
        "selection_context": {
            "methods": market,
            "patterns": context["runtime"]["patterns"],
            "partial": False,
        },
    }
    author_task = {
        "profile_id": "INCUBATE",
        "profile_version": "2",
        "original_input": {"input": {"incubation": author}},
    }
    for scene, request in (("即时", task), ("孵化", author_task)):
        planner = HierarchicalPlanner(request)
        inspect(planner, "first", "a")
        try:
            planner.advance(decision(
                steps[0], "parallel_join", children={"detail": "提取明细", "fee": "核对费用"}
            ))
        except ValueError as exc:
            assert "Each child must feed" in str(exc)
            print(scene, "独立子目标未被接受", str(exc))
        else:
            raise AssertionError("请复核新版本对独立子目标的支持")
        partial = planner.advance(decision(steps[0]))
        result = partial.get("selection", partial)
        assert result["status"] == "ready" and len(result["steps"]) == 1
        print(scene, result["status"], result["steps"][0]["deliver_as"])


if __name__ == "__main__":
    asyncio.run(main())
