"""Use the author submission path with a synthetic market HTTP response."""
import httpx
import pytest

from app.infrastructure.external.knowbot_clients import KnowmartDeliveryClient
from tests.test_knowbot_clients import FakeOidc, KNOWMART
from tests.test_knowbot_experts import OWNER, SELF, Parts, user_token


@pytest.mark.parametrize("receipt", [
    {"knowbot_id": "example"},
    {"knowbot_id": "example", "version": "9", "digest": "invalid"},
])
async def test_unverified_market_receipt_does_not_finish_delivery(receipt):
    world = Parts()
    _, expert, _ = await world.self_expert()
    world.deliveries.knowmart = KnowmartDeliveryClient(
        KNOWMART, oidc_client=FakeOidc(),
        transport=httpx.MockTransport(lambda _: httpx.Response(201, json=receipt)),
    )
    delivery = await world.deliveries.submit(OWNER, str(expert.id), SELF, user_token)
    saved = await world.repo.get_expert(expert.id)
    assert delivery.delivered_at is None and saved.listed_at is None, (delivery.receipt, saved.digest)
