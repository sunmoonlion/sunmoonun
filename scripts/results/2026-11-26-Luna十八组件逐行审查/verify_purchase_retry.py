"""在 KnowBase 环境模拟回执丢失后，原交易重试时卖家许可已经变化。"""
import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "knowbase-app/knowbase-backend/app"))
from app.application.services.user_library_service import UserLibraryService
from app.domain.user_data import UserDataError


async def check():
    repo = AsyncMock()
    material = SimpleNamespace(id="material", owner="seller", live=True, license="sale", current_version=1)
    repo.get_material.return_value = material
    issued = {}
    def add_holding(row):
        return issued.setdefault((row.subject, row.material_id, row.ref), row)
    repo.add_holding.side_effect = add_holding
    library = UserLibraryService(repo, None, prefix="test")
    original = await library.purchase("seller", "material", "buyer", "tx-example")
    material.license = "self"
    try:
        await library.purchase("seller", "material", "buyer", "tx-example")
    except UserDataError as exc:
        assert exc.code == "not_for_sale"
    else:
        raise AssertionError("预期复现原回执无法取回")
    assert list(issued.values()) == [original] and repo.add_holding.await_count == 1
    print("首笔购入已登记。卖家改为自用后，同交易号重试被拒，原有效回执未被取回。")


if __name__ == "__main__":
    asyncio.run(check())
