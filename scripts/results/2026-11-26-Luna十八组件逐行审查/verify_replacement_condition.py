"""将真实前端的替换结果交给后端正式定义校验器，并对照替换前结果。"""
import os
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

web = Path('knowlab-app/knowlab-web-frontend/app').resolve()
backend = Path('knowlab-app/knowlab-backend/app').resolve()
tests = web/'tests/component'
fixture = (tests/'formal-method-editor.test.tsx').read_text().split('const initial =')[0]
case = """
it('emits the replacement even when the original promise condition loses its input', () => {
  const original = orchestrationDraft(draft).definition
  const graph = original.procedure
  if(graph.kind !== 'orchestration') throw Error()
  graph.steps = graph.steps.slice(0,1)
  graph.exports.summary.step = 'first'
  original.capability_declaration.conditions = {summary:{when:'提供原文时', input_slots:['message']}}
  const candidate = structuredClone(original)
  const other = candidate.procedure
  if(other.kind !== 'orchestration') throw Error()
  delete candidate.capability_declaration.conditions
  delete other.steps[0].inputs.message
  other.steps[0].candidates[0].method_id = RUN
  const result = replaceP1Tool(original,'message','summary',candidate,'summary')
  if(!('plan' in result)) throw Error('no replacement')
  writeFileSync(process.env.LUNA_REVIEW_OUTPUT!,JSON.stringify([original,result.plan]))
})
"""
check = """
import json, sys
from pathlib import Path
from pydantic import ValidationError
from app.domain.knowbots.formal_method import FormalMethodDefinition
original, replacement = json.loads(Path(sys.argv[1]).read_text())
FormalMethodDefinition.model_validate(original)
try:
    FormalMethodDefinition.model_validate(replacement)
except ValidationError as exc:
    assert 'Condition inputs must name distinct public input slots' in str(exc)
else:
    raise AssertionError('replacement was accepted')
"""
with TemporaryDirectory() as temp, NamedTemporaryFile(dir=tests, suffix='.test.tsx', mode='w') as f:
    out = str(Path(temp)/'plans.json')
    f.write("import { writeFileSync } from 'node:fs'\n"+fixture+case)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest','run',f.name],cwd=web,
                   env={**os.environ,'LUNA_REVIEW_OUTPUT':out},check=True)
    subprocess.run([backend/'.venv/bin/python','-c',check,out],cwd=backend,check=True)
