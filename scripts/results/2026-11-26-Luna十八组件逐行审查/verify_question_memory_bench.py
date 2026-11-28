"""KnowBench 代答器的实际决定，捕获它交给工作台的答复。"""
from types import SimpleNamespace
from unittest.mock import AsyncMock
from app.application.workbench import test_runs as runtime
from app.domain.workbench.test_runs import RunCase


async def resolved(monkeypatch, labels, remembered, live):
    handoff = AsyncMock()
    monkeypatch.setattr(runtime, "answer_interaction", handoff)
    repo = SimpleNamespace(get_test_answer=AsyncMock(return_value=live),
                           interaction_token=AsyncMock(return_value="fixture"))
    interaction = {"id":"i", "kind":"question","session_id":"s",
                   "prompt":{"subject":{"ask_before":True,"questions":[{
                       "id":"period","question":"选择年份范围","options":labels}]}}}
    case = RunCase(case_id="c1", input={"question":"分析年报","answers":remembered})
    conductor = runtime.KnowbotTestConductor(None)
    assert await conductor._respond_if_ready(repo, {"run_id":"r"}, case, interaction,
                                              SimpleNamespace(actor_id="author"))
    return handoff.await_args.kwargs["response"]["answers"]["period"]


async def test_reordered_choices_change_a_remembered_answer(monkeypatch):
    previous = [{"id":"o1","label":"三年"},{"id":"o2","label":"五年"}]
    reordered = [{"id":"o1","label":"五年"},{"id":"o2","label":"三年"}]
    assert await resolved(monkeypatch, previous, {}, {"answer":{"option_id":"o1"}}) == "三年"
    assert await resolved(monkeypatch, reordered, {"period":"o1"}, None) == "五年"


async def test_first_run_and_retest_choose_different_text(monkeypatch):
    labels = [{"id":"3y","label":"近三年"}]
    given = {"answer":{"option_id":"3y","text":"只取有完整披露的年份"}}
    assert await resolved(monkeypatch, labels, {}, given) == "只取有完整披露的年份"
    assert await resolved(monkeypatch, labels, {"period":"3y"}, None) == "近三年"
