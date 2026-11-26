"""在 KnowLab 后端测试环境核对收回平台孵化授权，不接数据库或模型。"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock

backend = Path(__file__).resolve().parents[4] / "knowlab-app/knowlab-backend/app"
sys.path.insert(0, str(backend))

from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from tests.test_knowbot_proposals import OWNER, _platform, all_clear, world


async def main():
    repo, creation, _, _, platform, incubations, runner = world.__wrapped__()
    request = await _platform(creation)
    rid = str(request.id)
    await creation.accept(rid, 1, all_clear(), "operator")
    job = await incubations.operator_start(rid, action="draft")
    assert job.status == "queued" and len(runner.started) == 1

    # 使用本地业务样例提供读数据。字段校验和事务收尾走正式 SQL 仓储。
    session = AsyncMock()
    sql = SqlKnowlabRepository(session)
    repo.update_incubation = sql.update_incubation
    repo.transaction = sql.transaction
    try:
        await platform.take_back(OWNER, rid)
    except ValueError as exc:
        assert str(exc) == "unknown incubation fields: ['ended_at', 'last_error']"
    else:
        raise AssertionError("需重新核对当前版本撤权结果")
    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
    print("已排队时收回授权触发字段错误，SQL 事务进入回滚分支。")


if __name__ == "__main__":
    asyncio.run(main())
