"""Exercise KnowLab's real response handling with synthetic upstream responses."""
from unittest.mock import AsyncMock

import httpx
import pytest

from app.application.errors.exceptions import AppException
from app.infrastructure.external.knowbase_delivery import KnowbaseDelivery


def client(response):
    service = KnowbaseDelivery(
        {"KNOWBASE_INTERNAL_URL": "https://base.invalid"},
        transport=httpx.MockTransport(lambda _: response),
    )
    service._service_token = AsyncMock(return_value="synthetic")
    return service


async def test_end_requires_success_status():
    service = client(httpx.Response(307, headers={"Location": "/new"}))
    with pytest.raises(AppException):
        await service.end_platform(subject="author", kind="review", ref="case", reason="end")


async def test_freeze_requires_every_binding():
    service = client(httpx.Response(200, json=["incomplete binding"]))
    with pytest.raises(AppException):
        await service.freeze("expert", "1", author="author")


async def test_evidence_requires_reported_version():
    service = client(httpx.Response(200, json={"material_id": "example"}))
    with pytest.raises(AppException):
        await service.write_output(beneficiary="author", task_ref="task", run_ref="run",
            name="evidence", content=b"example", expert_id="expert", expert_version="1")
