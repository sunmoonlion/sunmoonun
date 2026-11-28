"""用可计数的内存目录核验分类翻页的跨服务读取量。无需账号或数据库。"""
import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

backend = Path(__file__).resolve().parents[4] / "knowbench-app/knowbench-backend/app"
sys.path.insert(0, str(backend))
from app.application.workbench.directory_browse import browse
from app.domain.workbench.formal_method_generated import MethodRef
from app.domain.workbench.method_search import DirectoryBrowse, DirectoryCategory


class Registry:
    def __init__(self):
        self.market = self.repo = self
        self.window_calls = self.label_calls = self.label_refs = 0
        self.refs = [MethodRef(method_id=UUID(int=i), version=1, digest="sha256:" + "a"*64)
                     for i in range(1, 10001)]
        self.category = DirectoryCategory(code="data.lookup", group="data", name="查找", group_name="数据")

    @asynccontextmanager
    async def transaction(self, **kwargs):
        yield

    async def actor_for_subject(self, subject):
        return subject

    async def planning_window(self, subject, offset, limit):
        self.window_calls += 1
        return self.refs[offset:offset + limit], offset + limit < len(self.refs)

    async def directory_labels(self, subject, refs):
        self.label_calls += 1
        self.label_refs += len(refs)
        return SimpleNamespace(categories={"tool": [self.category]}, items=[
            SimpleNamespace(reference=r, kind="tool", category=self.category.code) for r in refs
        ])

    async def registry_method_candidates(self, owner, limit, offset, *, eligible, **kwargs):
        return [{**r, "method_kind": "tool"} for r in eligible[offset:offset + limit]]

    def reference(self, row):
        return {k: row[k] for k in ("method_id", "version", "digest")}


async def check():
    reg = Registry()
    for offset in (0, 30):
        before = reg.window_calls, reg.label_calls, reg.label_refs
        result = await browse(reg, "author", "planning", DirectoryBrowse(kind="tool", offset=offset))
        assert result["total"] == 10000 and len(result["items"]) == 30
        counts = tuple(b - a for a, b in zip(before, (reg.window_calls, reg.label_calls, reg.label_refs)))
        assert counts == (100, 101, 10000)
        print(f"offset={offset} 返回 30 条；读取授权 100 次、分类 101 次，查询 10000 个引用的标签。")


if __name__ == "__main__":
    asyncio.run(check())
