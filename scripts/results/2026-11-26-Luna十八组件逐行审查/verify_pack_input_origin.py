"""执行计划、作者说明应指向生成输入的同一步。"""
from app.domain.workbench.fixed_plan import fixed_plan
from app.domain.workbench.pack_view import pack_view
from app.domain.workbench.packs import ExpertPack, StepContract


def test_same_named_intermediate_uses_different_source_in_preview():
    steps = tuple(
        StepContract(
            step_id=name, title=name, method_text="copy",
            input_refs=inputs, output_artifact=output,
        )
        for name, inputs, output in (
            ("draft", (), "figures"),
            ("verified", ("figures",), "figures"),
            ("report", ("figures",), "result"),
        )
    )
    pack = ExpertPack(pack_id="demo", profile_id="demo", version="1", title="核验", workflow=steps)
    assert fixed_plan(pack).steps[-1].inputs[0].instance_id == "verified"
    assert pack_view(pack)["steps"][-1]["uses"][0]["title"] == "draft"
