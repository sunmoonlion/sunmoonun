"""Check material processing and evidence identity against disposable PostgreSQL."""
from datetime import timedelta

from test_user_runs_db import ALICE, CSV, db, item, world
from app.domain.user_library import Description


async def test_completed_recent_rows_do_not_hide_older_work(world):
    waiting, _ = await world.upload(ALICE, process=True)
    for number in (1, 2):
        world.clock.now += timedelta(seconds=1)
        material, _ = await world.upload(ALICE, f"done-{number}.csv", process=True)
        grant = await world.runs.issue_processing("knowfeed", ALICE, material.id, 1)
        await world.runs.write_rendition("knowfeed", grant.id, "text", "1", b"ready")
    assert await world.runs.pending_processing("knowfeed", limit=1) == [(ALICE, waiting.id, 1)]


async def test_use_evidence_counts_only_read_version(world):
    material, first = await world.upload(ALICE, display_to="knowbench")
    _, second = await world.lib.add_version(ALICE, material.id, "report.csv", CSV + b"2")
    ref = "two-versions-in-one-task"
    grant = await world.runs.grant_by_user(ALICE, "knowbench", "delegation", ref, [
        item(version, "display", "app:knowbench") for version in (first, second)
    ])
    await world.runs.read("knowbench", "reader", grant.id, material.id, 2, "content")
    read = await world.runs.runs.items_read(ALICE, ref=ref, session_window=None)
    assert set(read) == {(material.id, 2)}


async def test_purge_removes_research_authorship_fields(world):
    material, _ = await world.upload(ALICE, description=Description(
        doc_type="research_company", attributes={"analysts": ["Synthetic Author"]}
    ))
    assert await world.runs.purge_material("operator", material.id, "personal-info", personal_info=True)
    stored = await world.lib.repo.get_material(material.id)
    assert not stored.description.attributes


async def test_purge_can_finish_recording_after_transient_journal_failure(world, monkeypatch):
    import pytest

    material, _ = await world.upload(ALICE)
    repo = world.runs.runs
    original = repo.add_deletion

    async def temporary_outage(**kwargs):
        raise ConnectionError("synthetic journal outage")

    monkeypatch.setattr(repo, "add_deletion", temporary_outage)
    with pytest.raises(ConnectionError):
        await world.runs.purge_material("operator", material.id, "cleanup", personal_info=False)
    monkeypatch.setattr(repo, "add_deletion", original)
    await world.runs.purge_material("operator", material.id, "cleanup", personal_info=False)
    events = await world.runs.deletions_of_material(material.id)
    assert any(event["action"] == "purge" for event in events)
