"""在隔离 KnowBench 测试库运行；模型与目录使用已有测试夹具。"""
import json

import pytest
from httpx import ASGITransport, AsyncClient
from test_find_expert_db import _project
from test_formal_expert_intake_db import Registry, proposal, web_app
from test_knowbot_test_runs_db import runner_for, setup_test_computer
from test_workbench_ledger_db import db
from test_workbench_task_runtime_db import ScriptedAppServer, close, drive


@pytest.mark.asyncio
async def test_remaining_candidate_is_hidden_by_withdrawal(db, monkeypatch):
    registry = Registry()
    available, withdrawn = registry.entries
    model = ScriptedAppServer([json.dumps(proposal(registry))])
    await model.start()
    runner = runner_for(db)
    try:
        await setup_test_computer(db, model)
        project = await _project(db)
        async with AsyncClient(
            transport=ASGITransport(app=web_app(db, registry, monkeypatch)),
            base_url="http://testserver",
        ) as client:
            made = await client.post(
                f"/api/workbench/projects/{project}/find-expert",
                json={
                    "question": "需要差异表",
                    "idempotency_key": "withdraw-one-match",
                    "match_contract": "knowbench/expert-match/v5",
                },
            )
            assert made.status_code == 201
            path = "/api/workbench/find-expert/" + made.json()["task_id"]
            await drive(runner)
            before = await client.get(path)
            assert before.status_code == 200
            review = before.json()["formal"]
            assert len(review["options"]) == 2
            del registry.entries[withdrawn]
            assert (await client.get(path)).status_code == 404
            selected = await client.put(path + "/selection", json={
                "reference": available.model_dump(mode="json"),
                "review_digest": review["review_digest"],
            })
            assert selected.status_code == 200
            assert (await client.get(path)).status_code == 200
            assert len(model.turn_inputs) == 1
    finally:
        await close(runner)
        await model.close()
