"""用普通安装入口登记包，再按同一份文件清单验证脚本入参。"""
import pytest
from test_capabilities_db import OWNER, service
from test_skill_package import archive
from test_skill_package_db import package
from test_workbench_ledger_db import db

from app.domain.workbench.script_contract_generated import ScriptExecution
from app.domain.workbench.skill_execution import execution_input
from app.infrastructure.workbench.repository import WorkbenchRepository


@pytest.mark.asyncio
async def test_new_install_accepts_unrunnable_file_layout(db):
    body = package().model_copy(update={"archive_base64": archive({
        "SKILL.md": "Run calculate.py", "calculate.py": "pass", "data": "index", "data/rows": "rows"
    })})
    async with db() as session:
        repo = WorkbenchRepository(session)
        svc = service(repo)
        installed = await svc.create_skill(OWNER, body, package=True)
        asset = await repo.capability_asset(OWNER, installed["id"])
        resources = await repo.skill_package_files(OWNER, asset["id"])
        assert asset["status"] == "active"
        frame = execution_input(asset, {"path": "calculate.py"}, resources)
        with pytest.raises(ValueError, match="file cannot also be a directory"):
            ScriptExecution.model_validate(frame)
