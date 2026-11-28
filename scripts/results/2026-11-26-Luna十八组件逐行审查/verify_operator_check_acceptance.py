"""在 KnowLab 后端 app 下以 PYTHONPATH=. 运行。按同一份真实目录构造可选输入用例。"""
import json
from pathlib import Path
from app.application.services.knowbot_proposals import _checked
from app.application.services.knowbot_workdraft import parse_body
from app.domain.knowbots.compile import decompile
from app.domain.knowbots.incubation_rounds import apply_suggestion

fixture = Path(__file__).resolve().parents[4]/"knowbench-app/knowbench-backend/app/tests/fixtures/capability-methods-manifest.json"
body, _ = decompile(json.loads(fixture.read_text()))
doc = body.model_dump(mode="json")
step = next(s for s in doc["steps"] if s["id"]=="report")
assert not step["input_required"]["review"]
path = step["outputs"][0]["name"]
step["checks"] = [
    {"template":"list_min","params":{"path":path,"min":1}},
    {"template":"non_empty","params":{"path":path},"when_input_present":"review"},
]
parse_body(doc)
replacement = [{"template":"list_min","params":{"path":path,"min":2}},
               {"template":"non_empty","params":{"path":path}}]
proposal = _checked({"path":"steps/report/checks","op":"set","value":replacement,"reason":"至少两行"})
changed = parse_body(apply_suggestion(doc,proposal.path,proposal.op,proposal.value))
assert getattr(next(s for s in changed.steps if s.id=="report").checks[1], "when_input_present", None) is None
