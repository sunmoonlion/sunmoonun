"""The author must receive a client validation error for a missing review reason."""
from uuid import uuid4

import httpx
import pytest

from app.main import app
from tests.test_knowbot_lab_routes import wired
from tests.test_knowbot_workdraft_routes import WEB, WEB_SID


@pytest.mark.asyncio
async def test_blank_rejection_note(wired):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        client.cookies.set(WEB_SID, "member")
        response = await client.post(
            f"/api/web/v1/knowbot-drafts/{uuid4()}/review",
            headers=WEB,
            json={"ok": False, "note": "  "},
        )
    assert response.status_code == 422
