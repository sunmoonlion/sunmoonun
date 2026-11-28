"""在当前任务编排的通用文件步骤上核对作者指定的成稿格式。"""
from app.application.workbench.task_runtime import TaskRuntime
from app.domain.workbench.packs import StepContract


def test_generating_a_translation_inherits_investment_report_format():
    step = StepContract(step_id="translate", title="翻译参观须知",
                        method_text="只交付面向游客的一段英文译文，保留原段落。",
                        output_artifact="translation", output_file="notice.md")
    prompt = TaskRuntime.compose(step, {"text": "请翻译参观须知"}, {}, 0)
    assert step.method_text in prompt
    assert "Sections, in this order" in prompt
    assert "buy/sell recommendation" in prompt


def test_purchase_transcription_hits_securities_check_in_a_generic_method():
    from app.application.workbench.acceptance import judge
    from app.domain.workbench.method_catalog import MethodUnit
    unit = MethodUnit.model_validate({
        "selection": {"applies_when": "采购表转录", "required": True, "max_calls": 1},
        "contract": {"step_id": "copy", "title": "采购表转录", "method_text": "逐字抄录采购摘要。",
                     "output_artifact": "copy", "output_schema": {"summary": "string"},
                     "acceptance": [{"kind":"json_object"}, {"kind":"required_keys","keys":["summary"]},
                                    {"kind":"no_positioning_advice"}]},
    })
    verdict = judge('{"summary":"会议用纸采购目标价为每包二十元。"}', unit.contract.acceptance)
    assert not verdict.ok
    assert [r["rule"] for r in verdict.checks if not r["pass"]] == ["no_positioning_advice"]


def test_large_adjacent_integer_ids_compare_equal():
    from app.application.workbench.acceptance import judge
    from app.domain.workbench.packs import AcceptanceRule
    rule = AcceptanceRule(kind="all_equal", path="rows", field="id", equals=9007199254740992)
    assert judge('{"rows":[{"id":9007199254740993}]}', (rule,)).ok
