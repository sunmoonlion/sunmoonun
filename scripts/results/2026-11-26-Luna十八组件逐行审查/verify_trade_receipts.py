"""在 KnowMart 虚拟环境运行。交易均为内存测试数据。"""
import asyncio
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "knowmart-app/knowmart-backend/app"))
from app.application.services.market import MarketService, _buy_digest
from app.domain.market import BuyIn


class Ledger:
    def __init__(self, status):
        self.request = BuyIn(request_id="example-0001")
        self.trade = dict(
            id=uuid4(), listing_ref="listing", kind="knowledge", title="测试资料",
            request_digest=_buy_digest("listing", self.request), target_app=None,
            buyer_subject="buyer", seller_subject="seller", resale_allowed=False,
            created_at=datetime.now(UTC), price=None, demand_id=None,
            planned=[dict(seller_item_id="material", name="报告", sha256="a"*64)],
            granted=[], status=status, failure="item_gone" if status == "failed" else None,
        )

    @asynccontextmanager
    async def transaction(self):
        yield

    async def trade_by_request(self, buyer, key):
        return dict(self.trade)

    async def get_trade(self, key, for_update=False):
        return dict(self.trade)

    async def update_trade(self, key, **changes):
        self.trade.update(changes)


async def check():
    for initial in ("failed", "granting"):
        ledger, vault = Ledger(initial), AsyncMock()
        vault.purchase.return_value = dict(material_id="material", version_no=2, license="self")
        receipt = await MarketService(ledger, None, vault).buy("buyer", "listing", ledger.request)
        assert receipt["status"] == "done"
        assert ledger.trade["granted"][0]["version_no"] == 2
        assert ledger.trade["granted"][0]["sha256"] == "a"*64
        assert vault.purchase.await_count == 1
        if initial == "failed":
            assert receipt["failure"] == "item_gone"
            print("原交易已终态失败，同键重试再次签发并改成 done，同时保留 item_gone。")
        else:
            print("资料库回执只含第 2 版及许可，市场把它与条目原先保存的摘要写进同一条记录。")

    repo = MagicMock()
    repo.transaction = ledger.transaction
    bot, demand, response = uuid4(), uuid4(), uuid4()
    repo.get_knowbot = AsyncMock(return_value=dict(id=bot, owner_subject="seller", name="专家", price=None, publisher_id=None))
    repo.has_bought_expert = AsyncMock(return_value=False)
    repo.demands_of = AsyncMock(return_value=[dict(id=demand, status="chosen", chosen_response_id=response)])
    repo.get_response = AsyncMock(return_value=dict(listing_kind="expert", listing_ref=f"{bot}@2"))
    repo.add_trade = AsyncMock(side_effect=lambda fields: dict(id=uuid4(), target_app=None,
                                    status="done", created_at=datetime.now(UTC), **fields))
    repo.update_demand = AsyncMock()
    receipt = await MarketService(repo, None, None).record_summon(buyer="buyer", knowbot_id=str(bot), version="1")
    assert receipt["listing_ref"] == f"{bot}@1" and receipt["demand_id"] == str(demand)
    repo.update_demand.assert_awaited_once_with(demand, status="closed")
    print("选定响应附的是专家 v2，另请 v1 仍会关闭该需求。")


if __name__ == "__main__":
    asyncio.run(check())
