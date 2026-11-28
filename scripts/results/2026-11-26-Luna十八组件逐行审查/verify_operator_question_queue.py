"""Use one waiting test with a data question and ordinary questions."""
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock

from tests.knowbot_fakes import waiting
from tests.test_knowbot_test_data import world

from app.application.services.knowbot_questions import KnowbotQuestionService
from app.interfaces.endpoints.knowbot_routes import open_questions


async def test_operator_and_unrelated_author_queues(world, monkeypatch):
    svc, _, repo, runtime, _, _, _, run = world
    runtime.results[run.run_id] = waiting(run.run_id)
    await svc.refresh(str(run.id))
    asks = KnowbotQuestionService(repo, runtime)
    response = await open_questions(None, asks)
    body = json.loads(response.body)
    assert sorted(q["kind"] for q in body["questions"]) == [
        "ask_before", "data", "question", "tool_approval"]
    if os.environ.get("LUNA_QUEUE_RESPONSE"):
        Path(os.environ["LUNA_QUEUE_RESPONSE"]).write_bytes(response.body)
    for name in ("find_test_by_run", "get_draft", "get_request"):
        monkeypatch.setattr(repo, name, AsyncMock(wraps=getattr(repo, name)))
    assert await asks.user_queue("author-with-no-requests") == []
    assert [getattr(repo, name).await_count for name in
            ("find_test_by_run", "get_draft", "get_request")] == [4, 4, 4]
