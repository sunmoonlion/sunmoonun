"""Point-in-time resolution and identity using the application's PostgreSQL fixture."""
from datetime import date

from test_user_resolution_db import ALICE, BOB, CSV, annual, db, world

from app.domain.user_resolution import DescriptionKey, PeriodRule, TaskParams, key_id
from dataclasses import replace


async def test_late_actual_disclosure_is_excluded_after_statutory_deadline(world):
    await world.report(ALICE, 2025, disclosed=date(2026, 7, 2))
    result = await world.resolve([annual(count=1)], TaskParams(date(2026, 6, 1)))
    assert all(not row.chosen for row in result.items)


async def test_nonempty_required_need_survives_fixed_window_without_year_end(world):
    need = replace(annual(count=1), period=PeriodRule("fixed", date(2025, 1, 1),
                                                      date(2025, 3, 31)))
    result = await world.resolve([need])
    assert any(row.need_key == "annual" for row in result.items)


def test_equivalent_topic_filters_find_same_preference():
    def ident(topics):
        return key_id(DescriptionKey(None, "disclosure", topics=topics).checked())
    assert ident(("equity", "dividend")) == ident(("dividend", "equity"))


async def test_two_purchases_keep_both_frozen_versions_selectable(world):
    material, first = await world.report(ALICE, 2025)
    await world.lib.set_license(ALICE, material.id, "sale", attest=True)
    await world.lib.purchase(ALICE, material.id, BOB, "trade-one")
    _, second = await world.lib.add_version(ALICE, material.id, "revision.csv", CSV + b"version2")
    await world.lib.purchase(ALICE, material.id, BOB, "trade-two")
    key = DescriptionKey("600519.SH", "annual_report", date(2025, 1, 1), date(2025, 12, 31))
    candidates = await world.resolver.repo.candidates(BOB, "knowbench", key)
    assert {row.version_no for row in candidates} == {first.version_no, second.version_no}
