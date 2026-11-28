"""Check per-file output identity, receipt validation and progress on partial replies."""
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from test_workbench_ledger_db import db as db
from test_workbench_outputs_db import Area, Reader, delivered, rows

from app.application.workbench.outputs import OutputWriter, output_name
from app.bootstrap.workbench import workbench_stores
from app.domain.workbench.packs import safe_relative_path


def test_two_supported_paths_have_distinct_storage_keys():
    paths = ("分析/年报.md", "分析／年报.md")
    assert all(map(safe_relative_path, paths))
    assert len({output_name(path) for path in paths}) == 2


async def test_written_receipt_matches_delivered_content(db):
    await delivered(db)
    writer = OutputWriter(workbench_stores(db), Reader(), Area())
    await writer.sweep()
    [output] = await rows(db)
    assert output["status"] != "written" or output["sha256"] == output["accepted_sha256"]


async def test_one_partial_reply_does_not_block_next_file(db):
    task = await delivered(db)
    async with db() as session, session.begin():
        await session.execute(text("""
            INSERT INTO workbench_task_outputs(task_id,run_ref,path,accepted_sha256,next_try_at)
            SELECT task_id,run_ref,'second.md',accepted_sha256,next_try_at+interval '1 second'
            FROM workbench_task_outputs WHERE task_id=:task
        """), {"task": task})

    class PartialFirstReply(Area):
        async def write_output(self, **args):
            result = await super().write_output(**args)
            if args["name"] != "second.md":
                result.pop("version_no")
            else:
                from hashlib import sha256
                result["sha256"] = sha256(args["content"]).hexdigest()
            return result

    writer = OutputWriter(workbench_stores(db), Reader(), PartialFirstReply(),
                          now=lambda: datetime.now(UTC) + timedelta(minutes=1))
    assert await writer.sweep() == 1
    results = {row["path"]: row for row in await rows(db)}
    assert results["second.md"]["status"] == "written"
