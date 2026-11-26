"""相同路由有两条沙箱专用凭据，检查预览及派发是否选择同一条。"""
import asyncio
from functools import partial
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from app.application.workbench.branch_review_dispatch import dispatch_choices
from app.application.workbench.instruction_requests import InstructionRequests
from app.application.workbench.reviewer_choices import ReviewerChoices
from app.domain.workbench.instruction_requests import InstructionRoute
from app.domain.workbench.pricing import DEFAULT_PRICES
from app.domain.workbench.review_routes import ReviewRoute


async def main():
    url = "https://example.test/v1"
    route = InstructionRoute("one","kimi-k3",url,"kimi-k3",1000,100)
    policy = ReviewerChoices((ReviewRoute(provider="one",model="kimi-k3"),),(),(route,),
                             DEFAULT_PRICES,"one","kimi-k3",url)
    creds = [dict(id=str(uuid4()),sandbox_id=str(uuid4()),provider="one",
                  base_url=url,status="active") for _ in range(2)]
    sandbox = creds[1]["sandbox_id"]
    repo = AsyncMock()
    repo.list_credentials.return_value = creds
    repo.get_prefs.return_value = {}
    repo.reviewer_preference.return_value = None
    repo.model_request_credential.side_effect = lambda owner, key: next(c for c in creds if c["id"] == key)
    repo.find_task_by_idempotency.return_value = None
    repo.list_sessions.return_value = []
    repo.direct_registrations.return_value = []
    options = (await policy.choices(repo,"author",sandbox=sandbox))["options"]
    assert [o["pin"]["credential_id"] for o in options] == [creds[1]["id"]]
    checked = SimpleNamespace(sandbox_id=sandbox,page={"review_digest":"review",
        "confirmed":"option","requirement":"isolated_reviewer","options":[dict(options[0],digest="option")]})
    executions = SimpleNamespace(repo=repo,capabilities=SimpleNamespace(
        formal_sources=SimpleNamespace(repo=repo),instruction_service=partial(
            InstructionRequests.for_account,routes=(route,),model="kimi-k3",prices=DEFAULT_PRICES,default_url=url)))
    assert await dispatch_choices(executions,"author",checked) == {"unavailable":"executorUnavailable"}
    repo.list_credentials.return_value = creds[::-1]
    assert await dispatch_choices(executions,"author",checked) == {"sessions":[],"sources":[]}


asyncio.run(main())
