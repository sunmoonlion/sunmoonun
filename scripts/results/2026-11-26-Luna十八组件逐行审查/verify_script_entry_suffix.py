"""从同一份可安装的包比较孵化来源、普通工具目录与脚本执行契约。"""
from datetime import UTC, datetime

import pytest
from test_skill_package import archive

from app.application.workbench.formal_methods import FormalMethods
from app.domain.workbench.script_contract_generated import ScriptCommand
from app.domain.workbench.skill_execution import script_tool
from app.domain.workbench.skill_package import unpack_skill


def test_extension_only_filename_is_offered_only_in_incubation():
    package = unpack_skill(archive({"SKILL.md": "Use run.py", ".py": "", "run.py": "pass"}))
    asset = {
        "id": "73b757f2-e08b-42f0-a7fb-205184767ac2", "revision": 1,
        "name": "sample", "kind": "skill", "status": "active",
        "detail": {**package, "version": "1"},
    }
    sources = FormalMethods(None)._sources(asset, "author", now=datetime.now(UTC))
    assert {s.entry for s in sources if s.kind == "skill_script"} == {".py", "run.py"}
    assert script_tool(asset)["inputSchema"]["properties"]["path"]["enum"] == ["run.py"]
    assert ScriptCommand(path="run.py").path == "run.py"
    with pytest.raises(ValueError, match="Supported scripts"):
        ScriptCommand(path=".py")
