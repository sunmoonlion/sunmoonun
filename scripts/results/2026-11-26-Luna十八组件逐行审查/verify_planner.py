"""在 KnowBench 后端测试环境运行，使用同一组方法版本核对两种入口的宿主判断。"""

import asyncio
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

workspace = Path(__file__).resolve().parents[4]
backend = workspace / "knowbench-app/knowbench-backend/app"
sys.path[:0] = [str(backend), str(backend / "tests")]

from test_hierarchical_planning import decision, inspect, setup

from app.application.workbench import temporary_planning as planning
from app.application.workbench.temporary_planning import compile_choice
from app.domain.workbench.expert_match import digest
from app.domain.workbench.formal_method_generated import (
    FormalMethodDefinition,
    MethodRef,
)
from app.domain.workbench.hierarchical_planning import HierarchicalPlanner
from app.domain.workbench.temporary_plan import read_choice


async def main():
    goal = "用我给的两份独立输入，分别交回标准明细和费用核对回执，两份分开交。"
    steps = [
        dict(
            id="detail",
            task="提取标准明细",
            method="first",
            inputs={"value": {"source": "caller", "name": "rows"}},
            deliver_as={"receipt": "detail"},
        ),
        dict(
            id="fee",
            task="核对费用",
            method="a",
            inputs={
                "value": {"source": "caller", "name": "fees"},
                "kind": {"source": "caller", "name": "kind"},
            },
            deliver_as={"receipt": "check"},
        ),
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

    service = SimpleNamespace(
        formal_registry=SimpleNamespace(planning_definitions=lookup)
    )
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
            planner.advance(
                decision(
                    steps[0],
                    "parallel_join",
                    children={"detail": "提取明细", "fee": "核对费用"},
                )
            )
        except ValueError as exc:
            assert "Each child must feed" in str(exc)
            print(scene, "独立子目标未被接受", str(exc))
        else:
            raise AssertionError("请复核新版本对独立子目标的支持")
        partial = planner.advance(decision(steps[0]))
        result = partial.get("selection", partial)
        assert result["status"] == "ready" and len(result["steps"]) == 1
        print(scene, result["status"], result["steps"][0]["deliver_as"])


async def check_shared_input(distinct_description):
    task, definitions = setup()
    ctx = task["original_input"]["input"]
    goal = "用同一份明细分别核两遍，再合并核验结果。"
    ctx["text"] = goal
    for entry in ctx["catalog"]["entries"]:
        alias = entry["alias"]
        old = MethodRef.model_validate(entry["reference"])
        definition = definitions.pop(old)
        doc = definition.document()
        port = doc["procedure"]["inputs"]["value"]
        if alias == "a" and distinct_description:
            port = {**port, "description": "另一位作者对同一输入的说明"}
        doc["procedure"]["inputs"] = (
            {"value": port} if alias != "b" else {"left": port, "right": port}
        )
        definition = FormalMethodDefinition.model_validate(doc)
        ref = old.model_copy(update={"digest": definition.digest()})
        definitions[ref] = definition
        entry.update(
            interfaces=definition.interfaces(), reference=ref.model_dump(mode="json")
        )
    planner = HierarchicalPlanner(task)
    inspect(planner, "first", "a", "b")
    root = dict(
        method="b",
        id="join",
        task="合并",
        inputs={
            name: dict(source="step", step=name, output="receipt")
            for name in ("left", "right")
        },
    )
    assert (
        planner.advance(
            decision(
                root,
                "parallel_join",
                children={"left": "核对明细", "right": "复算明细"},
            )
        )
        is None
    )

    def child(alias):
        return decision(
            dict(
                method=alias,
                id="review",
                task="核验",
                inputs={"value": dict(source="caller", name="rows")},
            ),
            shared_inputs=["value"],
        )

    assert planner.advance(child("first")) is None
    sketch = planner.advance(child("a"))
    assert sketch["status"] == "ready"
    choice = read_choice(task, sketch, check_graph=True)

    async def lookup(owner, refs):
        return {ref: definitions[ref] for ref in refs}

    svc = SimpleNamespace(formal_registry=SimpleNamespace(planning_definitions=lookup))
    try:
        await compile_choice(
            svc, "fixture", str(uuid4()), goal, choice, ctx["runtime"], ["join"]
        )
    except ValueError as e:
        assert distinct_description and "External aliases" in str(e), str(e)
        print("说明不同：草图 ready，编译拒绝", str(e))
    else:
        assert not distinct_description
        print("说明相同：草图 ready，编译成功")


async def check_negative_requirement():
    question = "请核对这份清单，只查一次。不要无限重试。"
    review = {
        "question": question,
        "review_digest": digest(question),
        "match": {"outcome": "no_match"},
    }
    repo = SimpleNamespace(
        subject_of_actor=AsyncMock(return_value="fixture"),
        transaction=nullcontext,
        get_task=AsyncMock(
            return_value=dict(
                id="task",
                session_id="s",
                profile_id="FIND_EXPERT",
                profile_version=5,
                state="SUCCEEDED",
            )
        ),
        latest_task_payload=AsyncMock(return_value=None),
        get_artifact=AsyncMock(),
        list_task_events=AsyncMock(return_value=[]),
        append_event=AsyncMock(),
    )
    service = SimpleNamespace(
        repo=repo,
        planning_enabled=lambda owner: True,
        instruction_service=object(),
        script_enabled=True,
        material_read_enabled=True,
    )
    with (
        patch.object(planning, "read_verified", AsyncMock(return_value=review)),
        patch.object(planning, "catalog", AsyncMock()) as catalog,
    ):
        result = await planning.start(
            service,
            "owner",
            "task",
            planning.PlanningRequest(review_digest=review["review_digest"]),
        )
        assert result["reason"] == "unsupported_capability" and result["missing"] == [
            "unbounded"
        ]
        assert result["planning_task"] is None and result["catalog_queries"] == 0
        catalog.assert_not_awaited()
        repo.append_event.assert_awaited_once()
        print(question, result["outcome"], result["missing"], result["catalog_queries"])


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(check_shared_input(False))
    asyncio.run(check_shared_input(True))
    asyncio.run(check_negative_requirement())
