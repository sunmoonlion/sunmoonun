"""KnowBase 运行服务的资料加工与同比日期边界。使用内存替身。"""
import asyncio
import hashlib
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

backend = Path(__file__).resolve().parents[4] / "knowbase-app/knowbase-backend/app"
sys.path.insert(0, str(backend))
from app.application.services.user_run_service import UserRunService
from app.domain.user_facts import FactQuery
from app.domain.user_data import UserDataError


async def check():
    runs, library = AsyncMock(), AsyncMock()
    service = UserRunService(library, runs, None, prefix="test")
    try:
        await service.query_metric(
            "revenue_growth", FactQuery(period_from=date(2024, 2, 29)), subject="fixture"
        )
    except ValueError as exc:
        assert "day is out of range" in str(exc)
    else:
        raise AssertionError("预期复现闰日异常")
    print("同比查询起日为 2024-02-29，查询资料前已抛 ValueError。")

    # 与库查询相同的排序和 LIMIT。最后一条仍未加工，前两条已加工。
    backlog = [("fixture", name, 1) for name in ("recent", "second", "oldest")]
    runs.live_processing_uses.side_effect = lambda limit: backlog[:limit]
    library.version.side_effect = lambda key, number: SimpleNamespace(id=key)
    runs.renditions.side_effect = lambda key: (
        [] if key == "oldest" else [SimpleNamespace(processor="knowfeed")]
    )
    for _ in range(2):
        assert await service.pending_processing("knowfeed", limit=1) == []
    assert library.version.await_count == 4
    assert all(call.args[0] != "oldest" for call in library.version.await_args_list)
    print("连续两次领取一项，均返回空；第 3 份待加工资料从未进入检查范围。")

    objects = AsyncMock()
    service.objects = objects
    body = b"sample"
    library.get_material.return_value = SimpleNamespace(
        id="fixture", owner="owner", live=True, in_output_zone=True,
        provenance={}, current_version=1, description=None,
    )
    library.version.side_effect = None
    library.version.return_value = SimpleNamespace(
        object_key="original", sha256=hashlib.sha256(body).hexdigest(),
        media_type="text/plain", size_bytes=len(body),
    )
    library.bytes_used.return_value = 0
    objects.get.return_value = body
    try:
        await service.convert("owner", "fixture", name="folder/name.txt")
    except UserDataError as exc:
        assert exc.code == "name_invalid"
    else:
        raise AssertionError("非法资料名称未被拒绝")
    objects.put.assert_awaited_once()
    objects.delete.assert_not_awaited()
    library.add_material.assert_not_awaited()
    print("改名被拒之前已经写入对象，未登记资料也未删除该副本。")


if __name__ == "__main__":
    asyncio.run(check())
