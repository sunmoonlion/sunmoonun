"""与 KnowLab 的 test_knowbot_questions.py 一起运行，使用内存仓和模拟运行端。"""
from tests.test_knowbot_questions import testing
from tests.knowbot_fakes import OWNER, result
from app.application.services.knowbot_questions import AnswerIn


async def test_ended_question_can_still_be_reassigned(testing):
    svc, asks, repo, runtime, _, _, run, questions = testing
    runtime.results[run.run_id] = result(run.run_id, "error")
    await svc.refresh(str(run.id))
    assert repo.tests[run.id].status == "platform_error"
    q = questions["q-scope"]
    assert not await asks.operator_queue()
    await asks.take(str(q.id), "确认测试已经结束")
    assert repo.questions[q.id].route == "operator"
    await asks.to_user(str(q.id))
    assert repo.questions[q.id].route == "user"


async def test_answer_changes_between_live_delivery_and_retest(testing):
    svc, asks, _, runtime, _, draft, run, questions = testing
    await asks.answer_as_user(OWNER, str(questions["q-scope"].id),
                              AnswerIn(option_id="3y", text="只取有完整披露的年份"))
    transmitted = runtime.answers[-1][1].answers[0]
    assert (transmitted.option_id, transmitted.text) == ("3y", "只取有完整披露的年份")
    runtime.results[run.run_id] = result(run.run_id, "error")
    await svc.refresh(str(run.id))
    await svc.start_test(str(draft.id), budget_limit="20", timeout_seconds=600)
    assert runtime.started[-1][1].cases[0].input.answers == {"period": "3y"}


def test_dynamic_compilation_reuses_option_id_after_reordering():
    from tests.dynamic_method_fixtures import body, build
    for labels in (["三年", "五年"], ["五年", "三年"]):
        doc = body()
        doc["steps"][0]["ask_before"] = [
            {"id": "period", "question": "选择年份范围", "options": labels}
        ]
        manifest, problems = build(doc)
        assert not problems
        assert manifest["schema"] == "knowbot-manifest/v3"
        [ask] = manifest["pack"]["method_units"][0]["contract"]["ask_before"]
        assert ask["options"] == [
            {"id": "o1", "label": labels[0]}, {"id": "o2", "label": labels[1]}
        ]
