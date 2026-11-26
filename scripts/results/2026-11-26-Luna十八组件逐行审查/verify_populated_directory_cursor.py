"""在 KnowBench 后端 app 下用 PYTHONPATH=.:tests 运行，固定两页目录顺序。"""
import asyncio

from app.application.workbench.formal_expert_intake import directory_for
from test_formal_expert_intake_db import Registry
from test_workbench_ledger_db import OWNER


class TwoPages(Registry):
    async def planning_versions(self, owner, limit, offset, *, query):
        refs = list(self.entries.values())
        if offset == 0:
            return {"items": [refs[0]["reference"]], "next": 96}
        assert offset == 96
        return {"items": [refs[1]["reference"]], "next": None}


async def verify():
    registry = TwoPages()
    first = await directory_for(registry, OWNER, "核对交易", None)
    second = await directory_for(registry, OWNER, "核对交易", None, offset=96)
    assert first["items"] and first["more"] and "next" not in first
    assert second["items"][0] != first["items"][0]


if __name__ == "__main__":
    asyncio.run(verify())
