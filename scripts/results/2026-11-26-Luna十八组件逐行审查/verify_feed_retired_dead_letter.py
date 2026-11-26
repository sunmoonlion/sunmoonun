"""死信有独立外键。使用与原回归相同的 0018 真实库和旧任务。"""
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from tests.test_drop_security_line_db import _seed, at_0018 as at_0018


async def test_old_dead_letter_blocks_upgrade(at_0018):
    engine, migrate = at_0018
    await _seed(engine)
    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO outbox_dead_letter(message_id,error_code)
            SELECT id,'handler_failed' FROM outbox_message WHERE topic='knowfeed.security.ingest.v1'
        """))
    with pytest.raises(IntegrityError) as error:
        await migrate("upgrade")
    assert error.value.orig.sqlstate == "23503"
