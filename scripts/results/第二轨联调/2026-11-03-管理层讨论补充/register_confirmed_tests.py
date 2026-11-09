"""发布后由 Luna 在 knowlab 应用环境执行；不启动测试、不签数据授权、不交付。

参数1为 confirmed-cases.json 文本，参数2为 confirmed-output-notation.json 文本。
只调用正式应用服务。检查当前版本与工作稿，重复执行不新增创意或准专家。
"""

import asyncio
import json
import sys

from app.bootstrap.knowbots import knowbot_service, knowbot_workdraft_service
from app.domain.knowbots.lifecycle import ACTIVE_TESTS, RevisionIn
from app.domain.knowbots.test_run import Expectation
from app.infrastructure.storage.postgres import get_postgres

OWNER = "b5f49830-db2a-4d1b-b325-567e77b59d4a"
REQUEST = "5814331f-b555-4de9-bee6-f01e4e84e909"


async def main():
    assert "row" in Expectation.model_fields, "knowlab row contract is not deployed"
    cases = json.loads(sys.argv[1])
    expected = json.loads(sys.argv[2])
    pg = get_postgres()
    await pg.init()
    try:
        async with pg.session_factory() as session:
            service = knowbot_service(session)
            workdrafts = knowbot_workdraft_service(session)
            async with service.repo.transaction():
                request, workdraft = await workdrafts.get(OWNER, REQUEST)
                await service.repo.lock_request(request.id)
                request, workdraft = await workdrafts.get(OWNER, REQUEST)
                assert workdraft.revision == expected["revision"] == 33, "workdraft drift"
                manifest, problems, version = await workdrafts.preview(OWNER, REQUEST)
                assert not problems and version == "2"
                assert manifest == expected["manifest"], "compiled candidate drift"
                tests = await service.repo.list_tests(request_ids=[request.id])
                assert not any(t.status in ACTIVE_TESTS for t in tests), "active test"
                revision = RevisionIn.model_validate({
                    "idea": request.idea, "cases": cases, "consent_test_data": True,
                })
                normalized = [c.model_dump(mode="json") for c in revision.cases]
                if request.latest_version == 1:
                    added = await service.revise(OWNER, REQUEST, revision)
                    assert added.version == 2 and added.idea == request.idea
                else:
                    assert request.latest_version == 2 and request.cases == normalized, "test version drift"
                matches = [d for d in await service.repo.list_drafts(request_ids=[request.id])
                           if d.request_version == 2 and d.manifest == manifest]
                draft = max(matches, key=lambda d: d.revision) if matches else await workdrafts.publish(OWNER, REQUEST)
                assert draft.request_version == 2 and draft.version == "2"
            print(json.dumps({
                "request_id": REQUEST, "request_version": 2,
                "workdraft_revision": workdraft.revision, "draft_id": str(draft.id),
                "draft_revision": draft.revision, "status": draft.status,
                "case_expectations": [len(c.expectations) for c in revision.cases],
                "real_test_started": False, "delivery_started": False,
                "manual_review_required": ["T2语义支持/章节读取", "T3人数与缺口", "T4实际授权与取数轨迹"],
            }, ensure_ascii=False))
    finally:
        await pg.shutdown()


asyncio.run(main())
