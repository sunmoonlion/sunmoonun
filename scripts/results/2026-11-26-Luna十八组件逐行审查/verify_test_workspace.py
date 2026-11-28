"""运行于 KnowBench 测试环境；服务流只记请求，不操作文件。"""

import re
from datetime import UTC, datetime

import pytest
from app.application.workbench.test_folders import AgentTestFolders, run_folder
from app.domain.workbench.test_runs import RUN_ID
from test_knowbot_test_folders import Service, stores


@pytest.mark.asyncio
async def test_existing_user_directory_is_preserved():
    service = Service(entries=[{"name": "archive", "type": "dir"}])
    folders = AgentTestFolders(service, stores)
    assert await folders.prepare(owner="tester", root="/workspace", folder="runs/current")
    assert ("fs/remove", {"path": "/workspace/runs/archive"}) not in service.calls


@pytest.mark.parametrize("left,right", [
    ("knowlab:a", "knowlab-a"),
    ("a" * 80 + "1", "a" * 80 + "2"),
])
def test_two_valid_run_ids_get_distinct_directories(left, right):
    accepted = datetime(2026, 11, 27, tzinfo=UTC)
    assert all(re.fullmatch(RUN_ID, value) for value in (left, right))
    assert run_folder({"created_at": accepted, "run_id": left}) != run_folder(
        {"created_at": accepted, "run_id": right}
    )
