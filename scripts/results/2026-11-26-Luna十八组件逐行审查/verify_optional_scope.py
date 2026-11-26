"""在 KnowBench 后端 app 下以 PYTHONPATH=.:tests 运行。"""
from test_formal_orchestration_admission import shape
from app.domain.workbench.formal_expert_match import frozen_scope

root, *_ = shape()
baseline = root.draft.definition
doc = baseline.document()
graph = doc["procedure"]
name, export = next(iter(graph["exports"].items()))
assert export["always_present"]
step = next(step for step in graph["steps"] if step["id"] == export["step"])
assert step["always_required"]
export["always_present"] = False
step["outputs"][export["output"]]["required"] = False
optional = type(baseline).model_validate(doc)
assert baseline.interfaces()["outputs"][name]["always_present"]
assert not optional.interfaces()["outputs"][name]["always_present"]
assert frozen_scope(baseline) == frozen_scope(optional)
