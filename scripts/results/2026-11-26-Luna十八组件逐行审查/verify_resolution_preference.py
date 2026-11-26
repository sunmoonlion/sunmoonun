"""用 KnowBase 的数据库夹具核对同一需求记偏好前后的解析结果。"""
from test_user_resolution_db import ALICE, CSV, annual, db, world


async def test_preference_does_not_fill_remaining_places(world):
    first, _ = await world.report(ALICE, 2025, name="a.csv")
    second, _ = await world.report(ALICE, 2025, name="b.csv", origin_csv=CSV + b"x")
    need = annual(count=1, min_count=2, max_count=2)
    before = (await world.resolve([need])).items[0]
    assert {c.material_id for c in before.chosen} == {first.id, second.id}
    await world.resolver.record_preference(ALICE, "expert:fa-1@2", before.key, [first.id])
    after = (await world.resolve([need])).items[0]
    assert before.key == after.key and after.status == "to_confirm"
