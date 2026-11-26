"""A text reading with no stored body cannot be advertised as ready after 0019."""
import pytest
from sqlalchemy import text
from test_readings_migration_db import _seed, at_0018


@pytest.mark.asyncio
async def test_ready_text_has_content_or_is_marked_failed(at_0018):
    engine, migrate = at_0018
    ids = await _seed(engine)
    async with engine.begin() as conn:
        await conn.execute(text("UPDATE user_data_rendition SET object_key=NULL WHERE id=:id"), {"id": ids["text"]})
    await migrate("upgrade")
    async with engine.begin() as conn:
        row = (await conn.execute(text("""
            SELECT r.status, t.body IS NOT NULL AS has_content
            FROM user_data_rendition r LEFT JOIN user_data_text t ON r.id=t.rendition_id
            WHERE r.id=:id
        """), {"id": ids["text"]})).one()
    assert row.status != "ready" or row.has_content
