"""在 KnowBench 后端 app 下以 PYTHONPATH=.:tests 运行；目录顺序固定以隔离匹配逻辑。"""
import asyncio
from test_formal_expert_intake_db import Registry
from test_workbench_ledger_db import OWNER
from app.application.workbench.formal_expert_intake import directory_for
from app.domain.workbench.errors import StaleStateVersion

async def main():
    registry = Registry()
    original, later = list(registry.definitions)
    definition = registry.definitions.pop(original)
    doc = definition.document()
    doc["capability_declaration"].update(
        purpose="逐项核对有来源的明细并列出差异。" * 1100,
        applies_when=["用户提供原始明细。" * 900],
    )
    definition = type(definition).model_validate(doc)
    large = original.model_copy(update={"digest":definition.digest()})
    registry.definitions[large] = definition
    registry.entries = {
        large: registry.public_declaration(large, definition),
        later: registry.entries[later],
    }
    try:
        await directory_for(registry,OWNER,"需要差异表",None)
    except StaleStateVersion as exc:
        assert "exceeds the matching context" in str(exc)
    else:
        raise AssertionError("当前版本不再因第一个候选过长而整轮失败")
    page = await directory_for(registry,OWNER,"需要差异表",later)
    assert page["items"][0]["reference"] == later.model_dump(mode="json")

if __name__ == "__main__":
    asyncio.run(main())
