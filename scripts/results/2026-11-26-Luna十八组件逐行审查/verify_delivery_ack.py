"""用模板 test_durable_delivery_db 的一次性 PostgreSQL fixture 运行。"""
from test_durable_delivery_db import db, request, runtime, sql


async def test_ack_before_publisher_crash(db):
    msg_id = await request(db)
    delivery = runtime(db, max_attempts=1)
    assert await delivery.claim_delivery()
    assert await delivery.consume(msg_id)
    await sql(db, "UPDATE outbox_message SET lease_expires_at='2000-01-01'")
    await delivery.reconcile()
    assert await sql(db, "SELECT value FROM delivery_test_counter") == 1
    assert await sql(db, "SELECT message_id FROM inbox_message") == msg_id
    assert await sql(db, "SELECT message_id FROM outbox_dead_letter WHERE replayed_at IS NULL") == msg_id


async def test_contended_resource_before_any_execution(db):
    first = await request(db, key="first")
    second = await request(db, key="second")
    delivery = runtime(db, max_attempts=2)
    held, _ = await delivery.claim_execution(first)
    for _ in range(2):
        msg = await delivery.claim_delivery()
        if msg["id"] == first:
            await delivery.finish_delivery(msg)
            msg = await delivery.claim_delivery()
        assert msg["id"] == second
        await delivery.finish_delivery(msg)
        assert await delivery.consume(second) is False
        await sql(db, "UPDATE outbox_message SET published_at='2000-01-01' WHERE id=:id", id=second)
        await delivery.reconcile()
    await delivery.release(held)
    assert not await delivery.consume(second)
    assert await sql(db, "SELECT message_id FROM outbox_dead_letter WHERE replayed_at IS NULL") == second
    assert await sql(db, "SELECT value FROM delivery_test_counter") == 0
