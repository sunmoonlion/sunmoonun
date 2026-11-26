"""Synthetic financial disclosures through KnowBase's ordinary query handlers."""
from decimal import Decimal
from types import SimpleNamespace

from test_user_facts_db import ALICE, Y2025, db, world
from app.interfaces.endpoints.user_fact_routes import chart, market_facts, market_metrics
from app.interfaces.schemas.user_facts import FactQueryIn, MetricQueryIn

owner = SimpleNamespace(subject=ALICE)


async def test_chart_preserves_unmapped_element_reason():
    payload = (await chart(owner)).model_dump()
    item = next(row for row in payload["items"] if row["code"] == "IS.RND")
    assert payload.get("cas_taxonomy") and item.get("cas_note")


async def test_fact_result_can_identify_exact_row_again(world):
    await world.publish("600519.SH", 1500, 300, 1300)
    rows = await market_facts(FactQueryIn(codes=["IS.REVENUE"]), owner, world.runs)
    assert all(row.model_dump().get("ref") for row in rows) and rows


async def test_standard_label_filter_does_not_return_unrelated_rows(world):
    await world.publish("600519.SH", 1500, 300, 1300)
    rows = await market_facts(FactQueryIn(labels=["营业收入"]), owner, world.runs)
    assert all(row.label == "营业收入" for row in rows)


async def test_metric_filter_respects_requested_minimum(world):
    await world.publish("600519.SH", 1500, 300, 1300)
    rows = await market_metrics(MetricQueryIn(metric="gross_margin", period_from=Y2025,
                                               value_min=Decimal("0.95")), owner, world.runs)
    assert all(row.value is not None and row.value >= Decimal("0.95") for row in rows)


async def test_old_personal_reference_does_not_hide_public_correction(db):
    from test_public_originals_db import World
    from test_user_data import CSV
    from app.domain.public_access import PublicGate

    available = World(db, gate=PublicGate())
    await available.deliver(references=[(ALICE, "old-reference")])
    _, corrected, _ = await available.deliver(content=CSV + b"9,9\n")
    with_reference = (await available.resolve(ALICE)).items[0]
    without_reference = (await available.resolve("bob")).items[0]
    assert without_reference.chosen[0].version_no == corrected.version_no
    assert corrected.version_no in {c.version_no for c in with_reference.chosen + with_reference.candidates}
