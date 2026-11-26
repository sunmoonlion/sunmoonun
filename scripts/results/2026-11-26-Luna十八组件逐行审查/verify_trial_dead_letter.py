"""真实 PostgreSQL、项目试采和消息消费代码。模拟适配器本次无法启动，再恢复。"""
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from test_durable_delivery_db import age_published, db as db, sql
from app.application.supply.catalog import TrialRunner
from app.domain.supply.catalog import ChannelEvent, Trial
from app.domain.supply.models import Channel
from app.infrastructure.messaging.durable_tasks import DurableTasks
from app.infrastructure.repositories.supply_catalog import SqlCatalogRepository, TRIAL_TOPIC


async def test_exhausted_delivery_leaves_business_trial_running_until_replay(db):
    now = datetime.now(UTC)
    uid = lambda: str(uuid4())
    repo = SqlCatalogRepository(lambda: db)
    channel = Channel("trial-local", "test", "web", "web", ("webpage",), ("text",),
                      "self", "pending", 1, 10, 2, created_at=now, updated_at=now)
    await repo.add_channel(channel, ChannelEvent(uid(), channel.id, "register", "author", None, {}, now))
    trial = Trial(uid(), channel.id, {"url":"https://example.org/fixture"}, "queued", "author", now)
    await repo.add_trial(trial)
    unavailable = True

    class Adapter:
        async def fetch_url(self, url):
            return b"fixture", "text/plain", url

    def build(_):
        if unavailable:
            raise RuntimeError("local initialization error")
        return Adapter()

    async def handle(session, payload):
        await TrialRunner(repo, build).run(payload["trial_id"])

    runtime = DurableTasks(db, handlers={TRIAL_TOPIC: handle}, max_attempts=1)
    msg = await runtime.claim_delivery()
    await runtime.finish_delivery(msg)
    with pytest.raises(RuntimeError, match="local initialization error"):
        await runtime.consume(msg["id"])
    await age_published(db)
    await runtime.reconcile()
    assert await sql(db, "SELECT error_code FROM outbox_dead_letter") == "consumer_unacknowledged"
    assert (await repo.latest_trial(channel.id)).status == "running"
    assert await runtime.consume(msg["id"]) is False
    unavailable = False
    await runtime.replay(msg["id"])
    assert await runtime.consume(msg["id"])
    assert (await repo.latest_trial(channel.id)).status == "ok"
