"""Library lifecycle expectations, checked against the ordinary service and DB fixture."""
from dataclasses import replace
from datetime import date, timedelta

import pytest
from test_user_resolution_db import ALICE, BOB, CSV, annual, db, world

from app.domain.user_data import UserDataError
from app.domain.user_library import Description, SubscriptionScope


async def test_failed_upload_leaves_no_unreferenced_bytes(world):
    before = dict(world.lib.objects.data)
    with pytest.raises(UserDataError):
        await world.lib.upload(ALICE, "report.csv", CSV, description=Description(doc_type="typo"))
    assert world.lib.objects.data == before


async def test_revised_format_matches_selected_payload(world):
    material, _ = await world.report(ALICE, 2025)
    _, version = await world.lib.add_version(ALICE, material.id, "correction.pdf", b"%PDF-1.4\nexample")
    assert version.media_type == "application/pdf"
    only_csv = replace(annual(count=1), formats=("csv",))
    result = await world.resolve([only_csv])
    assert not result.items[0].chosen


async def test_empty_freeze_is_repeatable(world):
    await world.lib.upsert_expert("expert-one", ALICE, "Example", "1")
    assert await world.lib.freeze_binding(ALICE, "expert-one", "1") == []
    material, _ = await world.report(ALICE, 2025)
    await world.lib.show(ALICE, material.id, "expert:expert-one")
    assert await world.lib.freeze_binding(ALICE, "expert-one", "1") == []


async def test_public_correction_keeps_actual_disclosure_date(world):
    old = Description(subject="600519.SH", doc_type="annual_report",
                      period_start=date(2025, 1, 1), period_end=date(2025, 12, 31),
                      disclosed_on=date(2026, 4, 10))
    args = ("knowfeed", "cninfo", "record-one", "report.csv")
    await world.lib.deliver_public(*args, CSV, old)
    correction = replace(old, disclosed_on=date(2026, 8, 15))
    updated, version, _ = await world.lib.deliver_public(*args, CSV + b"correction", correction)
    assert version.version_no == 2
    assert updated.description.disclosed_on == correction.disclosed_on


async def test_purchased_versions_remain_downloadable(world):
    material, first = await world.report(ALICE, 2025)
    await world.lib.set_license(ALICE, material.id, "sale", attest=True)
    await world.lib.purchase(ALICE, material.id, BOB, "trade-one")
    _, second = await world.lib.add_version(ALICE, material.id, "report.csv", CSV + b"2")
    await world.lib.purchase(ALICE, material.id, BOB, "trade-two")
    versions = await world.lib.versions(BOB, material.id)
    assert {row.version_no for row in versions} == {first.version_no, second.version_no}
    for row in versions:
        saved, _ = await world.lib.download(BOB, "knowbase", material.id, row.version_no)
        assert saved.sha256 == row.sha256


async def test_subscription_starts_on_agreed_day(world):
    start = world.clock.now.date() + timedelta(days=10)
    scope = SubscriptionScope("topic", start, start + timedelta(days=1), "daily check", topic="results")
    await world.lib.subscribe(ALICE, "daily", 1, scope, "user")
    with pytest.raises(UserDataError):
        await world.lib.live_subscription("knowfeed", ALICE, "daily", 1)


async def test_freeze_retries_after_storage_interruption(world, monkeypatch):
    await world.lib.upsert_expert("example", ALICE, "Example", "1")
    materials = []
    for year in (2024, 2025):
        material, _ = await world.report(ALICE, year)
        await world.lib.show(ALICE, material.id, "expert:example")
        materials.append(material.id)
    repo = world.lib.repo
    save = repo.add_use
    pending = 0

    async def interrupted(use):
        nonlocal pending
        pending += 1
        if pending == 2:
            raise ConnectionError("simulated database outage")
        return await save(use)

    monkeypatch.setattr(repo, "add_use", interrupted)
    with pytest.raises(ConnectionError):
        await world.lib.freeze_binding(ALICE, "example", "1")
    monkeypatch.setattr(repo, "add_use", save)
    recovered = await world.lib.freeze_binding(ALICE, "example", "1")
    assert {use.material_id for use, _ in recovered} == set(materials)
