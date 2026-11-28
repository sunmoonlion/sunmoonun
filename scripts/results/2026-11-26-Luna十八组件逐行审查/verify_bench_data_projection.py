"""核实已通过模型校验的步骤在数据准备环节能否保留末尾必需资料。"""
from app.application.workbench.task_runtime import compose_data_plan
from app.domain.workbench.packs import ExpertPack, SMOKE


def test_late_requirement_is_missing_from_step_zero():
    data = SMOKE.model_dump(mode="json")
    requirement = "取上一年度审定期初余额及原始页码。"
    data["workflow"][0]["method_text"] = "核对当期记录。" * 201 + requirement
    pack = ExpertPack.model_validate(data)
    assert requirement in pack.workflow[0].method_text
    prompt = compose_data_plan(pack, {"text": "请核对期初余额"}, "task-review", 0)
    assert requirement not in prompt
