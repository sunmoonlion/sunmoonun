"""一位受益人有两笔不同委托时，应能分别对齐每项交付记录。"""
from tests.test_supply_collected_readings_db import db as db, job_of, world


async def test_missing_second_receipt_becomes_ready(db):
    w = await world(db)
    first, a, _ = await w.submit(readings=("original",))
    second, b, _ = await w.submit(idem="another-sample-02", readings=("original",))
    assert first.id != second.id and a[0].basis_ref != b[0].basis_ref
    deliver = w.knowbase.deliver_collected
    async def first_only(**kw):
        both = await deliver(**kw)
        assert len(both) == 2
        return both[:1]
    w.knowbase.deliver_collected = first_only
    assert await w.runner.run(await job_of(db,a[0].id)) == "done"
    for demand in (first, second):
        _, items = await w.demands.get("knowbench", demand.id)
        assert items[0].status == "ready"
