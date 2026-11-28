"""KnowLab 的真实申请和分页存储；可变目录仅含受控测试候选。"""

from uuid import uuid4

from app.application.services.formal_methods import FormalMethodService
from app.application.services.method_search import scan_outputs
from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from tests.test_knowbot_repository_db import db as db
from tests.test_method_search_db import OWNER, project


async def scan_case(db, monkeypatch, *, initially_empty):
    runtime, rid, query = await project(db)
    item = {"reference": {"method_id": str(uuid4()), "version": 1, "digest": "sha256:" + "a" * 64}, "output": "balance", "title": "余额"}
    rows = [] if initially_empty else [item]

    async def match(self, *args, **kwargs):
        return {"items": list(rows), "next": None}

    monkeypatch.setattr(FormalMethodService, "matching_outputs", match)

    async def scan(cmd):
        async with db() as session:
            service = FormalMethodService(SqlKnowlabRepository(session), runtime)
            return await scan_outputs(service, OWNER, rid, cmd)

    first = await scan(query)
    if initially_empty:
        assert first["items"] == []
        rows.append(item)
        replay = await scan(query.model_copy(update={"action_id": uuid4()}))
    else:
        assert first["items"] == [item]
        replay = await scan(query)
    assert replay["items"] == [item], replay


async def test_candidate_available_after_response_loss(db, monkeypatch):
    await scan_case(db, monkeypatch, initially_empty=False)


async def test_fresh_search_after_filling_catalog_gap(db, monkeypatch):
    await scan_case(db, monkeypatch, initially_empty=True)
