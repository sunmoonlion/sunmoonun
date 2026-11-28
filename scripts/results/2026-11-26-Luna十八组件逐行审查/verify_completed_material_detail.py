"""Emit the operator detail before and after the author confirms resolved material."""
from pathlib import Path
import os
import json
from tests.test_knowbot_test_data import world, token, OWNER
from app.application.services.knowbot_board import KnowbotBoard
from app.application.services.knowbot_questions import KnowbotQuestionService
from app.interfaces.endpoints.knowbot_routes import request_detail


async def test_confirmed_material_enters_detail(world):
    svc, data, repo, runtime, kb, _, draft, run = world
    kb.fetched = True
    ask = KnowbotQuestionService(repo, runtime)

    async def detail():
        response = await request_detail(None, svc, KnowbotBoard(repo), ask, str(draft.request_id))
        return json.loads(response.body)

    before = await detail()
    [row] = await data.pending(OWNER, str(run.id), token)
    await data.confirm(OWNER, row["question_id"], token)
    after = await detail()
    assert before["answered"] == []
    [answer] = after["answered"]
    assert answer["kind"] == "data" and len(answer["answer"]["data"]["items"]) == 2
    if target := os.getenv("LUNA_COMPLETED_DETAIL"):
        Path(target).write_text(json.dumps([before, after]))
