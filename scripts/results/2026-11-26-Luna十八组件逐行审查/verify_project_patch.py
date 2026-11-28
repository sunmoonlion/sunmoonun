"""仅在一次性本地数据库中运行，复核批量修改被拒后的持久状态。"""
from test_workbench_project_routes import A, machine, project, make_client, db  # noqa: F401
import pytest

pytestmark = pytest.mark.usefixtures("builtin_packs_on_offer")


async def test_refused_patch_partially_commits(make_client, db):
    async with make_client(A) as http:
        env = await machine(http)
        made = (await project(http, env)).json()
        path = f"/api/workbench/projects/{made['id']}"
        created = await http.post("/api/workbench/sessions", json={"kind":"work","project_id":made["id"]})
        assert created.status_code == 201
        session = created.json()["session_id"]
        task = await http.post(f"/api/workbench/sessions/{session}/handover", json={
            "profile_id":"DATA_QUERY","original_input":{"text":"测试"},
            "budget_limit":"2","idempotency_key":"project-patch-0001",
        })
        assert task.status_code == 201
        changed = await http.patch(path, json={"title":"修改后的名称","archived":True})
        assert changed.status_code == 409
        state = (await http.get(path)).json()["project"]
        assert state["title"] == "修改后的名称"
        assert state["archived"] is False
