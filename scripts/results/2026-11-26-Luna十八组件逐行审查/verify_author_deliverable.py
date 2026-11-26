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
