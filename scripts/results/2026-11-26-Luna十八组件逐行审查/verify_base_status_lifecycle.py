"""Local operator status edits must preserve the ingestion lifecycle."""
import pytest
from test_knowledge_delivery_db import db, ingestion_policy, service, submit, sql


async def mark(session, job_id, status):
    return await service.update_ingestion_status(
        session, ingestion_id=job_id, status=status, metadata={}, last_error=None,
        knowledge_document_id=None, ragflow_document_id=None,
    )


@pytest.mark.asyncio
async def test_success_corresponds_to_an_indexed_version(db, ingestion_policy):
    job_id = await submit(db)
    async with db() as session:
        await mark(session, job_id, "succeeded")
    status = await sql(db, "SELECT status FROM knowledge_ingestion_job")
    versions = await sql(db, "SELECT count(*) FROM knowledge_document_version")
    assert status != "succeeded" or versions > 0


@pytest.mark.asyncio
async def test_nonterminal_state_has_no_completion_timestamp(db, ingestion_policy):
    job_id = await submit(db)
    async with db() as session:
        await mark(session, job_id, "failed")
        await mark(session, job_id, "running")
    assert await sql(db, "SELECT completed_at IS NULL FROM knowledge_ingestion_job")


@pytest.mark.asyncio
async def test_concurrent_status_notes_both_remain_in_journal(db, ingestion_policy):
    job_id = await submit(db)
    async with db() as left, db() as right:
        # Each operator has already loaded the same accepted job.
        first = await service.get_ingestion_job(left, job_id)
        second = await service.get_ingestion_job(right, job_id)
        assert first.status == second.status == "accepted"
        for session, note in [(left, "one"), (right, "two")]:
            await service.update_ingestion_status(
                session, ingestion_id=job_id, status="running", metadata={"note": note},
                last_error=None, knowledge_document_id=None, ragflow_document_id=None,
            )
    async with db() as session:
        row = await service.get_ingestion_job(session, job_id)
        notes = [entry.get("metadata", {}).get("note") for entry in row.status_history]
    assert {"one", "two"} <= set(notes)
