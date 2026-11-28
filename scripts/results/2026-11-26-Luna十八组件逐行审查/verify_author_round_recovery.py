"""KnowLab 作者服务，仓储与运行方沿用现有内存夹具。"""

import pytest

from app.application.errors.exceptions import ServiceUnavailableError
from tests.test_knowbot_incubation_service import FIRST, OWNER, _first_round, w


async def test_lost_submit_reply_recovers_existing_runtime(w, monkeypatch):
    request = await w.request()
    rid = str(request.id)
    original = w.incubator.start

    async def lost_reply(command):
        await original(command)
        raise ServiceUnavailableError("response lost")

    monkeypatch.setattr(w.incubator, "start", lost_reply)
    with pytest.raises(ServiceUnavailableError):
        await w.inc.start(OWNER, rid, action="draft")
    (record,) = w.repo.incubations.values()
    w.hand_back(record, FIRST)
    observed = await w.inc.refresh(OWNER, rid, str(record.id))
    assert observed.status == "succeeded"


async def test_quote_from_six_question_heading_is_not_author_text(w):
    request = await w.request()
    rid = str(request.id)
    record = await w.inc.start(OWNER, rid, action="draft")
    w.hand_back(record, {
        "sources": [{"path": "scope/does", "kind": "idea", "quote": "问：解决什么"}],
        "suggestions": [{"id":"s","op":"set","path":"scope/does","value":"按年预测三年利润","reason":"补全范围"}],
    })
    done = await w.inc.refresh(OWNER, rid, str(record.id))
    if done.review["s"]["verified"]:
        draft, _ = await w.inc.decide(OWNER,rid,str(record.id),"s",action="accept",revision=0)
        assert draft.sources["scope/does"]["kind"] != "user_text"


async def test_unchanged_proposal_is_not_an_author_edit(w):
    req, record = await _first_round(w)
    original = FIRST["suggestions"][2]
    saved, _ = await w.inc.decide(OWNER,str(req.id),str(record.id),original["id"],
        action="accept_edited",revision=0,value=original["value"])
    assert saved.sources["tagline"]["kind"] != "user_text"


async def test_later_active_round_gets_a_poll(w, monkeypatch):
    ids=[]
    for _ in range(3):
        request = await w.request()
        ids.append((await w.inc.start(OWNER,str(request.id),action="draft")).run_id)
    from app.application.services import knowbot_incubation as mod
    monkeypatch.setattr(mod, "REFRESH_BATCH", 2)
    polled=[]
    original=w.incubator.status
    async def status(run_id):
        polled.append(run_id)
        return await original(run_id)
    monkeypatch.setattr(w.incubator,"status",status)
    for _ in range(3):
        await w.inc.refresh_active()
    assert set(ids) == set(polled)

async def test_answer_history_can_span_multiple_full_rounds(w):
    from tests.test_knowbot_incubation_service import AnswerIn
    request = await w.request()
    rid = str(request.id)
    for total in (200, 1):
        record = await w.inc.start(OWNER, rid, action="draft")
        w.hand_back(record, {
            "gaps": [{"id": f"g{i}", "question": f"口径 {i}？", "proposal": "按金额"} for i in range(total)]
        })
        done = await w.inc.refresh(OWNER, rid, str(record.id))
        for gap in await w.inc.gaps(done):
            await w.questions.answer_as_user(OWNER, str(gap.id), AnswerIn(option_id="proposal"))
    await w.inc.start(OWNER, rid, action="revise", instruction="继续按已答口径整理")
