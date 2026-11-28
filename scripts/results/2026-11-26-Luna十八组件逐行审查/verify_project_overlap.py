"""Two approved roots can describe the same directory on the same machine."""
import pytest
from test_workbench_ledger_db import OWNER, db as db
from test_workbench_projects_db import machine

from app.application.workbench.project_service import ProjectService
from app.domain.workbench.errors import ProjectExists
from app.infrastructure.workbench.repository import WorkbenchRepository


async def test_same_directory_has_one_live_project(db):
    env, _ = await machine(db, roots=("/research", "/research/2026"))
    async with db() as session:
        projects = ProjectService(WorkbenchRepository(session))
        args = {"owner_actor_id": OWNER, "environment_id": env}
        first = await projects.create(**args, workspace_root="/research", path="2026/Q1")
        try:
            second = await projects.create(**args, workspace_root="/research/2026", path="Q1")
        except ProjectExists:
            return
        assert first["directory"] == second["directory"]
        assert first["id"] == second["id"], "same directory has two live project IDs"
