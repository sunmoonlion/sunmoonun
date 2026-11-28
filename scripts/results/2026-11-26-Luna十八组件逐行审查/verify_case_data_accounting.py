"""在 KnowBench 测试环境运行。只接替持久化操作，不连接外部服务。"""
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import UTC, datetime, timedelta
from app.application.workbench import test_runs as runs
from app.domain.workbench.errors import InteractionRejected


@asynccontextmanager
async def transaction():
    yield


def material():
    return {"material_id":"annual", "version_no":1, "sha256":"a"*64,
            "basis":"public","basis_ref":"record","name":"年报"}


async def apply(monkeypatch, answers, existing):
    requests = [{"id":key, "labels":[key], "status":"pending"} for key in answers]
    async def answer(run_id, key):
        return {"answer":{"data":answers[key.split(":")[-1]]}}
    repo = SimpleNamespace(
        get_task_resolution=AsyncMock(return_value={"detail":{"requests":requests}}),
        get_test_answer=AsyncMock(side_effect=answer),list_task_data=AsyncMock(return_value=existing),
        transaction=transaction, pin_task_data=AsyncMock(),update_task_resolution=AsyncMock())
    from app.application.workbench.ledger import Ledger
    monkeypatch.setattr(Ledger, "resume_data", AsyncMock())
    assert await runs.KnowbotTestConductor(None)._apply_data(repo, {"run_id":"r"}, {"id":"t"})
    return repo.update_task_resolution.await_args.kwargs["detail"]


async def test_selected_material_already_pinned_is_reported_declined(monkeypatch):
    detail = await apply(monkeypatch, {"年报":{"grant_id":"g","items":[material()]}},
                         [{"item_id":"annual","version_no":1}])
    assert detail["incomplete"] == ["年报：你没要"]
    assert detail["requests"][0]["status"] == "done"


async def test_mixed_answers_lose_the_declined_item(monkeypatch):
    detail = await apply(monkeypatch, {"年报":{"grant_id":"g","items":[material()]},
                                       "分部表":{"items":[]}}, [])
    assert "incomplete" not in detail
    assert all(r["status"] == "done" for r in detail["requests"])


async def test_rejected_answer_stops_wait_deadline_processing():
    now = datetime.now(UTC)
    conductor = runs.KnowbotTestConductor(None, now=lambda: now)
    conductor._respond_if_ready = AsyncMock(side_effect=InteractionRejected("interaction ended"))
    repo = SimpleNamespace(get_task=AsyncMock(return_value={
        "state":"WAITING","id":"t","active_interaction_id":"i"}),
        get_interaction=AsyncMock(return_value={"id":"i","kind":"question"}))
    row = {"task_id":"t","waiting_since":now-timedelta(hours=1)}
    for _ in range(2):
        await conductor._follow_case(repo, {"run_id":"r","max_wait_seconds":60},
                                     SimpleNamespace(case_id="c"), row, None)
    assert conductor._respond_if_ready.await_count == 2
    assert conductor._unanswerable == {"i"}


async def test_prestart_failure_loses_its_reason_in_status():
    from decimal import Decimal

    detail = "the computer refused to prepare a clean folder"
    row = {
        "run_id": "r",
        "status": "error",
        "error": detail,
        "request": {"contract": runs.CONTRACT, "manifest": {"schema": "knowbot-manifest/v3"}},
    }
    repo = SimpleNamespace(
        get_test_run=AsyncMock(return_value=row),
        list_test_cases=AsyncMock(return_value=[]),
        test_run_spent=AsyncMock(return_value=Decimal("0")),
    )
    result = await runs.KnowbotTestService(repo).status("r")
    assert result["status"] == "error"
    assert result["cases"] == []
    assert detail not in str(result)
