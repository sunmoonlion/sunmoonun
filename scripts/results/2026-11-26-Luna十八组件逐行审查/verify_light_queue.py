"""Compare the two operator queues before and after accepting a test-only grant."""
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from tests.knowbot_fakes import manifest, request_body
from tests.test_knowbot_creation_routes import ADMIN, ADMIN_SID, WEB, WEB_SID, client, wired


@pytest.mark.asyncio
async def test_light_acceptance_queue(wired):
    _, repo, *_ = wired
    root = "/api/admin/v1"
    async with client() as c:
        c.cookies.set(WEB_SID, "member")
        c.cookies.set(ADMIN_SID, "admin")
        body = request_body(mode="self")
        body.pop("budget_limit", None)
        created = await c.post("/api/web/v1/knowbot-requests", json=body, headers=WEB)
        created.raise_for_status()
        draft = await repo.create_draft(request_id=UUID(created.json()["request_id"]),
            request_version=1, revision=1, version="1", manifest=manifest(), mode="self")
        asked = await c.post(f"/api/web/v1/knowbot-drafts/{draft.id}/platform-test",
            json={"agree": True, "budget_limit": "5"}, headers=WEB)
        asked.raise_for_status()
        grant = asked.json()["grant"]["grant_id"]
        for expected in ("light_pending", "light_accepted"):
            queue = (await c.get(root + "/knowbot-board/acceptance")).json()["items"]
            assert [row["category"] for row in queue] == [expected]
            counts = (await c.get(root + "/knowbot-counts")).json()["counts"]
            assert (counts["acceptance"], counts["tests"]) == (0, 1)
            tests = (await c.get(root + "/knowbot-board/tests")).json()["items"]
            assert [(row["draft"]["draft_id"], row["category"]) for row in tests] == [
                (str(draft.id), "to_start")]
            if expected == "light_pending":
                decision = await c.post(root + f"/knowbot-grants/{grant}/decision",
                                        json={"accepted": True}, headers=ADMIN)
                decision.raise_for_status()

        await repo.update_grant(UUID(grant), expires_at=datetime.now(UTC) - timedelta(days=400))
        detail = await c.get(f"/api/web/v1/knowbot-requests/{created.json()['request_id']}")
        detail.raise_for_status()
        assert detail.json()["grants"][0]["state"] == "expired"
        again = await c.post(f"/api/web/v1/knowbot-drafts/{draft.id}/platform-test",
                             json={"agree": True, "budget_limit": "5"}, headers=WEB)
        assert again.status_code == 409 and "grant_exists" in again.text
