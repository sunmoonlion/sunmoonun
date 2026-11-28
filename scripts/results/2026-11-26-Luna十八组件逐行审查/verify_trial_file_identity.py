"""在临时目录和真实计划执行器上区分交付时文件与随后重新读取的文件。"""
import json
import hashlib

from method_plan_fixtures import proposal
from test_method_plans_db import task
from test_method_task_runtime_db import Driver, ROWS, patch_catalog
from test_method_test_exports_db import exported
from test_workbench_ledger_db import db as db

from app.application.workbench.deliverable_check import ReadFile
from app.application.workbench.task_runtime import TaskRuntime
from app.domain.workbench.states import TaskState
from app.infrastructure.workbench.repository import WorkbenchRepository, SqlWorkbenchStores


async def test_changed_report_is_exported_after_delivery(db, tmp_path):
    tid, _ = await task(db)
    def add_file(catalog):
        for method in catalog["method_units"]:
            if method["contract"]["step_id"] == "report":
                method["contract"]["output_file"] = "report.md"
    await patch_catalog(db, tid, add_file)
    file = tmp_path / "report.md"
    file.write_text("交付时的报告")
    class Files:
        async def exists(self, **kwargs):
            return file.exists()
        async def digest(self, **kwargs):
            return hashlib.sha256(file.read_bytes()).hexdigest()
        async def read(self, **kwargs):
            return ReadFile(file.read_text(), file.stat().st_mtime_ns // 1_000_000)
    files = Files()
    runtime = TaskRuntime(SqlWorkbenchStores(db), Driver([json.dumps(proposal().model_dump(mode="json")), ROWS, ROWS]), deliverables=files)
    assert await runtime.drive(tid) == TaskState.SUCCEEDED
    file.write_text("交付后改写的报告")
    async with db() as session:
        repo = WorkbenchRepository(session)
        out, _ = await exported(db, repo, await repo.get_task(tid), reader=files)
        final = next(x for x in out["final_outputs"] if x["method_id"] == "report")
        assert final["deliverable"]["text"] == "交付后改写的报告"
        assert final["result"]["digest"] and final["note"] is None
