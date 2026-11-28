"""在 agy 后端环境复验作者服务与编译器；仓储、来源引用均仅在本地测试中存在。"""

import asyncio
import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from app.application.services.method_drafts import (
    CreateMethodDraftIn,
    MethodDraftService,
    PatchMethodDraftIn,
)
from app.domain.knowbots.formal_method import MethodDraftV2, MethodRef
from app.domain.knowbots.formal_method_compiler import FrozenMethod
from app.domain.knowbots.formal_method_plan import expand_unique_plan
from tests.test_formal_method_service import Repository

from drafts import patch, tools
from parent import contract


async def verify():
    service = MethodDraftService(Repository())
    owner = "local-m09-test"
    refs, resolved = {}, {}
    for name in (*tools, "parent"):
        leaf = name in tools
        title = tools[name][0] if leaf else "前五大客户与供应商集中度透视"
        created = await service.create(
            owner,
            CreateMethodDraftIn(title=title, method_kind="tool" if leaf else "expert"),
        )
        mid = created["method_id"]
        if leaf:
            path = Path(__file__).with_name(name + ".py")
            source = {
                "kind": "registered_script",
                "source": str(uuid4()),
                "version": "1",
                "entry": path.name,
                "asset_id": None,
                "asset_revision": None,
                "license_basis": "本地试验",
                "digest": "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            cmd = patch(name, source, created["revision"])
        else:
            cmd = {"draft_contract": contract(refs), "revision": created["revision"]}
        view = await service.patch(owner, mid, PatchMethodDraftIn.model_validate(cmd))
        assert view["provenance_verified"] and view["projection"]["ready_to_freeze"]
        await service.ensure_runtime_anchor(owner, mid)
        definition = MethodDraftV2.model_validate(
            view["draft_contract"]
        ).to_definition()
        if leaf:
            ref = MethodRef(method_id=UUID(mid), version=1, digest=definition.digest())
            refs[name] = ref.model_dump(mode="json")
            resolved[ref.method_id, 1] = FrozenMethod(ref, definition)
        else:
            plan = expand_unique_plan(UUID(mid), definition, resolved)
            assert plan.steps == 3 and len(plan.dependencies) == 2
    print("agy 作者服务：2 个工具稿、1 个专家稿通过；2 个不同工具展开为 3 次调用。")


if __name__ == "__main__":
    asyncio.run(verify())
