"""在一次性 schema 中用 0013 允许的成交记录检查 0014 的升级行为。"""
import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from tests.test_drop_manifest_v1_db import ROOT, _module, engine as engine


def migrate(connection, first, last):
    paths = sorted((ROOT / "alembic/versions").glob("20*.py"))
    with Operations.context(MigrationContext.configure(connection)):
        for path in paths:
            if first <= path.stem[:13] <= last:
                _module(path).upgrade()


async def test_old_trade_pair_blocks_upgrade(engine):
    async with engine.begin() as conn:
        await conn.run_sync(migrate, "20261028_0010", "20261030_0013")
        for _ in range(2):
            await conn.execute(text("""
                INSERT INTO trade(id,kind,buyer_subject,seller_subject,listing_ref,title)
                VALUES (gen_random_uuid(),'expert','buyer','author','expert@1','demo')
            """))
    with pytest.raises(IntegrityError, match="ix_trade_buyer_expert_ref"):
        async with engine.begin() as conn:
            await conn.run_sync(migrate, "20261101_0014", "20261101_0014")
    async with engine.connect() as conn:
        assert await conn.scalar(text("SELECT count(*) FROM trade")) == 2


async def test_migration_with_its_historical_fixture(engine, monkeypatch):
    from tests import test_drop_manifest_v1_db as migration_test
    from tests.knowbot_fakes import historical_manifest

    monkeypatch.setattr(migration_test, "manifest", historical_manifest)
    await migration_test.test_v1_versions_and_v1_only_experts_are_dropped(engine)
