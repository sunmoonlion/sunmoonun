"""Follow a legal citation URL through the normal source resolver."""
import httpx
import pytest
from app.main import app
from app.interfaces.http.middleware.auth import get_web_current_user
from app.application.dto.retrieval import Citation, KnowledgeRetrievalResponse
from test_interaction_contract import principal
from test_knowledge_retrieval import _example


@pytest.mark.asyncio
async def test_contract_example_source_link_can_be_resolved(monkeypatch):
    evidence = KnowledgeRetrievalResponse.model_validate(_example("response.json")).evidence[0]
    path = Citation.from_evidence(evidence).source_href
    monkeypatch.setitem(app.dependency_overrides, get_web_current_user, principal)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get(path)
    assert response.status_code != 503, response.text
