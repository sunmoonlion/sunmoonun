"""在 KnowLab 后端 app 下用 PYTHONPATH=. 和项目 Python 运行。"""
import json
from pathlib import Path

from app.domain.knowbots.compile import compile_manifest, decompile, pack_problems
from app.domain.knowbots.workdraft import WorkdraftBody

fixture = Path(__file__).resolve().parents[4] / (
    "knowbench-app/knowbench-backend/app/tests/fixtures/capability-methods-manifest.json"
)
base, _ = decompile(json.loads(fixture.read_text()))


def compile_edit(edit):
    doc = base.model_dump(mode="json")
    edit(doc["steps"][0])
    body = WorkdraftBody.model_validate(doc)
    return compile_manifest(body, {}, pack_id="audit", version="1",
                            runtime="knowbench", fallback_name="核对")


def explicit_required(step):
    step["checks"].append({"template": "required",
                           "params": {"keys": [o["name"] for o in step["outputs"]]}})


manifest, issues = compile_edit(lambda step: None)
assert not issues and not pack_problems(manifest["pack"])
for edit in (
    lambda step: step.update(does="按顺序检查。\n\n规则：\n1. 优先核实原始数据。"),
    explicit_required,
):
    manifest, issues = compile_edit(edit)
    assert not issues
    assert any("differs from its author definitions" in p.message
               for p in pack_problems(manifest["pack"]))
try:
    compile_edit(lambda step: step.update(on_fail={"kind": "back", "back_to": "other"}))
except KeyError as exc:
    assert exc.args == ("other",)
else:
    raise AssertionError("expected unresolved return target to raise KeyError")
