"""从 Luna 六仓根目录运行，核对同一工作稿的作者编译和执行成图。"""
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

root = Path.cwd()
lab = root / "knowlab-app/knowlab-backend/app"
bench = root / "knowbench-app/knowbench-backend/app"
fixture = bench / "tests/fixtures/capability-methods-manifest.json"
with TemporaryDirectory() as folder:
    destination = Path(folder) / "manifest.json"
    def run(base, source):
        subprocess.run([base / ".venv/bin/python", "-c", source, fixture, destination],
                       cwd=base, check=True)
    run(lab, """
import json,sys
from pathlib import Path
from app.domain.knowbots.compile import decompile, compile_manifest
from app.domain.knowbots.workdraft import WorkdraftBody
body, _ = decompile(json.loads(Path(sys.argv[1]).read_text()))
doc = body.model_dump(mode="json")
extra = next(s for s in doc['steps'] if s['id']=='inspect').copy()
extra.update(id='separate', title='单独复核')
doc['steps'].append(extra)
doc['planning']['capability_bindings']['double_check']['required_units'].append('separate')
manifest, problems = compile_manifest(WorkdraftBody.model_validate(doc), {},
    pack_id='audit', version='1', runtime='knowbench', fallback_name='核对')
assert problems == [], problems
Path(sys.argv[2]).write_text(json.dumps(manifest, ensure_ascii=False))
""")
    run(bench, """
import json,sys
from pathlib import Path
from app.domain.workbench.method_catalog import parse_catalog, input_methods
from app.domain.workbench.method_plan import validate_composition, parse_plan
sys.path.insert(0,'tests')
from test_capability_method_plan import proposal
catalog = parse_catalog(json.loads(Path(sys.argv[2]).read_text())['pack'])
steps = {s.contract.step_id:s for s in catalog.method_units}
seen = set()
pending = list(catalog.planning.final_units)
while pending:
    name = pending.pop()
    if name not in seen:
        seen.add(name)
        pending.extend(input_methods(steps[name].contract))
assert 'separate' not in seen and steps['separate'].selection.required
doc = proposal(review=True)
doc['steps'][-1]['inputs'][0]['slot']='inspect'
doc['steps'][-1]['inputs'][-1]['slot']='review'
doc['steps'].insert(0, {**doc['steps'][0], 'instance_id':'extra_1','method_id':'separate'})
try:
    validate_composition(catalog,parse_plan(doc),available_tools={'read_input'})
except ValueError as exc:
    assert 'reach a final deliverable' in str(exc), exc
else:
    raise AssertionError('expected disconnected method to prevent execution')
""")
