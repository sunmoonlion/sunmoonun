"""Synthetic upstream responses at the actual service adapter boundary."""
import httpx
import pytest
from test_ragflow_receipt_api import provider
from app.application.ports.knowledge_provider import ProviderProtocolError, ProviderTimeoutError


@pytest.mark.parametrize("chunks", [None, {}, ""])
async def test_invalid_chunks_do_not_look_like_empty_search(chunks):
    def respond(request):
        return httpx.Response(200, json={"code": 0, "data": {"chunks": chunks, "total": 1}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ProviderProtocolError):
            await provider(client).retrieve(question="q", dataset_ids=["s"], document_ids=["d"], top_k=1)


async def test_repeated_dataset_page_is_not_proof_of_exhaustion():
    def respond(request):
        return httpx.Response(200, json={"code": 0, "total_datasets": 2,
                                        "data": [{"name": "first", "id": "one"}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ProviderProtocolError):
            await provider(client).find_datasets("second")


async def test_document_lookup_maps_bad_total_to_protocol_error():
    def respond(request):
        return httpx.Response(200, json={"code": 0, "data": {"docs": [], "total": "unknown"}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ProviderProtocolError):
            await provider(client).find_documents("s", "doc.txt")


async def test_content_verification_preserves_timeout():
    def respond(request):
        raise httpx.ReadTimeout("synthetic timeout", request=request)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ProviderTimeoutError):
            await provider(client).verify_document_content("s", "d", size=1, sha256="0" * 64)


async def test_config_check_rejects_invalid_dataset_listing(monkeypatch):
    from app.infrastructure.external import ragflow
    from core.config import Settings

    def respond(request):
        data = {"unexpected": "shape"} if request.url.path.endswith("/datasets") else {"embd_id": "model"}
        return httpx.Response(200, json={"code": 0, "data": data})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
        client = provider(http)
        monkeypatch.setattr(ragflow, "RAGFlowClient", lambda settings: client)
        check = await ragflow.check_ragflow_config(Settings(RAGFLOW_API_BASE="https://test.invalid", RAGFLOW_API_KEY="test-only"))
    assert check.issues or not check.reachable
