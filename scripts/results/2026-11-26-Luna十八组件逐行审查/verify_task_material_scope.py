"""本地检查工作台采单确认范围及补采回执。不连接账号或外部服务。"""
import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

from app.application.workbench.expert_data import DataWaiter, ExpertData, _asked_need


@asynccontextmanager
async def transaction():
    yield


def request(number):
    need = _asked_need({"doc_type": "annual_report", "reason": f"报告{number}"}, number, 1)
    return {"id": f"r{number}", "status": "pending", "needs": [need.model_dump(mode="json")]}


async def check():
    requests = [request(1), request(2)]
    row = {"resolution_id":"list", "status":"ready", "consumer":"expert",
           "detail":{"requests":requests}, "grant_ref":"run"}
    repo = AsyncMock()
    repo.transaction = transaction
    repo.get_task_resolution.return_value = row
    repo.list_task_data.return_value = []
    service = AsyncMock()
    entries = [
        {"need_key":r["needs"][0]["key"], "status":"resolved", "key":{},
         "chosen":[{"material_id":r["id"],"version_no":2,"sha256":"1"*64}]}
        for r in requests
    ]
    service.resolution.return_value = {"revision":2,"items":entries}
    service.run_grant.return_value = {"grant_id":"grant"}
    with patch("app.application.workbench.ledger.Ledger.resume_data",new_callable=AsyncMock) as resume:
        await ExpertData(service,None,supply_enabled=False).confirm_requests(
            repo, {"id":"task"}, owner_subject="actor", user_token=AsyncMock(return_value="token"))
        granted = service.run_grant.await_args.kwargs["items"]
        assert [(i["material_id"],i["version_no"]) for i in granted] == [("r1",2),("r2",2)]
        resume.assert_awaited_once()

    @asynccontextmanager
    async def store():
        yield repo

    req = requests[0]
    row.update(status="waiting", task_id="task", confirmation_id="confirm",
               detail={"requests":[req],"phase":{"requests":["r1"]}})
    repo.get_task.return_value = {"owner_actor_id":"actor","state":"WAITING"}
    repo.subject_of_actor.return_value = "subject"
    service.refresh.return_value = {"revision":3,"items":[dict(entries[0],status="ambiguous",chosen=[])]}
    waiter = DataWaiter(store,service,AsyncMock())
    with patch("app.application.workbench.ledger.Ledger.resume_data",new_callable=AsyncMock) as resume:
        assert await waiter._resume(row,dict(row["detail"]))
        assert repo.update_task_resolution.await_args.kwargs["detail"]["requests"][0]["status"] == "done"
        resume.assert_awaited_once()


if __name__ == "__main__":
    asyncio.run(check())
