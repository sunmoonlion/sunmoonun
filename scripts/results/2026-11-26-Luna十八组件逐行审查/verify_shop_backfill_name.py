"""比较同一普通昵称经小店迁移和应用初始化得到的店名。"""
from sqlalchemy import text
from app.domain.market import default_shop_name
from tests.test_shop_migration_db import _run, engine as engine


async def test_existing_and_new_shop_name_disagree(engine):
    name = " " * 5 + "青" * 40
    async with engine.begin() as conn:
        await conn.execute(text("""
            INSERT INTO demand(id,buyer_subject,kind,title,problem,deadline)
            VALUES (gen_random_uuid(),'customer','expert','sample','question',current_date)
        """))
        await conn.execute(text("""
            INSERT INTO auth_user(id,issuer,subject,display_name,roles,scopes)
            VALUES(gen_random_uuid(),'test','customer',:name,'[]','[]')
        """), {"name": name})
        await conn.run_sync(lambda sync: _run(sync, target=True))
        migrated = await conn.scalar(text("SELECT name FROM shop WHERE owner_subject='customer'"))
    assert (len(migrated), len(default_shop_name(name))) == (35, 40)
