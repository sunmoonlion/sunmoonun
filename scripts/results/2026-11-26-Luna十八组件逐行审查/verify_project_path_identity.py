"""Compare legacy migration and current project path identity on POSIX."""
from pathlib import Path
from runpy import run_path

import pytest

from app.domain.workbench.projects import project_dir, split_under_roots


@pytest.mark.parametrize("stage", ["migration", "runtime"])
def test_directory_identity(stage):
    split = split_under_roots
    if stage == "migration":
        migration = next(Path("alembic/versions").glob("*0012_workbench_projects.py"))
        split = run_path(str(migration))["_split"]
    first, second = r"/work/Q1\summary", "/work/Q1/summary"
    a, b = (split(path, ["/work"]) for path in (first, second))
    assert a != b, (split.__name__, a, b)
    assert [project_dir(*item) for item in (a, b)] == [first, second]
