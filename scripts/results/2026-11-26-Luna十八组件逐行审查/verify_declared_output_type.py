"""按项目自带已编译目录执行，检查实际交付能否按声明读取。"""
from method_plan_fixtures import proposal, catalog
from test_method_plans_db import task
from test_method_task_runtime_db import Driver
from test_workbench_ledger_db import db as db

from app.application.workbench.execution_plan import final_results
from app.application.workbench.task_runtime import TaskRuntime
from app.domain.workbench.states import TaskState
from app.infrastructure.workbench.repository import SqlWorkbenchStores, WorkbenchRepository


async def test_row_id_declared_as_text_is_accepted_as_number(db):
    tid, _ = await task(db)
    output = '{"rows":[{"id":123}]}'
    driver = Driver([proposal().model_dump_json(), output, output])
    declared = next(unit.contract for unit in catalog().method_units if unit.contract.step_id == "report")
    assert declared.output_schema == {"rows":[{"id":"string"}]}
    assert await TaskRuntime(SqlWorkbenchStores(db), driver).drive(tid) == TaskState.SUCCEEDED
    async with db() as session:
        repo = WorkbenchRepository(session)
        finals = await final_results(repo, await repo.get_task(tid))
        assert finals["report"]["content"]["rows"][0]["id"] == 123
