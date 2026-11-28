"""在 KnowBench app/tests 中使用项目自带的隔离 PostgreSQL 夹具运行。"""
import json
from types import SimpleNamespace

import httpx
from test_find_expert_db import _project
from test_formal_expert_intake_db import Registry, proposal, web_app
from test_knowbot_test_runs_db import runner_for, setup_test_computer
from test_workbench_ledger_db import db as db
from test_workbench_task_runtime_db import ScriptedAppServer, close, drive
from app.domain.workbench.tool_operations import OperationCatalog
from app.interfaces.http.web import workbench_expert as routes


async def test_edit_boolean_to_number_and_read_back(db, monkeypatch):
    registry = Registry()
    registry.methods = SimpleNamespace(operations=OperationCatalog(()))
    for old, definition in list(registry.definitions.items()):
        doc = definition.document()
        doc["procedure"]["steps"][0]["inputs"]["to"]["slot"]["schema"] = {
            "type": ["boolean", "integer"]
        }
        definition = type(definition).model_validate(doc)
        ref = old.model_copy(update={"digest": definition.digest()})
        del registry.definitions[old], registry.entries[old]
        registry.definitions[ref] = definition
        registry.entries[ref] = registry.public_declaration(ref, definition)
    fake = ScriptedAppServer([json.dumps(proposal(registry))])
    await fake.start()
    runner = runner_for(db)
    try:
        await setup_test_computer(db, fake)
        project = await _project(db)
        app = web_app(db, registry, monkeypatch)
        async def library_token():
            raise AssertionError("No materials were selected")
        app.dependency_overrides[routes.get_web_knowbase_token_provider] = lambda: library_token
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
            started = await client.post(f"/api/workbench/projects/{project}/find-expert", json={
                "idempotency_key":"typed-preparation", "question":"需要差异表",
                "match_contract":"knowbench/expert-match/v5",
            })
            started.raise_for_status()
            path = "/api/workbench/find-expert/" + started.json()["task_id"]
            await drive(runner)
            outcome = (await client.get(path)).json()["formal"]
            fingerprint = outcome["review_digest"]
            selection = await client.put(path+"/selection", json={
                "reference":outcome["options"][0]["reference"], "review_digest":fingerprint,
            })
            selection.raise_for_status()
            prep = path + "/preparation"
            body = {"review_digest":fingerprint, "expected_revision":0, "accounts":{},
                    "materials":{}, "budget_limit":"5", "values":{"to":True}}
            first = await client.put(prep, json=body)
            first.raise_for_status()
            assert first.json()["revision"] == 1
            second = await client.put(prep, json={**body, "expected_revision":1, "values":{"to":1}})
            second.raise_for_status()
            assert type(second.json()["bindings"]["values"]["to"]) is int
            assert second.json()["revision"] == 1
            stored = (await client.get(prep)).json()
            assert stored["bindings"]["values"]["to"] is True
    finally:
        await close(runner)
        await fake.close()
